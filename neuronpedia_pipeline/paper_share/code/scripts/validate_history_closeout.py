"""Offline closeout validation of the fixed history pilot and stopping rule."""
import json
from datetime import datetime
import history_choice_closeout as design
from run_history_closeout import verify_freeze,evaluate_pilot
from run_matched_choice_controls import LEDGER
from matched_choice_controls import ROOT,digest
from analyze_matched_choice_controls import csv_write
from control_io import atomic_json

def main():
    freeze,jobs=verify_freeze()
    jobs=sorted([j for j in jobs if j['split']!='held_out'],key=lambda j:(j['split']!='literal',j['job_id']))
    records=[];hashes={};rows=[]
    for j in jobs:
        folder=design.OUT/design.MODEL/'pilot'/j['job_id']
        r=json.loads((folder/'response.json').read_text());records.append(r)
        state=json.loads((folder/'request_state.json').read_text())
        assert state['payload']['prompt']==j['prompt'] and state['status']=='received'
        for p in folder.glob('*.json'):hashes[str(p.relative_to(ROOT))]=digest(p)
        top=max(r['salient_logits'],key=lambda x:x['probability'])
        rows.append(dict(job_id=j['job_id'],block=j['block'],expected=j['expected_label'],observed=top['token'],
                         correct=top['token'].strip()==j['expected_label'],probability=top['probability'],prompt=j['plain_prompt']))
    gate=evaluate_pilot(jobs,records)
    assert gate==json.loads((design.OUT/'pilot_gate.json').read_text())
    result=json.loads((design.OUT/'analysis/results.json').read_text())
    assert result['pilot']==gate and not gate['passed'] and result['primary']['status']=='not_run_pilot_failed'
    assert not list((design.OUT/design.MODEL/'graphs').glob('*/raw_graph.json'))
    frozen_epoch=datetime.fromisoformat(freeze['frozen_at']).timestamp()
    ledger=json.loads(LEDGER.read_text())['events']
    events=[e for e in ledger if e['epoch']>=frozen_epoch]
    history=[e for e in events if e['job_id'] in {j['job_id'] for j in jobs} and e['model']==design.MODEL]
    assert len(history)==20 and all(e['kind']=='pilot' for e in history)
    starts=sorted(e['epoch'] for e in events)
    assert all(b-a>=125-1e-6 for a,b in zip(starts,starts[1:]))
    assert all(sum(0<=b-a<3600 for b in starts)<=30 for a in starts)
    out=design.OUT/'analysis'
    csv_write(out/'pilot_responses.csv',rows)
    csv_write(design.OUT/'checksums.csv',[dict(path=p,sha256=s) for p,s in sorted(hashes.items())])
    report=dict(passed=True,pilot_correct=gate['correct'],pilot_n=20,graphs_requested=0,
                frozen_hashes_verified=True,archived_gate_reconstructed=True,quota_verified_from_shared_ledger=True,
                preview_file_hashes=hashes,script_sha256=digest(__file__))
    atomic_json(out/'validation.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='preview_file_hashes'},indent=2))

if __name__=='__main__':main()
