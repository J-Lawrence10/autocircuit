"""Immutable manifest and exact-token roles for the approved sixteen-graph diagnostic."""
from collections import Counter
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import shutil
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from matched_choice_controls import ROOT,digest
from matched_choice_chat_controls import TOKENIZER_DIR
from audit_position_pilot import CAPITALS,score_prompt_text
from control_io import atomic_json

OUT=ROOT/'data/model_extension/failure_case_graphs_v1'
SOURCE=ROOT/'data/model_extension/position_artifact_diagnostic_20261001'
PLAN=ROOT/'docs/papers/FAILURE_CASE_GRAPH_ANALYSIS_PLAN.md'
MODEL='qwen3-4b'
SETTINGS=dict(maxNLogits=10,desiredLogitProb=.99,nodeThreshold=.8,edgeThreshold=.85,maxFeatureNodes=5000)
SEED=20261003
SOURCE_HASHES={'jobs.json':'0d66055f849578b1b90ce6a4f48faec89ba6b440ad347bbc5375e6065aa3d05f',
               'diagnostic_results.json':'b58bfa5cab203d161d105797bd39e2ff2e17f4f89942910d00bd52ec4ee437e0'}


def layout(plain):
    return re.search(r'A: ([^.]+)\. B: ([^.]+)\. Countries: ([^.]+)\.',plain).groups()


def make_jobs():
    for name,sha in SOURCE_HASHES.items():
        if digest(SOURCE/name)!=sha:raise ValueError(f'Source diagnostic changed: {name}')
    rows=json.loads((SOURCE/'jobs.json').read_text())
    results={r['job_id']:r for r in json.loads((SOURCE/'diagnostic_results.json').read_text())['rows']}
    jobs=[]
    for j in rows:
        if 'case' not in j:continue
        reference,fmt=j['arm'].split('_')
        a,b,_=layout(j['plain_prompt'])
        if reference=='ordinal':country=score_prompt_text(j['plain_prompt'])['country']
        else:country=re.search(r'Question: what is the capital for ([^?]+)\?',j['plain_prompt']).group(1)
        intended=CAPITALS[country] if fmt=='capital' else ('A' if CAPITALS[country]==a else 'B')
        assert CAPITALS[country] in [a,b] and intended==j['expected']
        r=results[j['job_id']];assert r['transport_valid']
        jobs.append({**j,'reference':reference,'response_format':fmt,'queried_country':country,
                     'expected_label':intended,'preview_answer':r['top']['token'].strip(),
                     'preview_correct':r['correct'],'prompt_sha256':hashlib.sha256(j['prompt'].encode()).hexdigest(),
                     'preview_response_sha256':r['response_sha256']})
    assert len(jobs)==16 and len({j['prompt'] for j in jobs})==16
    for j in jobs:
        j['same_country_partner']=None;j['same_output_partner']=None
        if j['reference']!='ordinal':continue
        named=[x for x in jobs if x['reference']=='named' and x['response_format']==j['response_format']]
        same=[x for x in named if x['case']==j['case']]
        other=[x for x in named if layout(x['plain_prompt'])==layout(j['plain_prompt'])
               and x['queried_country']!=j['queried_country'] and x['preview_answer']==j['preview_answer']]
        assert len(same)==len(other)==1 and same[0]['preview_correct'] and other[0]['preview_correct']
        j['same_country_partner']=same[0]['job_id'];j['same_output_partner']=other[0]['job_id']
    return jobs


def token_roles(job):
    from tokenizers import Tokenizer
    tok=Tokenizer.from_file(str(TOKENIZER_DIR/'tokenizer.json'))
    enc=tok.encode(job['prompt'],add_special_tokens=False)
    plain=job['plain_prompt'];start=job['prompt'].index(plain);end=start+len(plain)
    spans=[]
    def span(a,b,role):spans.append((start+a,start+b,role))
    for letter in ['A','B']:
        m=re.search(rf'{letter}: ([^.]+)\.',plain)
        span(m.start(),m.start()+1,f'option_{letter}_label')
        span(m.start(1),m.end(1),f'option_{letter}_capital_{m.group(1)}')
    m=re.search(r'Countries: ([^,]+), ([^.]+)\.',plain)
    for i in [1,2]:span(m.start(i),m.end(i),f'country_list_{i}_{m.group(i)}')
    q=plain.index('Question:')
    for m in re.finditer(r'\b(first|second)\b',plain):span(m.start(),m.end(),'ordinal_'+m.group())
    for country in ['France','Germany']:
        for m in re.finditer(r'\b'+country+r'\b',plain):
            if m.start()>q:span(m.start(),m.end(),'question_country_'+country)
    rows=[]
    for i,(token_id,(a,b)) in enumerate(zip(enc.ids,enc.offsets)):
        matches=[role for x,y,role in spans if max(a,x)<min(b,y)]
        if len(set(matches))>1:raise ValueError('One token overlaps multiple semantic roles')
        fallback='chat_frame' if b<=start or a>=end else ('question_other' if a>=start+q else 'instruction_or_separator')
        rows.append(dict(token_index=i,token_id=token_id,token=tok.decode([token_id],skip_special_tokens=False),
                         char_start=a,char_end=b,role=matches[0] if matches else fallback))
    assert len(rows)+1<=64
    return rows


def freeze():
    jobs=make_jobs()
    for j in jobs:token_roles(j)
    paths=['scripts/failure_case_design.py','scripts/run_failure_case_graphs.py',
           'scripts/analyze_failure_case_graphs.py','scripts/plot_failure_case_graphs.py',
           'scripts/validate_failure_case_graphs.py','scripts/run_matched_choice_controls.py',
           'scripts/whole_graph_analysis.py','scripts/convert_model_extension.py','scripts/2_convert_graph.py',
           'scripts/control_io.py','scripts/audit_position_pilot.py','tests/test_failure_case_graphs.py',
           'scripts/matched_choice_controls.py','scripts/matched_choice_chat_controls.py',
           'scripts/analyze_matched_choice_controls.py',
           'docs/papers/FAILURE_CASE_GRAPH_ANALYSIS_PLAN.md','config/matched_choice_requirements.txt']
    record=dict(plan_sha256=digest(PLAN),source_hashes=SOURCE_HASHES,
                jobs_sha256=hashlib.sha256(json.dumps(jobs,sort_keys=True).encode()).hexdigest(),
                code_hashes={p:digest(ROOT/p) for p in paths},settings=SETTINGS,seed=SEED,
                equal_count_repetitions=200,model=MODEL,source_set='transcoder-hp',
                display_rule='Ten direct edges, then ten upstream edges into displayed direct predecessors; absolute weight, stable source/target ID ties.',
                tokenizer_hashes={n:digest(TOKENIZER_DIR/n) for n in ['tokenizer.json','tokenizer_config.json','provenance.json']},
                versions={n:importlib.metadata.version(n) for n in ['numpy','matplotlib','tokenizers','requests','PyYAML']},
                interpretation='Exploratory selected failures; no confirmatory p-values or independent-replicate claims.')
    path=OUT/'freeze.json'
    if path.exists():
        if json.loads(path.read_text())!=record:raise RuntimeError('Frozen graph diagnostic changed; review before any requests')
    else:
        atomic_json(path,record);atomic_json(OUT/'jobs.json',jobs)
        snapshot=OUT/'code_snapshot';snapshot.mkdir(exist_ok=True)
        for p in paths:shutil.copy2(ROOT/p,snapshot/p.replace('/','__'))
        for n in ['tokenizer.json','tokenizer_config.json','provenance.json']:
            shutil.copy2(TOKENIZER_DIR/n,snapshot/('qwen3-4b__'+n))
    return record,jobs
