# Error-aware whole-graph analysis protocol

**Status:** frozen before the confirmatory whole-graph outcomes are computed  
**Protocol date:** 2026-07-14  
**Scope:** sparse attribution graphs exported by the Neuronpedia pipeline for the controlled Gemma-2-2B and Qwen3-1.7B prompt cohorts, plus the independent Gemma format-variation cohort.

## 1. Decision this protocol is designed to make

The paper will not be organized around traceback. The confirmatory question is:

> Within a fixed model-exporter-decomposition pipeline, does a sparse attribution graph preserve fact identity across a paraphrase more strongly than it resembles graphs for other facts, after excluding reconstruction-error nodes and known ambiguous identifiers?

This is a claim about **graph representation within a model pipeline**, not proof that a graph is a causal mechanism, a complete input-to-output circuit, or a model-independent representation. Cross-model differences will be described as model-pipeline differences because model depth, decomposition method, exporter behavior, graph density, and model identity are confounded.

## 2. Cohorts and experimental units

### Confirmatory cohort

- Model pipeline: Gemma-2-2B.
- Manifest: `config/paper_control_manifest.csv`.
- Held-out split: 15 fact-level experimental units, five from each of chemistry, geography, and history.
- Each fact has four preregistered roles: target, positive paraphrase, same-template nonce control, and paraphrased nonce control.
- The fact, not a graph pair or graph node, is the unit of inference.

### Development cohort

- The remaining 15 Gemma facts have the same balanced domain and role design.
- Development results are diagnostic and descriptive. They cannot replace a failed held-out primary test.

### Replication cohort

- Qwen3-1.7B chemistry subset: eight complete four-role facts.
- This cohort is a direction-of-effect replication under a different model pipeline. It is underpowered for a definitive cross-model comparison.

### Independent crossed-format cohort

- Gemma-2-2B: 27 graphs from three domains, three facts per domain, and three prompt formats per fact.
- This cohort is used to estimate the relative contribution of fact identity and prompt format. Pairwise similarities are not treated as independent observations.

## 3. Graph eligibility and exclusions

A graph is eligible only when it:

1. maps uniquely to a manifest row and the intended model, prompt, role, domain, and split;
2. parses under the expected `metadata`, `nodes`, and `edges` schema;
3. has unique node identifiers after applying the declared collision policy;
4. has no dangling edge endpoints;
5. records the exporter/decomposition metadata needed to identify the model pipeline; and
6. belongs to a complete comparison set for the analysis in question.

For the fact-identity analyses, the target and positive-paraphrase graphs must also have the manifest's expected factual token as their top prediction after whitespace normalization. This rule is applied identically to both models. Graphs for incorrect factual completions remain in the audit but do not support a claim about the representation of a successfully retrieved fact.

The primary analysis uses collision-safe converted graphs and excludes:

- reconstruction-error nodes (`feature_id == -1` or an error node type);
- embedding and output-logit nodes;
- nodes involved in ambiguous identifier collisions;
- edges incident to any excluded node; and
- non-finite node or edge values.

Exclusions will be reported by graph and reason. No graph may be removed because of its effect size or statistical result. Clean-export-only and error-inclusive variants are sensitivity analyses, not replacements for the primary definition.

## 4. Representations and outcomes

### Primary representation: active feature identity

For each graph, active features are collapsed across token positions to the set of unique `(feature_family, layer, feature_id)` identities. `feature_family` prevents Qwen's transcoder and LoRSA namespaces from being conflated; it is constant for the eligible Gemma features. Feature identity is compared only within the same model pipeline.

For fact `i`, let:

- `S_i+` be Jaccard similarity between its target and positive-paraphrase feature sets;
- `S_i-other` be the mean Jaccard similarity between its target and all eligible positive-paraphrase graphs for different facts in the same domain and split.

The preregistered fact-level primary margin is:

`M_i = S_i+ - S_i-other`.

Using all matched other facts, rather than selecting the most favorable or unfavorable comparator after seeing outcomes, makes the estimand fixed and reproducible. A minimum-comparator sensitivity will be reported separately as a stringent worst-case check.

### Secondary representations

All secondary outcomes are reported as a family and multiplicity-corrected.

1. **Influence-weighted feature cosine:** aggregate `abs(influence)` by `(feature_family, layer, feature_id)` and compute sparse cosine similarity.
2. **Normalized layer profile:** per-layer sum of absolute feature influence, normalized to unit mass. Layers are compared directly within a pipeline and by relative depth only for descriptive cross-pipeline plots.
3. **Edge-flow profile:** aggregate absolute eligible edge weight by source and target layer, normalized to unit mass.
4. **Graph morphology:** eligible feature count, edge count, density, layer span, skip-edge fraction, and weight concentration. These are descriptive unless an explicit fact-level contrast is defined.
5. **Decomposition-error burden:** fraction of absolute node influence and incident edge weight assigned to reconstruction-error nodes before primary exclusions. This is a quality diagnostic and moderator, not mechanistic evidence.

### Control contrasts

For each target graph, similarity to the positive paraphrase is contrasted with:

- same-template nonce control;
- paraphrased nonce control; and
- other factual positive paraphrases in the same domain and split.

Nonce comparisons are secondary because nonce prompts can change output type. Output token class, whitespace/symbol status, and correctness will be tabulated and used in a matched-output sensitivity analysis where sufficient matches exist.

## 5. Statistical analysis

### Primary held-out test

- Null: the mean held-out fact-level primary margin is at most zero.
- Test: one-sided exact sign-flip randomization over the 15 fact-level margins (`2^15 = 32,768` assignments).
- Effect estimate: mean margin.
- Uncertainty: 95% percentile bootstrap confidence interval with 10,000 resamples clustered at the fact level, using a fixed recorded seed.
- Descriptive robustness: median margin and the number of positive fact-level margins.

The primary test passes only if both:

1. exact randomization `p <= 0.05`; and
2. the 95% fact-cluster bootstrap confidence interval excludes zero.

No multiplicity adjustment is needed for this single primary endpoint.

### Secondary and replication tests

- Secondary Gemma representation/control contrasts use fact-level sign-flip tests and fact-cluster bootstrap intervals.
- Holm correction controls family-wise error across the prespecified secondary confirmatory tests.
- Qwen uses the same fixed feature-set outcome and fact-level procedure; its effect must be directionally positive and uncertainty must be reported. Failure to reach significance at `n=8` is not converted into evidence of absence.
- Crossed-format inference uses within-domain permutations of fact labels and format labels. Pairwise graph comparisons are summarized within fact/domain cells before inference to avoid pseudo-replication.
- All tests report exact `n`, effect size, interval, raw `p`, and adjusted `p` where applicable. No star-only reporting is allowed.

## 6. Robustness analyses

The following analyses are mandatory and cannot silently redefine the primary result:

1. clean-export-only graphs;
2. error-inclusive feature representation, with errors kept as a separate class rather than a shared feature ID;
3. influence-weighted cosine instead of binary Jaccard;
4. minimum other-fact similarity margin as a stringent comparator check;
5. output-type-matched controls where support exists;
6. results stratified by domain and development/held-out split;
7. leave-one-fact-out influence analysis;
8. graph-size-adjusted diagnostic regression, with fact as the clustering level; and
9. a negative-control permutation in which fact labels are shuffled within domain and split.

If the conclusion changes under a defensible collision or error policy, the paper must present that dependence as a limitation rather than select the favorable policy.

## 7. Claim ladder and publication gates

### Gate A: artifact validity

Pass requires complete manifests, deterministic file selection, schema validation, collision accounting, no dangling edges, recorded software/environment information, and a one-command dry run. Failure blocks all quantitative claims.

### Gate B: confirmatory fact-identity result

Pass requires the held-out primary test criteria in Section 5 and a positive direction in all three held-out domains. Failure forbids the claim that graphs preserve fact identity across paraphrases.

### Gate C: robustness

Pass requires the primary direction to survive clean-export-only, influence-weighted, and leave-one-fact-out analyses. A sensitivity may be less precise, but no single fact or known exporter collision may determine the conclusion.

### Gate D: replication

For a broad model-pipeline claim, Qwen must show the same direction. If not, the main claim is restricted to the Gemma pipeline. Statistical significance in the small Qwen cohort is desirable but not required for a explicitly limited directional replication claim.

### Gate E: crossed fact/format interpretation

Statements about fact identity versus prompt form require the independent 27-graph crossed-format analysis to show separately estimable fact and format effects. If only format survives, the publishable result is prompt sensitivity, not factual representation.

### Allowed fallback stories

1. **Full pass:** sparse graph feature composition carries a reproducible within-pipeline fact signal while coarse geometry is more stable; reconstruction error bounds interpretation.
2. **Gemma-only pass:** same claim, explicitly restricted to one model pipeline; Qwen is an inconclusive small replication.
3. **Format-only pass:** sparse attribution graphs are substantially prompt-form sensitive, and apparent semantic overlap depends on representation and decomposition quality.
4. **No substantive pass:** release an audit/negative-result artifact, but do not submit a paper claiming factual circuits.

Traceback success or failure is not a publication gate and will appear only as a method audit or appendix if it clarifies graph coverage.

## 8. Reproducibility deliverables

Before submission, the artifact must include:

- immutable input and analysis manifests with checksums;
- environment lockfile and recorded Python/package versions;
- fixed seeds and exact command lines;
- machine-readable validation, exclusions, and result tables;
- one script or command that regenerates every paper table and figure;
- a fast smoke-test mode and full-run mode;
- recorded CPU/GPU, memory, storage, wall time, and external API usage;
- data and code availability statements, license, and provenance notes;
- a manuscript reproducibility statement and completed venue checklist; and
- a clean-room reproduction attempt from the documented instructions.

These requirements follow the current NeurIPS paper checklist emphasis on experimental detail, uncertainty, compute disclosure, and reproducibility; ICLR's reproducibility-statement guidance; and ACM artifact-evaluation criteria that artifacts be documented, consistent, complete, exercisable, and validated.

## 9. Change control

Any change after the protocol date must be appended to a deviation log containing:

- timestamp;
- exact change;
- reason;
- whether any affected outcome had already been inspected; and
- the analyses impacted.

Changes motivated by a result are exploratory by definition. They may generate future hypotheses but cannot be relabeled confirmatory in this paper.

### Deviation log

- **2026-07-14, before outcome computation:** feature identity was expanded from `(layer, feature_id)` to `(feature_family, layer, feature_id)` after the schema audit showed that the Qwen pipeline contains both cross-layer-transcoder and LoRSA feature nodes. This prevents namespace conflation. No whole-graph confirmatory outcome had been computed or inspected.
- **2026-07-14, before outcome computation:** factual correctness was made an explicit pair-level eligibility rule after the raw inventory showed that the presence of four graph files is not equivalent to successful retrieval. Both target and positive-paraphrase top predictions must match the manifest token. This is applied to Gemma and Qwen alike; excluded graphs remain in the audit.
