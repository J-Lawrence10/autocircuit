# History graph follow-up including correct and incorrect answers

Authorized 10 November 2026: collect the 16 unchanged historical prompts from the saved Qwen3-4B pilot and analyze every returned graph, including wrong answers. This additional analysis does not reopen the original 160-graph evaluation or change its stopping rule. The earlier response outcomes are already known; the graph outcomes are not.

## Fixed collection

Use all eight prompt combinations for each of two event pairs: Declaration of Independence adoption and Treaty of Paris signing; Sputnik 1 and Explorer 1 launch years. Copy prompts directly from the archived jobs, preserving model, chat template, response prefix, event, answer mapping, and question/context order. Do not collect the four literal instruction checks or any replacement questions. Use hosted Qwen3-4B, `transcoder-hp`, node threshold 0.8, edge threshold 0.85, maximum 10 logits, desired logit probability 0.99, and maximum 5,000 feature nodes.

Use the existing shared request ledger, at least 125 seconds between starts, and at most 30 requests per rolling hour. Resume saved outputs; never repeat an uncertain generation request. Allow the existing maximum of three attempts per job for safely retryable failures. No local inference or new model is authorized.

## Questions and measurements

1. Do newly collected graph predictions reproduce the 16 saved preview predictions? Report every expected, archived, and newly observed answer, including any changes. Correctness is a measured variable, never an inclusion gate.
2. How does Jaccard feature overlap differ for the same versus different queried event, and for the same versus different required answer letter? Reproduce the four cross-order comparison categories used in the geography analysis, with four comparisons per category in each eight-prompt block. Report category means, same-event differences within each required-letter condition, and their difference. These categories use the required letter, whether or not the model predicts it.
3. How does overlap relate to the actually predicted letter? Report all 28 unordered comparisons within each event pair, their factors and correctness, and descriptive summaries stratified by event match, required-letter match, predicted-letter match, and prompt-order match. Report group sizes and unsupported cells explicitly. Do not treat a predicted-letter grouping as a randomized manipulation.
4. What changes when only the question/context order changes? Pair the four fixed event/mapping combinations within each event pair. Report whether the predicted letter changes, whether correctness changes, and feature overlap for every pair. Likewise pair the four fixed event/order combinations when only the answer mapping changes. Decode the predicted letter to its year to distinguish changes in letter from changes in the selected date.

The main representation is the set of unique feature-family/layer/feature-ID identities, collapsed across token positions and excluding embeddings, logits, and reconstruction-error nodes. Use the established conversion and summarization functions. Compute influence-weighted cosine as a sensitivity. Repeat cross-order Jaccard contrasts after removing final-position features, last-quarter-layer features, or both, and after 200 independent equal-feature-count subsamples at K and floor(K/2), where K is the smallest feature set within the event-pair block. Save every sampling result; sampling repetitions are not additional observations.

## Integrity and reporting

Preserve every raw response, graph, request state, metadata record, and checksum. Audit prompt/model/source/settings, exact prompt token sequences against the saved previews, token inventories within each event pair, node identifiers, edge endpoints, duplicate edges, finite weights, and conversion integrity. A wrong prediction is retained. A technically invalid graph remains in accounting and behavioral reporting where provenance is valid, but does not contribute an interpretable overlap value. Do not repair ambiguous raw identities silently or replace failed exports. A changed prediction is reported, not excluded; mismatched token inventories prevent balanced block contrasts.

Report both event pairs separately. Any across-pair average weights the two event pairs equally. Provide no population confidence intervals or significance claims from these two selected pairs or their dependent pairwise comparisons. Output raw effect sizes and all comparison counts. This is an additional observational graph analysis, not a causal intervention or a replacement for the original geography analysis.

## Saved outputs

Maintain a separate folder, `data/model_extension/history_pilot_graphs_20261110`, with the plan and code snapshot, exact jobs, original preview records, raw/converted graphs, checksums, integrity audit, pair-level tables, sensitivity tables, figures with source data, machine-readable results, and a plain-language report. Preserve the original history archive and manuscript until the new results have been reviewed.
