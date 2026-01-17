# Node Steering Implementation Guide

**Purpose**: Manipulate feature activations to test causal relationships in circuits

---

## What is Node Steering?

**Node steering** = Modifying feature activations to see how model behavior changes

**Why it matters**:
- Proves causality (not just correlation)
- Tests feature necessity vs sufficiency
- Validates circuit hypotheses
- Discovers what features actually do

---

## 5 Types of Steering Experiments

### 1. ⭐ Feature Amplification
**What**: Multiply a feature's activation by 2x, 5x, 10x

**Purpose**: Test if boosting a feature increases confidence in output

**Example**:
```python
# Amplify L15_F376262 (top feature for "yen")
amplify_feature(graph_id, feature_id=376262, layer=15, multiplier=5.0)

# Expected result:
# Before: "yen" (98% confidence)
# After:  "yen" (99.9% confidence) - stronger!
```

**Hypothesis**: If L15_F376262 is critical for "yen", amplifying it should increase certainty

**Counter-test**: Amplify on unrelated prompt → should have no effect

---

### 2. ⭐⭐⭐ Feature Ablation (Knockout)
**What**: Set a feature's activation to 0 (knock it out)

**Purpose**: Test if a feature is NECESSARY for correct output

**Example**:
```python
# Ablate L15_F376262
ablate_feature(graph_id, feature_id=376262, layer=15)

# Expected result:
# Before: "yen" (98% confidence)
# After:  "dollar" or "currency" (wrong answer) OR low confidence
```

**This is the GOLD STANDARD test**:
- If output breaks → feature is necessary
- If output unchanged → feature is redundant

**Best for**: Identifying critical bottleneck features

---

### 3. ⭐⭐ Supernode Steering
**What**: Apply intervention to ALL features in a supernode

**Purpose**: Test functional role of entire computational modules

**Example**:
```python
# Suppress SN7 (identified as bottleneck)
steer_supernode(graph_id, supernode_id=7, intervention='suppress', amount=0.1)

# Expected result:
# Circuit breaks → SN7 is critical pathway
```

**Interventions**:
- **Suppress** (0.1x): Weaken module
- **Ablate** (0x): Complete knockout
- **Amplify** (5x): Boost module
- **Noise** (add random): Test robustness

**Best for**: Understanding hierarchical processing

---

### 4. ⭐⭐ Inhibitory Connection Analysis
**What**: Remove or strengthen negative-weight edges

**Purpose**: Understand what features suppress

**Example**:
```python
# Find what L15_F376262 inhibits
inhibited = find_inhibitory_targets(graph_id, feature_id=376262, layer=15)
# Result: ["L20_F123456" (dollar feature), "L20_F789012" (euro feature)]

# Remove inhibition
remove_inhibitory_edges(graph_id, feature_id=376262)

# Expected result:
# Before: "yen" (98% confidence)
# After:  "yen" (60%) + "dollar" (30%) + "euro" (10%) - confusion!
```

**Hypothesis**: Negative edges suppress competing answers

**Insight**: Shows how model maintains confident, unique predictions

---

### 5. ⭐ Activation Clamping
**What**: Fix a feature's activation at a specific value across tokens

**Purpose**: Test information routing and context dependency

**Example**:
```python
# Clamp "Japan detection" feature to max activation
clamp_feature(graph_id, feature_id=12345, layer=5, value=10.0)

# Then test with different prompts:
# "The currency in France is" → Still says "yen"? (overfitting!)
# "The currency in China is" → Says "yen"? (confirmation!)
```

**Best for**: Testing context-independence vs context-sensitivity

---

## Implementation Plan

### Phase 1: Single Feature Steering (Week 1)

**File**: `scripts/6_steering_experiments.py`

```python
import requests

def amplify_feature(graph_id, layer, feature_id, multiplier):
    """
    Amplify a feature's activation

    Args:
        graph_id: Neuronpedia graph slug
        layer: Feature layer (0-27)
        feature_id: Feature ID
        multiplier: Amplification factor (2.0, 5.0, 10.0)

    Returns:
        new_completion: Model output after intervention
        confidence: Probability of top token
    """

    # API endpoint (need to discover from Neuronpedia)
    endpoint = f"https://neuronpedia.org/api/steer/{graph_id}"

    payload = {
        "intervention": {
            "type": "multiply",
            "layer": layer,
            "feature": feature_id,
            "multiplier": multiplier
        }
    }

    response = requests.post(endpoint, json=payload)
    return response.json()

def ablate_feature(graph_id, layer, feature_id):
    """
    Knock out a feature completely

    Expected behavior:
    - If feature is necessary: output changes
    - If feature is redundant: output unchanged
    """

    payload = {
        "intervention": {
            "type": "ablate",
            "layer": layer,
            "feature": feature_id
        }
    }

    response = requests.post(endpoint, json=payload)
    return response.json()
```

**Experiments to run**:
1. Ablate L15_F376262 on "Japan currency" → expect failure
2. Ablate L15_F376262 on "France capital" → expect failure
3. Ablate random feature → expect no change (control)
4. Amplify L15_F376262 by 10x → expect higher confidence

---

### Phase 2: Supernode Steering (Week 2)

**File**: `scripts/7_supernode_steering.py`

```python
def steer_supernode(graph_id, supernode_features, intervention_type, amount):
    """
    Apply intervention to all features in a supernode

    Args:
        graph_id: Graph slug
        supernode_features: List of (layer, feature_id) tuples
        intervention_type: 'amplify', 'suppress', 'ablate'
        amount: Multiplier or noise level

    Example:
        # Suppress SN7 (bottleneck supernode)
        sn7_features = [(3, 12345), (5, 67890), (7, 11111), ...]
        steer_supernode(graph_id, sn7_features, 'suppress', 0.1)
    """

    payload = {
        "intervention": {
            "type": "multi_feature",
            "features": [
                {"layer": l, "feature": f, "type": intervention_type, "amount": amount}
                for l, f in supernode_features
            ]
        }
    }

    response = requests.post(endpoint, json=payload)
    return response.json()
```

**Experiments**:
1. Ablate SN3 (main processing) → expect major failure
2. Ablate SN7 (bottleneck) → expect circuit break
3. Ablate SN11 (input) → expect wrong interpretation
4. Amplify SN3 → expect higher confidence

---

### Phase 3: Inhibitory Analysis (Week 3)

**File**: `scripts/8_inhibitory_analysis.py`

```python
def find_inhibitory_targets(graph, feature_id, layer):
    """
    Find what a feature inhibits (negative edges)

    Returns:
        List of (target_layer, target_feature, weight) tuples
    """

    source_node = f"L{layer}_F{feature_id}"

    inhibited = []
    for u, v, data in graph.edges(data=True):
        if u == source_node and data['weight'] < 0:
            target = graph.nodes[v]
            inhibited.append({
                'layer': target['layer'],
                'feature': target['feature_id'],
                'weight': data['weight'],
                'label': target['label']
            })

    # Sort by strength
    inhibited.sort(key=lambda x: x['weight'])
    return inhibited

def test_inhibition_removal(graph_id, feature_id, layer):
    """
    Remove all inhibitory edges from a feature
    Test what competing answers emerge
    """

    # Get inhibitory targets
    inhibited = find_inhibitory_targets(graph, feature_id, layer)

    # Remove those edges
    payload = {
        "intervention": {
            "type": "remove_edges",
            "source": {"layer": layer, "feature": feature_id},
            "edge_filter": "negative_only"
        }
    }

    response = requests.post(endpoint, json=payload)

    # Expected: Multiple competing answers emerge
    return response.json()
```

**Experiments**:
1. Find what L15_F376262 inhibits
2. Remove inhibition → see if "dollar", "euro" emerge
3. Remove ALL inhibition from graph → chaos!
4. Strengthen inhibition → more confident predictions?

---

## Experiment Design Template

For each experiment, document:

```markdown
### Experiment: [Name]

**Hypothesis**: [What you expect to happen]

**Intervention**:
- Feature: L[X]_F[Y]
- Type: [amplify/ablate/suppress]
- Amount: [multiplier]

**Baseline**:
- Prompt: "[prompt text]"
- Output: "[token]" ([confidence]%)

**After Intervention**:
- Output: "[token]" ([confidence]%)

**Result**: [Confirmed/Rejected/Unexpected]

**Interpretation**: [What this tells us]

**Follow-up**: [Next experiments to run]
```

---

## Example Experiment: Ablate L15_F376262

### Hypothesis
L15_F376262 is NECESSARY for factual retrieval. Ablating it will cause:
1. Wrong answer OR
2. Low confidence OR
3. Generic response

### Method
```python
# Run on "The currency in Japan is"
baseline = generate_graph("The currency in Japan is")
# Result: "yen" (98% confidence)

# Ablate L15_F376262
intervened = ablate_feature(baseline.graph_id, layer=15, feature_id=376262)
# Expected: NOT "yen" or low confidence
```

### Expected Outcomes

**If confirmed (output changes)**:
- L15_F376262 is necessary for factual knowledge
- Circuit cannot compensate for its loss
- Single point of failure identified

**If rejected (output unchanged)**:
- Feature is redundant (surprising!)
- Circuit has backup pathways
- Need to find alternative critical features

### Counter-Tests
1. Ablate random feature → no change (control)
2. Ablate on "France capital" → also fails (generalization)
3. Ablate on "2+2=" → no effect (domain-specific)

---

## Statistical Validation

For robust conclusions, run N=20 trials:

```python
def validate_feature_necessity(feature_id, layer, test_prompts):
    """
    Test feature across multiple prompts

    Args:
        feature_id: Feature to test
        layer: Layer number
        test_prompts: List of factual prompts

    Returns:
        success_rate: % of prompts where ablation causes failure
    """

    failures = 0
    for prompt in test_prompts:
        baseline = generate_graph(prompt)
        intervened = ablate_feature(baseline.graph_id, layer, feature_id)

        if intervened.output != baseline.output:
            failures += 1

    necessity_score = failures / len(test_prompts)
    return necessity_score

# Test L15_F376262 on 20 factual prompts
factual_prompts = [
    "The currency in Japan is",
    "The capital of France is",
    "The largest planet is",
    "Water freezes at",
    # ... 16 more
]

score = validate_feature_necessity(376262, 15, factual_prompts)
# If score > 0.8: Highly necessary
# If score < 0.2: Not critical
```

---

## Visualization Ideas

### 1. Before/After Comparison
```python
# Show activation heatmap before and after intervention
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Before
plot_activation_heatmap(baseline_graph, ax=ax1, title="Baseline")

# After
plot_activation_heatmap(intervened_graph, ax=ax2, title="After Ablation")

# Highlight changed features
plt.savefig("ablation_comparison.png")
```

### 2. Confidence Decay Curve
```python
# Test amplification levels
multipliers = [0, 0.5, 1.0, 2.0, 5.0, 10.0]
confidences = []

for mult in multipliers:
    result = amplify_feature(graph_id, layer, feature_id, mult)
    confidences.append(result['confidence'])

plt.plot(multipliers, confidences)
plt.xlabel('Amplification Multiplier')
plt.ylabel('Output Confidence (%)')
plt.title('Effect of Amplifying L15_F376262')
plt.savefig("amplification_curve.png")
```

### 3. Inhibition Network
```python
# Visualize what a feature suppresses
inhibited = find_inhibitory_targets(graph, 376262, 15)

# Create network diagram
# Center node = L15_F376262
# Red edges to suppressed features
# Edge thickness = suppression strength
```

---

## API Discovery Needed

We need to find these Neuronpedia endpoints:

1. **Steering API**: `POST /api/steer/{graph_id}`
   - Apply interventions
   - Get new completion

2. **Feature details**: `GET /api/feature/{model}/{layer}/{feature}`
   - Get feature explanation
   - See top activating examples

3. **Batch steering**: `POST /api/steer/batch`
   - Test multiple interventions at once

**Action**: Research Neuronpedia docs or GitHub for these endpoints

---

## Next Steps

### Immediate (Week 1)
1. **Discover steering API endpoint** - Check Neuronpedia docs
2. **Implement `6_steering_experiments.py`** - Basic amplify/ablate
3. **Test L15_F376262 ablation** - Validate necessity
4. **Document results** - Create first lab notebook

### Short-term (Week 2-3)
5. **Supernode steering** - Test computational modules
6. **Inhibitory analysis** - Find suppression patterns
7. **Statistical validation** - 20+ prompt trials
8. **Comparison across prompts** - Does steering generalize?

### Medium-term (Month 1)
9. **Automated experiment runner** - Batch processing
10. **Interactive dashboard** - Real-time steering interface
11. **Publication figures** - High-quality visualizations
12. **Write up findings** - Submit to autocircuit

---

## Expected Impact

### Scientific
- **Prove causality** in circuit operation
- **Validate supernode roles** experimentally
- **Map inhibitory networks** systematically
- **Discover universal features** via cross-prompt steering

### Engineering
- **Model debugging** - Find failure modes
- **Safety analysis** - Test harmful activations
- **Interpretability** - Understand feature functions
- **Robustness testing** - How fragile are circuits?

---

**Status**: Design complete, awaiting API endpoint discovery

**Estimated timeline**: 3-4 weeks to full implementation

**Priority**: HIGH - This is the key to moving from correlation → causation
