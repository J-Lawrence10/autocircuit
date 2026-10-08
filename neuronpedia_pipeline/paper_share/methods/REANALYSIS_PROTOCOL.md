# Cross-Domain Circuit Paper: Reanalysis Protocol

**Status:** correction protocol 1.0  
**Preregistered:** July 11, 2026

## Amendments recorded before corpus-scale inference

### A1: Null endpoint clarification (July 11, 2026)

The initial pilot implementation tested maximum feature-hub concentration
against the shuffled-weight null. After one complete Gemma gold control pair,
and before corpus-scale analysis, the primary within-graph null endpoint was
clarified as target-versus-alternative top-ten hub specificity
(`1 - Jaccard`). Maximum hub concentration remains a separately reported
secondary null endpoint. All interim outputs made before this amendment are
invalidated and rerun. A feature-hub claim must pass both corrected endpoints;
a route-specificity claim need only pass the specificity endpoint and the
prompt controls.

### A2: Numeric next-token exclusion (July 11, 2026)

Inspection of the original history graphs showed that all three generators
often selected a standalone whitespace token immediately after prompts ending
in `in` or `was`; the expected year was therefore not a logit in the graph.
Such graphs are recorded as `excluded_missing_expected_logit` and never fall
back to another token. A trailing-space/immediate-year prompt repair will be
probed separately. If adopted, it will be frozen before controlled history
generation and reported as an amended cohort rather than silently substituted
for the original history graphs.

### A3: Controlled-cohort logit coverage (July 11, 2026)

Before bulk controlled generation, `desiredLogitProb` was raised from the
legacy default 0.95 to the API maximum 0.99 to maximize availability of a
within-graph alternative-token control. Graphs in which a single target token
itself exceeds 0.99 remain excluded as `excluded_missing_contrast_logit`;
another token is never fabricated or borrowed from a different graph.

### A4: Amended historical entity cohort (July 11, 2026)

Two numeric repair probes confirmed that the generator tokenizes years into
uninformative single digits (`1` after a trailing space and `4` after a `19`
prefix). Supplying more digits would leak the answer and trace numeric
continuation. Before bulk history-control generation, the ten history facts
were therefore reformulated as single-token historical entity completions
(for example `II`, `Titanic`, and `Bastille`). Development/held-out assignments
and all four prompt-control roles remain unchanged. This is an amended cohort;
the original year-based history graphs remain quarantined exclusions.

### A5: Geography positive-control repair (July 11, 2026)

The first five geography paraphrases (`X's capital city is`) made the expected
capital exceed 0.99 probability and therefore eliminated the mandatory
alternative-logit control. Before any geography pair entered aggregate
inference, the positive-control template was changed to
`X is governed from the capital city of`. A France probe produced `Paris` at
0.929 with nine alternatives. The amended template is used uniformly for all
ten geography facts; superseded graphs remain excluded.

### A6: Independence positive-control repair (July 11, 2026)

The initial independence paraphrase made `Jefferson` exceed 0.99 and removed
the contrast. Before the history aggregate was completed, it was replaced by
`In Philadelphia the Declaration of Independence was drafted by Thomas`.
The probe returned `Jefferson` at 0.988 and retained `Paine` as a contrast.

## Scope

This protocol replaces the legacy traceback, bottleneck, minimal-pathway, and
steering-distribution analyses. Historical outputs remain available for
auditability but cannot support current claims.

The original 60 Gemma-2-2B and Qwen3-4B graphs are the discovery corpus. The
71 Qwen3-1.7B graphs are a separate replication corpus because they use a
different model, graph generator, component schema, and graph density.

## Analysis unit

The unit is a prompt-model-output-token graph. The primary route must start at
the preregistered expected-token logit. If that logit is absent from the graph,
the graph must be regenerated with sufficient logit coverage or excluded. It
must not silently fall back to a final-layer SAE feature.

Every route must be an explicit connected sequence of directed edges ending at
that logit. Edge signs must be retained. Reconstruction-error and LORSA-error
components are reported separately from SAE feature hubs.

## Required controls

Each of the 30 factual pairs contains four prompts, enforced by
`config/paper_control_manifest.csv`:

1. `target`: the original factual query.
2. `positive_paraphrase`: the same fact with a different surface form.
3. `negative_same_template`: the original template with a nonce entity.
4. `negative_nonce`: the nonce fact with the paraphrased surface form.

Each graph additionally contains two internal controls:

- the expected or API-targeted output logit;
- a preregistered alternative-token logit, otherwise the strongest available
  non-target logit.

The graph null permutes signed weights within source-layer/target-layer strata,
preserving topology, layer structure, and the marginal signed-weight
distribution.

## Primary route statistics

- Route mass: product of local absolute incoming-attribution fractions.
- Route sign: product of signed edge directions.
- Feature-hub coverage: fraction of retained route mass passing through a
  feature.
- Target-contrast specificity: Jaccard overlap of the top ten feature hubs.
- Prompt invariance: target versus positive-paraphrase hub overlap.
- Prompt specificity: target-positive overlap minus the larger of the two
  target-negative overlaps.

The term *hub* is descriptive. It does not mean necessary, sufficient, causal,
or an information bottleneck.

## Robustness and decision rules

Paper analyses use at least 200 shuffled-weight nulls during development and
1,000 for final results.

A feature-level result is eligible for interpretation only if:

- all reported routes pass an automated connectivity check;
- the top-ten hub set has median Jaccard at least 0.60 and minimum Jaccard at
  least 0.40 across the preregistered coverage/branch grid;
- the observed statistic exceeds the shuffled-weight null after Benjamini-
  Hochberg correction at FDR 0.05;
- target-positive similarity exceeds both target-negative similarities, with
  a paired bootstrap 95% interval excluding zero;
- the effect replicates in held-out facts rather than only prompts used to
  choose parameters.

Architecture claims require at least three independently trained model
families or must be labeled as a two-model comparison. Model, SAE, graph
generator, graph density, and layer count may not be collapsed into the word
*architecture*.

## Steering controls and metrics

Existing steering responses are reanalyzed, but their feature-selection labels
(`bottleneck`, `essential pathway`) are discarded.

New steering experiments must contain:

- previously responsive features as positive controls;
- random layer-matched features;
- activation- and frequency-matched non-hub features;
- strength-zero sham calls;
- repeated unsteered baselines;
- symmetric dose levels, initially -20, -10, -5, 0, 5, 10, 20;
- randomized call order and correction across all feature-prompt-strength
  comparisons.

The primary distributional endpoint is first-token Jensen-Shannon divergence
over the union of returned top-k tokens plus a residual `OTHER` bin. Later
positions are analyzed only while baseline and steered generations share the
same sampled prefix. Text change is secondary and must not be interpreted as a
direct measure of mechanistic importance.

## Claim ladder

- **Descriptive:** a route or feature is present in a thresholded graph.
- **Above-null:** a preregistered route statistic exceeds graph nulls.
- **Specific:** the result passes token and prompt controls.
- **Predictive:** it generalizes to held-out facts/models.
- **Causal:** a controlled intervention establishes necessity or sufficiency.

Claims cannot skip levels.

## Post-analysis traceback verification (July 12, 2026)

After completion of the final null runs, all 152 controlled analysis files were
validated against their converted graphs with
`scripts/validate_traceback_outputs.py`. The audit covered 14,133 routes and
36,694 stored route edges. Every route ended at its recorded logit, every edge
existed in the converted graph with the same direction and weight, all edge and
route signs were correct, route masses were internally consistent, target and
contrast nodes were distinct, and all final files contained the required 1,000
null runs. A fixed-seed fresh rerun for one Gemma and one Qwen graph was
byte-identical across repetitions and reproduced the stored observed routes.

The same audit identified two interpretation limits. Only 4,865/14,133 routes
(34.4%) terminate at an input embedding; 9,268/14,133 (65.6%) terminate at a
source node whose incoming edges are absent from the thresholded graph. These
are connected upstream-source-to-logit routes, not complete input-to-logit
paths. In addition, 62/152 selected contrast logits are whitespace,
punctuation, or symbol tokens. They are valid next-logit competitors but not
semantic alternative answers.

Accordingly, future outputs report embedding anchoring and contrast-token class
explicitly. Publications must use `route`, not `complete input pathway`, unless
the route terminates at an embedding. Target-versus-contrast results must be
described as next-logit specificity unless a semantic contrast was specified
in advance. The current nonce controls also do not always produce an output of
the same semantic type as the factual answer, so target/paraphrase versus nonce
overlap supports prompt/output reproducibility but does not by itself isolate
fact identity.

### Exported-node identity audit

A subsequent raw-to-converted equivalence audit found that the converter
preserved all 248,211 node records and 20,477,033 edge records, but 84/120 Gemma
controlled exports contain 109 duplicated `node_id` values. Each collision
merges a transcoder feature and an MLP reconstruction-error node under the same
identifier. The associated JSON links reference only that ambiguous identifier;
the two node identities therefore cannot be recovered safely from the export.
Qwen contained no duplicated node identifiers.

The previous `DiGraph` loader silently retained the last node/edge record. It
now rejects duplicate node identifiers and duplicate edge pairs by default. A
separate `drop` sensitivity policy removes every ambiguous node and all incident
edges rather than guessing ownership or summing unlike components. This policy
is marked sensitivity-only and writes non-overlapping output filenames.

Only 17/10,933 Gemma observed routes touched a colliding identifier and none of
the top-ten hubs did. After dropping all ambiguous identifiers, 119/120 top-ten
hub sets were unchanged; all 30 directional prompt controls and the mean
specificity margin (0.494) were exactly unchanged. The final drop-policy
sensitivity reran all 120 graphs with 1,000 shuffled nulls. No graph passed the
route-specificity or feature-hub gate; the smallest uncorrected empirical
p-values were 0.499 and 0.360, and all adjusted q-values were 1.0. The original
negative Gemma null conclusion is therefore robust to conservative removal of
every ambiguous identity.

Three fresh July 14 exports were checked prospectively. Two contained no node
or edge collisions, but one still reused an identifier for a transcoder feature
and an MLP reconstruction-error node and contained four duplicate edge pairs
with differing weights. Strict conversion rejected it. The exporter defect is
intermittent and remains present, so every new export must pass identity checks.

### Reconstruction-error source audit

All non-embedding source terminations already exist in the raw exports and are
explicit MLP reconstruction-error or LORSA-error components, rather than edges
lost during conversion. For Gemma, embedding-terminated routes account for
44.4% of routes and 55.0% of traced route mass. For Qwen3-1.7B chemistry, they
account for 0.22% of routes and approximately 0.004% of traced mass. These
fractions were robust across the tested coverage and branching settings.

Consequently, Qwen's present attribution graphs are overwhelmingly driven by
un-decomposed error components and cannot support feature-complete pathway
claims. Future outputs report terminal-reason mass and source-component types,
not only route counts.

### Post-hoc matched-control and component sensitivities (July 14, 2026)

These analyses were specified after inspection of the final outputs and do not
replace the preregistered primary endpoint. To reduce nonce-output-type
confounding, each factual target was compared with positive-paraphrase graphs
for other facts matched on domain, split, and expected-token class. Gemma beat
the hardest such factual negative in 29/30 pairs, with one tie (mean margin
0.426, 95% bootstrap CI 0.339–0.516). Qwen chemistry passed 8/8 (mean 0.389,
95% CI 0.281–0.500).

Feature hubs were then recomputed separately for embedding-terminated and
source-terminated routes. Gemma embedding-route hubs passed directionally in
30/30 pairs (mean margin 0.494, 95% CI 0.426–0.561). Source-route feature hubs
passed in all 25 pairs with nonempty sets in all four roles (mean 0.399, 95% CI
0.337–0.461). Admitting reconstruction-error nodes into source-component hubs
reduced the Gemma result to 24/30 directional pairs and a mean margin of 0.138.
Qwen had no fully evaluable embedding-only pair; its source-feature result was
8/8, while the error-inclusive result was 6/8 with a mean margin of 0.188.

These sensitivities support reproducible SAE feature structure while showing
that unresolved error components weaken specificity. They do not establish
above-null or causal feature importance.

## Execution

Validate controls:

```powershell
python scripts/validate_experiment_controls.py
```

Dry-run a batch:

```powershell
python scripts/reconvert_and_trace_v3.py --model gemma-2-2b --limit 3
```

Run a pilot with paper-grade controls:

```powershell
python scripts/generate_controlled_graphs.py --models gemma-2-2b --limit 12 --execute
python scripts/reconvert_and_trace_v3.py --model gemma-2-2b --controls-only --null-runs 200 --execute
```

Run one converted graph directly:

```powershell
python scripts/traceback_v3.py --file PATH_TO_CONVERTED_V3.json --positive-token " Au" --negative-token " gold" --null-runs 200 --stability
```

The legacy scripts require explicit override flags and are not part of this
protocol.

## Reporting

Report exclusions, missing expected logits, all tested parameter settings,
null definitions, corrected p-values, effect sizes, uncertainty intervals, and
negative results. Do not select a decay factor, branch cap, layer boundary, or
feature threshold after viewing the outcome without labeling the result
exploratory and testing it on held-out data.
