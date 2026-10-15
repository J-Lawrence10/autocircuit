# Paper outline and integrated argument

Updated 15 October 2026. This outline follows the working manuscript, **What Sparse Attribution-Graph Feature Overlap Preserves Across Prompt Changes**. The study evaluates a measurement; the selected failures support that argument rather than forming a separate mechanism paper.

## Research question and central conclusion

**Question:** Do similar attribution graphs reflect the fact being asked about—or the answer the model produces?

These are not mutually exclusive explanations. The experiments ask whether shared facts remain associated with feature overlap when wording and answer labels vary.

**Conclusion:** Reworded questions about the same fact share more features in the included samples. Stronger Qwen3-4B controls show answer-letter dependence, and selected wrong-answer graphs resemble correct responses producing the same answer more than correct responses to the intended country. Feature overlap alone therefore cannot certify correct factual processing or a representation independent of the answer.

## Logical sequence

1. Establish the original association.
2. Explain why the original controls cannot separate facts from shared words and expected answers.
3. Preserve the available words while varying the queried country and produced answer letter.
4. Ask what graph resemblance means when the selected answer is wrong.
5. Report robustness checks and the boundaries imposed by incomplete coverage and failed pilots.

The presentation follows this reasoning sequence, while Methods retains the actual study chronology and the distinction between rules fixed before collection and analyses designed after earlier outcomes.

## 1 Introduction

State the research question early. Use the example of reworded France-capital questions to show that a shared fact can also preserve country names and the expected answer. Define feature-set overlap as shared learned components, not similarity of every graph connection or recovery of a causal pathway.

Preview the original three-model comparison, the Qwen3-4B answer-control experiment, and the selected-error comparison. Position the contribution as an evaluation of what this measurement supports, not as a validated traceback tool or the first discovery of prompt sensitivity.

## 2 Methods

Figure 1 introduces the study design before the cohort and measurement details.

- **2.1 Cohorts and coverage:** distinguish graph collection from question inclusion; retain all three models, two families, uneven subject coverage, and the incomplete original Qwen3-4B extension.
- **2.2 Measurement:** define Jaccard overlap and same-fact minus average other-fact overlap. State the four required prompt/control roles, next-token matching rule, and within-subject comparison requirements. Distinguish questions from graph pairs and repeated facts across models.
- **2.3 Original controls:** explain fact-by-wording and made-up-name comparisons using concrete prompt relationships.
- **2.4 Exploratory checks:** feature counts, word-matching support, expected answers, tokenization, and reconstruction of archived outcomes.
- **2.5 Matched-choice follow-up:** six Qwen3-4B country pairs, eight prompts per pair, identical word/token inventories within pairs, and variation of query, answer mapping, and wording. The average of the same-letter and changed-letter fact differences remains the prespecified primary outcome.
- **2.6 Position pilot and selected errors:** distinguish the failed 16-item pilot from the separate 20-preview diagnostic and its 16 graph prompts. State the deliberate selection of four France/Germany cases, two formats, and reused controls.
- **2.7 Later audit and history pilot:** keep the added direct difference test exploratory. Explain saved-graph filters without treating them as causal interventions. Retain the final 20-check history gate and its planned, uncollected evaluation cohort.

Protocols were frozen locally, not publicly preregistered. Earlier failed pilots remain reported; follow-ups do not replace original observations or alter original eligibility.

## 3 Results

### 3.1 Reworded questions about the same fact share more features

Figure 2 establishes the association: means 0.170, 0.085, and 0.162 for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B, with 8, 5, and 10 included questions. Retain the archived intervals and tests. These are not 23 independent facts, and unequal subjects prevent a model ranking.

**Next question:** Is the overlap specifically associated with the requested fact, or with the words and expected answer that travel with it?

### 3.2 Original controls do not separate facts from shared words and answers

No included question has an other-fact comparator meeting the declared word-matching rules. All 86 directed other-fact comparisons differ in expected answer, whereas same-fact rewordings share it. This is missing comparison support, not proof that words or answers explain the full result.

Figures 3 and 4 describe the fact-by-wording and made-up-name controls. Their ordering varies across model pipelines and subjects. Only Qwen3-4B geography passes the strict expected-token rule in all nine crossed questions; its fact/wording differences are approximately 0.101/0.106. Do not infer equivalence, universal wording dominance, or model superiority. Supporting analysis A1 retains detailed output counts.

**Next question:** Does the association remain when available words are matched and the answer letter changes?

### 3.3 The overlap difference depends on the answer letter

Explain the four conditions before the estimates. All 48 Qwen3-4B decisions are correct, with six country pairs supplying the analysis units. Figure 5 presents:

| Prompt relationship | Same answer letter | Different answer letter |
|---|---:|---:|
| Same queried country | 0.800 | 0.485 |
| Different queried countries | 0.738 | 0.487 |

These are rounded mean Jaccard scores, not accuracy rates. Within the two columns, same-country minus different-country overlap is 0.0628 and -0.0022. Their average, 0.0303, remains the prespecified primary outcome. Preserve its interval and conditional correspondence test; do not promote the later exploratory component comparison to a prespecified endpoint.

The descriptive answer-letter difference is 0.2827. It is not a fraction of reasoning or variance explained. The added exploratory paired comparison is 0.0650, with Student-t 95% interval 0.0553–0.0746 and two-sided sign-flip p=0.03125 under the stated six-block assumptions. A near-zero changed-letter estimate does not establish equivalence or absent factual knowledge. Graph-location filtering preserves the measured difference without providing causal evidence.

**Next question:** If resemblance is associated with the produced answer, can an incorrect response resemble a correct one?

### 3.4 Selected wrong-answer graphs resemble correct responses with the same answer

Open with France–Berlin: a question identifying France by its list position produces Berlin; naming France produces Paris; naming Germany produces Berlin. The error graph resembles the correct Germany–Berlin graph more closely.

Explain why these cases were examined: the separate position pilot passed only 8/16 checks and stopped before its planned evaluation graphs. The subsequent diagnostic passed all four literal/replay checks. Its deliberately selected errors are not a population sample.

Figure 6 reports 16 clean graphs, eight reproduced errors, eight correct named-country controls, and eight comparisons favoring the same-output control. Mean differences are 0.1983 for A/B responses and 0.2649 for capital names; equal-feature-count values are 0.1851 and 0.2361. Retain the graph-location checks and descriptive, dependent nature of the comparisons. Position matching, negation errors, and answer-associated graph construction remain alternatives. Supporting analysis A3 retains source-location observations and omitted-logit qualifications.

### 3.5 Equal feature counts preserve positive averages but not every question

Report the original feature-count check after the main argument. Positive averages survive equalizing counts, but one Gemma question reverses. This narrows the feature-count explanation; it does not remove differences in words, answers, or feature selection. Keep the historical regression-intercept correction and Supplement S3. Cite Supporting analyses A1–A2 for output and export checks.

### 3.6 The history pilot limits extension beyond the tested geography task

Report 4/4 literal checks, 7/8 documentary-history checks, and 4/8 spaceflight checks: 15/20 against the fixed 20/20 requirement. No evaluation graphs were requested, so no historical graph-overlap effect was measured. Preserve the count table and the order/mapping-sensitive behavioral example without making a history-knowledge or causal-mechanism claim.

This limits generalization; it neither refutes the completed geography comparison nor extends it to history. No further collection is part of this revision.

## 4 Discussion

Synthesize the evidence in the same order: original association, stronger answer controls, selected errors. Distinguish observed next-token behavior from properties of the model-plus-exporter and overlap measurement.

Explain what checks narrow and what they do not identify. Equal counts and saved-graph filters do not demonstrate a distributed causal circuit. The capital-name source-location pattern is an exploratory hypothesis about selecting the intended country; the A/B pattern differs, and position versus negation remains unresolved.

Keep scope explicit: three models overall, one model in the stronger controls, six country pairs in the matched-choice study, one pair in the selected-error diagnostic, incomplete original collection, failed historical extension, and next-token outcomes under one hosted setup. Stronger causal or generalization claims would require different evidence; those studies are not implied to have been performed.

## 5 Conclusion

End with the measurement lesson: shared graph features are associated with factual prompts in these samples, but the stronger comparisons show answer dependence and same-answer resemblance in selected errors. Similarity alone cannot establish correct factual processing or a representation independent of the answer.

## Supporting analyses and availability

- **A1:** next-token matching, incomplete answers, and detailed crossed-output support.
- **A2:** ambiguous identifiers, reconstruction-error contributions, and clean-export sensitivity.
- **A3:** format-dependent source-location observations, missing correct logits, and unresolved position/negation alternatives.

The availability statement identifies the public curated review package and excludes raw exports, tokenizer/model files, credentials, and downloaded reference PDFs. The historical 82-test reproduction was a same-machine check, not independent review or a fresh hosted run.

## Figures and source maintenance

Figure numbering is unchanged: 1 design, 2 original association, 3 fact/wording, 4 made-up names, 5 answer controls, 6 selected errors, plus S1–S6. Figure 1 option C remains a labeled alternative pending final author selection. The manuscript uses the current plain-language captions and figure package; no plotted values change.

The editable source is `docs/papers/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md`. Rebuild the portable folder with `scripts/build_paper_share_package.py`; this reconciles captions, checks links, records hashes, and creates a dated ZIP. The review copy is `paper_share/manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md`. Earlier ZIPs, compiled PDFs, raw data, and frozen analyses remain unchanged.

Scientific and reference review, author approval, redistribution permissions for excluded data, and venue formatting remain human handoff items.
