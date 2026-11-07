"""No new eligibility decisions: test remapping of saved current decisions."""
from copy import deepcopy
import csv
import json
from pathlib import Path
import unittest

from scripts import current_cohort_accounting as accounting

ROOT = Path(__file__).resolve().parents[1]


class CurrentAccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive_available = (ROOT/accounting.ORIGINAL).exists()
        original = ROOT/accounting.ORIGINAL if cls.archive_available else ROOT.parent/'tables/test_fact_inclusion_audit.csv'
        result = ROOT/accounting.ANALYSIS if cls.archive_available else ROOT.parent/'provenance/qwen17_completion_results.json'
        with original.open(encoding='utf-8-sig', newline='') as handle:
            cls.old = list(csv.DictReader(handle))
        cls.analysis = json.loads(result.read_text(encoding='utf-8'))

    def test_current_counts(self):
        rows = accounting.reconcile_rows(self.old, self.analysis)
        self.assertEqual(len(rows), 45)
        self.assertEqual(sum(r['included'] == 'True' for r in rows), 28)
        self.assertEqual(sum(int(r['available_graphs']) for r in rows if r['model'] == accounting.MODEL), 45)

    def test_frozen_archive_hashes(self):
        if not self.archive_available:
            self.skipTest('Full frozen author archive is intentionally not in the portable package.')
        self.assertEqual(accounting.input_hashes(ROOT), accounting.FROZEN)

    def test_other_models_unchanged(self):
        current = accounting.reconcile_rows(self.old, self.analysis)
        self.assertEqual([r for r in current if r['model'] != accounting.MODEL],
                         [r for r in self.old if r['model'] != accounting.MODEL])

    def test_empty_and_partial_history_remain_missing_role_exclusions(self):
        history = [r for r in accounting.reconcile_rows(self.old, self.analysis)
                   if r['model'] == accounting.MODEL and r['domain'] == 'history']
        self.assertEqual(sorted(int(r['available_graphs']) for r in history), [0, 0, 1, 2, 2])
        self.assertTrue(all(r['reason'] == 'incomplete_roles' and r['included'] == 'False' for r in history))
        french = next(r for r in history if r['pair_id'] == 'french_revolution')
        self.assertEqual(json.loads(french['observed_mismatched_tokens']),
                         {'positive_paraphrase': ' Bast', 'target': ' one'})

    def test_duplicate_saved_fact_is_rejected(self):
        analysis = deepcopy(self.analysis)
        row = next(r for r in analysis['eligibility']
                   if r['cohort'] == accounting.COHORT and r['split'] == 'held_out')
        analysis['eligibility'].append(deepcopy(row))
        with self.assertRaises(AssertionError):
            accounting.reconcile_rows(self.old, analysis)

    def test_missing_role_cannot_be_treated_as_present(self):
        analysis = deepcopy(self.analysis)
        row = next(r for r in analysis['eligibility']
                   if r['cohort'] == accounting.COHORT and r['pair_id'] == 'wwi_start')
        row['present_roles'] = ['target']
        with self.assertRaises(AssertionError):
            accounting.reconcile_rows(self.old, analysis)


if __name__ == '__main__':
    unittest.main()
