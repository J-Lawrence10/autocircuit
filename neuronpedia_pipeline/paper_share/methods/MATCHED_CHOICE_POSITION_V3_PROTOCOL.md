# Final position-balanced follow-up (v3)

9 September 2026. Outcome-informed follow-up after the v2 results, locally frozen before any v3 behavioral request. Not public preregistration. Original and v2 cohorts, claims, and gates remain unchanged.

## Question and stopping rule

Does a queried-country association in sparse feature overlap persist across both wording and the queried country's list position, balancing output-label agreement? This is the final planned control round before writing. Use Qwen3-4B, hosted `transcoder-hp`, only. No local inference, other models, new domains, adaptive prompt search, or automatic further experiment after failure.

The six country pairs are deliberately reused from v2: Japan/Italy, Spain/Portugal, Canada/Australia, Greece/Austria, Egypt/Kenya, Norway/Sweden. They are not unseen facts. France/Germany is a separate behavior-only pilot. Only v3 held-out GRAPH OUTCOMES are unseen at freeze time. This tests a new task formulation, not direct replication of v2 effect magnitudes.

## Fully crossed design

Within each block cross two queried countries, two capital-to-A/B mappings, two queried-country list positions, and two wordings: 16 cells. List both countries, refer to the requested one as first or second, and explicitly exclude the other ordinal. Example:

`Reply with only A or B. A: Tokyo. B: Rome. Countries: Japan, Italy. Question: what is the capital for the first country, not the second? Answer:`

Other wording: `Question: for the first country not the second, what is the capital? Answer:`. Both ordinal words and one query comma occur in every prompt. Reverse the list and select the second country to preserve the queried country while changing its location. Swap the capital options independently. Expected A iff fact equals mapping. Use the same archived official Qwen no-thinking chat template as v2, unchanged.

Before outcomes verify 112 unique prompts, all 16 factorial cells, identical case-folded word and tokenizer-ID multisets per block, one-token A/B continuation, and <=64 input tokens including allowance for BOS. Archive tokenizer hashes, design/protocol and analysis code hashes, jobs, dependencies, seed, and graph settings.

## Gates and execution

Require all 16 France/Germany pilot responses to have the expected top A/B label, exact requested prompt (known leading BOS normalization only), and identical nonempty server token multisets. If any fails, stop; do not generate the 96 held-out graphs or replace prompts. Save failed pilot behavior and complete the closeout report as a design/behavior limitation.

If pilot passes, generate all 96 fixed graph jobs. Share the existing durable Neuronpedia request ledger: >=125 seconds between POST starts and <=30 POSTs per rolling hour, counting retries and pilots. Honor Retry-After and preserve the existing uncertain-submission reconciliation rule. Resume only missing outputs. Preserve raw bytes, metadata, responses, checksums, logs, conversion and exclusions.

Settings remain maxNLogits=10, desiredLogitProb=.99, nodeThreshold=.8, edgeThreshold=.85, maxFeatureNodes=5000. Verify exact model/prompt, returned decomposition source, generation/pruning settings, finite weights, endpoints, correct top labels and token balance. Collision-safe conversion drops ambiguous IDs with exclusions audited. Additionally, v3's primary gate requires zero raw ambiguous IDs and duplicate endpoint edges; do not repair an ambiguous export into primary eligibility. All six 16-cell blocks must pass for primary inference. Otherwise report available descriptive contrasts and a failed gate, not a significance claim.

## Representation and tests

Reuse unique feature-family/layer/id sets collapsed across token positions, excluding logits, embeddings, reconstruction errors, and ambiguous identities. This is feature composition, not graph topology or causal pathway recovery.

For each block, form four 4x4 similarity matrices: wording 0 at queried position p versus wording 1 at queried position q, for p,q in {0,1}, indexed by (queried fact, correct A/B label). Average the two p!=q matrices for the primary cross-position matrix. Average p=q matrices for a descriptive within-position comparison. Each comparison crosses wording; neither uses identical graphs as a positive observation.

In either matrix SS, SD, DS, DD denote same/different fact then same/different label. Primary F=((SS-DS)+(SD-DD))/2, averaged equally across six blocks. Report SS-DS and SD-DD separately, label contrast L=((SS-SD)+(DS-DD))/2, and the within-position F. Report overall position contrast as mean similarity of p=q minus p!=q, balanced over fact and label. Same/different A/B refers to response labels, not the identity of the capital.

Use the v2 conditional correspondence null: flip fact correspondence in wording 1 independently within A and B, using the SAME flip at both positions, preserving label and position. Four assignments per block, 4096 combinations across six blocks; one-sided upper-tail exact enumeration including observed assignment. This is a conditional correspondence null with exchangeability assumptions, not a randomized causal intervention. Block-bootstrap 95% intervals, 10,000 resamples, seed 20260909. Blocks (n=6), not 96 graphs or pairs, are the units. Label secondary/component estimates and intervals descriptive; no equivalence claim from a near-zero estimate.

One primary endpoint in this new follow-up. Also show conservative cumulative correction min(1,4p) for the v1 Qwen, v1 Gemma, v2 Qwen, and v3 Qwen opportunities; this does not erase the adaptive study history. Never retroactively change the frozen v2 family size. Sensitivities: weighted cosine, error-inclusive Jaccard, equal-feature-count sampling across all 16 graphs per block (200 seeded repeats), minimum block effect. Synthetic software controls: identical, label-only, position-only, and mapping-only representations give zero primary fact contrast; fact-only gives positive primary contrast. Mapping-only may generate opposing conditional contrasts, illustrating that components alone are not pure fact estimates.

## Interpretation and closure

A positive primary result supports queried-country-associated feature composition across two wordings and changed list positions in this forced-choice pipeline. A null weakens that interpretation in this task. Neither establishes an abstract fact code, independent capital identity, causal circuits, or a repaired traceback. Option mapping, ordinal instructions, entity-role binding, and task-conditioned computations remain possible explanations. A positive same-label component alone is especially not sufficient: correct labels impose a dependency between fact and option mapping.

On completion (including pilot failure), produce a reproducible results summary, component figure, audit/validation record, and manuscript-ready text. Report v3 separately from v2 and the original three-model cohorts. Stop collection; do not search until significance. Technical errors may be repaired without changing frozen prompts/settings/statistics, with changes logged. A genuine external blocker must be reported rather than misrepresented as completion.
