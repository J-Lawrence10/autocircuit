# Traceback Graphing: Attribution Path Analysis for Top-K Predictions

**Date**: January 28, 2026
**Concept Author**: User
**Status**: Proposed Feature

---

## Core Idea

**"We take the outputs and work back, graphing the thought process that determined each one. We do this for the top 5 outputs."**

---

## What Is Traceback Graphing?

### Traditional Analysis
Current pipeline shows:
- ✓ Circuit structure (all nodes, all edges)
- ✓ Supernode communities
- ✓ Overall information flow

**Problem**: Doesn't explain WHY each specific prediction was made.

### Traceback Graphing
For each top-K prediction:
1. Start at the output token logit
2. Trace backward through the circuit
3. Identify which features/edges contributed
4. Visualize the "reasoning path" for that specific prediction

---

## Example: President Lives In

### Model Outputs
```
1. " the" (65.0%)      ← Why did this win?
2. " a" (21.7%)        ← What path led here?
3. " Washington" (2.9%) ← Why so low?
4. " an" (2.5%)        ← Grammatical variant
5. " " (1.2%)          ← Uncertainty signal
```

### Questions Traceback Can Answer

**For " the" (winner)**:
- Which features contributed most to this prediction?
- What layer made the "decision"?
- Were grammatical features dominant?
- Which input tokens influenced it most?

**For " Washington" (correct but buried)**:
- Which features activated for Washington?
- At what layer did they activate?
- Why did they get low weight?
- What suppressed them?

**Comparison**:
- Do " the" and " Washington" use different circuit paths?
- Where do the paths diverge?
- Can we identify the "fork" where grammar beat facts?

---

## Technical Approach

### Method 1: Gradient-Based Attribution (Integrated Gradients)

**How it works**:
1. Take a specific output logit (e.g., " the")
2. Compute gradient of that logit with respect to all node activations
3. Nodes with high gradient = contributed strongly to that prediction
4. Trace backward from high-gradient nodes to input

**Advantages**:
- ✓ Mathematically grounded
- ✓ Captures nonlinear interactions
- ✓ Standard interpretability technique

**Challenges**:
- ✗ Requires model access (we only have attribution graph)
- ✗ Computationally expensive
- ✗ Noisy gradients in deep networks

### Method 2: Edge Attribution Analysis (Our Current Data)

**How it works**:
1. Start with output token's logit node
2. Find all edges pointing TO that node
3. Weight by edge strength (from attribution graph)
4. Recursively trace high-weight edges backward
5. Build subgraph of "influential path"

**Advantages**:
- ✓ Uses existing attribution graph data
- ✓ No additional model queries needed
- ✓ Fast computation
- ✓ Already have edge weights

**Challenges**:
- ✗ Attribution graph might not capture all contributions
- ✗ Edge weights are already aggregated
- ✗ May miss indirect effects

### Method 3: Activation Path Tracing (Hybrid)

**How it works**:
1. Identify nodes with high activation in output layer
2. For each output token, find which output nodes represent it
3. Trace backward through highest-activation paths
4. Weight by both activation strength AND edge weight
5. Build "critical path" for each prediction

**Advantages**:
- ✓ Combines activation + edge information
- ✓ Uses data we already have
- ✓ Intuitive visualization
- ✓ Shows "hot paths" through circuit

**Challenges**:
- ✗ May oversimplify multi-path contributions
- ✗ Requires heuristic for "critical path" definition

---

## Proposed Implementation

### Step 1: Extend Circuit Analysis

**New data structure**: `token_attribution_paths`

```json
{
  "token_attributions": {
    " the": {
      "probability": 0.65,
      "rank": 1,
      "critical_path": {
        "nodes": [
          {"id": "L25_F1234", "activation": 15.3, "contribution": 0.89},
          {"id": "L22_F5678", "activation": 8.7, "contribution": 0.76},
          {"id": "L18_F9012", "activation": 12.1, "contribution": 0.64},
          ...
        ],
        "edges": [
          {"from": "L18_F9012", "to": "L22_F5678", "weight": 5.2},
          {"from": "L22_F5678", "to": "L25_F1234", "weight": 8.1}
        ],
        "dominant_features": ["syntactic_article", "grammar_pattern"],
        "layer_importance": {
          "L0-L5": 0.12,
          "L6-L10": 0.23,
          "L11-L15": 0.18,
          "L16-L20": 0.31,
          "L21-L25": 0.16
        }
      }
    },
    " Washington": {
      "probability": 0.029,
      "rank": 3,
      "critical_path": {
        "nodes": [
          {"id": "L25_F3456", "activation": 2.1, "contribution": 0.34},
          {"id": "L20_F7890", "activation": 5.8, "contribution": 0.28},
          {"id": "L15_F2345", "activation": 3.2, "contribution": 0.19},
          ...
        ],
        "edges": [...],
        "dominant_features": ["location_geographic", "president_concept"],
        "layer_importance": {...}
      }
    }
  }
}
```

### Step 2: Implement Traceback Algorithm

**Pseudocode**:
```python
def traceback_attribution_path(graph, target_token, top_k_nodes=20):
    """
    Trace backward from target token to identify contributing features

    Args:
        graph: NetworkX graph with nodes and edges
        target_token: Token to analyze (e.g., " the", " Washington")
        top_k_nodes: Number of top contributing nodes to trace

    Returns:
        AttributionPath with critical nodes, edges, and features
    """
    # Step 1: Find output nodes for target token
    output_nodes = find_output_nodes_for_token(graph, target_token)

    # Step 2: Initialize priority queue with output nodes
    pq = [(node, node.activation * node.influence) for node in output_nodes]

    visited = set()
    critical_path = []

    # Step 3: Backward breadth-first search weighted by contribution
    while pq and len(critical_path) < top_k_nodes:
        current_node, contribution = heappop(pq)

        if current_node in visited:
            continue

        visited.add(current_node)
        critical_path.append({
            'node': current_node,
            'contribution': contribution,
            'layer': current_node.layer,
            'activation': current_node.activation
        })

        # Step 4: Add predecessor nodes weighted by edge strength
        for predecessor in graph.predecessors(current_node):
            edge_weight = graph[predecessor][current_node]['weight']
            pred_contribution = contribution * edge_weight * predecessor.activation
            heappush(pq, (predecessor, pred_contribution))

    return build_attribution_path(critical_path, graph)
```

### Step 3: Visualize Comparison

**Visualization**: Side-by-side subgraphs for top-K predictions

```
┌─────────────────────────────────────────────────────────────┐
│         "the" (65%) vs " Washington" (2.9%)                 │
├─────────────────────────┬───────────────────────────────────┤
│   " the" Path           │   " Washington" Path              │
│   (Grammar Dominant)    │   (Facts Suppressed)              │
├─────────────────────────┼───────────────────────────────────┤
│                         │                                   │
│  L25: Output Logit      │  L25: Output Logit                │
│   ↑ (strong)            │   ↑ (weak)                        │
│  L22: Article Features  │  L22: Location Features           │
│   ↑ (strong)            │   ↑ (medium)                      │
│  L18: Syntax Pattern    │  L18: Geographic Concept          │
│   ↑ (strong)            │   ↑ (weak)                        │
│  L12: Grammar Rules     │  L15: President Context           │
│   ↑ (strong)            │   ↑ (medium)                      │
│  L5:  "lives in" phrase │  L10: "United States" entity      │
│   ↑ (strong)            │   ↑ (medium)                      │
│  L0:  Input tokens      │  L0:  Input tokens                │
│                         │                                   │
└─────────────────────────┴───────────────────────────────────┘

Key Insight: " the" has stronger connections at EVERY layer
Grammar features consistently outweigh factual features
```

### Step 4: Extract Insights

**Automated analysis**:
```python
def compare_attribution_paths(path1, path2):
    """
    Compare two attribution paths to identify differences

    Returns:
        - Divergence point (first layer where paths differ)
        - Feature type dominance (syntax vs semantic)
        - Strength differential by layer
        - Critical decision nodes
    """

    insights = {
        'divergence_layer': find_first_divergence(path1, path2),
        'path1_dominant_features': extract_feature_types(path1),
        'path2_dominant_features': extract_feature_types(path2),
        'strength_comparison': compare_layer_by_layer(path1, path2),
        'suppression_points': find_where_path2_lost(path1, path2)
    }

    return insights
```

---

## Use Cases

### 1. **Debugging Wrong Predictions**

**Question**: "Why did model output ' the' instead of ' Washington'?"

**Traceback reveals**:
- ✓ Grammar features had 3× stronger activation
- ✓ Divergence happened at Layer 18 (syntax beat semantics)
- ✓ "Washington" features existed but were suppressed
- ✓ No single "decision point" - accumulation across layers

### 2. **Finding Circuit Bottlenecks**

**Question**: "Where is ' Washington' losing probability?"

**Traceback reveals**:
- ✓ Layer 12: "President" concept activates strongly
- ✓ Layer 15: Geography features activate (moderate)
- ✓ Layer 18: Syntax override begins here ← BOTTLENECK
- ✓ Layer 22: Grammar wins, facts lose

**Intervention idea**: Amplify Layer 15 geography features

### 3. **Comparing Model Behaviors**

**GEMMA**: " Washington" at 2.9% via geography features
**QWEN**: " Washington" at <1% (different path)

**Traceback comparison**:
- Do they use same features?
- Different layer distributions?
- One model more reliant on syntax?

### 4. **Feature Steering**

**Goal**: Make " Washington" win

**Traceback suggests**:
- Amplify Layer 15 geographic features by 2×
- Suppress Layer 18 syntax features by 0.5×
- Predict: " Washington" probability increases to 15-20%

---

## Expected Outputs

### Visualization 1: Multi-Path Comparison

**Sankey diagram** showing flow for top-5 predictions:
- Width = contribution strength
- Color = feature type (syntax, semantic, grammar)
- Shows where paths diverge
- Highlights dominant features

### Visualization 2: Layer-by-Layer Attribution

**Stacked bar chart** for each layer:
```
L0:  ████████████████████████ (Input)
L5:  ███████████████ (Syntax) ████ (Semantic)
L10: ████████████████ (Syntax) ██ (Semantic)
L15: ███████████████████ (Syntax) █ (Semantic)  ← Grammar wins
L20: █████████████████████████ (Syntax)
L25: " the" wins at 65%
```

### Visualization 3: Feature Activation Map

**Heatmap** showing which features activated for each prediction:
```
                  " the"   " a"   " Washington"   " an"
Syntax Features    ████     ████   ██              ████
Grammar Features   ████     ████   ███             ████
Geographic Feat    █        █      ████            █
Location Features  █        █      ███             █
President Concept  ██       ██     ████            ██
```

### Visualization 4: Decision Timeline

**Flow diagram** showing layer-by-layer probability evolution:
```
Layer    " the"  " Washington"
─────────────────────────────────
L0       20%     20%          (Equal at input)
L5       30%     18%          (Syntax advantage begins)
L10      45%     12%          (Gap widens)
L15      58%     8%           (Decisive layer)
L20      63%     4%           (Consolidation)
L25      65%     2.9%         (Final output)
```

---

## Implementation Plan

### Phase 1: Data Collection (Script 3 Enhancement)

**Modify**: `3_analyze_circuit.py`

**Add**:
- Extract output logit nodes
- Map tokens to output nodes
- Store per-token activation data

### Phase 2: Traceback Algorithm (New Script)

**Create**: `3b_traceback_attribution.py`

**Functionality**:
- Load circuit analysis
- For each top-K prediction:
  - Run traceback algorithm
  - Extract critical path
  - Identify dominant features
  - Compute layer importance
- Save attribution paths to JSON

### Phase 3: Visualization (Script 4 Enhancement)

**Modify**: `4_visualize.py`

**Add new visualizations**:
- Viz 9: Multi-path comparison (Sankey)
- Viz 10: Layer attribution breakdown
- Viz 11: Feature activation heatmap
- Viz 12: Decision timeline

### Phase 4: Comparative Analysis (New Script)

**Create**: `compare_attribution_paths.py`

**Functionality**:
- Load attribution paths for multiple models
- Compare " the" vs " Washington" paths
- Identify divergence points
- Suggest interventions

---

## Research Questions This Enables

### 1. **Does Scaling Change Attribution Paths?**

Compare GEMMA (2B) vs QWEN (4B):
- Same features but different weights?
- Completely different paths?
- More layers = more complex attribution?

### 2. **Syntax vs Semantics: Where's the Battle?**

For each task (geography, arithmetic, multi-hop):
- At what layer does syntax beat semantics?
- Is there a consistent "decision layer"?
- Can we predict failures from early layers?

### 3. **Can We Fix Wrong Predictions?**

If traceback shows " Washington" loses at Layer 15:
- Amplify Layer 15 geography features
- Recompute output
- Does " Washington" win?

### 4. **Minimal Circuit for Each Prediction**

Instead of one minimal circuit for all predictions:
- Minimal circuit for " the"
- Minimal circuit for " Washington"
- Compare: Are they disjoint or overlapping?

### 5. **Feature Importance Validation**

Current: Top features by activation
New: Top features by contribution to SPECIFIC prediction

Are they the same? Or does high activation ≠ high contribution?

---

## Challenges & Limitations

### Challenge 1: Attribution Graph Completeness

**Issue**: Circuit-tracer might prune edges that matter for specific predictions

**Mitigation**: Compare with comprehensive fetch (all features)

### Challenge 2: Multi-Path Contributions

**Issue**: Output might result from MANY weak paths, not one strong path

**Mitigation**: Show top-K paths, not just top-1

### Challenge 3: Nonlinear Interactions

**Issue**: Features might interact nonlinearly (A+B ≠ contribution of A + contribution of B)

**Mitigation**: This is a limitation of linear attribution - acknowledge in documentation

### Challenge 4: Computational Complexity

**Issue**: Traceback for top-5 predictions × top-20 nodes = 100+ path segments to visualize

**Mitigation**: Smart aggregation, focus on divergence points

---

## Proof of Concept

### Test on "President Lives In"

**Run traceback for**:
1. " the" (65%) - expect syntax dominance
2. " a" (21.7%) - expect similar to " the"
3. " Washington" (2.9%) - expect geographic features

**Hypothesis**:
- " the" and " a" share 80%+ of path (both grammatical)
- " Washington" path diverges at Layer 12-15
- Syntax features have 3-5× stronger edges than geographic

**Success metric**: Visualization clearly shows WHERE grammar beats facts

---

## Next Steps

1. **Check if data is available**: Do we have per-token output node mappings?
2. **Implement basic traceback**: Start with simple backward BFS
3. **Visualize one comparison**: " the" vs " Washington" side-by-side
4. **Validate with manual inspection**: Does the path make sense?
5. **Scale to top-5**: Extend to all predictions
6. **Compare models**: GEMMA vs QWEN attribution paths

---

## Relation to Existing Interpretability Work

### Similar Techniques

**Integrated Gradients** (Sundararajan et al., 2017):
- Traces attribution from output to input
- Uses gradients (we use edge weights)
- Our approach is gradient-free

**Attention Rollout** (Abnar & Zuidema, 2020):
- Traces attention flow backward
- Transformer-specific
- We work with SAE features (more interpretable)

**Circuit Discovery** (Wang et al., 2022):
- Finds minimal circuits for behaviors
- We extend to PER-PREDICTION circuits
- More granular than behavior-level analysis

### Our Contribution

**Novel aspects**:
1. Per-prediction attribution (not just per-behavior)
2. Comparative analysis (winner vs runner-up)
3. Layer-by-layer decision tracking
4. Feature-type dominance analysis (syntax vs semantic)

---

## Summary

**Traceback Graphing** = Attribution path analysis for top-K predictions

**Core insight**: Don't just show THE circuit - show the SPECIFIC paths that led to EACH prediction

**Expected outcome**: Understand exactly WHY " the" beat " Washington" at every layer

**Implementation**: Feasible with existing data, requires new analysis script + visualization enhancements

**Research value**: Enables intervention, comparative analysis, and mechanistic understanding of model "decisions"

---

## Open Questions

1. How to handle cases where multiple paths contribute equally?
2. Should we weight by activation, influence, or both?
3. What's the right threshold for "critical path" (top-10? top-20? top-50 nodes)?
4. Can we automate "interesting divergence" detection?
5. How to visualize 5+ paths simultaneously without clutter?

These can be resolved during implementation and testing.
