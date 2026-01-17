"""
Convert real Neuronpedia graph to pipeline-compatible format
Transforms the detailed Circuit Tracer format to our simplified format
Supports auto-detection of latest file or manual file selection
"""

import json
import networkx as nx
from pathlib import Path
import argparse
import sys

def convert_neuronpedia_graph(input_file, output_file=None):
    """
    Convert real Neuronpedia graph JSON to our pipeline format

    Real format:
    - nodes: [{node_id, feature, layer, activation, influence, ...}]
    - links: [{source, target, weight}]

    Pipeline format:
    - nodes: [{id, label, layer, activation}]
    - edges: [{source, target, weight}]
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Converting graph from: {input_file}")
    print(f"Original nodes: {len(data['nodes'])}")
    print(f"Original links: {len(data['links'])}")

    # Convert nodes
    converted_nodes = []
    for node in data['nodes']:
        # Skip embedding nodes (layer 'E')
        if node['layer'] == 'E':
            continue

        # Skip nodes with missing activation data
        if node.get('activation') is None:
            continue

        converted_node = {
            'id': node['node_id'],
            'label': f"L{node['layer']}_F{node['feature']}",
            'layer': int(node['layer']),
            'activation': node['activation'],
            'influence': node.get('influence', 0.0),
            'feature_id': node['feature'],
            'ctx_idx': node.get('ctx_idx', 0)
        }
        converted_nodes.append(converted_node)

    # Create node_id set for filtering links
    valid_node_ids = set(n['id'] for n in converted_nodes)

    # Convert links (exclude embedding layer connections)
    converted_edges = []
    for link in data['links']:
        source = link['source']
        target = link['target']

        # Skip if source or target is embedding layer or not in valid nodes
        if source.startswith('E_') or target.startswith('E_'):
            continue
        if source not in valid_node_ids or target not in valid_node_ids:
            continue

        converted_edge = {
            'source': source,
            'target': target,
            'weight': link['weight']
        }
        converted_edges.append(converted_edge)

    # Create converted graph
    converted_graph = {
        'metadata': {
            'prompt': data['metadata']['prompt'],
            'slug': data['metadata']['slug'],
            'model': data['metadata']['scan'],
            'node_threshold': data['metadata']['node_threshold'],
            'original_nodes': len(data['nodes']),
            'original_links': len(data['links']),
            'converted_nodes': len(converted_nodes),
            'converted_edges': len(converted_edges)
        },
        'nodes': converted_nodes,
        'edges': converted_edges
    }

    print(f"\nConverted nodes: {len(converted_nodes)}")
    print(f"Converted edges: {len(converted_edges)}")

    # Get layer distribution
    layer_counts = {}
    for node in converted_nodes:
        layer = node['layer']
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    print(f"\nLayer distribution:")
    for layer in sorted(layer_counts.keys()):
        print(f"  Layer {layer}: {layer_counts[layer]} nodes")

    # Save converted graph
    if output_file is None:
        output_file = input_file.replace('.json', '_converted.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_graph, f, indent=2)

    print(f"\n[OK] Converted graph saved to: {output_file}")

    return converted_graph

def create_networkx_graph(converted_graph):
    """Create NetworkX graph from converted format"""

    G = nx.DiGraph()

    # Add nodes
    for node in converted_graph['nodes']:
        G.add_node(
            node['id'],
            label=node['label'],
            layer=node['layer'],
            activation=node['activation'],
            influence=node.get('influence', 0.0),
            feature_id=node['feature_id']
        )

    # Add edges
    for edge in converted_graph['edges']:
        G.add_edge(
            edge['source'],
            edge['target'],
            weight=edge['weight']
        )

    print(f"\n[OK] NetworkX graph created:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"  Density: {nx.density(G):.4f}")

    return G

def find_available_raw_graphs():
    """Find all raw (non-converted) graphs in the data directory"""
    graphs_dir = Path(__file__).parent.parent / "data" / "graphs"

    if not graphs_dir.exists():
        return []

    # Find all real_*.json files that are NOT converted
    all_graphs = list(graphs_dir.glob("real_*.json"))
    raw_graphs = [g for g in all_graphs if not g.name.endswith('_converted.json')]

    # Sort by modification time (newest first)
    raw_graphs.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    return raw_graphs

def display_available_graphs(graphs):
    """Display numbered list of available raw graphs"""
    print("\n" + "=" * 60)
    print("AVAILABLE RAW GRAPHS")
    print("=" * 60)

    if not graphs:
        print("No raw graphs found!")
        print("Please run '/circuit-tracer-fetch' first.")
        return

    for i, graph_path in enumerate(graphs, 1):
        # Get file size and modification time
        size_mb = graph_path.stat().st_size / (1024 * 1024)
        mtime = graph_path.stat().st_mtime

        # Check if already converted
        converted_path = graph_path.parent / f"{graph_path.stem}_converted.json"
        status = "[CONVERTED]" if converted_path.exists() else "[NOT CONVERTED]"

        print(f"{i}. {graph_path.name} ({size_mb:.2f} MB) {status}")

    print("=" * 60)

def get_user_selection(graphs):
    """Get user's graph selection interactively"""
    print("\nSelect graph to convert:")
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert Circuit Tracer graph to pipeline format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python 2_convert_graph.py  (interactive mode)
  python 2_convert_graph.py --file path/to/graph.json
        '''
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Path to specific graph file (if not provided, will use interactive mode)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("CIRCUIT TRACER - GRAPH CONVERSION")
    print("=" * 60)

    # Determine input file
    if args.file:
        # Command-line mode
        input_path = Path(args.file)
        if not input_path.exists():
            print(f"\n[ERROR] File not found: {input_path}")
            sys.exit(1)
        print(f"\nUsing file from command-line: {input_path.name}")
    else:
        # Interactive mode
        print("\nEntering interactive mode...")

        # Find available graphs
        available_graphs = find_available_raw_graphs()

        if not available_graphs:
            print("\n[ERROR] No raw graphs found!")
            print("Please run '/circuit-tracer-fetch' first.")
            sys.exit(1)

        # Display available graphs
        display_available_graphs(available_graphs)

        # Get user selection
        input_path = get_user_selection(available_graphs)
        print(f"\nSelected: {input_path.name}")

    # Generate output path
    output_path = input_path.parent / f"{input_path.stem}_converted.json"

    # Check if already converted
    if output_path.exists():
        print(f"\n[WARNING] Converted file already exists: {output_path.name}")
        overwrite = input("Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Conversion cancelled.")
            sys.exit(0)

    print("\n" + "=" * 60)
    print("CONVERTING GRAPH")
    print("=" * 60)

    # Convert
    converted = convert_neuronpedia_graph(input_path, output_path)

    # Create NetworkX graph to validate
    G = create_networkx_graph(converted)

    # Check for issues
    if not nx.is_weakly_connected(G):
        num_components = nx.number_weakly_connected_components(G)
        print(f"\n[WARNING] Graph has {num_components} weakly connected components")

        # Show component sizes
        components = list(nx.weakly_connected_components(G))
        component_sizes = sorted([len(c) for c in components], reverse=True)
        print(f"Component sizes: {component_sizes[:10]}")

    print("\n" + "=" * 60)
    print("[SUCCESS] Conversion complete!")
    print("=" * 60)
    print(f"Output: {output_path.name}")
    print(f"Location: {output_path}")
    print(f"\nNext step: Run '/circuit-tracer-analyze' to detect supernodes")

    print("\n" + "=" * 60)
    print("PROCESS COMPLETE")
    print("=" * 60)
