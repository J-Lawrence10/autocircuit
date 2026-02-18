# AutoCircuit: Neural Circuit Analysis Tools

**AI Safety Camp 2025 - Project #24**

[Original Project Overview](#original-project-overview) | **[Research Breakthrough](#research-breakthrough)** ⭐ | [Quick Start](#quick-start) | [Documentation](#documentation)

---

## 🔬 Research 

**We discovered why language models fail at factual recall** using our novel **traceback graphing** method.

### Key Finding: Bottleneck Position Determines Accuracy

**GEMMA-2-2B**: Early bottleneck (Layer 5, 19% depth) → Filters out semantic information → **Wrong predictions**

**QWEN3-4B**: Late bottleneck (Layer 12, 33% depth) → Preserves semantic information → **Correct predictions**

### Real-World Example: "The southern most US state is"

| Model | Top Prediction | Probability | Correct Answer | Result |
|-------|----------------|-------------|----------------|--------|
| **GEMMA-2-2B** | " home" | 10.5% | " Florida" (rank 6, 2.9%) | ❌ Wrong |
| **QWEN3-4B** | " Florida" | 78.1% | " Florida" (rank 1) | ✅ Correct |

**27× probability difference due to bottleneck position!**

### Research Impact

**What We Discovered**:
1. **Models use ONE shared universal circuit** for all tokens in this prompt (not separate circuits per output)
2. **Early bottlenecks cause systematic failures** by discarding semantic information before processing completes
3. **Bottleneck features are high-leverage intervention targets** - modifying one feature can fix entire categories of failures
4. **Architecture determines behavior** - bottleneck position is more important than model size for factual accuracy

**See Full Research**:
- 📄 [Traceback Graphing Paper](neuronpedia_pipeline/docs/papers/TRACEBACK_GRAPHING_PAPER.md) - Complete scientific paper (~6,800 words)
- 🔍 [Southern State Case Study](neuronpedia_pipeline/docs/papers/SOUTHERN_STATE_FINDINGS.md) - Detailed analysis with data
- ✅ [Validation Results](neuronpedia_pipeline/docs/papers/TOKEN_ATTRIBUTION_VALIDATION.md) - Hypothesis testing

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/[repo]/autocircuit.git
cd autocircuit/neuronpedia_pipeline

# Install dependencies
pip install networkx python-louvain matplotlib requests pyyaml numpy
```

### Run Traceback Analysis

```bash
cd scripts

# 1. Generate attribution graph from Neuronpedia
python 1_generate_graph.py
# Enter prompt: "The southern most US state is"
# Select model: 1 (GEMMA-2-2B) or 2 (QWEN3-4B)

# 2. Convert to pipeline format
python 2_convert_graph.py

# 3. Analyze circuit (detect supernodes, bottlenecks)
python 3_analyze_circuit.py

# 4. Run traceback analysis (identify critical paths) ⭐ KEY INNOVATION
python 3b_traceback_paths.py --top-k 5

# 5. Generate visualizations
python 4_visualize.py
```

**Output**: Comprehensive JSON analysis + 8 PNG visualizations showing circuit structure and bottleneck features

---

## 📁 Project Structure

```
autocircuit/
├── neuronpedia_pipeline/           # 🔬 Main research code (START HERE)
│   ├── README.md                   # Pipeline documentation
│   ├── scripts/                    # Analysis pipeline
│   │   ├── 1_generate_graph.py     # API → raw graph
│   │   ├── 2_convert_graph.py      # Convert format
│   │   ├── 3_analyze_circuit.py    # Detect supernodes
│   │   ├── 3b_traceback_paths.py   # Traceback analysis ⭐ KEY INNOVATION
│   │   ├── 4_visualize.py          # Generate visualizations
│   │   └── path_manager.py         # Utilities
│   ├── docs/                       # All documentation
│   │   ├── papers/                 # Main research papers (5)
│   │   ├── analyses/               # Supporting analyses (4)
│   │   ├── guides/                 # How-to guides
│   │   └── archive/                # Historical reference
│   ├── config/                     # Configuration
│   ├── data/                       # Generated data (gitignored)
│   └── skills/                     # Claude Code skills (6)
│
├── graph-analysis/                 # Additional analysis tools
├── agent-py/                       # Agent-based analysis
├── claude-code-skills/             # Automation skills
├── config/                         # Global configuration
└── data/                           # Global data

```

---

## 📖 Documentation

### Start Here
- **[Neuronpedia Pipeline README](neuronpedia_pipeline/README.md)** - Main pipeline documentation
- **[Documentation Index](neuronpedia_pipeline/docs/README.md)** - Complete guide to all docs

### Research Papers
- **[Traceback Graphing Paper](neuronpedia_pipeline/docs/papers/TRACEBACK_GRAPHING_PAPER.md)** ⭐ Main paper (~6,800 words)
- **[Southern State Findings](neuronpedia_pipeline/docs/papers/SOUTHERN_STATE_FINDINGS.md)** - Case study: Why GEMMA predicts " home" instead of " Florida"
- **[Token Attribution Validation](neuronpedia_pipeline/docs/papers/TOKEN_ATTRIBUTION_VALIDATION.md)** - Proof that models use shared circuits
- **[Traceback Findings](neuronpedia_pipeline/docs/papers/TRACEBACK_FINDINGS.md)** - Cross-prompt patterns
- **[Traceback Graphing Concept](neuronpedia_pipeline/docs/papers/TRACEBACK_GRAPHING_CONCEPT.md)** - Theoretical foundation

### Supporting Analyses
- [Arithmetic Comparison](neuronpedia_pipeline/docs/analyses/arithmetic_comparison.md)
- [Model Comparison](neuronpedia_pipeline/docs/analyses/model_comparison.md)
- [Self-Correction Analysis](neuronpedia_pipeline/docs/analyses/self_correction.md)
- [Research Findings](neuronpedia_pipeline/docs/analyses/research_findings.md)

---

## 🔑 Key Innovations

### 1. Traceback Graphing Algorithm

**Attribution method** that traces backward from model outputs to identify bottleneck features.

**How it works**:
- Start from final-layer predictions
- Use backward BFS with geometric decay (score^0.8) to prevent exponential explosion
- Identify features appearing in 80%+ of paths (bottlenecks)
- Trace causal influence through intermediate layers

**Why it matters**: Traditional attribution identifies which INPUT tokens matter; traceback identifies which INTERMEDIATE FEATURES control behavior.

### 2. Shared Circuit Architecture Discovery

**Finding**: Models use ONE universal circuit for all tokens, not separate per-token circuits.

**Evidence**: Both top-5 and bottom-5 final-layer nodes converge on the SAME bottleneck (L2_F2604900 for GEMMA).

**Implication**: Intervening on bottleneck features affects all outputs simultaneously.

### 3. Bottleneck Position Analysis

**Finding**: WHERE bottleneck occurs determines WHAT information survives.

| Model | Bottleneck | Depth % | Pattern |
|-------|-----------|---------|---------|
| GEMMA | L2-5 | 8-19% | Early compression → Loses semantics |
| QWEN | L12 | 33% | Late bottleneck → Preserves semantics |

**Implication**: Model designers should place bottlenecks AFTER semantic processing (30-40% depth), not before (10-20%).

---

## 🛠️ Requirements

- **Python 3.8+**
- **Dependencies**: `networkx`, `python-louvain`, `matplotlib`, `requests`, `pyyaml`, `numpy`
- **Neuronpedia API Key**: Get from [neuronpedia.org/account](https://neuronpedia.org/account)

---

## 📊 Research Status

**✅ Completed**:
- Traceback graphing algorithm implemented and validated
- GEMMA southern state analysis (L5 bottleneck identified - causes wrong predictions)
- Token attribution hypothesis REFUTED (models use shared circuits)
- Scientific paper drafted (~6,800 words, ready for submission)
- Comprehensive code documentation with detailed annotations

**⏳ In Progress**:
- QWEN southern state traceback completion
- Cross-prompt bottleneck comparison
- Feature semantic investigation (what L5_F7993995 represents)

**📋 Planned**:
- Intervention experiments (ablation, amplification)
- Additional visualizations and graphs
- Cross-model generalization testing (GPT, Claude, Llama)

---


## 🤝 Contributing

This is an active research project from AI Safety Camp 2025.




## Original Project Overview

### Summary

This project systematically discovers interpretable reasoning circuits in large language models by data mining attribution graphs from Neuronpedia's circuit tracer (based on [Anthropic's circuit tracing publication](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)).

**Our approach**: Use LLM agents to automatically collect, process, and analyze attribution graphs across diverse prompt categories (factual recall, arithmetic, linguistic reasoning), identifying recurring computational patterns that represent stable reasoning pathways.

### Key Components

1. **Automated graph collection** via Neuronpedia's API across systematically varied prompts
2. **Graph simplification algorithms** to extract core computational structures while filtering noise
3. **Pattern recognition** to identify circuit motifs that appear across multiple contexts
4. **Validation** through targeted interventions on discovered circuits
5. **Traceback graphing** ⭐ (our novel contribution) to identify bottleneck features

### Theory of Change

Automated circuit discovery could significantly contribute to reducing AGI risks by:
- Democratizing mechanistic interpretability
- Enabling real-time safety monitoring
- Detecting dangerous capabilities before they cause harm
- Accelerating AI alignment research through systematic understanding

**Key Assumptions**:
- AGI systems will continue using transformer-like architectures
- Dangerous AI behaviors correspond to identifiable computational circuits
- Human society maintains coordination to implement interpretability-based safety measures
- Automated interpretability tools will be adopted by AI developers
- Sufficient computational resources for real-time circuit analysis

### Project Phases

**Phase 1**: Automated Circuit Discovery and Feature Annotation (using Anthropic's methods + our traceback graphing)

**Phase 2**: Systematic Circuit Validation and Exploration (intervention experiments, steering)

**Current Status**: Phase 1 complete with major research breakthrough. See [research papers](neuronpedia_pipeline/docs/papers/) for findings.

---

**Version**: 2.0 (Traceback Implementation)

**Last Updated**: February 2, 2026

**Status**: ✅ Major findings documented, ready for team review and external sharing
