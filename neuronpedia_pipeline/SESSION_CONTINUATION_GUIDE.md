# Session Continuation Guide
## Neuronpedia Circuit Analysis Pipeline - Current State & Restart Instructions

**Last Updated**: February 16, 2026
**Current Stage**: Stage 1 COMPLETE — Ready for Stage 2 (Enhanced Visualizations)

---

## 📋 QUICK START PROMPT FOR NEW CHAT

```
I'm continuing work on the Neuronpedia Circuit Analysis Pipeline project.

CONTEXT:
We've built a 5-step automated pipeline that identifies bottleneck features in neural networks
explaining why models fail at factual recall. We discovered that bottleneck POSITION determines
accuracy (GEMMA bottleneck at L5/19% depth → wrong predictions vs QWEN at L12/33% → correct).

We also solved the feature ID mapping problem: neuronpedia_id = circuit_tracer_id % 16384

CURRENT STATUS:
✅ Stage 1.1 Complete: 80 features sampled and auto-annotated
✅ Stage 1.2 Complete: Manual validation done (18 LOW→0 LOW, 3 spot-check corrections)
✅ Stage 1.3 Complete: Bottleneck deep dive (13 features queried, cross-prompt reuse mapped)
✅ Stage 1.4 Complete: 4 distribution visualizations generated
✅ Stage 1.5 Complete: Cross-circuit bottleneck comparison (11 circuits, 51 cross-circuit features)
⏳ Next: Stage 2 (Enhanced Visualizations) or classifier improvements

We have:
- 80-feature VALIDATED CSV (58.8% CODE, 22.5% POLYSEMANTIC, 11.2% CONCEPT, 5% SYNTAX)
- 13 cross-prompt bottleneck features profiled via Neuronpedia
- 4 publication-quality figures (stacked bar, before/after, flow, heatmap)
- L1_F99962728 confirmed as universal gateway ("inhibition") in ALL GEMMA circuits
- QWEN L12 convergence confirmed (features F2735743452, F800099990 in all 3 analyses)
- PowerPoint deck generated (15 slides with speaker notes)
- Complete documentation in neuronpedia_pipeline/docs/

FILES TO REVIEW:
- neuronpedia_pipeline/semantic_taxonomy_annotations_auto.csv (80 features, VALIDATED)
- neuronpedia_pipeline/data/bottleneck_deep_dive.json (13 cross-prompt bottleneck profiles)
- neuronpedia_pipeline/data/stage_1_4_visualizations/ (4 PNGs)
- neuronpedia_pipeline/docs/analyses/bottleneck_deep_dive.md (Stage 1.3 findings)
- neuronpedia_pipeline/Traceback_Graphing_Presentation.pptx (15-slide deck)

IMMEDIATE TASK:
Start Stage 1.5: query bottlenecks from 5+ different circuits, identify common
filtering patterns, build bottleneck semantic library. OR implement classifier
improvements (use NP explanations, Unicode script detection, 10+ examples).

Please read the plan file and recent documentation to get up to speed, then let me know
you're ready to continue.
```

---

## 🎯 PROJECT OVERVIEW

### The Big Question
**Why do language models fail at simple factual recall despite being trained on the data?**

Example:
- Prompt: "The southern most US state is"
- GEMMA-2-2B predicts: " home" (10.5%) ❌
- QWEN3-4B predicts: " Florida" (78.1%) ✅
- **27× probability difference!**

### Our Hypothesis
Models fail due to **early bottleneck features** that filter out semantic information before
the model can use it. It's not a knowledge gap—it's an information filtering problem.

---

## 🔬 KEY DISCOVERIES

### Discovery 1: Bottleneck Position Determines Accuracy
- **GEMMA**: Bottleneck at Layer 5 (19% model depth) → Filters semantics early → Wrong predictions
- **QWEN**: Bottleneck at Layer 12 (33% depth) → Preserves semantics → Correct predictions
- Pattern holds across 10+ circuits (geography, arithmetic, entity recall)

### Discovery 2: Feature ID Mapping Formula
**Problem**: Circuit Tracer uses global IDs (7,993,995), Neuronpedia expects 0-16,383

**Solution**: `neuronpedia_id = circuit_tracer_id % 16384`

**Validation**: 4/4 test features successful, including the famous L5_F7993995 bottleneck

### Discovery 3: L5_F7993995 Bottleneck Semantics
- **Mapped ID**: L5_F14987 (via 7,993,995 % 16,384)
- **Activation examples**: "來的, 来的, Incoming" (motion/arrival concepts)
- **Interpretation**: Filters **static geographic facts**, preserves **motion/directional concepts**
- **Explains failure**: GEMMA prefers "home" (you go home) over "Florida" (static place)

### Discovery 4: Shared Universal Circuits
- Models use ONE circuit for all tokens, NOT separate per-token circuits
- Evidence: Top-5 AND bottom-5 final-layer nodes converge on same bottleneck (100% convergence)
- Implication: Cannot trace individual tokens separately

---

## 📊 CURRENT STATUS

### ✅ Completed Work

**Stage 1.1: Feature Sample Expansion** (Complete)
- 80 features queried across 8 layers (L0, L3, L6, L9, L12, L15, L20, L25)
- Results: 91.2% SEMANTICS, 5.0% SYNTAX, 2.5% POLYSEMANTIC, 1.2% UNKNOWN
- CSV file: `semantic_taxonomy_annotations.csv` (80 rows)
- Bottleneck query script working: 10 bottlenecks from "paris-is-in" circuit

**AI Auto-Annotation** (Complete)
- 80/80 features automatically annotated using decision tree logic
- Distribution:
  - SEMANTICS:CODE: 57 features (71.2%)
  - SEMANTICS:CONCEPT: 9 features (11.2%)
  - POLYSEMANTIC: 7 features (8.8%)
  - SEMANTICS:ENTITY: 3 features (3.8%)
  - SYNTAX: 2 features (2.5%)
  - SEMANTICS:GEOGRAPHIC: 1 feature (1.2%)
  - UNKNOWN: 1 feature (1.2%)
- Confidence: 7 HIGH (9%), 55 MEDIUM (69%), 18 LOW (22%)

**Infrastructure Created**
- `batch_query_features.py` - Automated feature sampling
- `annotate_features_auto.py` - Automatic annotation with decision tree
- `annotate_features_assisted.py` - Interactive human-in-loop annotation
- `query_bottleneck_semantics.py` - Extract and query bottleneck features
- `ANNOTATION_WORKFLOW_STAGE_1_2.md` - Complete annotation guide
- `POWERPOINT_DECK_OUTLINE.md` - 12-slide presentation outline
- Live demo plan (20 min presentation + 10 min Q&A)

### ✅ Recently Completed (Feb 13-16, 2026)

**Stage 1.2: Manual Annotation Validation** (Complete)
- All 18 LOW-confidence features validated and corrected
- 3 MEDIUM-confidence spot-check corrections (L0_F1000, L0_F8000 -> SYNTAX; L3_F1000 -> POLYSEMANTIC)
- Final: 26 HIGH / 54 MEDIUM / 0 LOW confidence
- Auto/manual agreement: 8.8% (classifier needs improvement - plan documented)

**Stage 1.3: Bottleneck Deep Dive** (Complete)
- 13 cross-prompt bottleneck features queried on Neuronpedia
- L1_F99962728 ("inhibition") = universal gateway in ALL GEMMA circuits
- L5_F7993995 ("sky/heaven") confirmed as abstract directional bottleneck
- L4_F110446948 ("East/place names") = geographic feature shared cross-prompt
- QWEN: L12 features appear in all 3 analyses but NP API not available for QWEN
- Results: `data/bottleneck_deep_dive.json`, `docs/analyses/bottleneck_deep_dive.md`

**Stage 1.4: Distribution Visualizations** (Complete)
- 4 figures generated in `data/stage_1_4_visualizations/`:
  1. `category_distribution_by_layer.png` - Stacked bar (CODE dominant, CONCEPT emerges at L6+)
  2. `bottleneck_before_after.png` - SYNTAX vanishes after bottleneck, CONCEPT appears
  3. `semantic_flow_by_layer.png` - Stacked area showing compositional shift
  4. `cross_prompt_convergence_heatmap.png` - Which bottlenecks appear in which prompts

**Stage 1.5: Cross-Circuit Bottleneck Comparison** (Complete - Feb 16, 2026)
- Ran traceback on 6 new circuits (3 GEMMA + 3 QWEN), total now 11 circuits
- Extracted 303 bottleneck features (220 unique) across all circuits
- 51 cross-circuit features identified (appear in 2+ circuits)
- Top cross-circuit features:
  - L34_F415944868: appears in 5 QWEN circuits (universal QWEN bottleneck)
  - L1_F99962728: appears in 4 GEMMA circuits ("inhibition" — universal gateway)
  - L24_F88478228: appears in 4 GEMMA circuits (Lithuanian place names)
  - L5_F7993995: appears in 3 GEMMA circuits ("sky/heaven" — bottleneck filter)
- Queried 30 new GEMMA features on Neuronpedia API (43 total now profiled)
- Results: `data/stage_1_5_bottleneck_library.json`, `data/stage_1_5_cross_circuit_report.md`
- 3 new visualizations: layer distribution, cross-circuit heatmap, convergence distribution

### ⏳ Pending Work

**Stage 2: Enhanced Visualizations** (14 hours, Week 2)
- Semantic-aware node coloring in circuit graphs
- "Thought progression" visualization showing semantic flow
- Interactive Plotly visualizations (hover, zoom, toggle)
- Comprehensive semantic dashboard

**Stage 3: Model Interventions** (17 hours, Week 3)
- Ablation experiments (remove L5_F14987, measure probability shift)
- Amplification experiments (boost geographic features at L4)
- Steering vectors (redirect model toward static geography)
- Statistical validation (p < 0.05, effect size > 15pp)

**Stage 4: Scale to N>1** (18 hours, Week 4)
- Batch analysis of 10 circuits across domains
- Cross-circuit semantic comparison
- Bottleneck taxonomy (Type A: motion-biased, Type B: syntax, etc.)
- Generalization testing and 4 cross-circuit visualizations

---

## 📁 KEY FILES & LOCATIONS

### Data Files
```
neuronpedia_pipeline/
├── semantic_taxonomy_annotations.csv (30 features, original sample)
├── semantic_taxonomy_annotations_auto.csv (80 features, AI-annotated) ⭐ CURRENT
├── data/
│   ├── bottleneck_semantics_paris.json (10 bottleneck features)
│   └── prompts/ (30+ circuit analyses)
│       ├── paris-is-in/
│       ├── the-southern-most-us-state-is/
│       └── [28 more circuits]
```

### Scripts
```
neuronpedia_pipeline/scripts/
├── 1_generate_graph.py (API → raw graph, ~10 sec)
├── 2_convert_graph.py (format conversion, <1 sec)
├── 3_analyze_circuit.py (supernode detection, ~30 sec)
├── 3b_traceback_paths.py (bottleneck identification, ~30 sec) ⭐ KEY INNOVATION
├── 4_visualize.py (8 publication figures, ~10 sec)
├── batch_query_features.py (automated sampling)
├── annotate_features_auto.py (AI auto-annotation) ⭐ NEW
├── annotate_features_assisted.py (interactive annotation) ⭐ NEW
└── query_bottleneck_semantics.py (bottleneck queries) ⭐ NEW
```

### Documentation
```
neuronpedia_pipeline/docs/
├── README.md (documentation index)
├── POWERPOINT_DECK_OUTLINE.md (12-slide presentation) ⭐ NEW
├── ANNOTATION_WORKFLOW_STAGE_1_2.md (annotation guide) ⭐ NEW
├── SESSION_SUMMARY_2025-02-09.md (breakthrough findings)
├── papers/
│   ├── TRACEBACK_GRAPHING_PAPER.md (~6,800 words, peer-ready)
│   ├── SOUTHERN_STATE_FINDINGS.md (case study)
│   ├── TOKEN_ATTRIBUTION_VALIDATION.md (hypothesis testing)
│   └── SEMANTIC_TAXONOMY_METHODOLOGY.md (categorization guide)
└── archive/ (historical docs)
```

### Plan File
```
C:\Users\jbl10\.claude\plans\structured-popping-teacup.md
- Complete Phase 2 plan with 4 stages
- Timeline: 62 hours total (8 workdays)
- Success metrics for each stage
- Live demonstration plan (20 min + Q&A) ⭐ NEW
```

---

## 🔧 TECHNICAL DETAILS

### Pipeline Architecture
**5-Step Automated Process** (~2 minutes total):
1. Generate graph from Neuronpedia API (~10 sec)
2. Convert to pipeline format (<1 sec)
3. Analyze circuit (supernodes, bottlenecks) (~30 sec)
4. Traceback paths (identify critical features) (~30 sec)
5. Visualize (8 publication-quality PNGs) (~10 sec)

### Feature ID Mapping
```python
def map_circuit_to_neuronpedia(circuit_id: int) -> int:
    """Map Circuit Tracer global ID to Neuronpedia per-layer ID."""
    return circuit_id % 16384
```

**Why it works**:
- Circuit Tracer: Global indexing (0 to ~133M for GEMMA)
- Neuronpedia: Per-layer indexing (0 to 16,383)
- 16,384 = 2^14 (power of 2, hash table common size)
- Validation: 4/4 test queries successful (100% success rate)

### Semantic Taxonomy Decision Tree
```
Q1: Are >70% examples punctuation/code/formatting?
    YES → SYNTAX
    NO  → Q2

Q2: Are >70% examples meaningful words with coherent theme?
    YES → SEMANTICS (+ identify sub-category: GEOGRAPHIC, TEMPORAL, ENTITY, CONCEPT, CODE)
    NO  → Q3

Q3: Mix of syntax patterns AND semantic concepts?
    YES → POLYSEMANTIC
    NO  → Q4

Q4: Mix of multiple unrelated semantic domains?
    YES → POLYSEMANTIC
    NO  → Default (mostly meaningful = SEMANTICS, mostly structural = SYNTAX)
```

### API Access (Circuit Tracer)
**Not a Python library** - accessed via Neuronpedia REST API

```python
# Generate graph
POST https://neuronpedia.org/api/graph/generate
JSON: {"prompt": "...", "modelId": "gemma-2-2b"}

# Fetch feature descriptions
GET https://neuronpedia.org/api/feature/gemma-2-2b/5-gemmascope-transcoder-16k/14987
Headers: {'x-api-key': 'sk-np-...'}
```

**Config**: `neuronpedia_pipeline/config/neuronpedia_config.yaml` (API key already populated)

---

## 📈 SUCCESS METRICS

### Stage 1: Semantic Taxonomy (Current)
- ✅ 80+ features annotated (auto-annotation complete)
- ⏳ Manual validation in progress (18 LOW-confidence features)
- ⏳ Inter-rater reliability κ > 0.7 (if multiple annotators)
- ⏳ 3 distribution visualizations (pending Stage 1.4)
- ⏳ Cross-circuit bottleneck comparison (pending Stage 1.5)

### Stage 2: Enhanced Visualizations
- ⏳ Semantic labels on circuit visualizations
- ⏳ Thought progression diagram showing semantic flow
- ⏳ Interactive HTML visualizations (Plotly)
- ⏳ Comprehensive semantic dashboard

### Stage 3: Interventions (Proof of Causality)
- ⏳ Ablating L5_F14987 increases " Florida" probability by >15pp
- ⏳ Effect significant at p < 0.05 across 5+ prompts
- ⏳ Control ablations show <5% change (proves specificity)
- ⏳ Results documented with statistical validation

### Stage 4: Generalization (N>1)
- ⏳ 10 circuits analyzed with bottleneck identification
- ⏳ Cross-circuit semantic patterns documented
- ⏳ Bottleneck taxonomy created (Type A/B/C)
- ⏳ Intervention effectiveness generalizes (p < 0.05)
- ⏳ 4 cross-circuit visualizations

---

## 🎯 IMMEDIATE NEXT STEPS

### Option A: Quick Validation (30 minutes) - RECOMMENDED
1. Open `semantic_taxonomy_annotations_auto.csv` in Excel/Google Sheets
2. Filter by `confidence = LOW` (18 features)
3. Manually verify these 18 features using decision tree
4. Spot-check 5-10 random MEDIUM confidence features
5. Save and proceed to Stage 1.3

### Option B: Interactive Annotation (1-2 hours)
```bash
cd neuronpedia_pipeline/scripts
python annotate_features_assisted.py \
    --input ../semantic_taxonomy_annotations_auto.csv \
    --output ../semantic_taxonomy_annotations_final.csv
```
- Shows each annotation with AI reasoning
- You can accept, modify, or skip
- Progress saved every 5 features

### Option C: Continue to Stage 1.3 (Trust AI)
- Accept AI auto-annotations as-is (69% MEDIUM confidence is reasonable)
- Proceed directly to bottleneck deep dive analysis
- Come back to validation later if needed

---

## 🎤 PRESENTATION MATERIALS

### PowerPoint Deck (12 slides)
**Location**: `neuronpedia_pipeline/docs/POWERPOINT_DECK_OUTLINE.md`

**Structure**:
1. Title: "Neural Circuit Bottlenecks Explain Model Failures"
2. The Big Question (GEMMA vs QWEN comparison)
3. Experimental Overview (backward traceback method)
4. End-to-End Workflow (5-step pipeline diagram)
5. Workflow Part 1 (generation & analysis)
6. Workflow Part 2 (traceback innovation)
7. What We've Produced (datasets, figures, scripts)
8. Key Finding 1 (bottleneck position determines accuracy)
9. Key Finding 2 (L5_F7993995 semantics)
10. Caveats & Limitations
11. Validation Plan (in progress)
12. Next Steps & Asks (GPU compute, multi-model access)

**Plus**: Executive summary slide (backup for short presentations)

### Live Demo Plan (20 min + 10 min Q&A)
**Location**: `C:\Users\jbl10\.claude\plans\structured-popping-teacup.md` (Addendum section)

**5-Part Demo**:
1. The Research Question (2 min)
2. Pipeline Demo - Live Execution (8 min) - Generate → Analyze → Visualize
3. The Breakthrough Discovery (5 min) - Mapping problem → Solution → Finding
4. Skills Demonstration (3 min) - 6 Claude Code skills
5. Semantic Taxonomy Work (2 min) - 80 features, AI annotation

**Materials Checklist**:
- PowerPoint deck
- Terminal (ready in scripts/)
- Browser tabs (Neuronpedia, model outputs)
- File explorer (example circuit, bottleneck JSON, CSV)
- Backup plan (use pre-generated paris-is-in circuit if API fails)

---

## 🔍 RESEARCH FINDINGS SUMMARY

### Main Papers (5 total)
1. **TRACEBACK_GRAPHING_PAPER.md** (~6,800 words) - Complete scientific paper
2. **SOUTHERN_STATE_FINDINGS.md** - GEMMA vs QWEN case study
3. **TOKEN_ATTRIBUTION_VALIDATION.md** - Shared circuit hypothesis test
4. **TRACEBACK_FINDINGS.md** - Cross-prompt bottleneck patterns
5. **TRACEBACK_GRAPHING_CONCEPT.md** - Theoretical foundation

### Key Claims
1. **Bottleneck position determines accuracy** (27× probability difference)
2. **Early decisions are irreversible** (downstream layers cannot recover filtered info)
3. **Shared universal circuits** (not per-token circuits)
4. **High-leverage intervention targets** (single-feature ablation possible)

### Evidence Strength
- ✅ Strong: Bottleneck position correlation (N=10 circuits)
- ✅ Strong: 100% path convergence to bottlenecks
- ✅ Strong: Feature mapping formula (100% query success)
- ⚠️ Medium: Bottleneck semantic interpretation (validated for 1 feature)
- ⏳ Pending: Causal claims (need ablation experiments)

---

## ⚠️ KNOWN LIMITATIONS

### Sample Size
- Current: N=10+ circuits analyzed
- Target: N=50+ for strong generalization claims
- Models: GEMMA-2-2B (6 circuits), QWEN3-4B (4 circuits)

### Model Coverage
- ✅ Validated: GEMMA-2-2B, QWEN3-4B
- ⏳ Untested: GPT, Claude, Llama
- Note: Mapping formula may differ per architecture

### Intervention Evidence
- ✅ Bottlenecks identified
- ⏳ Ablation experiments NOT yet run
- Causal claims theoretical (supported by convergence, not yet proven)

### Confounds
- Training data differences between GEMMA and QWEN
- Tokenization differences
- Architecture variations (attention patterns)

---

## 🎯 ASKS FROM STAKEHOLDERS

### Resource Requests
1. **GPU Compute**: 1× A100 for ~20 hours (ablation experiments)
2. **Multi-Model API Access**: GPT-4, Claude for generalization testing
3. **Feedback**: Critique semantic taxonomy methodology
4. **Collaboration**: Interest in extending to other domains?

### Timeline Expectations
- **Immediate** (2 weeks): Complete Stage 1 (semantic taxonomy)
- **Near-term** (1 month): Scale to N=50 circuits
- **Medium-term** (2 months): Multi-model validation, draft publication
- **Target Venue**: NeurIPS/ICML/ICLR 2026

---

## 🔗 USEFUL COMMANDS

### Run Full Pipeline
```bash
cd neuronpedia_pipeline/scripts

# Generate graph
python 1_generate_graph.py --prompt "Your prompt here"

# Convert
python 2_convert_graph.py

# Analyze
python 3_analyze_circuit.py

# Traceback
python 3b_traceback_paths.py --top-k 5

# Visualize
python 4_visualize.py
```

### Query Specific Features
```bash
# Query by Neuronpedia ID
python query_feature_semantics.py --layer 5 --feature-id 14987

# Query bottlenecks from circuit
python query_bottleneck_semantics.py \
    --circuit ../data/prompts/paris-is-in \
    --output ../data/bottleneck_semantics.json
```

### Annotation Tools
```bash
# Automatic batch annotation
python annotate_features_auto.py \
    --input ../semantic_taxonomy_annotations.csv \
    --output ../semantic_taxonomy_annotations_auto.csv \
    --summary

# Interactive assisted annotation
python annotate_features_assisted.py \
    --input ../semantic_taxonomy_annotations_auto.csv \
    --output ../semantic_taxonomy_annotations_final.csv \
    --start-row 2
```

### Using Claude Code Skills
```bash
/neuronpedia-fetch      # Generate attribution graph
/neuronpedia-convert    # Convert format
/neuronpedia-analyze    # Detect supernodes
/neuronpedia-visualize  # Generate figures
/neuronpedia-compare    # Cross-prompt analysis
/neuronpedia-validate   # Data quality checks
```

---

## 📞 GETTING HELP

### Documentation Hierarchy
1. **Quick Start**: `neuronpedia_pipeline/README.md`
2. **Research Papers**: `neuronpedia_pipeline/docs/papers/`
3. **Session Summaries**: `neuronpedia_pipeline/docs/SESSION_SUMMARY_*.md`
4. **Plan File**: `C:\Users\jbl10\.claude\plans\structured-popping-teacup.md`
5. **This Guide**: `neuronpedia_pipeline/SESSION_CONTINUATION_GUIDE.md`

### Common Issues
- **API connection fails**: Check `config/neuronpedia_config.yaml` for API key
- **Unicode errors on Windows**: Scripts already have encoding fixes (UTF-8 wrappers)
- **Missing dependencies**: `pip install -r config/requirements.txt`
- **Feature ID mismatch**: Use modulo 16384 mapping formula

---

## ✅ CHECKLIST FOR NEW SESSION

Before starting work:
- [ ] Read this continuation guide completely
- [ ] Review plan file: `C:\Users\jbl10\.claude\plans\structured-popping-teacup.md`
- [ ] Check current CSV: `semantic_taxonomy_annotations_auto.csv`
- [ ] Verify API access: `python scripts/1_generate_graph.py --test-connection`
- [ ] Understand current stage: Stage 1 COMPLETE, Stage 2 next
- [ ] Know immediate task: Stage 2 (Enhanced Visualizations) or classifier improvements

Ready to continue? Ask Claude to pick up where we left off using the quick start prompt at the top of this document.

---

**Document Created**: February 9, 2026
**Last Updated**: February 16, 2026
**Current Stage**: Stage 1 COMPLETE — Ready for Stage 2 (Enhanced Visualizations)
**Total Progress**: Stage 1 complete (1.1-1.5 done); Stage 2-4 pending
