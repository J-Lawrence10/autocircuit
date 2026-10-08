"""Frozen 20-preview diagnostic; hosted-only, no graphs or adaptive prompt search."""
import argparse
from collections import defaultdict
import hashlib
import json
import os
import random
import re
import traceback

import jinja2
from tokenizers import Tokenizer

from audit_position_pilot import ROOT, SOURCE, OUT, TOKENIZER_DIR, score_prompt_text, audit
from matched_choice_controls import digest
from control_io import atomic_json
from run_matched_choice_controls import Client, file_lock, now

PROTOCOL=ROOT/'docs/papers/POSITION_PILOT_ARTIFACT_DIAGNOSTIC.md'


def make_jobs():
    cfg=json.loads((TOKENIZER_DIR/'tokenizer_config.json').read_text())
    template=jinja2.Environment(trim_blocks=True,lstrip_blocks=True).from_string(cfg['chat_template'])
    def frame(plain):
        return template.render(messages=[dict(role='user',content=plain)],tools=None,
                               add_generation_prompt=True,enable_thinking=False)
    jobs=[]
    for label in ['A','B']:
        plain=f'Reply with only the letter {label}.'
        jobs.append(dict(job_id=f'literal_{label}',arm='literal',prompt=frame(plain),expected=label))
    v2=json.loads((ROOT/'data/model_extension/matched_choice_chat_v2/jobs.json').read_text())
    for name in ['pilot_france_germany__f0m1w0','pilot_france_germany__f1m1w0']:
        job=next(j for j in v2 if j['job_id']==name)
        jobs.append(dict(job_id='v2_'+name,arm='previous_success_replay',prompt=job['prompt'],expected=job['expected_label']))
    original=json.loads((SOURCE/'jobs.json').read_text());factorial=[]
    for suffix in ['f0m1p0w0','f0m0p1w0','f1m0p0w0','f1m1p1w0']:
        job=next(j for j in original if j['job_id']=='pilot_france_germany__'+suffix)
        oracle=score_prompt_text(job['plain_prompt'])
        for reference in ['ordinal','named']:
            for response in ['label','capital']:
                plain=job['plain_prompt']
                if reference=='named':
                    plain=re.sub(r'Question: .*\? Answer:',f'Question: what is the capital for {oracle["country"]}? Answer:',plain)
                if response=='capital':plain=plain.replace('Reply with only A or B.','Reply with only the capital name.')
                prompt=frame(plain)
                if reference=='ordinal' and response=='label':assert prompt==job['prompt']
                factorial.append(dict(job_id=f'{suffix}_{reference}_{response}',arm=f'{reference}_{response}',
                                      case=suffix,prompt=prompt,plain_prompt=plain,
                                      expected=oracle['expected_label'] if response=='label' else oracle['capital']))
    random.Random(20261001).shuffle(factorial)
    return jobs+factorial


def record(jobs):
    tokenizer=Tokenizer.from_file(str(TOKENIZER_DIR/'tokenizer.json'))
    assert len(jobs)==20 and len({j['job_id'] for j in jobs})==20
    for j in jobs:
        ids=tokenizer.encode(j['prompt'],add_special_tokens=False).ids
        assert len(ids)+1<=64
        tails=[]
        for space in ['', ' ']:
            suffix=tokenizer.encode(j['prompt']+space+j['expected'],add_special_tokens=False).ids
            if suffix[:len(ids)]==ids and len(suffix)==len(ids)+1:tails.append(suffix[-1])
        assert tails,(j['job_id'],'expected output not single-token')
    return dict(jobs_sha256=hashlib.sha256(json.dumps(jobs,sort_keys=True).encode()).hexdigest(),
                protocol_sha256=digest(PROTOCOL),script_sha256=digest(__file__),
                tokenizer_sha256=digest(TOKENIZER_DIR/'tokenizer.json'),
                tokenizer_config_sha256=digest(TOKENIZER_DIR/'tokenizer_config.json'),
                model='qwen3-4b',source='transcoder-hp',n=20,seed=20261001,
                scope='diagnostic previews only; no graph generation or confirmatory claims')


def summarize(jobs):
    rows=[];groups=defaultdict(list)
    tokenizer=Tokenizer.from_file(str(TOKENIZER_DIR/'tokenizer.json'))
    for job in jobs:
        path=OUT/'previews'/job['job_id']/'response.json'
        if not path.exists():continue
        r=json.loads(path.read_text());logits=r.get('salient_logits',[])
        top=max(logits,key=lambda x:x['probability']) if logits else {}
        pieces=[tokenizer.decode([i],skip_special_tokens=False) for i in tokenizer.encode(job['prompt'],add_special_tokens=False).ids]
        valid=r.get('prompt')==job['prompt'] and r.get('input_tokens')==pieces
        row=dict(job_id=job['job_id'],arm=job['arm'],expected=job['expected'],top=top,
                 transport_valid=valid,correct=valid and str(top.get('token','')).strip()==job['expected'],
                 response_sha256=digest(path))
        rows.append(row);groups[job['arm']].append(row)
    result=dict(complete=len(rows)==len(jobs),previews_archived=len(rows),planned=len(jobs),rows=rows,
                groups={arm:dict(correct=sum(r['correct'] for r in rs),n=len(rs)) for arm,rs in groups.items()},
                caveat='Outcome-informed diagnostic on four selected failures, not confirmatory or held-out evidence; no graphs generated.')
    atomic_json(OUT/'diagnostic_results.json',result)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    local=audit()
    if local['local_audit_failures'] or not all(local['frozen_files_match'].values()):
        raise RuntimeError('Local audit mismatch; inspect before remote diagnostics.')
    jobs=make_jobs();frozen=record(jobs);path=OUT/'freeze.json'
    if path.exists() and json.loads(path.read_text())!=frozen:raise RuntimeError('Diagnostic freeze changed')
    if not path.exists():atomic_json(path,frozen);atomic_json(OUT/'jobs.json',jobs)
    if not args.execute:
        print('Prepared 20 fixed diagnostic previews. No remote requests made.');return
    with file_lock(OUT/'runner.lock'):
        status=dict(state='running',pid=os.getpid(),started_at=now(),previews_archived=0)
        atomic_json(OUT/'status.json',status)
        try:
            client=Client()
            for job in jobs:
                status.update(current_job=job['job_id'],updated_at=now());atomic_json(OUT/'status.json',status)
                payload=dict(prompt=job['prompt'],modelId='qwen3-4b',sourceSetName='transcoder-hp',maxNLogits=10,desiredLogitProb=.99)
                client.post('qwen3-4b',{'job_id':'artifact20261001_'+job['job_id']},'pilot',payload,OUT/'previews'/job['job_id'])
                result=summarize(jobs);status['previews_archived']=result['previews_archived'];atomic_json(OUT/'status.json',status)
                print(f'Archived diagnostic {result["previews_archived"]}/20: {job["job_id"]}',flush=True)
                if not result['rows'][-1]['transport_valid']:raise RuntimeError('Returned prompt/token sequence mismatch; stopping diagnostics.')
            status.update(state='finished',finished_at=now());atomic_json(OUT/'status.json',status)
        except Exception as error:
            status.update(state='blocked',error=str(error),traceback=traceback.format_exc(),updated_at=now())
            atomic_json(OUT/'status.json',status);raise


if __name__=='__main__':main()
