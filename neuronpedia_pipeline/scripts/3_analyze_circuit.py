"""
Circuit Analysis with Supernode Detection
Analyzes converted Circuit Tracer graphs using Louvain community detection
Supports interactive selection or command-line file specification
"""

import json
import networkx as nx
from pathlib import Path
import sys
import argparse

# Import from same directory
sys.path.insert(0, str(Path(__file__).parent))

from supernode_detector import SupernodeDetector

def find_available_converted_graphs():
    """Find all converted graphs in the data directory"""
    graphs_dir = Path(__file__).parent.parent / "data" / "graphs"

    if not graphs_dir.exists():
        return []

    # Find all *_converted.json files
    converted_graphs = list(graphs_dir.glob("*_converted.json"))

    # Sort by modification time (newest first)
    converted_graphs.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    return converted_graphs

def display_available_graphs(graphs):
    """Display numbered list of available converted graphs"""
    print("\n" + "=" * 60)
    print("AVAILABLE CONVERTED GRAPHS")
    print("=" * 60)

    if not graphs:
        print("No converted graphs found!")
        print("Please run '/circuit-tracer-fetch' and '/circuit-tracer-convert' first.")
        return

    for i, graph_path in enumerate(graphs, 1):
        # Get file size
        size_mb = graph_path.stat().st_size / (1024 * 1024)
        print(f"{i}. {graph_path.name} ({size_mb:.2f} MB)")

    print("=" * 60)

def get_user_selection(graphs):
    """Get user's graph selection interactively"""
    print("\nSelect graph to analyze:")
    print("-" * 60)

    while True:
        try:
            choice = input("Select graph (enter number, or press Enter for latest): ").strip()

            if choice == "":
                # Use latest (first in list)
                return graphs[0]

            idx = int(choice) - 1
            if 0 <= idx < len(graphs):
                return graphs[idx]
            else:
                print(f"Please enter a number between 1 and {len(graphs)}")
        except ValueError:
            print("Please enter a valid number or press Enter for latest")

# Parse arguments
parser = argparse.ArgumentParser(
    description='Analyze Circuit Tracer graph with supernode detection',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''
Examples:
  python 3_analyze_circuit.py  (interactive mode)
  python 3_analyze_circuit.py --file path/to/graph_converted.json
    '''
)
parser.add_argument(
    '--file',
    type=str,
    help='Path to specific converted graph file (if not provided, will use interactive mode)'
)

args = parser.parse_args()

print("=" * 60)
print("CIRCUIT TRACER - CIRCUIT ANALYSIS")
print("=" * 60)

# Determine input file
if args.file:
    # Command-line mode
    graph_file = Path(args.file)
    if not graph_file.exists():
        print(f"\n[ERROR] File not found: {graph_file}")
        sys.exit(1)
    print(f"\nUsing file from command-line: {graph_file.name}")
else:
    # Interactive mode
    print("\nEntering interactive mode...")

    # Find available graphs
    available_graphs = find_available_converted_graphs()

    if not available_graphs:
        print("\n[ERROR] No converted graphs found!")
        print("Please run '/circuit-tracer-fetch' and '/circuit-tracer-convert' first.")
        sys.exit(1)

    # Display available graphs
    display_available_graphs(available_graphs)

    # Get user selection
    graph_file = get_user_selection(available_graphs)
    print(f"\nSelected: {graph_file.name}")

# Load converted real graph
print("\n" + "="*60)
print("STEP 1: Load Converted Graph")
print("="*60)

with open(graph_file) as f:
    graph_data = json.load(f)

metadata = graph_data['metadata']
print(f"Prompt: \"{metadata['prompt']}\"")
print(f"Model: {metadata['model']}")
print(f"Slug: {metadata['slug']}")
print(f"Original nodes: {metadata['original_nodes']}")
print(f"Original links: {metadata['original_links']}")
print(f"Converted nodes: {metadata['converted_nodes']}")
print(f"Converted edges: {metadata['converted_edges']}")

# Convert to NetworkX
print("\n" + "="*60)
print("STEP 2: Convert to NetworkX Graph")
print("="*60)

G = nx.DiGraph()

# Add nodes
for node in graph_data['nodes']:
    G.add_node(
        node['id'],
        feature_id=node['feature_id'],
        layer=node['layer'],
        activation=node['activation'],
        influence=node.get('influence', 0.0),
        label=node['label']
    )

# Add edges
for edge in graph_data['edges']:
    G.add_edge(
        edge['source'],
        edge['target'],
        weight=edge['weight']
    )

print(f"NetworkX graph created:")
print(f"  Nodes: {G.number_of_nodes()}")
print(f"  Edges: {G.number_of_edges()}")
print(f"  Directed: {G.is_directed()}")
print(f"  Density: {nx.density(G):.6f}")

# Get layer distribution
layer_counts = {}
for node in G.nodes():
    layer = G.nodes[node]['layer']
    layer_counts[layer] = layer_counts.get(layer, 0) + 1

print(f"\n  Layers present: {sorted(layer_counts.keys())}")
print(f"  Layer range: {min(layer_counts.keys())} to {max(layer_counts.keys())}")

# ============================================================================
# HELPER FUNCTIONS FOR HYBRID ANALYSIS
# ============================================================================

def auto_tune_louvain_params(G, target_range=(3, 10)):
    """
    Auto-tune Louvain resolution based on graph density.

    Dense graphs need higher resolution to split into multiple communities.
    Returns optimal parameters for one-size-fits-all approach.

    UPDATED: More relaxed max_size constraints to handle dense graphs.
    """
    n_nodes = G.number_of_nodes()
    density = nx.density(G)

    print(f"\nAuto-tuning Louvain parameters...")
    print(f"  Graph density: {density:.6f}")
    print(f"  Total nodes: {n_nodes}")

    # Density-based parameter selection with RELAXED max_size
    if density > 0.02:  # Very dense (>2%)
        resolution = 2.0  # Higher resolution for more splits
        min_size = max(5, n_nodes // 200)  # Lower min threshold
        max_size = max(200, n_nodes // 5)  # Much higher max (was //30)
        print(f"  Strategy: VERY DENSE - using very high resolution")
    elif density > 0.01:  # Dense (1-2%)
        resolution = 1.5
        min_size = max(3, n_nodes // 250)  # Lower min threshold
        max_size = max(150, n_nodes // 8)  # Higher max (was //50)
        print(f"  Strategy: DENSE - using high resolution")
    else:  # Sparse (<1%)
        resolution = 1.0
        min_size = 3
        max_size = max(100, n_nodes // 10)  # Higher max (was //100)
        print(f"  Strategy: SPARSE - using medium resolution")

    print(f"  Parameters: resolution={resolution}, min_size={min_size}, max_size={max_size}")

    return {
        'resolution': resolution,
        'min_size': min_size,
        'max_size': max_size
    }

def analyze_by_layer_groups(G):
    """
    Analyze graph using theory-driven layer groups.

    Layer groups based on transformer computational stages:
    - Input (0-5): Token embedding, early attention
    - Early Processing (6-10): Syntax, basic semantics
    - Middle Processing (11-15): Concept formation
    - Late Processing (16-20): Knowledge retrieval, reasoning
    - Output (21-25): Answer generation

    Returns dict with statistics for each group.
    """
    layer_groups_def = {
        'input': (0, 5),
        'early_proc': (6, 10),
        'middle_proc': (11, 15),
        'late_proc': (16, 20),
        'output': (21, 25)
    }

    layer_groups = {}

    for group_name, (min_layer, max_layer) in layer_groups_def.items():
        # Get nodes in this layer range
        group_nodes = [
            n for n in G.nodes()
            if min_layer <= G.nodes[n]['layer'] <= max_layer
        ]

        if len(group_nodes) == 0:
            continue

        # Calculate statistics
        activations = [G.nodes[n]['activation'] for n in group_nodes]
        influences = [G.nodes[n].get('influence', 0.0) for n in group_nodes]

        # Get top features
        top_features = sorted(
            group_nodes,
            key=lambda n: G.nodes[n]['activation'],
            reverse=True
        )[:5]

        top_features_list = [
            {
                'node_id': n,
                'label': G.nodes[n]['label'],
                'activation': G.nodes[n]['activation'],
                'influence': G.nodes[n].get('influence', 0.0)
            }
            for n in top_features
        ]

        # Count edge flows
        internal_edges = 0
        incoming_edges = 0
        outgoing_edges = 0

        for u, v in G.edges():
            u_in_group = u in group_nodes
            v_in_group = v in group_nodes

            if u_in_group and v_in_group:
                internal_edges += 1
            elif v_in_group and not u_in_group:
                incoming_edges += 1
            elif u_in_group and not v_in_group:
                outgoing_edges += 1

        layer_groups[group_name] = {
            'layer_range': [min_layer, max_layer],
            'nodes': group_nodes,
            'num_nodes': len(group_nodes),
            'mean_activation': sum(activations) / len(activations),
            'max_activation': max(activations),
            'mean_influence': sum(influences) / len(influences),
            'max_influence': max(influences),
            'top_features': top_features_list,
            'internal_edges': internal_edges,
            'incoming_edges': incoming_edges,
            'outgoing_edges': outgoing_edges
        }

    return layer_groups

def identify_flow_nodes(G, layer_groups):
    """
    Identify input/output/bottleneck nodes for steering interventions.

    - Input nodes: Early layers (0-5) with high out-degree
    - Output nodes: Late layers (21-25) with high activation
    - Bottleneck nodes: High betweenness centrality across all layers

    Returns dict with lists of candidate nodes for steering.
    """
    # Calculate betweenness centrality for all nodes
    print("\n  Calculating betweenness centrality for bottleneck detection...")
    node_betweenness = nx.betweenness_centrality(G, k=min(200, G.number_of_nodes()))

    # Input nodes: Early layers with high out-degree
    input_candidates = []
    if 'input' in layer_groups:
        input_nodes = layer_groups['input']['nodes']
        for node in input_nodes:
            out_deg = G.out_degree(node)
            if out_deg > 5:  # Significant output connections
                input_candidates.append({
                    'node_id': node,
                    'label': G.nodes[node]['label'],
                    'layer': G.nodes[node]['layer'],
                    'activation': G.nodes[node]['activation'],
                    'out_degree': out_deg,
                    'betweenness': node_betweenness.get(node, 0.0)
                })

    # Sort by out-degree
    input_candidates.sort(key=lambda x: x['out_degree'], reverse=True)

    # Output nodes: Late layers with high activation
    output_candidates = []
    if 'output' in layer_groups:
        output_nodes = layer_groups['output']['nodes']
        for node in output_nodes:
            output_candidates.append({
                'node_id': node,
                'label': G.nodes[node]['label'],
                'layer': G.nodes[node]['layer'],
                'activation': G.nodes[node]['activation'],
                'influence': G.nodes[node].get('influence', 0.0),
                'in_degree': G.in_degree(node),
                'betweenness': node_betweenness.get(node, 0.0)
            })
    elif 'late_proc' in layer_groups:
        # Fallback to late processing if no output layer
        late_nodes = layer_groups['late_proc']['nodes']
        for node in late_nodes:
            output_candidates.append({
                'node_id': node,
                'label': G.nodes[node]['label'],
                'layer': G.nodes[node]['layer'],
                'activation': G.nodes[node]['activation'],
                'influence': G.nodes[node].get('influence', 0.0),
                'in_degree': G.in_degree(node),
                'betweenness': node_betweenness.get(node, 0.0)
            })

    # Sort by activation
    output_candidates.sort(key=lambda x: x['activation'], reverse=True)

    # Bottleneck nodes: High betweenness across all layers
    bottleneck_candidates = []
    for node in G.nodes():
        betweenness = node_betweenness.get(node, 0.0)
        if betweenness > 0.0001:  # Threshold for significance
            bottleneck_candidates.append({
                'node_id': node,
                'label': G.nodes[node]['label'],
                'layer': G.nodes[node]['layer'],
                'activation': G.nodes[node]['activation'],
                'betweenness': betweenness,
                'in_degree': G.in_degree(node),
                'out_degree': G.out_degree(node)
            })

    # Sort by betweenness
    bottleneck_candidates.sort(key=lambda x: x['betweenness'], reverse=True)

    return {
        'input_nodes': input_candidates[:10],  # Top 10 input candidates
        'output_nodes': output_candidates[:10],  # Top 10 output candidates
        'bottleneck_nodes': bottleneck_candidates[:10]  # Top 10 bottlenecks
    }

# ============================================================================
# STEP 3: HYBRID ANALYSIS (Louvain + Layer-based)
# ============================================================================

# Detect supernodes
print("\n" + "="*60)
print("STEP 3A: Detect Supernodes (Auto-tuned Louvain)")
print("="*60)

# Auto-tune parameters based on graph density
louvain_params = auto_tune_louvain_params(G, target_range=(3, 10))

detector = SupernodeDetector(
    min_supernode_size=louvain_params['min_size'],
    max_supernode_size=louvain_params['max_size']
)

# Convert to undirected for community detection
# Important: Use absolute values of weights for community detection
# Negative weights represent inhibitory connections, but Louvain needs positive weights
G_undirected = G.to_undirected()

# Take absolute value of all edge weights
for u, v in G_undirected.edges():
    G_undirected[u][v]['weight'] = abs(G_undirected[u][v]['weight'])

print(f"\nGraph prepared for community detection (using absolute weights)")
supernodes = detector.detect_supernodes_louvain(
    G_undirected,
    resolution=louvain_params['resolution']
)

print(f"\nSupernodes detected: {len(supernodes)}")

# FALLBACK: If Louvain found no supernodes, use layer groups instead
if len(supernodes) == 0:
    print("\n[WARNING] Louvain detected 0 supernodes!")
    print("FALLBACK: Using layer groups as supernodes instead...")

    # Convert layer groups to supernode format
    # We'll compute layer groups early and use them as supernodes
    temp_layer_groups = analyze_by_layer_groups(G)
    supernodes = {}
    for idx, (group_name, group_data) in enumerate(temp_layer_groups.items()):
        supernodes[idx] = group_data['nodes']
        print(f"  Layer-based SN{idx} ({group_name}): {len(group_data['nodes'])} nodes")

    print(f"\nUsing {len(supernodes)} layer-based supernodes")

# Analyze each supernode
supernode_analyses = {}
for supernode_id, nodes in supernodes.items():
    # Manual analysis to avoid issues
    activations = [G.nodes[n]['activation'] for n in nodes]
    influences = [G.nodes[n].get('influence', 0.0) for n in nodes]
    layers = sorted(set(G.nodes[n]['layer'] for n in nodes))

    in_degree = sum(G.in_degree(n) for n in nodes)
    out_degree = sum(G.out_degree(n) for n in nodes)

    analysis = {
        'size': len(nodes),
        'nodes': nodes,
        'mean_activation': sum(activations) / len(activations),
        'max_activation': max(activations),
        'mean_influence': sum(influences) / len(influences),
        'max_influence': max(influences),
        'layers': layers,
        'total_in_degree': in_degree,
        'total_out_degree': out_degree
    }
    supernode_analyses[supernode_id] = analysis

    print(f"\nSupernode {supernode_id}:")
    print(f"  Size: {len(nodes)}")
    print(f"  Layers: {analysis['layers']}")
    print(f"  Mean activation: {analysis['mean_activation']:.3f}")
    print(f"  Mean influence: {analysis['mean_influence']:.3f}")
    print(f"  Degree (in/out): {analysis['total_in_degree']}/{analysis['total_out_degree']}")

# Rank supernodes
print("\n" + "="*60)
print("STEP 4: Rank Supernodes by Importance")
print("="*60)

ranked = detector.rank_supernodes(G, supernodes)
print("\nTop 10 supernodes (by importance):")
for rank, (supernode_id, score) in enumerate(ranked[:10], 1):
    nodes = supernodes[supernode_id]
    analysis = supernode_analyses[supernode_id]
    print(f"{rank}. SN{supernode_id}: score={score:.3f}, size={len(nodes)}, " +
          f"layers={analysis['layers']}, act={analysis['mean_activation']:.3f}")

# ============================================================================
# STEP 3B: Layer-based Analysis (Theory-driven)
# ============================================================================

print("\n" + "="*60)
print("STEP 3B: Layer-based Analysis (Theory-driven)")
print("="*60)

layer_groups = analyze_by_layer_groups(G)

print(f"\nLayer groups detected: {len(layer_groups)}")
for group_name, group_data in layer_groups.items():
    print(f"\n{group_name.upper()} (Layers {group_data['layer_range'][0]}-{group_data['layer_range'][1]}):")
    print(f"  Nodes: {group_data['num_nodes']}")
    print(f"  Mean activation: {group_data['mean_activation']:.3f}")
    print(f"  Max activation: {group_data['max_activation']:.3f}")
    print(f"  Edge flow: {group_data['incoming_edges']} in -> " +
          f"{group_data['internal_edges']} internal -> {group_data['outgoing_edges']} out")
    print(f"  Top feature: {group_data['top_features'][0]['label']} " +
          f"(act={group_data['top_features'][0]['activation']:.3f})")

# ============================================================================
# STEP 3C: Identify Steering Targets
# ============================================================================

print("\n" + "="*60)
print("STEP 3C: Identify Steering Targets")
print("="*60)

flow_analysis = identify_flow_nodes(G, layer_groups)

print(f"\nInput nodes (early layers, high fan-out): {len(flow_analysis['input_nodes'])}")
for i, node_data in enumerate(flow_analysis['input_nodes'][:5], 1):
    print(f"  {i}. {node_data['label']}: out_degree={node_data['out_degree']}, " +
          f"act={node_data['activation']:.3f}")

print(f"\nOutput nodes (late layers, high activation): {len(flow_analysis['output_nodes'])}")
for i, node_data in enumerate(flow_analysis['output_nodes'][:5], 1):
    print(f"  {i}. {node_data['label']}: act={node_data['activation']:.3f}, " +
          f"in_degree={node_data['in_degree']}")

print(f"\nBottleneck nodes (high betweenness): {len(flow_analysis['bottleneck_nodes'])}")
for i, node_data in enumerate(flow_analysis['bottleneck_nodes'][:5], 1):
    print(f"  {i}. {node_data['label']}: betweenness={node_data['betweenness']:.6f}, " +
          f"L{node_data['layer']}")

# ============================================================================
# SAVE COMPREHENSIVE ANALYSIS
# ============================================================================

print("\n" + "="*60)
print("STEP 4: Save Comprehensive Analysis")
print("="*60)

# Prepare comprehensive output with both analyses
comprehensive_analysis = {
    'metadata': metadata,
    'louvain_supernodes': {
        'params_used': louvain_params,
        'num_supernodes': len(supernodes),
        'supernodes': {
            str(sn_id): {
                'size': supernode_analyses[sn_id]['size'],
                'nodes': supernode_analyses[sn_id]['nodes'],
                'mean_activation': supernode_analyses[sn_id]['mean_activation'],
                'max_activation': supernode_analyses[sn_id]['max_activation'],
                'mean_influence': supernode_analyses[sn_id]['mean_influence'],
                'max_influence': supernode_analyses[sn_id]['max_influence'],
                'layers': supernode_analyses[sn_id]['layers'],
                'total_in_degree': supernode_analyses[sn_id]['total_in_degree'],
                'total_out_degree': supernode_analyses[sn_id]['total_out_degree']
            }
            for sn_id in supernodes.keys()
        },
        'rankings': [
            {'supernode_id': int(sn_id), 'score': float(score)}
            for sn_id, score in ranked
        ]
    },
    'layer_groups': {
        group_name: {
            'layer_range': group_data['layer_range'],
            'num_nodes': group_data['num_nodes'],
            'mean_activation': group_data['mean_activation'],
            'max_activation': group_data['max_activation'],
            'mean_influence': group_data['mean_influence'],
            'max_influence': group_data['max_influence'],
            'top_features': group_data['top_features'],
            'internal_edges': group_data['internal_edges'],
            'incoming_edges': group_data['incoming_edges'],
            'outgoing_edges': group_data['outgoing_edges']
        }
        for group_name, group_data in layer_groups.items()
    },
    'flow_analysis': flow_analysis
}

# Save comprehensive analysis
analysis_file = graph_file.parent / f"{graph_file.stem.replace('_converted', '')}_analysis.json"
with open(analysis_file, 'w') as f:
    json.dump(comprehensive_analysis, f, indent=2)

print(f"[OK] Comprehensive analysis saved to: {analysis_file}")
print(f"  - Louvain supernodes: {len(supernodes)}")
print(f"  - Layer groups: {len(layer_groups)}")
print(f"  - Steering targets: {len(flow_analysis['input_nodes']) + len(flow_analysis['output_nodes']) + len(flow_analysis['bottleneck_nodes'])} total")

# Also save old format for backward compatibility
supernode_file = graph_file.parent / f"{graph_file.stem.replace('_converted', '')}_supernodes.json"
detector.save_supernodes(supernodes, supernode_file)
print(f"\n[OK] Legacy supernodes file saved to: {supernode_file}")

# Analyze information flow
print("\n" + "="*60)
print("STEP 5: Additional Flow Statistics")
print("="*60)

# Identify early, middle, and late supernodes
early_supernodes = []  # Layers 0-5
middle_supernodes = []  # Layers 6-15
late_supernodes = []  # Layers 16+

for supernode_id, nodes in supernodes.items():
    analysis = supernode_analyses[supernode_id]
    layers = analysis['layers']
    min_layer = min(layers)
    max_layer = max(layers)

    if max_layer <= 5:
        early_supernodes.append(supernode_id)
    elif min_layer >= 16:
        late_supernodes.append(supernode_id)
    else:
        middle_supernodes.append(supernode_id)

print(f"Early supernodes (layers 0-5): {len(early_supernodes)}")
print(f"Middle supernodes (layers 6-15): {len(middle_supernodes)}")
print(f"Late supernodes (layers 16+): {len(late_supernodes)}")

# Find critical bottleneck supernodes
print("\nIdentifying bottleneck supernodes (high betweenness)...")

# Calculate betweenness centrality for supernodes
# Use representative nodes from each supernode
supernode_betweenness = {}
for supernode_id, nodes in supernodes.items():
    # Average betweenness of nodes in supernode
    node_betweenness = nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()))
    avg_betweenness = sum(node_betweenness.get(n, 0) for n in nodes) / len(nodes)
    supernode_betweenness[supernode_id] = avg_betweenness

# Top 5 bottlenecks
bottlenecks = sorted(supernode_betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
print("\nTop 5 bottleneck supernodes:")
for supernode_id, betweenness in bottlenecks:
    analysis = supernode_analyses[supernode_id]
    print(f"  SN{supernode_id}: betweenness={betweenness:.6f}, " +
          f"layers={analysis['layers']}, size={len(supernodes[supernode_id])}")

# Generate statistics
print("\n" + "="*60)
print("STEP 6: Graph Statistics")
print("="*60)

print(f"Overall graph:")
print(f"  Density: {nx.density(G):.6f}")
print(f"  Average degree: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}")

# Check connectivity
if nx.is_weakly_connected(G):
    print(f"  Weakly connected: Yes")
else:
    num_components = nx.number_weakly_connected_components(G)
    print(f"  Weakly connected: No ({num_components} components)")

print(f"\nActivation statistics:")
activations = [G.nodes[n]['activation'] for n in G.nodes()]
print(f"  Mean: {sum(activations)/len(activations):.3f}")
print(f"  Max: {max(activations):.3f}")
print(f"  Min: {min(activations):.3f}")

print(f"\nInfluence statistics:")
influences = [G.nodes[n]['influence'] for n in G.nodes()]
print(f"  Mean: {sum(influences)/len(influences):.3f}")
print(f"  Max: {max(influences):.3f}")
print(f"  Min: {min(influences):.3f}")

print(f"\nEdge weight statistics:")
weights = [G[u][v]['weight'] for u, v in G.edges()]
print(f"  Mean: {sum(weights)/len(weights):.3f}")
print(f"  Max: {max(weights):.3f}")
print(f"  Min: {min(weights):.3f}")

# Find highest activation nodes
print(f"\nTop 10 highest activation nodes:")
top_nodes = sorted(G.nodes(), key=lambda n: G.nodes[n]['activation'], reverse=True)[:10]
for i, node in enumerate(top_nodes, 1):
    data = G.nodes[node]
    print(f"  {i}. {data['label']}: act={data['activation']:.3f}, inf={data['influence']:.3f}")

print("\n" + "="*60)
print("[SUCCESS] Hybrid Circuit Analysis Complete!")
print("="*60)
print(f"\nComprehensive analysis saved: {analysis_file.name}")
print(f"Legacy supernodes file: {supernode_file.name}")
print(f"Location: {analysis_file.parent}")
print(f"\nAnalysis includes:")
print(f"  [+] Louvain community detection (auto-tuned, {len(supernodes)} communities)")
print(f"  [+] Layer-based analysis ({len(layer_groups)} theory-driven groups)")
print(f"  [+] Steering targets (input/output/bottleneck nodes)")
print(f"\nNext step: Run '/circuit-tracer-visualize' to create 8 visualizations")
print(f"  - 5 Louvain-based visualizations")
print(f"  - 3 Layer-based visualizations")

print("\n" + "="*60)
print("PROCESS COMPLETE")
print("="*60)
