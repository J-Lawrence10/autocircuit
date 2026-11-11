"""Saved-result reconciliation tests; no model calls, extraction, or new inference."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


BASE = Path(__file__).resolve().parents[1]
SCRIPT = BASE/'paper_share/code/verify_package.py'
if not SCRIPT.exists():
    SCRIPT = BASE/'verify_package.py'  # Portable package code/tests layout.
spec = importlib.util.spec_from_file_location('current_package_verifier', SCRIPT)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
ARCHIVE = BASE/'data/model_extension/qwen17_completion_20261106'
if ARCHIVE.exists():
    RESULT = ARCHIVE/'analysis/results.json'
    AUDIT = ARCHIVE/'figure_audit/results.json'
else:
    RESULT = BASE.parent/'provenance/qwen17_completion_results.json'
    AUDIT = BASE.parent/'provenance/qwen17_figure_audit_results.json'


def row(summary, **extra):
    interval = summary.get('ci95', summary.get('ci95_descriptive'))
    return dict(n=summary['n'], mean=summary['mean'], ci_low=interval[0], ci_high=interval[1],
                positive_n=summary.get('positive_n', ''),
                exact_one_sided_sign_flip_p=summary.get('exact_one_sided_sign_flip_p', ''), **extra)


def fixture(late, display):
    """Construct only display rows, directly from already-saved results."""
    exp = late['cohorts'][verify.COHORT]
    primary = exp['heldout_primary']
    facts = [r for r in exp['per_fact'] if r['split'] == 'held_out']
    audits = display['cohorts']['expanded91']
    tables = {
        'figure2_summary.csv': [dict(model='Gemma-2-2B', n=8, mean=.17035573839323534),
                                row(primary, model=verify.QWEN),
                                dict(model='Qwen3-4B', n=12, mean=.21832503734816042)],
        'figure2_fact_level.csv': [dict(model='Gemma-2-2B') for _ in range(8)] +
                                  [dict(r, model=verify.QWEN) for r in facts] +
                                  [dict(model='Qwen3-4B') for _ in range(12)],
        'figure4_controls.csv': [row(s, model=verify.QWEN, control=k)
                                 for k, s in exp['robustness']['output_type_matched_controls'].items()],
        'figureS1_quality.csv': [dict(cohort='Gemma controlled', graphs=120),
                                 dict(cohort='Gemma crossed', graphs=27),
                                 dict(cohort='Qwen4 controlled', graphs=120),
                                 dict(cohort='Qwen4 crossed', graphs=27),
                                 dict(cohort='Qwen1.7 controlled', graphs=91, ambiguous_raw_exports=0,
                                      error_influence_median_percent=audits['quality']['error_influence_median_percent'])],
        'figureS2_robustness.csv': [row(s, model=verify.QWEN, sensitivity=k) for k, s in {
            'Primary': primary,
            'Errors included': exp['robustness']['error_inclusive_heldout']['feature_jaccard_with_errors'],
            'Clean exports': exp['robustness']['clean_export_heldout_primary'],
            'Hardest other fact': exp['aggregates']['held_out']['feature_jaccard']['margin_other_factual_max'],
        }.items()],
        'figureS3_equal_counts.csv': [row(primary, model=verify.QWEN, comparison='full_set')] + [
            row(s, model=verify.QWEN, comparison='equal_count' if s['fraction'] == 1 else 'half_count')
            for s in late['equal_count_sensitivity'][verify.COHORT]['summaries']],
        'figureS4_lexical_support.csv': [dict(s, model=verify.QWEN) for s in audits['lexical']['summaries']],
        'figureS5_answer_audit.csv': [dict(model=verify.QWEN, category=k, count=v, total=50)
                                    for k, v in audits['answers']['statuses'].items()],
        'figureS7_collection.csv': deepcopy(late['collection_by_domain']),
        'figureS7_per_fact.csv': [dict(domain=r['domain'], margin=r[verify.PRIMARY]) for r in facts],
        'figureS7_domain_summary.csv': [dict(domain=d, included_evaluation_facts=s['n'], mean=s['mean'],
                                           ci95_low=s['ci95'][0], ci95_high=s['ci95'][1], status='estimated')
                                      for d, s in exp['heldout_domains'].items()] +
                                     [dict(domain='history', included_evaluation_facts=0, mean='', status='unavailable')],
    }
    tables['test_fact_inclusion_audit.csv'] = [dict(model=m, pair_id=f'fixture_{i}', included=str(i < n))
                                              for m, n in [('Gemma-2-2B', 8), ('Qwen3-4B', 12)] for i in range(15)]
    tables['test_fact_inclusion_audit.csv'].extend(
        dict(model=verify.QWEN, pair_id=r['pair_id'], domain=r['domain'],
             available_graphs=len(r['present_roles']), planned_graphs=4,
             included=str(r['included_in_comparisons']), reason=r['exclusion_reason'],
             observed_mismatched_tokens=json.dumps({k: r['factual_outputs'][k] for k in r['incorrect_factual_roles']}))
        for r in late['eligibility'] if r['cohort'] == verify.COHORT and r['split'] == 'held_out')
    return tables


class CurrentCohortPackageTests(unittest.TestCase):
    def setUp(self):
        self.late = json.loads(RESULT.read_text(encoding='utf-8'))
        self.audit = json.loads(AUDIT.read_text(encoding='utf-8'))
        self.tables = fixture(self.late, self.audit)

    def check(self):
        verify.verify_current_tables(self.tables.__getitem__, self.late, self.audit)

    def test_current_tables_pass_without_original_plot_panels(self):
        self.check()
        self.assertFalse(any('_expanded' in key for key in self.tables))

    def test_machine_model_ids_in_exploratory_tables(self):
        for name in ['figureS3_equal_counts.csv', 'figureS4_lexical_support.csv', 'figureS5_answer_audit.csv']:
            for item in self.tables[name]:
                item['model'] = 'qwen3-1.7b'
        self.check()

    def test_stale_original_main_count_is_rejected(self):
        self.tables['figure2_summary.csv'][1]['n'] = 5
        with self.assertRaises(AssertionError):
            self.check()

    def test_original_interval_cannot_be_reused_for_combined_mean(self):
        self.tables['figure2_summary.csv'][1]['ci_low'] = .07559125766022748
        with self.assertRaises(AssertionError):
            self.check()

    def test_duplicate_current_model_row_is_rejected(self):
        self.tables['figure2_summary.csv'].append(deepcopy(self.tables['figure2_summary.csv'][1]))
        with self.assertRaises(AssertionError):
            self.check()

    def test_stale_control_count_is_rejected(self):
        self.tables['figure4_controls.csv'][0]['n'] = 5
        with self.assertRaises(AssertionError):
            self.check()

    def test_stale_inclusion_counts_are_rejected(self):
        target = next(r for r in self.tables['test_fact_inclusion_audit.csv']
                      if r['model'] == verify.QWEN and r['domain'] == 'geography')
        target['included'] = 'False'
        with self.assertRaises(AssertionError):
            self.check()

    def test_stale_quality_denominator_is_rejected(self):
        self.tables['figureS1_quality.csv'][-1]['graphs'] = 50
        with self.assertRaises(AssertionError):
            self.check()

    def test_zero_is_not_a_missing_word_match(self):
        self.tables['figureS4_lexical_support.csv'][0]['mean'] = 0
        with self.assertRaises(AssertionError):
            self.check()

    def test_prefixes_cannot_be_folded_into_whole_answers(self):
        rows = self.tables['figureS5_answer_audit.csv']
        next(r for r in rows if r['category'] == 'whole_answer_next_token')['count'] = 46
        next(r for r in rows if r['category'] == 'multi_token_prefix_only')['count'] = 0
        with self.assertRaises(AssertionError):
            self.check()

    def test_absent_history_is_not_zero_overlap(self):
        self.tables['figureS7_domain_summary.csv'][-1]['mean'] = '0.0'
        with self.assertRaises(AssertionError):
            self.check()

    def test_historical_result_is_still_verified(self):
        self.late['cohorts']['original50_reconstructed']['heldout_primary']['mean'] = .089
        with self.assertRaises(AssertionError):
            self.check()

    def test_primary_not_in_secondary_holm_family(self):
        self.late['cohorts'][verify.COHORT]['aggregates']['held_out']['feature_jaccard']['margin_other_factual_mean']['holm_adjusted_p'] = .1
        with self.assertRaises(AssertionError):
            self.check()

    def test_nonfinite_numbers_cannot_pass_tolerance(self):
        with self.assertRaises(AssertionError):
            verify.close(float('nan'), .089)


if __name__ == '__main__':
    unittest.main()
