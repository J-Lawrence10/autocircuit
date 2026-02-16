#!/usr/bin/env python3
"""
Analyze feature ID patterns from Circuit Tracer raw graphs.

This script investigates how Circuit Tracer's feature numbering relates to
Neuronpedia's per-layer indices (0-16,383 for 16k transcoders).

Usage:
    python analyze_feature_mapping.py
    python analyze_feature_mapping.py --graph-dir ../data/prompts
"""

import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict

# Fix Windows console encoding
import io
if sys.platform == 'win32' and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def analyze_raw_graph(graph_file: Path) -> dict:
    """
    Extract feature ID statistics from a single raw graph.

    Returns:
        dict with layer -> list of feature IDs
    """
    with open(graph_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    layer_features = defaultdict(list)

    # Extract feature IDs per layer
    for node in data.get('nodes', []):
        layer_str = node['layer']

        # Skip embedding layers (marked as "E")
        if layer_str == 'E' or not layer_str.isdigit():
            continue

        layer = int(layer_str)
        feature = node['feature']
        layer_features[layer].append(feature)

    return dict(layer_features)


def test_mapping_hypothesis(feature_id: int, layer: int, hypothesis: str) -> dict:
    """
    Test different mapping hypotheses.

    Hypotheses:
    - modulo_16k: feature_id % 16384
    - modulo_32k: feature_id % 32768
    - modulo_65k: feature_id % 65536
    - sequential: feature_id - (layer * 16384)
    - identity: feature_id (no mapping)
    """
    results = {}

    if hypothesis == 'modulo_16k':
        results['neuronpedia_id'] = feature_id % 16384
        results['in_range'] = results['neuronpedia_id'] < 16384

    elif hypothesis == 'modulo_32k':
        results['neuronpedia_id'] = feature_id % 32768
        results['in_range'] = results['neuronpedia_id'] < 16384

    elif hypothesis == 'modulo_65k':
        results['neuronpedia_id'] = feature_id % 65536
        results['in_range'] = results['neuronpedia_id'] < 16384

    elif hypothesis == 'sequential':
        results['neuronpedia_id'] = feature_id - (layer * 16384)
        results['in_range'] = 0 <= results['neuronpedia_id'] < 16384

    elif hypothesis == 'identity':
        results['neuronpedia_id'] = feature_id
        results['in_range'] = feature_id < 16384

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Analyze feature ID mapping patterns from Circuit Tracer graphs"
    )
    parser.add_argument(
        '--graph-dir',
        default='../data/prompts',
        help='Directory containing prompt subdirectories with raw graphs'
    )
    parser.add_argument(
        '--max-graphs',
        type=int,
        default=5,
        help='Maximum number of graphs to analyze'
    )

    args = parser.parse_args()

    # Find raw graph files
    graph_dir = Path(args.graph_dir)
    raw_graphs = list(graph_dir.rglob('*_raw_graph.json'))

    print("=" * 70)
    print("FEATURE ID MAPPING ANALYSIS")
    print("=" * 70)
    print()
    print(f"Found {len(raw_graphs)} raw graphs")
    print(f"Analyzing first {min(len(raw_graphs), args.max_graphs)}...")
    print()

    # Analyze each graph
    all_stats = {}

    for i, graph_file in enumerate(raw_graphs[:args.max_graphs], 1):
        print(f"[{i}/{min(len(raw_graphs), args.max_graphs)}] {graph_file.name}")

        layer_features = analyze_raw_graph(graph_file)

        # Calculate statistics per layer
        for layer in sorted(layer_features.keys())[:6]:  # First 6 layers
            features = layer_features[layer]

            if layer not in all_stats:
                all_stats[layer] = {
                    'min': [],
                    'max': [],
                    'count': [],
                    'samples': []
                }

            all_stats[layer]['min'].append(min(features))
            all_stats[layer]['max'].append(max(features))
            all_stats[layer]['count'].append(len(features))
            all_stats[layer]['samples'].extend(features[:5])  # First 5 samples

    print()
    print("=" * 70)
    print("LAYER STATISTICS (First 6 Layers)")
    print("=" * 70)
    print()

    for layer in sorted(all_stats.keys()):
        stats = all_stats[layer]
        print(f"Layer {layer}:")
        print(f"  Feature range: {min(stats['min'])} - {max(stats['max'])}")
        print(f"  Avg features per graph: {sum(stats['count']) / len(stats['count']):.0f}")
        print(f"  Max feature / 16384 = {max(stats['max']) / 16384:.2f} (layers worth)")

        # Sample features
        samples = list(set(stats['samples'][:10]))
        print(f"  Sample features: {samples[:5]}")
        print()

    print("=" * 70)
    print("MAPPING HYPOTHESIS TESTING")
    print("=" * 70)
    print()

    # Test hypotheses on problematic feature IDs
    test_cases = [
        (0, 902, "Known to work in Neuronpedia"),
        (0, 32384, "Beyond 16k range"),
        (0, 680360, "Way beyond 16k"),
        (5, 7993995, "GEMMA bottleneck feature"),
    ]

    hypotheses = ['identity', 'modulo_16k', 'modulo_32k', 'modulo_65k', 'sequential']

    for layer, feature_id, description in test_cases:
        print(f"Feature: L{layer}_F{feature_id} ({description})")
        print(f"  Original ID: {feature_id}")

        for hyp in hypotheses:
            result = test_mapping_hypothesis(feature_id, layer, hyp)
            in_range_str = "OK" if result['in_range'] else "NO"
            print(f"  {hyp:15} -> {result['neuronpedia_id']:8} {in_range_str}")

        print()

    print("=" * 70)
    print("PATTERN ANALYSIS")
    print("=" * 70)
    print()

    # Check if features are clustered or spread
    for layer in sorted(all_stats.keys()):
        stats = all_stats[layer]
        max_feat = max(stats['max'])
        min_feat = min(stats['min'])

        if max_feat < 16384:
            print(f"Layer {layer}: All features in range ✓ (max={max_feat})")
        elif max_feat < 32768:
            print(f"Layer {layer}: Features exceed 16k, possibly 32k transcoders? (max={max_feat})")
        elif max_feat < 65536:
            print(f"Layer {layer}: Features exceed 32k, possibly 65k transcoders? (max={max_feat})")
        else:
            print(f"Layer {layer}: Features VERY large (max={max_feat})")
            # Check modulo hypothesis
            max_mod_16k = max_feat % 16384
            print(f"         max % 16384 = {max_mod_16k}")
            print(f"         max / 16384 = {max_feat / 16384:.1f} (could be global index?)")

    print()
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print()

    # Provide recommendations
    max_across_all = max(max(s['max']) for s in all_stats.values())

    if max_across_all < 16384:
        print("[OK] All features are in valid 16k range (0-16,383)")
        print("[OK] No mapping needed - use feature IDs directly")
    elif max_across_all < 32768:
        print("[WARNING] Features exceed 16k - possible 32k transcoders")
        print(" -> Test if Neuronpedia has 32k transcoder endpoint")
        print(" -> Try URL: .../layer-gemmascope-transcoder-32k/...")
    else:
        print("[WARNING] Features way beyond 16k/32k range")
        print(" -> Likely different numbering scheme")
        print(" -> Options:")
        print("    1. Use modulo_16k mapping (feature_id % 16384)")
        print("    2. Check Circuit Tracer docs for numbering")
        print("    3. Focus on features that ARE in range (Option A)")

    print()


if __name__ == '__main__':
    main()
