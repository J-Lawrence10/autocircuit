# Paper outline and integrated argument

Updated 28 October 2026. This outline follows the working manuscript, **What Sparse Attribution-Graph Feature Overlap Preserves Across Prompt Changes**. This is an editorial revision: experiments, inclusion rules, estimates, and scientific boundaries are unchanged. The selected failures support the paper's measurement argument rather than forming a separate mechanism paper.

**Editorial principle:** Build the reader's mental picture before introducing detail. Explain why each comparison is needed, what it reveals, and how that result motivates the next question. This applies Joseph's October 27 grant-writing note; it is writing guidance, not scientific evidence. State measured findings directly, keep claim-specific qualifications beside them, and consolidate general limitations in the Discussion.

## Research question and central conclusion

**Question:** Do similar attribution graphs reflect the fact being asked about—or the answer the model produces?

These are not mutually exclusive explanations. The experiments ask whether shared facts remain associated with feature overlap when wording and answer labels vary.

**Conclusion:** Reworded questions about the same fact share more features in all three analyzed model samples. In the stronger Qwen3-4B comparison, the same-country overlap difference is larger when the answer letter stays the same: 0.0628 versus -0.0022 when it changes. All eight selected error comparisons also favor a correct prediction giving the same answer over a correct prediction for the intended country. Together, these results identify an answer-associated pattern in feature overlap, including in selected errors. The practical implication is to interpret overlap jointly with the prompt comparison and predicted answer, rather than as a standalone marker of correct factual processing.

## Logical sequence

1. **Make the comparison tangible:** reworded France-capital questions share a requested fact, country name, and expected answer. Explain what shared graph features measure.
2. **Establish the observation:** same-fact rewordings have higher mean feature overlap in the original three-model samples.
3. **Identify the unresolved relationship:** those comparisons also share words and answers, and the available original controls cannot separate them.
4. **Make a more discriminating comparison:** preserve word inventories while varying the queried country and A/B answer. The same-country overlap advantage is larger when the answer letter stays the same.
5. **Test the interpretation in errors:** selected wrong-answer graphs share more features with correct predictions giving the same answer than with correct predictions for the intended country.
6. **Establish what carries through and where evidence stops:** report the count and graph-location sensitivities, then the failed history pilot and scope of the completed comparisons.

The presentation follows this reasoning sequence, while Methods retains the actual study chronology and the distinction between rules fixed before collection and analyses designed after earlier outcomes.

## 1 Introduction

Begin with two differently worded France-capital questions. Both request the same fact and expect Paris, so shared features have several possible relationships to the prompts. Define feature overlap as shared features divided by all distinct features across the two graphs. This gives the reader a concrete measurement before the research question and technical details.

State the question, then preview the original three-model comparison, the Qwen3-4B answer-control experiment, and the selected-error comparison as responses to successive ambiguities. State the positive empirical contribution: the observed same-fact association, the larger difference with the same answer letter, and same-answer resemblance in selected errors. Distinguish feature composition from connections or causal pathways once; position the study as an evaluation of graph measurements, not a validated traceback tool or a claim to have discovered prompt sensitivity.

## 2 Methods

Figure 1 introduces the study design before the cohort and measurement details.

- **2.1 Cohorts and coverage:** distinguish graph collection from question inclusion; retain all three models, two families, uneven subject coverage, and the incomplete original Qwen3-4B extension.
- **2.2 Measurement:** define Jaccard overlap and same-fact minus average other-fact overlap. Explain that repeated occurrences of a feature at different token positions count once. State the four required prompt/control roles, next-token matching rule, and within-subject comparison requirements. Distinguish questions from graph pairs and repeated facts across models.
- **2.3 Original controls:** explain fact-by-wording and invented name comparisons using concrete prompt relationships.
- **2.4 Exploratory checks:** feature counts, word-matching support, expected answers, tokenization, and reconstruction of archived outcomes.
- **2.5 Matched-choice follow-up:** six Qwen3-4B country pairs, eight prompts per pair, identical word/token inventories within pairs, and variation of query, answer mapping, and wording. The average of the same-letter and changed-letter fact differences remains the prespecified primary outcome. Explain the conditional correspondence test as a comparison with reassigned fact correspondence within answer-label groups; the 4,096 configurations do not increase the number of independent country pairs or remove prompt-order differences.
- **2.6 Position pilot and selected errors:** distinguish the failed 16-item pilot from the separate 20-preview diagnostic and its 16 graph prompts. State the deliberate selection of four France/Germany cases, two formats, and reused controls.
- **2.7 Later audit and history pilot:** distinguish the exploratory direct difference test from the prespecified average and its conditional correspondence test. The later sign-flip test uses six country-pair differences and assumes independent blocks and symmetric differences under the null. Explain saved-graph filters as checks of where the measured association remains, not interventions. Retain the final 20-check history gate and its planned, uncollected evaluation cohort.

Protocols were frozen locally, not publicly preregistered. Earlier failed pilots remain reported; follow-ups do not replace original observations or alter original eligibility.

## 3 Results

### 3.1 Reworded questions about the same fact share more features

Figure 2 establishes the association: means 0.170, 0.085, and 0.162 for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B, with 8, 5, and 10 included questions. Retain the archived intervals and tests. These are not 23 independent facts, and unequal subjects prevent a model ranking.

**Next question:** Is the overlap specifically associated with the requested fact, or with the words and expected answer that travel with it?

### 3.2 Same-fact questions share words and expected answers

Begin with the reason for the check: to interpret the original association, we need comparisons that separate a shared fact from shared words and expected answers. No included question has an other-fact comparator meeting the declared word-matching rules: 0/8 Gemma, 0/5 Qwen3-1.7B, and 0/10 Qwen3-4B. All 86 directed other-fact comparisons differ in expected answer, whereas same-fact rewordings share it. These data identify the missing comparison; they do not show that words or answers explain the entire association. Supporting analysis A4 contains Figure S4.

Figures 3 and 4 describe the fact-by-wording and invented name controls. Their ordering varies across model pipelines and subjects. Only Qwen3-4B geography passes the strict expected-token rule in all nine crossed questions; its fact/wording differences are approximately 0.101/0.106. Do not infer equivalence, universal wording dominance, or model superiority. Supporting analysis A1 retains detailed output counts.

**Next question:** Does the association remain when available words are matched and the answer letter changes?

### 3.3 Same-fact overlap is higher when the answer letter stays the same

Explain the four conditions before the estimates. All 48 Qwen3-4B decisions are correct, with six country pairs supplying the analysis units. Figure 5 presents:

| Prompt relationship | Same answer letter | Different answer letter |
|---|---:|---:|
| Same queried country | 0.800 | 0.485 |
| Different queried countries | 0.738 | 0.487 |

These are rounded mean Jaccard scores, not accuracy rates. Within the two columns, same-country minus different-country overlap is 0.0628 and -0.0022. Their average, 0.0303, remains the prespecified primary outcome. Preserve its interval and conditional correspondence test; do not promote the later exploratory component comparison to a prespecified endpoint.

The descriptive answer-letter difference is 0.2827. It is not a fraction of reasoning or variance explained. The added exploratory paired comparison is 0.0650, with Student-t 95% interval 0.0553–0.0746 and two-sided sign-flip p=0.03125 under the stated six-block assumptions. A near-zero changed-letter estimate does not establish equivalence or absent factual knowledge. The positive difference persists under the specified graph-location filters (Figure S6, Supporting analysis A4). Word order, country roles, and output-conditioned graph construction remain relevant to interpretation; the result is an answer-associated pattern, not an isolated causal effect of an answer letter.

**Next question:** If resemblance is associated with the produced answer, can an incorrect response resemble a correct one?

### 3.4 Error graphs show greater overlap with answer-matched controls

Connect explicitly to the preceding study: the matched-choice comparison used correct predictions, so the next question concerns an incorrect prediction. Use France–Berlin to show the three graphs: a question identifying France by its list position predicts Berlin; naming France predicts Paris; naming Germany predicts Berlin. The error graph shares more features with the correct Germany–Berlin graph.

Explain why these cases were examined: the separate position pilot passed only 8/16 checks and stopped before its planned evaluation graphs. The subsequent diagnostic passed all four literal/replay checks. Its deliberately selected errors are not a population sample.

Figure 6 reports 16 clean graphs, eight reproduced errors, eight correct named-country controls, and eight comparisons favoring the same-output control. Mean differences are 0.1983 for A/B responses and 0.2649 for capital names; equal-feature-count values are 0.1851 and 0.2361. State the observation first: the same-answer resemblance persists across both formats and the specified sensitivities. The cases share one country pair and overlapping controls, so they supply dependent descriptive comparisons rather than an error-frequency estimate. Position matching and negation errors remain unresolved. Supporting analysis A3 retains source-location observations and omitted-logit qualifications; A4 contains the graph-location figure.

### 3.5 Greater feature sharing between same-fact questions

Report the original feature-count check after the main argument. Positive averages survive equalizing counts: 0.149, 0.081, and 0.126 at K, and 0.058, 0.032, and 0.051 at K/2 for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B. Seven of eight Gemma questions remain positive; the tungsten question reverses. This supports persistence of the average association under count matching without removing differences in words, answers, or retained feature identities. Put the historical regression-intercept correction and Figure S3 in Supporting analysis A4. Cite A1–A2 for output and export checks.

### 3.6 The history pilot yields 15 of 20 correct predictions

Report 4/4 literal checks, 7/8 documentary-history checks, and 4/8 spaceflight checks: 15/20 against the fixed 20/20 requirement. No evaluation graphs were requested, so no historical graph-overlap effect was measured. Preserve the count table and the order/mapping-sensitive behavioral example without making a history-knowledge or causal-mechanism claim.

This limits generalization; it neither refutes the completed geography comparison nor extends it to history. No further collection is part of this revision.

## 4 Discussion

### 4.1 What the comparisons establish

Synthesize the positive evidence in the same order: same-fact association, larger same-country difference with the same answer letter, and same-answer resemblance in selected errors. Explain the practical consequence: interpreting feature overlap requires specifying what the two prompts and predictions share. Count matching and saved-graph filters show where the observations persist. The work establishes an empirical relationship in these comparisons rather than a causal account of factual processing.

The capital-name source-location pattern can be presented as an exploratory clue about selecting the intended country. The A/B pattern differs, and position versus negation remains unresolved. Keep this subordinate to the feature-overlap argument, rather than introducing a competing mechanism story.

### 4.2 Scope and remaining questions

Keep scope explicit: three models overall, one model in the stronger controls, six country pairs in the matched-choice study, one pair in the selected-error diagnostic, incomplete original collection, failed historical extension, and next-token outcomes under one hosted setup. Stronger causal or generalization claims would require different evidence; those studies are not implied to have been performed.

Consolidate remaining uncertainty here: prompt order and entity roles are not fully separated; decomposition, pruning, and output-conditioned graph construction may contribute; selected errors do not establish error frequency or mechanism. This section should bound the findings, not repeatedly negate them. Independent scientific review and broader reproduction remain handoff tasks, not work claimed to be complete.

## 5 Conclusion

End with the connected empirical picture: same-fact questions share more features in the original samples; the stronger Qwen3-4B comparison has a larger advantage with the same answer letter; selected error graphs share more features with correct predictions giving the same answer. These observations establish an answer-associated pattern in the measured overlap. Conclude that overlap should be interpreted with the prompt comparison and predicted answer, rather than used alone to certify correct factual processing.

## Supporting analyses and availability

- **A1:** next-token matching, incomplete answers, and detailed crossed-output support.
- **A2:** ambiguous identifiers, reconstruction-error contributions, and clean-export sensitivity.
- **A3:** format-dependent source-location observations, missing correct logits, and unresolved position/negation alternatives.
- **A4 Comparison and sensitivity figures:** Figures S4, S6, and S3, with their full captions, plus the historical centered-regression-intercept correction. Main Results retain the findings and point here for the detailed comparisons.

The availability statement identifies the public curated review package and excludes raw exports, tokenizer/model files, credentials, and downloaded reference PDFs. The historical 82-test reproduction was a same-machine check, not independent review or a fresh hosted run.

## Figures and source maintenance

Figure numbering is unchanged: 1 design, 2 original association, 3 fact/wording, 4 invented names, 5 answer controls, 6 selected errors, plus S1–S6. Figure 1 option C remains a labeled alternative pending final author selection. The manuscript uses the current plain-language captions and figure package; no plotted values change.

The editable source is `docs/papers/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md`. Rebuild the portable folder with `scripts/build_paper_share_package.py`; this reconciles captions, checks links, records hashes, and creates a dated ZIP. The review copy is `paper_share/manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md`. Earlier ZIPs, compiled PDFs, raw data, and frozen analyses remain unchanged.

Scientific and reference review, author approval, redistribution permissions for excluded data, and venue formatting remain human handoff items.
