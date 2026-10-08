import unittest
from pathlib import Path

from scripts.generate_model_extension import controlled_jobs, crossed_jobs, graph_path


class ModelExtensionTests(unittest.TestCase):
    def test_registered_job_counts_and_ids(self):
        jobs = controlled_jobs() + crossed_jobs()
        self.assertEqual(len(controlled_jobs()), 120)
        self.assertEqual(len(crossed_jobs()), 27)
        self.assertEqual(len({job["job_id"] for job in jobs}), 147)

    def test_crossed_expected_tokens_are_frozen(self):
        jobs = crossed_jobs()
        expected = {(job["domain"], job["fact_id"]): job["expected_token"] for job in jobs}
        self.assertEqual(expected[("chemistry", "gold")], "Au")
        self.assertEqual(expected[("geography", "france")], "Paris")
        self.assertEqual(expected[("history", "wwii")], "1945")

    def test_graph_paths_stay_under_extension_root(self):
        for job in controlled_jobs() + crossed_jobs():
            path = graph_path("qwen3-4b", job).resolve()
            self.assertIn("model_extension", path.parts)
            self.assertEqual(path.name, "raw_graph.json")
            self.assertNotIn("..", Path(job["job_id"]).parts)


if __name__ == "__main__":
    unittest.main()
