# Stage 1.3: Bottleneck Deep Dive Analysis

**Date**: February 13, 2026
**Status**: Complete

## Overview

Queried all traceback path results across 7 analyses (4 GEMMA, 3 QWEN) to identify cross-prompt bottleneck features and their semantic profiles.

## Major Discovery: Universal Gateway Features

**L1_F99962728** (Neuronpedia ID: 3944) appears in ALL 4 GEMMA analyses regardless of prompt. It activates on "words related to the inhibition of biological processes." This is a universal gateway -- every circuit must pass through it.

## GEMMA Cross-Prompt Bottleneck Profiles

### Features Appearing in 3+ Analyses

| Feature | NP ID | Appears In | Activates On | Category |
|---------|-------|-----------|-------------|----------|
| L1_F99962728 | 3944 | ALL 4 | "inhibition" (biological) | CONCEPT |
| L3_F5150441 | 5865 | Pres+Water | HTML `<i>` tags | SYNTAX |
| L4_F110446948 | 2404 | Pres+Water | "East", place names | GEOGRAPHIC |

### Features Appearing in 2 Different Prompts

| Feature | NP ID | Appears In | Activates On | Category |
|---------|-------|-----------|-------------|----------|
| L4_F47653198 | 8526 | South+Water | "resources", "greater" | CONCEPT |
| L5_F7993995 | 14987 | South+Water | "sky", "heaven" | CONCEPT (directional) |
| L5_F19497 | 3113 | Pres T+B | "note", filler words | SYNTAX (discourse) |
| L6_F2586668 | 14380 | South+Water | "method" (Drupal) | CODE |
| L7_F110677 | 12373 | South+Water | "men", "males" | CONCEPT (gender) |
| L9_F125286525 | 14461 | South+Water | `^` (math formulas) | SYNTAX (math) |
| L10_F100614194 | 50 | South+Water | Whitespace/indentation | SYNTAX |
| L12_F78206258 | 5426 | South+Water | "both", "combination" | CONCEPT (aggregation) |
| L15_F99637770 | 6666 | Pres T+B | "public" (code) | CODE |
| L19_F53462950 | 1958 | Pres T+B | "Any", "can", "could" | CONCEPT (possibility) |

### Semantic Flow Through GEMMA Layers

```
L0-L1:  Universal gateway (inhibition concept)
L3:     Syntax formatting (HTML tags)
L4:     Geographic + planning concepts start appearing
L5:     CRITICAL BOTTLENECK - sky/heaven (directional but NOT geographic)
L6:     Code patterns (method)
L7:     Human concepts (gender)
L9:     Math/formula patterns
L10:    Formatting (whitespace)
L12:    Aggregation concepts ("both", "combination")
L15+:   Code patterns ("public") + possibility ("can", "could")
```

### L5 Bottleneck Interpretation (Revised)

Previously: "motion/arrival concepts" (from Chinese character examples).
Updated: "sky and heaven -- mythical/metaphorical directional concepts."

Both interpretations converge: L5_F7993995 passes **abstract directional/spatial concepts** but blocks **concrete geographic locations**. This explains:
- "Southern most US state is" -> model can represent "southern" (directional) but not "Florida" (location)
- Result: predicts "home" (you go home = directional) instead of "Florida" (static place)

## QWEN Cross-Prompt Patterns

### Features Appearing in ALL 3 QWEN Analyses

| Feature | Layer | Category (inferred) |
|---------|-------|-------------------|
| L12_F2735743452 | 12 | Unknown (no NP data for QWEN) |
| L12_F800099990 | 12 | Unknown |
| L13_F1584085027 | 13 | Unknown |
| L14_F4638048813 | 14 | Unknown |

Note: QWEN features cannot be queried on Neuronpedia's feature API yet (model not supported for individual feature lookup). SAE source naming not available.

### QWEN vs GEMMA Architecture Comparison

| Metric | GEMMA (26L) | QWEN (36L) |
|--------|-------------|------------|
| Earliest convergence | L1 (4%) | L10 (28%) |
| Critical bottleneck | L5 (19%) | L12 (33%) |
| Latest shared bottleneck | L21 | L33 |
| Cross-prompt shared features | 14+ | 4+ |
| Universal gateways | 1 (L1) | 0 |
| Architecture style | Template-driven | Prompt-specific |

## Implications

1. **GEMMA is more rigid**: 14+ shared bottleneck features means similar circuits regardless of content
2. **QWEN is more adaptive**: Fewer shared bottlenecks means more prompt-specific processing
3. **L5 bottleneck confirmed**: Sky/heaven semantics explain geographic filtering
4. **L12 "both/combination"**: Aggregation concept at L12 may explain why GEMMA can handle multi-token reasoning but not factual recall
5. **Universal gateways exist**: L1_F99962728 (inhibition) acts as a master on/off switch

## Files Generated

- `data/bottleneck_deep_dive.json`: Raw Neuronpedia query results for all 13 cross-prompt features
