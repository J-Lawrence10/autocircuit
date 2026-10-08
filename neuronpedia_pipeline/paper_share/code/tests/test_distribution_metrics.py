import math
import unittest

from scripts.distribution_metrics import (
    jensen_shannon_divergence,
    sequence_distribution_metrics,
    top_logprobs_distribution,
)


class DistributionMetricTests(unittest.TestCase):
    def test_js_is_symmetric_and_nonnegative(self):
        left = {'a': 0.9, 'b': 0.1}
        right = {'a': 0.2, 'b': 0.8}
        self.assertGreaterEqual(jensen_shannon_divergence(left, right), 0.0)
        self.assertAlmostEqual(
            jensen_shannon_divergence(left, right),
            jensen_shannon_divergence(right, left),
        )

    def test_residual_probability_is_retained(self):
        distribution = top_logprobs_distribution([
            {'token': 'a', 'logprob': math.log(0.6)},
            {'token': 'b', 'logprob': math.log(0.2)},
        ])
        self.assertAlmostEqual(sum(distribution.values()), 1.0)
        self.assertAlmostEqual(distribution['__OTHER__'], 0.2)

    def test_later_positions_stop_after_prefix_diverges(self):
        baseline = [
            {'token': 'a', 'topLogprobs': [{'token': 'a', 'logprob': -0.1}]},
            {'token': 'b', 'topLogprobs': [{'token': 'b', 'logprob': -0.1}]},
        ]
        steered = [
            {'token': 'x', 'topLogprobs': [{'token': 'x', 'logprob': -0.1}]},
            {'token': 'y', 'topLogprobs': [{'token': 'y', 'logprob': -0.1}]},
        ]
        metrics = sequence_distribution_metrics(baseline, steered)
        self.assertEqual(metrics['comparable_positions'], 1)
        self.assertGreaterEqual(metrics['mean_js_divergence'], 0.0)


if __name__ == '__main__':
    unittest.main()
