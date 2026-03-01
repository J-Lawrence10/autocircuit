#!/usr/bin/env python3
"""Supernode Pipeline: End-to-end automated supernode detection for Neuronpedia circuit graphs.

Takes a text prompt, generates an attribution graph via Neuronpedia API, detects
communities (supernodes) using multi-algorithm graph community detection, labels them
with Neuronpedia feature explanations, and outputs a ready-to-upload annotated JSON.

Usage:
    python scripts/supernode_pipeline.py "The capital of France is"
    python scripts/supernode_pipeline.py "Water boils at 100 degrees" --model gemma-2-2b
    python scripts/supernode_pipeline.py --raw-graph path/to/raw_graph.json

Output:
    output/{model}_{prompt_slug}/
        annotated_graph.json        <- upload to neuronpedia.org/graph/validator
        supernode_report.md         <- human-readable analysis
        community_visualization.png <- colored community layout
        raw_graph.json              <- original unmodified graph
"""

import json
import sys
import io
import time
import math
import argparse
import re
import yaml
import requests
from pathlib import Path
from collections import Counter, defaultdict

import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
CONFIG_PATH = BASE_DIR / 'config' / 'neuronpedia_config.yaml'
OUTPUT_DIR = BASE_DIR / 'output'

# Model configs
MODEL_CONFIGS = {
    'gemma-2-2b': {
        'source_set': 'gemmascope-transcoder-16k',
        'sae_template': '{layer}-gemmascope-transcoder-16k',
        'features_per_sae': 16384,
        'num_layers': 26,
    },
    'qwen3-4b': {
        'source_set': None,  # Feature API not available
        'sae_template': None,
        'features_per_sae': 16384,
        'num_layers': 36,
    },
}


# =============================================================================
#  UTILITIES
# =============================================================================

def load_api_key():
    """Load API key from config."""
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return config['api']['api_key']


def slugify(text, max_len=40):
    """Convert text to URL-friendly slug."""
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower().strip())
    return slug[:max_len].strip('-')


# =============================================================================
#  STEP 1: GRAPH GENERATION
# =============================================================================

def generate_graph(api_key, prompt, model_id='gemma-2-2b'):
    """Step 1: Generate attribution graph via Neuronpedia API.

    Returns (raw_graph_dict, slug) or raises on failure.
    """
    print(f"\n  [Step 1] Generating attribution graph...")
    print(f"  Prompt: \"{prompt}\"")
    print(f"  Model: {model_id}")

    payload = {
        'prompt': prompt,
        'modelId': model_id,
    }

    # Add source set for supported models
    mc = MODEL_CONFIGS.get(model_id, {})
    if mc.get('source_set'):
        payload['sourceSetName'] = mc['source_set']

    resp = requests.post(
        'https://www.neuronpedia.org/api/graph/generate',
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=120,
    )

    if resp.status_code != 200:
        raise RuntimeError(
            f"Graph generation failed ({resp.status_code}): {resp.text[:300]}")

    data = resp.json()
    s3_url = data.get('s3url', '')
    slug = ''
    url = data.get('url', '')
    if 'slug=' in url:
        slug = url.split('slug=')[-1].split('&')[0]

    if not s3_url:
        raise RuntimeError("No S3 URL returned from graph generation")

    print(f"  Slug: {slug}")
    print(f"  Downloading graph from S3...")

    s3_resp = requests.get(s3_url, timeout=60)
    if s3_resp.status_code != 200:
        raise RuntimeError(f"S3 download failed ({s3_resp.status_code})")

    graph = s3_resp.json()
    n_nodes = len(graph.get('nodes', []))
    n_links = len(graph.get('links', []))
    print(f"  Downloaded: {n_nodes} nodes, {n_links} links")

    return graph, slug


# =============================================================================
#  STEP 2: COMMUNITY DETECTION
# =============================================================================

def build_graph(raw_graph):
    """Build NetworkX DiGraph from raw Neuronpedia graph JSON.

    Filters out embedding nodes (layer="E") and error nodes (feature=-1).
    Returns (nx.DiGraph, filtered_node_ids set).
    """
    G = nx.DiGraph()

    valid_nodes = set()
    for node in raw_graph.get('nodes', []):
        layer = node.get('layer', '')
        feature = node.get('feature', -1)
        # Skip embedding and error nodes for community detection
        if layer == 'E' or feature == -1:
            continue
        nid = node['node_id']
        valid_nodes.add(nid)

        layer_int = int(layer) if layer.isdigit() else 0
        G.add_node(nid,
                    layer=layer_int,
                    feature=feature,
                    activation=node.get('activation', 0.0),
                    influence=node.get('influence', 0.0),
                    ctx_idx=node.get('ctx_idx', 0),
                    feature_type=node.get('feature_type', ''))

    for link in raw_graph.get('links', []):
        src = link['source']
        tgt = link['target']
        if src in valid_nodes and tgt in valid_nodes:
            G.add_edge(src, tgt, weight=abs(link.get('weight', 0.0)))

    return G, valid_nodes


def _count_singletons(partition):
    """Count communities with only 1 member."""
    counts = Counter(partition.values())
    return sum(1 for c in counts.values() if c == 1)


def _postprocess_communities(partition, G, min_size=3, max_pct=0.30):
    """Merge small communities into nearest neighbor by edge weight."""
    communities = defaultdict(list)
    for node, comm in partition.items():
        communities[comm].append(node)

    new_partition = dict(partition)

    # Merge small communities into nearest neighbor
    for comm_id, members in list(communities.items()):
        if len(members) < min_size:
            for node in members:
                neighbor_comms = Counter()
                for neighbor in G.predecessors(node):
                    if neighbor in new_partition and new_partition[neighbor] != comm_id:
                        neighbor_comms[new_partition[neighbor]] += 1
                for neighbor in G.successors(node):
                    if neighbor in new_partition and new_partition[neighbor] != comm_id:
                        neighbor_comms[new_partition[neighbor]] += 1

                if neighbor_comms:
                    best_neighbor = neighbor_comms.most_common(1)[0][0]
                    new_partition[node] = best_neighbor

    # Renumber communities to be contiguous (0, 1, 2, ...)
    unique_comms = sorted(set(new_partition.values()))
    remap = {old: new for new, old in enumerate(unique_comms)}
    new_partition = {node: remap[comm] for node, comm in new_partition.items()}

    return new_partition


def _layer_based_grouping(G):
    """Fallback: group by layer ranges for small graphs."""
    partition = {}
    for node, data in G.nodes(data=True):
        layer = data.get('layer', 0)
        if layer <= 5:
            partition[node] = 0  # input
        elif layer <= 15:
            partition[node] = 1  # processing
        else:
            partition[node] = 2  # output

    return {
        'partition': partition,
        'best_algorithm': 'layer_grouping',
        'all_results': {},
    }


def detect_communities(G, min_size=3, max_pct=0.30):
    """Step 2: Run multi-algorithm community detection.

    Returns dict with best partition and algorithm comparison.
    """
    import community as community_louvain

    print(f"\n  [Step 2] Detecting communities...")
    print(f"  Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    if G.number_of_nodes() < 20:
        print(f"  Small graph (<20 nodes), using layer-based grouping")
        return _layer_based_grouping(G)

    # Convert to undirected for community detection
    G_undirected = G.to_undirected()

    results = {}

    # 1. Louvain
    try:
        partition_louvain = community_louvain.best_partition(
            G_undirected, resolution=2.0, random_state=42)
        mod_louvain = community_louvain.modularity(partition_louvain, G_undirected)
        n_comms = len(set(partition_louvain.values()))
        results['louvain'] = {
            'partition': partition_louvain,
            'modularity': mod_louvain,
            'n_communities': n_comms,
        }
        print(f"    Louvain: {n_comms} communities, modularity={mod_louvain:.4f}")
    except Exception as e:
        print(f"    Louvain failed: {e}")

    # 2. Leiden
    try:
        import igraph as ig
        import leidenalg

        mapping = {n: i for i, n in enumerate(G_undirected.nodes())}
        reverse_mapping = {i: n for n, i in mapping.items()}
        edges = [(mapping[u], mapping[v]) for u, v in G_undirected.edges()]
        ig_graph = ig.Graph(n=len(mapping), edges=edges, directed=False)

        leiden_part = leidenalg.find_partition(
            ig_graph, leidenalg.ModularityVertexPartition, seed=42)
        mod_leiden = leiden_part.modularity

        partition_leiden = {}
        for comm_id, members in enumerate(leiden_part):
            for idx in members:
                partition_leiden[reverse_mapping[idx]] = comm_id

        n_comms = len(leiden_part)
        results['leiden'] = {
            'partition': partition_leiden,
            'modularity': mod_leiden,
            'n_communities': n_comms,
        }
        print(f"    Leiden: {n_comms} communities, modularity={mod_leiden:.4f}")
    except Exception as e:
        print(f"    Leiden failed: {e}")

    # 3. Greedy Modularity
    try:
        greedy_comms = list(
            nx.community.greedy_modularity_communities(G_undirected))
        partition_greedy = {}
        for comm_id, members in enumerate(greedy_comms):
            for node in members:
                partition_greedy[node] = comm_id
        mod_greedy = nx.community.modularity(G_undirected, greedy_comms)

        n_comms = len(greedy_comms)
        results['greedy'] = {
            'partition': partition_greedy,
            'modularity': mod_greedy,
            'n_communities': n_comms,
        }
        print(f"    Greedy: {n_comms} communities, modularity={mod_greedy:.4f}")
    except Exception as e:
        print(f"    Greedy failed: {e}")

    if not results:
        print(f"  All algorithms failed, falling back to layer grouping")
        return _layer_based_grouping(G)

    # Select best by modularity (tie-break: fewer singletons)
    best_name = max(results, key=lambda k: (
        results[k]['modularity'],
        -_count_singletons(results[k]['partition'])
    ))
    best = results[best_name]

    print(f"  Best: {best_name} (modularity={best['modularity']:.4f})")

    # Post-process: merge small communities
    partition = _postprocess_communities(
        best['partition'], G, min_size=min_size, max_pct=max_pct)

    n_final = len(set(partition.values()))
    print(f"  After post-processing: {n_final} communities")

    return {
        'partition': partition,
        'best_algorithm': best_name,
        'all_results': {k: {'modularity': v['modularity'],
                            'n_communities': v['n_communities']}
                        for k, v in results.items()},
    }


# =============================================================================
#  STEP 3: BOTTLENECK IDENTIFICATION
# =============================================================================

def identify_bottlenecks(G, partition, top_n=10):
    """Step 3: Identify bottleneck nodes via betweenness centrality.

    Returns dict with bottleneck nodes and community flags.
    """
    print(f"\n  [Step 3] Identifying bottlenecks...")

    # Compute betweenness centrality (sample for large graphs)
    if G.number_of_nodes() > 500:
        bc = nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()))
    else:
        bc = nx.betweenness_centrality(G)

    # Top bottleneck nodes
    sorted_bc = sorted(bc.items(), key=lambda x: x[1], reverse=True)[:top_n]
    bottleneck_nodes = [nid for nid, _ in sorted_bc]

    # Flag communities containing 2+ bottleneck nodes
    bottleneck_communities = set()
    comm_bottleneck_count = Counter()
    for nid in bottleneck_nodes:
        if nid in partition:
            comm_bottleneck_count[partition[nid]] += 1

    for comm_id, count in comm_bottleneck_count.items():
        if count >= 2:
            bottleneck_communities.add(comm_id)

    print(f"  Top {len(sorted_bc)} bottleneck nodes identified")
    print(f"  Bottleneck communities: {len(bottleneck_communities)}")

    for nid, score in sorted_bc[:5]:
        layer = G.nodes[nid].get('layer', '?')
        feature = G.nodes[nid].get('feature', '?')
        comm = partition.get(nid, '?')
        print(f"    L{layer}_F{feature} (betweenness={score:.4f}, community={comm})")

    # Optional: check bottleneck library
    library_info = {}
    lib_path = BASE_DIR / 'data' / 'stage_1_5_bottleneck_library.json'
    if lib_path.exists():
        try:
            with open(lib_path, 'r', encoding='utf-8') as f:
                lib = json.load(f)
            ccf = lib.get('cross_circuit_features', {})

            for nid in bottleneck_nodes:
                feature = G.nodes[nid].get('feature', -1)
                layer = G.nodes[nid].get('layer', -1)
                for feat_label, feat_data in ccf.items():
                    if (feat_data.get('np_id') == feature
                            and feat_data.get('layer') == layer):
                        library_info[nid] = {
                            'label': feat_label,
                            'circuits_appeared_in': feat_data.get(
                                'circuits_appeared_in', 0),
                            'explanation': feat_data.get('explanation', ''),
                        }
                        break

            if library_info:
                print(f"  Library matches: {len(library_info)} features found")
        except Exception as e:
            print(f"  Library lookup skipped: {e}")

    return {
        'bottleneck_nodes': bottleneck_nodes,
        'betweenness': dict(sorted_bc),
        'bottleneck_communities': bottleneck_communities,
        'library_info': library_info,
    }


# =============================================================================
#  STEP 4: SEMANTIC LABELING
# =============================================================================

def fetch_feature_explanation(api_key, model_id, layer, np_id, rate_delay=0.5):
    """Fetch a single feature explanation from Neuronpedia API."""
    mc = MODEL_CONFIGS.get(model_id, {})
    if not mc.get('sae_template'):
        return None

    sae_path = mc['sae_template'].format(layer=layer)
    url = f"https://neuronpedia.org/api/feature/{model_id}/{sae_path}/{np_id}"

    try:
        resp = requests.get(
            url, headers={'X-Api-Key': api_key}, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            explanations = data.get('explanations', [{}])
            if explanations:
                desc = explanations[0].get('description', '')
                time.sleep(rate_delay)
                return desc
        elif resp.status_code == 429:
            print(f"      [RATE LIMITED] Waiting 60s...")
            time.sleep(60)
            return fetch_feature_explanation(
                api_key, model_id, layer, np_id, rate_delay)
    except Exception:
        pass

    time.sleep(rate_delay)
    return None


def _summarize_explanations(explanations, layer_str, n_nodes):
    """Find common theme across explanations via keyword overlap."""
    if not explanations or len(explanations) < 2:
        return None

    stopwords = {'the', 'and', 'for', 'that', 'with', 'this', 'are', 'was',
                 'were', 'been', 'from', 'have', 'has', 'had', 'not', 'but',
                 'its', 'such', 'related', 'including', 'particularly', 'often',
                 'also', 'various', 'specific', 'certain'}

    word_sets = []
    for exp in explanations:
        words = set(w.lower() for w in re.findall(r'\b\w{3,}\b', exp))
        words -= stopwords
        word_sets.append(words)

    # Find words appearing in 2+ explanations
    all_words = Counter()
    for ws in word_sets:
        for w in ws:
            all_words[w] += 1

    common = [w for w, c in all_words.most_common(5) if c >= 2]

    if common:
        theme = ' / '.join(common[:3])
        return f"{theme} ({layer_str})"

    # Fallback: use shortest explanation
    shortest = min(explanations, key=len)
    if len(shortest) > 30:
        shortest = shortest[:27] + '...'
    return f"{shortest} ({layer_str})"


def _direct_label(explanation, layer_str, n_nodes):
    """Use top feature explanation directly."""
    if not explanation:
        return None

    exp = explanation.strip()
    if len(exp) > 35:
        exp = exp[:32] + '...'

    return f"{exp} ({layer_str})"


def label_communities(G, partition, bottleneck_info, api_key, model_id,
                      max_label_len=50, rate_delay=0.5):
    """Step 4: Generate semantic labels for each community.

    Runs two strategies: top-3 summarization and top-1 direct.
    Returns dict mapping community_id -> label info.
    """
    print(f"\n  [Step 4] Labeling communities...")

    mc = MODEL_CONFIGS.get(model_id, {})
    has_feature_api = mc.get('sae_template') is not None

    # Group nodes by community
    communities = defaultdict(list)
    for node, comm in partition.items():
        communities[comm].append(node)

    labels = {}
    api_calls = 0

    for comm_id in sorted(communities.keys()):
        members = communities[comm_id]

        # Get layer range
        layers = [G.nodes[n].get('layer', 0)
                  for n in members if n in G.nodes]
        min_layer = min(layers) if layers else 0
        max_layer = max(layers) if layers else 0
        layer_str = (f"L{min_layer}" if min_layer == max_layer
                     else f"L{min_layer}-L{max_layer}")

        # Rank by influence (handle None values)
        ranked = sorted(
            members,
            key=lambda n: (G.nodes[n].get('influence') or 0) if n in G.nodes else 0,
            reverse=True)

        is_bottleneck = comm_id in bottleneck_info.get(
            'bottleneck_communities', set())

        explanations = []

        if has_feature_api:
            for node in ranked[:3]:
                if node not in G.nodes:
                    continue
                layer = G.nodes[node].get('layer', 0)
                feature = G.nodes[node].get('feature', 0)
                np_id = feature  # In raw graph, feature IS the NP id

                explanation = fetch_feature_explanation(
                    api_key, model_id, layer, np_id, rate_delay)
                api_calls += 1

                if explanation:
                    explanations.append(explanation)

                if api_calls % 10 == 0:
                    print(f"    ({api_calls} API calls...)")

        # Generate labels with both strategies
        strategy1_label = _summarize_explanations(
            explanations, layer_str, len(members))
        strategy2_label = _direct_label(
            explanations[0] if explanations else None,
            layer_str, len(members))

        # Pick best
        if strategy1_label and len(explanations) >= 2:
            chosen_label = strategy1_label
            chosen_strategy = 'top3'
        elif strategy2_label:
            chosen_label = strategy2_label
            chosen_strategy = 'top1'
        else:
            bn_tag = ', bottleneck' if is_bottleneck else ''
            chosen_label = f"{layer_str} cluster ({len(members)} nodes{bn_tag})"
            chosen_strategy = 'structural'

        # Truncate
        if len(chosen_label) > max_label_len:
            chosen_label = chosen_label[:max_label_len - 3] + '...'

        labels[comm_id] = {
            'label': chosen_label,
            'strategy': chosen_strategy,
            'strategy1_label': strategy1_label,
            'strategy2_label': strategy2_label,
            'n_nodes': len(members),
            'layer_range': layer_str,
            'is_bottleneck': is_bottleneck,
            'explanations': explanations,
        }

        bn_marker = ' [BN]' if is_bottleneck else ''
        print(f"    Community {comm_id}: \"{chosen_label}\"{bn_marker} "
              f"({chosen_strategy}, {len(members)} nodes)")

    print(f"  Total API calls: {api_calls}")
    return labels


# =============================================================================
#  STEP 5: EXPORT & VISUALIZATION
# =============================================================================

def export_annotated_graph(raw_graph, partition, labels, bottleneck_info,
                           output_dir):
    """Step 5a: Inject supernodes into qParams and export annotated JSON."""
    print(f"\n  [Step 5] Exporting annotated graph...")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Build supernodes array for qParams
    communities = defaultdict(list)
    for node, comm in partition.items():
        communities[comm].append(node)

    supernodes = []
    for comm_id in sorted(communities.keys()):
        label_info = labels.get(comm_id, {})
        label = label_info.get('label', f'Community {comm_id}')
        members = communities[comm_id]
        supernodes.append([label] + members)

    # Build pinnedIds from bottleneck nodes
    pinned_ids = bottleneck_info.get('bottleneck_nodes', [])[:10]

    # Inject into graph (shallow copy preserves nodes/links)
    annotated = dict(raw_graph)
    annotated['qParams'] = {
        'pinnedIds': pinned_ids,
        'supernodes': supernodes,
        'linkType': 'both',
        'clickedId': '',
        'sg_pos': '',
    }

    # Save annotated graph
    annotated_path = output_dir / 'annotated_graph.json'
    with open(annotated_path, 'w', encoding='utf-8') as f:
        json.dump(annotated, f, indent=2, ensure_ascii=False)

    size_mb = annotated_path.stat().st_size / (1024 * 1024)
    print(f"  Saved: {annotated_path.name} ({size_mb:.1f} MB)")
    print(f"  Supernodes: {len(supernodes)}")
    print(f"  Pinned nodes: {len(pinned_ids)}")

    return annotated_path


def generate_report(partition, labels, bottleneck_info, community_results,
                    prompt, model_id, output_dir):
    """Step 5b: Generate human-readable supernode report."""
    report_path = output_dir / 'supernode_report.md'

    best_algo = community_results.get('best_algorithm', 'unknown')
    all_results = community_results.get('all_results', {})

    lines = []
    lines.append(f"# Supernode Analysis Report\n\n")
    lines.append(f"**Prompt:** \"{prompt}\"\n\n")
    lines.append(f"**Model:** {model_id}\n\n")
    lines.append(f"**Algorithm:** {best_algo}\n\n")
    lines.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    lines.append(f"---\n\n")
    lines.append(f"## Communities Found: {len(labels)}\n\n")
    lines.append(f"| # | Label (Chosen) | Strategy | Nodes | Layers | Bottleneck |\n")
    lines.append(f"|---|----------------|----------|-------|--------|------------|\n")

    for comm_id in sorted(labels.keys()):
        info = labels[comm_id]
        bn = 'Yes' if info.get('is_bottleneck') else 'No'
        lines.append(
            f"| {comm_id} | {info['label']} | {info['strategy']} | "
            f"{info['n_nodes']} | {info['layer_range']} | {bn} |\n"
        )

    # Algorithm comparison
    if all_results:
        lines.append(f"\n## Algorithm Comparison\n\n")
        lines.append(f"| Algorithm | Modularity | Communities |\n")
        lines.append(f"|-----------|-----------|-------------|\n")
        for algo, res in sorted(all_results.items()):
            lines.append(
                f"| {algo} | {res['modularity']:.4f} | "
                f"{res['n_communities']} |\n")

    # Label strategy comparison
    lines.append(f"\n## Label Strategy Comparison\n\n")
    lines.append(f"| # | Top-3 Summary | Top-1 Direct |\n")
    lines.append(f"|---|---------------|--------------|\n")
    for comm_id in sorted(labels.keys()):
        info = labels[comm_id]
        s1 = info.get('strategy1_label') or 'N/A'
        s2 = info.get('strategy2_label') or 'N/A'
        lines.append(f"| {comm_id} | {s1} | {s2} |\n")

    # Bottleneck nodes
    lines.append(f"\n## Bottleneck Nodes (pinned)\n\n")
    for nid, score in list(bottleneck_info.get('betweenness', {}).items())[:10]:
        lib = bottleneck_info.get('library_info', {}).get(nid, {})
        lib_note = ""
        if lib:
            lib_note = (f" -- {lib['label']} "
                        f"({lib['circuits_appeared_in']} circuits)")
        lines.append(f"- {nid} (betweenness={score:.4f}){lib_note}\n")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(''.join(lines))

    print(f"  Report: {report_path.name}")


def generate_visualization(G, partition, labels, bottleneck_info, output_dir,
                           max_nodes=200):
    """Step 5c: Generate community visualization PNG."""
    print(f"  Generating visualization...")

    viz_path = output_dir / 'community_visualization.png'

    # Select top nodes by influence (handle None)
    node_influences = {n: (G.nodes[n].get('influence') or 0) for n in G.nodes()}
    top_nodes = sorted(
        node_influences, key=node_influences.get, reverse=True)[:max_nodes]

    G_sub = G.subgraph(top_nodes).copy()

    if G_sub.number_of_nodes() == 0:
        print(f"  No nodes to visualize, skipping")
        return

    n_comms = max(len(set(partition.values())), 1)
    cmap = plt.cm.get_cmap('tab20', max(n_comms, 2))

    bottleneck_set = set(bottleneck_info.get('bottleneck_nodes', []))

    fig, ax = plt.subplots(1, 1, figsize=(16, 12))

    # Layout
    k_val = 2.0 / math.sqrt(max(G_sub.number_of_nodes(), 1))
    pos = nx.spring_layout(G_sub, k=k_val, iterations=50, seed=42)

    # Draw edges
    nx.draw_networkx_edges(G_sub, pos, alpha=0.05, arrows=False, ax=ax)

    # Draw regular nodes
    regular_nodes = [n for n in G_sub.nodes() if n not in bottleneck_set]
    if regular_nodes:
        regular_colors = [cmap(partition.get(n, 0) % 20) for n in regular_nodes]
        regular_sizes = [
            max(10, (G_sub.nodes[n].get('influence') or 0.5) * 100)
            for n in regular_nodes]
        nx.draw_networkx_nodes(
            G_sub, pos, nodelist=regular_nodes,
            node_color=regular_colors, node_size=regular_sizes,
            alpha=0.7, ax=ax)

    # Draw bottleneck nodes with star marker
    bn_in_graph = [n for n in G_sub.nodes() if n in bottleneck_set]
    if bn_in_graph:
        bn_colors = [cmap(partition.get(n, 0) % 20) for n in bn_in_graph]
        bn_sizes = [
            max(30, (G_sub.nodes[n].get('influence') or 0.5) * 300)
            for n in bn_in_graph]
        nx.draw_networkx_nodes(
            G_sub, pos, nodelist=bn_in_graph,
            node_color=bn_colors, node_size=bn_sizes,
            node_shape='*', alpha=0.9, ax=ax,
            edgecolors='red', linewidths=2)

    # Legend
    legend_patches = []
    active_comms = sorted(set(partition.get(n, 0) for n in G_sub.nodes()))
    for comm_id in active_comms:
        label_info = labels.get(comm_id, {})
        label = label_info.get('label', f'Community {comm_id}')
        color = cmap(comm_id % 20)
        legend_patches.append(mpatches.Patch(color=color, label=label))

    legend_patches.append(plt.Line2D(
        [0], [0], marker='*', color='w',
        markerfacecolor='gray', markersize=15,
        markeredgecolor='red', label='Bottleneck node'))

    ax.legend(handles=legend_patches, loc='upper left', fontsize=7,
              bbox_to_anchor=(1.01, 1), borderaxespad=0)

    ax.set_title(
        f'Community Structure\n'
        f'(top {G_sub.number_of_nodes()} nodes by influence)',
        fontsize=12)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(viz_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  Visualization: {viz_path.name}")


# =============================================================================
#  MAIN ORCHESTRATOR
# =============================================================================

def run_pipeline(prompt, model_id='gemma-2-2b', skip_generation=False,
                 raw_graph_path=None, rate_delay=0.5):
    """Run the full supernode pipeline."""

    print("=" * 70)
    print("  SUPERNODE PIPELINE")
    print("=" * 70)
    print(f"  Prompt: \"{prompt}\"")
    print(f"  Model: {model_id}")

    api_key = load_api_key()
    prompt_slug = slugify(prompt)
    output_dir = OUTPUT_DIR / f"{model_id}_{prompt_slug}"

    # Step 1: Generate or load graph
    if raw_graph_path:
        print(f"\n  [Step 1] Loading graph from: {raw_graph_path}")
        with open(raw_graph_path, 'r', encoding='utf-8') as f:
            raw_graph = json.load(f)
        slug = raw_graph.get('metadata', {}).get('slug', 'local')
    elif skip_generation and (output_dir / 'raw_graph.json').exists():
        print(f"\n  [Step 1] Loading cached graph...")
        with open(output_dir / 'raw_graph.json', 'r', encoding='utf-8') as f:
            raw_graph = json.load(f)
        slug = raw_graph.get('metadata', {}).get('slug', 'cached')
    else:
        raw_graph, slug = generate_graph(api_key, prompt, model_id)
        # Cache raw graph
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / 'raw_graph.json', 'w', encoding='utf-8') as f:
            json.dump(raw_graph, f, indent=2, ensure_ascii=False)

    # Step 2: Build graph and detect communities
    G, valid_nodes = build_graph(raw_graph)
    community_results = detect_communities(G)
    partition = community_results['partition']

    # Step 3: Identify bottlenecks
    bottleneck_info = identify_bottlenecks(G, partition)

    # Step 4: Label communities
    labels = label_communities(
        G, partition, bottleneck_info, api_key, model_id,
        rate_delay=rate_delay)

    # Step 5: Export
    annotated_path = export_annotated_graph(
        raw_graph, partition, labels, bottleneck_info, output_dir)

    generate_report(
        partition, labels, bottleneck_info, community_results,
        prompt, model_id, output_dir)

    generate_visualization(
        G, partition, labels, bottleneck_info, output_dir)

    # Save raw graph if not already cached
    raw_save_path = output_dir / 'raw_graph.json'
    if not raw_save_path.exists():
        with open(raw_save_path, 'w', encoding='utf-8') as f:
            json.dump(raw_graph, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"  PIPELINE COMPLETE")
    print(f"{'=' * 70}")
    print(f"  Output: {output_dir}")
    print(f"  Files:")
    print(f"    annotated_graph.json  <- upload to Neuronpedia")
    print(f"    supernode_report.md   <- human-readable summary")
    print(f"    community_visualization.png")
    print(f"  Validate at: https://neuronpedia.org/graph/validator")
    print(f"{'=' * 70}")

    return {
        'output_dir': str(output_dir),
        'annotated_graph': str(annotated_path),
        'n_communities': len(labels),
        'algorithm': community_results.get('best_algorithm'),
        'slug': slug,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Supernode Pipeline: automated supernode detection '
                    'for Neuronpedia circuit graphs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scripts/supernode_pipeline.py "The capital of France is"
  python scripts/supernode_pipeline.py "Water boils at 100" --model gemma-2-2b
  python scripts/supernode_pipeline.py --raw-graph path/to/raw_graph.json
        '''
    )
    parser.add_argument('prompt', nargs='?', help='The prompt to analyze')
    parser.add_argument('--model', default='gemma-2-2b',
                        help='Model ID (default: gemma-2-2b)')
    parser.add_argument('--raw-graph', type=str, default=None,
                        help='Path to existing raw graph JSON (skips generation)')
    parser.add_argument('--skip-generation', action='store_true',
                        help='Skip generation if cached raw_graph.json exists')
    parser.add_argument('--rate-delay', type=float, default=0.5,
                        help='Delay between feature API calls (default: 0.5s)')

    args = parser.parse_args()

    if not args.prompt and not args.raw_graph:
        parser.error("Either provide a prompt or --raw-graph path")

    prompt = args.prompt or "unknown"

    # If raw-graph provided without prompt, extract from metadata
    if args.raw_graph and not args.prompt:
        with open(args.raw_graph, 'r', encoding='utf-8') as f:
            rg = json.load(f)
        prompt = rg.get('metadata', {}).get('prompt', 'unknown')

    run_pipeline(
        prompt=prompt,
        model_id=args.model,
        raw_graph_path=args.raw_graph,
        skip_generation=args.skip_generation,
        rate_delay=args.rate_delay,
    )
