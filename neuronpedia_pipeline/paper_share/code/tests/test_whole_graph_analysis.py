import unittest

from scripts.whole_graph_analysis import (
    complete_pair_ids,
    exact_sign_flip_p,
    holm_adjust,
    is_error_node,
    is_feature_node,
    jaccard,
    normalize_prompt,
    sparse_cosine,
    summarize_graph,
    summarize_values,
)


class WholeGraphAnalysisTests(unittest.TestCase):
    def test_prompt_normalization_removes_exporter_special_tokens(self):
        expected = "the chemical symbol for gold is"
        self.assertEqual(normalize_prompt("<bos>The chemical symbol for gold is"), expected)
        self.assertEqual(normalize_prompt("<|im_end|>The chemical symbol for gold is"), expected)
        self.assertEqual(normalize_prompt("<|endoftext|>The chemical symbol for gold is"), expected)

    def test_error_is_not_feature(self):
        node = {
            "id": "e",
            "layer": 0,
            "feature_id": -1,
            "node_type": "mlp reconstruction error",
            "influence": 1.0,
        }
        self.assertTrue(is_error_node(node))
        self.assertFalse(is_feature_node(node))

    def test_feature_namespaces_stay_distinct(self):
        graph = {
            "metadata": {"prompt": "p", "model": "m"},
            "nodes": [
                {"id": "a", "layer": 0, "feature_id": 1, "node_type": "lorsa", "influence": 1.0},
                {
                    "id": "b",
                    "layer": 0,
                    "feature_id": 1,
                    "node_type": "cross layer transcoder",
                    "influence": 1.0,
                },
            ],
            "edges": [{"source": "a", "target": "b", "weight": 2.0}],
        }
        audit, representation = summarize_graph(
            graph, path=None, file_sha256="test", raw_schema=False
        )
        self.assertEqual(audit["unique_feature_identity_count"], 2)
        self.assertEqual(len(representation["features"]), 2)

    def test_ambiguous_nodes_and_edges_are_excluded(self):
        graph = {
            "metadata": {},
            "nodes": [
                {"id": "x", "layer": 0, "feature_id": 1, "node_type": "feature", "influence": 1.0},
                {"id": "x", "layer": 0, "feature_id": -1, "node_type": "error", "influence": 1.0},
                {"id": "y", "layer": 1, "feature_id": 2, "node_type": "feature", "influence": 1.0},
            ],
            "edges": [{"source": "x", "target": "y", "weight": 1.0}],
        }
        audit, representation = summarize_graph(
            graph, path=None, file_sha256="test", raw_schema=False
        )
        self.assertEqual(audit["ambiguous_node_id_count"], 1)
        self.assertEqual(audit["dangling_edge_count"], 0)
        self.assertEqual(audit["ambiguous_incident_edge_count"], 1)
        self.assertEqual(len(representation["features"]), 1)
        self.assertEqual(representation["eligible_edge_count"], 0)

    def test_similarity_metrics(self):
        self.assertEqual(jaccard({1, 2}, {2, 3}), 1 / 3)
        self.assertAlmostEqual(sparse_cosine({"x": 1}, {"x": 2}), 1.0)
        self.assertEqual(sparse_cosine({}, {"x": 2}), 0.0)

    def test_exact_sign_flip(self):
        self.assertEqual(exact_sign_flip_p([1.0, 1.0]), 0.25)
        self.assertEqual(exact_sign_flip_p([-1.0, -1.0]), 1.0)

    def test_descriptive_summary_skips_exact_test(self):
        summary = summarize_values(
            [1.0] * 30, bootstrap_runs=10, seed=1, run_exact_test=False
        )
        self.assertTrue(summary["exact_one_sided_sign_flip_p"] != summary["exact_one_sided_sign_flip_p"])

    def test_holm_is_monotone_in_sorted_order(self):
        adjusted = holm_adjust([0.01, 0.04, 0.03])
        self.assertEqual(adjusted, [0.03, 0.06, 0.06])

    def test_factual_pair_requires_correct_target_and_paraphrase(self):
        roles = {
            ("ok", role): {"top_token_matches_expected": True}
            for role in [
                "target",
                "positive_paraphrase",
                "negative_same_template",
                "negative_nonce",
            ]
        }
        roles[("bad", "target")] = {"top_token_matches_expected": False, "top_token": "wrong"}
        roles[("bad", "positive_paraphrase")] = {"top_token_matches_expected": True}
        roles[("bad", "negative_same_template")] = {}
        roles[("bad", "negative_nonce")] = {}
        eligible, excluded = complete_pair_ids(roles)
        self.assertEqual(eligible, ["ok"])
        self.assertEqual(excluded[0]["reason"], "expected_token_not_top_prediction")


if __name__ == "__main__":
    unittest.main()
