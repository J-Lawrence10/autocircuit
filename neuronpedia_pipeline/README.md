# Neuronpedia Circuit Analysis Pipeline

Traceback graphing pipeline for identifying bottleneck features in neural network circuits. Traces backward through SAE attribution graphs to find convergence points that control model predictions, with cross-circuit comparison and semantic classification.

Supported models: GEMMA-2-2B (26 layers), QWEN3-4B (36 layers).

## Quick Start

```bash
pip install -r config/requirements.txt
# Add your Neuronpedia API key to config/neuronpedia_config.yaml
python run_full_pipeline.py --prompt "The chemical symbol for Argon is" --model gemma-2-2b
```

## Pipeline Orchestrator

`run_full_pipeline.py` runs the full pipeline end-to-end via CLI.

```
--prompt TEXT       Prompt to analyze (required)
--model MODEL       gemma-2-2b | qwen3-4b | both (default: both)
--advanced          Also run advanced analysis steps 5-10
--steer-quick       Run Stage 3 steering validation (quick: top 5 features, ~20 min)
--steer-full        Run Stage 3 steering validation (full: all features, ~10 hours)
--steer-rate-delay  Seconds between steering API calls (default: 36 = 100/hr)
--skip-api          Skip Neuronpedia API queries in Stage 1.5
--api-limit N       Max API queries for Stage 1.5 (default: 100)
```

Execution order: Steps 1 > 2 > 3 > 3b > 4 > Stage 1.5 > Stage 2. With `--steer-quick/--steer-full`: also Stage 3. With `--advanced`: also Steps 5, 7, 8, 9, 10.

## Core Scripts (`scripts/`)

**`1_generate_graph.py`** -- Connects to the Neuronpedia circuit tracer API and generates a raw SAE attribution graph for a given prompt and model. Outputs a JSON graph file with node activations and edge weights to `data/prompts/<circuit>/1_generation/`.

**`2_convert_graph.py`** -- Converts the raw Circuit Tracer JSON into the pipeline's standardized format. Extracts node metadata, edge weights, model predictions, and handles model-specific token formatting differences between GEMMA and QWEN.

**`3_analyze_circuit.py`** -- Performs structural analysis of the converted circuit graph. Runs Louvain community detection for supernode clustering, computes betweenness centrality for bottleneck identification, and optionally fetches feature descriptions from Neuronpedia.

**`3b_traceback_paths.py`** -- Core innovation: backward BFS from output nodes to input layers with geometric decay scoring (score^0.8 per hop). Identifies bottleneck features where 60%+ of critical paths converge, revealing which features gate model predictions.

**`4_visualize.py`** -- Generates 8 PNG visualizations per circuit: supernode overview, layer distribution, activation heatmap, feature importance rankings, information flow diagram, thought progression, supernode connections, and a summary dashboard.

**`annotate_features_v2.py`** -- Keyword-based semantic classifier for Neuronpedia feature explanations. Classifies into SYNTAX, SEMANTICS:CODE/CONCEPT/GEOGRAPHIC/ENTITY/TEMPORAL, or POLYSEMANTIC. Exports `classify_from_explanation()` for use by other scripts.

**`feature_description_fetcher.py`** -- Queries the Neuronpedia API for human-readable feature descriptions. Handles the ID mapping (`neuronpedia_id = circuit_tracer_id % 16384`) and rate limiting. Used by Step 3 and Stage 1.5.

**`path_manager.py`** -- Centralized path resolution for the pipeline directory structure. Manages `data/prompts/<model>_<slug>/` layout and provides consistent path access across all scripts.

**`pipeline_constants.py`** -- Shared constants: model layer counts, SAE dictionary sizes, layer group boundaries, and the bottleneck convergence threshold (0.6). Prevents threshold mismatches between stages.

**`supernode_detector.py`** -- Community detection module using Louvain clustering on circuit graphs. Groups individual SAE features into high-level supernodes based on connection density, with configurable min/max cluster sizes.

**`stage_1_4_visualizations.py`** -- Distribution analysis visualizations: category-by-layer stacked bar chart, bottleneck before/after semantic profile, layer-wise semantic flow Sankey diagram, and cross-prompt convergence heatmap. Sources data from the bottleneck library.

**`stage_1_5_cross_circuit_bottlenecks.py`** -- Cross-circuit bottleneck analysis across all analyzed prompts and models. Builds the bottleneck library by comparing convergence features across circuits, enriches with Neuronpedia API descriptions, and identifies features that appear as bottlenecks in multiple circuits.

**`stage_2_enhanced_visualizations.py`** -- Generates semantically color-coded circuit diagrams, interactive HTML dashboards, and thought progression maps. Integrates the v2 classifier for automatic node categorization with multi-source feature lookup (cross-circuit library, per-circuit descriptions, fallback).

**`5_steering_validation.py`** -- Stage 3: Tests whether bottleneck features identified via cross-circuit analysis actually steer model output when amplified or suppressed via the Neuronpedia Steering API. Computes Steering Impact Score (SIS), Disruption Score (DS), and correlates cross-circuit frequency with steering effectiveness. Supports quick, full, single-feature, resume, and analyze-only modes.

## Advanced Analysis (`scripts/advanced_analysis/`)

These scripts perform deeper analysis beyond the core pipeline. Run via `--advanced` flag or individually.

| Script | Purpose |
|--------|---------|
| `3_analyze_circuit_multi.py` | Batch analysis across multiple circuits with multi-algorithm comparison |
| `5_compare_prompts.py` | Cross-prompt comparison of circuit structure and bottleneck overlap |
| `6_identify_targets.py` | Identifies high-leverage intervention targets from bottleneck analysis |
| `6_visualize_validation.py` | Generates validation visualizations for circuit analysis results |
| `7_extract_minimal_pathways.py` | Extracts the minimum viable circuit -- fewest nodes preserving prediction |
| `8_supernode_evolution.py` | Tracks how supernode composition and roles evolve across layers |
| `9_steering_analysis.py` | Analyzes potential for feature steering/intervention at bottleneck points |
| `10_polysemanticity_analysis.py` | Measures semantic purity vs polysemanticity of bottleneck features |
| `batch_query_features.py` | Batch queries to Neuronpedia API for feature descriptions |
| `query_bottleneck_semantics.py` | Targeted semantic queries for bottleneck features |
| `query_feature_semantics.py` | Individual feature semantic profiling via Neuronpedia |

## Skills (`skills/`)

Claude Code skills for interactive pipeline usage:

- **neuronpedia-convert** -- Convert raw graphs to pipeline format
- **neuronpedia-compare** -- Compare circuits across prompts/models
- **neuronpedia-validate** -- Validate circuit analysis results
- **neuronpedia-visualize** -- Generate and inspect visualizations
- **steering-validate** -- Validate bottleneck features via Neuronpedia Steering API
- **circuit-report** -- Run full pipeline and generate comprehensive analysis report

## Key Concepts

- **Traceback graphing**: Backward BFS from output to input with geometric decay (0.8) to score feature importance without exponential path explosion.
- **Bottleneck convergence**: Features appearing in 60%+ of critical paths act as information gates. Where they occur in the layer stack determines what information survives to the output.
- **Feature ID mapping**: Neuronpedia uses 16k SAE dictionaries, so `neuronpedia_id = circuit_tracer_id % 16384`. Only GEMMA features are currently queryable via the Neuronpedia feature API.
- **Cross-circuit features**: Features that appear as bottlenecks across multiple prompts suggest universal circuit components rather than prompt-specific processing.

## Output Structure

All generated data goes to `data/` (gitignored). Per-circuit outputs follow:

```
data/prompts/<model>_<prompt-slug>/
  1_generation/    Raw API graph
  2_conversion/    Standardized pipeline format
  3_analysis/      Circuit analysis + traceback paths
  4_visualizations/ PNG figures
```

Cross-circuit results: `data/stage_1_5_bottleneck_library.json`, `data/stage_2_visualizations/`.

Steering validation: `data/stage_3_steering/` (baselines, results, analysis, report).
