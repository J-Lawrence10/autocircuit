# Paper outline and integrated argument

Review edition updated 12 November 2026. This outline follows the working manuscript, **Feature sharing in attribution graphs tracks predicted responses**. The main comparison uses one final sample per model: eight Gemma-2-2B, ten Qwen3-1.7B, and twelve Qwen3-4B evaluation facts. The final scoring accepts valid registered spellings; earlier scoring decisions and subset analyses are retained in the audit archive, not displayed as additional evidence. The selected failures support the paper's measurement argument rather than forming a separate mechanism paper.

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
7. **Test the distinction in history:** after the count and graph-location sensitivities, show how graphs can remain similar when the predicted letter stays the same but the selected year changes. Figure 6 uses 16 graphs from two event pairs, including incorrect answers. Retain the original stopped study's accounting in Supporting analysis A7.

The presentation follows this reasoning sequence. Methods leads with collected totals and analysis rules; protocol and provenance records retain the distinction between rules fixed before collection and analyses designed after earlier outcomes.

## 1 Introduction

The Introduction moves from broad background to the specific comparison and contribution:

1. **Broader problem:** a correct answer does not explain the internal computations that produced it. Define mechanistic interpretability and introduce the question of what remains similar across rewordings.
2. **Available tools and prior research:** Explicitly acknowledge output-dependent graph pruning as an established construction step, not a discovery of this study. retain the author-approved attribution-graph and feature definitions. Connect prior prompt-specific circuit work and multiple-choice option sensitivity to comparing features across questions and predictions.
3. **Interpretation problem:** Ask whether greater feature overlap still distinguishes same-fact questions when the predicted response changes. use France/Paris to show why a shared fact, shared words, and a shared answer can coincide. Motivate changing the required output while retaining the fact.
4. **Original hypothesis and measurement:** state the initial within-model same-fact hypothesis, name all three models, and introduce Jaccard overlap in one sentence. Do not present the later answer-letter interpretation as the original prespecified hypothesis.
5. **Approach:** briefly explain the Qwen3-4B multiple-choice controls and selected incorrect-prediction comparisons. State that a correct prediction giving the same answer concerns another country, so correctness is evaluated against each question.
6. **Contribution and transition:** retain one sentence stating that feature overlap was associated with the question relationship and predicted answer, followed by a transition into the model samples, question designs, and graph comparisons in Methods. The fuller findings remain in the Abstract and Results, with interpretation and causal boundaries in the Discussion.

The full Jaccard definition and range are preserved in Methods 2.2. The full A/B manipulation and France/Paris illustration are preserved in Methods 2.5. The observed France/Berlin error and both correct named-country controls are preserved in Methods 2.6, alongside the actual pilot chronology, selection details, and related position-retrieval literature. The author's two-sentence interpretation of the near-zero changed-letter contrast is preserved verbatim in Results 3.3. The Introduction review is complete. The approved Abstract is now added, ending with the scientific finding rather than the proposed final recommendation. It retains the primary estimate and uncertainty, conditional answer-letter contrasts, three-model scope, and selected error/history sample limits.

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

Then describe Qwen3-4B's history results: Columbus and Franz Ferdinand have differences of 0.601 and 0.395, with mean 0.498. Figure S9 details their raw comparisons and equal-count checks. The two facts use each other as comparators; this does not constitute independent history replication. Figure 3 uses ten Qwen3-4B facts because all four history invented name controls predict commas and fail output-type matching. Explain the different denominator once, without presenting superseded results.

Qwen3-1.7B has five chemistry and five geography evaluation facts, all positive, with subject means 0.0854 and 0.0935. Its combined mean is 0.0894 [0.0820, 0.0976]. Show this model once alongside the other two, with subject estimates in the subject panel and collection accounting in Figure S7. No history fact has a complete four-version set. Do not retain the five-fact subset as an additional model-level estimate.

**Next question:** Is the overlap specifically associated with the requested fact, or with the words and expected answer that travel with it?

### 3.2 Same-fact questions share words and expected answers

Begin with the reason for the check: to interpret the same-fact association, we need comparisons that separate a shared fact from shared words and expected answers. No included question has an other-fact comparator meeting the declared word-matching rules: 0/8 Gemma, 0/10 Qwen3-1.7B, and 0/12 Qwen3-4B. All 108 directed other-fact comparisons differ in expected answer, whereas all 30 model-specific same-fact pairs share it. These data identify the missing comparison; they do not show that words or answers explain the entire association. Supporting analysis A4 contains Figure S4.

Supplementary Figure S10 and Figure 3 describe the fact-by-wording and invented name controls. Their ordering varies across model pipelines and subjects. Only Qwen3-4B geography passes the strict expected-token rule in all nine crossed questions; its fact/wording differences are approximately 0.101/0.106. Do not infer equivalence, universal wording dominance, or model superiority. Supporting analysis A1 retains detailed output counts.

For Qwen3-1.7B, eight of ten evaluation questions favor the same-pattern invented name control over the factual rewording, while all ten favor the factual rewording over the reworded control. The plotted output-type-matched means are -0.0109 (n=9, seven favoring the control) and +0.1059 (n=10), alongside the corresponding Gemma and Qwen3-4B results in Figure 3. This supports the need for the next comparison, not a claim that geography data isolate factual meaning.

**Next question:** Does the association remain when available words are matched and the answer letter changes?

### 3.3 Same-fact overlap is higher when the answer letter stays the same

Explain the four conditions before the estimates. All 48 Qwen3-4B decisions are correct, with six country pairs supplying the analysis units. Figure 4 presents:

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

Figure 5 reports 16 clean graphs, eight reproduced errors, eight correct named-country controls, and eight comparisons favoring the same-output control. Mean differences are 0.1983 for A/B responses and 0.2649 for capital names; equal-feature-count values are 0.1851 and 0.2361. State the observation first: the same-answer resemblance persists across both formats and the specified sensitivities. The cases share one country pair and overlapping controls, so they supply dependent descriptive comparisons rather than an error-frequency estimate. Position matching and negation errors remain unresolved. Supporting analysis A3 retains source-location observations and omitted-logit qualifications; A4 contains the graph-location figure.

### 3.5 Greater same-fact feature sharing persists after matching feature counts

Report the feature-count check after the main argument. Positive averages survive equalizing counts: 0.149, 0.084, and 0.181 at K, and 0.058, 0.033, and 0.072 at K/2 for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B. Seven of eight Gemma questions remain positive; the tungsten question reverses. All ten Qwen3-1.7B and twelve Qwen3-4B fact averages remain positive. This supports persistence of the average association under count matching without removing differences in words, answers, or retained feature identities. Put the historical regression-intercept correction and Figure S3 in Supporting analysis A4. Cite A1–A2 for output and export checks.

### 3.6 History graphs can remain similar when the selected year changes

Figure 6a starts with exact Declaration of Independence prompts: the same A prediction selects different years with overlap 0.795, whereas A/B predictions retain 1776 with overlap 0.512. Across all eight date-mapping comparisons, five same-letter pairs select different years and have overlaps of 0.795–0.911; the three changed-letter pairs retain the same correct year and have overlaps of 0.512–0.532 (6b). Across eight order comparisons, same-letter overlaps are 0.766–0.808 and changed-letter overlaps are 0.527–0.602 (6c). All 16 graphs, including 11 correct and five incorrect predictions, remain included.

These are descriptive comparisons from two event pairs, not a completion of the original 20-pair history evaluation. A7 retains the failed 15/20 preliminary gate, all exclusions, the required-letter contrasts that do not uniformly reproduce geography, and the separate predicted-letter summaries. Qwen3-1.7B history coverage remains incomplete; the shorter-prompt feasibility draft is deferred and unrun. No further collection is authorized.

## 4 Discussion

### 4.1 What the comparisons establish

Synthesize the positive evidence in the same order: same-fact association, larger same-country difference with the same answer letter, and same-answer resemblance in selected errors. Explain the practical consequence: interpreting feature overlap requires specifying what the two prompts and predictions share. Count matching and saved-graph filters show where the observations persist. The work establishes an empirical relationship in these comparisons rather than a causal account of factual processing.

Discussion 4.1 now synthesizes the measured findings in two paragraphs; 4.2 interprets their consequence and 4.3 proposes tests of their source. Detailed source-location clues remain in the selected-error results and supporting analyses.

### 4.2 Graph similarity and factual correctness can diverge

Lead with the interpretation: feature overlap changed without a loss of factual accuracy in the answer-letter comparison, while selected errors and history comparisons separate similar graphs from correct factual answers. Connect this observation to what Jaccard overlap measures and why comparisons should consider the requested fact, predicted response, and correctness together. Retain the distinction between the three-model same-fact association and Qwen3-4B-only answer controls; selected dependent cases do not establish frequency across questions. End with the unresolved source of answer-associated overlap, motivating Section 4.3.

Use this interpretive structure throughout the Discussion: each paragraph should state a point, connect it to evidence, and explain its consequence. Keep detailed collection counts, next-token scoring, subject exclusions, statistical assumptions, and original pilot accounting in Methods and supporting analyses, where they remain documented. Preserve alternative error explanations in the selected-error results and supporting analysis A3. Independent scientific review and broader reproduction remain author handoff tasks, not manuscript claims of completed validation. Sections 4.2 and 4.3, the Conclusion, and the Abstract are approved. Next is a whole-paper consistency pass, followed by the remaining supporting-material and reference review.

### 4.3 Future research: separating model activity from graph construction

Connect each proposed test to the question it would resolve. First, hold the prompt, model activity, and graph settings fixed while explaining alternative A/B outputs from one recorded run. This tests sensitivity to the explained token, not by itself how much of the cross-question pattern comes from that choice. Second, repeat the same-fact and same-answer comparisons on activity before output-dependent feature selection, keeping feature definitions fixed and checking feature counts. The contrast asks whether similarity is already present in model activity or emerges or strengthens during graph construction. These possibilities can coexist; neither is an established causal explanation.

Then explain what interventions would add: test candidate feature roles across facts and answer mappings, distinguishing selective effects from general disruption. Preserve questions not used for feature selection, unchanged-model and random-feature controls matched in number, layer, and activation, and multiple intervention strengths. Saved retained-node exports and incomplete alternative-output coverage cannot provide these complete comparisons.

These are proposed studies, not completed experiments or authorization to reopen collection. The approved section moves from observing feature sharing to the tests needed to identify its source and functional role. The current paper retains its measured answer-associated pattern without claiming a resolved mechanism.

## 5 Conclusion

The approved concise conclusion connects the three-model same-fact association to the Qwen3-4B answer-letter, selected-error, and historical-date comparisons. Highlight that overlap decreased with a changed answer letter despite unchanged accuracy and could remain similar when the selected year changed. End with the practical implication: attribution-graph comparisons should distinguish the requested fact, the predicted response, and correctness when investigating factual processing. No new experiments or stronger causal claims are introduced.

## Supporting analyses and availability

- **A1:** next-token matching, incomplete answers, accepted spellings, and detailed crossed-output support. Qwen3-1.7B has 42 complete accepted answers, four compatible beginnings, and four other first tokens among 50 factual graphs. Qwen3-4B has 50 complete accepted answers, five compatible beginnings, and five other tokens among 60. Figure S5 distinguishes complete answers from partial or different first tokens. Figure S9 details the two history facts already included in Figure 2 and their equal-count checks; accompanying results and tables retain both invented name controls. Do not show a second pre-correction cohort.
- **A2:** distinguish graph-file identifier conflicts from activity not captured by the learned-feature approximation. Explain the per-graph absolute-influence ratio and retain all reported audit counts and medians; reconstruction error is not an incorrect answer and no reconstruction-error threshold excludes graphs. The main Gemma comparison uses eight evaluation facts; only the stricter conflict-free factual-graph check uses two facts (four factual-question graphs), a rule-derived subset rather than a chosen cutoff. Retain the error-inclusive and most-similar-other-fact checks, the smaller-subset limitation, and the boundary against architecture or accuracy rankings.
- **A3:** explain direct incoming connections and country-name input positions in the 16 selected Qwen3-4B graphs. Preserve the capital-name error ratios, correct-control reversal, and absence of a consistent A/B counterpart. Use the recorded France/Germany prompt to explain why answer-option position matching and mishandled negation predict the same incorrect answer. Distinguish the 23.1% direct-edge reconstruction-error share from A2's internal-node influence ratio; retain missing correct output nodes and the limits of interpreting feature locations.
- **A4 Checks on wording, feature counts, and graph locations:** Explain the fact/version comparison and its baseline, missing word-matched controls, equal-feature-count sampling and the tungsten reversal, and filtering saved graph positions/layers without intervening on the model. Preserve Figures S10, S4, S3, and S6 with their approved captions and the historical centered-regression-intercept correction. Main Results retain the findings and point here for the detailed comparisons.
- **A5 Qwen3-1.7B results in chemistry and geography:** distinguish 91 graphs, 19 included development/evaluation facts, and ten evaluation facts; report subject means, the complete sensitivity table, contrasting invented name controls, and feature-level versus coarse-structure results. Preserve the four-role, complete-next-token, and within-subject comparison rules, all exclusions, statistical assumptions, exploratory status, and A5.1 generation and verification details. The 29 unavailable history requests reflect the Qwen3-1.7B input limit, not incorrect answers; explicitly point to completed Qwen3-4B history analyses in Section 3.6 and A1/A7. Figure S7 separates graph availability from included facts. No qualifying word-matched comparisons exist under the three rules, and matching expected answers occur in 10/10 same-fact pairs versus 0/40 other-fact pairs; this remains missing matched-control support, not a measured zero effect.

- **A6 Feature-overlap analysis workflow:** Explain the inclusion checks, unique learned-feature sets, and same-fact minus average other-fact overlap within each model/subject/split, yielding one difference per fact. Invented name controls remain a separate comparison. Figure S8 supplies the methods reference diagram cited in Section 2.2; gold is the chemical element and zorium an invented name, while feature letters and scores are illustrative rather than additional results. Other experiments retain their own comparisons and inclusion rules.

- **A7 Historical-date comparisons:** Define required and predicted letters, retain all sixteen graphs and both event-pair summaries, and explain the cross-order comparison counts and reused graphs. Preserve all numerical tables and the distinction between required-letter sensitivity contrasts and predicted-letter groupings. Explain that positive subsampling summaries are averages, not a claim about every repetition. Retain the stopped 160-graph evaluation, preliminary 15/20 result against 20/20, minimum support requirements, and the completed analysis's timing and descriptive scope.

The availability statement identifies the public curated review package and excludes raw exports, tokenizer/model files, credentials, and downloaded reference PDFs. The historical 82-test reproduction was a same-machine check, not independent review or a fresh hosted run.

## Remaining final review

The main-text, title, Abstract, A1–A8 body (including A5.1), and all sixteen figure-legend reviews are complete. The approved legends describe panels, comparison definitions, visual encodings, sample units, and statistical summaries; figure titles, artwork, and data are unchanged. The approved text is integrated in the manuscript and sharing copies for the authorized GitHub and website release, whose exact contents are recorded by the package manifest and Git commit. A8 distinguishes public materials from the restricted author archive, historical reproduction from later scoped checks, and credentials from materials awaiting redistribution review. Remaining review covers references and citation support, author details, release permissions, and PI/coauthor scientific and statistical feedback; venue formatting follows the venue decision. These are review and release tasks, not authorization for new experiments.

## Figures and source maintenance

The current sequence is Figure 1: four-comparison design; Figure 2: same-fact association; Figure 3: invented name controls; Figure 4: answer-letter comparison; Figure 5: selected errors; Figure 6: historical dates. The descriptive question-version comparison moved to Supplement S10. Supplements S1–S9 retain their topics. All 16 figures are rebuilt from saved results at 180 mm width with text of at least 7 points. Figure 1 reads the final 8/10/12 counts from the source table. Figure 3 retains its ten-fact Qwen3-4B output-type-matched subset. Original measurement filenames remain stable; the figure guide maps them to current figures and includes the S6 source tables. The paper has three models, with each design retaining its own sample. Historical figures, scoring records, and review packages remain archived.

The editable source is `docs/papers/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md`. Rebuild figures with `scripts/build_reviewed_paper_figures.py`, then the portable folder with `scripts/build_paper_share_package.py`; this reconciles captions, checks links, records hashes, and creates a dated ZIP. The review copy is `paper_share/manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md`. Earlier ZIPs, compiled PDFs, raw data, and frozen analyses remain unchanged.

Scientific and reference review, author approval, redistribution permissions for excluded data, and venue formatting remain human handoff items.

Supporting analysis A8 preserves detailed analysis and reproduction records. The main availability statement is concise and distinguishes the public derived-data package from the excluded raw-data archive.
