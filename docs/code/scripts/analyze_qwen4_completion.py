"""Reconcile the two one-shot recoveries with the unchanged controlled analysis."""
from copy import deepcopy
import json
import math
from pathlib import Path

import numpy as np

from analyze_model_extension import load_jobs, load_representations, write_csv
from complete_qwen4_controls import ROOT, ORIGINAL, OUT, MODEL, EXPECTED, digest
from control_io import atomic_json
from run_matched_choice_controls import now
from whole_graph_analysis import analyze_controlled, json_ready

PRIMARY = 'feature_jaccard__margin_other_factual_mean'


def summary_matches(actual, expected):
    for key in ['n', 'mean', 'ci95', 'positive_n', 'exact_one_sided_sign_flip_p']:
        assert np.allclose(actual[key], expected[key], rtol=0, atol=1e-12), key


def main():
    status = json.loads((OUT / 'status.json').read_text())
    assert status['state'] == 'two_attempts_finished'
    assert status['generation_requests'] == 2 and status['original_archive_unchanged']
    frozen = json.loads((OUT / 'freeze.json').read_text())
    for path, sha in frozen['dependencies'].items():
        assert digest(ROOT / path) == sha, path
    for row in frozen['original_raw']:
        assert digest(ROOT / row['path']) == row['sha256'], row['path']
    original_jobs = load_jobs(ORIGINAL)
    saved = json.loads((ORIGINAL / 'analysis/model_extension_results.json').read_text())
    settings = json.loads((ROOT / 'data/model_extension/model_extension_results.json').read_text())
    assert settings['seed'] == 20260830 and settings['bootstrap_runs'] == 10000
    original_reps, _, original_audits = load_representations(MODEL, original_jobs)
    original = analyze_controlled(original_reps, bootstrap_runs=10000, seed=20260830)
    summary_matches(original['heldout_primary'], saved['controlled']['heldout_primary'])
    before = {r['pair_id']: r for r in original['per_fact']}
    archived = {r['pair_id']: r for r in saved['controlled']['per_fact']}
    assert set(before) == set(archived)
    for key in before:
        for field, value in before[key].items():
            if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
                assert np.isclose(value, archived[key][field], rtol=0, atol=1e-12), (key, field)
    combined_jobs = deepcopy(original_jobs)
    recovered_audits = []
    for job in combined_jobs:
        if job['job_id'] not in EXPECTED:
            continue
        folder = OUT / 'graphs' / job['job_id']
        audit = json.loads((folder / 'audit.json').read_text())
        assert audit['technical_passed']
        assert digest(folder / 'raw_graph.json') == audit['raw_sha256']
        assert digest(folder / 'converted_graph.json') == audit['converted_sha256']
        job['raw_graph_path'] = (folder / 'raw_graph.json').relative_to(ROOT).as_posix()
        recovered_audits.append(dict(job=job, audit=audit))
    combined_reps, crossed, audits = load_representations(MODEL, combined_jobs)
    assert len(combined_reps) == 120 and len(crossed) == 27
    combined = analyze_controlled(combined_reps, bootstrap_runs=10000, seed=20260830)
    # One completed extension model: this correction does not change either p-value.
    combined['extension_holm_primary_p'] = combined['heldout_primary']['exact_one_sided_sign_flip_p']
    combined['extension_holm_specificity_p'] = combined['robustness']['exact_fact_label_permutation']['exact_one_sided_p']
    after = {r['pair_id']: r for r in combined['per_fact']}
    unchanged = set(before) == set(after) and all(
        np.isclose(before[key][PRIMARY], after[key][PRIMARY], rtol=0, atol=1e-12) for key in before)
    if unchanged:
        summary_matches(combined['heldout_primary'], original['heldout_primary'])
    heldout = [r for r in combined['per_fact'] if r['split'] == 'held_out']
    verification = dict(checked_at=now(), original_reconstruction_passed=True,
                        original_raw_hashes_verified=145, recovered_raw_hashes_verified=2,
                        recovered_converted_hashes_verified=2, original_archive_unchanged=True,
                        frozen_analysis_settings_unchanged=True, primary_margins_unchanged=bool(unchanged),
                        complete_controlled_graphs=len(combined_reps), complete_crossed_graphs=len(crossed),
                        heldout_facts=len(heldout), heldout_history_facts=sum(r['domain'] == 'history' for r in heldout),
                        original_primary=original['heldout_primary'], current_primary=combined['heldout_primary'])
    result = deepcopy(saved)
    result.update(controlled=combined,
                  audit_counts=dict(registered=147, ok=sum(r['status'] == 'ok' for r in audits), missing=0, error=0),
                  recovery=dict(scope='Late observational completion; original estimates retained separately',
                                controlled_collected=120, crossed_collected=27, complete=True))
    analysis = OUT / 'analysis'
    analysis.mkdir(parents=True, exist_ok=True)
    atomic_json(analysis / 'model_extension_results.json', json_ready(result))
    atomic_json(analysis / 'original_reconstructed_controlled.json', json_ready(original))
    atomic_json(analysis / 'graph_audit.json', json_ready(audits))
    atomic_json(analysis / 'verification.json', json_ready(verification))
    atomic_json(analysis / 'combined_jobs.json', combined_jobs)
    write_csv(analysis / 'graph_audit.csv', audits)
    write_csv(analysis / 'controlled_per_fact.csv', combined['per_fact'])
    write_csv(analysis / 'original_reconstructed_per_fact.csv', original['per_fact'])
    conversions = json.loads((ORIGINAL / 'analysis/conversion_audit.json').read_text())
    by_id = {item['job']['job_id']: item for item in recovered_audits}
    # Preserve the existing conversion records and replace only the two missing rows.
    for row in conversions:
        if row['job_id'] not in by_id:
            continue
        item = by_id[row['job_id']]
        audit, job = item['audit'], item['job']
        row.update(audit['raw'], **audit['converted'], status='ok',
                   raw_path=job['raw_graph_path'], converted_path=job['raw_graph_path'].replace('raw_graph.json', 'converted_graph.json'),
                   raw_sha256=audit['raw_sha256'], converted_sha256=audit['converted_sha256'],
                   ambiguous_policy='drop', sensitivity_only=bool(audit['raw']['raw_ambiguous_node_id_count']))
    assert sum(r['status'] == 'ok' for r in conversions) == 147
    atomic_json(analysis / 'conversion_audit.json', conversions)
    write_csv(analysis / 'conversion_audit.csv', conversions)
    spelling = next(item['audit'] for item in recovered_audits if item['job']['role'] == 'positive_paraphrase')
    report = [
        '# Qwen3-4B two-request recovery results', '',
        'Both unchanged prompts returned graphs on their single authorized attempts. All 147 planned graphs are now available: 120 controlled and 27 crossed. Both recovered graphs passed the recorded technical checks. The original 145 raw hashes and frozen source/result hashes are unchanged.', '',
        f"The Columbus rewording predicts `{str(spelling['observed']).strip()}`, whereas the frozen expected text is `{spelling['expected']}`. This is an accented spelling variant, not evidence of a wrong historical answer. It fails the unchanged exact-text rule; no accent normalization or new accepted answer was introduced.", '',
        f"The controlled analysis retains {len(heldout)} evaluation facts, including {verification['heldout_history_facts']} history facts. The World War I fact still lacks another eligible history comparator. Original reconstruction passed, and primary margins are {'unchanged' if unchanged else 'changed; inspect per-fact tables'}.", '',
        f"Current mean same-fact-minus-other-fact Jaccard overlap: {combined['heldout_primary']['mean']:.12f}. No new generation, altered prompts, or changed inclusion rules were used in this saved-data analysis.", '',
        'The collection gap is closed. The remaining history comparison gap concerns exact-answer eligibility, not missing Qwen3-4B graph files.', '',
    ]
    (analysis / 'RESULTS.md').write_text('\n'.join(report), encoding='utf-8')
    print(json.dumps(json_ready(verification), indent=2), flush=True)


if __name__ == '__main__':
    main()
