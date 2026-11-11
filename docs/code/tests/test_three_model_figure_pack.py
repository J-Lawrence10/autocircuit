"""Guard against presenting incomplete or inconsistent cohorts as complete."""
import copy
import json
import unittest

from scripts.build_three_model_figure_pack import (
    EXTENSION, ORIGINAL, PRIMARY, release_status, validate_arithmetic,
)


class FigurePackTests(unittest.TestCase):
    def cohort(self):
        return [dict(job_id=f'{design}_{i}', design=design, status='ok')
                for design, n in [('controlled', 120), ('crossed', 27)]
                for i in range(n)]

    def test_complete_cohort(self):
        self.assertTrue(release_status(self.cohort())['full_cohort_complete'])

    def test_failure_or_duplicate_prevents_completion(self):
        rows = self.cohort()
        rows[0]['status'] = 'missing_raw'
        self.assertFalse(release_status(rows)['full_cohort_complete'])
        rows = self.cohort()
        rows[0]['job_id'] = rows[1]['job_id']
        self.assertFalse(release_status(rows)['full_cohort_complete'])

    def test_missing_row_prevents_completion(self):
        self.assertFalse(release_status(self.cohort()[:-1])['full_cohort_complete'])

    def test_saved_arithmetic_and_mismatch_detection(self):
        original = json.loads((ORIGINAL / 'whole_graph_results.json').read_text())
        ext = json.loads((EXTENSION / 'analysis/model_extension_results.json').read_text())
        results = [original['models']['gemma'], original['models']['qwen'], ext['controlled']]
        crossed = [('Gemma', original['format_variation']), ('Qwen4', ext['crossed'])]
        self.assertEqual(len(validate_arithmetic(results, crossed)), 5)
        altered = copy.deepcopy(results)
        next(r for r in altered[0]['per_fact'] if r['split'] == 'held_out')[PRIMARY] += .01
        with self.assertRaises(AssertionError):
            validate_arithmetic(altered, crossed)


if __name__ == '__main__':
    unittest.main()
