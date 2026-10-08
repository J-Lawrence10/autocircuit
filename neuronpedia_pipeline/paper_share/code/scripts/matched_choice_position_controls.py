"""Final v3: query identity x answer mapping x queried-list position x wording."""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))

from matched_choice_controls import ROOT, BLOCKS, digest, word_bag
from matched_choice_chat_controls import TOKENIZER_DIR
from control_io import atomic_json

OUT = ROOT / 'data/model_extension/matched_choice_position_v3'
PROTOCOL = ROOT / 'docs/papers/MATCHED_CHOICE_POSITION_V3_PROTOCOL.md'
MODELS = {'qwen3-4b': 'transcoder-hp'}
SEED = 20260909


def make_jobs():
    import jinja2
    cfg = json.loads((TOKENIZER_DIR / 'tokenizer_config.json').read_text())
    template = jinja2.Environment(trim_blocks=True, lstrip_blocks=True).from_string(cfg['chat_template'])
    jobs = []
    for block, split, c0, a0, c1, a1 in BLOCKS:
        for fact, mapping, position, wording in itertools.product(range(2), repeat=4):
            countries = [c0, c1] if fact == position else [c1, c0]
            options = [a0, a1] if mapping == 0 else [a1, a0]
            ordinal, other = ('first', 'second') if position == 0 else ('second', 'first')
            clause = f'for the {ordinal} country, not the {other}'
            query = (f'what is the capital {clause}' if wording == 0 else
                     f'for the {ordinal} country not the {other}, what is the capital')
            plain = (f'Reply with only A or B. A: {options[0]}. B: {options[1]}. '
                     f'Countries: {countries[0]}, {countries[1]}. Question: {query}? Answer:')
            prompt = template.render(messages=[{'role':'user', 'content':plain}], tools=None,
                                     add_generation_prompt=True, enable_thinking=False)
            jobs.append(dict(job_id=f'{block}__f{fact}m{mapping}p{position}w{wording}', block=block,
                             split=split, fact=fact, mapping=mapping, position=position, wording=wording,
                             queried_country=[c0,c1][fact], expected_capital=[a0,a1][fact],
                             country_list=countries, expected_label='A' if fact==mapping else 'B',
                             plain_prompt=plain, prompt=prompt,
                             prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest()))
    return jobs


def validate_design(jobs):
    from tokenizers import Tokenizer
    tokenizer = Tokenizer.from_file(str(TOKENIZER_DIR / 'tokenizer.json'))
    assert len(jobs)==112 and len({j['prompt'] for j in jobs})==112
    assert len({j['job_id'] for j in jobs})==112
    rows_out = []
    for block in sorted({j['block'] for j in jobs}):
        rows = [j for j in jobs if j['block']==block]
        assert {tuple(j[k] for k in ('fact','mapping','position','wording')) for j in rows} == set(itertools.product(range(2),repeat=4))
        ids = [tokenizer.encode(j['prompt'],add_special_tokens=False).ids for j in rows]
        assert all(Counter(x)==Counter(ids[0]) for x in ids), (block,'token bags differ')
        assert all(word_bag(j['prompt'])==word_bag(rows[0]['prompt']) for j in rows)
        assert max(map(len,ids))+1<=64
        for j, prefix in zip(rows,ids):
            suffix = tokenizer.encode(j['prompt']+j['expected_label'],add_special_tokens=False).ids
            assert suffix[:len(prefix)]==prefix and len(suffix)==len(prefix)+1
            assert j['country_list'][j['position']]==j['queried_country']
        rows_out.append(dict(block=block,n=16,input_tokens=len(ids[0]),identical_token_bags=True))
    return rows_out


def frozen_record():
    import jinja2
    jobs = make_jobs()
    code = ['scripts/matched_choice_position_controls.py','scripts/analyze_position_controls.py',
            'scripts/matched_choice_controls.py','scripts/matched_choice_chat_controls.py',
            'scripts/analyze_matched_choice_controls.py','scripts/whole_graph_analysis.py',
            'scripts/convert_model_extension.py','scripts/2_convert_graph.py']
    return dict(jobs_sha256=hashlib.sha256(json.dumps(jobs,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                protocol_sha256=digest(PROTOCOL), frozen_code={p:digest(ROOT/p) for p in code},
                tokenizer_sha256=digest(TOKENIZER_DIR/'tokenizer.json'),
                tokenizer_config_sha256=digest(TOKENIZER_DIR/'tokenizer_config.json'),
                jinja2_version=jinja2.__version__, validation=validate_design(jobs), models=MODELS,
                model_settings=dict(maxNLogits=10,desiredLogitProb=.99,nodeThreshold=.8,edgeThreshold=.85,maxFeatureNodes=5000),
                seed=SEED,post_interval_seconds=125,requests_per_rolling_hour=30,planned_primary_family_size=4)


def freeze():
    import csv
    record = frozen_record()
    path = OUT/'freeze.json'
    if path.exists() and json.loads(path.read_text())!=record:
        raise RuntimeError('Frozen v3 design/analysis changed; do not overwrite.')
    atomic_json(path,record)
    jobs = make_jobs()
    atomic_json(OUT/'jobs.json',jobs)
    with (OUT/'jobs.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(jobs[0]));writer.writeheader();writer.writerows(jobs)
    print(json.dumps(record['validation'],indent=2))


if __name__=='__main__':
    freeze()
