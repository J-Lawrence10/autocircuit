"""Final, bounded historical-date choice design. Freeze before any hosted outcome."""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
from functools import lru_cache

import jinja2
from tokenizers import Tokenizer
from scipy.stats import t

from matched_choice_controls import ROOT, digest, word_bag
from control_io import atomic_json
from analyze_matched_choice_controls import csv_write

OUT=ROOT/'data/model_extension/history_choice_final_v1'
PROTOCOL=ROOT/'docs/papers/HISTORY_CHOICE_FINAL_PROTOCOL.md'
MODEL='qwen3-4b'
MODELS={MODEL:'transcoder-hp'}
TOKENIZER_DIR=ROOT/'data/model_extension/exploratory_20260905/tokenizers/qwen3-4b'
NARA='https://www.archives.gov/milestone-documents/'
NASA='https://nssdc.gsfc.nasa.gov/planetary/chronology.html'
# Event, year, authoritative source. Explicit action distinguishes adoption, signing, and ratification.
DOCUMENTS=[
 ('US Constitution signing',1787,NARA+'constitution'),('Bill of Rights ratification',1791,NARA+'bill-of-rights'),
 ('Louisiana Purchase treaty',1803,NARA+'list'),('Treaty of Ghent signing',1814,NARA+'list'),
 ('Guadalupe Hidalgo treaty',1848,NARA+'list'),('Homestead Act enactment',1862,NARA+'list'),
 ('Emancipation Proclamation issuance',1863,NARA+'list'),('13th Amendment ratification',1865,NARA+'13th-amendment'),
 ('14th Amendment ratification',1868,NARA+'14th-amendment'),('15th Amendment ratification',1870,NARA+'15th-amendment'),
 ('Yellowstone park establishment',1872,NARA+'list'),('Chinese Exclusion Act enactment',1882,NARA+'list'),
 ('Sherman Antitrust Act enactment',1890,NARA+'list'),('Plessy v. Ferguson decision',1896,NARA+'list'),
 ('16th Amendment ratification',1913,NARA+'16th-amendment'),('19th Amendment ratification',1920,NARA+'19th-amendment'),
 ('Social Security Act enactment',1935,NARA+'list'),('Lend-Lease Act enactment',1941,NARA+'list'),
 ('Brown v. Board decision',1954,NARA+'list'),('Civil Rights Act enactment',1964,NARA+'list'),
]
SPACE=[(event+' launch',year,NASA) for event,year in [
 ('Luna 1',1959),('Mariner 2',1962),('Ranger 7',1964),('Luna 9',1966),
 ('Venera 4',1967),('Apollo 8',1968),('Apollo 13',1970),('Mariner 9',1971),
 ('Pioneer 10',1972),('Pioneer 11',1973),('Viking 1',1975),('Voyager 1',1977),
 ('Magellan',1989),('Ulysses',1990),('Mars Pathfinder',1996),('Cassini',1997),
 ('Stardust',1999),('Mars Odyssey',2001),('Rosetta',2004),('New Horizons',2006)]]
PILOTS=[('pilot_documents','documents',('US Declaration of Independence adoption',1776,NARA+'list'),('American Revolutionary Treaty of Paris signing',1783,NARA+'list')),
        ('pilot_space','space',('Sputnik 1 launch',1957,NASA),('Explorer 1 launch',1958,NASA))]


@lru_cache(maxsize=1)
def template():
    cfg=json.loads((TOKENIZER_DIR/'tokenizer_config.json').read_text())
    return jinja2.Environment(trim_blocks=True,lstrip_blocks=True).from_string(cfg['chat_template'])


def render(plain):
    return template().render(
        messages=[{'role':'user','content':plain}],tools=None,add_generation_prompt=True,enable_thinking=False)


def make_jobs():
    blocks=[(b,'pilot',theme,a,c) for b,theme,a,c in PILOTS]
    for theme,events in [('documents',DOCUMENTS),('space',SPACE)]:
        blocks += [(f'{theme}_{i//2+1:02d}','held_out',theme,events[i],events[i+1]) for i in range(0,len(events),2)]
    jobs=[]
    for block,split,theme,a,b in blocks:
        for fact,mapping,wording in itertools.product(range(2),repeat=3):
            chosen,other=(a,b) if fact==0 else (b,a)
            ya,yb=(a[1],b[1]) if mapping==0 else (b[1],a[1])
            question=f'question: year of {chosen[0]}; context: {other[0]}.'
            if wording:question=f'context: {other[0]}; question: year of {chosen[0]}.'
            plain=f'Reply only A or B. A: {ya}. B: {yb}. {question}'
            prompt=render(plain)
            jobs.append(dict(job_id=f'{block}__f{fact}m{mapping}w{wording}',block=block,split=split,theme=theme,
                             fact=fact,mapping=mapping,wording=wording,expected_label='A' if fact==mapping else 'B',
                             event=chosen[0],year=chosen[1],source=chosen[2],plain_prompt=plain,prompt=prompt,
                             prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest()))
    for i,label in enumerate(['A','B','B','A']):
        plain=f'Reply with only the letter {label}.' if i<2 else f'The requested label is {label}. Return that label only.'
        prompt=render(plain)
        jobs.append(dict(job_id=f'literal_{i}',block='literal',split='literal',theme='instruction',fact=-1,mapping=-1,wording=i,
                         expected_label=label,event='',year=None,source='',plain_prompt=plain,prompt=prompt,
                         prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest()))
    return jobs


def validate(jobs):
    tok=Tokenizer.from_file(str(TOKENIZER_DIR/'tokenizer.json'));rows=[]
    assert len(jobs)==180 and len({j['job_id'] for j in jobs})==180
    assert len({j['prompt'] for j in jobs})==180
    for block in sorted({j['block'] for j in jobs}):
        group=[j for j in jobs if j['block']==block]
        ids=[tok.encode(j['prompt'],add_special_tokens=False).ids for j in group]
        assert max(map(len,ids))+1<=64,(block,max(map(len,ids)))
        if block!='literal':
            assert len(group)==8
            assert all(Counter(x)==Counter(ids[0]) for x in ids),(block,'token bags differ')
            assert all(word_bag(j['prompt'])==word_bag(group[0]['prompt']) for j in group)
            assert len({j['year'] for j in group})==2
        for j,prefix in zip(group,ids):
            continuation=tok.encode(j['prompt']+j['expected_label'],add_special_tokens=False).ids
            assert continuation[:len(prefix)]==prefix and len(continuation)==len(prefix)+1
        rows.append(dict(block=block,split=group[0]['split'],n=len(group),max_tokens=max(map(len,ids)),
                         matched_inventory=block!='literal'))
    evaluation={j['event'] for j in jobs if j['split']=='held_out'}
    pilot={j['event'] for j in jobs if j['split']=='pilot'}
    assert len(evaluation)==40 and not evaluation & pilot
    return rows


def freeze():
    from datetime import datetime,timezone
    jobs=make_jobs();validation=validate(jobs)
    files=[PROTOCOL,Path(__file__),ROOT/'scripts/run_history_closeout.py',ROOT/'scripts/analyze_history_closeout.py',
           ROOT/'scripts/run_matched_choice_controls.py',ROOT/'scripts/analyze_matched_choice_controls.py',
           ROOT/'scripts/convert_model_extension.py',ROOT/'scripts/2_convert_graph.py',ROOT/'scripts/whole_graph_analysis.py',
           ROOT/'scripts/control_io.py',ROOT/'scripts/audit_paper_closeout.py',ROOT/'scripts/matched_choice_controls.py',
           TOKENIZER_DIR/'tokenizer.json',TOKENIZER_DIR/'tokenizer_config.json']
    record=dict(file_hashes={str(p.relative_to(ROOT)):digest(p) for p in files},
                jobs_sha256=hashlib.sha256(json.dumps(jobs,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                models=MODELS,validation=validation,seed=20261005,
                settings=dict(maxNLogits=10,desiredLogitProb=.99,nodeThreshold=.8,edgeThreshold=.85,maxFeatureNodes=5000),
                n_blocks=20,min_correct_blocks=16,min_correct_blocks_per_theme=6,
                precision=dict(assumed_sd=.05,target_halfwidth=.025,n=20,t_halfwidth=float(t.ppf(.975,19)*.05/(20**.5))),
                post_interval_seconds=125,requests_per_rolling_hour=30,planned_primary_family_size=1)
    path=OUT/'freeze.json'
    if path.exists():
        old=json.loads(path.read_text());stamp=old.pop('frozen_at');assert old==record,'Frozen design changed'
        record['frozen_at']=stamp
    else:record['frozen_at']=datetime.now(timezone.utc).isoformat()
    atomic_json(path,record);atomic_json(OUT/'jobs.json',jobs);csv_write(OUT/'jobs.csv',jobs)
    atomic_json(OUT/'design_validation.json',validation)
    csv_write(OUT/'historical_sources.csv',[dict(event=e,year=y,source=s,checked_date='2026-10-05') for e,y,s in DOCUMENTS+SPACE+[x for _,_,a,b in PILOTS for x in [a,b]]])
    print(json.dumps(record,indent=2))


if __name__=='__main__':freeze()
