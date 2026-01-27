"""
Cross-Prompt Supernode Reuse Analysis
Identifies which supernodes and features are reused across related prompts

This is the foundation for:
- Understanding which cognitive modules are shared
- Identifying prompt-invariant vs prompt-specific processing
- Building steering vectors from stable features
"""

import json
from pathlib import Path
import numpy as np
import argparse
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns


class CrossPromptAnalyzer:
    """Analyze feature and supernode reuse across multiple prompts"""

    def __init__(self, analysis_files):
        """
        Args:
            analysis_files: List of paths to analysis JSON files
        """
        self.analyses = []
        self.prompts = []

        for file_path in analysis_files:
            with open(file_path) as f:
                data = json.load(f)
                self.analyses.append(data)
                self.prompts.append(data['metadata']['prompt'])

        print(f"[OK] Loaded {len(self.analyses)} circuit analyses")
        for i, prompt in enumerate(self.prompts):
            print(f"  {i+1}. {prompt}")

    def extract_active_features(self, analysis_idx):
        """Extract all active features from an analysis"""
        analysis = self.analyses[analysis_idx]
        features = set()

        # Extract from louvain_supernodes (which contains all nodes)
        supernodes = analysis.get('louvain_supernodes', {}).get('supernodes', {})
        for sn_id, sn_data in supernodes.items():
            # Each supernode is a dict with 'nodes' key containing list of node IDs
            if isinstance(sn_data, dict):
                node_list = sn_data.get('nodes', [])
                for node_id in node_list:
                    features.add(node_id)

        return features

    def extract_supernode_features(self, analysis_idx):
        """Extract features grouped by supernode"""
        analysis = self.analyses[analysis_idx]
        supernode_features = {}

        supernodes = analysis.get('louvain_supernodes', {}).get('supernodes', {})
        for sn_id, sn_data in supernodes.items():
            # Each supernode is a dict with 'nodes' key containing list of node IDs
            if isinstance(sn_data, dict):
                node_list = sn_data.get('nodes', [])
                supernode_features[int(sn_id)] = set(node_list)

        return supernode_features

    def extract_supernode_themes(self, analysis_idx):
        """Extract supernode themes"""
        analysis = self.analyses[analysis_idx]
        themes = {}

        layer_groups = analysis.get('layer_groups', {})
        # Note: themes are stored in visualization, not analysis
        # We'll compute them on the fly if needed

        return themes

    def compute_feature_overlap(self):
        """Compute pairwise feature overlap between prompts"""
        n = len(self.analyses)
        overlap_matrix = np.zeros((n, n))

        feature_sets = [self.extract_active_features(i) for i in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    overlap_matrix[i, j] = 1.0
                else:
                    intersection = len(feature_sets[i] & feature_sets[j])
                    union = len(feature_sets[i] | feature_sets[j])
                    overlap_matrix[i, j] = intersection / union if union > 0 else 0

        return overlap_matrix, feature_sets

    def compute_supernode_similarity(self):
        """
        Compute supernode similarity across prompts
        Two supernodes are similar if they contain overlapping features
        """
        supernode_sets = [self.extract_supernode_features(i) for i in range(len(self.analyses))]

        # For each pair of prompts, find matching supernodes
        matches = []

        for i in range(len(self.analyses)):
            for j in range(i+1, len(self.analyses)):
                prompt_i = self.prompts[i]
                prompt_j = self.prompts[j]

                # Compare each supernode in i with each in j
                for sn_i, features_i in supernode_sets[i].items():
                    for sn_j, features_j in supernode_sets[j].items():
                        overlap = len(features_i & features_j)
                        union = len(features_i | features_j)
                        jaccard = overlap / union if union > 0 else 0

                        if jaccard > 0.3:  # Significant overlap threshold
                            matches.append({
                                'prompt_i': i,
                                'prompt_j': j,
                                'supernode_i': sn_i,
                                'supernode_j': sn_j,
                                'jaccard': jaccard,
                                'overlap_features': overlap,
                                'total_features': union
                            })

        return matches

    def identify_shared_features(self, threshold=0.5):
        """
        Identify features that appear in multiple prompts

        Args:
            threshold: Minimum fraction of prompts a feature must appear in

        Returns:
            dict: {feature_id: [prompt_indices where it appears]}
        """
        feature_appearances = defaultdict(list)

        for i in range(len(self.analyses)):
            features = self.extract_active_features(i)
            for feature in features:
                feature_appearances[feature].append(i)

        # Filter to features appearing in at least threshold * n_prompts
        min_appearances = int(threshold * len(self.analyses))
        shared_features = {
            feat: prompts
            for feat, prompts in feature_appearances.items()
            if len(prompts) >= min_appearances
        }

        return shared_features

    def analyze_layer_distribution(self):
        """Compare layer usage across prompts"""
        layer_stats = []

        for i, analysis in enumerate(self.analyses):
            layer_groups = analysis['layer_groups']
            stats = {
                'prompt': self.prompts[i],
                'input_features': layer_groups['input']['num_nodes'],
                'early_features': layer_groups['early_proc']['num_nodes'],
                'middle_features': layer_groups['middle_proc']['num_nodes'],
                'late_features': layer_groups['late_proc']['num_nodes'],
                'output_features': layer_groups['output']['num_nodes'],
                'middle_activation': layer_groups['middle_proc']['max_activation'],
                'total_features': sum(lg['num_nodes'] for lg in layer_groups.values())
            }
            layer_stats.append(stats)

        return layer_stats

    def generate_report(self, output_path):
        """Generate comprehensive cross-prompt analysis report"""

        report = []
        report.append("=" * 80)
        report.append("CROSS-PROMPT CIRCUIT ANALYSIS")
        report.append("=" * 80)
        report.append("")
        report.append(f"Analyzed {len(self.analyses)} prompts:")
        for i, prompt in enumerate(self.prompts, 1):
            report.append(f"  {i}. {prompt}")
        report.append("")

        # Feature overlap
        report.append("=" * 80)
        report.append("FEATURE OVERLAP ANALYSIS")
        report.append("=" * 80)
        overlap_matrix, feature_sets = self.compute_feature_overlap()

        for i in range(len(self.analyses)):
            report.append(f"\nPrompt {i+1}: {len(feature_sets[i])} features")

        report.append("\nPairwise Jaccard Similarity:")
        for i in range(len(self.analyses)):
            for j in range(i+1, len(self.analyses)):
                similarity = overlap_matrix[i, j]
                report.append(f"  Prompt {i+1} ↔ Prompt {j+1}: {similarity:.2%}")

        # Shared features
        report.append("")
        report.append("=" * 80)
        report.append("SHARED FEATURES (appearing in ≥50% of prompts)")
        report.append("=" * 80)
        shared = self.identify_shared_features(threshold=0.5)
        report.append(f"Found {len(shared)} shared features")
        report.append("")

        # Show top shared features
        sorted_shared = sorted(shared.items(), key=lambda x: len(x[1]), reverse=True)
        for feat, prompt_indices in sorted_shared[:20]:
            report.append(f"  {feat}: appears in {len(prompt_indices)}/{len(self.analyses)} prompts")

        # Supernode similarity
        report.append("")
        report.append("=" * 80)
        report.append("SUPERNODE REUSE (Jaccard > 0.3)")
        report.append("=" * 80)
        matches = self.compute_supernode_similarity()
        report.append(f"Found {len(matches)} supernode matches across prompts")
        report.append("")

        for match in sorted(matches, key=lambda x: x['jaccard'], reverse=True)[:15]:
            i = match['prompt_i']
            j = match['prompt_j']
            report.append(f"Prompt {i+1} SN{match['supernode_i']} ↔ Prompt {j+1} SN{match['supernode_j']}")
            report.append(f"  Jaccard: {match['jaccard']:.2%}, {match['overlap_features']} shared features")

        # Consensus supernodes
        report.append("")
        report.append("=" * 80)
        report.append("CONSENSUS SUPERNODES (appearing in ≥50% of prompts)")
        report.append("=" * 80)
        consensus = self.identify_consensus_supernodes(matches, threshold=0.5)
        report.append(f"Found {len(consensus)} consensus supernode clusters")
        report.append("")

        if consensus:
            report.append("These are prompt-invariant cognitive modules:")
            for idx, cluster in enumerate(consensus, 1):
                report.append(f"\n  Consensus Cluster {idx}:")
                report.append(f"    Coverage: {cluster['coverage']:.0%} ({cluster['num_prompts']}/{len(self.analyses)} prompts)")
                report.append(f"    Members: {len(cluster['supernodes'])} supernodes")
                # Show which supernodes from each prompt
                for prompt_idx, sn_idx in cluster['supernodes'][:5]:  # Show first 5
                    report.append(f"      - Prompt {prompt_idx+1} SN{sn_idx}")
                if len(cluster['supernodes']) > 5:
                    report.append(f"      ... and {len(cluster['supernodes'])-5} more")
        else:
            report.append("No consensus supernodes found.")
            report.append("Try lowering the threshold or collecting more related prompts.")

        # Layer distribution comparison
        report.append("")
        report.append("=" * 80)
        report.append("LAYER USAGE COMPARISON")
        report.append("=" * 80)
        layer_stats = self.analyze_layer_distribution()

        report.append("\nMiddle Layer Efficiency (fewer features = more efficient):")
        for stats in sorted(layer_stats, key=lambda x: x['middle_features']):
            prompt_short = stats['prompt'][:50] + "..." if len(stats['prompt']) > 50 else stats['prompt']
            report.append(f"  {stats['middle_features']:4d} features @ {stats['middle_activation']:6.1f} peak: {prompt_short}")

        report.append("\nTotal Circuit Size:")
        for stats in sorted(layer_stats, key=lambda x: x['total_features']):
            prompt_short = stats['prompt'][:50] + "..." if len(stats['prompt']) > 50 else stats['prompt']
            report.append(f"  {stats['total_features']:5d} features: {prompt_short}")

        # Key findings
        report.append("")
        report.append("=" * 80)
        report.append("KEY FINDINGS")
        report.append("=" * 80)

        avg_overlap = np.mean([overlap_matrix[i, j] for i in range(len(self.analyses))
                                for j in range(i+1, len(self.analyses))])
        report.append(f"\n1. Average feature overlap: {avg_overlap:.2%}")

        report.append(f"\n2. Core shared features: {len(shared)} features appear in ≥50% of prompts")
        report.append("   These represent prompt-invariant processing modules")

        report.append(f"\n3. Supernode reuse: {len(matches)} cross-prompt supernode matches found")
        report.append("   Suggests functional modules are reused for similar reasoning")

        min_features = min(s['total_features'] for s in layer_stats)
        max_features = max(s['total_features'] for s in layer_stats)
        report.append(f"\n4. Circuit complexity range: {min_features:,} to {max_features:,} features")
        report.append(f"   {max_features/min_features:.1f}x difference in circuit size")

        report.append("")
        report.append("=" * 80)

        # Write report
        output_text = "\n".join(report)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)

        print(f"\n[OK] Cross-prompt analysis saved to: {output_path}")
        return output_text

    def identify_consensus_supernodes(self, matches, threshold=0.5):
        """
        Identify consensus supernodes that appear across multiple prompts

        Args:
            matches: List of supernode matches from compute_supernode_similarity()
            threshold: Minimum fraction of prompts a supernode must appear in

        Returns:
            List of consensus supernode clusters
        """
        # Build graph of supernode relationships
        from collections import defaultdict
        supernode_graph = defaultdict(set)

        for match in matches:
            key_i = (match['prompt_i'], match['supernode_i'])
            key_j = (match['prompt_j'], match['supernode_j'])
            supernode_graph[key_i].add(key_j)
            supernode_graph[key_j].add(key_i)

        # Find connected components (groups of matching supernodes)
        visited = set()
        consensus_clusters = []

        def dfs(node, cluster):
            if node in visited:
                return
            visited.add(node)
            cluster.append(node)
            for neighbor in supernode_graph[node]:
                dfs(neighbor, cluster)

        for node in supernode_graph:
            if node not in visited:
                cluster = []
                dfs(node, cluster)
                if len(cluster) > 1:  # Only keep clusters with multiple supernodes
                    # Count unique prompts in cluster
                    unique_prompts = len(set(prompt_idx for prompt_idx, sn_idx in cluster))
                    if unique_prompts >= threshold * len(self.analyses):
                        consensus_clusters.append({
                            'supernodes': cluster,
                            'num_prompts': unique_prompts,
                            'coverage': unique_prompts / len(self.analyses)
                        })

        # Sort by coverage
        consensus_clusters.sort(key=lambda x: x['coverage'], reverse=True)
        return consensus_clusters

    def visualize_overlap(self, output_path):
        """Create heatmap of feature overlap"""
        overlap_matrix, _ = self.compute_feature_overlap()

        fig, ax = plt.subplots(figsize=(10, 8))

        # Short labels
        labels = [f"P{i+1}" for i in range(len(self.prompts))]

        sns.heatmap(overlap_matrix, annot=True, fmt='.2f',
                   xticklabels=labels, yticklabels=labels,
                   cmap='RdYlGn', vmin=0, vmax=1, ax=ax,
                   cbar_kws={'label': 'Jaccard Similarity'})

        ax.set_title('Feature Overlap Across Prompts', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Prompt', fontsize=12)
        ax.set_ylabel('Prompt', fontsize=12)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"[OK] Overlap heatmap saved to: {output_path}")
        plt.close()

    def visualize_supernode_reuse_network(self, output_path):
        """Create network diagram showing supernode reuse across prompts"""
        import networkx as nx

        matches = self.compute_supernode_similarity()

        # Build graph
        G = nx.Graph()

        # Add nodes for each supernode
        for i, analysis in enumerate(self.analyses):
            supernodes = analysis.get('louvain_supernodes', {}).get('supernodes', {})
            for sn_id in supernodes.keys():
                node_id = f"P{i+1}_SN{sn_id}"
                G.add_node(node_id, prompt=i, supernode=int(sn_id))

        # Add edges for matches
        for match in matches:
            if match['jaccard'] > 0.4:  # Only strong matches
                node_i = f"P{match['prompt_i']+1}_SN{match['supernode_i']}"
                node_j = f"P{match['prompt_j']+1}_SN{match['supernode_j']}"
                G.add_edge(node_i, node_j, weight=match['jaccard'])

        if len(G.nodes()) == 0 or len(G.edges()) == 0:
            print("[WARNING] No supernode matches found for network visualization")
            return

        # Layout
        fig, ax = plt.subplots(figsize=(14, 10))
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

        # Color nodes by prompt
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.analyses)))
        node_colors = [colors[G.nodes[node]['prompt']] for node in G.nodes()]

        # Draw
        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                              node_size=500, alpha=0.8, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)

        # Draw edges with varying thickness
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        nx.draw_networkx_edges(G, pos, width=[w*3 for w in weights],
                              alpha=0.5, ax=ax)

        ax.set_title('Supernode Reuse Network\n(Nodes = Supernodes, Edges = Similarity > 0.4)',
                    fontsize=14, fontweight='bold', pad=15)
        ax.axis('off')

        # Legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                     markerfacecolor=colors[i], markersize=10,
                                     label=f"P{i+1}: {self.prompts[i][:30]}...")
                          for i in range(len(self.analyses))]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"[OK] Reuse network saved to: {output_path}")
        plt.close()


def main():
    parser = argparse.ArgumentParser(description='Cross-prompt circuit analysis')
    parser.add_argument('--analyses', nargs='+', required=True,
                       help='Paths to analysis JSON files')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='Output directory for reports and visualizations')

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run analysis
    analyzer = CrossPromptAnalyzer(args.analyses)

    # Generate report
    report_path = output_dir / "cross_prompt_analysis.txt"
    analyzer.generate_report(report_path)

    # Generate visualizations
    heatmap_path = output_dir / "feature_overlap_heatmap.png"
    analyzer.visualize_overlap(heatmap_path)

    network_path = output_dir / "supernode_reuse_network.png"
    analyzer.visualize_supernode_reuse_network(network_path)

    # Save consensus supernodes as JSON
    matches = analyzer.compute_supernode_similarity()
    consensus = analyzer.identify_consensus_supernodes(matches, threshold=0.5)
    consensus_path = output_dir / "consensus_supernodes.json"
    with open(consensus_path, 'w') as f:
        json.dump(consensus, f, indent=2, default=str)
    print(f"[OK] Consensus supernodes saved to: {consensus_path}")

    print("\n" + "="*60)
    print("CROSS-PROMPT ANALYSIS COMPLETE")
    print("="*60)
    print(f"Report: {report_path}")
    print(f"Heatmap: {heatmap_path}")
    print(f"Network: {network_path}")
    print(f"Consensus: {consensus_path}")


if __name__ == "__main__":
    main()
