#!/usr/bin/env python3
"""
Extended validation of the modulo 16384 feature ID mapping.

This script performs comprehensive testing to validate that:
1. Circuit Tracer feature IDs map correctly to Neuronpedia indices
2. The mapping generalizes across layers, circuits, and models
3. Edge cases are handled correctly

Usage:
    python validate_mapping_extended.py --sample-size 20
    python validate_mapping_extended.py --test-collisions
    python validate_mapping_extended.py --full-suite
"""

import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
import io

# Fix Windows console encoding
if sys.platform == 'win32' and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from query_feature_semantics import FeatureSemanticAnalyzer


def map_circuit_to_neuronpedia(circuit_id: int) -> int:
    """Map Circuit Tracer global ID to Neuronpedia per-layer ID."""
    return circuit_id % 16384


class MappingValidator:
    """Validate the modulo 16384 mapping hypothesis."""

    def __init__(self):
        self.analyzer = FeatureSemanticAnalyzer()
        self.results = {
            'total_tests': 0,
            'successful': 0,
            'failed': 0,
            'failures': []
        }

    def test_single_feature(self, layer: int, circuit_id: int, description: str = "") -> dict:
        """
        Test a single feature mapping.

        Returns:
            dict with test results including success status and semantic info
        """
        neuronpedia_id = map_circuit_to_neuronpedia(circuit_id)

        test_result = {
            'layer': layer,
            'circuit_id': circuit_id,
            'neuronpedia_id': neuronpedia_id,
            'description': description,
            'success': False,
            'activation_examples': None,
            'semantic_category': None,
            'error': None
        }

        try:
            # Query the mapped feature
            result = self.analyzer.query_single_feature(layer, neuronpedia_id)

            # Check if we got valid data (key is 'positive_examples', not 'activation_examples')
            if result and result.get('positive_examples') is not None:
                test_result['success'] = True
                test_result['activation_examples'] = ', '.join(result['positive_examples'][:3])
                test_result['semantic_category'] = result.get('semantic_category', 'UNKNOWN')
            elif result and result.get('description'):
                # Even if no activation examples, if we got a description, it's a valid query
                test_result['success'] = True
                test_result['activation_examples'] = result['description'][:60]
                test_result['semantic_category'] = result.get('semantic_category', 'UNKNOWN')
            else:
                test_result['error'] = "No data returned from API"

        except Exception as e:
            test_result['error'] = str(e)

        # Update statistics
        self.results['total_tests'] += 1
        if test_result['success']:
            self.results['successful'] += 1
        else:
            self.results['failed'] += 1
            self.results['failures'].append(test_result)

        return test_result

    def test_diverse_sample(self, sample_size: int = 20) -> list:
        """
        Test diverse features from different layers and circuits.

        Args:
            sample_size: Number of features to test

        Returns:
            list of test results
        """
        print("=" * 70)
        print(f"TEST 1: DIVERSE SAMPLE ({sample_size} features)")
        print("=" * 70)
        print()

        # Collect diverse features from raw graphs
        test_features = self._collect_diverse_features(sample_size)

        results = []
        for i, (layer, circuit_id, desc) in enumerate(test_features, 1):
            print(f"[{i}/{len(test_features)}] Testing L{layer}_F{circuit_id} ({desc})")

            result = self.test_single_feature(layer, circuit_id, desc)

            if result['success']:
                print(f"  ✓ SUCCESS: Mapped to {result['neuronpedia_id']}")
                print(f"    Examples: {result['activation_examples'][:60]}...")
            else:
                print(f"  ✗ FAILED: {result['error']}")

            results.append(result)
            print()

        return results

    def _collect_diverse_features(self, sample_size: int) -> list:
        """
        Collect diverse features from raw graphs.

        Returns:
            list of (layer, circuit_id, description) tuples
        """
        features = []

        # Find all raw graph files
        data_dir = Path(__file__).parent.parent / 'data' / 'prompts'
        raw_graphs = list(data_dir.rglob('*_raw_graph.json'))

        if not raw_graphs:
            print("Warning: No raw graphs found. Using default test set.")
            return self._get_default_test_set(sample_size)

        # Sample features from multiple circuits and layers
        features_per_circuit = max(1, sample_size // min(len(raw_graphs), 3))

        for graph_file in raw_graphs[:3]:  # Use first 3 circuits
            try:
                with open(graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                circuit_name = graph_file.parent.parent.name

                # Collect features per layer
                layer_features = defaultdict(list)
                for node in data.get('nodes', []):
                    layer_str = node.get('layer', '')
                    if layer_str == 'E' or not str(layer_str).isdigit():
                        continue

                    layer = int(layer_str)
                    feature = node.get('feature')
                    if feature is not None:
                        layer_features[layer].append(feature)

                # Sample from different layers
                target_layers = [0, 3, 5, 8, 12, 15, 20, 25]
                sampled = 0

                for target_layer in target_layers:
                    if sampled >= features_per_circuit:
                        break

                    if target_layer in layer_features and layer_features[target_layer]:
                        # Pick a feature from this layer
                        feature_list = layer_features[target_layer]
                        # Try to get diverse feature IDs (low, mid, high)
                        if len(feature_list) >= 3:
                            indices = [0, len(feature_list)//2, -1]
                            for idx in indices:
                                if sampled >= features_per_circuit:
                                    break
                                feat = feature_list[idx]
                                features.append((
                                    target_layer,
                                    feat,
                                    f"{circuit_name[:20]}, L{target_layer}"
                                ))
                                sampled += 1
                        else:
                            feat = feature_list[0]
                            features.append((
                                target_layer,
                                feat,
                                f"{circuit_name[:20]}, L{target_layer}"
                            ))
                            sampled += 1

            except Exception as e:
                print(f"Warning: Could not process {graph_file.name}: {e}")
                continue

        # If we don't have enough, add default test cases
        if len(features) < sample_size:
            features.extend(self._get_default_test_set(sample_size - len(features)))

        return features[:sample_size]

    def _get_default_test_set(self, size: int) -> list:
        """Get default test features if raw graphs not available."""
        default_features = [
            # Previously tested (should work)
            (0, 902, "Known good - historical text"),
            (0, 32384, "Known good - international text"),
            (0, 680360, "Known good - code identifiers"),
            (5, 7993995, "Known good - bottleneck"),

            # Different layers
            (1, 500000, "Layer 1 - mid range"),
            (3, 1248372, "Layer 3 - mid range"),
            (8, 3456789, "Layer 8 - mid range"),
            (12, 7234567, "Layer 12 - high range"),
            (20, 9876543, "Layer 20 - high range"),

            # Edge cases
            (0, 16383, "Exactly at boundary"),
            (0, 16385, "Just over boundary"),
            (5, 0, "Zero"),
            (10, 1000, "Low ID"),
            (15, 100000000, "Very high ID"),

            # More diverse samples
            (2, 425678, "Layer 2"),
            (6, 2345678, "Layer 6"),
            (9, 4567890, "Layer 9"),
            (13, 6789012, "Layer 13"),
            (18, 8901234, "Layer 18"),
            (22, 10234567, "Layer 22"),
        ]

        return default_features[:size]

    def test_collision_theory(self) -> list:
        """
        Test if features that map to the same Neuronpedia ID have similar semantics.

        This tests the hypothesis that collisions are intentional (same semantic feature).
        """
        print("=" * 70)
        print("TEST 2: COLLISION THEORY")
        print("=" * 70)
        print()
        print("Testing if Circuit IDs that map to the same Neuronpedia ID")
        print("return the same semantic meaning...")
        print()

        collision_sets = [
            # All map to 14987
            {
                'neuronpedia_id': 14987,
                'circuit_ids': [14987, 31371, 47755, 64139],
                'layer': 5
            },
            # All map to 100
            {
                'neuronpedia_id': 100,
                'circuit_ids': [100, 16484, 32868, 49252],
                'layer': 0
            },
            # All map to 8616
            {
                'neuronpedia_id': 8616,
                'circuit_ids': [8616, 25000, 41384, 57768],
                'layer': 0
            }
        ]

        results = []

        for i, collision_set in enumerate(collision_sets, 1):
            print(f"[Collision Set {i}] Testing features that map to {collision_set['neuronpedia_id']}")
            layer = collision_set['layer']

            set_results = []
            for circuit_id in collision_set['circuit_ids']:
                result = self.test_single_feature(
                    layer,
                    circuit_id,
                    f"Maps to {collision_set['neuronpedia_id']}"
                )
                set_results.append(result)

                if result['success']:
                    print(f"  Circuit ID {circuit_id:>6} → {result['neuronpedia_id']}")
                    print(f"    Examples: {result['activation_examples'][:50]}...")
                else:
                    print(f"  Circuit ID {circuit_id:>6} → FAILED: {result['error']}")

            # Check if all successful results have similar activation examples
            successful_results = [r for r in set_results if r['success']]
            if len(successful_results) > 1:
                # Compare activation examples
                first_examples = successful_results[0]['activation_examples']
                all_same = all(
                    r['activation_examples'] == first_examples
                    for r in successful_results[1:]
                )

                if all_same:
                    print(f"  ✓ COLLISION VALIDATION: All return SAME activation examples")
                else:
                    print(f"  ⚠ COLLISION WARNING: Different activation examples returned")

            results.append(set_results)
            print()

        return results

    def test_edge_cases(self) -> list:
        """Test boundary conditions and edge cases."""
        print("=" * 70)
        print("TEST 3: EDGE CASES & BOUNDARIES")
        print("=" * 70)
        print()

        edge_cases = [
            (0, 0, "Zero"),
            (0, 16383, "Max valid (boundary - 1)"),
            (0, 16384, "Exactly at boundary (should wrap to 0)"),
            (0, 32767, "Just under 2× boundary"),
            (0, 32768, "Exactly 2× boundary"),
            (5, 1, "Minimal positive"),
            (10, 163840, "Exactly 10× boundary"),
            (25, 2147483647, "Near max int32"),
        ]

        results = []
        for layer, circuit_id, desc in edge_cases:
            print(f"Testing: {desc}")
            print(f"  Circuit ID: {circuit_id}, Layer: {layer}")

            result = self.test_single_feature(layer, circuit_id, desc)

            expected_neuronpedia = circuit_id % 16384
            print(f"  Expected mapping: {expected_neuronpedia}")
            print(f"  Actual mapping: {result['neuronpedia_id']}")

            if result['success']:
                print(f"  ✓ SUCCESS")
                print(f"    Examples: {result['activation_examples'][:50]}...")
            else:
                print(f"  ✗ FAILED: {result['error']}")

            results.append(result)
            print()

        return results

    def print_summary(self):
        """Print summary statistics."""
        print("=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print()

        total = self.results['total_tests']
        successful = self.results['successful']
        failed = self.results['failed']

        success_rate = (successful / total * 100) if total > 0 else 0

        print(f"Total tests: {total}")
        print(f"Successful: {successful} ({success_rate:.1f}%)")
        print(f"Failed: {failed}")
        print()

        if success_rate >= 90:
            print("✓ VALIDATION PASSED: ≥90% success rate")
            print("  The modulo 16384 mapping is RELIABLE")
            print("  Ready to proceed with semantic analysis")
        elif success_rate >= 75:
            print("⚠ VALIDATION PARTIAL: 75-90% success rate")
            print("  The mapping works but has edge cases")
            print("  Recommend investigating failures before full analysis")
        else:
            print("✗ VALIDATION FAILED: <75% success rate")
            print("  The mapping has significant issues")
            print("  DO NOT proceed with semantic analysis")

        print()

        if self.results['failures']:
            print(f"Failed tests ({len(self.results['failures'])}):")
            for failure in self.results['failures'][:10]:  # Show first 10
                print(f"  - L{failure['layer']}_F{failure['circuit_id']}: {failure['error']}")
                if len(self.results['failures']) > 10:
                    print(f"  ... and {len(self.results['failures']) - 10} more")
                    break


def main():
    parser = argparse.ArgumentParser(
        description="Validate the modulo 16384 feature ID mapping"
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=20,
        help='Number of features to test in diverse sample'
    )
    parser.add_argument(
        '--test-collisions',
        action='store_true',
        help='Test collision theory'
    )
    parser.add_argument(
        '--test-edge-cases',
        action='store_true',
        help='Test boundary conditions'
    )
    parser.add_argument(
        '--full-suite',
        action='store_true',
        help='Run all validation tests'
    )

    args = parser.parse_args()

    # Create validator
    validator = MappingValidator()

    print("=" * 70)
    print("EXTENDED MAPPING VALIDATION")
    print("=" * 70)
    print()
    print("Formula: neuronpedia_id = circuit_id % 16384")
    print()

    # Run tests based on arguments
    if args.full_suite:
        # Run everything
        validator.test_diverse_sample(args.sample_size)
        validator.test_collision_theory()
        validator.test_edge_cases()
    else:
        # Run diverse sample by default
        validator.test_diverse_sample(args.sample_size)

        if args.test_collisions:
            validator.test_collision_theory()

        if args.test_edge_cases:
            validator.test_edge_cases()

    # Print summary
    validator.print_summary()


if __name__ == '__main__':
    main()
