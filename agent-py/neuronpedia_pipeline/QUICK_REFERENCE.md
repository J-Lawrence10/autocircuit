# Quick Reference Card

**One-page guide for using the pipeline**

---

## Installation (First Time Only)

```bash
cd neuronpedia_pipeline
pip install -r config/requirements.txt
# Add API key to config/neuronpedia_config.yaml
```

---

## Basic Usage

### Generate & Analyze One Prompt
```bash
python scripts/1_generate_graph.py     # Edit prompt in line 107 first
python scripts/2_convert_graph.py      # Convert format
python scripts/3_analyze_circuit.py    # Find supernodes
python scripts/4_visualize.py          # Create 5 PNG files
```

### Compare Two Prompts
```bash
python scripts/5_compare_prompts.py \
    data/graphs/graph1_converted.json \
    data/graphs/graph2_converted.json \
    --name1 "Prompt A" \
    --name2 "Prompt B"
```

### Validate Data
```bash
python scripts/validate_real_data.py
```

---

## Output Files

### After Generation (Step 1)
- `data/graphs/real_PROMPT.json` - Raw graph from API

### After Conversion (Step 2)
- `data/graphs/real_PROMPT_converted.json` - Pipeline format

### After Analysis (Step 3)
- `data/graphs/real_PROMPT_supernodes.json` - Supernode data
- Console output with statistics

### After Visualization (Step 4)
- `data/visualizations/real_supernodes_overview.png`
- `data/visualizations/real_layer_distribution.png`
- `data/visualizations/real_activation_heatmap.png`
- `data/visualizations/real_top_features.png`
- `data/visualizations/real_edge_weights.png`

### After Comparison (Step 5)
- `data/visualizations/comparison_A_vs_B.png`
- Console output with overlap statistics

---

## Key Metrics to Look For

### Node Count
- 800-1000 nodes = typical factual prompt
- <500 nodes = simple retrieval
- >1500 nodes = complex reasoning

### Top Features
- Check Layer 15 for factual prompts
- Look for L15_F376262 (universal feature)
- Activation >100 = highly important

### Feature Overlap
- 30-40% = shared circuits
- <20% = very different tasks
- >50% = very similar tasks

### Inhibitory Edges
- 40-45% = normal
- <30% = unusual (less suppression)
- >60% = highly competitive outputs

---

## Common Issues

### "No API key"
→ Edit `config/neuronpedia_config.yaml`

### "Graph generation failed"
→ Check internet, try shorter prompt

### "No supernodes detected"
→ Lower `min_supernode_size` in script 3

### Unicode errors (Windows)
→ Already fixed with UTF-8 encoding

---

## Key Files to Read

1. `README.md` - Setup guide
2. `PIPELINE_STATUS.md` - What's working now
3. `INNOVATION_REPORT.md` - Why it's better than base
4. `NODE_STEERING_GUIDE.md` - What's next (Phase 2)

---

## Performance

- Graph generation: 10 sec
- Conversion: <1 sec
- Analysis: 5 sec
- Visualization: 10 sec
- Comparison: 5 sec

**Total: ~30 seconds per prompt**

---

## Quick Checks

### Is my data real?
```bash
python scripts/validate_real_data.py
# Should say: ✓ Real data confirmed
```

### Did visualization work?
```bash
ls data/visualizations/*.png
# Should see 5 PNG files
```

### What's my top feature?
```bash
python scripts/3_analyze_circuit.py
# Look for "Top 5 features by activation"
```

---

## Discovered Features

### L15_F376262
- Activation: 150.29 (consistent)
- Found in: Japan, France prompts
- Role: Universal factual retrieval

### Layer 15
- Specializes in factual knowledge
- 3 of top 5 features typically from L15
- Critical for correct output

### Inhibitory Connections
- ~42% of all edges
- Suppress competing answers
- Maintain prediction confidence

---

## Next Phase Features (Coming Soon)

1. **Node Steering** - Test causality
2. **Feature Lookup** - What features mean
3. **Interactive Viz** - Explore circuits
4. **Batch Processing** - 100+ prompts

---

## One-Line Commands

```bash
# Validate everything
python scripts/validate_real_data.py

# Quick test
python scripts/1_generate_graph.py && python scripts/2_convert_graph.py

# Full pipeline (manual)
python scripts/1_generate_graph.py && \
python scripts/2_convert_graph.py && \
python scripts/3_analyze_circuit.py && \
python scripts/4_visualize.py

# Compare prompts
python scripts/5_compare_prompts.py graph1.json graph2.json
```

---

**Keep this card handy for quick reference!**
