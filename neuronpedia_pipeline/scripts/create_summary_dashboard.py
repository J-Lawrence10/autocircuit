"""
Create Clear Summary Dashboard
Generates an easy-to-read summary visualization with key statistics
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import sys
import argparse
import numpy as np

def create_summary_dashboard(analysis_file, output_path):
    """Create a clear, readable summary dashboard"""

    with open(analysis_file) as f:
        data = json.load(f)

    metadata = data['metadata']
    layer_groups = data['layer_groups']
    flow_analysis = data['flow_analysis']

    # Create figure with clear layout
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)

    # Main title with model output (showing top prediction)
    prompt = metadata['prompt'].replace('<bos>', '')
    model_output = metadata.get('model_output', '?')
    output_prob = metadata.get('output_probability', 0)

    if model_output:
        title = f'Circuit Analysis: "{prompt}"\n✓ TOP PREDICTION: "{model_output}" ({output_prob:.1%})'
    else:
        title = f'Circuit Analysis Summary\n"{prompt}"'

    fig.suptitle(title, fontsize=18, fontweight='bold', y=0.98)

    # ============================================================================
    # TOP LEFT: Model Predictions
    # ============================================================================
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')

    # Show top predictions if available
    top_predictions = metadata.get('top_predictions', [])
    if top_predictions:
        pred_text = "MODEL OUTPUT PREDICTIONS\n\n"
        for i, pred in enumerate(top_predictions[:6], 1):
            token = pred['token'].replace('\n', '\\n').replace(' ', '·')
            prob = pred['probability']
            marker = '→' if i == 1 else ' '
            pred_text += f"{marker} {i}. \"{token}\" ({prob:.1%})\n"
    else:
        pred_text = f"MODEL OUTPUT\n\nTop: \"{model_output}\" ({output_prob:.1%})"

    ax1.text(0.05, 0.95, pred_text, transform=ax1.transAxes,
            fontsize=11, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

    # ============================================================================
    # TOP MIDDLE: Key Statistics
    # ============================================================================
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis('off')

    stats_text = f"""
CIRCUIT STATISTICS

Total Features: {metadata['converted_nodes']:,}
Total Connections: {metadata['converted_edges']:,}
Model: {metadata['model']}

LAYER BREAKDOWN
• Input (L0-5): {layer_groups['input']['num_nodes']} features
• Early Proc (L6-10): {layer_groups['early_proc']['num_nodes']} features
• Middle Proc (L11-15): {layer_groups['middle_proc']['num_nodes']} features
• Late Proc (L16-20): {layer_groups['late_proc']['num_nodes']} features
• Output (L21-25): {layer_groups['output']['num_nodes']} features
"""

    ax2.text(0.05, 0.95, stats_text, transform=ax2.transAxes,
            fontsize=11, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

    # ============================================================================
    # TOP RIGHT: Feature Distribution
    # ============================================================================
    ax3 = fig.add_subplot(gs[0, 2])

    group_names = ['Input\n(L0-5)', 'Early\n(L6-10)', 'Middle\n(L11-15)',
                   'Late\n(L16-20)', 'Output\n(L21-25)']
    node_counts = [layer_groups['input']['num_nodes'],
                   layer_groups['early_proc']['num_nodes'],
                   layer_groups['middle_proc']['num_nodes'],
                   layer_groups['late_proc']['num_nodes'],
                   layer_groups['output']['num_nodes']]

    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']

    bars = ax2.bar(group_names, node_counts, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Number of Features', fontsize=12, fontweight='bold')
    ax2.set_title('Feature Distribution Across Layers', fontsize=13, fontweight='bold', pad=15)
    ax2.grid(axis='y', alpha=0.3)

    # Add values on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # ============================================================================
    # TOP RIGHT: Activation Strengths
    # ============================================================================
    ax3 = fig.add_subplot(gs[0, 2])

    max_acts = [layer_groups['input']['max_activation'],
                layer_groups['early_proc']['max_activation'],
                layer_groups['middle_proc']['max_activation'],
                layer_groups['late_proc']['max_activation'],
                layer_groups['output']['max_activation']]

    bars = ax3.barh(group_names, max_acts, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('Maximum Activation Strength', fontsize=12, fontweight='bold')
    ax3.set_title('Strongest Features Per Stage', fontsize=13, fontweight='bold', pad=15)
    ax3.grid(axis='x', alpha=0.3)
    ax3.invert_yaxis()

    # Add values
    for i, (bar, val) in enumerate(zip(bars, max_acts)):
        ax3.text(val + 2, bar.get_y() + bar.get_height()/2.,
                f'{val:.1f}',
                ha='left', va='center', fontsize=10, fontweight='bold')

    # ============================================================================
    # MIDDLE ROW: Information Flow
    # ============================================================================
    ax4 = fig.add_subplot(gs[1, :])
    ax4.axis('off')
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 6)

    # Draw flow diagram
    x_positions = [1, 2.8, 4.6, 6.4, 8.2]
    y_center = 3

    stage_names = ['INPUT', 'EARLY\nPROC', 'MIDDLE\nPROC', 'LATE\nPROC', 'OUTPUT']
    stage_data = [
        layer_groups['input'],
        layer_groups['early_proc'],
        layer_groups['middle_proc'],
        layer_groups['late_proc'],
        layer_groups['output']
    ]

    for i, (x, name, color, data) in enumerate(zip(x_positions, stage_names, colors, stage_data)):
        # Draw circle
        circle = plt.Circle((x, y_center), 0.6, color=color, alpha=0.7, zorder=2,
                           edgecolor='black', linewidth=2)
        ax4.add_patch(circle)

        # Stage name
        ax4.text(x, y_center+0.15, name, ha='center', va='center',
                fontsize=10, fontweight='bold', zorder=3)

        # Node count
        ax4.text(x, y_center-0.15, f"{data['num_nodes']}\nfeatures",
                ha='center', va='center', fontsize=8, zorder=3)

        # Max activation below
        ax4.text(x, y_center-1.2, f"Max: {data['max_activation']:.0f}",
                ha='center', va='center', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # Draw arrow to next stage
        if i < len(x_positions) - 1:
            arrow = mpatches.FancyArrowPatch(
                (x+0.6, y_center), (x_positions[i+1]-0.6, y_center),
                arrowstyle='->', mutation_scale=30, linewidth=3,
                color='gray', alpha=0.6, zorder=1
            )
            ax4.add_patch(arrow)

            # Edge count
            if i == 0:
                edge_count = layer_groups['input']['outgoing_edges']
            elif i == 1:
                edge_count = layer_groups['early_proc']['outgoing_edges']
            elif i == 2:
                edge_count = layer_groups['middle_proc']['outgoing_edges']
            elif i == 3:
                edge_count = layer_groups['late_proc']['outgoing_edges']

            mid_x = (x + x_positions[i+1]) / 2
            ax4.text(mid_x, y_center+0.8, f"{edge_count:,}\nconnections",
                    ha='center', va='center', fontsize=8, style='italic')

    ax4.set_title('Information Flow Through Model', fontsize=14, fontweight='bold',
                 y=0.95, pad=20)

    # ============================================================================
    # BOTTOM LEFT: Top Input Features
    # ============================================================================
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.axis('off')

    input_nodes = flow_analysis['input_nodes'][:5]

    input_text = "TOP INPUT AMPLIFIERS\n"
    input_text += "(Early features with many connections)\n\n"

    for i, node in enumerate(input_nodes, 1):
        layer = node['label'].split('_')[0]
        connections = node['out_degree']
        activation = node['activation']
        input_text += f"{i}. {node['label']}\n"
        input_text += f"   → {connections} connections, act={activation:.1f}\n\n"

    ax5.text(0.05, 0.95, input_text, transform=ax5.transAxes,
            fontsize=9, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

    # ============================================================================
    # BOTTOM MIDDLE: Top Output Features
    # ============================================================================
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')

    output_nodes = flow_analysis['output_nodes'][:5]

    output_text = "TOP OUTPUT FEATURES\n"
    output_text += "(Final layer features with strong activation)\n\n"

    for i, node in enumerate(output_nodes, 1):
        layer = node['label'].split('_')[0]
        activation = node['activation']
        in_connections = node['in_degree']
        output_text += f"{i}. {node['label']}\n"
        output_text += f"   → act={activation:.1f}, {in_connections} inputs\n\n"

    ax6.text(0.05, 0.95, output_text, transform=ax6.transAxes,
            fontsize=9, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))

    # ============================================================================
    # BOTTOM RIGHT: Key Bottlenecks
    # ============================================================================
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.axis('off')

    bottleneck_nodes = flow_analysis['bottleneck_nodes'][:5]

    bottleneck_text = "KEY BOTTLENECK FEATURES\n"
    bottleneck_text += "(Critical features for information flow)\n\n"

    for i, node in enumerate(bottleneck_nodes, 1):
        layer = node['layer']
        betweenness = node['betweenness']
        bottleneck_text += f"{i}. {node['label']}\n"
        bottleneck_text += f"   → Layer {layer}, centrality={betweenness:.5f}\n\n"

    ax7.text(0.05, 0.95, bottleneck_text, transform=ax7.transAxes,
            fontsize=9, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))

    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"[OK] Summary dashboard saved to: {output_path.name}")
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create summary dashboard')
    parser.add_argument('--analysis', type=str, required=True, help='Path to analysis JSON')
    parser.add_argument('--output', type=str, required=True, help='Output PNG path')

    args = parser.parse_args()

    create_summary_dashboard(Path(args.analysis), Path(args.output))
