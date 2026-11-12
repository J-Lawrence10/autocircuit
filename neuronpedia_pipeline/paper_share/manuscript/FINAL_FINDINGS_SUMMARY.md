# Paper findings and interpretation

Review materials updated 12 November 2026. The manuscript and figures use the final available datasets and corrected answer scoring, with the approved supporting sections A1–A8 and descriptive figure legends. This is a working paper for PI review, not a peer-reviewed publication.

The paper connects three findings. Questions about the same fact share more graph features across the three analyzed models. In the stronger Qwen3-4B comparison, that difference is larger when the answer letter stays the same. Selected wrong-answer graphs also resemble correct predictions giving the same answer more than correct predictions for the intended country. Together, these results show why feature overlap should be interpreted alongside the question and predicted response.

## Current data and primary comparison

The four-version design includes a starting question, its factual rewording, and two invented name controls. The values below are the final results: same-fact minus average other-fact Jaccard overlap within the same subject and evaluation set.

| Model | Four-version graphs available / planned | Included evaluation facts | Mean difference | Descriptive 95% interval |
|---|---:|---|---:|---|
| Gemma-2-2B | 120/120 | 8: chemistry 5, history 3 | 0.170 | [0.085, 0.276] |
| Qwen3-1.7B | 91/120 | 10: chemistry 5, geography 5 | 0.089 | [0.082, 0.098] |
| Qwen3-4B | 120/120 | 12: chemistry 5, geography 5, history 2 | 0.218 | [0.150, 0.307] |

All included evaluation facts have positive differences. The same facts recur across models, and facts within a subject share comparison questions. These are within-model associations, not independent observations that can be pooled to rank models.

The two Qwen3-4B history facts concern Columbus's flagship and Franz Ferdinand. Their overlap differences are 0.601 and 0.395, averaging 0.498, and both remain positive at equal and half feature counts. The two facts are each other's comparison partners, so these results describe the two questions rather than broad independent validation across history. Figure S9 shows their individual comparisons.

Gemma and Qwen3-4B also have 27 fact-by-wording graphs each. The stronger Qwen3-4B answer-letter study uses a separate 48-graph collection, and the selected-error study uses a separate 16-graph collection. These are not included in the graph counts above.

## Main findings

1. **Shared facts, words, and answers remain coupled in the initial comparison.** No other-fact question meets any of the three declared word-matching rules for the included facts: 0/8 Gemma, 0/10 Qwen3-1.7B, and 0/12 Qwen3-4B. All 108 directed other-fact comparisons differ in expected answer; the 30 model-specific same-fact pairs share it. The positive association therefore does not isolate factual meaning.

2. **Sentence pattern matters to the control comparison.** In Qwen3-1.7B, eight of ten evaluation questions share more features with the invented name control using the starting sentence pattern than with their factual rewording. All ten favor the factual rewording over the reworded invented name control. Matching broad next-token categories gives differences of -0.0109 (n=9) and +0.1059 (n=10), respectively. The fact-by-wording study also finds positive average associations with both fact and wording, but their ordering differs across models and only Qwen3-4B geography passes all nine expected-token checks.

3. **The same-country overlap difference is larger when the answer letter stays the same.** All 48 Qwen3-4B predictions across six country pairs are correct. The difference is 0.0628 with the same A/B answer and -0.0022 with a changed answer. Their prespecified average is 0.0303 (95% block-bootstrap interval 0.0265–0.0338). The direct paired difference is 0.0650, with a Student-t interval of 0.0553–0.0746; this direct difference analysis is exploratory. Near zero is not proof of equivalence or missing factual knowledge.

4. **Wrong-answer graphs can resemble correct same-answer graphs.** All eight selected comparisons favor the correct response producing the same answer over the correct response for the intended country. Mean differences are 0.1983 for A/B answers and 0.2649 for capital names. These cases share one country pair and overlapping controls; they do not estimate general failure frequency or identify a causal shortcut.

5. **The feature-sharing result survives the main sensitivity checks.** Equalizing feature counts preserves positive model averages, although one Gemma fact reverses. Qwen3-1.7B averages are 0.0835 at the subject-specific minimum feature count and 0.0331 at half that count, with all ten fact-level averages positive. Qwen3-4B averages are 0.1811 and 0.0724, with all twelve fact-level averages positive. Influence-weighted and reconstruction-error-inclusive comparisons are also positive. Qwen3-1.7B's coarser edge-flow comparison is inconclusive, so the result does not extend to every aspect of graph structure. The Qwen3-4B answer-related differences remain after the specified feature-count and graph-location filters.

6. **History graphs can stay similar while the selected year changes.** All 16 Qwen3-4B historical-date graphs passed integrity checks, including 11 correct and five incorrect predictions. When dates assigned to A/B were swapped, five comparisons retained the predicted letter but selected different years, with Jaccard overlaps of 0.795–0.911. Three comparisons changed the letter to retain the same correct year, with overlaps of 0.512–0.532. The eight question/context-order comparisons also had higher overlaps when the predicted letter was unchanged. Figure 6 shows every comparison and real prompt examples. These two event pairs are descriptive evidence, not independent population tests or completion of the original 160-graph study.

Qwen3-1.7B still has 11/40 history graphs and no complete four-version sets because 29 requests exceeded the hosted input limit. These are collection failures, not wrong answers. The original Qwen3-4B history gate remains 15/20 against a required 20/20, with no evaluation graphs from that protocol. The additional 16-graph analysis includes all historical prompts from that preliminary check and does not change the original gate or three-model inclusion. Gemma still contributes three history facts to the primary comparison. Required-letter contrasts do not uniformly reproduce the geography pattern; their event-pair summaries remain in Supporting analysis A7.

## What the findings mean

Feature overlap is associated with both the question relationship and predicted response. It cannot, on its own, establish that the model retrieved the intended fact or answered correctly.

The source of the answer-associated pattern remains unresolved. Shared activity involved in producing an answer and output-dependent selection of features into a graph could both contribute. Removing nodes after export does not undo that selection. The wrong-country source weights in selected capital-name errors are compatible with incorrect reference selection, but position matching and mishandled negation remain alternative explanations. Discussion Section 4.3 presents these questions as future research, not experiments already performed.

## Scope, provenance, and readiness

The main paper uses one current sample per model. Earlier subset analyses remain in the audit archive, not as extra data or an independent replication. The Qwen3-1.7B analysis was specified after earlier findings were known, with unchanged questions, expected tokens, and inclusion rules. The paper retains the distinction between prespecified outcomes and exploratory analyses.

Qwen3-4B has all 147 planned four-version and fact-by-wording graphs. Answer scoring accepts `Maria` and `María` as the same flagship answer. The correction was applied across 170 available factual outputs and changed one classification; the superseded strict-text decisions remain in the audit archive, not as an alternative main result. The final Qwen3-4B primary sample has twelve facts. Its output-type-matched control sample has ten because all four controls for the history facts predict commas. No shortened history prompts, new graphs, models, or local inference were introduced for the scoring correction.

Scripts, raw graphs, metadata, checksums, analysis plans, derived tables, and figures are maintained in the author archive. The sharing folder contains the current manuscript, figures, tables, protocols, and selected code, but excludes raw exports, tokenizer/model files, credentials, and reference PDFs. Automated checks do not substitute for independent scientific review. Author approval, independent review, redistribution permissions for a fuller release, and venue formatting remain before submission.
