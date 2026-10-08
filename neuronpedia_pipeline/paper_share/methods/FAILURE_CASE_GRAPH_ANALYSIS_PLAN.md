# Plan to investigate the country selection failures

2 October 2026. Status: plan only; no graph generation started for this investigation.

## Purpose

Determine whether attribution graphs provide evidence consistent with the model selecting an answer option by position instead of resolving the requested country. Compare failures with two kinds of correct answers: answers to the intended question and answers that produce the same output token as the failure.

This is a small, explicitly exploratory investigation of known failures. It will not replace the failed position pilot, change earlier results, or establish a causal mechanism from graph similarity alone. The immediate deliverable is a reproducible account of where the graphs differ, with candidate explanations and limitations.

## What we already know

The independent local audit found no expected-answer, submitted-prompt, returned-token, or top-token decoding mismatch. In the subsequent diagnostic, the four selected cases were correct when the country was named directly and incorrect when it was identified as first or second. This held for both A/B responses and capital-name responses. All eight ordinal failures matched the answer option occupying the requested ordinal position.

That pattern motivates a position-selection hypothesis. It does not prove that the model internally used that rule, nor rule out a hosted-runtime issue. The four cases involve France and Germany in two list/option layouts; they are not four independent country-pair replications.

Sources are the saved `local_audit.json`, `jobs.json`, and `diagnostic_results.json` under `data/model_extension/position_artifact_diagnostic_20261001/`. Earlier protocols and results stay unchanged.

## The graph batch

Generate exactly the sixteen factorial prompts already evaluated in the diagnostic. Reuse their full archived prompt strings, including the official Qwen chat frame, without rewording them.

| Country reference | Requested response | Previously observed behavior | Graphs |
|---|---|---|---:|
| First or second country | A/B label | Incorrect | 4 |
| Country named directly | A/B label | Correct | 4 |
| First or second country | Capital name | Incorrect | 4 |
| Country named directly | Capital name | Correct | 4 |

Use hosted Qwen3-4B with `transcoder-hp`; no other model and no local inference. The four literal/replay checks in the twenty-preview diagnostic are behavioral checks, not additional graph jobs. Named and ordinal prompts differ in wording, token count, and entity repetition: this is not an identical-token-inventory experiment.

### Comparisons built into these sixteen graphs

For each failure and each response format, compare:

1. **Same intended country:** its named-country counterpart asks the same factual question but previously answered correctly. This contrast changes both question wording and observed output, so it cannot isolate a mechanism by itself.
2. **Same observed answer:** the named-country question for the opposite country, with the same option mapping and country-list order, previously produced the failure's output correctly. This controls the output token while changing which country is requested.
3. **Response format:** examine the corresponding A/B and capital-name cases separately, then describe whether the pattern is consistent across formats. Do not directly treat an A logit and a Berlin logit as equivalent graph targets.

Example: with `A: Berlin. B: Paris. Countries: France, Germany`, the first-country question incorrectly produced A. The named-France question correctly produced B; the named-Germany question correctly produced A. These are three different comparisons, not interchangeable controls.

## Phase one Freeze inputs and validate the implementation

Before any graph request:

- Create a separate output folder, proposed as `data/model_extension/failure_case_graphs_v1/`.
- Build a sixteen-job manifest by selecting the four factorial arms from the saved diagnostic. Record each prompt hash, intended answer, previously observed answer, source diagnostic job, response format, and both comparison partners.
- Independently validate the expected answer from prompt text. Verify that output-matched partners have the same option mapping and country list, and that the archived outputs actually match.
- Archive this plan, the manifest, implementation snapshot, dependency versions, tokenizer provenance, and their hashes in a freeze record. A local freeze is not public preregistration.
- Add tests for partner matching, token-span alignment, sign handling, duplicate/colliding IDs, missing logits, empty denominators, and resume behavior. Known wrong answers must remain analyzable: do not reuse the earlier all-correct retrieval gate to discard the failures we are studying.

The source diagnostic manifest SHA-256 is `0d66055f849578b1b90ce6a4f48faec89ba6b440ad347bbc5375e6065aa3d05f`; its results SHA-256 is `b58bfa5cab203d161d105797bd39e2ff2e17f4f89942910d00bd52ec4ee437e0`. Verify these before constructing the graph manifest.

## Phase two Generate and audit all sixteen graphs

Reuse established settings: maxNLogits=10, desiredLogitProb=0.99, nodeThreshold=0.8, edgeThreshold=0.85, maxFeatureNodes=5000. Use deterministic slugs, the existing shared request ledger, at least 125 seconds between POST starts, and no more than 30 POSTs per rolling hour. Honor longer server delays. Sixteen successful submissions span at least about 31 minutes under that spacing, excluding initial quota waits and any additional service delay.

Save raw bytes, responses, request state, metadata, checksums, and logs. Resume only missing jobs; reconcile uncertain submissions rather than blindly repeating them. No adaptive extra prompts or replacement exports chosen for a more favorable answer.

For every export check:

- Exact model, prompt/token sequence, decomposition source, and generation/pruning settings.
- Missing or ambiguous node IDs, duplicate edges, orphan endpoints, and nonfinite weights.
- The newly exported top answer against both the intended answer and the archived preview. Flag changes as behavior drift; retain the graph without relabeling its history.
- Availability of output logits and the amount of reconstruction-error content.

Keep raw exports immutable. Ambiguous exports are excluded from the clean graph comparison and retained for a clearly labeled sensitivity analysis using the existing collision-safe policy. Missing or invalid graphs are reported, not replaced silently. A complete clean comparison requires all of its constituent graphs to pass integrity checks. Output-matched comparisons additionally require matching newly observed output tokens.

If the intended correct logit is absent from an export, record it as unavailable, not zero influence. The top-logit export may include only the confidently predicted wrong answer. This batch will not add forced-target or alternative-threshold exports to fill that gap.

## Phase three Analyze the differences

### Feature composition

Compute feature-set Jaccard similarity and exported-influence-weighted cosine using feature family, layer, and ID, excluding embeddings, logits, and reconstruction errors. Report all matched pairs, layer profiles, and graph sizes. Add equal-feature-count subsampling within each comparison triple as a descriptive sensitivity; fix the seed and 200 repetitions before outcomes. Sampling variation is not an inferential confidence interval.

For each failure, report its similarity to the same-country correct graph and to the same-output correct graph, plus their difference. Higher similarity to the same-output graph alone is not evidence of a shortcut: output conditioning can produce that result.

### Token locations and local edge structure

Map exact token spans before inspecting attribution strength: country names in the list, country names in the question, ordinal words, A/B option labels, each option's capital, question/instruction tokens, and chat markers. Preserve occurrence identity when a country appears twice. Align roles across prompts rather than comparing bare token indices; named and ordinal prompts have different lengths. Do not name a feature a country or ordinal detector solely because it occurs at that token.

For the observed answer logit, tabulate its direct incoming edges by source type and source token role. Report signed weights, absolute weights, and a clearly defined within-graph absolute-weight fraction, alongside unnormalized totals. Treat these as local exported attributions, not probabilities or complete semantic contributions.

Inspect the direct predecessors of the answer logit and one further upstream step using a fixed selection rule: all predecessors in tables, and the top ten per step by absolute edge weight in display panels, with stable ID tie-breaking. Keep positive and negative edges visually distinct. Preserve omitted-edge weight totals. Do not multiply edge weights into an asserted causal path score or describe a route starting at an error/source node as a complete input-to-output pathway.

Repeat summaries with reconstruction-error sources visible and with feature-only sources. Report how much of the displayed answer support comes from errors or unobserved upstream connections. If those limitations dominate the apparent difference, the correct result is that this export does not resolve the mechanism.

### Robustness and interpretation

Show all four cases and both response formats, including disagreements. Retain stable feature IDs even if textual explanations are unavailable; any later feature descriptions require independently recorded provenance and must not substitute for intervention evidence.

Use descriptive tables and within-case differences only. There are two country facts in one country pair, with dependent prompts and comparisons; sixteen graphs are not sixteen independent scientific replicates. Do not attach confirmatory p-values or population confidence intervals to this selected failure sample.

## Phase four Produce the evidence package

- **Behavior and integrity table:** all sixteen jobs, intended/preview/exported answers, hashes, and any exclusions or drift.
- **Comparison figure:** each failure's feature similarity to both correct comparators, separated by response format, with graph-size sensitivities.
- **Token-role figure:** local answer-logit incoming attribution by source role/type, including errors and missing coverage.
- **Graph panels:** fixed examples for France with `A: Berlin, B: Paris`, both response formats, showing the failure and its two correct comparators. Provide all remaining panels in the supplement rather than selecting examples by effect strength.
- **Machine-readable outputs:** complete node/edge tables, pairwise values, token alignment, exclusions, figure-source tables, analysis settings, checksums, and reproduction commands.
- **Short findings memo:** what reproduced, what graph evidence supports, what remains ambiguous, and whether a causal follow-up would be justified.

Proposed implementation files are `run_failure_case_graphs.py`, `analyze_failure_case_graphs.py`, and `plot_failure_case_graphs.py`; these are planned files, not existing completed tools. Reuse the established transport and converter where appropriate without altering frozen earlier analyses.

## Decision rules and stopping point

| Outcome | Interpretation and next action |
|---|---|
| Behavior reproduces and location-specific differences remain after output matching | Evidence consistent with a position-selection hypothesis; nominate features or sites for a separately approved causal test |
| Differences are explained mainly by output identity or feature-set size | The graphs do not distinguish the proposed shortcut from output/task effects |
| Errors, pruning, missing logits, or export defects prevent comparison | Report a graph-measurement limitation; do not claim absence of a mechanism |
| Previously observed behavior changes | Report drift and analyze current behavior separately; do not force the old failure labels onto new graphs |
| Patterns disagree across cases or formats | Report the disagreement; do not average it into a single mechanism story |

Stop after this sixteen-graph batch and its report, regardless of whether the evidence favors the hypothesis. No new models, prompt search, local inference, steering, ablation, activation patching, or additional graph batches are included. Any intervention study would require a separate plan, controls, and authorization.

The plan succeeds by producing an auditable answer about what these exports can and cannot explain, not by obtaining a particular graph pattern. Original paper cohorts and claims remain unchanged until the authors review the completed diagnostic.
