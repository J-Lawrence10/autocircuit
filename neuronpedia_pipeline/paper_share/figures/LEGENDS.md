# Figures for the integrated paper outline

6 October 2026. Plain-language review of all six main figures and six supplements. Saved estimates, inclusion rules, and conclusions are unchanged; no new model runs or statistical tests.

## How to read these figures

A feature is a learned component represented in the exported graph, not a verified concept or a complete reasoning step. Feature overlap counts which components appear in both graphs; it does not compare all their connections. Jaccard overlap divides the number shared by the total number of distinct features across the two graphs: 0 means none shared, and 1 means identical sets. A difference in feature overlap subtracts one overlap score from another; each figure specifies the comparison. It can be positive, zero, or negative. Zero means equal overlap, not missing data.

A test question was reserved for evaluation rather than for developing the analysis. A token is one unit of predicted text; it may be a whole word, part of a word, or a symbol. A/B answer means the letter produced, not necessarily the same capital city. Category colors are explained by labels or legends; numerical colors have a scale. An asterisk on Qwen3-4B marks the incomplete original collection (145/147 graphs), not the separate completed follow-ups.

## Figure 1 Three tests ask what similar graphs can tell us

![Figure 1](figure1_design_and_coverage.png)

A, Compare a question with a reworded question about the same fact and with questions about other facts. Comparisons stay within the same subject and evaluation group. Gold means the chemical element, not an ideal or gold-standard question. The gold, iron, and made-up-name examples come from the development questions, not the test questions plotted in Figure 2. The original samples cover three models, with different subjects available in each. B, In Qwen3-4B, keep the same words and token counts within each country pair, but change which country is asked about, which capital is assigned to A or B, and the wording. This tests whether questions about the same fact still share more features when the correct A/B answer changes. All 48 predicted answer letters were correct. The France/Germany example illustrates the design using a pilot pair, not an additional test pair. Displayed examples are shortened; full prompts preserve both country names and all other words within a pair. Word order and the role of each country still differ, so this does not isolate meaning alone. C, Compare a selected wrong-answer graph with two correct-answer graphs: one answering the intended country and one producing the same answer as the error. This Qwen3-4B study contains 16 graphs from one country pair and two answer formats, not 16 independent tests. Arrows show comparison steps, not causes. Box colors identify labeled steps, not quantities. Collection counts, exclusions, and failed preliminary checks are reported separately.

[Editable SVG](figure1_design_and_coverage.svg)

## Figure 2 Reworded questions about the same fact share more features in these samples

![Figure 2](figure2_fact_signal.png)

A, Each point represents one test question that passed the fixed inclusion rules. A test question was reserved for evaluation, rather than for developing the analysis. The difference in feature overlap is the overlap with a reworded version of the same fact minus the average overlap with reworded questions about other facts in the same subject and test set. For illustration only, 0.50 overlap with the same fact minus 0.30 average overlap with other facts gives a difference of +0.20. These example numbers are not measured results. A positive difference means more overlap with the same fact, zero means equal overlap, and a negative difference means more overlap with the other-fact questions. The difference is not a percentage increase. B, The same measure is averaged separately by subject. Colors and shapes identify subjects; diamonds show model averages. Bars are saved 95% bootstrap intervals, obtained by resampling questions 10,000 times. n counts questions, not graph pairs. Averages are 0.170 for Gemma-2-2B (8 questions), 0.085 for Qwen3-1.7B (5), and 0.162 for Qwen3-4B (10). The same facts recur across models, and subject coverage differs, so these results do not rank the models. Shared words and shared answers remain possible explanations. Missing subject groups are unavailable comparisons, not zero effects. *The original Qwen3-4B collection is incomplete: 145 of 147 planned graphs are available.

[Editable SVG](figure2_fact_signal.svg)

## Figure 3 Both the fact and the wording are linked to shared features

![Figure 3](figure3_fact_and_wording.png)

A, Difference in feature overlap. B, Difference in similarity when each feature is weighted by its saved graph-influence score (cosine similarity, which compares the direction of the weighted feature vectors). For both panels, the baseline is a pair of questions differing in both fact and wording. The same-fact comparison changes the wording; the same-wording comparison changes the fact. For example, compare “The chemical symbol for gold is ...” with “Gold has the chemical symbol ...” to keep the fact but change the wording. Compare the starting prompt with “The chemical symbol for iron is ...” to keep the wording pattern but change the fact. Compare it with “Iron has the chemical symbol ...” to change both: this is the baseline. These examples illustrate the comparisons. “Same wording” means the same sentence pattern, not an identical prompt; the element name must change. Each difference is similarity in the labeled comparison minus similarity in that baseline, calculated within each subject. Panel A counts which features are shared; panel B also considers their saved influence weights. Neither panel directly measures correctness. Each model has 27 graphs: three facts, three wordings, and three subjects. Colored points are subject averages; black diamonds average the subjects equally. Lines connect descriptive estimates, not confidence intervals. Average fact/wording differences in A are 0.074/0.118 for Gemma-2-2B and 0.101/0.064 for Qwen3-4B. Some first predicted tokens are incomplete answers or not answers at all. Only Qwen3-4B geography matches the expected first token in all nine questions; its fact/wording differences are 0.101/0.106. These results do not establish that one factor dominates or that one model is better. Qwen3-1.7B was not tested in this design.

[Editable SVG](figure3_fact_and_wording.svg)

## Figure 4 Made-up-name controls give different results across models

![Figure 4](figure4_control_comparisons.png)

Replace the real name in a question with a made-up name, either keeping the original wording (A) or rewording the question (B). For each target question, subtract its overlap with the made-up-name version from its overlap with a reworded factual version. Above zero favors the factual version; below zero favors the made-up-name version. Colors identify models, points represent test questions, diamonds show averages, and bars are saved 95% bootstrap intervals from resampling questions. n counts included questions. The controls match only the kind of first token: letters/numbers, whitespace, or punctuation/symbols. They do not match the exact answer, its meaning, confidence, or correctness. Averages in A are -0.069 (2 questions), -0.014 (4), and +0.096 (10) for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B. Small samples and different subject coverage prevent a general claim that wording explains the original result. *The original Qwen3-4B collection is incomplete (145/147 graphs).

[Editable SVG](figure4_control_comparisons.svg)

## Figure 5 Same-fact versus other-fact overlap depends on the A/B answer

![Figure 5](figure5_matched_choice.png)

Qwen3-4B only: six country pairs and 48 correct predicted A/B answers. This follow-up was designed after earlier results were seen; its rules were fixed before collection. The words and token counts are identical within each country pair. A, Average overlap for questions asking about the same or different countries and producing the same or different A/B letters. All comparisons change the wording. The four averages are 0.8005, 0.4853, 0.7377, and 0.4874, read row by row. The color scale runs from no shared features (0) to identical feature sets (1); it is not an accuracy scale. B, Subtract different-country overlap from same-country overlap, separately when the answer letter stays the same or changes. The averages are 0.0628 and -0.0022. Their paired difference is 0.0650 (exploratory Student-t 95% interval 0.0553–0.0746; two-sided sign-flip p=0.03125, assuming independent country pairs and symmetric differences under the null). C, Average the two fact differences in B: 0.0303, with a saved 95% bootstrap interval of 0.0265–0.0338. For comparison, overlap with the same answer letter minus overlap with a different letter is 0.2827, averaged across same- and different-country comparisons. Each line in B–C represents one country pair; diamonds mark averages. Only the fact average in C has an interval drawn. Colors identify the labeled categories; B and C have different vertical scales. Six country pairs—not 48 graphs or 4,096 possible reassignments in the earlier null test—supply the independent units assumed by the statistical tests. A near-zero estimate does not prove no effect. These differences are not fractions of reasoning explained and do not establish a cause. Word order and country roles remain possible explanations. Supplement S6 checks whether the differences remain after excluding some features.

[Editable SVG](figure5_matched_choice.svg)

## Figure 6 In selected errors, graph similarity follows the answer more than the question

![Figure 6](figure6_failure_cases.png)

A, In 16 new Qwen3-4B graphs, all eight questions naming the country are answered correctly and all eight selected questions referring to its position reproduce the error. Each answer format has four correct and four wrong responses. These selected cases do not estimate how often the model makes errors in general. B–C, Compare each wrong-answer graph with a correct response to the intended country (blue) and a correct response giving the same answer as the error (orange). The country-list order and A/B assignments stay fixed. For example, with France first and A: Berlin, B: Paris, an indirect question about France produces Berlin. Naming France produces Paris; naming Germany produces Berlin. The error graph is more similar to the Germany/Berlin graph. Circles use all retained features; open squares use equal numbers of randomly sampled features, averaged over 200 repetitions. Lines connect comparisons for the same error. The same-answer minus intended-country overlap averages 0.1983 for A/B answers and 0.2649 for capital names (0.1851 and 0.2361 after equalizing feature counts). All 16 exports and eight three-graph comparisons pass the file-integrity and output checks. The cases share one country pair and overlapping controls, so no population confidence intervals or confirmatory p-values are shown. These comparisons do not keep the exact words constant. Confusing list positions, mishandling negation, or graph structure tied to the produced answer remain possible explanations—not established causes. The correct-answer output node is missing from each error graph; its contribution is unknown, not zero.

[Editable SVG](figure6_failure_cases.svg)

## Supplement S1 Graph files have two separate limits: ID conflicts and approximation error

![Supplement S1](figureS1_export_and_error.png)

A, The percentage of saved raw graph files in which the same node ID refers to conflicting node identities. Labels show affected files over files checked. Zero means no conflict was detected, not no graphs or no model errors. The original question sets include factual questions and controls; the fact/wording sets vary both factors. B, Reconstruction-error nodes record part of the model computation not captured by the feature approximation. The axis gives their share of absolute nonterminal-node influence, using the saved audit definitions. This is not the percentage of wrong answers or of reasoning explained. Box centers mark medians; boxes span the middle 50%, whiskers extend to values within 1.5 box lengths, and dots show values beyond the whiskers. Original distributions use raw-file audits; Qwen3-4B uses converted graphs with no ambiguous IDs removed. Differences combine model, exporter, and approximation choices; they do not isolate model size or architecture.

[Editable SVG](figureS1_export_and_error.svg)

## Supplement S2 Average overlap differences stay positive under alternative graph comparisons

![Supplement S2](figureS2_robustness.png)

The difference in feature overlap is same-fact overlap minus other-fact overlap, using the comparison specified for each check. Compare the original analysis with three alternatives: include reconstruction-error nodes; use only files without detected node-ID conflicts; or compare with the most similar other-fact question rather than the average other-fact question. Reconstruction-error nodes represent approximation error, not wrong model answers. Points are saved averages; bars are 95% bootstrap intervals from resampling test questions. n counts questions. Restricting files requires rebuilding the comparison groups and leaves only two Gemma questions, so that positive result is weak evidence on its own. The size-regression intercept is not plotted: with centered predictors it equals the unadjusted mean and is not an independent check. *Qwen3-4B remains incomplete (145/147 graphs).

[Editable SVG](figureS2_robustness.svg)

## Supplement S3 Average overlap differences stay positive with equal numbers of features

![Supplement S3](figureS3_equal_feature_counts.png)

The difference in feature overlap is same-fact overlap minus average other-fact overlap within the same subject and test set. Within each model, subject, and test set, randomly sample the same number of features from every graph. K is the number of features in the smallest graph in that group; the second check uses half that number, rounded down. Repeat 200 times, reusing each sampled graph across comparisons within a repetition. Lines show individual test questions; diamonds show averages. Bars are descriptive 95% bootstrap intervals from resampling questions, not from the 200 feature samples. Seven of eight Gemma questions and all included Qwen questions retain positive average differences. Equalizing counts does not remove differences in shared words, answers, or which features the exporter retains. A smaller overlap score after sampling is not a percentage of signal explained. *Qwen3-4B remains incomplete (145/147 graphs).

[Editable SVG](figureS3_equal_feature_counts.svg)

## Supplement S4 Other-fact questions share fewer words, leaving a gap in the controls

![Supplement S4](figureS4_lexical_support.png)

For each test question, compare word overlap with its same-fact rewording (horizontal axis) against the highest word overlap with any other-fact rewording (vertical axis). Word overlap uses unique letter/number words, ignores letter case, and keeps common words. Both axes use Jaccard overlap: shared words divided by all distinct words across the pair. The dashed line means equal overlap; the shaded band allows a difference of 0.05 in either direction. Every other-fact comparison falls below that band. Thus 0/8 Gemma, 0/5 Qwen3-1.7B, and 0/10 Qwen3-4B questions have a comparison meeting the specified word-matching rule. None qualifies under the alternative at-least-as-much-word-overlap rule or the joint word/feature-count rule either. This is a missing comparison, not a measured zero effect or proof that words explain all feature overlap. Same-fact questions also share their expected answer, so the data do not isolate meaning from words or answers. *Qwen3-4B remains incomplete (145/147 graphs).

[Editable SVG](figureS4_lexical_support.svg)

## Supplement S5 A matching first token does not always verify the whole answer

![Supplement S5](figureS5_answer_audit.png)

A, Audit the first predicted text unit, or token, using the Qwen tokenizers. Green means the whole expected answer fits in that token; yellow means it is only a compatible beginning, so the completed answer is unverified; gray means a different token. Seven apparent mismatches across the two Qwen models are compatible beginnings of multi-token answers. Counts include development and test factual questions, including Qwen3-1.7B geography questions without complete controls; they are not the question counts in Figure 2. Qwen3-4B is missing one factual graph and one made-up-name graph. Official Qwen tokenizer versions agree with all saved prompt pieces and decoded top tokens, but the exact versions used at the time of graph collection cannot be fully recovered. Gemma tokenizer access was denied, leaving that audit unresolved. B, In the fact/wording experiment, counts use the original exact first-token matching rule after trimming whitespace; that rule is unchanged. Only Qwen3-4B geography matches in all nine questions. Its fact/wording differences are 0.101/0.106, which do not establish that either factor dominates. A zero in history means zero matches under this rule, not zero history knowledge. *The original Qwen3-4B collection is incomplete.

[Editable SVG](figureS5_answer_audit.svg)

## Supplement S6 The answer-related differences remain after removing some graph features

![Supplement S6](figureS6_graph_location_sensitivity.png)

Qwen3-4B only. Repeat the saved comparisons after removing features at the last token position, in the last quarter of observed feature layers, or both. Removal happens before combining feature identities across positions. A, Plot the difference between the same-letter and changed-letter fact comparisons in Figure 5B. Each line represents one of six country pairs; black diamonds show averages. B, Plot overlap with the correct same-answer response minus overlap with the correct intended-country response in the selected errors from Figure 6. Lines show the individual comparisons; colored diamonds show format averages. All filtered feature sets are nonempty. Zero means equal overlap, not missing data. These checks were chosen after seeing earlier results. No confidence intervals or new population tests are attached. Removing features from saved graphs is not an intervention on the model and does not establish a cause. The remaining graphs are still constructed around the answer being produced.

[Editable SVG](figureS6_graph_location_sensitivity.svg)

## Final history pilot

| Checks | Correct | Required |
|---|---:|---:|
| Literal A/B instructions | 4/4 | 4/4 |
| Document-history pilot | 7/8 | 8/8 |
| Spaceflight pilot | 4/8 | 8/8 |
| Overall | 15/20 | 20/20 |

The fixed pilot failed. No evaluation graphs were requested, so no history graph-overlap effect was measured. This is not a history-accuracy benchmark. The original history exclusions remain unchanged.

## Reproduction and source data

Run `.venv-final-reproduction/Scripts/python.exe scripts/build_outline_figures_v2.py`. All 12 figures are rebuilt from saved data as 300-dpi PNGs and editable SVGs. The wording is maintained in `scripts/figure_plain_language.py`; the label review is recorded in `wording_audit.json`.

The manifest records input, builder, helper, and output hashes; plotted source tables are in `tables`. Figure 5 shows six blocks, not 48 independent observations. Category colors are directly labeled or keyed in legends; the numerical heatmap has a 0–1 color scale. Missing groups are unavailable, never effect-size zeros.

Earlier figures, the compiled manuscript, and the sealed release archive remain unchanged. This is a figure revision for author review, not a new scientific analysis.
