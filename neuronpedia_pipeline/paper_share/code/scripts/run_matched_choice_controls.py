#!/usr/bin/env python3
"""Serial, restart-safe remote pilot then graph generation; no local inference."""
import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import requests
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from matched_choice_controls import ROOT, OUT, PROTOCOL, MODELS, make_jobs, digest, atomic_json
from control_io import atomic_json, replace_with_retry

LEDGER=ROOT/'data/model_extension/neuronpedia_request_ledger.json'


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def file_lock(path,wait_for_contention=False):
    import msvcrt
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as f:
        if path.stat().st_size==0:
            f.write(b'0');f.flush()
        f.seek(0)
        deadline=time.monotonic()+5
        while True:
            try:
                msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
                break
            except OSError as error:
                if not wait_for_contention or error.errno not in (13,36) or time.monotonic()>=deadline:
                    raise
                time.sleep(.1)
                f.seek(0)
        try:
            yield
        finally:
            f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)


def rate_delay(events, timestamp):
    starts=sorted(e['epoch'] for e in events)
    recent=[t for t in starts if timestamp-t<3600]
    delay=max(0,starts[-1]+125-timestamp) if starts else 0
    if len(recent)>=30:
        delay=max(delay,recent[-30]+3601-timestamp)
    return delay


def reserve_post(model,job_id,kind):
    while True:
        with file_lock(LEDGER.with_suffix('.lock'),wait_for_contention=True):
            ledger=json.loads(LEDGER.read_text()) if LEDGER.exists() else {'events':[]}
            delay=rate_delay(ledger['events'],time.time())
            if delay<=0:
                ledger['events'].append(dict(epoch=time.time(),utc=now(),model=model,job_id=job_id,kind=kind))
                atomic_json(LEDGER,ledger)
                return
        print(f'Quota pacing: next request in {delay:.0f}s',flush=True)
        time.sleep(min(delay,30))


def clean_prompt(text):
    for marker in ['<bos>','<|endoftext|>','<|im_end|>']:
        if text.startswith(marker):
            text=text[len(marker):]
    return text


def pilot_gate(records,jobs):
    if len(records)!=8 or len(jobs)!=8:
        return {'passed':False,'reason':'incomplete','correct':0,'n':len(records)}
    correct=0;bags=[];details=[]
    for result,job in zip(records,jobs):
        logits=result.get('salient_logits',[])
        top=max(logits,key=lambda r:r['probability']) if logits else {}
        pieces=result.get('input_tokens',[])
        ok=(str(top.get('token','')).strip()==job['expected_label'])
        prompt_ok=clean_prompt(result.get('prompt',''))==job['prompt']
        correct+=ok and prompt_ok
        bags.append(Counter(pieces))
        details.append(dict(job_id=job['job_id'],expected=job['expected_label'],top=top,
                            prompt_ok=prompt_ok,input_token_count=len(pieces),correct=bool(ok)))
    balance=all(b==bags[0] for b in bags) and bool(bags[0])
    return {'passed':correct==8 and balance,'correct':int(correct),'n':8,
            'server_token_multisets_identical':balance,'details':details}


class Client:
    def __init__(self):
        config=yaml.safe_load((ROOT.parent/'config/neuronpedia_config.yaml').read_text(encoding='utf-8'))
        self.base=config['api']['base_url'].rstrip('/')
        self.headers={'Content-Type':'application/json'}
        key=config['api'].get('api_key')
        if key:self.headers['X-Api-Key']=key

    def reconcile(self,model,slug):
        response=requests.get(f'{self.base}/graph/{model}/{slug}',headers=self.headers,timeout=60)
        if response.status_code==200:
            info=response.json()
            if info.get('url'):
                return {'s3url':info['url'],'reconciled_metadata':info}
        return None

    def post(self,model,job,kind,payload,folder):
        folder.mkdir(parents=True,exist_ok=True)
        done=folder/'response.json'
        state_path=folder/'request_state.json'
        if done.exists():
            return json.loads(done.read_text())
        state=json.loads(state_path.read_text()) if state_path.exists() else {}
        if state.get('status')=='http_error' and state.get('status_code') not in [429,500,502,503,504]:
            raise RuntimeError(f'Non-retriable saved HTTP {state.get("status_code")}; inspect before resuming')
        while state.get('retry_not_before',0)>time.time():
            time.sleep(min(30,state['retry_not_before']-time.time()))
        if state.get('status') in ['submitting','uncertain'] and kind=='generate':
            recovered=self.reconcile(model,payload['slug'])
            if recovered:
                atomic_json(done,recovered);return recovered
            raise RuntimeError(f'Uncertain export for {job["job_id"]}; no duplicate POST permitted. Reconcile later.')
        attempts=state.get('attempts',0)
        while attempts<3:
            reserve_post(model,job['job_id'],kind)
            attempts+=1
            state=dict(status='submitting',attempts=attempts,started_at=now(),payload=payload)
            atomic_json(state_path,state)
            try:
                response=requests.post(f'{self.base}/graph/{"tokenize" if kind=="pilot" else "generate"}',
                                       json=payload,headers=self.headers,timeout=(30,360))
            except requests.RequestException as error:
                state.update(status='uncertain',error=type(error).__name__,updated_at=now())
                atomic_json(state_path,state)
                raise RuntimeError(f'{kind} request uncertain: {type(error).__name__}; saved for reconciliation') from error
            try:body=response.json()
            except ValueError:body={'non_json_response':response.text[:1000]}
            atomic_json(folder/f'http_attempt_{attempts}.json',dict(status_code=response.status_code,
                        retry_after=response.headers.get('Retry-After'),body=body,received_at=now()))
            if response.status_code==200:
                atomic_json(done,body)
                state.update(status='received',updated_at=now());atomic_json(state_path,state)
                return body
            state.update(status='http_error',status_code=response.status_code,updated_at=now())
            atomic_json(state_path,state)
            if kind=='generate':
                recovered=self.reconcile(model,payload['slug'])
                if recovered:atomic_json(done,recovered);return recovered
            if response.status_code not in [429,500,502,503,504]:
                raise RuntimeError(f'{kind} HTTP {response.status_code}; see archived response')
            delay=0
            retry=response.headers.get('Retry-After','')
            if retry:
                try:delay=float(retry)
                except ValueError:
                    from email.utils import parsedate_to_datetime
                    try:delay=max(0,parsedate_to_datetime(retry).timestamp()-time.time())
                    except (ValueError,TypeError):delay=3600 if response.status_code==429 else 0
            elif response.status_code==429:
                delay=3600
            if delay:
                until=time.time()+delay
                state['retry_not_before']=until;atomic_json(state_path,state)
                while time.time()<until:time.sleep(min(30,until-time.time()))
        raise RuntimeError(f'{kind}: maximum 3 attempts exhausted for {job["job_id"]}')


def graph_job(client,model,job,settings):
    folder=OUT/model/'graphs'/job['job_id']
    raw=folder/'raw_graph.json';meta=folder/'metadata.json'
    if raw.exists():
        if not meta.exists():raise RuntimeError(f'Raw graph lacks metadata: {raw}')
        recorded=json.loads(meta.read_text())
        if recorded['sha256']!=digest(raw):raise RuntimeError(f'Checksum mismatch: {raw}')
        return recorded
    slug=f'{OUT.name}-{model}-{job["job_id"]}'.replace('_','-')
    payload=dict(prompt=job['prompt'],modelId=model,sourceSetName=MODELS[model],slug=slug,**settings)
    info=client.post(model,job,'generate',payload,folder)
    url=info.get('s3url') or info.get('s3Location') or info.get('graphUrl')
    if not url:raise RuntimeError('Generation response lacks raw graph URL')
    response=requests.get(url,timeout=(30,180));response.raise_for_status()
    g=response.json()
    if not g.get('nodes') or not g.get('links',g.get('edges')):raise RuntimeError('Empty graph')
    m=g.get('metadata',{})
    if m.get('scan',m.get('model'))!=model or clean_prompt(m.get('prompt',''))!=job['prompt']:
        raise RuntimeError('Returned graph model or prompt mismatch')
    # Metadata is persisted before raw promotion so an interrupted download is never mistaken for a completed graph.
    record=dict(model=model,job=job,settings=settings,source_set=MODELS[model],created_at=now(),
                sha256=hashlib.sha256(response.content).hexdigest(),url=url,slug=slug,
                raw_path=str(raw.relative_to(ROOT)),bytes=len(response.content))
    atomic_json(meta,record)
    temp=raw.with_suffix('.json.tmp');temp.write_bytes(response.content);replace_with_retry(temp,raw)
    return record


def main():
    global OUT, PROTOCOL, MODELS, make_jobs
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true')
    parser.add_argument('--models',nargs='+',choices=list(MODELS))
    parser.add_argument('--experiment',choices=['matched_choice_v1','matched_choice_chat_v2'],default='matched_choice_v1')
    parser.add_argument('--pilot-only',action='store_true')
    args=parser.parse_args()
    if args.experiment=='matched_choice_chat_v2':
        import matched_choice_chat_controls as design
        OUT,PROTOCOL,MODELS,make_jobs=design.OUT,design.PROTOCOL,design.MODELS,design.make_jobs
    args.models=args.models or list(MODELS)
    if any(model not in MODELS for model in args.models):parser.error('Model not in selected experiment')
    from analyze_matched_choice_controls import configure_experiment
    configure_experiment(OUT,make_jobs,MODELS)
    freeze=json.loads((OUT/'freeze.json').read_text());jobs=make_jobs()
    assert freeze['protocol_sha256']==digest(PROTOCOL)
    assert freeze['design_script_sha256']==digest(ROOT/freeze.get('design_script_path','scripts/matched_choice_controls.py'))
    assert freeze['jobs_sha256']==hashlib.sha256(json.dumps(jobs,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if not args.execute:
        print(f'DRY RUN: {len(args.models)} models; per model 8 pilot previews then 48 graphs if pilot passes.');return
    with file_lock(OUT/'runner.lock'):
        client=Client()
        status_path=OUT/'status.json'
        status=json.loads(status_path.read_text()) if status_path.exists() else {'models':{}}
        status.update(pid=os.getpid(),started_at=now(),state='running',runner_sha256=digest(__file__))
        atomic_json(status_path,status)
        for model in args.models:
            try:
                pilot_jobs=[j for j in jobs if j['split']=='pilot'];records=[]
                for j in pilot_jobs:
                    status.update(current_model=model,current_job=j['job_id'],stage='pilot',updated_at=now());atomic_json(status_path,status)
                    payload=dict(prompt=j['prompt'],modelId=model,sourceSetName=MODELS[model],maxNLogits=10,desiredLogitProb=.99)
                    result=client.post(model,j,'pilot',payload,OUT/model/'pilot'/j['job_id'])
                    records.append(result)
                    print(f'{model} pilot {len(records)}/8 archived',flush=True)
                gate=pilot_gate(records,pilot_jobs)
                atomic_json(OUT/model/'pilot_gate.json',gate)
                status['models'][model]={'pilot':gate,'graphs_complete':0}
                atomic_json(status_path,status)
                if not gate['passed']:
                    status['models'][model]['state']='pilot_failed'
                    print(f'{model}: PILOT FAILED {gate["correct"]}/8; no held-out graphs requested',flush=True)
                    continue
                if args.pilot_only:
                    status['models'][model]['state']='pilot_passed';continue
                for i,j in enumerate([j for j in jobs if j['split']=='held_out'],1):
                    status.update(current_model=model,current_job=j['job_id'],stage='graphs',updated_at=now());atomic_json(status_path,status)
                    graph_job(client,model,j,freeze['model_settings'])
                    status['models'][model]['graphs_complete']=i
                    atomic_json(status_path,status)
                    print(f'{model} graphs {i}/48 archived',flush=True)
                from analyze_matched_choice_controls import analyze_model
                status.update(stage='analysis',updated_at=now());atomic_json(status_path,status)
                result=analyze_model(model)
                status['models'][model].update(state='analyzed',retrieval_gate=result['retrieval_gate'])
            except Exception as error:
                import traceback
                status['models'].setdefault(model,{})
                status['models'][model].update(state='blocked',error=str(error),traceback=traceback.format_exc(),updated_at=now())
                print(f'{model}: BLOCKED: {error}',flush=True)
            finally:
                atomic_json(status_path,status)
        status.update(state='finished_with_blockers' if any(m['state']=='blocked' for m in status['models'].values()) else 'finished',finished_at=now())
        atomic_json(status_path,status)
        from analyze_matched_choice_controls import overview
        overview()


if __name__=='__main__':main()
