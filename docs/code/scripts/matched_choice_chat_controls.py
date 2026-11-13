"""Version 2: identical choice design in Qwen's official no-thinking chat frame."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

from matched_choice_controls import ROOT, make_jobs as plain_jobs, word_bag, digest, atomic_json

OUT=ROOT/'data/model_extension/matched_choice_chat_v2'
PROTOCOL=ROOT/'docs/papers/MATCHED_CHOICE_CHAT_V2_PROTOCOL.md'
MODELS={'qwen3-4b':'transcoder-hp'}
TOKENIZER_DIR=ROOT/'data/model_extension/exploratory_20260905/tokenizers/qwen3-4b'


def make_jobs():
    import jinja2
    cfg=json.loads((TOKENIZER_DIR/'tokenizer_config.json').read_text())
    template=jinja2.Environment(trim_blocks=True,lstrip_blocks=True).from_string(cfg['chat_template'])
    jobs=[]
    for job in plain_jobs():
        prompt=template.render(messages=[{'role':'user','content':job['prompt']}],tools=None,
                               add_generation_prompt=True,enable_thinking=False)
        jobs.append({**job,'plain_prompt':job['prompt'],'prompt':prompt,
                     'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()})
    return jobs


def freeze():
    from tokenizers import Tokenizer
    import jinja2
    jobs=make_jobs();tokenizer=Tokenizer.from_file(str(TOKENIZER_DIR/'tokenizer.json'));validation=[]
    for block in sorted({j['block'] for j in jobs}):
        rows=[j for j in jobs if j['block']==block]
        encoded=[tokenizer.encode(j['prompt'],add_special_tokens=False).ids for j in rows]
        assert all(Counter(x)==Counter(encoded[0]) for x in encoded)
        assert all(word_bag(j['prompt'])==word_bag(rows[0]['prompt']) for j in rows)
        assert len(encoded[0])+1<=64
        for j,ids in zip(rows,encoded):
            continuation=tokenizer.encode(j['prompt']+j['expected_label'],add_special_tokens=False).ids
            assert continuation[:len(ids)]==ids and len(continuation)==len(ids)+1
        validation.append(dict(block=block,qwen_tokens=len(encoded[0]),identical_word_and_token_bags=True))
    record=dict(jobs_sha256=hashlib.sha256(json.dumps(jobs,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                protocol_sha256=digest(PROTOCOL),design_script_path='scripts/matched_choice_chat_controls.py',
                design_script_sha256=digest(__file__),base_design_sha256=digest(ROOT/'scripts/matched_choice_controls.py'),
                tokenizer_sha256=digest(TOKENIZER_DIR/'tokenizer.json'),tokenizer_config_sha256=digest(TOKENIZER_DIR/'tokenizer_config.json'),
                jinja2_version=jinja2.__version__,models=MODELS,validation=validation,planned_primary_family_size=3,
                model_settings=dict(maxNLogits=10,desiredLogitProb=.99,nodeThreshold=.8,edgeThreshold=.85,maxFeatureNodes=5000),
                seed=20260905,post_interval_seconds=125,requests_per_rolling_hour=30)
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/'freeze.json'
    if path.exists() and json.loads(path.read_text())!=record:
        raise RuntimeError('Frozen chat v2 design changed; create a new version.')
    atomic_json(path,record);atomic_json(OUT/'jobs.json',jobs)
    with (OUT/'jobs.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(jobs[0]));w.writeheader();w.writerows(jobs)
    atomic_json(OUT/'design_validation.json',validation)
    print(json.dumps(validation,indent=2))


if __name__=='__main__':freeze()
