# Accepted spelling sensitivity analysis

## Question and decision

Does accepting the correct accented spelling `María` change the Qwen3-4B history comparison? The original exact-text analysis rejects this token because the expected completion is `Maria`. The author requested an explicit correction check after seeing that mismatch. This is therefore a post hoc sensitivity analysis, not a new preregistered result or an independent replication.

Royal Museums Greenwich identifies Columbus's 1492 flagship as [Santa Maria](https://www.rmg.co.uk/collections/objects/rmgc-object-12245). Fundación Nao Victoria identifies the same flagship as [Santa María](https://www.fundacionnaovictoria.org/history-nao-santa-maria/). These records support accepting either complete spelling in this question. They do not justify treating all accent differences as interchangeable.

## Fixed scope and rule

- Use saved graphs only. No hosted requests, replacement prompts, new models, or local model inference.
- Preserve the original exact-match results and raw files. Do not replace the confirmatory inclusion rule silently.
- Apply the same fact-specific accepted-answer registry to all three models, both factual prompt roles, and both development and evaluation sets.
- Accept `Maria` and `María` for `columbus_americas` with expected `Maria`. Trim surrounding whitespace and allow Unicode NFC equivalence within the registered spellings. Do not accept partial words, whitespace, synonyms for other facts, case changes, or unrelated accent differences.
- Inventory all available factual outputs for other accent-only mismatches, using accent removal for discovery only. Additional unregistered matches are reported, not automatically accepted.
- Preserve the four-graph requirement, integrity exclusions, development/evaluation split, and requirement for another qualifying fact within the same model and subject.
- Retain each graph's actual predicted token. Accepting an answer spelling must not relabel its output, change feature identities, or change the graph itself.

## Analysis and reporting

Freeze the registry, code, protocol, saved input records, and Qwen3-4B graph hashes before calculating the new overlap results. Reconstruct Qwen3-4B representations using the existing loader and verify the original included fact-level metrics. Recompute its controlled analysis with the accepted-spelling flags, using the existing metric definitions, 10,000 bootstrap draws, and seed 20260830. Compare exact-match and accepted-spelling samples, subject summaries, all four similarity measures, invented name controls, and graph-quality sensitivities.

Report all newly included history facts individually with their own-rewording and other-fact overlaps. The two candidate history facts would reuse each other as comparators; they are not independent replications. Treat the history result descriptively. Existing test and interval calculations may be archived for transparency but do not establish a new confirmatory history finding or repair the original three-subject gate retrospectively.

Repeat equal-feature-count sampling at the smallest group size K and K/2, 200 repetitions per condition. Use a fixed seed of 20261111 plus the character-code sum of the model, subject, and fraction label, with separate random streams for each group. This is a new descriptive sensitivity; retain the earlier subsampling estimates separately. Reuse each sampled graph across comparisons within a repetition.

Update Methods, Results, Discussion, supporting analyses, sample accounting, the outline, the findings summary, figure legends, and the local review package. Keep exact-match estimates identifiable; display accepted-spelling results separately. Distinguish a correct spelling variant from a partial answer or an incorrect prediction in the output audit. Preserve all exclusions and negative results. Do not push to GitHub unless requested.
