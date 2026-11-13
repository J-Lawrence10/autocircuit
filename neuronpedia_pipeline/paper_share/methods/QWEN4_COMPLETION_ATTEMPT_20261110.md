# Bounded recovery of two missing Qwen3-4B graphs

Authorized 10 November 2026: make one additional generation attempt for each of the two missing original prompts. This authorization does not restart the original batch, permit further retries, or authorize replacement prompts, new models, or local inference.

## Fixed requests

Use Qwen3-4B and `transcoder-hp`, with the original `desiredLogitProb=0.99` request. Preserve the original plain prompts without adding a chat wrapper:

1. `columbus_americas__positive_paraphrase`: `Columbus's flagship in 1492 was the Santa` (expected next token: `Maria`).
2. `columbus_americas__negative_nonce`: `Torven's flagship in 2192 was the Pelorian` (invented name control; no correctness requirement).

Copy the jobs from the frozen original manifest. The only added request field is a unique operational slug for recovery without a duplicate generation request. Compare returned graph settings with the original recorded defaults: ten logits, cumulative output probability 0.99, 5,000 feature nodes, node threshold 0.8, and edge threshold 0.85. Record the exporter metadata; identical hosted weights cannot be established merely by requesting the same model name.

## Execution and preservation

Use the shared request ledger, at least 125 seconds between request starts, and at most 30 generation/preview requests in any rolling hour. Submit at most one new generation POST per job, including on server errors or timeouts. Existing attempted request states must never cause another POST. Retrieval of a saved response or GET-based reconciliation is permitted. A definitive failure for one job does not justify retrying it or replacing its prompt. Respect any server rate-limit response before proceeding with the other job.

Write requests, responses, raw graphs, metadata, checksums, audits, conversion outputs, code snapshots, and logs only under `data/model_extension/qwen4_completion_20261110`. Verify all 145 original raw hashes and preserve original manifests, results, graphs, and stopping records. Do not reactivate the original generator.

## Analysis and reporting

Collection completeness and scientific inclusion are different outcomes. If both exports are recovered, the combined available inventory can reach 120/120 controlled graphs and 147/147 including the crossed design. No correctness-based repeated generation is allowed.

Use the existing conversion, feature definitions, expected-next-token rule, four-role requirement, and same-subject/split comparator requirement. Include all returned outcomes in accounting. Raw defects and any metadata differences remain explicit; do not repair raw graph identities silently. If usable graphs are recovered, reconstruct the archived analysis first, then apply the unchanged controlled analysis to the combined available sample in this separate recovery directory. Retain the original estimates and report any changed eligibility, history comparisons, or aggregate estimates. This late completion is not an independent prospective replication. The 27 crossed graphs and the separate geography, error, and historical-date studies are unchanged.

Stop after these two attempts regardless of outcome. Further requests require new authorization.
