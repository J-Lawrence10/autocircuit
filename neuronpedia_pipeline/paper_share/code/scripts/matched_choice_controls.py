"""Frozen lexical-bag x queried-country x answer-label control design."""
from collections import Counter
import csv
import hashlib
import itertools
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/model_extension/matched_choice_v1'
PROTOCOL = ROOT / 'docs/papers/MATCHED_CHOICE_CONTROL_PROTOCOL.md'
MODELS = {'qwen3-4b':'transcoder-hp', 'gemma-2-2b':'gemmascope-transcoder-16k'}
BLOCKS = [
    ('pilot_france_germany','pilot','France','Paris','Germany','Berlin'),
    ('japan_italy','held_out','Japan','Tokyo','Italy','Rome'),
    ('spain_portugal','held_out','Spain','Madrid','Portugal','Lisbon'),
    ('canada_australia','held_out','Canada','Ottawa','Australia','Canberra'),
    ('greece_austria','held_out','Greece','Athens','Austria','Vienna'),
    ('egypt_kenya','held_out','Egypt','Cairo','Kenya','Nairobi'),
    ('norway_sweden','held_out','Norway','Oslo','Sweden','Stockholm'),
]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False),encoding='utf-8')
    tmp.replace(path)


def word_bag(prompt):
    return Counter(re.findall(r'[^\W_]+', prompt.casefold()))


def make_jobs():
    jobs=[]
    for block,split,c0,a0,c1,a1 in BLOCKS:
        for fact,mapping,wording in itertools.product(range(2),repeat=3):
            country,other = (c0,c1) if fact==0 else (c1,c0)
            answer_a,answer_b = (a0,a1) if mapping==0 else (a1,a0)
            query = (f'for {country} rather than {other} what is the capital'
                     if wording==0 else f'what is the capital for {country} rather than {other}')
            prompt=f'Reply with only A or B. A: {answer_a}. B: {answer_b}. Question: {query}? Answer:'
            jobs.append(dict(job_id=f'{block}__f{fact}m{mapping}w{wording}',block=block,split=split,
                             fact=fact,mapping=mapping,wording=wording,
                             expected_label='A' if fact==mapping else 'B',queried_country=country,
                             expected_capital=a0 if fact==0 else a1,prompt=prompt,
                             prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest()))
    return jobs


def validate_design(jobs):
    from tokenizers import Tokenizer
    tokenizer_path=ROOT/'data/model_extension/exploratory_20260905/tokenizers/qwen3-4b/tokenizer.json'
    tokenizer=Tokenizer.from_file(str(tokenizer_path))
    assert len(jobs)==56 and len({j['job_id'] for j in jobs})==56
    assert len({j['prompt'] for j in jobs})==56
    blocks=[]
    for block,*_ in BLOCKS:
        rows=[j for j in jobs if j['block']==block]
        assert len(rows)==8
        assert {tuple(j[k] for k in ['fact','mapping','wording']) for j in rows}==set(itertools.product(range(2),repeat=3))
        bags=[word_bag(j['prompt']) for j in rows]
        assert all(b==bags[0] for b in bags)
        ids=[tokenizer.encode(j['prompt'],add_special_tokens=False).ids for j in rows]
        assert all(Counter(x)==Counter(ids[0]) for x in ids),block
        assert max(map(len,ids))+1<=64,block
        for j,prefix in zip(rows,ids):
            suffix=tokenizer.encode(j['prompt']+' '+j['expected_label'],add_special_tokens=False).ids
            assert suffix[:len(prefix)]==prefix and len(suffix)==len(prefix)+1
        assert Counter(j['expected_label'] for j in rows)=={'A':4,'B':4}
        blocks.append(dict(block=block,graphs_or_preflights=8,word_multiset_identical=True,
                           qwen_token_multiset_identical=True,qwen_prompt_tokens=len(ids[0]),
                           single_token_expected_labels=True))
    return dict(blocks=blocks,qwen_tokenizer_sha256=digest(tokenizer_path),
                models=MODELS,deferred={'qwen3-1.7b':'Hosted LoRSA limit 10 tokens; cannot fit this unchanged design.'})


def freeze():
    OUT.mkdir(parents=True,exist_ok=True)
    jobs=make_jobs();validation=validate_design(jobs)
    rows_json=json.dumps(jobs,sort_keys=True,separators=(',',':')).encode()
    record={'jobs_sha256':hashlib.sha256(rows_json).hexdigest(), 'protocol_sha256':digest(PROTOCOL),
            'design_script_sha256':digest(__file__),'validation':validation,
            'model_settings':{'maxNLogits':10,'desiredLogitProb':.99,'nodeThreshold':.8,
                              'edgeThreshold':.85,'maxFeatureNodes':5000},
            'seed':20260905,'post_interval_seconds':125,'requests_per_rolling_hour':30}
    path=OUT/'freeze.json'
    if path.exists() and json.loads(path.read_text())!=record:
        raise RuntimeError('Frozen design changed. Create a new version; do not overwrite this experiment.')
    atomic_json(path,record)
    atomic_json(OUT/'jobs.json',jobs)
    with (OUT/'jobs.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(jobs[0]));w.writeheader();w.writerows(jobs)
    atomic_json(OUT/'design_validation.json',validation)
    print(json.dumps(validation,indent=2))


if __name__=='__main__':
    freeze()
