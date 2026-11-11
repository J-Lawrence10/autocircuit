# Questions and graphs included in the paper

This table covers the final four-version question comparison: a starting question, its factual rewording, and two invented name controls. Each model has five evaluation facts per subject, requiring four graphs per fact. Included plus excluded facts always equals five. Graph availability and analysis inclusion are different counts, and neither column is an accuracy score. Development questions, the fact-by-wording design, and the Qwen3-4B answer-letter and error comparisons are not included in this evaluation-only table.

| Model | Subject | Graphs available | Graphs planned | Evaluation facts included | Evaluation facts excluded | Reasons facts were excluded |
|---|---|---:|---:|---:|---:|---|
| Gemma-2-2B | Chemistry | 20 | 20 | 5 | 0 | None |
| Gemma-2-2B | Geography | 20 | 20 | 0 | 5 | Expected next-token check failed: 4; No qualifying comparison question: 1 |
| Gemma-2-2B | History | 20 | 20 | 3 | 2 | Expected next-token check failed: 2 |
| Qwen3-1.7B | Chemistry | 20 | 20 | 5 | 0 | None |
| Qwen3-1.7B | Geography | 20 | 20 | 5 | 0 | None |
| Qwen3-1.7B | History | 5 | 20 | 0 | 5 | Incomplete prompt/control set: 5, including two facts with no returned graphs |
| Qwen3-4B | Chemistry | 20 | 20 | 5 | 0 | None |
| Qwen3-4B | Geography | 20 | 20 | 5 | 0 | None |
| Qwen3-4B | History | 20 | 20 | 2 | 3 | Complete accepted-answer check failed: 3 |

A failed next-token check does not necessarily mean a wrong completed answer: partial words and alternative continuations can fail this rule. A complete question can still be unused if no second qualifying question remains in its subject and evaluation split.

The primary comparisons include eight facts for Gemma-2-2B, ten for Qwen3-1.7B, and twelve for Qwen3-4B. Facts recur across models and share comparison questions within subjects, so these counts are not independent replicates that can be pooled to rank models. Inclusion requires all four graphs, a complete accepted answer in the next token on both factual prompts, and another qualifying fact in the same subject and evaluation set. Maria and María are accepted spellings for the flagship answer.

[Per-question inclusion audit](../tables/test_fact_inclusion_audit.csv)

## Available graphs across development and evaluation

The table below includes both development and evaluation questions. It reports the four-version and fact-by-wording collections, not the separate Qwen3-4B answer-letter and error studies.

| Model | Four-version graphs available / planned | Fact-by-wording graphs available / planned |
|---|---:|---:|
| Gemma-2-2B | 120/120 | 27/27 |
| Qwen3-1.7B | 91/120 | Not collected |
| Qwen3-4B | 120/120 | 27/27 |

Qwen3-1.7B has 40/40 chemistry graphs, 40/40 geography graphs, and 11/40 history graphs. All ten chemistry and ten geography facts have complete four-version sets; none of the ten history facts does. The 29 missing history requests exceeded the hosted 10-input-token cap and produced no prediction or graph. They cannot be counted as wrong answers.

Across development and evaluation, 19 Qwen3-1.7B facts qualify: nine chemistry and ten geography. Mercury is the only complete four-version fact excluded by the expected-token rule, and it belongs to development: both factual forms predict `H` rather than the full expected `Hg`. Its evaluation estimate uses ten facts, not 91 graphs or 19 independent evaluation observations.

Qwen3-4B has all 147 planned graphs: 120 four-version graphs and 27 fact-by-wording graphs. Its evaluation sample contains twelve facts: five chemistry, five geography, and two history.

## History and output-type-matched controls

Two of five Qwen3-4B history evaluation facts are included and three are excluded because the predicted next token does not provide the complete accepted answer. All 20 history evaluation graphs are available. The included questions concern Columbus's flagship and Franz Ferdinand. Each uses the other as its comparator, giving differences of 0.601 and 0.395. Both facts' invented name controls predict punctuation, so the output-type-matched control comparison includes ten Qwen3-4B facts for each control type, rather than the twelve in the primary analysis.

## Separate Qwen3-4B comparisons

The answer-letter study contains 48 graphs from six country pairs. The selected-error study contains 16 graphs and eight dependent error-versus-control comparisons from one country pair. These graphs are separate from the collection totals above. The Qwen3-4B history pilot passed 15/20 behavioral checks against a required 20/20; no history evaluation graphs were requested for that study. This stopped pilot is distinct from the Qwen3-1.7B input-length rejections.

An additional Qwen3-4B history analysis collected graphs for all 16 historical prompts from that preliminary check, excluding its four literal-instruction checks. All 16 passed integrity checks and reproduced the preview predictions: 11 correct and five incorrect. None was excluded for correctness. These two event pairs yield 56 dependent within-pair graph comparisons, including eight date-mapping comparisons and eight question/context-order comparisons. The two groups of eight reuse the same 16 graphs. This analysis is separate from both the 385 question/control and fact/wording graphs and the uncollected 160-graph history evaluation; it does not add evaluation facts to the three-model sample.

## Analysis provenance

The paper uses the current available data for each model. Earlier Qwen3-1.7B subset results remain in the audit archive, not as an additional sample or independent replication. Its current analysis was specified after the earlier findings were known, with the question set, expected answers, and inclusion rules unchanged. Methods Section 2.8 and the archived plans retain that distinction.

The accepted-spelling correction was applied to all 170 available factual outputs and changed one classification. The final manuscript and figures use the corrected results; superseded exact-text decisions remain only in the audit archive. This corrects scoring without changing prompts, graphs, or the recorded outcomes of earlier collection gates.
