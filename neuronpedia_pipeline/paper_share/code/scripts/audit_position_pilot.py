"""Independent text-based scoring and transport audit; never modifies frozen runs."""
from collections import Counter
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from matched_choice_controls import ROOT, digest
from matched_choice_chat_controls import TOKENIZER_DIR
from control_io import atomic_json

SOURCE=ROOT/'data/model_extension/matched_choice_position_v3'
OUT=ROOT/'data/model_extension/position_artifact_diagnostic_20261001'
CAPITALS=dict(France='Paris',Germany='Berlin',Japan='Tokyo',Italy='Rome',Spain='Madrid',
              Portugal='Lisbon',Canada='Ottawa',Australia='Canberra',Greece='Athens',
              Austria='Vienna',Egypt='Cairo',Kenya='Nairobi',Norway='Oslo',Sweden='Stockholm')


def score_prompt_text(plain):
    # Deliberately do not use fact, mapping, position, expected_label or make_jobs.
    a,b=re.search(r'A: ([^.]+)\. B: ([^.]+)\.',plain).groups()
    countries=re.search(r'Countries: ([^,]+), ([^.]+)\.',plain).groups()
    ordinal=re.search(r'for the (first|second) country',plain).group(1)
    country=countries[0 if ordinal=='first' else 1]
    capital=CAPITALS[country]
    if capital not in (a,b) or a==b:raise ValueError('Invalid options')
    return dict(country=country,capital=capital,expected_label='A' if a==capital else 'B',ordinal=ordinal)


def audit():
    from tokenizers import Tokenizer
    tokenizer=Tokenizer.from_file(str(TOKENIZER_DIR/'tokenizer.json'))
    jobs=json.loads((SOURCE/'jobs.json').read_text());rows=[]
    for job in jobs:
        oracle=score_prompt_text(job['plain_prompt'])
        row=dict(job_id=job['job_id'],split=job['split'],**oracle,
                 expected_label_matches=oracle['expected_label']==job['expected_label'],
                 country_matches=oracle['country']==job['queried_country'],
                 capital_matches=oracle['capital']==job['expected_capital'])
        if job['split']=='pilot':
            folder=SOURCE/'qwen3-4b/pilot'/job['job_id']
            response=json.loads((folder/'response.json').read_text())
            request=json.loads((folder/'request_state.json').read_text())
            ids=tokenizer.encode(job['prompt'],add_special_tokens=False).ids
            pieces=[tokenizer.decode([i],skip_special_tokens=False) for i in ids]
            top=max(response['salient_logits'],key=lambda r:r['probability'])
            row.update(request_prompt_matches=request['payload']['prompt']==job['prompt'],
                       response_prompt_matches=response['prompt']==job['prompt'],
                       exact_token_sequence_matches=response['input_tokens']==pieces,
                       top_id_matches_text=tokenizer.decode([top['token_id']],skip_special_tokens=False)==top['token'],
                       observed=top['token'].strip(),correct=top['token'].strip()==oracle['expected_label'],
                       ordinal_label_heuristic_matches=top['token'].strip()==('A' if oracle['ordinal']=='first' else 'B'),
                       response_sha256=digest(folder/'response.json'),request_sha256=digest(folder/'request_state.json'))
        rows.append(row)
    freeze=json.loads((SOURCE/'freeze.json').read_text())
    checks={p:digest(ROOT/p)==sha for p,sha in freeze['frozen_code'].items()}
    checks['protocol']=digest(ROOT/'docs/papers/MATCHED_CHOICE_POSITION_V3_PROTOCOL.md')==freeze['protocol_sha256']
    pilots=[r for r in rows if r['split']=='pilot']
    fields=['expected_label_matches','country_matches','capital_matches','request_prompt_matches',
            'response_prompt_matches','exact_token_sequence_matches','top_id_matches_text']
    failures=[dict(job_id=r['job_id'],check=k) for r in rows for k in fields if k in r and not r[k]]
    result=dict(n_jobs=len(rows),n_pilot=len(pilots),correct=sum(r['correct'] for r in pilots),
                ordinal_label_heuristic_matches=sum(r['ordinal_label_heuristic_matches'] for r in pilots),
                local_audit_failures=failures,frozen_files_match=checks,rows=rows,
                limitations='Local audit cannot independently certify hosted weights, numerical backend, or deployment identity. Ordinal-label agreement is observed behavior, not proof of its internal cause.')
    atomic_json(OUT/'local_audit.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
    return result


if __name__=='__main__':audit()
