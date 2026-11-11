"""Bounded final hosted history run; resume saved requests without duplicating exports."""
import argparse
import hashlib
import json
import os
import traceback

import history_choice_closeout as design
import run_matched_choice_controls as remote
from control_io import atomic_json
from matched_choice_controls import ROOT, digest


def verify_freeze():
    record=json.loads((design.OUT/'freeze.json').read_text())
    for name,sha in record['file_hashes'].items():
        if digest(ROOT/name)!=sha:raise ValueError(f'Frozen file changed: {name}')
    jobs=design.make_jobs()
    sha=hashlib.sha256(json.dumps(jobs,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if sha!=record['jobs_sha256']:raise ValueError('Frozen jobs changed')
    design.validate(jobs)
    return record,jobs


def evaluate_pilot(jobs,records):
    details=[]
    if len(records)!=len(jobs) or len(jobs)!=20:
        return dict(passed=False,reason='incomplete',n=len(records))
    for job,result in zip(jobs,records):
        logits=result.get('salient_logits',[])
        top=max(logits,key=lambda x:x['probability']) if logits else {}
        prompt_ok=remote.clean_prompt(result.get('prompt',''))==job['prompt']
        details.append(dict(job_id=job['job_id'],expected=job['expected_label'],top=top,
                            prompt_ok=prompt_ok,correct=str(top.get('token','')).strip()==job['expected_label']))
    blocks={}
    for block in sorted({j['block'] for j in jobs if j['split']=='pilot'}):
        pairs=[(j,r) for j,r in zip(jobs,records) if j['block']==block]
        blocks[block]=remote.pilot_gate([r for _,r in pairs],[j for j,_ in pairs])
    passed=all(d['correct'] and d['prompt_ok'] for d in details) and all(b['passed'] for b in blocks.values())
    return dict(passed=passed,n=20,correct=sum(d['correct'] and d['prompt_ok'] for d in details),blocks=blocks,details=details)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    record,jobs=verify_freeze()
    if not args.execute:
        print('DRY RUN: 20 pilot previews; only if all pass, 160 fixed graphs and automatic analysis.');return
    remote.OUT,remote.MODELS=design.OUT,design.MODELS
    status_path=design.OUT/'status.json'
    with remote.file_lock(design.OUT/'runner.lock'):
        status=dict(state='running',pid=os.getpid(),started_at=remote.now(),graphs_complete=0)
        def save(**updates):
            status.update(updated_at=remote.now(),**updates);atomic_json(status_path,status)
        try:
            client=remote.Client();pilot_jobs=sorted([j for j in jobs if j['split']!='held_out'],key=lambda j:(j['split']!='literal',j['job_id']))
            records=[]
            for j in pilot_jobs:
                save(stage='pilot',current_job=j['job_id'],pilot_complete=len(records))
                payload=dict(prompt=j['prompt'],modelId=design.MODEL,sourceSetName=design.MODELS[design.MODEL],maxNLogits=10,desiredLogitProb=.99)
                records.append(client.post(design.MODEL,j,'pilot',payload,design.OUT/design.MODEL/'pilot'/j['job_id']))
                print(f'Pilot {len(records)}/20 archived',flush=True)
            gate=evaluate_pilot(pilot_jobs,records);atomic_json(design.OUT/'pilot_gate.json',gate)
            save(pilot_complete=20,pilot=gate)
            if not gate['passed']:
                save(state='pilot_failed',stage='terminal',finished_at=remote.now())
                from analyze_history_closeout import analyze
                analyze();return
            for i,j in enumerate([j for j in jobs if j['split']=='held_out'],1):
                save(stage='graphs',current_job=j['job_id'])
                remote.graph_job(client,design.MODEL,j,record['settings'])
                save(graphs_complete=i)
                print(f'Graphs {i}/160 archived',flush=True)
            save(stage='analysis')
            from analyze_history_closeout import analyze
            result=analyze()
            save(state='complete',stage='terminal',primary_status=result['primary']['status'],finished_at=remote.now())
        except Exception as error:
            save(state='blocked',error=str(error),traceback=traceback.format_exc())
            raise


if __name__=='__main__':main()
