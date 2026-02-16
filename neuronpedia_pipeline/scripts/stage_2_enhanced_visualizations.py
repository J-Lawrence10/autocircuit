#!/usr/bin/env python3
"""
Stage 2: Enhanced Visualizations

Creates semantic-aware, interactive visualizations that tell the story of how
information flows through neural circuits and where bottlenecks filter it.

Outputs:
  1. semantic_circuit_overview.png - Circuit graph with semantic node coloring
  2. thought_progression.png - Visual diagram of semantic flow through layers
  3. interactive_circuit.html - Plotly interactive circuit explorer
  4. semantic_dashboard.html - Comprehensive semantic dashboard

Usage:
    python stage_2_enhanced_visualizations.py [--circuit CIRCUIT_DIR] [--all]
"""

import json
import sys
import io
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False
matplotlib.rcParams['text.parse_math'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
PROMPTS_DIR = DATA_DIR / 'prompts'

# Semantic color palette
SEMANTIC_COLORS = {
    'SYNTAX': '#E74C3C',           # Red
    'SEMANTICS:CODE': '#95A5A6',   # Gray
    'SEMANTICS:CONCEPT': '#2ECC71', # Green
    'SEMANTICS:GEOGRAPHIC': '#3498DB', # Blue
    'SEMANTICS:TEMPORAL': '#F39C12',   # Yellow/Orange
    'SEMANTICS:ENTITY': '#E67E22',     # Orange
    'POLYSEMANTIC': '#9B59B6',     # Purple
    'UNKNOWN': '#BDC3C7',          # Light gray
    'BOTTLENECK': '#C0392B',       # Dark red
}

# Layer stage definitions
GEMMA_STAGES = {
    'Input Recognition': (0, 2),
    'Syntactic Parse': (3, 5),
    'Semantic Encoding': (6, 10),
    'Knowledge Retrieval': (11, 18),
    'Decision Formation': (19, 25),
}

QWEN_STAGES = {
    'Input Recognition': (0, 4),
    'Syntactic Parse': (5, 8),
    'Semantic Encoding': (9, 15),
    'Knowledge Retrieval': (16, 26),
    'Decision Formation': (27, 35),
}


def load_bottleneck_library() -> Dict:
    """Load the Stage 1.5 bottleneck library."""
    lib_file = DATA_DIR / 'stage_1_5_bottleneck_library.json'
    if lib_file.exists():
        with open(lib_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_traceback_data(circuit_dir: Path) -> Optional[Dict]:
    """Load traceback_paths.json for a circuit."""
    tb_file = circuit_dir / '3_analysis' / 'traceback_paths.json'
    if tb_file.exists():
        with open(tb_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def load_converted_graph(circuit_dir: Path) -> Optional[Dict]:
    """Load converted graph for a circuit."""
    conv_dir = circuit_dir / '2_conversion'
    if not conv_dir.exists():
        return None
    conv_files = list(conv_dir.glob('*_converted_graph.json'))
    if not conv_files:
        return None
    with open(conv_files[0], 'r', encoding='utf-8') as f:
        return json.load(f)


def get_feature_semantic_info(label: str, library: Dict) -> Dict:
    """Look up semantic info for a feature from the library."""
    cross = library.get('cross_circuit_features', {})
    if label in cross:
        entry = cross[label]
        return {
            'explanation': entry.get('explanation', ''),
            'examples': entry.get('examples', []),
            'cross_circuit': True,
            'circuits_count': entry.get('circuits_appeared_in', 0),
        }
    return {'explanation': '', 'examples': [], 'cross_circuit': False, 'circuits_count': 0}


def classify_node_semantic(label: str, layer: int, library: Dict, bottleneck_labels: set) -> str:
    """Classify a node's semantic category based on available data."""
    if label in bottleneck_labels:
        return 'BOTTLENECK'

    info = get_feature_semantic_info(label, library)
    explanation = info.get('explanation', '').lower()

    if not explanation:
        # Heuristic based on layer
        if layer <= 2:
            return 'SYNTAX'
        elif layer <= 10:
            return 'SEMANTICS:CODE'
        else:
            return 'SEMANTICS:CONCEPT'

    # Classify based on explanation keywords
    if any(w in explanation for w in ['code', 'programming', 'function', 'variable', 'html', 'xml', 'tag']):
        return 'SEMANTICS:CODE'
    elif any(w in explanation for w in ['place', 'city', 'country', 'state', 'geographic', 'location', 'capital']):
        return 'SEMANTICS:GEOGRAPHIC'
    elif any(w in explanation for w in ['date', 'time', 'year', 'month', 'temporal', 'period']):
        return 'SEMANTICS:TEMPORAL'
    elif any(w in explanation for w in ['name', 'person', 'entity', 'who']):
        return 'SEMANTICS:ENTITY'
    elif any(w in explanation for w in ['opinion', 'concept', 'meaning', 'idea', 'inhibit', 'transition']):
        return 'SEMANTICS:CONCEPT'
    elif any(w in explanation for w in ['pronoun', 'conjunction', 'grammar', 'syntax', 'punctuation']):
        return 'SYNTAX'
    else:
        return 'SEMANTICS:CONCEPT'


def extract_path_features(traceback_data: Dict) -> Tuple[List, set]:
    """Extract all features from traceback paths and identify bottlenecks."""
    all_features = []
    feature_path_count = defaultdict(int)
    num_paths = len(traceback_data.get('critical_paths', []))

    for path in traceback_data.get('critical_paths', []):
        seen = set()
        for node in path.get('path_nodes', []):
            label = node.get('label', '')
            if label and label not in seen:
                seen.add(label)
                feature_path_count[label] += 1
                all_features.append(node)

    # Bottlenecks: features in 80%+ of paths
    bottleneck_labels = {
        label for label, count in feature_path_count.items()
        if count / max(num_paths, 1) >= 0.8
    }

    return all_features, bottleneck_labels


# ========================================================================
# FIGURE 1: Semantic Circuit Overview (Static PNG)
# ========================================================================

def create_semantic_circuit_overview(
    circuit_dir: Path,
    traceback_data: Dict,
    graph_data: Dict,
    library: Dict,
    output_dir: Path,
):
    """Create circuit overview with semantic node coloring."""
    all_features, bottleneck_labels = extract_path_features(traceback_data)

    metadata = graph_data.get('metadata', {})
    model = metadata.get('model', 'unknown')
    prompt = metadata.get('prompt', '').replace('<bos>', '').replace('<|im_end|>', '').strip()
    predictions = metadata.get('top_predictions', [])
    is_gemma = 'gemma' in model
    total_layers = 26 if is_gemma else 36

    # Group features by layer
    layer_features = defaultdict(list)
    for feat in all_features:
        layer_features[feat['layer']].append(feat)

    # Deduplicate per layer
    layer_unique = {}
    for layer, feats in layer_features.items():
        seen = set()
        unique = []
        for f in sorted(feats, key=lambda x: -x.get('score', 0)):
            if f['label'] not in seen:
                seen.add(f['label'])
                unique.append(f)
        layer_unique[layer] = unique[:8]  # Max 8 per layer for readability

    fig, ax = plt.subplots(figsize=(20, 12))
    ax.set_xlim(-1, total_layers)
    ax.set_ylim(-2, 10)
    ax.set_axis_off()

    # Title
    top_pred = predictions[0]['token'] if predictions else '?'
    top_prob = predictions[0]['probability'] if predictions else 0
    correct = top_prob > 0.5
    result_emoji = "CORRECT" if correct else "WRONG"
    ax.set_title(
        f'Semantic Circuit Overview: "{prompt}"\n'
        f'Model: {model.upper()} | Top prediction: "{top_pred}" ({top_prob:.1%}) | {result_emoji}',
        fontsize=16, fontweight='bold', pad=20
    )

    # Draw layer columns
    stages = GEMMA_STAGES if is_gemma else QWEN_STAGES
    stage_colors = ['#FDEBD0', '#D5F5E3', '#D4E6F1', '#F5EEF8', '#FADBD8']

    for i, (stage_name, (start, end)) in enumerate(stages.items()):
        ax.axvspan(start - 0.4, end + 0.4, alpha=0.15, color=stage_colors[i])
        mid = (start + end) / 2
        ax.text(mid, 9.5, stage_name, ha='center', va='top', fontsize=9,
                fontstyle='italic', color='gray')

    # Draw nodes
    legend_categories = set()
    for layer, features in sorted(layer_unique.items()):
        x = layer
        for i, feat in enumerate(features):
            y = 7 - i * 1.1
            label = feat['label']

            # Determine semantic category
            category = classify_node_semantic(label, layer, library, bottleneck_labels)
            color = SEMANTIC_COLORS.get(category, '#BDC3C7')
            legend_categories.add(category)

            # Draw node
            size = 200 if category == 'BOTTLENECK' else 120
            edgecolor = '#C0392B' if category == 'BOTTLENECK' else 'black'
            linewidth = 2.5 if category == 'BOTTLENECK' else 0.5

            ax.scatter(x, y, s=size, c=color, edgecolors=edgecolor,
                      linewidths=linewidth, zorder=5, alpha=0.85)

            # Short label
            short = label.split('_F')[1][:6] if '_F' in label else label[-6:]
            ax.text(x, y - 0.35, short, ha='center', va='top', fontsize=5.5,
                   color='#333', alpha=0.7)

    # Draw connections between consecutive layers (simplified)
    for path in traceback_data.get('critical_paths', [])[:3]:
        nodes = path.get('path_nodes', [])
        for j in range(len(nodes) - 1):
            l1, l2 = nodes[j]['layer'], nodes[j+1]['layer']
            if l1 != l2:
                y1_idx = min(3, j % 8)
                y2_idx = min(3, (j+1) % 8)
                ax.plot([l1, l2], [7 - y1_idx * 1.1, 7 - y2_idx * 1.1],
                       color='gray', alpha=0.15, linewidth=0.5, zorder=1)

    # Legend
    legend_patches = []
    for cat in sorted(legend_categories):
        color = SEMANTIC_COLORS.get(cat, '#BDC3C7')
        name = cat.replace('SEMANTICS:', '').replace(':', ': ')
        legend_patches.append(mpatches.Patch(facecolor=color, edgecolor='black',
                                             linewidth=0.5, label=name))

    ax.legend(handles=legend_patches, loc='lower right', fontsize=8,
             title='Semantic Categories', framealpha=0.9, ncol=2)

    # Layer numbers at bottom
    for layer in range(total_layers):
        if layer in layer_unique:
            ax.text(layer, -1.5, f'L{layer}', ha='center', va='center',
                   fontsize=7, color='gray')

    plt.tight_layout()
    output_path = output_dir / 'semantic_circuit_overview.png'
    fig.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  [1] semantic_circuit_overview.png")
    return output_path


# ========================================================================
# FIGURE 2: Thought Progression Diagram (Static PNG)
# ========================================================================

def create_thought_progression_diagram(
    circuit_dir: Path,
    traceback_data: Dict,
    graph_data: Dict,
    library: Dict,
    output_dir: Path,
):
    """Create visual thought progression showing semantic flow through layers."""
    all_features, bottleneck_labels = extract_path_features(traceback_data)

    metadata = graph_data.get('metadata', {})
    model = metadata.get('model', 'unknown')
    prompt = metadata.get('prompt', '').replace('<bos>', '').replace('<|im_end|>', '').strip()
    predictions = metadata.get('top_predictions', [])
    is_gemma = 'gemma' in model
    stages = GEMMA_STAGES if is_gemma else QWEN_STAGES

    # Classify all features by stage
    stage_composition = {}
    for stage_name, (start, end) in stages.items():
        stage_feats = [f for f in all_features if start <= f['layer'] <= end]
        cats = defaultdict(int)
        for f in stage_feats:
            cat = classify_node_semantic(f['label'], f['layer'], library, bottleneck_labels)
            cats[cat] += 1
        total = sum(cats.values()) or 1
        stage_composition[stage_name] = {
            'counts': dict(cats),
            'total': total,
            'percentages': {k: v/total for k, v in cats.items()},
            'bottleneck_count': cats.get('BOTTLENECK', 0),
            'layer_range': (start, end),
        }

    fig, axes = plt.subplots(1, 5, figsize=(22, 8))
    fig.suptitle(
        f'Thought Progression: "{prompt}"\nModel: {model.upper()}',
        fontsize=16, fontweight='bold', y=0.98
    )

    stage_icons = ['INPUT', 'PARSE', 'ENCODE', 'RETRIEVE', 'DECIDE']
    stage_descriptions = [
        'Token recognition\n& embedding',
        'Grammar structure\n& syntax rules',
        'Meaning extraction\n& concept formation',
        'Factual knowledge\n& associations',
        'Final answer\nselection',
    ]

    for idx, (stage_name, comp) in enumerate(stage_composition.items()):
        ax = axes[idx]

        # Pie chart of semantic composition
        cats = comp['counts']
        if not cats:
            cats = {'UNKNOWN': 1}

        labels = []
        sizes = []
        colors = []
        for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
            short_name = cat.replace('SEMANTICS:', '').replace(':', '')
            labels.append(f'{short_name}\n({count})')
            sizes.append(count)
            colors.append(SEMANTIC_COLORS.get(cat, '#BDC3C7'))

        wedges, texts = ax.pie(sizes, colors=colors, startangle=90,
                               wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})

        # Add bottleneck indicator
        if comp['bottleneck_count'] > 0:
            ax.set_title(
                f'{stage_name}\n(L{comp["layer_range"][0]}-L{comp["layer_range"][1]})\n'
                f'BOTTLENECK: {comp["bottleneck_count"]} features',
                fontsize=10, fontweight='bold', color='#C0392B', pad=10
            )
        else:
            ax.set_title(
                f'{stage_name}\n(L{comp["layer_range"][0]}-L{comp["layer_range"][1]})',
                fontsize=10, fontweight='bold', pad=10
            )

        # Stage description below
        ax.text(0, -1.5, stage_descriptions[idx], ha='center', va='top',
               fontsize=8, color='gray', fontstyle='italic')

        # Feature count
        ax.text(0, -1.9, f'{comp["total"]} features', ha='center', va='top',
               fontsize=9, fontweight='bold')

    # Add flow arrows between stages
    for i in range(4):
        fig.text(
            0.14 + i * 0.19, 0.48, '>>>',
            fontsize=20, color='#3498DB', fontweight='bold',
            ha='center', va='center',
            transform=fig.transFigure,
        )

    # Add prediction result at bottom
    if predictions:
        pred_text = ' | '.join([
            f'"{p["token"]}" ({p["probability"]:.1%})'
            for p in predictions[:3]
        ])
        fig.text(0.5, 0.02, f'Output: {pred_text}', ha='center', fontsize=11,
                fontstyle='italic', color='#2C3E50')

    # Legend
    legend_patches = [
        mpatches.Patch(facecolor=SEMANTIC_COLORS[cat], edgecolor='black',
                      linewidth=0.5, label=cat.replace('SEMANTICS:', ''))
        for cat in ['SYNTAX', 'SEMANTICS:CODE', 'SEMANTICS:CONCEPT',
                    'SEMANTICS:GEOGRAPHIC', 'POLYSEMANTIC', 'BOTTLENECK']
    ]
    fig.legend(handles=legend_patches, loc='lower center', ncol=6,
              fontsize=8, framealpha=0.9, bbox_to_anchor=(0.5, 0.06))

    plt.tight_layout(rect=[0, 0.12, 1, 0.95])
    output_path = output_dir / 'thought_progression.png'
    fig.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  [2] thought_progression.png")
    return output_path


# ========================================================================
# FIGURE 3: Interactive Plotly Circuit Explorer (HTML)
# ========================================================================

def create_interactive_circuit(
    circuit_dir: Path,
    traceback_data: Dict,
    graph_data: Dict,
    library: Dict,
    output_dir: Path,
):
    """Create interactive Plotly visualization of the circuit."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("  [3] SKIPPED - plotly not installed")
        return None

    all_features, bottleneck_labels = extract_path_features(traceback_data)

    metadata = graph_data.get('metadata', {})
    model = metadata.get('model', 'unknown')
    prompt = metadata.get('prompt', '').replace('<bos>', '').replace('<|im_end|>', '').strip()
    predictions = metadata.get('top_predictions', [])
    is_gemma = 'gemma' in model
    total_layers = 26 if is_gemma else 36

    # Deduplicate features per layer
    layer_features = defaultdict(list)
    seen_labels = set()
    for feat in sorted(all_features, key=lambda x: -x.get('score', 0)):
        label = feat['label']
        if label not in seen_labels:
            seen_labels.add(label)
            layer_features[feat['layer']].append(feat)

    # Build scatter data
    x_vals, y_vals = [], []
    colors, sizes = [], []
    hover_texts, marker_symbols = [], []

    for layer in range(total_layers):
        feats = layer_features.get(layer, [])[:10]
        for i, feat in enumerate(feats):
            label = feat['label']
            category = classify_node_semantic(label, layer, library, bottleneck_labels)
            info = get_feature_semantic_info(label, library)

            x_vals.append(layer)
            y_vals.append(8 - i * 0.9)
            colors.append(SEMANTIC_COLORS.get(category, '#BDC3C7'))
            sizes.append(20 if category == 'BOTTLENECK' else 10)
            marker_symbols.append('diamond' if category == 'BOTTLENECK' else 'circle')

            # Build hover text
            explanation = info.get('explanation', 'No data')[:80]
            examples = ', '.join(info.get('examples', [])[:3]) or 'N/A'
            cross = f"YES ({info['circuits_count']} circuits)" if info.get('cross_circuit') else 'No'
            convergence = ''
            for bn in traceback_data.get('critical_paths', [{}])[0].get('path_nodes', []):
                if bn.get('label') == label:
                    convergence = f"Score: {bn.get('score', 0):.2e}"
                    break

            hover = (
                f"<b>{label}</b><br>"
                f"Layer: {layer} | Category: {category}<br>"
                f"Explanation: {explanation}<br>"
                f"Examples: {examples}<br>"
                f"Cross-circuit: {cross}<br>"
                f"{convergence}"
            )
            hover_texts.append(hover)

    # Create figure
    fig = go.Figure()

    # Add nodes
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode='markers',
        marker=dict(
            size=sizes,
            color=colors,
            line=dict(width=1, color='black'),
            opacity=0.85,
        ),
        text=hover_texts,
        hoverinfo='text',
        name='Features',
    ))

    # Add path connections (top path only)
    if traceback_data.get('critical_paths'):
        path_nodes = traceback_data['critical_paths'][0].get('path_nodes', [])
        path_x, path_y = [], []
        for node in path_nodes:
            layer = node['layer']
            # Find y position for this node
            feats = layer_features.get(layer, [])
            y_pos = 8
            for j, f in enumerate(feats[:10]):
                if f['label'] == node.get('label'):
                    y_pos = 8 - j * 0.9
                    break
            path_x.append(layer)
            path_y.append(y_pos)

        fig.add_trace(go.Scatter(
            x=path_x, y=path_y,
            mode='lines',
            line=dict(color='rgba(52, 152, 219, 0.3)', width=2),
            name='Top Path',
            hoverinfo='skip',
        ))

    # Layout
    fig.update_layout(
        title=dict(
            text=f'Interactive Circuit Explorer: "{prompt}"<br>'
                 f'<sub>Model: {model.upper()} | Hover over nodes for semantic details</sub>',
            font=dict(size=16),
        ),
        xaxis=dict(title='Layer', dtick=1, range=[-0.5, total_layers - 0.5]),
        yaxis=dict(title='', showticklabels=False, range=[-1, 10]),
        plot_bgcolor='white',
        width=1400,
        height=700,
        showlegend=True,
        hovermode='closest',
    )

    # Add stage annotations
    stages = GEMMA_STAGES if is_gemma else QWEN_STAGES
    for stage_name, (start, end) in stages.items():
        fig.add_vrect(x0=start-0.4, x1=end+0.4, fillcolor='lightblue',
                     opacity=0.08, line_width=0)
        fig.add_annotation(
            x=(start+end)/2, y=9.5,
            text=stage_name, showarrow=False,
            font=dict(size=10, color='gray'),
        )

    output_path = output_dir / 'interactive_circuit.html'
    fig.write_html(str(output_path), include_plotlyjs=True)
    print(f"  [3] interactive_circuit.html")
    return output_path


# ========================================================================
# FIGURE 4: Semantic Dashboard (HTML)
# ========================================================================

def create_semantic_dashboard(
    circuit_dir: Path,
    traceback_data: Dict,
    graph_data: Dict,
    library: Dict,
    output_dir: Path,
):
    """Create comprehensive semantic dashboard with multiple panels."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("  [4] SKIPPED - plotly not installed")
        return None

    all_features, bottleneck_labels = extract_path_features(traceback_data)

    metadata = graph_data.get('metadata', {})
    model = metadata.get('model', 'unknown')
    prompt = metadata.get('prompt', '').replace('<bos>', '').replace('<|im_end|>', '').strip()
    predictions = metadata.get('top_predictions', [])
    is_gemma = 'gemma' in model
    total_layers = 26 if is_gemma else 36
    stages = GEMMA_STAGES if is_gemma else QWEN_STAGES

    # Classify all features
    category_counts = defaultdict(int)
    layer_category_counts = defaultdict(lambda: defaultdict(int))
    seen = set()
    for feat in all_features:
        if feat['label'] not in seen:
            seen.add(feat['label'])
            cat = classify_node_semantic(feat['label'], feat['layer'], library, bottleneck_labels)
            category_counts[cat] += 1
            layer_category_counts[feat['layer']][cat] += 1

    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[
            'Semantic Category Distribution',
            'Top Predictions',
            'Bottleneck Features',
            'Semantic Flow by Layer',
            'Cross-Circuit Features',
            'Stage Composition',
        ],
        specs=[
            [{'type': 'pie'}, {'type': 'bar'}, {'type': 'table'}],
            [{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}],
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.08,
    )

    # Panel 1: Category Pie Chart
    cats = sorted(category_counts.items(), key=lambda x: -x[1])
    fig.add_trace(
        go.Pie(
            labels=[c[0].replace('SEMANTICS:', '') for c in cats],
            values=[c[1] for c in cats],
            marker=dict(colors=[SEMANTIC_COLORS.get(c[0], '#BDC3C7') for c in cats]),
            textinfo='label+percent',
            hole=0.3,
        ),
        row=1, col=1,
    )

    # Panel 2: Predictions Bar Chart
    if predictions:
        pred_tokens = [p['token'][:15] for p in predictions[:6]]
        pred_probs = [p['probability'] for p in predictions[:6]]
        pred_colors = ['#2ECC71' if p > 0.5 else '#E74C3C' if p > 0.1 else '#95A5A6'
                      for p in pred_probs]
        fig.add_trace(
            go.Bar(
                x=pred_tokens, y=pred_probs,
                marker_color=pred_colors,
                text=[f'{p:.1%}' for p in pred_probs],
                textposition='outside',
                name='Predictions',
            ),
            row=1, col=2,
        )

    # Panel 3: Bottleneck Features Table
    bn_data = []
    for label in sorted(bottleneck_labels):
        info = get_feature_semantic_info(label, library)
        bn_data.append({
            'Feature': label,
            'Explanation': (info.get('explanation', 'N/A'))[:40],
            'Cross-Circuit': str(info.get('circuits_count', 0)),
        })

    if bn_data:
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Feature', 'Explanation', 'X-Circuit'],
                    fill_color='#3498DB',
                    font=dict(color='white', size=10),
                    align='left',
                ),
                cells=dict(
                    values=[
                        [d['Feature'] for d in bn_data[:10]],
                        [d['Explanation'] for d in bn_data[:10]],
                        [d['Cross-Circuit'] for d in bn_data[:10]],
                    ],
                    fill_color='#ECF0F1',
                    font=dict(size=9),
                    align='left',
                    height=25,
                ),
            ),
            row=1, col=3,
        )

    # Panel 4: Semantic Flow by Layer (Stacked Bar)
    categories_ordered = ['SYNTAX', 'SEMANTICS:CODE', 'SEMANTICS:CONCEPT',
                         'SEMANTICS:GEOGRAPHIC', 'POLYSEMANTIC', 'BOTTLENECK', 'UNKNOWN']
    layers_with_data = sorted(layer_category_counts.keys())

    for cat in categories_ordered:
        values = [layer_category_counts[l].get(cat, 0) for l in layers_with_data]
        if sum(values) > 0:
            fig.add_trace(
                go.Bar(
                    x=[f'L{l}' for l in layers_with_data],
                    y=values,
                    name=cat.replace('SEMANTICS:', ''),
                    marker_color=SEMANTIC_COLORS.get(cat, '#BDC3C7'),
                    showlegend=True,
                ),
                row=2, col=1,
            )

    # barmode applies globally in plotly

    # Panel 5: Cross-Circuit Feature Frequency
    cross = library.get('cross_circuit_features', {})
    cross_sorted = sorted(cross.items(), key=lambda x: -x[1].get('circuits_appeared_in', 0))[:15]
    if cross_sorted:
        fig.add_trace(
            go.Bar(
                x=[c[0] for c in cross_sorted],
                y=[c[1]['circuits_appeared_in'] for c in cross_sorted],
                marker_color='#9B59B6',
                name='Circuit Count',
            ),
            row=2, col=2,
        )

    # Panel 6: Stage Composition
    stage_names = list(stages.keys())
    for cat in ['SYNTAX', 'SEMANTICS:CODE', 'SEMANTICS:CONCEPT', 'BOTTLENECK']:
        values = []
        for stage_name, (start, end) in stages.items():
            count = sum(
                layer_category_counts[l].get(cat, 0)
                for l in range(start, end + 1)
            )
            values.append(count)
        if sum(values) > 0:
            fig.add_trace(
                go.Bar(
                    x=stage_names,
                    y=values,
                    name=cat.replace('SEMANTICS:', ''),
                    marker_color=SEMANTIC_COLORS.get(cat, '#BDC3C7'),
                    showlegend=False,
                ),
                row=2, col=3,
            )

    fig.update_layout(
        title=dict(
            text=f'Semantic Dashboard: "{prompt}" ({model.upper()})',
            font=dict(size=18),
        ),
        height=900,
        width=1600,
        showlegend=True,
        template='plotly_white',
        barmode='stack',
    )

    output_path = output_dir / 'semantic_dashboard.html'
    fig.write_html(str(output_path), include_plotlyjs=True)
    print(f"  [4] semantic_dashboard.html")
    return output_path


# ========================================================================
# MAIN
# ========================================================================

def process_circuit(circuit_dir: Path, library: Dict, output_dir: Path):
    """Process a single circuit directory."""
    circuit_name = circuit_dir.name
    print(f"\n{'='*60}")
    print(f"Processing: {circuit_name}")
    print(f"{'='*60}")

    # Load data
    traceback_data = load_traceback_data(circuit_dir)
    if not traceback_data:
        print(f"  SKIP - no traceback_paths.json")
        return

    graph_data = load_converted_graph(circuit_dir)
    if not graph_data:
        print(f"  SKIP - no converted_graph.json")
        return

    # Create output dir for this circuit
    circuit_output = output_dir / circuit_name
    circuit_output.mkdir(parents=True, exist_ok=True)

    # Generate all 4 visualizations
    create_semantic_circuit_overview(circuit_dir, traceback_data, graph_data, library, circuit_output)
    create_thought_progression_diagram(circuit_dir, traceback_data, graph_data, library, circuit_output)
    create_interactive_circuit(circuit_dir, traceback_data, graph_data, library, circuit_output)
    create_semantic_dashboard(circuit_dir, traceback_data, graph_data, library, circuit_output)


def main():
    parser = argparse.ArgumentParser(description='Stage 2: Enhanced Visualizations')
    parser.add_argument('--circuit', type=str, help='Specific circuit directory to process')
    parser.add_argument('--all', action='store_true', help='Process all circuits with traceback data')
    args = parser.parse_args()

    print("=" * 80)
    print("STAGE 2: ENHANCED SEMANTIC VISUALIZATIONS")
    print("=" * 80)

    # Load bottleneck library
    library = load_bottleneck_library()
    print(f"Loaded bottleneck library: {library.get('metadata', {}).get('total_unique_features', 0)} features")

    output_dir = DATA_DIR / 'stage_2_visualizations'
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.circuit:
        circuit_dir = Path(args.circuit)
        if not circuit_dir.is_absolute():
            circuit_dir = PROMPTS_DIR / args.circuit
        process_circuit(circuit_dir, library, output_dir)
    elif args.all:
        # Process all circuits with traceback data
        for tb_file in sorted(PROMPTS_DIR.rglob('traceback_paths.json')):
            if 'bottom' in tb_file.name:
                continue
            circuit_dir = tb_file.parent.parent
            process_circuit(circuit_dir, library, output_dir)
    else:
        # Default: process one GEMMA and one QWEN circuit
        default_circuits = [
            'gemma-2-2b_the-southern-most-us-state-is',
            'qwen3-4b_im-endthe-southern-most-us-state-is',
            'gemma-2-2b_paris-is-the-capital-of',
            'qwen3-4b_im-endthe-capital-of-france-is',
        ]
        for circuit_name in default_circuits:
            circuit_dir = PROMPTS_DIR / circuit_name
            if circuit_dir.exists():
                process_circuit(circuit_dir, library, output_dir)

    print(f"\n{'='*80}")
    print(f"STAGE 2 COMPLETE!")
    print(f"{'='*80}")
    print(f"Output: {output_dir}/")


if __name__ == '__main__':
    main()
