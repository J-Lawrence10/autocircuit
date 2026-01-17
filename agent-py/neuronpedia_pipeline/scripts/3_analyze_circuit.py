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

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'skills' / 'phase1_data_collection'))

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

# Detect supernodes
print("\n" + "="*60)
print("STEP 3: Detect Supernodes (Louvain)")
print("="*60)

detector = SupernodeDetector(min_supernode_size=3, max_supernode_size=100)

# Convert to undirected for community detection
# Important: Use absolute values of weights for community detection
# Negative weights represent inhibitory connections, but Louvain needs positive weights
G_undirected = G.to_undirected()

# Take absolute value of all edge weights
for u, v in G_undirected.edges():
    G_undirected[u][v]['weight'] = abs(G_undirected[u][v]['weight'])

print(f"Graph prepared for community detection (using absolute weights)")
supernodes = detector.detect_supernodes_louvain(G_undirected)

print(f"\nSupernodes detected: {len(supernodes)}")

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

# Save supernodes
supernode_file = graph_file.parent / f"{graph_file.stem.replace('_converted', '')}_supernodes.json"
detector.save_supernodes(supernodes, supernode_file)
print(f"\n[OK] Supernodes saved to: {supernode_file}")

# Analyze information flow
print("\n" + "="*60)
print("STEP 5: Analyze Information Flow")
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
print("[SUCCESS] Circuit Analysis Complete!")
print("="*60)
print(f"Supernodes saved: {supernode_file.name}")
print(f"Location: {supernode_file}")
print(f"\nNext step: Run '/circuit-tracer-visualize' to create visualizations")

print("\n" + "="*60)
print("PROCESS COMPLETE")
print("="*60)
