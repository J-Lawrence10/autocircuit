# Neuronpedia Pipeline Documentation

This directory contains all documentation for the traceback graphing research project.

---

## 📄 Papers (Main Research Outputs)

### **[TRACEBACK_GRAPHING_PAPER.md](papers/TRACEBACK_GRAPHING_PAPER.md)** ⭐ **MAIN PAPER**
**~6,800 words** | Scientific journal-style paper

Complete documentation of traceback graphing method, experimental results, and findings. Ready for submission to NeurIPS/ICML/ICLR.

**Key Sections**:
- Novel traceback algorithm with decay normalization
- GEMMA vs QWEN comparative analysis
- Bottleneck position determines factual accuracy
- Shared universal circuit architecture
- Intervention opportunities

**Key Finding**: GEMMA's L5 bottleneck (19% depth) causes factual failures; QWEN's L12 bottleneck (33% depth) preserves semantic information.

---

### **[SOUTHERN_STATE_FINDINGS.md](papers/SOUTHERN_STATE_FINDINGS.md)** 🔍 **CASE STUDY**
Detailed analysis of "The southern most US state is" prompt

**GEMMA**: Predicts " home" (10.5%) - WRONG
**QWEN**: Predicts " Florida" (78.1%) - CORRECT

Complete traceback analysis showing why GEMMA fails:
- ALL paths converge on L5_F7993995 (100% convergence)
- Geographic information filtered out at 19% depth
- No recovery mechanism in downstream layers

---

### **[TOKEN_ATTRIBUTION_VALIDATION.md](papers/TOKEN_ATTRIBUTION_VALIDATION.md)** ✅ **VALIDATION**
Tests and REFUTES the hypothesis that top/bottom final-layer nodes map to different tokens

**Finding**: Both top and bottom nodes converge on the SAME bottleneck (L2_F2604900 for GEMMA).

**Conclusion**: Models use ONE shared circuit for all tokens, not separate circuits per token.

---

### **[TRACEBACK_FINDINGS.md](papers/TRACEBACK_FINDINGS.md)** 📊 **CORE FINDINGS**
Comprehensive summary of all traceback analysis results across multiple prompts

**Bottleneck Patterns**:
- GEMMA: L2-5 (8-19% depth) across all prompts
- QWEN: L12 (33% depth) - consistent architectural pattern

---

### **[TRACEBACK_GRAPHING_CONCEPT.md](papers/TRACEBACK_GRAPHING_CONCEPT.md)** 💡 **CONCEPT**
Theoretical foundation and methodology for traceback graphing

**Algorithm**: Backward BFS with geometric decay (score^0.8) to identify critical paths and bottlenecks.

---

## 📊 Supporting Analyses

### **[arithmetic_comparison.md](analyses/arithmetic_comparison.md)**
Analysis of arithmetic task ("2+2=4") showing how models handle numerical reasoning

### **[model_comparison.md](analyses/model_comparison.md)**
Detailed comparison of GEMMA-2-2B vs QWEN3-4B architectures and performance

### **[self_correction.md](analyses/self_correction.md)**
Analysis of how models self-correct (or fail to correct) incorrect predictions

### **[research_findings.md](analyses/research_findings.md)**
General research findings and observations from the project

---

## 📚 Guides

*(To be created)*

### Getting Started
- Installing dependencies
- Running the pipeline
- Understanding output format

### Pipeline Usage
- Script 1: Graph generation
- Script 2: Graph conversion
- Script 3: Circuit analysis
- Script 3b: Traceback paths
- Script 4: Visualizations

### Troubleshooting
- Common errors and solutions
- Unicode encoding issues
- Interactive mode problems

---

## 🗄️ Archive

The [archive/](archive/) directory contains old documentation for reference:

**Old planning docs**:
- action_plan.md
- reorganization_plan.md
- pathmanager_integration_complete.md

**Old status reports**:
- tier1_complete.md
- tier2_validation_report.md
- pipeline_status.md

**Old guides**:
- deployment_checklist.md
- node_steering_guide.md
- innovation_report.md
- skills_created.md

These are kept for historical reference but are no longer actively maintained.

---

## 🎯 Quick Navigation

**For newcomers**: Start with [TRACEBACK_GRAPHING_PAPER.md](papers/TRACEBACK_GRAPHING_PAPER.md)

**For specific case studies**: See [SOUTHERN_STATE_FINDINGS.md](papers/SOUTHERN_STATE_FINDINGS.md)

**For methodology details**: See [TRACEBACK_GRAPHING_CONCEPT.md](papers/TRACEBACK_GRAPHING_CONCEPT.md)

**For validation**: See [TOKEN_ATTRIBUTION_VALIDATION.md](papers/TOKEN_ATTRIBUTION_VALIDATION.md)

**For comprehensive results**: See [TRACEBACK_FINDINGS.md](papers/TRACEBACK_FINDINGS.md)

---

## 📈 Research Status

**Current Status**: ✅ Major findings documented, paper draft complete

**Completed**:
- ✅ Traceback algorithm implemented and validated
- ✅ GEMMA southern state analysis complete (L5 bottleneck identified)
- ✅ Token attribution hypothesis tested and refuted
- ✅ Shared circuit architecture confirmed
- ✅ Scientific paper drafted (~6,800 words)

**In Progress**:
- ⏳ QWEN southern state traceback (pending completion)
- ⏳ Cross-prompt bottleneck comparison
- ⏳ Feature investigation (what L5_F7993995 represents)

**Planned**:
- 📋 Intervention experiments (ablation, amplification)
- 📋 Additional visualizations and graphs
- 📋 Cross-model generalization testing

---

## 📬 Contributing

This is an active research project. Documentation is updated as new findings emerge.

**Last Updated**: February 2, 2026
