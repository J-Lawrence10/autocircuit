"""One bounded, hosted-only v3 experiment; archive, analyze and close out automatically."""
from collections import Counter
import argparse
import json
import os
import traceback

import run_matched_choice_controls as transport
from matched_choice_position_controls import OUT, MODELS, make_jobs, frozen_record, digest
from control_io import atomic_json


def pilot_gate(records,jobs):
    if len(records)!=16 or len(jobs)!=16:
        return dict(passed=False,reason='incomplete',n=len(records),correct=0)
    gates=[]
    for p in [0,1]:
        subset=[(r,j) for r,j in zip(records,jobs) if j['position']==p]
        gates.append(transport.pilot_gate([r for r,j in subset],[j for r,j in subset]))
    bags=[Counter(r.get('input_tokens',[])) for r in records]
    balance=bool(bags[0]) and all(b==bags[0] for b in bags)
    return dict(passed=all(g['passed'] for g in gates) and balance,n=16,
                correct=sum(g['correct'] for g in gates),server_token_multisets_identical=balance,
                details=[d for g in gates for d in g['details']])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    freeze=json.loads((OUT/'freeze.json').read_text())
    if freeze!=frozen_record():raise RuntimeError('Frozen inputs or analysis changed; refusing requests.')
    jobs=make_jobs();pilot=[j for j in jobs if j['split']=='pilot'];held=[j for j in jobs if j['split']=='held_out']
    if not args.execute:
        print(f'DRY RUN: {len(pilot)} pilot previews, then {len(held)} hosted Qwen3-4B graphs only if all pass.');return
    transport.OUT=OUT;transport.MODELS=MODELS
    model='qwen3-4b';path=OUT/'status.json'
    with transport.file_lock(OUT/'runner.lock'):
        status=json.loads(path.read_text()) if path.exists() else {}
        status.pop('finished_at',None)
        status.update(state='running',pid=os.getpid(),started_at=transport.now(),
                      runner_sha256=digest(__file__),model=model)
        atomic_json(path,status)
        try:
            client=transport.Client();records=[]
            for job in pilot:
                status.update(stage='pilot',current_job=job['job_id'],updated_at=transport.now());atomic_json(path,status)
                payload=dict(prompt=job['prompt'],modelId=model,sourceSetName=MODELS[model],maxNLogits=10,desiredLogitProb=.99)
                records.append(client.post(model,job,'pilot',payload,OUT/model/'pilot'/job['job_id']))
                status['pilot_archived']=len(records);atomic_json(path,status)
                print(f'v3 pilot {len(records)}/16 archived',flush=True)
            gate=pilot_gate(records,pilot);atomic_json(OUT/model/'pilot_gate.json',gate)
            status['pilot']=gate
            if not gate['passed']:
                status.update(state='finished',stage='pilot_failed',finished_at=transport.now(),graphs_complete=0)
                print(f'PILOT FAILED {gate["correct"]}/16; no held-out graphs will be requested.',flush=True)
            else:
                for i,job in enumerate(held,1):
                    status.update(stage='graphs',current_job=job['job_id'],updated_at=transport.now());atomic_json(path,status)
                    transport.graph_job(client,model,job,freeze['model_settings'])
                    status['graphs_complete']=i;atomic_json(path,status)
                    print(f'v3 graphs {i}/96 archived',flush=True)
                status.update(stage='analysis',updated_at=transport.now());atomic_json(path,status)
                from analyze_position_controls import analyze_model
                result=analyze_model(model)
                status.update(state='finished',stage='analyzed',retrieval_gate=result['retrieval_gate'],finished_at=transport.now())
            atomic_json(path,status)
            from build_control_closeout import main as closeout
            closeout()
            status.update(closeout_complete=True,updated_at=transport.now());atomic_json(path,status)
        except Exception as error:
            status.update(state='blocked',error=str(error),traceback=traceback.format_exc(),updated_at=transport.now())
            atomic_json(path,status)
            print(traceback.format_exc(),flush=True)
            # No automatic new design, prompt search or blind uncertain-request retry.
            raise


if __name__=='__main__':main()
