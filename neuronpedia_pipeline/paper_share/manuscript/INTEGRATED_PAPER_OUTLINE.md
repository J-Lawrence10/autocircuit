# Paper outline and integrated argument

Updated locally 11 November 2026. This outline follows the working manuscript, **What Sparse Attribution-Graph Feature Overlap Preserves Across Prompt Changes**. The main comparison uses one final sample per model: eight Gemma-2-2B, ten Qwen3-1.7B, and twelve Qwen3-4B evaluation facts. The final scoring accepts valid registered spellings; earlier scoring decisions and subset analyses are retained in the audit archive, not displayed as additional evidence. The selected failures support the paper's measurement argument rather than forming a separate mechanism paper.

**Editorial principle:** Build the reader's mental picture before introducing detail. Explain why each comparison is needed, what it reveals, and how that result motivates the next question. This applies Joseph's October 27 grant-writing note; it is writing guidance, not scientific evidence. State measured findings directly, keep claim-specific qualifications beside them, and consolidate general limitations in the Discussion.

**Style:** Use American English spelling and no em dashes. Introduce terms before using them in comparisons. Preserve numerical ranges and the wording of frozen protocols and quoted source titles.

## Research question and central conclusion

**Question:** Do similar attribution graphs reflect the fact being asked about, or the answer the model produces?

These are not mutually exclusive explanations. The experiments ask whether shared facts remain associated with feature overlap when wording and answer labels vary.

**Conclusion:** Reworded questions about the same fact share more features in all three analyzed model samples. In the stronger Qwen3-4B comparison, the same-country overlap difference is larger when the answer letter stays the same: 0.0628 versus -0.0022 when it changes. All eight selected error comparisons also favor a correct prediction giving the same answer over a correct prediction for the intended country. Together, these results identify an answer-associated pattern in feature overlap, including in selected errors. The practical implication is to interpret overlap jointly with the prompt comparison and predicted answer, rather than as a standalone marker of correct factual processing.

## Logical sequence

1. **Establish the broader purpose:** connect correct answers to the question of how internal computations produce them. Introduce mechanistic interpretability and relevant prior research.
2. **Make the measurement question tangible:** introduce attribution graphs and features, then use France/Paris to distinguish a shared fact, shared words, and a shared answer.
3. **State the original hypothesis:** within a model, reworded questions about the same fact were predicted to share more features than questions about different facts. Keep this distinct from the answer-related interpretation developed through later analyses.
4. **Establish the observation:** same-fact rewordings have higher mean feature overlap in the three analyzed model samples, but the question/control comparisons do not separate shared words and expected answers.
5. **Make a more discriminating comparison:** preserve word inventories while varying the queried country and A/B answer. The same-country overlap advantage is larger when the answer letter stays the same.
6. **Test the interpretation in errors:** selected wrong-answer graphs share more features with correct predictions giving the same answer than with correct predictions for the intended country.
7. **Test the distinction in history:** after the count and graph-location sensitivities, show how graphs can remain similar when the predicted letter stays the same but the selected year changes. Figure 7 uses 16 graphs from two event pairs, including incorrect answers. Retain the original stopped study's accounting in Supporting analysis A7.

The presentation follows this reasoning sequence. Methods leads with collected totals and analysis rules; protocol and provenance records retain the distinction between rules fixed before collection and analyses designed after earlier outcomes.

## 1 Introduction

The six paragraphs now move from broad background to the specific comparison and contribution:

1. **Broader problem:** a correct answer does not explain the internal computations that produced it. Define mechanistic interpretability and introduce the question of what remains similar across rewordings.
2. **Available tools and prior research:** retain the author-approved attribution-graph and feature definitions. Connect prior prompt-specific circuit work and multiple-choice option sensitivity to comparing features across questions and predictions.
3. **Interpretation problem:** use France/Paris to show why a shared fact, shared words, and a shared answer can coincide. Motivate changing the required output while retaining the fact.
4. **Original hypothesis and measurement:** state the initial within-model same-fact hypothesis, name all three models, and introduce Jaccard overlap in one sentence. Do not present the later answer-letter interpretation as the original prespecified hypothesis.
5. **Approach:** briefly explain the Qwen3-4B multiple-choice controls and selected incorrect-prediction comparisons. State that a correct prediction giving the same answer concerns another country, so correctness is evaluated against each question.
6. **Contribution and transition:** retain one sentence stating that feature overlap was associated with the question relationship and predicted answer, followed by a transition into the model samples, question designs, and graph comparisons in Methods. The fuller findings remain in the Abstract and Results, with interpretation and causal boundaries in the Discussion.

The full Jaccard definition and range are preserved in Methods 2.2. The full A/B manipulation and France/Paris illustration are preserved in Methods 2.5. The observed France/Berlin error and both correct named-country controls are preserved in Methods 2.6, alongside the actual pilot chronology, selection details, and related position-retrieval literature. The author's two-sentence interpretation of the near-zero changed-letter contrast is preserved verbatim in Results 3.3. The abstract is unchanged and remains for later revision. Paragraph-by-paragraph introduction review resumes with paragraph 1.

## 2 Methods

Section 2.2 defines complete accepted answers, including Maria and María for the flagship question. Briefly disclose that the scoring correction was identified during the audit and applied across all 170 available factual outputs, changing one classification. Use corrected results throughout; retain the earlier decisions in provenance, not as a second sample. Prompts, graphs, four-role requirements, and comparison definitions stay fixed.

The Methods overview introduces the three Figure 1 comparisons in order. Explain the A/B manipulation as swapping the capitals assigned to the letters before stating the feature-overlap comparison. Define an error graph as an attribution graph for an incorrect prediction before using the shorthand. Its two correct-prediction comparators concern the intended country and the same answer in a context where that answer is correct. The three analyses retain separate question sets and separate evaluation. Figure 1 follows this overview before the model and measurement details.

- **2.1 Models, questions, and collected data:** lead with totals for the question/control and fact/wording designs: Gemma 120+27 graphs, Qwen3-1.7B 91 graphs, and Qwen3-4B 120+27 graphs, totaling 385. Evaluation counts are 8, 10, and 12, with subjects identified. Qwen3-1.7B contains 40 chemistry, 40 geography, and 11 history graphs; 29 input-length rejections leave no complete history control sets and are not incorrect answers. Qwen3-4B includes five chemistry, five geography, and two history evaluation facts. Its matched-choice, selected-error, and historical-date comparisons contain 48, 16, and 16 graphs, respectively. Explain the four question versions and split before inclusion. Do not present collection history as additional samples.
- **2.2 Measurement:** define Jaccard overlap and same-fact minus average other-fact overlap. Explain that repeated occurrences of a feature at different token positions count once. State the four required prompt/control roles, next-token matching rule, and within-subject comparison requirements. Distinguish questions from graph pairs and repeated facts across models.
- **Methods reference diagram (Figure S8):** show the primary question/control workflow from four prompt roles through hosted graphs, inclusion, unique feature sets, Jaccard comparisons, and fact-level summaries. Use exact development prompts and explicitly illustrative feature sets and arithmetic. Keep invented name comparisons separate from the all-other-fact baseline; the other experimental designs retain their own rules.
- **2.3 Original controls:** explain fact-by-wording and invented name comparisons using concrete prompt relationships.
- **2.4 Exploratory checks:** feature counts, word-matching support, expected answers, tokenization, and reconstruction of archived outcomes.
- **2.5 Matched-choice follow-up:** six Qwen3-4B country pairs, eight prompts per pair, identical word/token inventories within pairs, and variation of query, answer mapping, and wording. The average of the same-letter and changed-letter fact differences remains the prespecified primary outcome. Explain the conditional correspondence test as a comparison with reassigned fact correspondence within answer-label groups; the 4,096 configurations do not increase the number of independent country pairs or remove prompt-order differences.
- **2.6 Position pilot and selected errors:** distinguish the failed 16-item pilot from the separate 20-preview diagnostic and its 16 graph prompts. State the deliberate selection of four France/Germany cases, two formats, and reused controls.
- **2.7 Later audit and historical-date comparisons:** distinguish the exploratory direct difference test from the prespecified average and its conditional correspondence test. The later sign-flip test uses six country-pair differences and assumes independent blocks and symmetric differences under the null. Explain saved-graph filters as checks of where the measured association remains, not interventions. Describe the additional 16-graph history analysis, including incorrect predictions, both event pairs, date-mapping and order changes, and the distinction between required and predicted letters. Report dependent comparisons descriptively. Retain the original 20-check gate and uncollected 160-graph cohort in A7.
- **2.8 Qwen3-1.7B analysis and verification:** use the combined 91-graph dataset and its ten evaluation facts throughout. Describe hash and representation checks, reconstruction of archived contrasts, recorded 0.95/0.99 output-coverage settings, unchanged inclusion, 10,000 fact-bootstrap resamples, exact within-subject permutations, the defined 15-test secondary Holm family, both invented name controls, and 200 equal-count subsamples. Leave-one-fact-out summaries keep comparator pools fixed. Distinguish audit denominators: 91 graph files, ten evaluation facts, and 50 available factual prompts including partial history. Retain exploratory status and all exclusions; archived subset estimates are not independent extra evidence. The mechanism tests in Section 4.3 were not performed.

Protocols were frozen locally, not publicly preregistered. Earlier failed pilots and their gates remain in the audit record. Corrected scoring changes answer classification, not the observations or the recorded outcomes of those gates.

## 3 Results

### 3.1 Reworded questions about the same fact share more features

Figure 2 establishes the association: means 0.170, 0.0894, and 0.218 for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B, with 8, 10, and 12 included questions. Use the saved intervals and tests for these final samples. These are 30 model-specific observations, not 30 independent unique facts; unequal subjects prevent a model ranking.

Then describe Qwen3-4B's history results: Columbus and Franz Ferdinand have differences of 0.601 and 0.395, with mean 0.498. Figure S9 details their raw comparisons and equal-count checks. The two facts use each other as comparators; this does not constitute independent history replication. Figure 4 uses ten Qwen3-4B facts because all four history invented name controls predict commas and fail output-type matching. Explain the different denominator once, without presenting superseded results.

Qwen3-1.7B has five chemistry and five geography evaluation facts, all positive, with subject means 0.0854 and 0.0935. Its combined mean is 0.0894 [0.0820, 0.0976]. Show this model once alongside the other two, with subject estimates in the subject panel and collection accounting in Figure S7. No history fact has a complete four-version set. Do not retain the five-fact subset as an additional model-level estimate.

**Next question:** Is the overlap specifically associated with the requested fact, or with the words and expected answer that travel with it?

### 3.2 Same-fact questions share words and expected answers

Begin with the reason for the check: to interpret the same-fact association, we need comparisons that separate a shared fact from shared words and expected answers. No included question has an other-fact comparator meeting the declared word-matching rules: 0/8 Gemma, 0/10 Qwen3-1.7B, and 0/12 Qwen3-4B. All 108 directed other-fact comparisons differ in expected answer, whereas all 30 model-specific same-fact pairs share it. These data identify the missing comparison; they do not show that words or answers explain the entire association. Supporting analysis A4 contains Figure S4.

Figures 3 and 4 describe the fact-by-wording and invented name controls. Their ordering varies across model pipelines and subjects. Only Qwen3-4B geography passes the strict expected-token rule in all nine crossed questions; its fact/wording differences are approximately 0.101/0.106. Do not infer equivalence, universal wording dominance, or model superiority. Supporting analysis A1 retains detailed output counts.

For Qwen3-1.7B, eight of ten evaluation questions favor the same-pattern invented name control over the factual rewording, while all ten favor the factual rewording over the reworded control. The plotted output-type-matched means are -0.0109 (n=9, seven favoring the control) and +0.1059 (n=10), alongside the corresponding Gemma and Qwen3-4B results in Figure 4. This supports the need for the next comparison, not a claim that geography data isolate factual meaning.

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

Report the feature-count check after the main argument. Positive averages survive equalizing counts: 0.149, 0.084, and 0.181 at K, and 0.058, 0.033, and 0.072 at K/2 for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B. Seven of eight Gemma questions remain positive; the tungsten question reverses. All ten Qwen3-1.7B and twelve Qwen3-4B fact averages remain positive. This supports persistence of the average association under count matching without removing differences in words, answers, or retained feature identities. Put the historical regression-intercept correction and Figure S3 in Supporting analysis A4. Cite A1–A2 for output and export checks.

### 3.6 History graphs can remain similar when the selected year changes

Figure 7a starts with exact Declaration of Independence prompts: the same A prediction selects different years with overlap 0.795, whereas A/B predictions retain 1776 with overlap 0.512. Across all eight date-mapping comparisons, five same-letter pairs select different years and have overlaps of 0.795–0.911; the three changed-letter pairs retain the same correct year and have overlaps of 0.512–0.532 (7b). Across eight order comparisons, same-letter overlaps are 0.766–0.808 and changed-letter overlaps are 0.527–0.602 (7c). All 16 graphs, including 11 correct and five incorrect predictions, remain included.

These are descriptive comparisons from two event pairs, not a completion of the original 20-pair history evaluation. A7 retains the failed 15/20 preliminary gate, all exclusions, the required-letter contrasts that do not uniformly reproduce geography, and the separate predicted-letter summaries. Qwen3-1.7B history coverage remains incomplete; the shorter-prompt feasibility draft is deferred and unrun. No further collection is authorized.

## 4 Discussion

### 4.1 What the comparisons establish

Synthesize the positive evidence in the same order: same-fact association, larger same-country difference with the same answer letter, and same-answer resemblance in selected errors. Explain the practical consequence: interpreting feature overlap requires specifying what the two prompts and predictions share. Count matching and saved-graph filters show where the observations persist. The work establishes an empirical relationship in these comparisons rather than a causal account of factual processing.

The capital-name source-location pattern can be presented as an exploratory clue about selecting the intended country. The A/B pattern differs, and position versus negation remains unresolved. Keep this subordinate to the feature-overlap argument, rather than introducing a competing mechanism story.

### 4.2 Scope and remaining questions

Keep scope explicit: three models overall, one model in the stronger controls, six country pairs in the matched-choice study, one pair in the selected-error diagnostic, two event pairs in the historical-date analysis, unequal subject coverage, the uncollected 20-pair history evaluation, and next-token outcomes under one hosted setup. Qwen3-4B's factual-completion history comparison contains two flagship/Franz Ferdinand facts that share comparison graphs. This is distinct from the historical-date A/B design within the same study. Stronger causal or generalization claims would require different evidence; those studies are not implied to have been performed.

Consolidate remaining uncertainty here: prompt order and entity roles are not fully separated; decomposition, pruning, and output-conditioned graph construction may contribute; selected errors do not establish error frequency or mechanism. This section should bound the findings, not repeatedly negate them. Independent scientific review and broader reproduction remain handoff tasks, not work claimed to be complete.

### 4.3 Future research: separating computation from graph selection

Pose the source of answer-associated overlap as an open mechanistic question. Shared answer-producing activity and answer-dependent selection of features into the exported graph can both contribute; the present comparisons do not separate them. Explain why count matching and saved-graph filters do not undo selection. Keep decomposition and pruning as possible contributors, not proven artifacts.

Propose two complementary future comparisons: construct A-targeted and B-targeted graphs from the same recorded model run without changing the prompt or activity, and repeat the country/answer comparisons using feature activity recorded before answer-dependent selection. The first establishes sensitivity to the attribution target; it does not alone quantify the source of the cross-question association. The second tests whether answer-associated similarity is present independently of graph selection. Saved retained-node exports and incomplete alternative-logit coverage cannot provide this full comparison.

Describe causal follow-up as a later step: test candidate answer-production versus fact-related features across answer mappings, using questions not used for feature selection, unchanged-model and matched-random controls, and multiple intervention strengths. These are proposed studies, not completed experiments or authorization to reopen collection. The current paper retains its measured answer-associated pattern without claiming a resolved mechanism.

## 5 Conclusion

End with the connected empirical picture: same-fact questions share more features in the three analyzed samples; the stronger Qwen3-4B comparison has a larger advantage with the same answer letter; selected error graphs share more features with correct predictions giving the same answer. These observations establish an answer-associated pattern in the measured overlap. Conclude that overlap should be interpreted with the prompt comparison and predicted answer, rather than used alone to certify correct factual processing.

## Supporting analyses and availability

- **A1:** next-token matching, incomplete answers, accepted spellings, and detailed crossed-output support. Qwen3-1.7B has 42 complete accepted answers, four compatible beginnings, and four other first tokens among 50 factual graphs. Qwen3-4B has 50 complete accepted answers, five compatible beginnings, and five other tokens among 60. Figure S5 distinguishes complete answers from partial or different first tokens. Figure S9 details the two history facts already included in Figure 2 and their equal-count checks; accompanying results and tables retain both invented name controls. Do not show a second pre-correction cohort.
- **A2:** ambiguous identifiers, reconstruction-error contributions, and clean-export sensitivity. Qwen3-1.7B has 0/91 ID-conflicted exports and a median approximation-error influence fraction of 6.06%; this is not the percentage of wrong model answers.
- **A3:** format-dependent source-location observations, missing correct logits, and unresolved position/negation alternatives.
- **A4 Comparison and sensitivity figures:** Figures S4, S6, and S3, with their full captions, plus the historical centered-regression-intercept correction. Main Results retain the findings and point here for the detailed comparisons.
- **A5 Qwen3-1.7B subject results and sensitivity analyses:** report current chemistry and geography means, the ten-fact combined result, and the 29 history input-length rejections separately from model errors. Figure S7 separates total graph availability from included evaluation facts without old/new collection bars. Keep the four-role, next-token, and within-subject comparison rules, all exclusions, and the current control sensitivities. The retrospective display audit finds 0/10 qualifying word-matched comparisons under all three rules, with matching expected answers in 10/10 same-fact pairs and 0/40 other-fact pairs. This leaves an interpretation gap rather than producing a measured zero semantic effect.

- **A6 Feature-overlap analysis workflow:** Figure S8 supplies the methods reference diagram cited in Section 2.2. It explains the measurement and does not add observations or empirical results.

The availability statement identifies the public curated review package and excludes raw exports, tokenizer/model files, credentials, and downloaded reference PDFs. The historical 82-test reproduction was a same-machine check, not independent review or a fresh hosted run.

## Figures and source maintenance

Existing figure numbering is retained: 1 design, 2 same-fact association, 3 fact/wording, 4 invented names, 5 answer controls, 6 selected errors, and 7 historical-date comparisons, plus S1–S9. Figure S8 explains the final accepted-answer workflow. Figure S9 details the Qwen3-4B history facts included in the main comparison. All affected panels and tables use the corrected twelve-fact Qwen3-4B sample; Figure 4 retains its ten-fact output-type-matched subset. The paper has three models, not duplicated old and new samples. Figure 3 and the Qwen3-4B-only Figures 5, 6, 7, and S6 retain their design-specific data. S7 reports Qwen3-1.7B collection and inclusion accounting. The claims map follows the same final totals. Earlier numerical estimates, source files, figures, and review packages remain archived. Figure 1 option C remains a labeled historical layout alternative, not the current data summary.

The editable source is `docs/papers/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md`. Rebuild the portable folder with `scripts/build_paper_share_package.py`; this reconciles captions, checks links, records hashes, and creates a dated ZIP. The review copy is `paper_share/manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md`. Earlier ZIPs, compiled PDFs, raw data, and frozen analyses remain unchanged.

Scientific and reference review, author approval, redistribution permissions for excluded data, and venue formatting remain human handoff items.
