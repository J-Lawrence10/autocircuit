"""Offline package integrity and current-cohort table checks; standard library only.

This checks saved evidence, not raw-graph reproduction or scientific validity.
Run: python code/verify_package.py from the paper_share directory.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
QWEN = 'Qwen3-1.7B'
PRIMARY = 'feature_jaccard__margin_other_factual_mean'
COHORT = 'expanded91_late_observational'


def is_qwen(value):
    return value.casefold() == 'qwen3-1.7b'


def close(actual, expected, label='value'):
    actual, expected = float(actual), float(expected)
    assert math.isfinite(actual) and math.isfinite(expected), label
    assert abs(actual - expected) <= 1e-12, (label, actual, expected)


def check_summary(row, expected):
    assert int(row['n']) == expected['n'], (row, expected['n'])
    close(row['mean'], expected['mean'], 'mean')
    interval = expected.get('ci95', expected.get('ci95_descriptive'))
    close(row['ci_low'], interval[0], 'ci_low')
    close(row['ci_high'], interval[1], 'ci_high')


def verify_current_tables(rows, late, display):
    """Reconcile current presentation tables to immutable saved analysis results."""
    assert late['status'] == 'completed' and late['original_reconstruction']['passed']
    assert late['input_counts'] == {
        'original_raw': 50, 'new_raw': 41, 'combined_raw': 91, 'length_rejections': 29}
    # Preserve the historical result as provenance, not as a second current model.
    old = late['cohorts']['original50_reconstructed']['heldout_primary']
    assert old['n'] == 5
    close(old['mean'], .08542266140474333, 'archived original mean')
    close(old['exact_one_sided_sign_flip_p'], .03125, 'archived original p')
    close(old['ci95'][0], .07559125766022748, 'archived original interval lower')
    close(old['ci95'][1], .09526537124736285, 'archived original interval upper')
    expanded = late['cohorts'][COHORT]
    primary = expanded['heldout_primary']
    assert primary['n'] == primary['positive_n'] == 10
    close(primary['mean'], .08943970371340235, 'current primary mean')
    close(primary['exact_one_sided_sign_flip_p'], 1 / 1024, 'current nominal sign flip')
    permutation = expanded['robustness']['exact_fact_label_permutation']
    assert permutation['exact_permutation_count'] == 14400
    close(permutation['exact_one_sided_p'], 1 / 14400, 'conditional permutation')
    # This is the fixed 4-metric x 4-contrast secondary family minus the primary.
    secondary = [(metric, contrast) for metric, contrasts in expanded['aggregates']['held_out'].items()
                 for contrast, summary in contrasts.items() if 'holm_adjusted_p' in summary]
    expected_secondary = {(metric, contrast)
                          for metric in ['feature_jaccard', 'feature_influence_cosine', 'layer_profile_cosine', 'edge_flow_cosine']
                          for contrast in ['margin_other_factual_mean', 'margin_other_factual_max', 'margin_same_template_nonce', 'margin_paraphrased_nonce']}
    expected_secondary.remove(('feature_jaccard', 'margin_other_factual_mean'))
    assert len(secondary) == 15 and set(secondary) == expected_secondary

    current = rows('figure2_summary.csv')
    assert len(current) == 3
    by_model = {r['model']: r for r in current}
    assert set(by_model) == {'Gemma-2-2B', QWEN, 'Qwen3-4B'}
    assert [int(by_model[m]['n']) for m in ['Gemma-2-2B', QWEN, 'Qwen3-4B']] == [8, 10, 12]
    assert [round(float(by_model[m]['mean']), 3) for m in ['Gemma-2-2B', QWEN, 'Qwen3-4B']] == [.170, .089, .218]
    check_summary(by_model[QWEN], primary)
    close(by_model[QWEN]['exact_one_sided_sign_flip_p'], primary['exact_one_sided_sign_flip_p'])
    assert int(by_model[QWEN]['positive_n']) == 10
    fact_rows = rows('figure2_fact_level.csv')
    assert len(fact_rows) == 30  # Model-specific observations, not independent unique facts.
    qwen_facts = [r for r in fact_rows if r['model'] == QWEN]
    expected = {r['pair_id']: r for r in expanded['per_fact'] if r['split'] == 'held_out'}
    assert len(qwen_facts) == len(expected) == 10
    assert {r['pair_id'] for r in qwen_facts} == set(expected)
    for row in qwen_facts:
        assert row['domain'] == expected[row['pair_id']]['domain']
        close(row[PRIMARY], expected[row['pair_id']][PRIMARY], row['pair_id'])
    assert sum(r['domain'] == 'chemistry' for r in qwen_facts) == 5
    assert sum(r['domain'] == 'geography' for r in qwen_facts) == 5

    inclusion = rows('test_fact_inclusion_audit.csv')
    assert len(inclusion) == len({(r['model'], r['pair_id']) for r in inclusion}) == 45
    for model, included in [('Gemma-2-2B', 8), (QWEN, 10), ('Qwen3-4B', 12)]:
        subset = [r for r in inclusion if r['model'] == model]
        assert len(subset) == 15 and sum(str(r['included']) == 'True' for r in subset) == included
    expected_inclusion = {r['pair_id']: r for r in late['eligibility']
                          if r['cohort'] == COHORT and r['split'] == 'held_out'}
    for row in (r for r in inclusion if r['model'] == QWEN):
        saved = expected_inclusion[row['pair_id']]
        assert row['domain'] == saved['domain']
        assert int(row['available_graphs']) == len(saved['present_roles'])
        assert int(row['planned_graphs']) == 4
        assert str(row['included']) == str(saved['included_in_comparisons'])
        assert row['reason'] == saved['exclusion_reason']
        assert json.loads(row['observed_mismatched_tokens']) == {
            role: saved['factual_outputs'][role] for role in saved['incorrect_factual_roles']}

    controls = [r for r in rows('figure4_controls.csv') if r['model'] == QWEN]
    assert len(controls) == 2
    assert {r['control'] for r in controls} == {'same_template_nonce', 'paraphrased_nonce'}
    for row in controls:
        check_summary(row, expanded['robustness']['output_type_matched_controls'][row['control']])
    assert {r['control']: int(r['n']) for r in controls} == {'same_template_nonce': 9, 'paraphrased_nonce': 10}

    assert display['status'] == 'completed' and display['original_reconciliation']['passed']
    assert display['no_hosted_requests'] and not display['eligibility_changed'] and not display['primary_statistics_changed']
    audit = display['cohorts']['expanded91']
    quality = rows('figureS1_quality.csv')
    qwen_quality = [r for r in quality if r['cohort'] == 'Qwen1.7 controlled']
    assert len(qwen_quality) == 1
    assert int(qwen_quality[0]['graphs']) == audit['quality']['graph_n'] == 91
    assert int(qwen_quality[0]['ambiguous_raw_exports']) == audit['quality']['ambiguous_export_n'] == 0
    close(qwen_quality[0]['error_influence_median_percent'], audit['quality']['error_influence_median_percent'])
    assert sum(int(r['graphs']) for r in quality) == 385  # 342 archived + 41 Qwen1.7 + 2 Qwen4 exports.

    robust = [r for r in rows('figureS2_robustness.csv') if r['model'] == QWEN]
    expected_robust = {
        'Primary': primary,
        'Errors included': expanded['robustness']['error_inclusive_heldout']['feature_jaccard_with_errors'],
        'Clean exports': expanded['robustness']['clean_export_heldout_primary'],
        'Hardest other fact': expanded['aggregates']['held_out']['feature_jaccard']['margin_other_factual_max'],
    }
    assert len(robust) == len(expected_robust)
    for row in robust:
        check_summary(row, expected_robust[row['sensitivity']])

    equal = [r for r in rows('figureS3_equal_counts.csv') if is_qwen(r['model'])]
    equal_saved = late['equal_count_sensitivity'][COHORT]['summaries']
    equal_expected = {'full_set': primary,
                      'equal_count': next(s for s in equal_saved if s['fraction'] == 1),
                      'half_count': next(s for s in equal_saved if s['fraction'] == .5)}
    assert len(equal) == 3 and {r['comparison'] for r in equal} == set(equal_expected)
    for row in equal:
        check_summary(row, equal_expected[row['comparison']])

    lexical = [r for r in rows('figureS4_lexical_support.csv') if is_qwen(r['model'])]
    assert len(lexical) == 3 and {r['rule'] for r in lexical} == {s['rule'] for s in audit['lexical']['summaries']}
    for row in lexical:
        assert int(row['eligible_n']) == 10 and int(row['n']) == 0
        assert row['mean'] in ('', None), 'Unavailable word matches must not be displayed as zero.'
    assert (audit['lexical']['own_pairs_same_expected_answer_n'],
            audit['lexical']['other_fact_pairs_same_expected_answer_n'],
            audit['lexical']['other_fact_pair_n']) == (10, 0, 40)
    token_rows = [r for r in rows('figureS5_answer_audit.csv') if is_qwen(r['model'])]
    tokens = {r['category']: int(r['count']) for r in token_rows}
    assert len(tokens) == len(token_rows)
    if 'accepted_spelling_variant' in tokens:
        assert tokens.pop('accepted_spelling_variant') == 0
    assert tokens == {'whole_answer_next_token': 42, 'multi_token_prefix_only': 4, 'next_token_mismatch': 4}
    assert tokens == audit['answers']['statuses'] and sum(tokens.values()) == 50
    assert all(int(r['total']) == 50 for r in token_rows)

    collection = {r['domain']: r for r in rows('figureS7_collection.csv')}
    assert set(collection) == {'chemistry', 'geography', 'history'}
    for domain, available, complete, rejected in [('chemistry', 40, 10, 0), ('geography', 40, 10, 0), ('history', 11, 0, 29)]:
        row = collection[domain]
        assert (int(row['planned_graphs']), int(row['available_graphs']), int(row['complete_four_role_sets']),
                int(row['length_rejected_jobs'])) == (40, available, complete, rejected)
    facts = rows('figureS7_per_fact.csv')
    assert len(facts) == primary['n'] and not any(r['domain'] == 'history' for r in facts)
    close(mean(float(r['margin']) for r in facts), primary['mean'])
    for row in rows('figureS7_domain_summary.csv'):
        if row['domain'] == 'history':
            assert row['status'] == 'unavailable' and not row['mean']
        else:
            summary = expanded['heldout_domains'][row['domain']]
            assert int(row['included_evaluation_facts']) == summary['n']
            close(row['mean'], summary['mean'])
            close(row['ci95_low'], summary['ci95'][0])
            close(row['ci95_high'], summary['ci95'][1])


def verify_history_figure(rows, result, examples):
    """Check every displayed history pair against the saved 16-graph analysis."""
    assert result['valid_graphs'] == result['observed'] == result['planned'] == 16
    assert result['correct'] == 11 and result['wrong'] == 5 and result['preview_matches'] == 16
    audits = {r['job_id']: r for r in result['audits']}
    assert len(audits) == 16 and all(r['graph_eligible'] for r in audits.values())
    assert sum(r['correct'] for r in audits.values()) == 11
    pairs = {(r['a'], r['b']): r for r in result['pairs']}
    assert len(pairs) == 56 and all(r['status'] == 'ok' for r in pairs.values())
    displayed = rows('figure7_history_answers_source.csv')
    assert len(displayed) == 16
    for panel, flag in [('b', 'mapping_only'), ('c', 'order_only')]:
        subset = [r for r in displayed if r['panel'] == panel]
        expected = {key for key, pair in pairs.items() if pair[flag]}
        assert len(subset) == len(expected) == 8
        assert {(r['a'], r['b']) for r in subset} == expected
        assert len({r[side] for r in subset for side in ('a', 'b')}) == 16
        assert sum(r['same_letter'] == 'True' for r in subset) == 5
        for row in subset:
            pair = pairs[(row['a'], row['b'])]
            close(row['jaccard'], pair['jaccard'], (panel, row['a'], row['b']))
            assert row['same_letter'] == str(pair['same_predicted_letter'])
            assert row['same_year'] == str(pair['same_predicted_year'])
            for side in ('a', 'b'):
                audit = audits[row[side]]
                assert row[f'correct_{side}'] == str(audit['correct'])
                assert row[f'observed_{side}'] == audit['observed']
                assert int(row[f'selected_year_{side}']) == audit['predicted_year']
            if panel == 'b':
                assert pair['same_predicted_year'] is not pair['same_predicted_letter']
    assert len(examples) == 2
    for example in examples:
        first, second = example['prompts']
        close(example['jaccard'], pairs[(first['job_id'], second['job_id'])]['jaccard'])
        for prompt in example['prompts']:
            audit = audits[prompt['job_id']]
            assert prompt['predicted_letter'] == audit['observed']
            assert prompt['selected_year'] == audit['predicted_year']
            assert prompt['correct'] == audit['correct']
    all_rows = rows('history_all_pairs.csv')
    assert len(all_rows) == 56 and {(r['a'], r['b']) for r in all_rows} == set(pairs)
    for row in all_rows:
        close(row['jaccard'], pairs[(row['a'], row['b'])]['jaccard'])


def verify_corrected_tables(rows, final, spelling):
    """Require corrected scoring in every dependent current Qwen3-4B display."""
    assert final['status']=='completed' and final['no_hosted_requests']
    accepted=final['controlled']
    assert accepted==spelling['accepted_spelling']
    primary=accepted['heldout_primary']
    assert primary['n']==primary['positive_n']==12
    close(primary['mean'],.21832503734816042)
    close(primary['exact_one_sided_sign_flip_p'],1/4096)
    close(accepted['robustness']['exact_fact_label_permutation']['exact_one_sided_p'],1/28800)
    check_summary(next(r for r in rows('figure2_summary.csv') if r['model']=='Qwen3-4B'),primary)
    expected={r['pair_id']:r for r in accepted['per_fact'] if r['split']=='held_out'}
    points=[r for r in rows('figure2_fact_level.csv') if r['model']=='Qwen3-4B']
    assert len(points)==len(expected)==12 and {r['pair_id'] for r in points}==set(expected)
    for r in points:
        for key in [k for k in expected[r['pair_id']] if k.startswith('feature_jaccard__')]:
            close(r[key],expected[r['pair_id']][key])
    history={r['pair_id'] for r in points if r['domain']=='history'}
    assert history=={'columbus_americas','wwi_start'}
    for row in rows('test_fact_inclusion_audit.csv'):
        if row['model']=='Qwen3-4B':
            assert (row['included']=='True')==(row['pair_id'] in expected)
    specs={'Primary':primary,
           'Errors included':accepted['robustness']['error_inclusive_heldout']['feature_jaccard_with_errors'],
           'Clean exports':accepted['robustness']['clean_export_heldout_primary'],
           'Hardest other fact':accepted['aggregates']['held_out']['feature_jaccard']['margin_other_factual_max']}
    for row in rows('figureS2_robustness.csv'):
        if row['model']=='Qwen3-4B':
            check_summary(row,specs[row['sensitivity']])
    eq={1.0:'equal_count',.5:'half_count'}
    stats={eq[s['fraction']]:s for s in final['equal_count']['summaries']}
    stats['full_set']=primary
    for row in rows('figureS3_equal_counts.csv'):
        if row['model']=='qwen3-4b':
            check_summary(row,stats[row['comparison']])
    equal_rows=[r for r in rows('figureS3_per_fact.csv') if r['model']=='qwen3-4b']
    assert {r['fact'] for r in equal_rows}==set(expected)
    for row in equal_rows:
        close(row['full_set'],expected[row['fact']][PRIMARY])
        for fraction,key in eq.items():
            saved=next(r for r in final['equal_count']['rows'] if r['fact']==row['fact'] and r['fraction']==fraction)
            close(row[key],saved['mean_margin'])
    lexical=[r for r in rows('figureS4_lexical_scatter.csv') if r['model']=='qwen3-4b']
    assert {r['fact'] for r in lexical}==set(expected)
    for row in lexical:
        saved=next(r for r in final['lexical']['scatter'] if r['fact']==row['fact'])
        for key in ['own_word_overlap','best_other_word_overlap']:
            close(row[key],saved[key])
    for row in rows('figureS4_lexical_support.csv'):
        if row['model']=='qwen3-4b':
            assert int(row['eligible_n'])==12 and int(row['n'])==0
    answers={r['category']:int(r['count']) for r in rows('figureS5_answer_audit.csv') if r['model']=='qwen3-4b'}
    assert answers==final['answers']['statuses']=={'whole_answer_next_token':50,'multi_token_prefix_only':5,'next_token_mismatch':5}
    for row in rows('figure4_controls.csv'):
        if row['model']=='Qwen3-4B':
            check_summary(row,accepted['robustness']['output_type_matched_controls'][row['control']])
    assert accepted['robustness']['output_type_matched_controls']==spelling['exact_match']['robustness']['output_type_matched_controls']
    comparisons=rows('figureS9_history_comparisons.csv')
    assert len(comparisons)==4
    for row in comparisons:
        saved=next(r for r in final['history_comparisons'] if r['fact']==row['fact'] and r['comparator']==row['comparator'])
        close(row['jaccard'],saved['jaccard'])


def verify_package(root=ROOT):
    root = Path(root).resolve()
    manifest = json.loads((root/'provenance/package_manifest.json').read_text(encoding='utf-8'))
    for row in manifest['files']:
        p = (root/row['path']).resolve()
        assert p.is_relative_to(root), row['path']
        assert p.is_file() and p.stat().st_size == row['bytes'], row['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], row['path']

    def rows(name):
        with (root/'tables'/name).open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))

    assert not list((root/'tables').glob('figure*_expanded.csv')), 'Stale expanded presentation tables must be archived outside the current package.'
    late = json.loads((root/'provenance/qwen17_completion_results.json').read_text(encoding='utf-8'))
    display = json.loads((root/'provenance/qwen17_figure_audit_results.json').read_text(encoding='utf-8'))
    verify_current_tables(rows, late, display)
    recovery = json.loads((root/'provenance/qwen4_completion_verification.json').read_text(encoding='utf-8'))
    assert recovery['primary_margins_unchanged'] and recovery['original_reconstruction_passed']
    assert (recovery['complete_controlled_graphs'], recovery['complete_crossed_graphs']) == (120, 27)
    assert recovery['heldout_facts'] == 10 and recovery['heldout_history_facts'] == 0
    answer = json.loads((root/'provenance/qwen4_completion_display_audit.json').read_text(encoding='utf-8'))
    assert answer['recovered_answer']['top_text'].strip() == 'María'
    assert answer['recovered_answer']['expected'] == 'Maria'
    assert answer['recovered_answer']['strict_string_match'] is False
    spelling = json.loads((root/'provenance/answer_spelling_results.json').read_text(encoding='utf-8'))
    assert spelling['post_hoc'] and spelling['no_hosted_requests'] and len(spelling['changed_outputs']) == 1
    assert spelling['exact_match']['heldout_primary'] == recovery['current_primary']
    final = json.loads((root/'provenance/final_scoring_results.json').read_text(encoding='utf-8'))
    verify_corrected_tables(rows, final, spelling)
    assert not (root/'tables/figureS9_pooled_estimates.csv').exists(), 'Superseded before/after display retained'
    columbus = next(r for r in rows('test_fact_inclusion_audit.csv')
                    if r['model'] == 'Qwen3-4B' and r['pair_id'] == 'columbus_americas')
    assert int(columbus['available_graphs']) == 4 and columbus['included'] == 'True'
    assert columbus['reason'] == 'included' and json.loads(columbus['observed_mismatched_tokens'])=={}
    blocks = rows('figure5_block_contrasts.csv')
    assert len(blocks) == 6
    assert round(mean(float(r['fact_same_label']) for r in blocks), 4) == .0628
    assert round(mean(float(r['fact_different_label']) for r in blocks), 4) == -.0022
    pairs = {}
    for r in rows('figure6_comparisons.csv'):
        pairs.setdefault(r['job_id'], {})[r['comparator']] = float(r['jaccard'])
    assert len(pairs) == 8 and all(p['same_output'] > p['same_country'] for p in pairs.values())
    pilot = next(r for r in rows('table_history_pilot.csv') if r['component'] == 'Overall')
    assert (int(pilot['correct']), int(pilot['total'])) == (15, 20)
    history = json.loads((root/'provenance/history_results.json').read_text(encoding='utf-8'))
    examples = json.loads((root/'provenance/history_prompt_examples.json').read_text(encoding='utf-8'))
    verify_history_figure(rows, history, examples)
    print(f"Verified {len(manifest['files'])} file hashes and current-cohort values from included tables.")
    print('These checks do not reproduce raw graph extraction or provide independent scientific review.')


if __name__ == '__main__':
    verify_package()
