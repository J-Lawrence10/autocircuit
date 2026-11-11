"""Late observational Qwen1.7B completion analysis, separate from archived results.

No network calls, model inference, original-file writes, or canonical-paper edits.
The analysis plan is saved and checked before any new graph outcomes are read.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import whole_graph_analysis as whole
import exploratory_confound_checks as exploratory
from audit_qwen17_completion import DEPENDENCIES, REL_OUT, digest, inside, read_json
from complete_qwen17_controls import MANIFEST_SHA, MODEL, SOURCE, SETTINGS
from control_io import atomic_json
from control_manifest import load_control_manifest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/REL_OUT/'analysis'
SEED = 20260714
BOOTSTRAPS = 10000
SIZE_RUNS = 200
SIZE_SEED = 20260905
PRIMARY = 'feature_jaccard__margin_other_factual_mean'
MAX_LABEL_PERMUTATIONS = 120**3
SET_KEYS = ('features', 'features_with_errors')
MAP_KEYS = ('feature_weights', 'feature_weights_with_errors', 'layer_profile', 'edge_flow')
DEPENDENCE_NOTE = (
    'Late expanded observational analysis, not a new confirmatory sample or independent replication. '
    'Original and expanded cohorts overlap; facts within a domain share other-fact comparators. '
    'Fact bootstrap intervals and sign-flip p-values therefore have limited independence justification. '
    'The exact within-domain label permutation is conditional on exchangeability of factual pairing, '
    'not a randomized causal test or a control for wording and answer-token confounds. '
    'Secondary comparisons are exploratory; repeated feature subsamples are not new independent facts.'
)


def save(path, payload):
    atomic_json(path, whole.json_ready(payload))


def plan_spec(root=ROOT):
    names = sorted(DEPENDENCIES | {
        'scripts/analyze_qwen17_completion.py', 'scripts/audit_qwen17_completion.py',
        'scripts/whole_graph_analysis.py', 'scripts/exploratory_confound_checks.py',
        'scripts/2_convert_graph.py',
    })
    return dict(schema_version='qwen17-late-analysis-plan-v1', model=MODEL,
        study_status='Late expanded observational analysis with separate original-cohort reconstruction',
        collection_root=str(REL_OUT), expected_original_raw_count=50, expected_new_raw_count=41,
        expected_length_rejections=29, frozen_manifest_sha256=MANIFEST_SHA,
        main_seed=SEED, bootstrap_runs=BOOTSTRAPS, primary_metric='feature_jaccard',
        primary_contrast='same-fact rewording minus mean other-fact rewording overlap within domain and split',
        eligibility='All four roles, exact stripped expected top token on both factual forms, and at least one other included fact in the same domain/split. No replacement questions.',
        raw_representation='Family/layer/feature identity; collapse token positions; exclude ambiguous IDs, errors, embeddings and logits as implemented by whole_graph_analysis. Error-inclusive sensitivity retained separately.',
        raw_logit_extraction='Match the existing converter: sort raw logit nodes by token_prob; direct token or Output/Logit clerp extraction; take first decodable token among top ten.',
        planned_outputs=['original50 reconstruction', 'expanded91 analysis', 'all30-fact eligibility audit',
            'domain/split summaries', 'closest-other-fact margin', 'influence-weighted cosine',
            'error-inclusive metrics', 'both invented-name controls', 'output-type-matched control subsets',
            'leave-one-fact-out fixed-comparator means', 'within-domain exact fact-label permutation',
            'fact bootstrap and one-sided sign-flip summaries', 'equal-count feature sensitivities'],
        exact_label_permutation_bound=MAX_LABEL_PERMUTATIONS,
        numerical_optimization='Memoize identical set-pair Jaccard calls; retain original exact enumeration/statistics.',
        size_sensitivity=dict(helper='exploratory_confound_checks.size_checks', runs=SIZE_RUNS,
                             seed=SIZE_SEED, fractions=[1.0, .5], interpretation='Algorithmic feature subsampling, not independent replication or additional sample size'),
        old_reconstruction_tolerance=1e-12,
        centered_regression_policy='Retain legacy computation only as explicitly non-independent diagnostic; centered intercept is the mean, not independent confound adjustment.',
        interpretation=DEPENDENCE_NOTE,
        method_sha256={name: digest(inside(root, name)) for name in names})


def ensure_plan(root=ROOT):
    destination = inside(root, REL_OUT/'analysis')
    destination.mkdir(parents=True, exist_ok=True)
    path = destination/'analysis_plan.json'
    spec = plan_spec(root)
    if path.exists():
        recorded = read_json(path)
        if recorded['specification'] != spec:
            raise RuntimeError('Analysis plan/code changed; explicit versioned amendment required')
    else:
        save(path, dict(recorded_before_graph_outcomes_at=datetime.now(timezone.utc).isoformat(),
                        specification=spec))
    return digest(path)


def pack_representation(rep):
    result = {k: v for k, v in rep.items() if k not in SET_KEYS+MAP_KEYS}
    for key in SET_KEYS:
        result[key] = [list(item) for item in sorted(rep[key])]
    for key in MAP_KEYS:
        result[key] = [[list(k) if isinstance(k, tuple) else k, v] for k, v in sorted(rep[key].items())]
    return result


def unpack_representation(record):
    rep = dict(record)
    for key in SET_KEYS:
        rep[key] = {tuple(item) for item in rep[key]}
    for key in MAP_KEYS:
        rep[key] = {tuple(k) if isinstance(k, list) else k: v for k, v in rep[key]}
    return rep


def with_raw_predictions(graph):
    """In-memory metadata enrichment matching 2_convert_graph.py; raw remains untouched."""
    logits = [node for node in graph['nodes'] if node.get('feature_type') == 'logit']
    logits.sort(key=lambda node: node.get('token_prob', 0), reverse=True)
    predictions = []
    for node in logits[:10]:
        token = node.get('token')
        if token is None:
            match = re.search(r'(?:Output|Logit)\s+"([\s\S]*?)"\s+\(p=', node.get('clerp', ''))
            token = match.group(1) if match else None
        if token is not None:
            predictions.append(dict(node_id=node.get('node_id'), token=token,
                probability=node.get('token_prob', 0), is_target=node.get('is_target_logit', False)))
    metadata = dict(graph.get('metadata', {}), top_predictions=predictions,
                    model_output=predictions[0]['token'] if predictions else None)
    return dict(graph, metadata=metadata)


def local_archived_path(root, value):
    normalized = str(value).replace('\\', '/')
    if '/data/' in normalized:
        normalized = 'data/'+normalized.split('/data/', 1)[1]
    return inside(root, normalized)


def compare_representations(raw_rep, converted_rep, tolerance=1e-12):
    for key in SET_KEYS:
        if raw_rep[key] != converted_rep[key]:
            raise RuntimeError(f'Raw/converted feature identity mismatch: {key}')
    for key in MAP_KEYS:
        if raw_rep[key].keys() != converted_rep[key].keys() or any(
            not math.isclose(float(value), float(converted_rep[key][item]), rel_tol=0, abs_tol=tolerance)
            for item, value in raw_rep[key].items()):
            raise RuntimeError(f'Raw/converted numeric representation mismatch: {key}')
    for key in ('top_token', 'top_token_class', 'eligible_feature_node_count', 'eligible_edge_count'):
        if raw_rep[key] != converted_rep[key]:
            raise RuntimeError(f'Raw/converted metadata mismatch: {key}')


def preflight(root):
    base = inside(root, REL_OUT)
    frozen = read_json(base/'freeze.json')
    technical = read_json(base/'audit/collection_verification.json')
    status = read_json(base/'status.json')
    if technical.get('technical_verification_passed') is not True:
        raise RuntimeError('Successful technical collection audit required')
    if technical.get('original_graphs_verified_unchanged') != 50:
        raise RuntimeError('Original50 preservation not verified')
    if status.get('state') != 'attempt_finished' or status.get('counts') != {'saved': 41, 'prompt_too_long': 29}:
        raise RuntimeError('Unexpected or unfinished bounded collection inventory')
    if technical.get('collection_counts') != status['counts']:
        raise RuntimeError('Technical audit and collection status disagree')
    if digest(root/'config/paper_control_manifest.csv') != MANIFEST_SHA or frozen.get('manifest_sha256') != MANIFEST_SHA:
        raise RuntimeError('Fixed original manifest changed')
    if frozen.get('model') != MODEL or frozen.get('source') != SOURCE or frozen.get('settings') != SETTINGS:
        raise RuntimeError('Frozen collection model/source/settings changed')
    for name, expected in frozen['dependencies'].items():
        if digest(inside(root, name)) != expected:
            raise RuntimeError(f'Frozen collection dependency changed: {name}')
    jobs = load_control_manifest(root/'config/paper_control_manifest.csv')
    archived = read_json(root/'data/publication_analysis/whole_graph_results.json')
    converted = read_json(root/'data/publication_analysis/converted_graph_audit.json')
    converted_index = {(r['pair_id'], r['role']): r for r in converted
                       if r.get('model_dir') == 'qwen3-1-7b' and r.get('status') == 'ok'}
    tech_jobs = {r['job_id']: r for r in technical['jobs']}
    inventory = []
    for item in frozen['existing']:
        inventory.append(dict(job=item['job'], collection='original', path=item['path'],
                              sha256=item['sha256'], bytes=item['bytes']))
    for job in frozen['missing']:
        audited = tech_jobs[job['job_id']]
        if audited['collection_status'] == 'saved':
            if not audited['technical_checks_pass']:
                raise RuntimeError('New saved graph failed technical audit')
            inventory.append(dict(job=job, collection='late_completion',
                path=str(REL_OUT/'graphs'/job['job_id']/'raw_graph.json'),
                sha256=audited['raw_sha256'], bytes=audited['raw_bytes']))
    if Counter(item['collection'] for item in inventory) != {'original': 50, 'late_completion': 41}:
        raise RuntimeError('Unexpected analyzable raw-file inventory')
    return jobs, inventory, archived, converted_index, tech_jobs


def load_representations(root, inventory, converted_index, plan_sha):
    out = inside(root, REL_OUT/'analysis')
    cache_dir = out/'representation_cache'
    cache_dir.mkdir(exist_ok=True)
    index_path = out/'representation_cache_index.json'
    cache_index = read_json(index_path) if index_path.exists() else {}
    original, expanded, audits, provenance = {}, {}, [], []
    for i, item in enumerate(inventory, 1):
        path = inside(root, item['path'])
        raw_sha = digest(path)
        if raw_sha != item['sha256'] or path.stat().st_size != item['bytes']:
            raise RuntimeError(f'Raw input changed: {item["job"]["job_id"]}')
        job = item['job']
        cache_path = cache_dir/(raw_sha+'.json')
        prior = cache_index.get(raw_sha)
        if prior and cache_path.exists() and digest(cache_path) == prior['cache_sha256']:
            cached = read_json(cache_path)
            if cached['analysis_plan_sha256'] != plan_sha or cached['job'] != job:
                raise RuntimeError('Representation cache provenance differs')
            graph_audit, rep = cached['graph_audit'], unpack_representation(cached['representation'])
            parity = cached['raw_converted_parity']
        else:
            graph = with_raw_predictions(read_json(path))
            graph_audit, rep = whole.summarize_graph(graph, path=path, file_sha256=raw_sha, raw_schema=True)
            if whole.normalize_prompt(graph_audit['prompt']) != whole.normalize_prompt(job['prompt']):
                raise RuntimeError('Raw prompt differs from manifest')
            if graph_audit['model'] != MODEL:
                raise RuntimeError('Raw model differs from Qwen3-1.7B')
            if any(graph_audit[key] for key in ('missing_node_ids', 'ambiguous_node_id_count',
                    'dangling_edge_count', 'nonfinite_edge_count', 'duplicate_exact_edge_count')):
                raise RuntimeError(f'Unexpected raw integrity failure: {job["job_id"]}')
            parity = dict(status='new_raw_direct', note='Same raw-schema representation implementation; original50 converter parity is checked separately.')
            if item['collection'] == 'original':
                old = converted_index[(job['pair_id'], job['role'])]
                converted_path = local_archived_path(root, old['path'])
                converted_graph, converted_sha = whole.read_json_with_hash(converted_path)
                if converted_sha != old['sha256']:
                    raise RuntimeError(f'Archived converted input changed: {job["job_id"]}')
                _, converted_rep = whole.summarize_graph(converted_graph, path=converted_path,
                    file_sha256=converted_sha, raw_schema=False)
                compare_representations(rep, converted_rep)
                parity = dict(status='passed', converted_path=str(converted_path.relative_to(root)),
                              converted_sha256=converted_sha, tolerance=1e-12)
                del converted_graph, converted_rep
            top_matches = (bool(job['expected_token'].strip()) and
                           str(rep['top_token'] or '').strip() == job['expected_token'].strip()) if job['role'] in {'target', 'positive_paraphrase'} else None
            base = dict(job, collection=item['collection'], raw_path=str(path.relative_to(root)),
                        raw_sha256=raw_sha, top_token_matches_expected=top_matches)
            rep.update(base)
            graph_audit.update(base, status='ok', source_metadata=graph['metadata'].get('feature_details', {}),
                exporter=graph['metadata'].get('info', {}).get('generator', {}),
                generation_settings=graph['metadata'].get('generation_settings', {}),
                raw_converted_parity=parity)
            save(cache_path, dict(schema_version='qwen17-representation-cache-v1',
                analysis_plan_sha256=plan_sha, raw_sha256=raw_sha, job=job, graph_audit=graph_audit,
                representation=pack_representation(rep), raw_converted_parity=parity))
            cache_index[raw_sha] = dict(job_id=job['job_id'], collection=item['collection'],
                path=str(cache_path.relative_to(root)), cache_sha256=digest(cache_path))
            save(index_path, cache_index)
            del graph
        if item['collection'] == 'original':
            # Revalidate archived converted bytes even when a representation cache is used.
            if digest(inside(root, parity['converted_path'])) != parity['converted_sha256']:
                raise RuntimeError('Archived converted bytes changed since cache creation')
            original[(job['pair_id'], job['role'])] = rep
        expanded[(job['pair_id'], job['role'])] = rep
        audits.append(graph_audit)
        provenance.append(dict(item, raw_sha256=raw_sha, cache_sha256=digest(cache_path), raw_converted_parity=parity))
        print(f'[{i}/{len(inventory)}] verified {item["collection"]} {job["job_id"]}', flush=True)
    return original, expanded, audits, provenance


def bounded_controlled_analysis(representations):
    eligible, _ = whole.complete_pair_ids(representations)
    sizes = Counter(representations[(pair_id, 'target')]['domain'] for pair_id in eligible
                    if representations[(pair_id, 'target')]['split'] == 'held_out')
    permutations = math.prod(math.factorial(n) for n in sizes.values() if n > 1)
    if permutations > MAX_LABEL_PERMUTATIONS:
        raise RuntimeError('Exact label permutation exceeds fixed design bound; no unplanned approximation')
    baseline_jaccard = whole.jaccard
    cache = {}
    def memoized(a, b):
        key = (id(a), id(b))
        if key not in cache:
            cache[key] = baseline_jaccard(a, b)
        return cache[key]
    with patch.object(whole, 'jaccard', memoized):
        result = whole.analyze_controlled(representations, bootstrap_runs=BOOTSTRAPS, seed=SEED)
    result['legacy_gate_diagnostics_not_new_confirmatory_claims'] = {
        name: result.pop(name) for name in (
            'pooled_confirmatory_test_pass', 'gate_b_confirmatory_fact_identity_pass',
            'gate_b_required_domains', 'gate_c_robustness_pass')}
    regression = result['robustness'].pop('graph_size_adjusted_regression')
    result['legacy_centered_regression_not_independent_evidence'] = dict(
        explanation='Centering makes the fitted intercept the observed mean; this is not independent evidence after graph-size control.', result=regression)
    result['interpretation'] = DEPENDENCE_NOTE
    return result


def reconstruct_original(result, archived):
    expected = {row['pair_id']: row for row in archived['models']['qwen']['per_fact']}
    observed = {row['pair_id']: row for row in result['per_fact']}
    if expected.keys() != observed.keys():
        raise RuntimeError('Original analyzable fact inventory differs from archive')
    discrepancies = []
    for pair_id, row in expected.items():
        for key, value in row.items():
            if key.startswith(('feature_jaccard__', 'feature_influence_cosine__')):
                if not math.isclose(float(value), float(observed[pair_id][key]), rel_tol=0, abs_tol=1e-12):
                    discrepancies.append(f'{pair_id}/{key}')
    old = archived['models']['qwen']['heldout_primary']
    new = result['heldout_primary']
    if old['n'] != new['n'] or new['n'] != 5 or not math.isclose(old['mean'], new['mean'], abs_tol=1e-12, rel_tol=0):
        raise RuntimeError('Original held-out n/mean differs from archived Qwen result')
    if not math.isclose(new['mean'], .0854227, abs_tol=5e-8, rel_tol=0):
        raise RuntimeError('Original Qwen mean differs from expected .0854227')
    if discrepancies:
        raise RuntimeError('Original reconstructed values differ: '+', '.join(discrepancies))
    return dict(passed=True, tolerance=1e-12, per_fact_rows=len(expected),
                heldout_n=new['n'], heldout_mean=new['mean'],
                note='All original per-fact Jaccard and influence-cosine contrasts reproduced; original50 raw/converted representations also verified.')


def eligibility_table(jobs, representations, result, cohort, technical_jobs):
    by_pair = defaultdict(list)
    for job in jobs:
        by_pair[job['pair_id']].append(job)
    complete = set(result['complete_pair_ids'])
    analyzable = set(result['analyzable_pair_ids'])
    rows = []
    for pair_id, group in sorted(by_pair.items()):
        present = {r for p, r in representations if p == pair_id}
        missing = sorted(whole.REQUIRED_ROLES-present)
        incorrect = [role for role in ('target', 'positive_paraphrase')
                     if (pair_id, role) in representations and not representations[(pair_id, role)]['top_token_matches_expected']]
        reason = ('incomplete_roles' if missing else 'expected_token_not_top_prediction' if incorrect else
                  'no_same_domain_split_comparator' if pair_id not in analyzable else 'included')
        rows.append(dict(cohort=cohort, pair_id=pair_id, domain=group[0]['domain'], split=group[0]['split'],
            present_roles=sorted(present), missing_roles=missing, incorrect_factual_roles=incorrect,
            factual_outputs={role: representations.get((pair_id, role), {}).get('top_token') for role in ('target', 'positive_paraphrase')},
            collection_rejections={r['role']: technical_jobs.get(f'{pair_id}__{r["role"]}', {}).get('collection_status')
                                  for r in group if r['role'] in missing and f'{pair_id}__{r["role"]}' in technical_jobs},
            four_role_expected_token_gate_pass=pair_id in complete,
            included_in_comparisons=pair_id in analyzable, exclusion_reason=reason))
    return rows


def domain_split_summaries(result, cohort):
    summaries = []
    for domain in ('chemistry', 'geography', 'history'):
        for split in ('development', 'held_out'):
            rows = [r for r in result['per_fact'] if r['domain'] == domain and r['split'] == split]
            for metric in ('feature_jaccard', 'feature_influence_cosine'):
                key = metric+'__margin_other_factual_mean'
                summary = whole.summarize_values([r[key] for r in rows], bootstrap_runs=BOOTSTRAPS,
                    seed=SEED+sum(map(ord, domain+':'+split+':'+key)), run_exact_test=bool(rows))
                summaries.append(dict(cohort=cohort, domain=domain, split=split, metric=metric, **summary))
    return summaries


def equal_count_checks(representations, result):
    graphs = [dict(model=MODEL, status='ok', design='controlled', fact=p, role=r, features=rep['features'])
              for (p, r), rep in representations.items()]
    heldout = [r for r in result['per_fact'] if r['split'] == 'held_out']
    if not heldout:
        return dict(status='no_eligible_heldout_facts', rows=[], repetitions=[], strata=[], summaries=[])
    with patch.object(exploratory, 'MODELS', [MODEL]), patch.object(exploratory, 'SEED', SIZE_SEED):
        rows, repetitions, strata, summaries = exploratory.size_checks(graphs, {MODEL: heldout}, SIZE_RUNS)
    return dict(status='computed', seed=SIZE_SEED, runs=SIZE_RUNS,
        interpretation='200 feature subsamples are algorithmic sensitivity draws, not 200 independent data points. Fact-level descriptive intervals do not remove shared-comparator dependence.',
        rows=rows, repetitions=repetitions, strata=strata, summaries=summaries)


def run(root=ROOT):
    root = Path(root).resolve()
    plan_sha = ensure_plan(root)  # Must precede graph outcome reads.
    out = inside(root, REL_OUT/'analysis')
    jobs, inventory, archived, converted_index, technical_jobs = preflight(root)
    original, expanded, audits, provenance = load_representations(root, inventory, converted_index, plan_sha)
    original_result = bounded_controlled_analysis(original)
    reconstruction = reconstruct_original(original_result, archived)
    print('Original50 primary margins and raw/converted parity reproduced.', flush=True)
    expanded_result = bounded_controlled_analysis(expanded)
    cohorts = {'original50_reconstructed': original_result, 'expanded91_late_observational': expanded_result}
    eligibility, domains, size_results = [], [], {}
    for name, result in cohorts.items():
        reps = original if name.startswith('original') else expanded
        eligibility.extend(eligibility_table(jobs, reps, result, name, technical_jobs))
        domains.extend(domain_split_summaries(result, name))
        size_results[name] = equal_count_checks(reps, result)
        whole.write_csv(out/(name+'_per_fact.csv'), result['per_fact'])
        whole.write_csv(out/(name+'_equal_count_per_fact.csv'), size_results[name]['rows'])
        whole.write_csv(out/(name+'_equal_count_repetitions.csv'), size_results[name]['repetitions'])
    inputs = [root/REL_OUT/'freeze.json', root/REL_OUT/'status.json',
              root/REL_OUT/'audit/collection_verification.json', root/'config/paper_control_manifest.csv',
              root/'data/publication_analysis/whole_graph_results.json', root/'data/publication_analysis/converted_graph_audit.json']
    collection_by_domain = []
    for domain in ('chemistry', 'geography', 'history'):
        old_n = sum(i['collection'] == 'original' and i['job']['domain'] == domain for i in inventory)
        new_n = sum(i['collection'] == 'late_completion' and i['job']['domain'] == domain for i in inventory)
        collection_by_domain.append(dict(domain=domain, planned_graphs=sum(j['domain'] == domain for j in jobs),
            original_graphs=old_n, new_graphs=new_n, available_graphs=old_n+new_n,
            length_rejected_jobs=sum(r['domain'] == domain and r['collection_status'] == 'prompt_too_long' for r in technical_jobs.values()),
            complete_four_role_sets=sum(r['cohort'] == 'expanded91_late_observational' and r['domain'] == domain and not r['missing_roles'] for r in eligibility)))
    result = dict(schema_version='qwen17-late-completion-analysis-v1', created_at=datetime.now(timezone.utc).isoformat(),
        status='completed', interpretation=DEPENDENCE_NOTE, analysis_plan_sha256=plan_sha,
        model=MODEL, input_counts=dict(original_raw=50, new_raw=41, combined_raw=91, length_rejections=29),
        collection_by_domain=collection_by_domain,
        original_reconstruction=reconstruction, cohorts=cohorts, eligibility=eligibility,
        domain_split_summaries=domains, equal_count_sensitivity=size_results,
        graph_audits=audits, provenance=provenance,
        input_sha256={str(p.relative_to(root)): digest(p) for p in inputs},
        environment=dict(python=sys.version, numpy=np.__version__))
    save(out/'results.json', result)
    save(out/'graph_audit.json', audits)
    save(out/'eligibility_audit.json', eligibility)
    whole.write_csv(out/'graph_audit.csv', audits)
    whole.write_csv(out/'eligibility_audit.csv', eligibility)
    whole.write_csv(out/'domain_split_summaries.csv', domains)
    save(out/'output_checksums.json', {str(p.relative_to(out)): digest(p) for p in sorted(out.glob('*'))
                                     if p.is_file() and p.name != 'output_checksums.json'})
    print(json.dumps(whole.json_ready(dict(original=original_result['heldout_primary'],
        expanded=expanded_result['heldout_primary'], expanded_domains=expanded_result['heldout_domains'],
        permutation=expanded_result['robustness']['exact_fact_label_permutation'])), indent=2), flush=True)
    return result


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    run()


if __name__ == '__main__':
    main()
