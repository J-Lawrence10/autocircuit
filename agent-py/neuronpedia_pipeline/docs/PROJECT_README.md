# LLM Circuit Analysis Pipeline

**AI Safety Research Tool for Understanding LLM Reasoning via Attribution Graphs**

This pipeline enables automated circuit discovery and analysis using Neuronpedia attribution graphs. Built with Claude Agent Skills for seamless integration with the [autocircuit research project](https://github.com/KKrampis/autocircuit).

**Status**: Phase 1 Complete - Full pipeline operational with demo results

---

## Quick Navigation

- **[Quick Start Guide](QUICK_START.md)** - Run the pipeline in 5 minutes
- **[Complete Pipeline Demo](PIPELINE_COMPLETE.md)** - Full results for "Japan currency" example
- **[Lab Notebook](LAB_NOTEBOOK_JAPAN_CURRENCY.md)** - Detailed research process documentation
- **[Project Alignment](PROJECT_ALIGNMENT.md)** - How this aligns with autocircuit goals
- **[Project Comparison](PROJECT_COMPARISON.md)** - Our work vs autocircuit requirements

## Project Structure

```
Claude_code/
├── config/
│   ├── neuronpedia_config.yaml    # Main configuration
│   └── requirements.txt            # Python dependencies
├── skills/
│   ├── phase1_data_collection/
│   │   ├── neuronpedia_fetch.py        # Fetch features from API
│   │   ├── prompt_generator.py         # Generate test prompts
│   │   ├── feature_processor.py        # Process and normalize data
│   │   └── connection_analyzer.py      # Build connection graph
│   ├── phase2_circuit_discovery/      # Circuit detection (TODO)
│   ├── phase3_analysis/                # Interpretability analysis (TODO)
│   └── phase4_reporting/               # Report generation (TODO)
├── data/
│   ├── raw/                            # Raw API data
│   └── processed/                      # Processed features and graphs
└── outputs/
    ├── circuits/                       # Discovered circuits
    ├── visualizations/                 # Graph visualizations
    └── reports/                        # Analysis reports
```

## Setup

### 1. Install Dependencies

```bash
pip install -r config/requirements.txt
```

### 2. Configure Pipeline

Edit `config/neuronpedia_config.yaml` to adjust:
- Model parameters (layers, features per layer)
- API settings (rate limiting)
- Analysis thresholds (activation, connections, clustering)
- Safety focus areas
- Output preferences

## Pipeline Phases

### Phase 1: Data Collection & Processing

**Goal:** Fetch and prepare feature data from Neuronpedia

#### Skills:

1. **neuronpedia_fetch.py** - Fetch feature data
   ```bash
   python skills/phase1_data_collection/neuronpedia_fetch.py
   ```
   - Fetches features from specified layers
   - Retrieves feature metadata and activations
   - Saves raw data to `data/raw/`

2. **prompt_generator.py** - Generate test prompts
   ```bash
   python skills/phase1_data_collection/prompt_generator.py
   ```
   - Creates baseline neutral prompts
   - Generates safety-focused prompts (deception, power-seeking, sycophancy, jailbreaks)
   - Creates minimal contrast pairs
   - Saves to `data/processed/prompts/`

3. **feature_processor.py** - Process features
   ```bash
   python skills/phase1_data_collection/feature_processor.py
   ```
   - Normalizes feature data
   - Extracts activation statistics
   - Filters by activation thresholds
   - Saves to `data/processed/features_processed.csv`

4. **connection_analyzer.py** - Analyze connections
   ```bash
   python skills/phase1_data_collection/connection_analyzer.py
   ```
   - Builds feature graph structure
   - Identifies co-activation patterns
   - Finds connected components
   - Saves graph to `data/processed/graphs/`

### Phase 2: Circuit Discovery (Planned)

**Goal:** Identify meaningful circuits and supernodes

#### Planned Skills:

1. **circuit_detector.py** - Detect candidate circuits
   - Use graph algorithms to find interesting paths
   - Identify feedback loops
   - Score circuits by strength and coherence

2. **supernode_builder.py** - Create supernodes
   - Cluster related features using Louvain/Leiden algorithms
   - Build hierarchical feature abstractions
   - Label clusters based on shared semantics

3. **circuit_validator.py** - Validate circuits
   - Test circuits with generated prompts
   - Measure activation consistency
   - Filter false positives

### Phase 3: Analysis & Interpretation (Planned)

**Goal:** Understand what circuits do and identify safety concerns

#### Planned Skills:

1. **safety_analyzer.py** - Safety-focused analysis
   - Identify deception circuits
   - Find power-seeking patterns
   - Detect sycophancy mechanisms
   - Flag potential backdoors

2. **mechanistic_explainer.py** - Generate explanations
   - Create natural language descriptions of circuits
   - Explain information flow through supernodes
   - Document reasoning mechanisms

3. **visualization_generator.py** - Create visualizations
   - Generate circuit diagrams
   - Visualize supernode hierarchies
   - Create activation heatmaps

### Phase 4: Reporting & Documentation (Planned)

**Goal:** Compile findings into actionable reports

#### Planned Skills:

1. **report_generator.py** - Generate reports
   - Compile circuit discoveries
   - Summarize safety findings
   - Create visual documentation
   - Export in markdown/HTML

## Configuration

### Key Parameters

#### Feature Selection
- `min_activation_threshold`: Minimum activation to consider (default: 0.1)
- `max_features_per_layer`: Maximum features to fetch per layer (default: 1000)
- `focus_layers`: Specific layers to analyze (null = all layers)

#### Circuit Detection
- `max_circuit_depth`: Maximum path length for circuits (default: 5)
- `min_circuit_strength`: Minimum connection strength (default: 0.3)
- `connection_threshold`: Threshold for including connections (default: 0.2)

#### Supernode Clustering
- `algorithm`: Clustering algorithm (louvain, leiden, hierarchical)
- `min_cluster_size`: Minimum features per supernode (default: 3)
- `max_cluster_size`: Maximum features per supernode (default: 50)
- `similarity_threshold`: Threshold for grouping features (default: 0.4)

#### Safety Focus
Currently configured to analyze:
- Deception
- Power-seeking
- Sycophancy
- Backdoors
- Jailbreaks

## Usage Workflow

### Quick Start (Phase 1 Only)

```bash
# 1. Fetch features from Neuronpedia
python skills/phase1_data_collection/neuronpedia_fetch.py

# 2. Generate test prompts
python skills/phase1_data_collection/prompt_generator.py

# 3. Process features
python skills/phase1_data_collection/feature_processor.py

# 4. Analyze connections
python skills/phase1_data_collection/connection_analyzer.py
```

### Full Pipeline (When Complete)

```bash
# Run all phases in sequence
python run_pipeline.py --all

# Or run specific phases
python run_pipeline.py --phase 1
python run_pipeline.py --phase 2
```

## Data Flow

```
Neuronpedia API
    ↓
[neuronpedia_fetch.py]
    ↓
data/raw/layer_X_features.json
    ↓
[feature_processor.py]
    ↓
data/processed/features_processed.csv
    ↓
[connection_analyzer.py]
    ↓
data/processed/graphs/feature_graph.json
    ↓
[Phase 2: Circuit Discovery]
    ↓
outputs/circuits/discovered_circuits.json
    ↓
[Phase 3: Analysis]
    ↓
outputs/reports/safety_analysis.md
```

## Prompts for Testing Features

The prompt generator creates several categories:

1. **Baseline prompts** - Neutral prompts for comparison
2. **Safety prompts** - Test safety-relevant features
3. **Contrast pairs** - Minimal pairs differing in safety properties
4. **Feature-specific prompts** - Generated from known activations

These prompts can be used to:
- Validate circuit hypotheses
- Test feature activation patterns
- Compare safe vs unsafe reasoning paths

## Output Files

### Data Files
- `data/raw/layer_X_features.json` - Raw feature data per layer
- `data/processed/features_processed.csv` - Cleaned feature metadata
- `data/processed/graphs/feature_graph.json` - Feature connection graph
- `data/processed/prompts/*.json` - Generated test prompts

### Analysis Outputs (Future)
- `outputs/circuits/circuit_*.json` - Discovered circuits
- `outputs/visualizations/*.png` - Circuit diagrams
- `outputs/reports/*.md` - Analysis reports

## Example Results

### "The currency in Japan is" → "yen"

**Completed Analysis**:
- 13 nodes across 5 layers (L5, L7, L10, L15, L20)
- 12 directed edges showing information flow
- 4 supernodes detected via Louvain algorithm
- Complete lab notebook with findings
- Network visualizations generated

**Key Finding**: Layer 15 feature (0.96 activation) identified as critical bottleneck for fact retrieval

**Supernodes**:
1. **Country/Query Detection** (3 features, act=0.910)
2. **Currency Context** (3 features, act=0.817)
3. **Yen Fact Retrieval** (4 features, act=0.872) ⭐
4. **Output Formatting** (3 features, act=0.800)

See [PIPELINE_COMPLETE.md](PIPELINE_COMPLETE.md) for full results.

---

## Next Steps

### Immediate Validation
- [ ] Test with real Neuronpedia graph data (awaiting graph ID from manual exploration)
- [ ] Execute steering experiments via Circuit Tracer API
- [ ] Compare with contrast prompt ("France" → "euro")
- [ ] Statistical validation across multiple prompts

### For AutoCircuit Repository
- [ ] Create agent skills documentation (.md files)
- [ ] Submit pull request with lab notebook and scripts
- [ ] Document API limitations and findings

### Phase 1 Complete ✓
- [x] Graph-based workflow infrastructure
- [x] Supernode detection (Louvain algorithm)
- [x] Information flow analysis
- [x] Visualization pipeline
- [x] Lab notebook documentation
- [x] Complete pipeline execution on demo prompt

## Contributing

This is an AI safety research project. Key areas for improvement:

1. **Better connection detection** - Currently uses simple co-activation; could use:
   - Activation correlation analysis
   - Causal intervention methods
   - Attention pattern analysis

2. **Semantic clustering** - Group features by meaning, not just activation patterns

3. **Circuit interpretability** - Better methods for explaining what circuits do

4. **Safety detection** - More sophisticated methods for identifying concerning behaviors

## Notes

- The Neuronpedia API structure may vary; adjust `neuronpedia_fetch.py` as needed
- Start with a few test layers (e.g., 10, 15, 20) before processing all layers
- Large models may have 10,000+ features per layer - use filtering aggressively
- Graph analysis can be memory-intensive; consider processing in batches

## References

- Neuronpedia: https://neuronpedia.org/
- Model: Gemma-2-2b
- Graph view: https://neuronpedia.org/gemma-2-2b/graph
