# Neuronpedia Circuit Analysis Pipeline

**AI Safety Tool for Analyzing LLM Reasoning via Attribution Graphs**

This is a clean, organized pipeline for analyzing neural circuits in language models using Neuronpedia attribution graphs.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r config/requirements.txt
```

### 2. Configure API Key

Edit `config/neuronpedia_config.yaml` and add your Neuronpedia API key:

```yaml
api:
  api_key: "your-api-key-here"
```

### 3. Run Pipeline

```bash
# Step 1: Generate attribution graph from prompt
python scripts/1_generate_graph.py

# Step 2: Convert to pipeline format
python scripts/2_convert_graph.py

# Step 3: Analyze circuit and detect supernodes
python scripts/3_analyze_circuit.py

# Step 4: Generate visualizations
python scripts/4_visualize.py

# Step 5 (Optional): Compare two prompts
python scripts/5_compare_prompts.py graph1.json graph2.json --name1 "A" --name2 "B"
```

---

## What This Does

1. **Generate Graph**: Connects to Neuronpedia API and generates an attribution graph for your prompt
2. **Convert Format**: Transforms Circuit Tracer format to pipeline-compatible structure
3. **Analyze Circuit**: Detects supernodes using Louvain community detection, identifies bottlenecks
4. **Visualize**: Creates PNG visualizations showing circuit structure and activation patterns
5. **Compare Prompts**: Analyze feature overlap and shared circuits across different prompts

---

## Pipeline Structure

```
neuronpedia_pipeline/
├── scripts/
│   ├── 1_generate_graph.py        # API connection & graph generation
│   ├── 2_convert_graph.py         # Format conversion
│   ├── 3_analyze_circuit.py       # Circuit analysis & supernodes
│   ├── 4_visualize.py             # Generate PNG visualizations
│   ├── 5_compare_prompts.py       # Multi-prompt comparison (NEW)
│   ├── supernode_detector.py      # Louvain algorithm implementation
│   └── validate_real_data.py      # Data validation & quality checks
├── config/
│   ├── neuronpedia_config.yaml    # API key and settings
│   └── requirements.txt           # Python dependencies
├── data/
│   ├── graphs/                    # Generated graphs stored here
│   └── visualizations/            # PNG outputs saved here
├── docs/
│   ├── REAL_DATA_SUCCESS.md       # Success story with real data
│   ├── QUICK_START.md             # Detailed quick start guide
│   └── PROJECT_README.md          # Full project documentation
├── INNOVATION_REPORT.md           # Comparison to AutoCircuit base
├── DATA_SOURCE_CONFIRMATION.md    # Real data validation proof
├── COMPARISON_ANALYSIS_RESULTS.md # Japan vs France findings
├── NODE_STEERING_GUIDE.md         # Phase 2 implementation guide
├── PIPELINE_STATUS.md             # Current status & roadmap
└── README.md                      # This file
```

---

## Example Output

For prompt **"The currency in Japan is"**:

- **Nodes**: 858 features across 26 layers
- **Edges**: 22,687 connections (43% inhibitory)
- **Supernodes**: 3 communities detected
  - SN3 (92 nodes): Main processing pathway
  - SN7 (37 nodes): Critical bottleneck
  - SN11 (41 nodes): Input processing

**Key Finding**: Layer 15 feature (L15_F376262) has activation 150.29 - critical for factual retrieval!

---

## Visualizations Generated

1. **real_supernodes_overview.png** - Supernode-level circuit diagram
2. **real_layer_distribution.png** - Node distribution across layers
3. **real_activation_heatmap.png** - Activation patterns by layer
4. **real_top_features.png** - Top 20 features by activation
5. **real_edge_weights.png** - Excitatory vs inhibitory connections

All saved as high-resolution PNG files (300 DPI).

---

## Key Features

### ✅ Real Data
- Connects to actual Neuronpedia API
- Downloads real Circuit Tracer attribution graphs
- Analyzes genuine neural circuits (not mock data)

### ✅ Automatic Analysis
- Detects supernodes via Louvain algorithm
- Identifies bottlenecks using betweenness centrality
- Ranks features by importance

### ✅ Rich Visualizations
- 5 different visualization types
- High-resolution PNG output
- Color-coded by supernode

### ✅ Flexible
- Works with any prompt
- Configurable thresholds
- Supports multiple models (gemma-2-2b ready)

---

## Customization

### Change the Prompt

Edit `scripts/1_generate_graph.py`, line 107:

```python
test_prompt = "Your custom prompt here"
```

### Adjust Supernode Detection

Edit `scripts/3_analyze_circuit.py`, line 79:

```python
detector = SupernodeDetector(min_supernode_size=3, max_supernode_size=100)
```

### Change Visualization Style

Edit `scripts/4_visualize.py` - modify colors, sizes, or add new plots.

---

## Technical Details

### Graph Structure

**Nodes**:
```json
{
  "id": "0_96_1",
  "label": "L0_F4752",
  "layer": 0,
  "activation": 3.554,
  "influence": 0.707
}
```

**Edges**:
```json
{
  "source": "0_96_1",
  "target": "1_234_2",
  "weight": 4.472
}
```

### Handling Negative Weights

43% of connections are inhibitory (negative weights). The pipeline:
- Uses absolute values for community detection
- Preserves original signs for analysis
- Visualizes excitatory vs inhibitory separately

### Performance

- Graph generation: ~10 seconds
- Conversion: <1 second
- Analysis: ~5 seconds
- Visualization: ~10 seconds
- **Total: ~30 seconds**

---

## Requirements

- Python 3.8+
- networkx
- python-louvain
- matplotlib
- requests
- pyyaml
- numpy

All listed in `config/requirements.txt`.

---

## API Key

Get your Neuronpedia API key:
1. Visit https://neuronpedia.org
2. Log in
3. Go to /account
4. Copy your API key
5. Add to `config/neuronpedia_config.yaml`

---

## Troubleshooting

### "No API key" Error
- Check `config/neuronpedia_config.yaml`
- Ensure key is properly formatted: `api_key: "sk-np-..."`

### "Graph generation failed"
- Verify internet connection
- Check Neuronpedia API status
- Try a shorter prompt (<100 chars)

### "No supernodes detected"
- Lower `min_supernode_size` in `3_analyze_circuit.py`
- Check graph has sufficient nodes (>50)

### Visualization errors
- Ensure matplotlib backend is configured
- Check output directory exists: `data/visualizations/`

---

## Next Steps

1. **Test new prompts** - Analyze different completions
2. **Compare circuits** - How does "Japan" differ from "France"?
3. **Steering experiments** - Modify supernode activations
4. **Feature investigation** - Explore what high-activation features do

---

## Documentation

- **REAL_DATA_SUCCESS.md**: Complete success report
- **QUICK_START.md**: Detailed usage guide
- **PROJECT_README.md**: Full project documentation

---

## Citation

If you use this pipeline in research:

```
Neuronpedia Circuit Analysis Pipeline
Built with Claude Agent Skills for autocircuit project
Uses Circuit Tracer attribution graphs from Neuronpedia
Model: gemma-2-2b (Google)
```

---

## License

See autocircuit project for licensing.

---

## Support

For issues or questions:
- Check `docs/` folder for detailed documentation
- Review `REAL_DATA_SUCCESS.md` for examples
- See original project: https://github.com/KKrampis/autocircuit

---

**Status**: ✅ Production Ready

**Last Updated**: 2026-01-16

**Version**: 1.0
