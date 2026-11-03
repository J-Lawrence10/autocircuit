# Paper findings and changes

Updated 28 October 2026. The analyses are closed out; the manuscript and sharing materials are being prepared for PI review. This update changes the writing, not the data or estimates.

The paper connects three findings. Questions about the same fact share more features in the original three-model samples. In the stronger Qwen3-4B comparison, the same-fact overlap difference is larger when the answer letter stays the same. In selected errors, graph features overlap more with a correct prediction giving the same answer than with a correct prediction for the intended country. Together, these findings show why feature overlap should be interpreted alongside the prompt relationship and predicted answer.

## What was wrong initially

The original interpretation was stronger than the evidence. Many traced routes did not reach input embeddings, exporter collisions could merge distinct nodes, and graph overlap was treated too readily as a semantic or causal signal. Same-fact questions also shared more words and the same expected answer, so those explanations were not separated. Missing controls and partial next-token answers further limited the comparison sample. A missing comparison is not a measured zero effect.

## What we changed

We withdrew the unsupported pathway and causal claims and made feature-set overlap the measurement under study. We audited identifiers, graph completeness, tokenization, comparison eligibility, and reconstruction-error contributions. We preserved the original data and exclusions instead of changing rules to improve results.

We added controls that keep the token inventory fixed while changing the queried country, answer mapping, and wording. We compared selected wrong-answer graphs with both correct intended-country and correct same-output graphs. We also checked equal feature counts and removed final-position or late-layer nodes to test whether the measured differences were confined to those parts of the graph. None of these checks is a causal intervention.

## Main findings

1. **The original association is reproducible within the analyzed samples.** Mean same-fact overlap advantages are 0.170 for Gemma-2-2B, 0.085 for Qwen3-1.7B, and 0.162 for the available Qwen3-4B cohort. Unequal subject coverage prevents ranking the models.
2. **Same-fact overlap is higher when the answer letter stays the same.** All 48 Qwen3-4B decisions in six country-pair blocks were correct. The same-fact advantage was 0.0628 when the answer label stayed the same and -0.0022 when it changed. Their prespecified average was 0.0303 (95% block-bootstrap interval 0.0265–0.0338). Their direct paired difference is 0.0650, with a Student-t 95% interval of 0.0553 to 0.0746. This added six-block difference analysis is exploratory; the near-zero changed-label estimate does not prove equivalence.
3. **Wrong-answer graphs can resemble correct graphs.** Every selected failure comparison favored the correct response producing the same answer over the correct response to the intended country. The mean differences were 0.1983 for A/B answers and 0.2649 for capital names. These dependent, selected cases do not estimate general error rates or identify a causal shortcut.
4. **The average patterns persist under the sensitivity checks.** Equal-feature-count sampling preserves the positive original model averages, although one Gemma question reverses. The answer-related differences remain after the specified feature-count and graph-location checks.
5. **The final history extension stopped at its preset gate.** Literal A/B checks passed 4/4, document-history checks 7/8, and spaceflight checks 4/8: 15/20 overall against a required 20/20. Prompt and token-inventory checks passed. No evaluation graphs were requested, so there is no new historical graph-overlap estimate. The pilot does not demonstrate an absence of historical knowledge.

## What we can claim

This is a measurement study with an original association in three models and stronger controls and a failure diagnostic in Qwen3-4B. Its contribution is an observed answer-associated pattern in feature overlap: separating answer conditions changes the interpretation of the average same-fact result, and the selected errors show that same-answer resemblance can accompany an incorrect prediction. We identify the relationship, not its causal mechanism or its prevalence across all tasks.

The selected error comparisons share one country pair and overlapping controls. The original Qwen3-4B extension remains incomplete at 145/147 graphs, separate from the completed stronger-control and error studies.

## Where the work ends

The October 5 isolated same-machine reproduction recovered all 23 original fact margins from 342 available raw graphs, matched the closeout audit, and passed 82 software tests. These are archived checks, not a new or independent reproduction. Scripts, raw data, checksums, source tables, figures, failed pilots, and protocols are retained. No further experimental round is planned. A curated review package is already public; raw exports and restricted source materials are excluded. Independent scientific and statistical review, redistribution permissions for a fuller release, venue selection, and author approval remain before submission.
