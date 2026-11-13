"""Synthetic tests; never access model services or real saved-data outcomes."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_qwen17_completion_figures as figures


class FigureAuditTests(unittest.TestCase):
    def test_plan_written_before_reading_analysis(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(figures, 'specification', return_value={'fixed': True}), \
                 patch.object(figures, 'read_json', side_effect=RuntimeError('stop before outcomes')):
                with self.assertRaisesRegex(RuntimeError, 'before outcomes'):
                    figures.run(root)
            record = json.loads((root/figures.REL_AUDIT/'analysis_plan.json').read_text())
            self.assertEqual(record['specification'], {'fixed': True})

    def test_changed_plan_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(figures, 'specification', return_value={'v': 1}):
                figures.ensure_plan(Path(temp))
            with patch.object(figures, 'specification', return_value={'v': 2}):
                with self.assertRaisesRegex(RuntimeError, 'explicit new version'):
                    figures.ensure_plan(Path(temp))

    def test_expanded_and_original_denominators_are_distinct(self):
        rows = [dict(collection='original'), dict(collection='late_completion')]
        self.assertEqual(len(figures.selected_rows(rows, 'original50')), 1)
        self.assertEqual(len(figures.selected_rows(rows, 'expanded91')), 2)

    def test_quality_burden_uses_percent_of_absolute_nonterminal_influence(self):
        row = {field: 0 for field in figures.FIELDS_QUALITY}
        rows = [dict(row, error_influence_fraction=.05), dict(row, error_influence_fraction=.07,
                                                              ambiguous_node_id_count=1)]
        result = figures.quality_summary(rows)
        self.assertEqual(result['graph_n'], 2)
        self.assertEqual(result['ambiguous_export_rate_percent'], 50)
        self.assertEqual(result['error_influence_percent_values'], [5, 7.000000000000001])
        self.assertAlmostEqual(result['error_influence_median_percent'], 6)

    def test_lexical_three_rules_and_shared_answer_counts(self):
        graphs = []
        features = {fact: {('feature', 0, i)} for i, fact in enumerate(['a', 'b'])}
        for fact, country, expected in [('a', 'France', 'Paris'), ('b', 'Italy', 'Rome')]:
            for role, text in [('target', f'the capital of {country} is'),
                               ('positive_paraphrase', f'{country} has its capital in')]:
                graphs.append(dict(model=figures.MODEL, design='controlled', status='ok', fact=fact,
                    role=role, manifest_prompt=text, expected=expected, features=features[fact]))
        saved = {'per_fact': [dict(pair_id=f, domain='geography', split='held_out',
                                  feature_jaccard__margin_other_factual_mean=1.0) for f in ('a', 'b')]}
        pairs, rows, summary = figures.lexical_for_cohort(graphs, saved)
        self.assertEqual(len(pairs), 4)
        self.assertEqual(len(rows), 6)
        self.assertEqual(summary['eligible_evaluation_n'], 2)
        self.assertEqual(summary['own_pairs_same_expected_answer_n'], 2)
        self.assertEqual(summary['other_fact_pairs_same_expected_answer_n'], 0)
        self.assertTrue(all(r['comparator_n'] == 0 for r in rows))
        self.assertTrue(all(r['margin'] is None for r in rows))

    def test_factual_answer_counts_preserve_partial_and_unresolved(self):
        rows = [dict(answer_status=status, strict_string_match=status == 'whole_answer_next_token',
                     domain='history', prompt_pieces_match=True, logit_decode_matches=True)
                for status in ('whole_answer_next_token', 'multi_token_prefix_only', 'next_token_mismatch',
                               'whitespace_only_compatible', 'unresolved_token_boundary')]
        result = figures.answer_summary(rows)
        self.assertEqual(result['available_factual_graph_n'], 5)
        self.assertEqual(sum(result['statuses'].values()), 5)
        self.assertEqual(result['strict_matches'], 1)
        self.assertEqual(result['statuses']['multi_token_prefix_only'], 1)
        self.assertIn('not independent facts', result['denominator_note'])

    def test_old_answer_comparison_catches_changed_status(self):
        rows = [dict(fact=str(i), role='target', answer_status='whole_answer_next_token',
                     top_text=' x', top_id=i, strict_string_match=True) for i in range(30)]
        old = [dict(row, model=figures.MODEL, design='controlled', top_id=str(row['top_id']),
                    strict_string_match='True') for row in rows]
        self.assertEqual(figures.validate_old_answers(rows, old), 30)
        changed = copy.deepcopy(rows)
        changed[0]['answer_status'] = 'multi_token_prefix_only'
        with self.assertRaisesRegex(RuntimeError, 'token audit changed'):
            figures.validate_old_answers(changed, old)


if __name__ == '__main__':
    unittest.main()
