# Exploratory confound checks - 5 September 2026

Analysis plan written after inspection of the original and extension outcomes, but before computing these additional sensitivities. These are exploratory, not preregistered primary tests. Original cohorts, expected answers, exclusions, hypotheses, and gates remain unchanged. No model weights or local inference will be used; tokenizer-only files may be downloaded from the official model repositories.

## 1. Frozen inputs and reconciliation

Read the archived graph audits and load their recorded files. Verify file hashes and reconstruct collision-safe feature identities using the existing representation code. Reproduce every eligible held-out primary fact margin to numerical tolerance before any sensitivity. Maintain three independent model-pipeline analyses. Preserve unavailable/failed records in the answer audit.

## 2. Feature-count sensitivity

Within each model/domain/held-out stratum, choose K as the smallest feature-identity count among eligible targets and positive paraphrases. Independently subsample every graph to K features without replacement; repeat 200 times with seed 20260905. Reuse each sampled graph across comparisons within a repetition, retaining comparator dependence. Also report floor(K/2), bounded below by one. Report per-fact mean margins across repetitions, descriptive fact-bootstrap intervals (10,000 resamples), and the distribution of pooled means across repetitions (sampling variability, not a confidence interval). This equalizes observed cardinality, not the feature-selection mechanism. Include all variants regardless of direction.

## 3. Shared-word and joint-size comparator support

Define word overlap as Jaccard of case-folded Unicode alphanumeric word sets, retaining numbers, with punctuation splitting words; no stopword removal, stemming, or outcome-dependent exclusions. For each primary target, compare its own paraphrase against other eligible paraphrases in the same domain/split using three prespecified rules:

- other-prompt word overlap at least as high as own-paraphrase overlap;
- absolute word-overlap difference at most 0.05;
- that 0.05 caliper plus other-paraphrase feature count within a factor of 1.25 of own-paraphrase feature count.

Average all qualifying comparators, not a selected best match. Report support denominators, lexical and feature-size balance, per-fact margins, and descriptive intervals where n >= 2. No support means not estimable, not zero. Do not widen calipers after inspecting outcomes. Tabulate shared expected output identity to expose any remaining answer-identity confound. No causal semantic interpretation follows solely from a positive matched margin.

## 4. Tokenizer-aware answer audit

Pin the official tokenizer repository revision and hash downloaded tokenizer files. Do not download model weights or use a mirror to evade gating. Validate tokenizer decoding against archived prompt token pieces and logit IDs. Use the exact stored prompt, without adding a chat template. Encode prompt plus the expected answer with either zero or one separating space (collapse to one variant when the prompt already ends in whitespace). A continuation is assessable only if its encoded prefix exactly matches the encoded prompt. Compare the recorded top logit ID to the next expected ID, and record whether the answer occupies one token or several. Keep whitespace-only next-token agreement separate from a substantive answer prefix.

Report strict trimmed-string agreement, tokenizer-confirmed whole-answer next-token agreement, substantive multi-token prefix compatibility, whitespace-only compatibility, mismatch under both explicit boundary conventions, or unresolved provenance/access/boundary. Multi-token compatibility does not verify full-answer retrieval. Archived generation checkpoint revisions are not fully pinned: even official current pinned tokenizers validated against observed pieces are an audit resource, not proof of historical bit-identical provenance. Never silently change primary eligibility based on this audit.

For the crossed cohorts, tabulate strict answer agreement and these classes by domain/format. Report whether all nine cells within a domain satisfy the strict rule; only those fully balanced domains may support an exploratory strict-output-filtered crossed summary. Do not select individual favorable cells.

## 5. Reporting

No new confirmatory p-values or publication-gate passes. Report small-sample uncertainty and non-estimable checks plainly. Save scripts, input/output hashes, seeds, environment versions, per-graph/per-pair/per-fact data, figures, and a report under data/model_extension/exploratory_20260905. Update a separate three-model manuscript draft with the empirical findings and limitations; preserve the original manuscript. Formal fact-versus-wording interaction inference and clean-room/public-deposit work remain separate future tasks.
