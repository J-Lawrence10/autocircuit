#!/usr/bin/env python3
"""Post-hoc, CPU-only sensitivities; never changes primary eligibility or files."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import re
import sys
import time
import urllib.request

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from whole_graph_analysis import is_feature_node, node_identity, jaccard, bootstrap_ci

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/model_extension/exploratory_20260905'
PLAN = ROOT / 'docs/papers/EXPLORATORY_CONFOUND_CHECKS_20260905.md'
SEED = 20260905
MODELS = ['gemma-2-2b', 'qwen3-1.7b', 'qwen3-4b']
REPOS = dict(zip(MODELS, ['google/gemma-2-2b', 'Qwen/Qwen3-1.7B', 'Qwen/Qwen3-4B']))
PRIMARY = 'feature_jaccard__margin_other_factual_mean'
SOURCES = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    path = Path(path)
    data = path.read_bytes()
    SOURCES[str(path.relative_to(ROOT))] = sha(data)
    return json.loads(data)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False), encoding='utf-8')


def write_csv(name, rows):
    path = OUT / f'{name}.csv'
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows({k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in r.items()} for r in rows)


def local_path(value):
    # Archived Windows absolute paths remain portable after moving the repository.
    value = str(value).replace('\\', '/')
    if '/data/' in value:
        value = 'data/' + value.split('/data/', 1)[1]
    return ROOT / value


def words(prompt):
    return set(re.findall(r'[^\W_]+', prompt.casefold(), flags=re.UNICODE))


def brief(values):
    values = list(map(float, values))
    return {'n': len(values), 'mean': float(np.mean(values)) if values else None,
            'positive_n': sum(v > 0 for v in values),
            'ci95_descriptive': bootstrap_ci(values, runs=10000, seed=SEED) if len(values) >= 2 else None}


def features(nodes):
    ids = Counter(str(n.get('node_id', n.get('id', ''))) for n in nodes)
    return {node_identity(n) for n in nodes
            if ids[str(n.get('node_id', n.get('id', '')))] == 1
            and str(n.get('node_id', n.get('id', ''))) and is_feature_node(n)}


def logit_record(nodes):
    logits = [n for n in nodes if n.get('feature_type', n.get('node_type')) == 'logit']
    if not logits:
        return {'top_id': None, 'top_text': None, 'top_probability': None}
    top = max(logits, key=lambda n: float(n.get('token_prob', n.get('token_probability', 0)) or 0))
    token = top.get('token')
    if token is None:
        match = re.search(r'(?:Output|Logit) "(.*)" \(p=', str(top.get('clerp', '')), flags=re.DOTALL)
        token = match.group(1) if match else None
    return {'top_id': int(top.get('feature', top.get('feature_id'))),
            'top_text': token, 'top_probability': top.get('token_prob', top.get('token_probability'))}


def inventory():
    raw = read(ROOT / 'data/publication_analysis/raw_graph_audit.json')
    converted = read(ROOT / 'data/publication_analysis/converted_graph_audit.json')
    conv_index = {(r['model_dir'], r['pair_id'], r['role']): r for r in converted if r['status'] == 'ok'}
    fmt = read(ROOT / 'data/publication_analysis/format_graph_audit.json')
    ext_audit = read(ROOT / 'data/model_extension/qwen3-4b/analysis/graph_audit.json')
    ext_index = {r['job_id']: r for r in ext_audit}
    jobs_path = ROOT / 'data/model_extension/qwen3-4b/jobs.csv'
    checks_path = ROOT / 'data/model_extension/qwen3-4b/checksums.csv'
    SOURCES[str(jobs_path.relative_to(ROOT))] = sha(jobs_path.read_bytes())
    SOURCES[str(checks_path.relative_to(ROOT))] = sha(checks_path.read_bytes())
    jobs = list(csv.DictReader(jobs_path.open(newline='', encoding='utf-8')))
    checks = {str(local_path(r['path'])): r['sha256'] for r in csv.DictReader(checks_path.open(newline='', encoding='utf-8'))}
    crossed_expected = {(r['domain'], r['fact_id'], r['format']): r['expected_token'] for r in jobs if r['design'] == 'crossed'}
    rows = []
    for r in raw:
        if r['status'] != 'ok':
            continue
        c = conv_index[(r['model_dir'], r['pair_id'], r['role'])]
        rows.append(dict(model=r['model_dir'].replace('qwen3-1-7b', 'qwen3-1.7b'), design='controlled',
                         fact=r['pair_id'], role=r['role'], format='', domain=r['domain'], split=r['split'],
                         expected=r['expected_token'], manifest_prompt=r['manifest_prompt'],
                         path=str(local_path(r['path'])), sha256=r['sha256'],
                         archived_feature_count=c['unique_feature_identity_count'], archived_top=c['top_token']))
    for r in fmt:
        rows.append(dict(model=MODELS[0], design='crossed', fact=r['fact'], role='', format=r['format'],
                         domain=r['domain'], split='crossed', expected=crossed_expected[(r['domain'], r['fact'], r['format'])],
                         manifest_prompt=r['prompt'], path=str(local_path(r['path'])), sha256=r['sha256'],
                         archived_feature_count=r['unique_feature_identity_count']))
    for r in jobs:
        p = local_path(r['raw_graph_path'])
        a = ext_index[r['job_id']]
        rows.append(dict(model=MODELS[2], design=r['design'], fact=r['fact_id'], role=r['role'], format=r['format'],
                         domain=r['domain'], split=r['split'], expected=r['expected_token'], manifest_prompt=r['prompt'],
                         path=str(p), sha256=checks.get(str(p)), archived_feature_count=a.get('unique_feature_identity_count'),
                         archived_top=a.get('top_token'), archived_status=a['status']))
    return rows


def load_graphs(rows):
    cache_dir = OUT / 'representation_cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    result = []
    for i, r in enumerate(rows):
        if not r['sha256']:
            result.append({**r, 'status': 'missing_raw'})
            continue
        # Cache is keyed by raw hash; primary-margin and count reconciliation also run on reuse.
        cache = cache_dir / (r['sha256'] + '.json')
        if cache.exists():
            parsed = json.loads(cache.read_text())
        else:
            payload = Path(r['path']).read_bytes()
            if sha(payload) != r['sha256']:
                raise ValueError(f'Raw checksum mismatch: {r["path"]}')
            g = json.loads(payload)
            m = g['metadata']
            parsed = dict(feature_ids=sorted(features(g['nodes'])), prompt=m['prompt'],
                          prompt_tokens=m.get('prompt_tokens'), **logit_record(g['nodes']))
            write_json(cache, parsed)
        r = {**r, **parsed, 'status': 'ok'}
        r['features'] = {tuple(x) for x in r.pop('feature_ids')}
        if r['archived_feature_count'] != len(r['features']):
            raise ValueError(f'Representation count changed: {r["model"]} {r["fact"]} {r["role"]}')
        if r.get('archived_top') is not None and r['archived_top'] != r['top_text']:
            raise ValueError(f'Top output changed: {r["path"]}')
        result.append(r)
        if (i + 1) % 30 == 0:
            print(f'Read and reconciled {i+1}/{len(rows)} graph records', flush=True)
    return result


def primary_results():
    a = read(ROOT / 'data/publication_analysis/whole_graph_results.json')
    b = read(ROOT / 'data/model_extension/qwen3-4b/analysis/model_extension_results.json')
    return dict(zip(MODELS, [a['models']['gemma'], a['models']['qwen'], b['controlled']]))


def pair_table(graphs, saved):
    rows = []
    eligible = {}
    for model in MODELS:
        selected = [r for r in saved[model]['per_fact'] if r['split'] == 'held_out']
        eligible[model] = selected
        lookup = {(g['fact'], g['role']): g for g in graphs if g['model'] == model and g['design'] == 'controlled' and g['status'] == 'ok'}
        for r in selected:
            fact = r['pair_id']; target = lookup[(fact, 'target')]; own = lookup[(fact, 'positive_paraphrase')]
            same_stratum = [x for x in selected if x['domain'] == r['domain']]
            local = []
            for candidate in same_stratum:
                p = lookup[(candidate['pair_id'], 'positive_paraphrase')]
                local.append(dict(model=model, domain=r['domain'], target_fact=fact, candidate_fact=candidate['pair_id'],
                                  same_fact=fact == candidate['pair_id'], feature_jaccard=jaccard(target['features'], p['features']),
                                  word_jaccard=jaccard(words(target['manifest_prompt']), words(p['manifest_prompt'])),
                                  target_n=len(target['features']), candidate_n=len(p['features']), own_n=len(own['features']),
                                  same_expected_answer=target['expected'] == p['expected']))
            margin = next(v['feature_jaccard'] for v in local if v['same_fact']) - np.mean([v['feature_jaccard'] for v in local if not v['same_fact']])
            if not np.isclose(margin, r[PRIMARY], atol=1e-12, rtol=0):
                raise ValueError(f'Primary mismatch: {model} {fact}: {margin} != {r[PRIMARY]}')
            rows.extend(local)
    return rows, eligible


def lexical_checks(pairs):
    rows = []
    rules = {
        'at_least_own_overlap': lambda p, own: p['word_jaccard'] >= own['word_jaccard'] - 1e-12,
        'word_caliper_0.05': lambda p, own: abs(p['word_jaccard'] - own['word_jaccard']) <= .05 + 1e-12,
        'word_and_size_caliper': lambda p, own: abs(p['word_jaccard'] - own['word_jaccard']) <= .05 + 1e-12 and abs(math.log(p['candidate_n'] / own['candidate_n'])) <= math.log(1.25) + 1e-12,
    }
    groups = defaultdict(list)
    for p in pairs:
        groups[(p['model'], p['target_fact'])].append(p)
    for (model, fact), candidates in groups.items():
        own = next(p for p in candidates if p['same_fact'])
        for rule, fn in rules.items():
            matched = [p for p in candidates if not p['same_fact'] and fn(p, own)]
            rows.append(dict(model=model, fact=fact, domain=own['domain'], rule=rule, own_word_overlap=own['word_jaccard'],
                             comparator_n=len(matched), comparator_facts=[p['candidate_fact'] for p in matched],
                             matched_word_overlap=float(np.mean([p['word_jaccard'] for p in matched])) if matched else None,
                             matched_same_answer_n=sum(p['same_expected_answer'] for p in matched),
                             margin=own['feature_jaccard'] - float(np.mean([p['feature_jaccard'] for p in matched])) if matched else None))
    summaries = [{**dict(model=m, rule=rule, eligible_n=len(groups_for_model(groups, m))),
                  **brief(r['margin'] for r in rows if r['model'] == m and r['rule'] == rule and r['margin'] is not None)}
                 for m in MODELS for rule in rules]
    return rows, summaries


def groups_for_model(groups, model):
    return [k for k in groups if k[0] == model]


def size_checks(graphs, eligible, runs):
    rows, reps, strata = [], [], []
    rng = np.random.default_rng(SEED)
    for model in MODELS:
        available = {(g['fact'], g['role']): g for g in graphs if g['status'] == 'ok' and g['model'] == model and g['design'] == 'controlled'}
        blocks = defaultdict(list)
        for r in eligible[model]:
            blocks[r['domain']].append(r['pair_id'])
        for fraction in [1.0, .5]:
            values = defaultdict(list)
            for domain, facts in sorted(blocks.items()):
                arrays = {(f, role): sorted(available[(f, role)]['features']) for f in sorted(facts) for role in ['target', 'positive_paraphrase']}
                minimum = min(map(len, arrays.values()))
                k = max(1, int(minimum * fraction))
                strata.append(dict(model=model, domain=domain, fraction=fraction, minimum_n=minimum, sampled_k=k, facts=len(facts)))
                for rep in range(runs):
                    sampled = {key: {arr[j] for j in rng.choice(len(arr), size=k, replace=False)} for key, arr in arrays.items()}
                    for fact in sorted(facts):
                        a = sampled[(fact, 'target')]
                        margin = jaccard(a, sampled[(fact, 'positive_paraphrase')]) - np.mean([jaccard(a, sampled[(f, 'positive_paraphrase')]) for f in facts if f != fact])
                        values[fact].append(float(margin))
            for fact, vals in values.items():
                rows.append(dict(model=model, fact=fact, fraction=fraction, runs=runs, mean_margin=float(np.mean(vals)),
                                 resampling_sd=float(np.std(vals, ddof=1))))
            for rep in range(runs):
                reps.append(dict(model=model, fraction=fraction, repetition=rep, pooled_mean=float(np.mean([v[rep] for v in values.values()]))))
    summaries = []
    for model in MODELS:
        for fraction in [1.0, .5]:
            values = [r['mean_margin'] for r in rows if r['model'] == model and r['fraction'] == fraction]
            pooled = [r['pooled_mean'] for r in reps if r['model'] == model and r['fraction'] == fraction]
            summaries.append(dict(model=model, fraction=fraction, **brief(values),
                                  resampling_mean_range=[min(pooled), max(pooled)],
                                  resampling_95pct_range=list(map(float, np.quantile(pooled, [.025, .975])))))
    return rows, reps, strata, summaries


def tokenizer_files(download):
    from tokenizers import Tokenizer
    loaded, status = {}, {}
    for model, repo in REPOS.items():
        folder = OUT / 'tokenizers' / model
        record_path = folder / 'provenance.json'
        if record_path.exists():
            info = json.loads(record_path.read_text())
        else:
            info = {'repository': repo, 'status': 'not_downloaded'}
        if info['status'] != 'ok' and download:
            folder.mkdir(parents=True, exist_ok=True)
            try:
                # Public official files only; no credentials, mirrors, remote code, or weights.
                with urllib.request.urlopen(f'https://huggingface.co/api/models/{repo}', timeout=45) as response:
                    revision = json.load(response)['sha']
                info.update(revision=revision, file_hashes={})
                for filename in ['tokenizer.json', 'tokenizer_config.json']:
                    url = f'https://huggingface.co/{repo}/resolve/{revision}/{filename}'
                    with urllib.request.urlopen(url, timeout=60) as response:
                        payload = response.read()
                    (folder / filename).write_bytes(payload)
                    info['file_hashes'][filename] = sha(payload)
                info['status'] = 'ok'
            except Exception as e:
                info.update(status='unavailable', error=f'{type(e).__name__}: {e}')
            write_json(record_path, info)
        if info['status'] == 'ok':
            for filename, expected in info['file_hashes'].items():
                if sha((folder / filename).read_bytes()) != expected:
                    raise ValueError(f'Tokenizer checksum mismatch: {model}/{filename}')
            loaded[model] = Tokenizer.from_file(str(folder / 'tokenizer.json'))
        status[model] = info
        print(f'Tokenizer {model}: {info["status"]}', flush=True)
    return loaded, status


def answer_check(graph, tokenizer):
    result = {'strict_string_match': (graph.get('top_text') or '').strip() == graph['expected'].strip(),
              'answer_status': 'tokenizer_unavailable', 'prompt_pieces_match': None, 'logit_decode_matches': None}
    if tokenizer is None:
        return result
    prompt = graph['prompt']
    ids = tokenizer.encode(prompt, add_special_tokens=False).ids
    pieces = [tokenizer.decode([i], skip_special_tokens=False) for i in ids]
    result['prompt_pieces_match'] = pieces == graph.get('prompt_tokens')
    result['logit_decode_matches'] = tokenizer.decode([graph['top_id']], skip_special_tokens=False) == graph.get('top_text')
    if not result['prompt_pieces_match'] or not result['logit_decode_matches']:
        result['answer_status'] = 'unresolved_tokenizer_validation'
        return result
    continuations = []
    for separator in ([''] if prompt[-1:].isspace() else ['', ' ']):
        full = tokenizer.encode(prompt + separator + graph['expected'], add_special_tokens=False).ids
        prefix_ok = full[:len(ids)] == ids
        suffix = full[len(ids):] if prefix_ok else []
        continuations.append(dict(separator=repr(separator), prefix_ok=prefix_ok, expected_ids=suffix,
                                  first_id_matches=bool(suffix) and suffix[0] == graph['top_id']))
    result['continuations'] = continuations
    matches = [c for c in continuations if c['first_id_matches']]
    if matches:
        if graph['top_text'].isspace():
            result['answer_status'] = 'whitespace_only_compatible'
        elif any(len(c['expected_ids']) == 1 for c in matches):
            result['answer_status'] = 'whole_answer_next_token'
        else:
            result['answer_status'] = 'multi_token_prefix_only'
    else:
        result['answer_status'] = 'next_token_mismatch' if all(c['prefix_ok'] for c in continuations) else 'unresolved_token_boundary'
    return result


def answer_audit(graphs, tokenizers):
    rows = []
    for g in graphs:
        row = {k: g.get(k) for k in ['model', 'design', 'fact', 'role', 'format', 'domain', 'split', 'expected', 'prompt', 'top_id', 'top_text', 'status']}
        if g['status'] != 'ok':
            row.update(answer_status='missing_graph', strict_string_match=None)
        elif g['design'] == 'controlled' and g['role'] not in ['target', 'positive_paraphrase']:
            row.update(answer_status='nonce_control_not_scored', strict_string_match=None)
        else:
            row.update(answer_check(g, tokenizers.get(g['model'])))
        rows.append(row)
    summaries = []
    for model in MODELS:
        for design in ['controlled', 'crossed']:
            selected = [r for r in rows if r['model'] == model and r['design'] == design and (design == 'crossed' or r['role'] in ['target', 'positive_paraphrase'])]
            summaries.append(dict(model=model, design=design, planned_or_available_records=len(selected),
                                  strict_matches=sum(r['strict_string_match'] is True for r in selected),
                                  statuses=dict(Counter(r['answer_status'] for r in selected))))
    return rows, summaries


def crossed_support(graphs, answers):
    rows = []
    for model in [MODELS[0], MODELS[2]]:
        for domain in ['chemistry', 'geography', 'history']:
            selected = [r for r in answers if r['model'] == model and r['design'] == 'crossed' and r['domain'] == domain]
            passed = len(selected) == 9 and all(r['strict_string_match'] is True for r in selected)
            record = dict(model=model, domain=domain, graphs=len(selected), strict_match_n=sum(r['strict_string_match'] is True for r in selected), fully_balanced_strict_subset=passed)
            if passed:
                gs = [g for g in graphs if g['model'] == model and g['design'] == 'crossed' and g['domain'] == domain]
                cats = defaultdict(list)
                for i, a in enumerate(gs):
                    for b in gs[i+1:]:
                        cat = 'fact' if a['fact'] == b['fact'] else 'wording' if a['format'] == b['format'] else 'baseline'
                        cats[cat].append(jaccard(a['features'], b['features']))
                record.update(fact_effect=float(np.mean(cats['fact']) - np.mean(cats['baseline'])),
                              wording_effect=float(np.mean(cats['wording']) - np.mean(cats['baseline'])))
            rows.append(record)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download-tokenizers', action='store_true')
    parser.add_argument('--resamples', type=int, default=200)
    args = parser.parse_args()
    if args.resamples < 2:
        parser.error('--resamples must be at least 2')
    start = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    SOURCES[str(PLAN.relative_to(ROOT))] = sha(PLAN.read_bytes())
    specs = inventory(); graphs = load_graphs(specs); saved = primary_results()
    pairs, eligible = pair_table(graphs, saved)
    print('All 23 archived held-out primary margins reproduced from raw feature identities', flush=True)
    lexical, lex_summary = lexical_checks(pairs)
    sizes, repetitions, strata, size_summary = size_checks(graphs, eligible, args.resamples)
    tokenizers, token_status = tokenizer_files(args.download_tokenizers)
    answers, answer_summary = answer_audit(graphs, tokenizers)
    crossed = crossed_support(graphs, answers)
    for name, rows in [('graph_inventory', specs), ('pairwise_lexical_and_size', pairs), ('lexical_per_fact', lexical),
                       ('size_per_fact', sizes), ('size_repetitions', repetitions), ('size_strata', strata),
                       ('answer_audit', answers), ('crossed_output_support', crossed)]:
        write_csv(name, rows)
    result = dict(exploratory=True, seed=SEED, resamples=args.resamples, source_hashes=SOURCES,
                  raw_input_hashes={str(local_path(r['path']).relative_to(ROOT)): r['sha256'] for r in specs if r['sha256']},
                  script_sha256=sha(Path(__file__).read_bytes()), python=platform.python_version(), numpy=np.__version__,
                  duration_seconds=time.time()-start, primary_reconciliation={m:len(eligible[m]) for m in MODELS},
                  package_versions={name:importlib.metadata.version(name) for name in ['numpy', 'tokenizers', 'matplotlib']},
                  representation_cache_hashes={p.name:sha(p.read_bytes()) for p in sorted((OUT / 'representation_cache').glob('*.json'))},
                  lexical=lex_summary, size=size_summary, tokenizer_provenance=token_status,
                  answers=answer_summary, crossed_output_support=crossed,
                  caveats=['No primary eligibility or gates changed.', 'Descriptive exploratory intervals; no new confirmatory p-values.',
                           'Subsampling controls observed cardinality, not selection or lexical content.',
                           'Tokenizer-confirmed partial answers are not verified full answers.',
                           'Cached representations are reused by raw hash; delete cache to force a fresh raw-file read.'])
    write_json(OUT / 'results.json', result)
    print(json.dumps({k:result[k] for k in ['lexical', 'size', 'answers', 'crossed_output_support']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
