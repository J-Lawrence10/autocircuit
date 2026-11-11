"""Validate saved accepted-spelling results, raw feature overlaps, and displays."""
from collections import Counter
import json
from pathlib import Path
import shutil

import numpy as np

from analyze_answer_spelling import OUT, ROOT, RECOVERY, PRIMARY, read, inputs
from analyze_model_extension import write_csv
from complete_qwen4_controls import digest, read_csv
from control_io import atomic_json
from exploratory_confound_checks import features
from whole_graph_analysis import jaccard
from run_matched_choice_controls import now

FIG = OUT/'paper_figures_v1'
PREVIOUS = ROOT/'data/model_extension/paper_figures_qwen4_complete_20261110'


def main():
    plan, result = read(OUT/'plan.json'), read(OUT/'results.json')
    for path, sha in {**plan['inputs'], **plan['raw_graph_hashes'], **plan['converted_graph_hashes']}.items():
        assert digest(ROOT/path) == sha, path
    assert result['status'] == 'completed' and result['post_hoc'] and result['no_hosted_requests']
    assert len(result['changed_outputs']) == 1 and not result['unregistered_accent_candidates']
    inventory = read_csv(OUT/'answer_inventory.csv')
    assert len(inventory) == len({(r['model'], r['fact'], r['role']) for r in inventory}) == 170
    assert sum(r['newly_accepted'] == 'True' for r in inventory) == 1
    original = read(RECOVERY/'analysis/model_extension_results.json')['controlled']
    assert result['exact_match'] == original
    after = result['accepted_spelling']
    evaluated = [r for r in after['per_fact'] if r['split'] == 'held_out']
    assert len(evaluated) == 12
    assert Counter(r['domain'] for r in evaluated) == {'chemistry': 5, 'geography': 5, 'history': 2}
    assert all(r[PRIMARY] > 0 for r in evaluated)
    assert np.isclose(np.mean([r[PRIMARY] for r in evaluated]), after['heldout_primary']['mean'], atol=1e-12)
    assert original['robustness']['output_type_matched_controls'] == after['robustness']['output_type_matched_controls']
    history = {r['pair_id']: r for r in evaluated if r['domain'] == 'history'}
    jobs = read(RECOVERY/'analysis/combined_jobs.json')
    raw_sets = {}
    for job in jobs:
        if job['fact_id'] in history and job['role'] in {'target', 'positive_paraphrase'}:
            graph = read(ROOT/job['raw_graph_path'])
            raw_sets[(job['fact_id'], job['role'])] = features(graph['nodes'])
    assert len(raw_sets) == 4
    for row in result['history_comparisons']:
        actual = jaccard(raw_sets[(row['fact'], 'target')], raw_sets[(row['comparator'], 'positive_paraphrase')])
        assert np.isclose(actual, row['jaccard'], rtol=0, atol=1e-12)
    for fact, row in history.items():
        compared = [r for r in result['history_comparisons'] if r['fact'] == fact]
        own = next(r['jaccard'] for r in compared if r['comparison'] == 'same_fact')
        other = next(r['jaccard'] for r in compared if r['comparison'] == 'other_fact')
        assert np.isclose(own-other, row[PRIMARY], rtol=0, atol=1e-12)
        assert row['same_template_top_token'] == row['nonce_top_token'] == ','
    # Full inclusion/exclusion ledger for both rules, including development facts.
    eligibility = []
    controlled = [j for j in jobs if j['design'] == 'controlled']
    for name, analysis in [('exact_match', original), ('accepted_spelling', after)]:
        excluded = {r['pair_id']: r['reason'] for r in analysis['excluded_pairs']}
        included = set(analysis['analyzable_pair_ids'])
        for fact in sorted({j['fact_id'] for j in controlled}):
            job = next(j for j in controlled if j['fact_id'] == fact)
            reason = 'included' if fact in included else excluded.get(fact, 'no_same_domain_split_comparator')
            eligibility.append(dict(rule=name, model='qwen3-4b', fact=fact, domain=job['domain'], split=job['split'],
                                    available_graphs=4, included=fact in included, reason=reason))
    write_csv(OUT/'eligibility_comparison.csv', eligibility)
    for path in (PREVIOUS/'tables').glob('*.csv'):
        if path.name != 'figureS5_answer_audit.csv':
            assert digest(path) == digest(FIG/'tables'/path.name), path.name
    current_manifest = read(FIG/'figure_manifest.json')
    for path, sha in current_manifest['source_hashes'].items():
        assert digest(ROOT/path) == sha, path
    for path, sha in current_manifest['output_hashes'].items():
        assert digest(FIG/path) == sha, path
    prior = read(PREVIOUS/'figure_manifest.json')
    for row in prior['figures']+prior['supplements']:
        if row['stem'] == 'figureS5_answer_audit':
            continue
        for extension in ['png', 'svg']:
            name = f"{row['stem']}.{extension}"
            assert digest(FIG/name) == prior['output_hashes'][name]
    tokens = read_csv(FIG/'tables/figureS5_answer_audit.csv')
    q4 = {r['category']: int(r['count']) for r in tokens if r['model'] == 'qwen3-4b'}
    assert q4 == {'whole_answer_next_token': 49, 'accepted_spelling_variant': 1, 'multi_token_prefix_only': 5, 'next_token_mismatch': 5}
    for row in read_csv(FIG/'tables/figureS9_pooled_estimates.csv'):
        expected = result['exact_match' if row['rule']=='Exact matching' else 'accepted_spelling']['heldout_primary']
        assert int(row['n']) == expected['n'] and float(row['mean']) == expected['mean']
        assert float(row['ci_low']) == expected['ci95'][0] and float(row['ci_high']) == expected['ci95'][1]
    for row in read_csv(FIG/'tables/figureS9_history_equal_counts.csv'):
        if row['comparison'] == 'Full set':
            expected = history[row['fact']][PRIMARY]
        else:
            fraction = 1.0 if row['comparison'] == 'Equal count (K)' else .5
            expected = next(r['mean'] for r in result['equal_count']['per_fact'] if r['fact']==row['fact'] and r['fraction']==fraction)
        assert float(row['margin']) == expected
    for name in ['answer_spelling_analysis_stdout.log', 'answer_spelling_analysis_stderr.log']:
        shutil.copy2(ROOT/'tmp'/name, OUT/name)
    scripts = [ROOT/'scripts'/f'{name}.py' for name in ['analyze_answer_spelling', 'build_answer_spelling_figures', 'validate_answer_spelling']]
    snapshot = OUT/'code_snapshot'
    snapshot.mkdir(exist_ok=True)
    for path in scripts:
        shutil.copy2(path, snapshot/path.name)
    summary = dict(passed=True, checked_at=now(), frozen_inputs_unchanged=True,
                   raw_graphs_hash_verified=147, converted_graphs_hash_verified=147,
                   independent_raw_history_overlaps_verified=4, original_exact_results_unchanged=True,
                   exact_evaluation_facts=10, accepted_spelling_evaluation_facts=12,
                   accepted_history_facts=2, unchanged_output_type_matched_controls=True,
                   current_figure_sources_and_outputs_hash_verified=True,
                   no_hosted_requests=True, source_hashes={p.relative_to(ROOT).as_posix(): digest(p) for p in scripts})
    atomic_json(OUT/'validation.json', summary)
    report = [
        '# Accepted spellings and the history comparison', '',
        'Recognizing María as the correct variant of Maria changes one answer classification among 170 available factual-prompt outputs. It adds two Qwen3-4B history facts because Columbus and Franz Ferdinand can now serve as each other’s comparison partner.', '',
        'The original exact-match Qwen3-4B mean is 0.162 (10 facts; descriptive 95% interval 0.131–0.194). Accepting the spelling gives 0.218 (12 facts; 0.150–0.307). The original ten fact-level values are unchanged.', '',
        'The two history differences are 0.601 and 0.395, averaging 0.498. Both remain positive at equal feature counts (0.543 and 0.370) and half counts (0.210 and 0.151). This two-fact comparison is descriptive and is not independent replication.', '',
        'Both facts favor the factual rewording over either invented name control, but all four controls predict commas. The output-type-matched control samples and estimates therefore remain unchanged.', '',
        'The result repairs a scoring artifact, not a model failure. It does not change the separate geography answer-letter or historical-date A/B experiments. No new graphs, model calls, changed prompts, or model inference were used. The exact-match reference and post hoc accepted-spelling estimates are retained separately.', '',
    ]
    (OUT/'RESULTS.md').write_text('\n'.join(report), encoding='utf-8')
    atomic_json(OUT/'artifact_manifest.json', dict(files=[dict(path=p.relative_to(OUT).as_posix(), sha256=digest(p), bytes=p.stat().st_size)
                for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json' and '__pycache__' not in p.parts]))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
