# Qwen3-1.7B missing-graph completion attempt

Authorized by the author on 6 November 2026: "before we continue attempt to rerun those."
This narrowly reopens collection of the 70 missing original Qwen3-1.7B prompts.
It does not reopen other models, the failed history-choice pilot, or local inference.
The October closeout and original results remain historical and unchanged.

## Fixed scope

- Use the unchanged 120-row `config/paper_control_manifest.csv`; SHA-256
  `c2c36a46e09a4c7943ff38e537f78cf3e7d4aa27e031b011be3b6035c6106196`.
- Inventory and hash all 50 existing graphs before collection. Never overwrite them.
- Request only the 70 missing rows, in manifest order: 30 geography and 40 history.
- Keep prompts, expected tokens, roles, subjects, and development/evaluation assignments unchanged.
- Model: `qwen3-1.7b`; source: `llamascope-2-transcoder-16k-k64`, with the recorded LoRSA family.
- Use the amended original generator's desired-logit coverage .99, maxNLogits 10,
  nodeThreshold .8, edgeThreshold .85, maxFeatureNodes 5000, qkTopFraction .5,
  qkTopk 5. Some old graphs used .95 coverage; preserve those files and their metadata.
- Save new raw bytes, response bodies, request states, metadata, checksums, code snapshots,
  and status under `data/model_extension/qwen17_completion_20261106`.

## Transport safeguards

Reuse the shared request ledger with at least 125 seconds between POST starts and
at most 30 POSTs per rolling hour. Every attempted POST counts, including failures.
Use deterministic slugs and one POST attempt per missing job in this initial attempt.
On restart, never repeat a saved attempted request automatically. A saved successful
response may be used to retry downloading its raw file, without generating again.
Reconcile uncertain submissions by their existing slug; do not create replacements.
Stop the batch on an uncertain submission, authentication error, service error, unexpected
schema/settings/source change, or other non-prompt-specific failure. Explicit prompt-length
rejections are recorded as unavailable and do not authorize shortened prompts.
No output-correctness gate is used to select which requested graphs to retain.

## Interpretation

This is a late completion attempt after inspecting the original results, not a new
untouched confirmatory sample. Newly generated graphs may reflect a changed hosted
exporter. Preserve and audit exact source/settings/version metadata before combining
any feature identities across collection dates. Do not change manuscript estimates,
eligibility, significance tests, or frozen claims automatically. Report completion and
failures first; any subsequent analysis must retain the original cohort separately.

## Current service evidence

The Neuronpedia source inspected on 6 November lists Qwen3-1.7B as a LoRSA model with
a 10-input-token cap. The generation route checks token length before generation.
This is evidence about the present attempt, not an explanation of July's incomplete run.

- https://github.com/hijohnnylin/neuronpedia/blob/main/apps/webapp/lib/utils/graph.ts
- https://github.com/hijohnnylin/neuronpedia/blob/main/apps/webapp/app/api/graph/generate/route.ts
