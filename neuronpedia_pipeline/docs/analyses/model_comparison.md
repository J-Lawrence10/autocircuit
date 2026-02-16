# Model Comparison Findings: GEMMA-2-2B vs QWEN3-4B

**Date**: January 28, 2026
**Models Tested**: gemma-2-2b (2B params) vs qwen3-4b (4B params)
**Task**: Factual completion about Paris/France geography

---

## Prompt 1: "Paris is the capital of"

### Outputs

| Model | Top Prediction | Probability | Correct? |
|-------|---------------|-------------|----------|
| **GEMMA-2-2B** | " France" | 85.7% | ✓ YES |
| **QWEN3-4B** | " the" | 20.0% | ✗ NO |

**Winner: GEMMA (smaller model)**

### QWEN's Full Distribution
- 1st: " the" (20.0%) - syntactic filler
- 2nd: " which" (17.7%) - syntactic filler
- 3rd: " France" (8.3%) - correct answer buried
- 4th: " China" (5.7%)
- 5th: " Russia" (2.2%)
- Also: Australia, Egypt in top predictions

**Analysis**: QWEN knows multiple countries but can't decide which one.

### Circuit Comparison

| Metric | GEMMA-2-2B | QWEN3-4B | Difference |
|--------|------------|----------|------------|
| Nodes | 893 | 885 | -1% |
| Edges | 22,954 | 32,225 | **+40%** |
| Density | 0.0288 | 0.0412 | **+43%** |
| Layers | 26 | 36 | +38% |
| Supernodes | 9 | 10 | +11% |
| Connected | No (2 parts) | Yes | More complex |

**Key Finding**: QWEN creates a 40% more complex circuit but performs worse.

---

## Prompt 2: "The capital of France is" (REVERSED)

### Outputs

| Model | Top Prediction | Probability | Correct? |
|-------|---------------|-------------|----------|
| **GEMMA-2-2B** | " a" | 20.7% | ✗ NO |
| **QWEN3-4B** | " Paris" | 80.1% | ✓ YES |

**Winner: QWEN (larger model)**

### Full Distributions

**GEMMA-2-2B:**
- 1st: " a" (20.7%) - article filler
- 2nd: " the" (10.0%) - article filler
- 3rd: " one" (8.1%)
- 4th: " also" (7.8%)
- 5th: " home" (5.0%)
- 6th: " known" (4.8%)
- **No geographic answers in top predictions!**

**QWEN3-4B:**
- 1st: " Paris" (80.1%) - correct!
- 2nd: " in" (5.1%)
- 3rd: " located" (2.7%)
- 4th: " a" (2.4%)

**Analysis**: QWEN handles reversed structure; GEMMA completely fails.

### Circuit Comparison

| Metric | GEMMA-2-2B | QWEN3-4B | Difference |
|--------|------------|----------|------------|
| Nodes | 985 | 805 | -18% |
| Edges | 34,025 | 26,465 | -22% |
| Layers | 26 | 36 | +38% |

**Key Finding**: QWEN uses a **smaller** circuit (fewer nodes/edges) for reversed prompt.

---

## Key Discoveries

### 1. **Prompt Structure Sensitivity**

**GEMMA-2-2B:**
- ✓ Strong on: "X is the capital of ___"
- ✗ Fails on: "The capital of X is ___"
- **Pattern-dependent**: Relies on specific syntactic templates

**QWEN3-4B:**
- ✗ Weak on: "X is the capital of ___" (overthinking)
- ✓ Strong on: "The capital of X is ___"
- **More robust**: Handles different syntactic structures

### 2. **The Overthinking Hypothesis**

**Prompt 1 ("Paris is capital of"):**
- QWEN's 40% more edges → More competing pathways
- Result: Model considers France, China, Russia, Australia, Egypt
- Conclusion: **Complexity creates uncertainty**

**Prompt 2 ("Capital of France is"):**
- QWEN uses FEWER edges than GEMMA (26k vs 34k)
- Result: Direct path to "Paris" at 80% confidence
- Conclusion: **Efficiency creates certainty**

### 3. **Circuit Efficiency vs Complexity**

| Scenario | Model | Edges | Outcome |
|----------|-------|-------|---------|
| Prompt 1 | GEMMA | 22,954 | ✓ Correct (85.7%) |
| Prompt 1 | QWEN | 32,225 | ✗ Wrong (20.0%) |
| Prompt 2 | GEMMA | 34,025 | ✗ Wrong (20.7%) |
| Prompt 2 | QWEN | 26,465 | ✓ Correct (80.1%) |

**Pattern**: **Fewer edges correlates with correct answers!**

### 4. **Syntactic Pattern Matching**

**Both models** show minimal geographic features:
- GEMMA (Prompt 1): 2 geographic tokens in top 50
- QWEN (Prompt 1): 0 geographic tokens in top 50

**Conclusion**: Neither model uses semantic geographic knowledge. Both rely on syntactic patterns, but **QWEN has learned more diverse patterns**.

---

## Mechanistic Interpretability Insights

### Traditional Scaling Hypothesis
> "More parameters → Better performance"

### Our Findings
> "More parameters → More complex circuits → More uncertainty on some patterns, better robustness on others"

### Model Behaviors

**GEMMA-2-2B (Specialist):**
- Memorized specific templates ("X is capital of Y")
- Fails when template changes
- Direct, efficient circuits
- High confidence when pattern matches

**QWEN3-4B (Generalist):**
- Learned multiple syntactic patterns
- More robust to template variations
- Sometimes overthinks → creates overly complex circuits
- Better at novel formulations

---

## Implications for AI Safety

### 1. **Brittleness of Small Models**
- GEMMA fails completely on prompt reformulation
- 85.7% → 20.7% confidence on semantically identical question
- **Risk**: Production systems could fail on paraphrased inputs

### 2. **Uncertainty from Scaling**
- QWEN's 2× parameters don't guarantee 2× performance
- More capacity can create confusion (Prompt 1)
- **Risk**: Larger models may be confidently wrong in unexpected ways

### 3. **Lack of Semantic Understanding**
- Neither model uses geographic features
- Both use syntactic shortcuts
- **Risk**: Models appear to "know" facts but use pattern matching

---

## Testing Recommendations

### To Validate Findings:

1. **Test more prompt structures:**
   - "In France, the capital is"
   - "France's capital is"
   - "What is the capital of France?"
   - Question vs statement structures

2. **Test other factual domains:**
   - Math: "5 + 6 =" vs "What is 5 + 6?"
   - Science: "Water boils at" vs "The boiling point of water is"
   - History: Different date/event orderings

3. **Ablation studies:**
   - Remove syntactic features → does performance collapse?
   - Amplify semantic features → does it improve robustness?

4. **Cross-model comparisons:**
   - Test on gemma-2-9b, gemma-2-27b (if available)
   - Do larger GEMMA models show QWEN's pattern?

---

## Summary

### Question: "Does scaling improve factual reasoning?"

### Answer: **It depends on the prompt structure.**

- **Small models (GEMMA-2-2B)**: Efficient pattern matchers, brittle to reformulation
- **Medium models (QWEN3-4B)**: More robust patterns, but can overthink

### The Real Question: "What circuits are being used?"

- **Efficient circuits** (fewer edges) → Higher confidence
- **Complex circuits** (more edges) → More uncertainty
- **Syntactic features dominate** → Neither model uses semantic reasoning

### Conclusion

**Scaling alone doesn't solve factual reasoning.** Both models:
- Use syntactic shortcuts instead of semantic knowledge
- Show high variance based on prompt structure
- Create different circuit complexities for similar tasks

**True semantic reasoning requires:**
1. Features that represent geographic concepts (not just syntax)
2. Circuits that access those features regardless of prompt structure
3. Validation mechanisms that check factual consistency

---

## Files Generated

**Model-specific directories:**
- `gemma-2-2b_paris-is-the-capital-of/`
- `qwen3-4b_im-endparis-is-the-capital-of/`
- `gemma-2-2b_the-capital-of-france-is/`
- `qwen3-4b_the-capital-of-france-is/`

**Comparison tools:**
- `scripts/compare_models.py` - Token category analysis

**Visualizations:**
- 8 visualizations per model per prompt
- Supernode structure, layer distribution, activation heatmaps
- Feature importance rankings
- Information flow diagrams

---

## Next Steps

1. Document this finding in RESEARCH_FINDINGS.md
2. Test additional prompt structures
3. Investigate feature perturbation (Anthropic's approach)
4. Build cross-prompt feature overlap analysis
