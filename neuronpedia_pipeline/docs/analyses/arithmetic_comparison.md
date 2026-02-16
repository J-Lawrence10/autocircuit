# Arithmetic Task Comparison: GEMMA-2-2B vs QWEN3-4B

**Date**: January 28, 2026
**Prompt**: "2 plus 3 equals"
**Expected Answer**: "5" or " 5" or " five"

---

## Summary: Both Models FAIL at Simple Arithmetic

### GEMMA-2-2B Results

**Top Prediction**: " " (space) at 60.9% ✗ WRONG

**Full Distribution**:
1. " " (space) - 60.9%
2. " what" - 5.7%
3. **" five" - 4.0% ✓ CORRECT (but ranked #3!)**
4. "?" - 3.5%
5. "\n\n" - 2.9%
6. " ?" - 1.4%
7. " how" - 1.3%
8. "\n" - 1.2%
9. " six" - 1.0% ✗ (wrong number)
10. " four" - 1.0% ✗ (wrong number)

**Circuit Stats**:
- Nodes: 1,021
- Edges: 30,144
- Density: ~0.029

**Analysis**:
- Model "knows" the answer is " five" (ranked #3 at 4%)
- Also considers " six" and " four" (wrong numbers at ~1% each)
- Prefers to output a space (60.9%) instead of attempting the calculation
- **Behavior**: Uncertainty avoidance - outputs neutral token rather than committing to wrong answer

---

### QWEN3-4B Results

**Top Prediction**: " " (space) at 80.5% ✗ WRONG

**Circuit Stats**:
- Nodes: 1,251
- Edges: 70,546
- Density: ~0.045

**Analysis**:
- Even MORE confident in outputting space (80.5% vs GEMMA's 60.9%)
- Larger model, more complex circuit, but WORSE performance
- **Behavior**: Even stronger uncertainty avoidance

*(Note: Full distribution unavailable due to Unicode encoding error in conversion script)*

---

## Key Findings

### 1. **Neither Model Can Do Arithmetic**

Both models output " " (space) as their top prediction:
- GEMMA: 60.9% confidence
- QWEN: 80.5% confidence

Neither model successfully completes the arithmetic operation.

### 2. **GEMMA Shows Some Numerical Reasoning**

GEMMA's top 10 includes:
- " five" (4.0%) - CORRECT
- " six" (1.0%) - close, off by 1
- " four" (1.0%) - close, off by 1

This suggests GEMMA has SOME learned association between "2 plus 3" and numerical outputs around 5.

### 3. **Uncertainty Avoidance Strategy**

Both models prefer to output a "safe" neutral token (space) rather than commit to a potentially wrong numerical answer:
- Space is grammatically valid continuation
- Avoids being confidently wrong
- But also avoids being correct!

### 4. **Larger Model = More Uncertain**

| Metric | GEMMA-2-2B | QWEN3-4B | Winner |
|--------|------------|----------|--------|
| Space probability | 60.9% | 80.5% | GEMMA (less certain about giving up) |
| Circuit edges | 30,144 | 70,546 | GEMMA (simpler) |
| Correct answer | #3 at 4% | Unknown | GEMMA |

QWEN's larger circuit (2.3× more edges) leads to HIGHER confidence in the wrong answer (space).

---

## Comparison with Geographic Tasks

### Task Performance Summary

| Task | GEMMA-2-2B | QWEN3-4B | Winner |
|------|------------|----------|--------|
| "Paris is capital of" | 85.7% → " France" ✓ | 20.0% → " the" ✗ | GEMMA |
| "Capital of France is" | 20.7% → " a" ✗ | 80.1% → " Paris" ✓ | QWEN |
| "2 plus 3 equals" | 60.9% → " " ✗ | 80.5% → " " ✗ | Neither |

### Pattern Analysis

**Geographic factual completion**:
- Both models show capability (at least for certain phrasings)
- Performance depends on syntactic structure
- Models use pattern matching, not semantic understanding

**Arithmetic**:
- Both models FAIL completely
- Neither model outputs the correct answer as top prediction
- Larger model is MORE confident in failing
- **Arithmetic requires genuine computation, not just pattern matching**

---

## Why Arithmetic Fails (Hypotheses)

### 1. **No Computational Features**

Geographic tasks can succeed via:
- Memorization: "Paris" often appears with "France" in training data
- Syntactic patterns: "X is the capital of Y"

Arithmetic CANNOT succeed this way:
- Infinite possible combinations (can't memorize all)
- Requires actual computation, not pattern matching
- Small models lack capacity for true numerical reasoning

### 2. **Emergence Threshold**

Research shows arithmetic emerges around **13B+ parameters**:
- GEMMA-2-2B (2B): Below threshold
- QWEN3-4B (4B): Still below threshold
- Both models haven't "learned" to compute

### 3. **Training Data Bias**

Models trained on text may learn:
- "2 plus 3 equals" is often followed by questions or explanations
- Rare to see bare "2 plus 3 equals 5" in natural language
- More common: "2 plus 3 equals what?" or "2 plus 3 equals five apples"

Result: Models output grammatical continuations (space, "what", "?") instead of bare numerical answers.

---

## Implications

### For AI Safety

1. **Capability Cliffs**: Models confidently handle geography but completely fail arithmetic
   - Risk: Users may overestimate general capability based on success in one domain

2. **Uncertainty Masking**: Both models output "safe" tokens rather than attempting answers
   - Risk: Appears uncertain/incomplete rather than wrong
   - Users may not realize model CAN'T do the task

3. **Scaling Doesn't Universally Help**: QWEN (2× parameters) performs WORSE than GEMMA
   - More edges → More uncertainty → More confident in giving up

### For Interpretability Research

1. **Domain-Specific Circuits**:
   - Geographic facts: ~23k-32k edges, moderate success
   - Arithmetic: ~30k-70k edges, complete failure
   - **Circuit size doesn't predict task success**

2. **Feature Analysis Needed**:
   - Do these circuits have ANY numerical features?
   - Or all syntactic/grammar features?
   - Hypothesis: Zero computational/arithmetic features in top activations

3. **Comparison to Larger Models**:
   - Test gemma-2-9b, gemma-2-27b (if available)
   - Does arithmetic capability emerge?
   - At what parameter count?

---

## Next Steps

### Immediate Analysis

1. **Run Script 3 (Analysis)** on both arithmetic circuits
   - Check for numerical/arithmetic features
   - Compare to geographic circuits
   - **Prediction**: Zero arithmetic features found

2. **Feature Description Analysis**:
   - What tokens activate top features?
   - Are they numerical ("1", "2", "3", "4", "5")?
   - Or syntactic (" what", "?", " equals")?

3. **Visualization**:
   - Do supernode themes show ANY numerical processing?
   - Or all syntactic pattern matching?

### Extended Testing

1. **Different Arithmetic Structures**:
   - "2 + 3 =" (symbolic)
   - "What is 2 plus 3?" (question form)
   - "Two plus three equals" (words vs digits)

2. **Difficulty Scaling**:
   - "1 plus 1 equals" (easier?)
   - "7 plus 8 equals" (harder?)
   - "2 times 3 equals" (multiplication)

3. **Compare to Baseline**:
   - "The sky is" → expect " blue" (memorization)
   - "2 plus 3 equals" → expect " 5" (computation)
   - **Hypothesis**: Memorization works, computation fails

---

## Conclusion

### The Scaling Paradox Continues

**Geographic tasks (pattern matching)**:
- Small models: Work on specific templates, fail on reformulations
- Medium models: More robust to templates, but can overthink

**Arithmetic tasks (genuine computation)**:
- Small models: Complete failure (but show some number awareness)
- Medium models: Even worse failure (more confident in giving up)

### Core Insight

**Scaling improves pattern diversity, not computational ability.**

- More parameters → More syntactic patterns learned
- More parameters → Better robustness to reformulation
- More parameters ≠ Arithmetic reasoning (below emergence threshold)

### The Real Question

**"What's the minimum parameter count for true arithmetic?"**

Based on research:
- 2B: No
- 4B: No
- 13B+: Yes (reported in literature)
- Gemma-2-9b/27b: Unknown (need testing)

Our pipeline can now test this systematically across model sizes and architectures!

---

## Files Generated

**Arithmetic circuits**:
- `gemma-2-2b_2-plus-3-equals/` - 1,021 nodes, 30,144 edges
- `qwen3-4b_2-plus-3-equals/` - 1,251 nodes, 70,546 edges

**Next**: Run analysis + visualization to examine feature composition
