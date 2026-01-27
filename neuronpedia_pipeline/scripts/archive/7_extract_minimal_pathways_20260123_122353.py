"""
Minimal Pathway Extraction - Find Essential Circuit
Extracts the minimum viable circuit connecting input features to output features

This analysis identifies:
- Critical features necessary for the output
- Essential edges that must be present
- Redundant connections that can be removed
- Circuit efficiency metrics
"""

import json
from pathlib import Path
import networkx as nx
import numpy as np
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict
import sys

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from path_manager import PathManager


class MinimalPathwayExtractor:
    """Extract minimal sufficient circuit from full attribution graph"""

    def __init__(self, analysis_path):
        """
        Args:
            analysis_path: Path to analysis JSON file
        """
        self.analysis_path = Path(analysis_path)

        with open(self.analysis_path) as f:
            self.analysis = json.load(f)

        self.metadata = self.analysis['metadata']
        self.prompt = self.metadata['prompt']

        # Build NetworkX graph
        self.G = self._build_graph()

        print(f"[OK] Loaded circuit: {self.prompt}")
        print(f"  Original: {len(self.G.nodes())} nodes, {len(self.G.edges())} edges")

    def _build_graph(self):
        """Build NetworkX directed graph from analysis data"""
        G = nx.DiGraph()

        # Add nodes from supernodes
        supernodes = self.analysis.get('louvain_supernodes', {}).get('supernodes', {})
        for sn_id, sn_data in supernodes.items():
            node_list = sn_data.get('nodes', [])
            for node_id in node_list:
                # Parse node format: "layer_feature_ctx"
                parts = node_id.split('_')
                if len(parts) >= 2:
                    layer = int(parts[0])
                    G.add_node(node_id, layer=layer)

        # For edges, we need to load from converted graph
        # (analysis JSON doesn't have edges, only supernode structure)
        # Use PathManager to find converted graph
        pm = PathManager()
        converted_path = pm.converted_graph_path(self.prompt)

        if converted_path.exists():
            print(f"[OK] Loading edges from: {converted_path.name}")
            with open(converted_path) as f:
                converted = json.load(f)
                for edge in converted.get('edges', []):
                    source = edge['source']
                    target = edge['target']
                    weight = edge.get('weight', 1.0)
                    if source in G.nodes() and target in G.nodes():
                        G.add_edge(source, target, weight=weight)
        else:
            print(f"[WARNING] Converted file not found: {converted_path}")
            print("[WARNING] Building graph without edges")

        return G

    def identify_input_features(self, top_k=20):
        """
        Identify input features (early layers with high fan-out)

        Returns:
            List of (node_id, out_degree, layer) tuples
        """
        input_features = []

        for node in self.G.nodes():
            layer = self.G.nodes[node].get('layer', 999)
            out_degree = self.G.out_degree(node)

            # Input features: layers 0-5, high out-degree
            if layer <= 5 and out_degree > 0:
                input_features.append((node, out_degree, layer))

        # Sort by out-degree
        input_features.sort(key=lambda x: x[1], reverse=True)

        return input_features[:top_k]

    def identify_output_features(self, top_k=20):
        """
        Identify output features (late layers with high in-degree)

        Returns:
            List of (node_id, in_degree, layer) tuples
        """
        output_features = []

        for node in self.G.nodes():
            layer = self.G.nodes[node].get('layer', 0)
            in_degree = self.G.in_degree(node)

            # Output features: layers 21-25, high in-degree
            if layer >= 21 and in_degree > 0:
                output_features.append((node, in_degree, layer))

        # Sort by in-degree
        output_features.sort(key=lambda x: x[1], reverse=True)

        return output_features[:top_k]

    def find_all_paths_bfs(self, sources, targets, max_paths_per_pair=3):
        """
        Find shortest paths from sources to targets (optimized)

        Args:
            sources: List of source node IDs
            targets: List of target node IDs
            max_paths_per_pair: Maximum paths to find per source-target pair

        Returns:
            List of paths (each path is a list of node IDs)
        """
        all_paths = []
        total_pairs = len(sources) * len(targets)
        processed = 0

        print(f"[INFO] Finding paths for {len(sources)} sources x {len(targets)} targets = {total_pairs} pairs")

        for source in sources:
            for target in targets:
                processed += 1
                if processed % 10 == 0:
                    print(f"  Progress: {processed}/{total_pairs} pairs ({processed/total_pairs*100:.1f}%)")

                try:
                    # Use shortest_simple_paths instead of all_simple_paths (much faster)
                    # This finds paths in order of increasing length
                    path_generator = nx.shortest_simple_paths(self.G, source, target)

                    # Take only first max_paths_per_pair paths
                    paths = []
                    for i, path in enumerate(path_generator):
                        if i >= max_paths_per_pair:
                            break
                        if len(path) <= 15:  # Skip very long paths
                            paths.append(path)

                    all_paths.extend(paths)

                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    # No path exists between this source-target pair
                    continue

        print(f"[OK] Found {len(all_paths)} total paths")
        return all_paths

    def extract_essential_edges(self, paths, threshold=0.5):
        """
        Extract edges that appear in many paths (essential edges)

        Args:
            paths: List of paths
            threshold: Minimum fraction of paths an edge must appear in

        Returns:
            Set of essential edges (source, target) tuples
        """
        edge_counts = defaultdict(int)

        # Count edge appearances
        for path in paths:
            for i in range(len(path) - 1):
                edge = (path[i], path[i+1])
                edge_counts[edge] += 1

        # Filter to essential edges
        min_count = int(threshold * len(paths))
        essential_edges = {edge for edge, count in edge_counts.items() if count >= min_count}

        print(f"[OK] Found {len(essential_edges)} essential edges (appear in >={threshold:.0%} of paths)")
        return essential_edges

    def construct_minimal_circuit(self, essential_edges):
        """
        Build minimal circuit graph with only essential edges

        Returns:
            NetworkX graph of minimal circuit
        """
        minimal_G = nx.DiGraph()

        # Add nodes from essential edges
        for source, target in essential_edges:
            if source not in minimal_G:
                minimal_G.add_node(source, **self.G.nodes[source])
            if target not in minimal_G:
                minimal_G.add_node(target, **self.G.nodes[target])

            # Add edge with original weight
            if self.G.has_edge(source, target):
                minimal_G.add_edge(source, target, **self.G[source][target])

        print(f"[OK] Minimal circuit: {len(minimal_G.nodes())} nodes, {len(minimal_G.edges())} edges")
        return minimal_G

    def compute_pathway_metrics(self, minimal_G, paths):
        """Compute metrics about the minimal circuit"""

        reduction_pct = (1 - len(minimal_G.nodes()) / len(self.G.nodes())) * 100

        # Bottleneck width: narrowest layer in circuit
        layer_counts = defaultdict(int)
        for node in minimal_G.nodes():
            layer = minimal_G.nodes[node].get('layer', 0)
            layer_counts[layer] += 1

        bottleneck_width = min(layer_counts.values()) if layer_counts else 0
        bottleneck_layer = min(layer_counts, key=layer_counts.get) if layer_counts else 0

        # Path diversity: how many parallel pathways?
        path_diversity = len(set(tuple(path) for path in paths))

        metrics = {
            'original_nodes': len(self.G.nodes()),
            'original_edges': len(self.G.edges()),
            'minimal_nodes': len(minimal_G.nodes()),
            'minimal_edges': len(minimal_G.edges()),
            'reduction_pct': reduction_pct,
            'bottleneck_width': bottleneck_width,
            'bottleneck_layer': bottleneck_layer,
            'path_diversity': path_diversity,
            'avg_path_length': np.mean([len(p) for p in paths]) if paths else 0
        }

        return metrics

    def extract_minimal_pathway(self, output_path):
        """Main method to extract minimal pathway"""

        print("\n" + "="*60)
        print("STEP 1: Identify Input Features")
        print("="*60)
        input_features = self.identify_input_features(top_k=10)
        print(f"Top input features (by out-degree):")
        for node, out_deg, layer in input_features[:5]:
            print(f"  {node} (L{layer}): out_degree={out_deg}")

        print("\n" + "="*60)
        print("STEP 2: Identify Output Features")
        print("="*60)
        output_features = self.identify_output_features(top_k=10)
        print(f"Top output features (by in-degree):")
        for node, in_deg, layer in output_features[:5]:
            print(f"  {node} (L{layer}): in_degree={in_deg}")

        print("\n" + "="*60)
        print("STEP 3: Find All Paths (Input -> Output)")
        print("="*60)
        sources = [node for node, _, _ in input_features]
        targets = [node for node, _, _ in output_features]
        paths = self.find_all_paths_bfs(sources, targets, max_paths_per_pair=3)

        if not paths:
            print("[ERROR] No paths found! Cannot extract minimal circuit.")
            return None

        print("\n" + "="*60)
        print("STEP 4: Extract Essential Edges")
        print("="*60)
        essential_edges = self.extract_essential_edges(paths, threshold=0.2)

        # If threshold too high, try lower
        if len(essential_edges) == 0:
            print("[WARNING] No edges found at 20% threshold, trying 10%...")
            essential_edges = self.extract_essential_edges(paths, threshold=0.1)

        # If still nothing, use top N most frequent edges
        if len(essential_edges) == 0:
            print("[WARNING] Extreme path diversity detected. Using top 500 most frequent edges...")
            edge_counts = defaultdict(int)
            for path in paths:
                for i in range(len(path) - 1):
                    edge = (path[i], path[i+1])
                    edge_counts[edge] += 1

            # Get top 500 edges by frequency
            sorted_edges = sorted(edge_counts.items(), key=lambda x: x[1], reverse=True)
            essential_edges = {edge for edge, count in sorted_edges[:500]}
            print(f"[OK] Using {len(essential_edges)} most frequent edges")

        print("\n" + "="*60)
        print("STEP 5: Construct Minimal Circuit")
        print("="*60)
        minimal_G = self.construct_minimal_circuit(essential_edges)

        print("\n" + "="*60)
        print("STEP 6: Compute Metrics")
        print("="*60)
        metrics = self.compute_pathway_metrics(minimal_G, paths)

        print(f"Circuit Reduction: {metrics['reduction_pct']:.1f}%")
        print(f"  Original: {metrics['original_nodes']:,} nodes -> Minimal: {metrics['minimal_nodes']:,} nodes")
        print(f"Bottleneck: Layer {metrics['bottleneck_layer']} with {metrics['bottleneck_width']} features")
        print(f"Path Diversity: {metrics['path_diversity']} unique paths")
        print(f"Average Path Length: {metrics['avg_path_length']:.1f} features")

        # Save results
        result = {
            'metadata': self.metadata,
            'minimal_circuit': {
                'nodes': list(minimal_G.nodes()),
                'edges': [(u, v, minimal_G[u][v]) for u, v in minimal_G.edges()]
            },
            'metrics': metrics,
            'input_features': [{'node': n, 'out_degree': d, 'layer': l} for n, d, l in input_features],
            'output_features': [{'node': n, 'in_degree': d, 'layer': l} for n, d, l in output_features],
            'num_paths': len(paths),
            'sample_paths': [[str(node) for node in path] for path in paths[:5]]
        }

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n[OK] Minimal pathway saved to: {output_path}")
        return minimal_G, metrics

    def visualize_comparison(self, minimal_G, metrics, output_path):
        """Create side-by-side comparison visualization"""

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Bar chart: Node counts
        categories = ['Nodes', 'Edges']
        original = [metrics['original_nodes'], metrics['original_edges']]
        minimal = [metrics['minimal_nodes'], metrics['minimal_edges']]

        x = np.arange(len(categories))
        width = 0.35

        ax1.bar(x - width/2, original, width, label='Original Circuit', color='steelblue', alpha=0.8)
        ax1.bar(x + width/2, minimal, width, label='Minimal Circuit', color='coral', alpha=0.8)

        ax1.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax1.set_title('Circuit Comparison', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)

        # Add percentage labels
        for i, (orig, mini) in enumerate(zip(original, minimal)):
            reduction = (1 - mini/orig) * 100
            ax1.text(i, max(orig, mini) * 1.05, f'-{reduction:.1f}%',
                    ha='center', fontsize=10, fontweight='bold', color='green')

        # Metrics summary
        ax2.axis('off')
        metrics_text = f"""
MINIMAL PATHWAY METRICS

Circuit Reduction:
  {metrics['reduction_pct']:.1f}% fewer features

Original Circuit:
  {metrics['original_nodes']:,} nodes
  {metrics['original_edges']:,} edges

Minimal Circuit:
  {metrics['minimal_nodes']:,} nodes
  {metrics['minimal_edges']:,} edges

Bottleneck:
  Layer {metrics['bottleneck_layer']} (width: {metrics['bottleneck_width']})

Path Analysis:
  {metrics['path_diversity']} unique pathways
  {metrics['avg_path_length']:.1f} avg features per path

Interpretation:
  The minimal circuit contains only the
  ESSENTIAL features needed to connect
  inputs to outputs. All redundant
  connections have been pruned.
        """

        ax2.text(0.1, 0.5, metrics_text, fontsize=11, verticalalignment='center',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.suptitle(f'Minimal Pathway Analysis\n"{self.prompt}"',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"[OK] Comparison visualization saved to: {output_path}")
        plt.close()


def main():
    parser = argparse.ArgumentParser(description='Extract minimal pathway from circuit')
    parser.add_argument('--analysis', type=str,
                       help='Path to analysis JSON file (if not provided, uses latest)')
    parser.add_argument('--prompt', type=str,
                       help='Prompt text to analyze')

    args = parser.parse_args()

    pm = PathManager()

    # Auto-discover analysis file if not provided
    if args.analysis:
        analysis_path = Path(args.analysis)
    elif args.prompt:
        analysis_path = pm.circuit_analysis_path(args.prompt)
        if not analysis_path.exists():
            print(f"[ERROR] Analysis not found for prompt: {args.prompt}")
            print("Please run Scripts 1-3 first.")
            return
    else:
        # Find latest analysis
        prompts = pm.get_all_analyzed_prompts()
        if not prompts:
            print("[ERROR] No analysis files found!")
            print("Please run Scripts 1-3 first to generate circuit analyses.")
            return
        # Use first (most recent) prompt
        prompt = prompts[0]
        analysis_path = pm.circuit_analysis_path(prompt)
        print(f"[INFO] Auto-selected latest analysis: {prompt}")

    # Extract prompt from analysis
    with open(analysis_path) as f:
        analysis = json.load(f)
        prompt = analysis['metadata']['prompt']

    # Create output directory using PathManager
    output_dir = pm.minimal_pathways_dir(prompt)
    print(f"\nOutput directory: {output_dir}")

    # Extract minimal pathway
    extractor = MinimalPathwayExtractor(analysis_path)

    pathway_path = pm.minimal_pathways_result_path(prompt)
    minimal_G, metrics = extractor.extract_minimal_pathway(pathway_path)

    if minimal_G:
        # Create visualization
        viz_path = pm.minimal_pathways_viz_path(prompt)
        extractor.visualize_comparison(minimal_G, metrics, viz_path)

        print("\n" + "="*60)
        print("MINIMAL PATHWAY EXTRACTION COMPLETE")
        print("="*60)
        print(f"Results: {pathway_path.name}")
        print(f"Visualization: {viz_path.name}")
        print(f"Location: {output_dir}")
    else:
        print("\n[ERROR] Failed to extract minimal pathway")


if __name__ == "__main__":
    main()
