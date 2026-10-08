import sys
import json
import contextlib
import io
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import history_choice_closeout as design
from run_history_closeout import evaluate_pilot
from analyze_history_closeout import block_statistics, eligibility, contrast_set
from analyze_matched_choice_controls import contrasts


def test_fixed_design_offline():
    jobs=design.make_jobs();validation=design.validate(jobs)
    assert len(validation)==23
    assert sum(j['split']=='held_out' for j in jobs)==160
    assert len({j['event'] for j in jobs if j['split']=='held_out'})==40


def pilot_fixture():
    jobs=[j for j in design.make_jobs() if j['split']!='held_out']
    records=[dict(prompt=j['prompt'],salient_logits=[dict(token=j['expected_label'],probability=.9)],input_tokens=['same','bag']) for j in jobs]
    return jobs,records


def test_pilot_positive_and_negative_controls():
    jobs,records=pilot_fixture()
    assert evaluate_pilot(jobs,records)['passed']
    records[0]['salient_logits'][0]['token']='wrong'
    assert not evaluate_pilot(jobs,records)['passed']


def test_pilot_requires_prompt_and_tokens_and_complete():
    jobs,records=pilot_fixture();records[0]['input_tokens']=['different']
    assert not evaluate_pilot(jobs,records)['passed']
    jobs,records=pilot_fixture();records[0]['prompt']='wrong'
    assert not evaluate_pilot(jobs,records)['passed']
    assert not evaluate_pilot(jobs,records[:-1])['passed']


def test_exact_sign_null_and_positive_control():
    assert block_statistics([0]*6)['exact_two_sided_sign_flip_p']==1
    assert block_statistics([1]*6)['exact_two_sided_sign_flip_p']==2/64
    assert block_statistics([-1,1,-1,1])['exact_two_sided_sign_flip_p']==1
    assert block_statistics([1]*6)['t_ci95']==[1,1]


def test_support_gate_fixed():
    rows=[dict(theme='documents' if i<10 else 'space',correct_response_supported=i<16) for i in range(20)]
    assert eligibility(rows)
    rows[15]['correct_response_supported']=False
    assert not eligibility(rows)
    assert not eligibility(rows[:-1])


def test_contrast_detects_interaction_not_label_main_effect():
    from analyze_matched_choice_controls import KEYS
    m=np.array([[float(l==ll) for ff,ll in KEYS] for f,l in KEYS])
    c=contrasts(m)
    assert c['fact_same_label']-c['fact_different_label']==0
    assert c['label_effect']==1
    m=np.eye(4);c=contrasts(m)
    assert c['fact_same_label']-c['fact_different_label']==1


def test_perfect_identical_graphs_are_null():
    reps={(f,l,w):{'features':{'common'}} for f in [0,1] for l in ['A','B'] for w in [0,1]}
    c=contrast_set(reps)
    assert c['label_condition_difference']==0


def test_full_synthetic_history_analysis_without_remote_calls(tmp_path,monkeypatch):
    import analyze_history_closeout as analysis
    import run_history_closeout as runner
    from matched_choice_controls import digest
    jobs=design.make_jobs()
    settings=dict(maxNLogits=10,desiredLogitProb=.99,nodeThreshold=.8,edgeThreshold=.85,maxFeatureNodes=5000)
    monkeypatch.setattr(design,'OUT',tmp_path)
    monkeypatch.setattr(analysis,'ROOT',tmp_path)
    monkeypatch.setattr(runner,'verify_freeze',lambda:({'settings':settings},jobs))
    monkeypatch.setattr(analysis,'plot',lambda result,out:None)
    (tmp_path/'freeze.json').write_text('{}')
    (tmp_path/'pilot_gate.json').write_text(json.dumps({'passed':True}))
    for j in [j for j in jobs if j['split']=='held_out']:
        label=int(j['expected_label']=='B')
        nodes=[]
        for layer,fid in enumerate([0,100+2*j['fact']+label,200+label]):
            nodes.append(dict(node_id=f'f{layer}',feature_type='transcoder',layer=str(layer),feature=fid,ctx_idx=0,influence=1,activation=1))
        nodes.append(dict(node_id='l',feature_type='logit',layer='3',feature=32+label,ctx_idx=1,influence=1,activation=1,
                          token=j['expected_label'],token_prob=1,is_target_logit=True))
        raw=dict(nodes=nodes,links=[dict(source=f'f{i}',target='l',weight=1) for i in range(3)],
                 metadata=dict(scan='qwen3-4b',slug='SYNTHETIC-ONLY',prompt=j['prompt'],prompt_tokens=['matched','tokens'],
                               node_threshold=.8,pruning_settings={'edge_threshold':.85},
                               generation_settings={'max_n_logits':10,'desired_logit_prob':.99},
                               info={'transcoder_set':'mwhanna/qwen3-4b-transcoders'}))
        dest=tmp_path/'qwen3-4b/graphs'/j['job_id'];dest.mkdir(parents=True)
        p=dest/'raw_graph.json';p.write_text(json.dumps(raw))
        (dest/'metadata.json').write_text(json.dumps(dict(sha256=digest(p),settings=settings)))
    with contextlib.redirect_stdout(io.StringIO()):result=analysis.analyze()
    assert result['valid']==160 and result['supported_blocks']==20
    assert result['retrieval_gate']
    assert result['primary']['mean']==pytest.approx(.5)
    assert result['primary']['exact_two_sided_sign_flip_p']==2/2**20
    # A checksum-corrupt graph is preserved, explicitly unavailable, and excludes its block.
    p=tmp_path/'qwen3-4b/graphs/documents_01__f0m0w0/raw_graph.json'
    p.write_text('{}')
    with contextlib.redirect_stdout(io.StringIO()):result=analysis.analyze()
    assert result['valid']==159 and result['supported_blocks']==19
    assert next(r for r in result['audits'] if r['job_id']=='documents_01__f0m0w0')['error']=='Raw checksum mismatch'
