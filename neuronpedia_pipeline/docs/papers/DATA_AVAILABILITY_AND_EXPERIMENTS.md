# Data Availability and Experimental Summary

**Companion document to:** `CROSS_DOMAIN_CIRCUIT_PAPER.md`
**Project:** Cross-Domain Circuit Analysis of Factual Knowledge Retrieval in LLMs
**Last updated:** 2026-04-08

This document provides a complete inventory of the data and experiments supporting the main paper's findings, intended for reproducibility and review.

---

## 1. Scope

- **60 attribution circuits** generated via the Neuronpedia Circuit Tracer API
- **2 models**: GEMMA-2-2B (26 layers, 16k SAE features/layer), QWEN3-4B (36 layers)
- **3 knowledge domains**: chemistry (10 prompts), geography (10 prompts), history (10 prompts)
- **80 causal steering experiments** on the GEMMA model (QWEN steering API not yet available)
- **244 cross-circuit bottleneck features** identified; 130 semantically annotated

## 2. Prompt Set

### Chemistry (10)
Gold, iron, lead, mercury, argon, sodium, silver, potassium, copper, tungsten — all using the format "The chemical symbol for X is".

### Geography (10)
France, Japan, Germany, Egypt, Italy, Spain, Canada, Thailand, Turkey, South Korea — all using the format "The capital of X is".

### History (10)
WWII, moon landing, Berlin Wall, Titanic, American independence, French Revolution, WWI, Columbus, Great Fire of London, Mandela release — all using the format "[Event] [occurred/ended/began] in".

Full prompt list with expected answers: Appendix A of `CROSS_DOMAIN_CIRCUIT_PAPER.md`.

## 3. Directory Structure

All data lives under `neuronpedia_pipeline/data/` (gitignored, ~2 GB).

### 3.1 Per-Circuit Data
```
data/prompts/<model>_<prompt-slug>/
  1_generation/           Raw API graph JSON
  2_conversion/           Standardized pipeline format
  3_analysis/             Structural analysis + traceback paths
  4_visualizations/       8 PNG figures per circuit
```

60 circuit directories total. Naming convention: `gemma-2-2b_the-chemical-symbol-for-gold-is`, `qwen3-4b_the-capital-of-japan-is`, etc.

### 3.2 Cross-Circuit Aggregates
```
data/stage_1_5_bottleneck_library.json   Cross-circuit bottleneck library
data/stage_1_5_cross_circuit_report.md   Summary report
data/stage_1_5_visualizations/           Cross-circuit visualizations
```

### 3.3 Stage 2 Analyses
Each Stage 2 analysis writes to its own directory:
```
data/stage_2_analysis/             Main cross-domain statistical results
data/stage_2_minimal_pathways/     Essential pathway extraction (94.1% redundancy)
data/stage_2_multi_algorithm/      Community detection with 4 algorithms
data/stage_2_polysemanticity/      Semantic purity analysis
data/stage_2_layer_energy/         Per-layer activation energy profiles
data/stage_2_edge_flow/            Edge weight flow patterns
data/stage_2_coactivation/         Feature co-activation networks
data/stage_2_output_decomposition/ Output node contribution analysis
data/stage_2_enhanced_analysis/    Enhanced circuit metrics (8 categories)
data/stage_2_statistical_deepdive/ Extended statistical tests
data/stage_2_outlier_analysis/     Circuit outlier identification
data/stage_2_unused_columns/       Hidden predictor discovery
data/stage_2_annotations/          Feature annotations
data/stage_2_figures/              Publication-quality figures
data/stage_2_visualizations/       Additional visualizations
```

### 3.4 Steering Experiments
```
data/stage_3_steering/                       D4 (20 experiments) + D5 expansion (30 experiments) = 50 total
data/stage_2_essential_pathway_steering/     New 30 experiments (D6, added 2026-04-08)
```

## 4. Experiments Summary

### 4.1 Stage 1: Initial Analysis
- Per-circuit analysis of 60 circuits with traceback graphing (backward BFS, geometric decay = 0.8)
- Bottleneck identification: features where ≥60% of critical paths converge
- Circuit statistics: nodes, edges, communities, centrality, layer distribution

### 4.2 Stage 1.5: Cross-Circuit Library
- Aggregated bottleneck features across all 60 circuits
- 244 unique cross-circuit features identified (all appearing in ≥2 circuits)
- 130 semantically annotated via Neuronpedia feature API (GEMMA only)

### 4.3 Stage 2: Cross-Domain Statistics
| Analysis | Output | Key result |
|----------|--------|-----------|
| Cross-category (ANOVA, regression) | `stage_2_analysis/` | 13/16 structural metrics differ cross-model |
| Layer energy profiling | `stage_2_layer_energy/` | Within-model cos sim=0.978; between-model=0.696 |
| Edge flow analysis | `stage_2_edge_flow/` | 80-85% of edges are skip connections |
| Minimal pathway extraction | `stage_2_minimal_pathways/` | 94.1% node redundancy |
| Multi-algorithm community validation | `stage_2_multi_algorithm/` | Modularity >0.4, Jaccard agreement=0.363 |
| Polysemanticity classification | `stage_2_polysemanticity/` | 87.7% monosemantic; CODE+LANGUAGE=40% |
| Co-activation analysis | `stage_2_coactivation/` | Within-layer 1.9× cross-layer |
| Output decomposition | `stage_2_output_decomposition/` | Output/path overlap ratio up to 4.4× |

### 4.4 Stage 3: Causal Steering Validation

**D4 (20 experiments)** — Initial 5 features, 6 circuits
- Features: L0_F1813559, L3_F5150441, L4_F110446948, L6_F2586668, L24_F88478228
- Strength: ±20
- 50% text change rate; mean logprob shift = 0.045

**D5 (30 experiments)** — Frequency-based expansion (5 new features)
- Features: L1_F99962728, L2_F25751073, L5_F7993995, L7_F4828270, L9_F125286525
- Strength: ±20
- 23.3% text change rate; highest-frequency feature produced zero changes

**D6 (30 experiments)** — Essential-pathway features (added 2026-04-08)
- Features: L0_F64712375, L1_F1736314, L21_F5479683, L25_F50014975, L24_F18002975
- Strength: ±20
- 26.7% text change rate; mean KL divergence = 1.448 (highest of any group)
- Domain breakdown: chemistry 0%, geography 20%, history 60%

**Aggregate (80 experiments)**: three-tier dissociation finding — topology predicts distributional perturbation, frequency predicts statistical commonality, output determinism governs text-level changes.

## 5. Key Result Files

Files referenced by specific findings in the paper:

| Finding | File |
|---------|------|
| Bottleneck library | `stage_1_5_bottleneck_library.json` |
| Minimal pathway metrics | `stage_2_minimal_pathways/minimal_pathway_results.json` |
| Multi-algorithm validation | `stage_2_multi_algorithm/multi_algorithm_results.json` |
| Layer energy profiles | `stage_2_layer_energy/layer_energy_analysis.json` |
| Steering D4 results | `stage_3_steering/steering_results.json` |
| Steering D4+D5 results | `stage_3_steering/steering_results.json` |
| Steering D6 results | `stage_2_essential_pathway_steering/essential_pathway_steering_results.json` |
| Polysemanticity classification | `stage_2_polysemanticity/polysemanticity_results.json` |

## 6. Reproducibility

### Requirements
- Python 3.8+, dependencies in `neuronpedia_pipeline/config/requirements.txt`
- Neuronpedia API key (free at neuronpedia.org)
- ~2 GB disk for full pipeline outputs

### Reproducing a single circuit
```bash
python run_full_pipeline.py --prompt "The capital of France is" --model gemma-2-2b
```

### Reproducing a steering experiment set
```bash
python scripts/5_steering_validation.py --quick                 # D4 equivalent
python scripts/stage_2_expanded_steering.py                     # D5 equivalent
python scripts/stage_2_essential_pathway_steering.py            # D6 equivalent
```

### Regenerating Stage 2 statistical analyses
```bash
python scripts/stage_2_cross_category_analysis.py
python scripts/stage_2_layer_energy_analysis.py
python scripts/stage_2_minimal_pathways.py
python scripts/stage_2_multi_algorithm_validation.py
python scripts/stage_2_polysemanticity_analysis.py
```

Each script reads from `data/prompts/` and writes to its own `data/stage_2_*/` directory.

## 7. Limitations of Released Data

1. **Generated data is gitignored** due to size (~2 GB). Recreate by running the pipeline against the prompt list in Appendix A.
2. **Neuronpedia API key** required for generation and semantic annotation — free but rate-limited.
3. **QWEN feature API** not yet publicly available; QWEN circuits are structural only.
4. **Manual semantic annotations** (80 features) are in `semantic_taxonomy_annotations_auto.csv` in the repo root.
5. **Steering experiments** are non-deterministic at the token level but use `temperature=0, seed=42` for reproducibility.

## 8. Contact and Citation

Paper: `CROSS_DOMAIN_CIRCUIT_PAPER.md`
Repository: `github.com/J-Lawrence10/autocircuit` (branch: `main`)
Related work: Anthropic's attribution graph framework; Neuronpedia platform (Decode Research)
