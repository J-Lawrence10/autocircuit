# Questions and graphs included in the paper

This table covers the four-version question design: a starting question, its factual rewording, and two invented name controls. Each model has five evaluation facts per subject, requiring four graphs per fact. Included plus excluded facts always equals five. Graph availability and analysis inclusion are different counts, and neither column is an accuracy score. Development questions, the fact-by-wording design, and the separate Qwen3-4B answer-letter and error studies are not included in this evaluation-only table.

| Model | Subject | Graphs available | Graphs planned | Evaluation facts included | Evaluation facts excluded | Reasons facts were excluded |
|---|---|---:|---:|---:|---:|---|
| Gemma-2-2B | Chemistry | 20 | 20 | 5 | 0 | None |
| Gemma-2-2B | Geography | 20 | 20 | 0 | 5 | Expected next-token check failed: 4; No qualifying comparison question: 1 |
| Gemma-2-2B | History | 20 | 20 | 3 | 2 | Expected next-token check failed: 2 |
| Qwen3-1.7B | Chemistry | 20 | 20 | 5 | 0 | None |
| Qwen3-1.7B | Geography | 20 | 20 | 5 | 0 | None |
| Qwen3-1.7B | History | 5 | 20 | 0 | 5 | Incomplete prompt/control set: 5, including two facts with no returned graphs |
| Qwen3-4B* | Chemistry | 20 | 20 | 5 | 0 | None |
| Qwen3-4B* | Geography | 20 | 20 | 5 | 0 | None |
| Qwen3-4B* | History | 18 | 20 | 0 | 5 | Incomplete prompt/control set: 1; Expected next-token check failed: 3; No qualifying comparison question: 1 |

A failed next-token check does not necessarily mean a wrong completed answer: partial words and alternative continuations can fail this rule. A complete question can still be unused if no second qualifying question remains in its subject and evaluation split.

The current primary comparisons include eight facts for Gemma-2-2B, ten for Qwen3-1.7B, and ten for Qwen3-4B. Facts recur across models and share comparison questions within subjects, so these counts are not independent replicates that can be pooled to rank models. Inclusion requires all four graphs, the expected next token on both factual prompts, and another qualifying fact in the same subject and evaluation set.

[Per-question inclusion audit](../tables/test_fact_inclusion_audit.csv)

## Available graphs across development and evaluation

The table below includes both development and evaluation questions. It reports the four-version and fact-by-wording collections, not the separate Qwen3-4B answer-letter and error studies.

| Model | Four-version graphs available / planned | Fact-by-wording graphs available / planned |
|---|---:|---:|
| Gemma-2-2B | 120/120 | 27/27 |
| Qwen3-1.7B | 91/120 | Not collected |
| Qwen3-4B* | 118/120 | 27/27 |

Qwen3-1.7B has 40/40 chemistry graphs, 40/40 geography graphs, and 11/40 history graphs. All ten chemistry and ten geography facts have complete four-version sets; none of the ten history facts does. The 29 missing history requests exceeded the hosted 10-input-token cap and produced no prediction or graph. They cannot be counted as wrong answers.

Across development and evaluation, 19 Qwen3-1.7B facts qualify: nine chemistry and ten geography. Mercury is the only complete four-version fact excluded by the expected-token rule, and it belongs to development: both factual forms predict `H` rather than the full expected `Hg`. Its evaluation estimate uses ten facts, not 91 graphs or 19 independent evaluation observations.

Qwen3-4B is missing the factual rewording and reworded invented name control for Columbus after repeated server failures. Its four-version and fact-by-wording collections therefore contain 145/147 planned graphs. The asterisk identifies this incomplete collection, not a model-performance result.

## Separate Qwen3-4B comparisons

The answer-letter study contains 48 graphs from six country pairs. The selected-error study contains 16 graphs and eight dependent error-versus-control comparisons from one country pair. These graphs are separate from the collection totals above. The Qwen3-4B history pilot passed 15/20 behavioral checks against a required 20/20; no history evaluation graphs were requested for that study. This stopped pilot is distinct from the Qwen3-1.7B input-length rejections.

## Analysis provenance

The paper uses the current available data for each model. Earlier Qwen3-1.7B subset results remain in the audit archive, not as an additional sample or independent replication. Its current analysis was specified after the earlier findings were known, with the question set, expected answers, and inclusion rules unchanged. Methods Section 2.8 and the archived plans retain that distinction.
