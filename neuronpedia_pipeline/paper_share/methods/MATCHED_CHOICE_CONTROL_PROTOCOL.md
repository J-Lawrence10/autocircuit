# Matched-choice control experiment v1

5 September 2026. New prospective follow-up, developed after the earlier studies and September exploratory audit. This is not a modification of those cohorts, and not a claim of external preregistration. Freeze this document and the complete manifest before any new behavioral outcome is requested.

## Purpose and scope

Test whether target-paraphrase feature similarity distinguishes the queried fact when the complete word multiset, response alphabet, and answer-label agreement are controlled. A two-choice capital-selection task replaces open-ended completion. It still requires a factual country-capital association, but recognition, distractors, query order, label mapping, and instructions differ from the original task. Success will not retroactively identify a lexical-independent semantic effect in the old dataset or establish causal circuits.

Primary pipeline: Qwen3-4B, `transcoder-hp`. Replication pipeline: Gemma-2-2B, `gemmascope-transcoder-16k`. No local inference. Qwen3-1.7B is explicitly deferred because current hosted code caps LoRSA graphs at 10 input tokens, incompatible with this unchanged matched design. Other model families are not silently substituted.

## Design

Each block contains two countries and their two capitals. All eight prompts use the identical case-folded word multiset and, verified before outcomes, the identical Qwen tokenizer-ID multiset and input token count. They differ only in arrangement:

- queried country: first or second country;
- capital-to-letter mapping: direct or swapped A/B labels;
- question wording: `for COUNTRY rather than OTHER what is the capital` versus `what is the capital for COUNTRY rather than OTHER`.

Common structure: `Reply with only A or B. A: CAPITAL_A. B: CAPITAL_B. Question: QUESTION? Answer:`.

Example: France/Paris and Germany/Berlin. When queried country and option mapping agree, expected label is A; otherwise B. Swapping country while swapping the option mapping changes the fact but preserves the output label. Holding country fixed while swapping mapping preserves the fact but changes the output label. Paraphrases preserve both. All prompts contain both countries and capitals; the correct country-capital bindings are not supplied as statements.

The France/Germany block is a behavior-only development pilot, excluded from inferential graph analysis. Six fixed held-out blocks are Japan/Italy, Spain/Portugal, Canada/Australia, Greece/Austria, Egypt/Kenya, and Norway/Sweden. No block is substituted after observing outcomes. Countries and capitals are disjoint across blocks; blocks, not graph pairs, are the inferential units.

## Pilot and generation gates

1. Validate the 56 unique prompts, factorial balance, word/token multisets, and one-token spaced A/B continuations offline. Reserve room for a possible BOS marker within the hosted 64-token cap.
2. Per model, obtain all eight pilot forward-pass previews using `/api/graph/tokenize`. Archive the complete returned probabilities and token pieces before assessing behavior. Require eight of eight top predictions to equal the expected single label after whitespace trimming, and identical input-token multisets across the eight server responses. No graph-similarity outcomes are inspected for this gate. If the pilot fails, stop that model and report the failure; revise only in a new documented version, not by editing these prompts.
3. A passing model proceeds to all 48 held-out graph jobs without selecting by graph similarity. Settings: source set fixed above, maxNLogits=10, desiredLogitProb=.99, nodeThreshold=.8, edgeThreshold=.85, maxFeatureNodes=5000. Save raw bytes, API responses, job metadata, SHA-256, failures, and converted graphs. No completed graph is regenerated. Deterministic slugs and a durable request ledger prevent silent duplicate submissions after uncertain responses.
4. Every API POST, including previews and retries, counts against a shared local 30-per-rolling-3600-seconds ceiling, with at least 125 seconds between starts. Honor a longer Retry-After. No rate-limit circumvention. Stop on an uncertain submission, non-retriable failure, or authentication failure; do not blindly repeat a timed-out export. Other independent pipelines must not be started concurrently without sharing the ledger.

## Integrity and eligibility

Verify returned model, exact prompt apart from known leading BOS markers, expected next-label decoding, finite edge weights, known endpoints, and feature identity namespaces. Exclude ambiguous node IDs and incident edges using the established collision-safe policy, and preserve an audit of every exclusion. Primary feature sets exclude reconstruction errors, embeddings, and logits. Retain error-inclusive and influence-weighted versions as sensitivities.

All six complete held-out blocks are reported descriptively. The retrieval-conditioned primary analysis requires all eight cells per block to have the expected top label and identical server input-token multisets, as well as graph integrity. The full inferential retrieval gate requires all six blocks to qualify. If any does not, report the incomplete/failed gate and available block estimates without a primary significance claim. Do not delete failed cells and average an unbalanced block. A single A/B label is the defined decision; this experiment does not verify unconstrained subsequent prose or natural-language answers.

## Contrasts and null controls

For each block, compare the four wording-0 graphs with the four wording-1 graphs. The resulting 16 cross-wording pairs form four equally sized categories, indexed by same/different queried fact and same/different correct output label:

- SS: same fact, same label (positive paraphrase controls);
- SD: same fact, different label (output-label-change controls);
- DS: different fact, same label (answer-matched negative controls);
- DD: different fact, different label (joint negative controls).

Primary block fact contrast: `F = ((SS - DS) + (SD - DD)) / 2`. Report `SS - DS` and `SD - DD` separately to expose interactions. Secondary output-label contrast: `L = ((SS - SD) + (DS - DD)) / 2`. No feature identity is compared across models.

For a complete six-block eligible model, use an exact assignment null: independently permute queried-fact correspondence in the wording-1 graphs within each correct-output-label group. Each block has four assignments and the six-block pooled mean has 4^6=4096 assignments. Report a one-sided upper-tail p including the observed assignment, alongside a 10,000-resample block-bootstrap 95% interval, seed 20260905. The null tests correspondence conditional on label and lexical bag; it does not make word order or factual identity experimentally indistinguishable. Correct across the two planned model primary tests using conservative Bonferroni `min(1,2p)` regardless of model completion. All secondary contrasts and sensitivities are descriptive, not selectively promoted to primary outcomes.

Prespecified sensitivities: influence-weighted cosine, error-inclusive Jaccard, equal-feature-count subsampling (within block, all eight graphs, 200 seeded repetitions), and minimum observed block fact contrast. Implementation positive/null controls use synthetic identical sets and label-only sets: identical representations must give zero fact contrast; label-only representations must give zero fact contrast and positive label contrast. These are software tests, not empirical validation of semantic mechanisms.

## Interpretation and deliverables

A positive result supports a queried-fact association within this forced-choice pipeline beyond bag-of-words counts and correct answer-label identity. It does not isolate an abstract semantic mechanism from query order, attention, entity-role binding, mapping computations, or original output-capital identity. A null, behavior failure, or unbalanced cohort is reported without prompt substitution.

Keep this experiment under `data/model_extension/matched_choice_v1`, with manifest, immutable freeze record, status, shared request ledger, pilot predictions, raw graphs, metadata, converted graphs, audit tables, full pairwise tables, block statistics, null distributions, figures, logs, and scripts. Background execution may continue the frozen jobs and finalize analysis automatically. Original paper estimates and manuscript are not changed based on unfinished results.

API references inspected before the run: [tokenize route](https://github.com/hijohnnylin/neuronpedia/blob/main/apps/webapp/app/api/graph/tokenize/route.ts), [generate route](https://github.com/hijohnnylin/neuronpedia/blob/main/apps/webapp/app/api/graph/generate/route.ts), and [hosted model/token limits](https://github.com/hijohnnylin/neuronpedia/blob/main/apps/webapp/lib/utils/graph.ts). No private inference host or secret endpoint is used.
