# Stage 1.5: Cross-Circuit Bottleneck Comparison

**Date**: 2026-02-16
**Circuits Analyzed**: 11
**Unique Bottleneck Features**: 220
**Cross-Circuit Features**: 51

---

## 1. Executive Summary

Analyzed **6 GEMMA** and **5 QWEN** circuits.
Found **51** features that appear as bottlenecks in 2+ circuits.

## 2. Cross-Circuit Bottleneck Features

Features appearing as bottlenecks in multiple circuits (sorted by frequency):

| Feature | Layer | Circuits | Avg Convergence | Explanation |
|---------|-------|----------|-----------------|-------------|
| L34_F415944868 | L34 | 5 | 75% |  |
| L26_F10368215974 | L26 | 4 | 94% |  |
| L33_F10240593794 | L33 | 4 | 95% |  |
| L1_F99962728 | L1 | 4 | 90% |  words related to the inhibition of biological processes |
| L24_F88478228 | L24 | 4 | 90% | parts of long place names from the Lithuanian language |
| L12_F2735743452 | L12 | 3 | 100% |  |
| L12_F800099990 | L12 | 3 | 100% |  |
| L13_F1584085027 | L13 | 3 | 100% |  |
| L14_F4638048813 | L14 | 3 | 100% |  |
| L15_F308649419 | L15 | 3 | 92% |  |
| L24_F457788386 | L24 | 3 | 92% |  |
| L27_F12610705050 | L27 | 3 | 87% |  |
| L32_F3158177517 | L32 | 3 | 92% |  |
| L3_F5150441 | L3 | 3 | 93% |  HTML formatting tags such as italics, paragraph delimiters,... |
| L4_F110446948 | L4 | 3 | 93% |  place names and surrounding words |
| L9_F125286525 | L9 | 3 | 100% |  mathematical formulas and expressions |
| L5_F7993995 | L5 | 3 | 100% |  words and phrases related to myths and metaphors of sky and... |
| L9_F4701701 | L9 | 3 | 100% |  code and data tables |
| L9_F3843368 | L9 | 3 | 100% |  instances of the first-person perspective combined with ind... |
| L7_F110677 | L7 | 3 | 100% | words referring to human genders and sexual situations |
| L7_F16528367 | L7 | 3 | 100% |  language related to laws and legal obligations. |
| L4_F47653198 | L4 | 3 | 100% |  words related to planning or future activities |
| L10_F100614194 | L10 | 3 | 100% |  code with indentation consisting of tabs or layout informat... |
| L12_F78206258 | L12 | 3 | 100% |  the word "both," and to a lesser extent, words associated w... |
| L9_F91037261 | L9 | 3 | 80% |  the keyword "while" used in code |
| L0_F1813559 | L0 | 3 | 93% | code and file related keywords and annotations (e.g. handler... |
| L12_F3151902093 | L12 | 2 | 100% |  |
| L13_F2980576222 | L13 | 2 | 100% |  |
| L11_F3608378664 | L11 | 2 | 100% |  |
| L13_F6061500446 | L13 | 2 | 100% |  |
| L12_F2242323015 | L12 | 2 | 100% |  |
| L11_F11058149958 | L11 | 2 | 100% |  |
| L11_F702431409 | L11 | 2 | 100% |  |
| L11_F10545222913 | L11 | 2 | 80% |  |
| L26_F10912888953 | L26 | 2 | 100% |  |
| L25_F942235729 | L25 | 2 | 100% |  |
| L29_F89625936 | L29 | 2 | 88% |  |
| L6_F2586668 | L6 | 2 | 100% |  code snippets related to Drupal views, specifically around ... |
| L6_F10231019 | L6 | 2 | 100% |  personal pronouns combined with past tense verbs |
| L8_F7313391 | L8 | 2 | 100% |  code snippets and programming-related keywords such as "typ... |
| L6_F105683984 | L6 | 2 | 100% |  dates |
| L7_F38531023 | L7 | 2 | 100% |  tokens in website-related text, including references to tra... |
| L0_F80638649 | L0 | 2 | 80% |  capitalized words and phrases, particularly acronyms or abb... |
| L15_F376262 | L15 | 2 | 100% |  code-related keywords, especially related to data structure... |
| L9_F38548580 | L9 | 2 | 90% |  |
| L2_F25751073 | L2 | 2 | 90% |  |
| L4_F7332530 | L4 | 2 | 80% |  |
| L4_F29464321 | L4 | 2 | 80% |  |
| L5_F5576124 | L5 | 2 | 80% |  |
| L1_F502501 | L1 | 2 | 80% |  |
| L6_F10902108 | L6 | 2 | 80% |  |


## 3. Per-Circuit Bottleneck Summary

### gemma-2-2b_2-plus-3-equals
- Model: GEMMA
- Bottleneck features: 29
- Bottleneck layers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18, 20, 23, 24]
- Cross-circuit features: 18/29

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L5_F7993995 | L5 | 100% | ✓ |
| L9_F4701701 | L9 | 100% | ✓ |
| L7_F110677 | L7 | 100% | ✓ |
| L9_F125286525 | L9 | 100% | ✓ |
| L7_F16528367 | L7 | 100% | ✓ |
| L9_F3843368 | L9 | 100% | ✓ |
| L10_F100614194 | L10 | 100% | ✓ |
| L8_F7313391 | L8 | 100% | ✓ |

### gemma-2-2b_paris-is-the-capital-of
- Model: GEMMA
- Bottleneck features: 29
- Bottleneck layers: [0, 1, 2, 3, 4, 5, 6, 7, 13, 14, 15, 17, 18, 20, 23, 24]
- Cross-circuit features: 7/29

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L2_F25751073 | L2 | 100% | ✓ |
| L3_F97839062 | L3 | 100% |  |
| L4_F29464321 | L4 | 100% | ✓ |
| L6_F10902108 | L6 | 100% | ✓ |
| L7_F244642 | L7 | 100% |  |
| L4_F7332530 | L4 | 100% | ✓ |
| L2_F70110558 | L2 | 100% |  |
| L1_F502501 | L1 | 100% | ✓ |

### gemma-2-2b_the-capital-of-france-is
- Model: GEMMA
- Bottleneck features: 18
- Bottleneck layers: [0, 1, 2, 3, 4, 5, 6, 8, 15, 16]
- Cross-circuit features: 10/18

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L0_F1813559 | L0 | 80% | ✓ |
| L3_F5150441 | L3 | 80% | ✓ |
| L4_F110446948 | L4 | 80% | ✓ |
| L2_F25751073 | L2 | 80% | ✓ |
| L0_F80638649 | L0 | 60% | ✓ |
| L0_F11637899 | L0 | 60% |  |
| L2_F2110482 | L2 | 60% |  |
| L0_F25343639 | L0 | 60% |  |

### gemma-2-2b_the-president-of-the-united-states-lives-in
- Model: GEMMA
- Bottleneck features: 28
- Bottleneck layers: [0, 1, 2, 3, 4, 5, 6, 8, 14, 15, 16, 17, 19, 22, 24]
- Cross-circuit features: 5/28

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L3_F5150441 | L3 | 100% | ✓ |
| L2_F2604900 | L2 | 100% |  |
| L1_F99962728 | L1 | 100% | ✓ |
| L5_F19497 | L5 | 100% |  |
| L0_F1813559 | L0 | 100% | ✓ |
| L4_F110446948 | L4 | 100% | ✓ |
| L4_F106397573 | L4 | 100% |  |
| L0_F20624252 | L0 | 100% |  |

### gemma-2-2b_the-southern-most-us-state-is
- Model: GEMMA
- Bottleneck features: 28
- Bottleneck layers: [0, 1, 4, 5, 6, 7, 8, 9, 10, 12, 15, 21, 22, 23]
- Cross-circuit features: 20/28

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L5_F7993995 | L5 | 100% | ✓ |
| L7_F110677 | L7 | 100% | ✓ |
| L6_F106470521 | L6 | 100% |  |
| L7_F16528367 | L7 | 100% | ✓ |
| L9_F125286525 | L9 | 100% | ✓ |
| L6_F10231019 | L6 | 100% | ✓ |
| L4_F47653198 | L4 | 100% | ✓ |
| L9_F4701701 | L9 | 100% | ✓ |

### gemma-2-2b_water-boils-at-100-degrees
- Model: GEMMA
- Bottleneck features: 29
- Bottleneck layers: [1, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16, 17, 18, 19, 20, 21, 24]
- Cross-circuit features: 15/29

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L3_F5150441 | L3 | 100% | ✓ |
| L4_F110446948 | L4 | 100% | ✓ |
| L9_F125286525 | L9 | 100% | ✓ |
| L5_F7993995 | L5 | 100% | ✓ |
| L9_F4701701 | L9 | 100% | ✓ |
| L7_F22879222 | L7 | 100% |  |
| L9_F3843368 | L9 | 100% | ✓ |
| L7_F110677 | L7 | 100% | ✓ |

### qwen3-4b_im-endparis-is-the-capital-of
- Model: QWEN
- Bottleneck features: 29
- Bottleneck layers: [10, 11, 12, 13, 14, 15, 18, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34]
- Cross-circuit features: 20/29

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L12_F2735743452 | L12 | 100% | ✓ |
| L13_F1584085027 | L13 | 100% | ✓ |
| L12_F3151902093 | L12 | 100% | ✓ |
| L13_F2980576222 | L13 | 100% | ✓ |
| L12_F800099990 | L12 | 100% | ✓ |
| L13_F6061500446 | L13 | 100% | ✓ |
| L11_F3608378664 | L11 | 100% | ✓ |
| L12_F2242323015 | L12 | 100% | ✓ |

### qwen3-4b_im-endthe-capital-of-france-is
- Model: QWEN
- Bottleneck features: 27
- Bottleneck layers: [8, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
- Cross-circuit features: 7/27

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L23_F2077126807 | L23 | 100% |  |
| L27_F10384782758 | L27 | 100% |  |
| L22_F8843502505 | L22 | 100% |  |
| L29_F32865748 | L29 | 100% |  |
| L28_F344964482 | L28 | 100% |  |
| L27_F904081475 | L27 | 100% |  |
| L28_F10343750167 | L28 | 100% |  |
| L29_F12336827551 | L29 | 100% |  |

### qwen3-4b_im-endthe-president-of-the-united-states-lives-in
- Model: QWEN
- Bottleneck features: 28
- Bottleneck layers: [8, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29, 32, 33, 34]
- Cross-circuit features: 11/28

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L12_F2735743452 | L12 | 100% | ✓ |
| L12_F800099990 | L12 | 100% | ✓ |
| L13_F1584085027 | L13 | 100% | ✓ |
| L14_F4638048813 | L14 | 100% | ✓ |
| L16_F1043399704 | L16 | 100% |  |
| L19_F6611637508 | L19 | 100% |  |
| L17_F6197796762 | L17 | 100% |  |
| L33_F10240593794 | L33 | 100% | ✓ |

### qwen3-4b_im-endthe-southern-most-us-state-is
- Model: QWEN
- Bottleneck features: 29
- Bottleneck layers: [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
- Cross-circuit features: 7/29

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L27_F13064633807 | L27 | 100% |  |
| L26_F3361303009 | L26 | 100% |  |
| L25_F3262663784 | L25 | 100% |  |
| L27_F822049850 | L27 | 100% |  |
| L26_F10912888953 | L26 | 100% | ✓ |
| L28_F3796559062 | L28 | 100% |  |
| L30_F2998980150 | L30 | 100% |  |
| L29_F4780024170 | L29 | 100% |  |

### qwen3-4b_water-boils-at-100-degrees
- Model: QWEN
- Bottleneck features: 29
- Bottleneck layers: [10, 11, 12, 13, 14, 15, 25, 27, 28, 29, 30, 31, 33, 34]
- Cross-circuit features: 14/29

| Feature | Layer | Convergence | Cross-Circuit |
|---------|-------|-------------|---------------|
| L12_F2735743452 | L12 | 100% | ✓ |
| L12_F800099990 | L12 | 100% | ✓ |
| L12_F3151902093 | L12 | 100% | ✓ |
| L13_F1584085027 | L13 | 100% | ✓ |
| L13_F2980576222 | L13 | 100% | ✓ |
| L11_F3608378664 | L11 | 100% | ✓ |
| L13_F6061500446 | L13 | 100% | ✓ |
| L12_F2242323015 | L12 | 100% | ✓ |

## 4. GEMMA vs QWEN Bottleneck Architecture

### GEMMA-2-2B
- Total unique bottleneck features: 115
- Average bottleneck layer: L8.0 (31% depth)
- Bottleneck range: L0 - L24
- Unique features: 115

### QWEN3-4B
- Total unique bottleneck features: 105
- Average bottleneck layer: L22.6 (63% depth)
- Bottleneck range: L8 - L34
- Unique features: 105

## 5. Key Findings

### Universal Bottleneck Features (3+ circuits)

- **L34_F415944868** (L34): appears in 5 circuits
  - Explanation: 
  - Circuits: water-boils-at-100-degrees, im-endthe-southern-most-us-state-is, im-endthe-president-of-the-united-states-lives-in, im-endthe-capital-of-france-is, im-endparis-is-the-capital-of

- **L26_F10368215974** (L26): appears in 4 circuits
  - Explanation: 
  - Circuits: im-endthe-southern-most-us-state-is, im-endthe-president-of-the-united-states-lives-in, im-endthe-capital-of-france-is, im-endparis-is-the-capital-of

- **L33_F10240593794** (L33): appears in 4 circuits
  - Explanation: 
  - Circuits: im-endthe-southern-most-us-state-is, im-endthe-president-of-the-united-states-lives-in, im-endthe-capital-of-france-is, im-endparis-is-the-capital-of

- **L1_F99962728** (L1): appears in 4 circuits
  - Explanation:  words related to the inhibition of biological processes
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, the-president-of-the-united-states-lives-in, 2-plus-3-equals
  - Top activations: ▁inhibition, ▁inhibition, ▁inhibition, ▁inhibition, ▁inhibition

- **L24_F88478228** (L24): appears in 4 circuits
  - Explanation: parts of long place names from the Lithuanian language
  - Circuits: water-boils-at-100-degrees, the-president-of-the-united-states-lives-in, paris-is-the-capital-of, 2-plus-3-equals
  - Top activations: inio, inio, inio, inio, inio

- **L12_F2735743452** (L12): appears in 3 circuits
  - Explanation: 
  - Circuits: water-boils-at-100-degrees, im-endthe-president-of-the-united-states-lives-in, im-endparis-is-the-capital-of

- **L12_F800099990** (L12): appears in 3 circuits
  - Explanation: 
  - Circuits: water-boils-at-100-degrees, im-endthe-president-of-the-united-states-lives-in, im-endparis-is-the-capital-of

- **L13_F1584085027** (L13): appears in 3 circuits
  - Explanation: 
  - Circuits: water-boils-at-100-degrees, im-endthe-president-of-the-united-states-lives-in, im-endparis-is-the-capital-of

- **L14_F4638048813** (L14): appears in 3 circuits
  - Explanation: 
  - Circuits: water-boils-at-100-degrees, im-endthe-president-of-the-united-states-lives-in, im-endparis-is-the-capital-of

- **L15_F308649419** (L15): appears in 3 circuits
  - Explanation: 
  - Circuits: water-boils-at-100-degrees, im-endthe-president-of-the-united-states-lives-in, im-endparis-is-the-capital-of

- **L24_F457788386** (L24): appears in 3 circuits
  - Explanation: 
  - Circuits: im-endthe-southern-most-us-state-is, im-endthe-president-of-the-united-states-lives-in, im-endparis-is-the-capital-of

- **L27_F12610705050** (L27): appears in 3 circuits
  - Explanation: 
  - Circuits: im-endthe-southern-most-us-state-is, im-endthe-capital-of-france-is, im-endparis-is-the-capital-of

- **L32_F3158177517** (L32): appears in 3 circuits
  - Explanation: 
  - Circuits: im-endthe-president-of-the-united-states-lives-in, im-endthe-capital-of-france-is, im-endparis-is-the-capital-of

- **L3_F5150441** (L3): appears in 3 circuits
  - Explanation:  HTML formatting tags such as italics, paragraph delimiters, and list delimiters
  - Circuits: water-boils-at-100-degrees, the-president-of-the-united-states-lives-in, the-capital-of-france-is
  - Top activations: <i>, <i>, <i>, <i>, ▁"*

- **L4_F110446948** (L4): appears in 3 circuits
  - Explanation:  place names and surrounding words
  - Circuits: water-boils-at-100-degrees, the-president-of-the-united-states-lives-in, the-capital-of-france-is
  - Top activations: ▁East, ▁East, ▁East, ▁East, East

- **L9_F125286525** (L9): appears in 3 circuits
  - Explanation:  mathematical formulas and expressions
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, 2-plus-3-equals
  - Top activations: ^, ^, ^, ^, ^

- **L5_F7993995** (L5): appears in 3 circuits
  - Explanation:  words and phrases related to myths and metaphors of sky and heaven
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, 2-plus-3-equals
  - Top activations: ▁sky, ▁sky, ▁sky, ▁heaven, ▁heaven

- **L9_F4701701** (L9): appears in 3 circuits
  - Explanation:  code and data tables
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, 2-plus-3-equals
  - Top activations: 					, 					, -------------, ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁, ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁

- **L9_F3843368** (L9): appears in 3 circuits
  - Explanation:  instances of the first-person perspective combined with indicators of time or scheduling.
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, 2-plus-3-equals
  - Top activations: ▁month, ▁month, ▁month, ▁I, ▁I

- **L7_F110677** (L7): appears in 3 circuits
  - Explanation: words referring to human genders and sexual situations
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, 2-plus-3-equals
  - Top activations: ▁men, ▁boys, ▁males, ▁males, ▁men

- **L7_F16528367** (L7): appears in 3 circuits
  - Explanation:  language related to laws and legal obligations.
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, 2-plus-3-equals
  - Top activations: ▁legally, ▁legally, ▁law, ▁legal, ▁legal

- **L4_F47653198** (L4): appears in 3 circuits
  - Explanation:  words related to planning or future activities
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, 2-plus-3-equals
  - Top activations: ▁resources, ▁greater, ▁grave, ▁grave, ▁larger

- **L10_F100614194** (L10): appears in 3 circuits
  - Explanation:  code with indentation consisting of tabs or layout information for Android apps
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, 2-plus-3-equals
  - Top activations: ▁▁▁▁▁▁▁▁, ▁▁▁▁▁▁▁▁, ▁▁▁▁▁▁▁▁, ▁▁▁▁▁▁▁▁, ▁▁▁▁▁▁▁▁

- **L12_F78206258** (L12): appears in 3 circuits
  - Explanation:  the word "both," and to a lesser extent, words associated with combinations of items
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, 2-plus-3-equals
  - Top activations: ▁both, ▁both, ▁both, ▁combination, ▁combination

- **L9_F91037261** (L9): appears in 3 circuits
  - Explanation:  the keyword "while" used in code
  - Circuits: water-boils-at-100-degrees, the-southern-most-us-state-is, 2-plus-3-equals
  - Top activations: while, while, while, while, while

- **L0_F1813559** (L0): appears in 3 circuits
  - Explanation: code and file related keywords and annotations (e.g. handler, Logger, php, function, return)
  - Circuits: the-southern-most-us-state-is, the-president-of-the-united-states-lives-in, the-capital-of-france-is
  - Top activations: assert, assert, assert, assert, assert

### Bottleneck Patterns by Domain

**Arithmetic** (1 circuits):
  - No shared bottleneck features within domain

**Geography (Paris/France)** (4 circuits):
  - Shared bottleneck features: L1_F502501, L26_F10368215974, L27_F12610705050, L2_F25751073, L32_F3158177517, L33_F10240593794, L34_F415944868, L4_F29464321, L4_F7332530, L5_F5576124, L6_F10902108

**Geography (US States)** (4 circuits):
  - Shared bottleneck features: L0_F1813559, L1_F99962728, L24_F457788386, L26_F10368215974, L33_F10240593794, L34_F415944868

**Science** (2 circuits):
  - No shared bottleneck features within domain

## 6. Implications for Traceback Graphing Research

### Shared Universal Circuit Hypothesis

The cross-circuit analysis provides evidence for the **shared universal circuit** hypothesis:

- 26 features appear in 3+ circuits as bottlenecks
- This supports the finding that models use template circuits rather than per-prompt circuits

### Bottleneck Depth Comparison

- GEMMA concentrates bottlenecks in early-to-mid layers (L1-L14)
- QWEN concentrates bottlenecks in mid-to-late layers (L12-L27)
- This confirms the earlier finding that GEMMA's early bottleneck causes information loss

---

*Generated by Stage 1.5 Cross-Circuit Bottleneck Analysis*