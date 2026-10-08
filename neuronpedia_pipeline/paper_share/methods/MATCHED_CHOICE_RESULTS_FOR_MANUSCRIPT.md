# Matched-choice controls: results ready for manuscript integration

Original three-model cohorts remain separate. The completed matched-choice graph test is Qwen3-4B only. This is an evidence package, not a claim that the manuscript is submission-ready.

## Main result in plain language

The graphs contain a small, consistent association with which country is asked about, but a much larger association with the A/B label being produced. The fact-associated advantage is concentrated in comparisons preserving the answer label; it is not visibly retained on average when the label changes. This is not evidence of an answer-independent fact code.

## What changed and what completed

- Plain-completion Qwen3-4B passed only 4/8 pilot decisions by always choosing A; no v1 held-out graph cohort was generated.
- Gemma-2-2B supplied the correct capital names on all eight pilot prompts, but 0/8 requested A/B labels; this was response-format failure, not factual-error evidence.
- A separately frozen, explicitly outcome-informed Qwen official-chat revision passed 8/8 pilot decisions and 48/48 held-out decisions.
- All 48 v2 raw hashes and converted-file hashes verify; archived pairwise values reconstruct the six reported block contrasts. These exports have zero raw ambiguous IDs and duplicate endpoint edges.
- The v2 final status-file rename failed after output creation. An administrative recovery record documents correction without regenerating data or changing estimates.

## Manuscript-ready methods (v2)

Following failures of the plain-completion behavior pilots, we prospectively froze a Qwen3-4B chat-framed forced-choice follow-up before requesting its outcomes. Each of six country-pair blocks crossed queried country, capital-to-A/B mapping, and wording (eight graphs per block). Each block had identical word and tokenizer-ID multisets. France/Germany was a separate behavior-only pilot. All six blocks were required to have correct top A/B decisions, matched token multisets, and valid graph representations. The primary endpoint was the equally weighted mean of same-fact advantages within same-label and changed-label comparisons. Uncertainty used six blocks, not 48 independent graphs. The exact conditional fact-correspondence null contained 4096 assignments; the prespecified v2 multiplicity family comprised three model/version opportunities. These were locally frozen protocols, not public preregistrations.

## Manuscript-ready results (v2)

All 48 held-out top-label decisions were correct. The balanced same-fact Jaccard contrast was 0.0303 (95% block-bootstrap interval 0.0265 to 0.0338), positive in all six blocks (exact conditional correspondence p=0.000244141; multiplicity-adjusted p=0.000732422). The descriptive output-label contrast was 0.2827. The same-label fact contrast was 0.0628, whereas the changed-label contrast was -0.0022. The latter is a descriptive near-zero estimate, not an equivalence test. The average balanced fact contrast therefore does not demonstrate invariance to the produced answer label.

## Essential limitations

- Six geography blocks in one model; the paper has three models overall, but this control does not establish three-model replication.
- Feature-set overlap is not topology, complete input-to-output traceback, or a causal intervention.
- Output-label magnitude comparison is descriptive; ninefold larger does not mean ninefold variance explained.
- Correct label depends on both the queried fact and option mapping. Thus same-label versus changed-label components are not pure fact manipulations; option mapping and entity-role binding remain possible explanations.
- V2 does not separate queried identity from query order. V3 specifically tests list-position dependence in a different task, not all possible semantic confounds.
- Pilot revisions, exclusions, failed controls, and incomplete original model-extension jobs must remain visible in the paper.

## Suggested paper structure

1. Original three-model association: factual paraphrases share features, within the eligible cohorts.
2. Why that alone is insufficient: lexical and answer matching lacked support in the original comparisons.
3. Stronger Qwen3-4B controls: identical token inventories, crossed answer mappings, and a small balanced fact-associated signal.
4. The critical boundary: answer-label dependence, conditional components, and the separately reported final position test.
5. Conclusion: characterize what overlap measures; do not claim abstract semantic or causal circuit recovery.

## Final position-balanced follow-up (v3)

Outcome-informed follow-up specified after v2. It uses the same six country pairs in a new ordinal-selection task; these are not unseen facts. Queried country, list position, answer mapping, and wording vary independently in 16 cells per block.

The pilot failed: 8/16 correct A/B decisions. No held-out graphs were generated.

This is a task/behavior limitation, not evidence that a graph-level fact effect is zero. The fixed stopping rule closes this control round without prompt replacement.
