"""
Visualize Real Neuronpedia Data
Creates PNG visualizations of converted graphs and supernodes
Supports interactive selection or command-line file specification
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np
import argparse
import sys

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

        # Check if supernodes exist
        supernode_path = graph_path.parent / f"{graph_path.stem.replace('_converted', '')}_supernodes.json"
        status = "[HAS SUPERNODES]" if supernode_path.exists() else "[NO SUPERNODES]"

        print(f"{i}. {graph_path.name} ({size_mb:.2f} MB) {status}")

    print("=" * 60)

def get_user_selection(graphs):
    """Get user's graph selection interactively"""
    print("\nSelect graph to visualize:")
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
    description='Visualize Circuit Tracer graph with supernodes',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''
Examples:
  python 4_visualize.py  (interactive mode)
  python 4_visualize.py --file path/to/graph_converted.json
    '''
)
parser.add_argument(
    '--file',
    type=str,
    help='Path to specific converted graph file (if not provided, will use interactive mode)'
)

args = parser.parse_args()

print("=" * 60)
print("CIRCUIT TRACER - VISUALIZATION")
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

# Determine supernode file path
supernode_file = graph_file.parent / f"{graph_file.stem.replace('_converted', '')}_supernodes.json"

if not supernode_file.exists():
    print(f"\n[ERROR] Supernodes file not found: {supernode_file.name}")
    print("Please run '/circuit-tracer-analyze' first to generate supernodes.")
    sys.exit(1)

# Load data
print("\n" + "=" * 60)
print("LOADING DATA")
print("=" * 60)
print(f"Graph: {graph_file.name}")
print(f"Supernodes: {supernode_file.name}")

with open(graph_file) as f:
    graph_data = json.load(f)

with open(supernode_file) as f:
    supernodes = json.load(f)

print(f"Loaded {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges")
print(f"Loaded {len(supernodes)} supernodes")

# Extract prompt for titles
prompt_text = graph_data.get('metadata', {}).get('prompt', 'Unknown prompt')
# Truncate if too long
if len(prompt_text) > 60:
    prompt_text = prompt_text[:57] + "..."

# Create NetworkX graph
G = nx.DiGraph()

for node in graph_data['nodes']:
    G.add_node(
        node['id'],
        layer=node['layer'],
        activation=node['activation'],
        influence=node.get('influence', 0.0),
        label=node['label']
    )

for edge in graph_data['edges']:
    G.add_edge(edge['source'], edge['target'], weight=edge['weight'])

# Assign supernode membership
node_to_supernode = {}
supernode_ids = []
for sn_id, node_list in supernodes.items():
    sn_id_int = int(sn_id)
    supernode_ids.append(sn_id_int)
    for node in node_list:
        node_to_supernode[node] = sn_id_int

supernode_ids = sorted(supernode_ids)
print(f"Supernode IDs: {supernode_ids}")

# Generate colors dynamically for all supernodes
def generate_colors(n):
    """Generate n distinct colors"""
    import colorsys
    colors = []
    for i in range(n):
        hue = i / n
        rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        colors.append(hex_color)
    return colors

color_list = generate_colors(len(supernode_ids))
supernode_colors = {sn_id: color_list[i] for i, sn_id in enumerate(supernode_ids)}

print("\n" + "="*60)
print("VISUALIZATION 1: Supernode Overview (Compressed)")
print("="*60)

# For large graphs, we'll create a compressed view showing supernode-level connections
fig, ax = plt.subplots(figsize=(14, 10))

# Create supernode graph (compressed view)
SG = nx.DiGraph()
supernode_stats = {}

for sn_id, nodes in supernodes.items():
    sn_id_int = int(sn_id)

    # Calculate supernode statistics
    activations = [G.nodes[n]['activation'] for n in nodes if n in G.nodes()]
    influences = [G.nodes[n].get('influence', 0.0) for n in nodes if n in G.nodes()]
    layers = [G.nodes[n]['layer'] for n in nodes if n in G.nodes()]

    mean_layer = np.mean(layers) if layers else 0
    mean_activation = np.mean(activations) if activations else 0

    supernode_stats[sn_id_int] = {
        'size': len(nodes),
        'mean_layer': mean_layer,
        'mean_activation': mean_activation,
        'mean_influence': np.mean(influences) if influences else 0,
        'layers': sorted(set(layers))
    }

    SG.add_node(sn_id_int, **supernode_stats[sn_id_int])

# Add edges between supernodes
supernode_edges = {}
for u, v in G.edges():
    if u in node_to_supernode and v in node_to_supernode:
        sn_u = node_to_supernode[u]
        sn_v = node_to_supernode[v]
        if sn_u != sn_v:
            key = (sn_u, sn_v)
            supernode_edges[key] = supernode_edges.get(key, 0) + 1

for (sn_u, sn_v), count in supernode_edges.items():
    SG.add_edge(sn_u, sn_v, weight=count)

# Layout: position by mean layer
pos = {}
for sn_id in SG.nodes():
    mean_layer = supernode_stats[sn_id]['mean_layer']
    # x = layer, y = spread vertically
    y_offset = (sn_id - 7) * 2  # Spread out vertically
    pos[sn_id] = (mean_layer, y_offset)

# Draw supernodes
node_sizes = [supernode_stats[sn_id]['size'] * 50 for sn_id in SG.nodes()]
node_colors = [supernode_colors.get(sn_id, '#CCCCCC') for sn_id in SG.nodes()]

nx.draw_networkx_nodes(
    SG, pos,
    node_size=node_sizes,
    node_color=node_colors,
    alpha=0.8,
    ax=ax
)

# Draw edges with weights
edge_widths = [SG[u][v]['weight'] / 100 for u, v in SG.edges()]
nx.draw_networkx_edges(
    SG, pos,
    width=edge_widths,
    alpha=0.3,
    edge_color='gray',
    arrows=True,
    arrowsize=20,
    ax=ax
)

# Labels
labels = {}
for sn_id in SG.nodes():
    stats = supernode_stats[sn_id]
    labels[sn_id] = f"SN{sn_id}\n{stats['size']} nodes\nL{min(stats['layers'])}-{max(stats['layers'])}\nAct: {stats['mean_activation']:.1f}"

nx.draw_networkx_labels(SG, pos, labels, font_size=9, font_weight='bold', ax=ax)

# Edge labels (connection counts)
edge_labels = {(u, v): f"{SG[u][v]['weight']}" for u, v in SG.edges()}
nx.draw_networkx_edge_labels(SG, pos, edge_labels, font_size=7, ax=ax)

ax.set_title(f'Supernode-Level Circuit\n"{prompt_text}"',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Mean Layer', fontsize=12)
ax.axis('off')

# Legend - dynamically generate based on actual supernodes
legend_elements = []
for sn_id in sorted(supernode_stats.keys())[:10]:  # Show up to 10 supernodes
    stats = supernode_stats[sn_id]
    color = supernode_colors.get(sn_id, '#CCCCCC')
    label = f"SN{sn_id}: {stats['size']} nodes (L{min(stats['layers'])}-{max(stats['layers'])})"
    legend_elements.append(mpatches.Patch(color=color, label=label))

if legend_elements:
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9)

plt.tight_layout()
# Create output directory using the graph file stem
output_dir = graph_file.parent.parent / "processed" / "visualizations"
output_dir.mkdir(parents=True, exist_ok=True)
base_name = graph_file.stem.replace('_converted', '')
output_path = output_dir / f"{base_name}_supernodes_overview.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"[OK] Saved: {output_path.name}")
plt.close()

print("\n" + "="*60)
print("VISUALIZATION 2: Layer-by-Layer Supernode Distribution")
print("="*60)

fig, ax = plt.subplots(figsize=(16, 8))

# Count nodes per layer per supernode
layer_supernode_counts = {}
for sn_id, nodes in supernodes.items():
    sn_id_int = int(sn_id)
    for node in nodes:
        if node in G.nodes():
            layer = G.nodes[node]['layer']
            if layer not in layer_supernode_counts:
                layer_supernode_counts[layer] = {}
            layer_supernode_counts[layer][sn_id_int] = layer_supernode_counts[layer].get(sn_id_int, 0) + 1

# Prepare data for stacked bar chart
layers = sorted(layer_supernode_counts.keys())
# Use actual supernode IDs
sn_ids = supernode_ids

data = {sn_id: [layer_supernode_counts.get(layer, {}).get(sn_id, 0) for layer in layers] for sn_id in sn_ids}

# Create stacked bar chart
x = np.arange(len(layers))
width = 0.8

bottom = np.zeros(len(layers))
for sn_id in sn_ids:
    ax.bar(x, data[sn_id], width, label=f'SN{sn_id}',
           bottom=bottom, color=supernode_colors.get(sn_id, '#CCCCCC'), alpha=0.8)
    bottom += data[sn_id]

ax.set_xlabel('Layer', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Nodes', fontsize=12, fontweight='bold')
ax.set_title(f'Supernode Distribution Across Layers\n"{prompt_text}"',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x[::2])  # Show every 2nd layer
ax.set_xticklabels(layers[::2])
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
output_path = output_dir / f"{base_name}_layer_distribution.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"[OK] Saved: {output_path.name}")
plt.close()

print("\n" + "="*60)
print("VISUALIZATION 3: Activation Heatmap by Layer")
print("="*60)

fig, ax = plt.subplots(figsize=(16, 6))

# Organize activations by layer and supernode
layer_sn_activations = {}
for sn_id, nodes in supernodes.items():
    sn_id_int = int(sn_id)
    for node in nodes:
        if node in G.nodes():
            layer = G.nodes[node]['layer']
            activation = G.nodes[node]['activation']

            if layer not in layer_sn_activations:
                # Initialize with all supernode IDs
                layer_sn_activations[layer] = {sn: [] for sn in supernode_ids}

            layer_sn_activations[layer][sn_id_int].append(activation)

# Calculate mean activations
layers = sorted(layer_sn_activations.keys())
mean_activations = {sn_id: [] for sn_id in supernode_ids}

for layer in layers:
    for sn_id in supernode_ids:
        acts = layer_sn_activations[layer][sn_id]
        mean_act = np.mean(acts) if acts else 0
        mean_activations[sn_id].append(mean_act)

# Plot
x = np.arange(len(layers))
for sn_id in supernode_ids:
    ax.plot(x, mean_activations[sn_id], marker='o', linewidth=2,
            label=f'SN{sn_id}', color=supernode_colors.get(sn_id, '#CCCCCC'), markersize=6)

ax.set_xlabel('Layer', fontsize=12, fontweight='bold')
ax.set_ylabel('Mean Activation', fontsize=12, fontweight='bold')
ax.set_title(f'Mean Activation by Layer and Supernode\n"{prompt_text}"',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x[::2])
ax.set_xticklabels(layers[::2])
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
output_path = output_dir / f"{base_name}_activation_heatmap.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"[OK] Saved: {output_path.name}")
plt.close()

print("\n" + "="*60)
print("VISUALIZATION 4: Top Features by Activation")
print("="*60)

fig, ax = plt.subplots(figsize=(12, 8))

# Get top 20 nodes by activation
nodes_by_activation = sorted(
    [(n, G.nodes[n]['activation'], G.nodes[n]['layer'], node_to_supernode.get(n, -1))
     for n in G.nodes()],
    key=lambda x: x[1],
    reverse=True
)[:20]

# Extract data
labels = [G.nodes[n]['label'] for n, _, _, _ in nodes_by_activation]
activations = [act for _, act, _, _ in nodes_by_activation]
colors = [supernode_colors.get(sn, '#CCCCCC') for _, _, _, sn in nodes_by_activation]

# Create horizontal bar chart
y_pos = np.arange(len(labels))
ax.barh(y_pos, activations, color=colors, alpha=0.8)

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel('Activation', fontsize=12, fontweight='bold')
ax.set_title(f'Top 20 Features by Activation\n"{prompt_text}"',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Add activation values as text
for i, (_, act, layer, sn) in enumerate(nodes_by_activation):
    ax.text(act + 2, i, f'{act:.1f} (L{layer}, SN{sn})',
            va='center', fontsize=8)

# Legend - dynamically generate based on actual supernodes
legend_elements = []
for sn_id in supernode_ids:
    color = supernode_colors.get(sn_id, '#CCCCCC')
    legend_elements.append(mpatches.Patch(color=color, label=f'SN{sn_id}'))

if legend_elements:
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()
output_path = output_dir / f"{base_name}_top_features.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"[OK] Saved: {output_path.name}")
plt.close()

print("\n" + "="*60)
print("VISUALIZATION 5: Edge Weight Distribution")
print("="*60)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Get all edge weights
weights = [G[u][v]['weight'] for u, v in G.edges()]
positive_weights = [w for w in weights if w > 0]
negative_weights = [w for w in weights if w < 0]

# Histogram of all weights
ax1.hist(weights, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
ax1.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero')
ax1.set_xlabel('Edge Weight', fontsize=11, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax1.set_title('Edge Weight Distribution\n(All Connections)', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Pie chart: positive vs negative
sizes = [len(positive_weights), len(negative_weights)]
labels = [f'Excitatory\n({len(positive_weights)} edges)',
          f'Inhibitory\n({len(negative_weights)} edges)']
colors_pie = ['#2ecc71', '#e74c3c']
explode = (0.05, 0.05)

ax2.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
        autopct='%1.1f%%', shadow=True, startangle=90, textprops={'fontsize': 11})
ax2.set_title('Excitatory vs Inhibitory Connections', fontsize=12, fontweight='bold')

plt.tight_layout()
output_path = output_dir / f"{base_name}_edge_weights.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"[OK] Saved: {output_path.name}")
plt.close()

print("\n" + "="*60)
print("[SUCCESS] ALL VISUALIZATIONS COMPLETE!")
print("="*60)
print("\nGenerated files:")
print(f"  1. {base_name}_supernodes_overview.png - Supernode-level circuit diagram")
print(f"  2. {base_name}_layer_distribution.png - Nodes per layer per supernode")
print(f"  3. {base_name}_activation_heatmap.png - Mean activation across layers")
print(f"  4. {base_name}_top_features.png - Top 20 features by activation")
print(f"  5. {base_name}_edge_weights.png - Edge weight distribution")
print(f"\nAll saved to: {output_dir}")
print(f"\nNext step: Run '/circuit-tracer-compare' to compare multiple graphs")

print("\n" + "=" * 60)
print("PROCESS COMPLETE")
print("=" * 60)
