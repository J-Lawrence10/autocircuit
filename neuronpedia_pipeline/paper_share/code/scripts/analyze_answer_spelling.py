"""Post hoc accepted-answer spelling sensitivity using saved graphs only."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unicodedata

import numpy as np

from analyze_model_extension import load_representations, write_csv
from complete_qwen4_controls import ROOT, OUT as RECOVERY, digest, read_csv
from control_io import atomic_json
from run_matched_choice_controls import now
from whole_graph_analysis import analyze_controlled, jaccard, json_ready, SIMILARITIES

OUT = ROOT/'data/model_extension/answer_spelling_20261111'
REGISTRY = ROOT/'config/answer_spelling_aliases_20261111.json'
PROTOCOL = ROOT/'docs/papers/ANSWER_SPELLING_SENSITIVITY_20261111.md'
MODEL = 'qwen3-4b'
PRIMARY = 'feature_jaccard__margin_other_factual_mean'
SEED = 20260830


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def accepts(fact, expected, observed, registry):
    expected, observed = str(expected or '').strip(), str(observed or '').strip()
    if observed == expected:
        return True
    alias = registry['aliases'].get(fact)
    if not alias or expected != alias['expected']:
        return False
    return unicodedata.normalize('NFC', observed) in {
        unicodedata.normalize('NFC', value) for value in alias['accepted']}


def accent_key(value):
    return ''.join(c for c in unicodedata.normalize('NFD', value.strip()) if not unicodedata.combining(c))


def inputs():
    return [REGISTRY, PROTOCOL, Path(__file__), ROOT/'scripts/whole_graph_analysis.py',
            ROOT/'scripts/analyze_model_extension.py', ROOT/'config/paper_control_manifest.csv',
            ROOT/'data/publication_analysis/converted_graph_audit.json',
            ROOT/'data/publication_analysis/whole_graph_results.json',
            ROOT/'data/model_extension/qwen17_completion_20261106/figure_audit/answer_audit.csv',
            ROOT/'data/model_extension/qwen17_completion_20261106/analysis/results.json',
            RECOVERY/'freeze.json', RECOVERY/'analysis/combined_jobs.json',
            RECOVERY/'analysis/graph_audit.json', RECOVERY/'analysis/model_extension_results.json',
            RECOVERY/'analysis/verification.json', RECOVERY/'analysis/display_audit.json']


def freeze():
    hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs()}
    originals = read(RECOVERY/'freeze.json')['original_raw']
    raw = {r['path']: r['sha256'] for r in originals}
    for path in (RECOVERY/'graphs').glob('*/raw_graph.json'):
        raw[path.relative_to(ROOT).as_posix()] = digest(path)
    assert len(raw) == 147
    converted = {r['path']: r['sha256'] for r in read(RECOVERY/'analysis/graph_audit.json')}
    for path, sha in {**raw, **converted}.items():
        assert digest(ROOT/path) == sha, path
    plan = dict(inputs=hashes, raw_graph_hashes=raw, converted_graph_hashes=converted,
                bootstrap_runs=10000, seed=SEED, size_seed=20261111, size_runs=200,
                status='post_hoc_sensitivity', no_hosted_requests=True)
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT/'plan.json').exists():
        assert read(OUT/'plan.json') == plan, 'Frozen plan changed; do not overwrite.'
    else:
        atomic_json(OUT/'plan.json', plan)
    return plan


def output_inventory(registry):
    result = []
    for model, source in [
        ('gemma-2-2b', read(ROOT/'data/publication_analysis/converted_graph_audit.json')),
        ('qwen3-4b', read(RECOVERY/'analysis/graph_audit.json'))]:
        for r in source:
            if r.get('model_dir', model) != model or r['role'] not in {'target', 'positive_paraphrase'} or r['status'] != 'ok':
                continue
            result.append(dict(model=model, fact=r['pair_id'], role=r['role'], domain=r['domain'], split=r['split'],
                               expected=r['expected_token'], observed=r['top_token']))
    q17 = read_csv(ROOT/'data/model_extension/qwen17_completion_20261106/figure_audit/answer_audit.csv')
    for r in q17:
        if r['cohort'] == 'expanded91':
            result.append(dict(model='qwen3-1.7b', fact=r['fact'], role=r['role'], domain=r['domain'], split=r['split'],
                               expected=r['expected'], observed=r['top_text']))
    assert Counter(r['model'] for r in result) == {'gemma-2-2b': 60, 'qwen3-1.7b': 50, 'qwen3-4b': 60}
    for r in result:
        r['strict_match'] = str(r['observed'] or '').strip() == r['expected'].strip()
        r['accepted_match'] = accepts(r['fact'], r['expected'], r['observed'], registry)
        r['accent_only_candidate'] = not r['strict_match'] and accent_key(str(r['observed'] or '')) == accent_key(r['expected'])
        r['newly_accepted'] = r['accepted_match'] and not r['strict_match']
    return result


def verify_old_margins(reps, old):
    included = old['analyzable_pair_ids']
    for row in old['per_fact']:
        fact = row['pair_id']
        target, positive = reps[(fact, 'target')], reps[(fact, 'positive_paraphrase')]
        others = [reps[(f, 'positive_paraphrase')] for f in included if f != fact
                  and reps[(f, 'target')]['domain'] == row['domain'] and reps[(f, 'target')]['split'] == row['split']]
        for name, metric in SIMILARITIES.items():
            actual = metric(target, positive) - np.mean([metric(target, other) for other in others])
            assert np.isclose(actual, row[name+'__margin_other_factual_mean'], rtol=0, atol=1e-12)


def equal_counts(reps, result):
    output, groups = [], []
    included = [r for r in result['per_fact'] if r['split'] == 'held_out']
    for domain in sorted({r['domain'] for r in included}):
        facts = sorted(r['pair_id'] for r in included if r['domain'] == domain)
        arrays = {(f, role): sorted(reps[(f, role)]['features']) for f in facts for role in ['target', 'positive_paraphrase']}
        minimum = min(map(len, arrays.values()))
        for fraction in [1.0, .5]:
            count = max(1, int(minimum*fraction))
            seed = 20261111 + sum(map(ord, f'{MODEL}:{domain}:{fraction}'))
            rng = np.random.default_rng(seed)
            groups.append(dict(domain=domain, fraction=fraction, sampled_k=count, min_features=minimum, facts=len(facts), seed=seed))
            for repetition in range(200):
                selected = {key: {arr[i] for i in rng.choice(len(arr), count, replace=False)} for key, arr in arrays.items()}
                for fact in facts:
                    own = jaccard(selected[(fact, 'target')], selected[(fact, 'positive_paraphrase')])
                    baseline = np.mean([jaccard(selected[(fact, 'target')], selected[(other, 'positive_paraphrase')]) for other in facts if other != fact])
                    output.append(dict(fact=fact, domain=domain, fraction=fraction, repetition=repetition, margin=float(own-baseline)))
    summary = []
    for r in included:
        for fraction in [1.0, .5]:
            values = [x['margin'] for x in output if x['fact'] == r['pair_id'] and x['fraction'] == fraction]
            summary.append(dict(fact=r['pair_id'], domain=r['domain'], fraction=fraction, repetitions=200,
                                mean=float(np.mean(values)), sd=float(np.std(values, ddof=1))))
    return dict(groups=groups, per_fact=summary), output


def main():
    plan = freeze()
    registry = read(REGISTRY)
    inventory = output_inventory(registry)
    changed = [r for r in inventory if r['newly_accepted']]
    assert len(changed) == 1 and changed[0]['model'] == MODEL
    assert (changed[0]['fact'], changed[0]['role']) == ('columbus_americas', 'positive_paraphrase')
    jobs = read(RECOVERY/'analysis/combined_jobs.json')
    reps, crossed, audits = load_representations(MODEL, jobs)
    assert len(reps) == 120 and len(crossed) == 27
    old = read(RECOVERY/'analysis/model_extension_results.json')['controlled']
    verify_old_margins(reps, old)
    # Only the inclusion flag changes; retain actual predictions and feature sets.
    adjusted = {key: dict(value) for key, value in reps.items()}
    for (fact, role), rep in adjusted.items():
        if role in {'target', 'positive_paraphrase'}:
            rep['top_token_matches_expected'] = accepts(fact, rep['expected_token'], rep['top_token'], registry)
    new = analyze_controlled(adjusted, bootstrap_runs=10000, seed=SEED)
    before = {r['pair_id']: r for r in old['per_fact']}
    after = {r['pair_id']: r for r in new['per_fact']}
    assert set(after) - set(before) == {'columbus_americas', 'wwi_start'}
    assert not set(before) - set(after)
    for fact, row in before.items():
        for key, value in row.items():
            if isinstance(value, (float, int)) and not isinstance(value, bool):
                assert np.isclose(value, after[fact][key], rtol=0, atol=1e-12), (fact, key)
    size, repetitions = equal_counts(adjusted, new)
    histories = [r for r in new['per_fact'] if r['domain'] == 'history' and r['split'] == 'held_out']
    history_comparisons = []
    for r in histories:
        for other in histories:
            if r['pair_id'] == other['pair_id']:
                continue
            for same, comparator in [(True, r['pair_id']), (False, other['pair_id'])]:
                history_comparisons.append(dict(fact=r['pair_id'], comparison='same_fact' if same else 'other_fact',
                    comparator=comparator, jaccard=jaccard(adjusted[(r['pair_id'], 'target')]['features'], adjusted[(comparator, 'positive_paraphrase')]['features'])))
    summary = dict(status='completed', post_hoc=True, no_hosted_requests=True,
                   original_margins_verified=True, original_included_facts_unchanged=True,
                   policy=registry, changed_outputs=changed,
                   unregistered_accent_candidates=[r for r in inventory if r['accent_only_candidate'] and not r['accepted_match']],
                   model_coverage=[dict(model=m, factual_graphs=sum(r['model'] == m for r in inventory),
                                        newly_accepted_outputs=sum(r['model'] == m for r in changed))
                                   for m in ['gemma-2-2b', 'qwen3-1.7b', 'qwen3-4b']],
                   exact_match=old, accepted_spelling=new, equal_count=size,
                   history_comparisons=history_comparisons,
                   history_independent_replication=False,
                   interpretation='Two history facts reuse each other as comparators. Descriptive sensitivity, not a confirmatory history test. Previously recorded confirmatory gates are not changed.',
                   plan_sha256=digest(OUT/'plan.json'))
    for path, sha in plan['inputs'].items():
        assert digest(ROOT/path) == sha
    atomic_json(OUT/'results.json', json_ready(summary))
    write_csv(OUT/'answer_inventory.csv', inventory)
    write_csv(OUT/'accepted_spelling_per_fact.csv', new['per_fact'])
    write_csv(OUT/'history_comparisons.csv', history_comparisons)
    write_csv(OUT/'equal_count_per_fact.csv', size['per_fact'])
    write_csv(OUT/'equal_count_repetitions.csv', repetitions)
    atomic_json(OUT/'execution_record.json', dict(finished_at=now(), plan_sha256=digest(OUT/'plan.json'),
                script_sha256=digest(Path(__file__)), no_hosted_requests=True, original_inputs_unchanged=True))
    print(json.dumps(json_ready(dict(exact=old['heldout_primary'], accepted=new['heldout_primary'],
                                    history=new['heldout_domains'].get('history'),
                                    history_rows=histories, equal_count=size)), indent=2))


if __name__ == '__main__':
    main()
