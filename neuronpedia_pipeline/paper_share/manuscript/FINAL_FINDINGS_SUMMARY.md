# Paper findings and changes

The paper now asks what shared features in attribution graphs actually tell us. Across the analyzed samples, questions about the same fact share more features. Stronger controls show that this resemblance also depends on the answer being produced. Similarity alone therefore cannot establish correct factual reasoning or an answer-independent semantic circuit.

## What was wrong initially

The original interpretation was stronger than the evidence. Many traced routes did not reach input embeddings, exporter collisions could merge distinct nodes, and graph overlap was treated too readily as a semantic or causal signal. Same-fact questions also shared more words and the same expected answer, so those explanations were not separated. Missing controls and partial next-token answers further limited the comparison sample. A missing comparison is not a measured zero effect.

## What we changed

We withdrew the unsupported pathway and causal claims and made feature-set overlap the measurement under study. We audited identifiers, graph completeness, tokenization, comparison eligibility, and reconstruction-error contributions. We preserved the original data and exclusions instead of changing rules to improve results.

We added controls that keep the token inventory fixed while changing the queried country, answer mapping, and wording. We compared selected wrong-answer graphs with both correct intended-country and correct same-output graphs. We also checked equal feature counts and removed final-position or late-layer nodes to test whether the measured differences were confined to those parts of the graph. None of these checks is a causal intervention.

## Main findings

1. **The original association is reproducible within the analyzed samples.** Mean same-fact overlap advantages are 0.170 for Gemma-2-2B, 0.085 for Qwen3-1.7B, and 0.162 for the available Qwen3-4B cohort. Unequal subject coverage prevents ranking the models.
2. **The stronger Qwen3-4B controls show answer dependence.** All 48 decisions in six country-pair blocks were correct. The same-fact advantage was 0.0628 when the answer label stayed the same and -0.0022 when it changed. Their direct paired difference is 0.0650, with a Student-t 95% interval of 0.0553 to 0.0746. This added six-block analysis is exploratory; the near-zero changed-label estimate does not prove equivalence.
3. **Wrong-answer graphs can resemble correct graphs.** Every selected failure comparison favored the correct response producing the same answer over the correct response to the intended country. The mean differences were 0.1983 for A/B answers and 0.2649 for capital names. These dependent, selected cases do not estimate general error rates or identify a causal shortcut.
4. **The interpretation survives limited sensitivity checks.** The answer-related differences remain after the specified feature-count and graph-location checks. This strengthens the measurement observation without establishing a mechanism.
5. **The final history extension stopped at its preset gate.** Literal A/B checks passed 4/4, document-history checks 7/8, and spaceflight checks 4/8: 15/20 overall against a required 20/20. Prompt and token-inventory checks passed. No evaluation graphs were requested, so there is no new historical graph-overlap estimate. The pilot does not demonstrate an absence of historical knowledge.

## What we can claim

This is a three-model, domain-limited measurement study, with the stronger controls and failure diagnostic in Qwen3-4B only. Its contribution is evidence that attribution-graph feature overlap needs matched prompts, answers, and behavioral checks before it can support a factual interpretation. It is not a new validated traceback tool or a discovery of universal factual circuits.

## Where the work ends

The isolated reproduction recovered all 23 original fact margins from 342 available raw graphs and matched the new audit exactly. The final software suite passed 82 tests. Scripts, raw data, checksums, source tables, figures, failed pilots, and protocols are retained. No further experimental round is planned. Independent scientific review, redistribution permissions, venue selection, and author approval remain necessary before public release or submission.
