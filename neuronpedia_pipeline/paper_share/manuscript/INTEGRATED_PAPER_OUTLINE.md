# Paper outline and integrated argument

Updated 5 October 2026. This outline accompanies the working manuscript, **What Sparse Attribution-Graph Feature Overlap Preserves Across Prompt Changes**. The failure-case analysis is a supporting result within the existing measurement study, not a standalone paper or a claim to have identified a new causal mechanism.

## Central question and conclusion

**Question:** When two attribution graphs share features, how much does that resemblance tell us about the requested fact, the prompt formulation, and the answer being produced?

**Conclusion:** Questions about the same fact share more graph features in the analyzed samples, but stronger controls show that this resemblance also depends on the answer being produced. Selected wrong answers resemble correct responses producing that same answer more than correct responses to the intended question. Feature overlap therefore cannot, on its own, certify correct factual processing or an answer-independent semantic circuit.

The argument proceeds from **observed factual overlap**, to **alternative explanations**, to **stronger answer controls**, to **a concrete failure case that illustrates the interpretation limit**.

## Three findings that hold the paper together

1. **Related factual questions produce reproducible overlap in the analyzed three-model samples.** This establishes a measurement worth explaining, not a recovered semantic circuit.
2. **The same-fact advantage depends on the answer label in the stronger Qwen3-4B controls.** Holding the available words constant does not make the measured association independent of the produced answer.
3. **Wrong-answer graphs can resemble correct graphs producing the same answer.** Similarity alone therefore does not distinguish correct processing of the intended question from a response aligned with a different answer or referent.

The first finding motivates the second; the third shows why the distinction matters. Wording controls and sensitivity checks test alternative explanations. Export audits establish measurement limits. The failed pilots delimit which tasks were behaviorally supported. None needs a separate discovery narrative.

Closeout boundary: collection ended with the separately frozen history pilot. It passed 15/20 checks and failed the required 20/20 gate; no evaluation graphs were requested. Include that result once, with no further experimental round. The existing measurement argument is unchanged. See `FINAL_CLOSEOUT_SCOPE.md` for the handoff criteria.

## Manuscript outline

### 1 Introduction

Open with the distinction between two questions: do related factual prompts produce similar graphs, and does that similarity establish that the intended fact was processed correctly? Explain why the second does not follow automatically from the first. A paraphrase can preserve the fact, words, and answer together; a graph generated around an answer can reflect that answer as well as the question.

State the measurement question and distinguish feature-set overlap from graph topology and causal validation. Preview the three findings above: the original association across three model pipelines, stronger controls in Qwen3-4B, and selected failures that test the interpretation. Do not frame the paper around a failed traceback tool or claim that prompt sensitivity itself is new.

### 2 Methods

Describe the experiments in their actual sequence, with a separate evidential status for each.

| Study | Scope and comparison | Role in the paper |
|---|---|---|
| Original cohorts and third-model extension | Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B; paraphrases, nonce controls, and available crossed cohorts | Establish the original overlap associations; retain the incomplete extension status |
| Exploratory audits | Feature counts, lexical comparator support, tokenization, and export integrity | Identify which alternative explanations the original data cannot separate |
| Matched-choice follow-up | Qwen3-4B; 48 graphs in six country-pair blocks with identical token inventories within blocks | Test fact-associated overlap while crossing answer mapping and wording |
| Position-balanced pilot | Qwen3-4B; 16 behavioral decisions | Report the failed gate and explain why its held-out graphs were not collected |
| Failure-case diagnostic | Qwen3-4B; 16 graphs from four selected France/Germany cases and two response formats | Test how wrong-answer graphs compare with correct intended-country and same-output controls |
| Final saved-data audit | Six matched-choice blocks and selected failure graphs; direct component difference and position/layer filters | Check the answer-dependence contrast without treating graph pairs as independent observations |
| Final prospective history pilot | Qwen3-4B; 15/20 checks correct, including 4/4 literal checks, 7/8 document-history cells and 4/8 spaceflight cells | Report the failed behavioral gate; no evaluation graph effect was measured |

Define feature-set Jaccard and the analysis unit before presenting results. Explain the positive controls, nonce controls, within-domain other-fact comparisons, and the two distinct correct comparators in the failure diagnostic. Keep local freezes distinct from public preregistration and outcome-informed follow-ups distinct from original hypotheses.

### 3 Results

**3.1 Related factual questions share more features in the analyzed samples.** Report the original same-fact margins of 0.170, 0.085, and 0.162 for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B, with 8, 5, and 10 included questions respectively. Preserve domains and incomplete collection. The same facts recur across models, so these are not 23 independent factual replications. Unequal subject coverage prevents ranking the models. Lead with the observed association rather than a semantic mechanism.

**3.2 The positive average survives equal feature counts.** The pooled direction remains positive after sampling equal numbers of features, although one Gemma question reverses. Unequal feature counts are therefore insufficient as the sole explanation under this sensitivity; lexical, answer, and feature-selection differences remain.

**3.3 The original comparisons cannot separate facts from shared words and answers.** None of the included questions has an other-fact comparator meeting the declared word-matching rules. All 86 directed other-fact comparisons differ in expected answer, whereas own-paraphrase pairs share it. This is a limitation of identification, not proof that words or answers explain the entire original effect.

**3.4 A next-token mismatch is not always a wrong completed answer.** Separate whole-answer matches, compatible word prefixes, whitespace, and other continuations. These distinctions explain some exclusions without changing the original inclusion rules. Missing comparison support is unavailable, not zero overlap or evidence that a model lacks knowledge of a subject.

**3.5 Wording matters, but it does not explain every cohort in the same way.** The crossed and made-up-name controls vary by pipeline and subject. Only Qwen3-4B geography meets the strict output rule in every crossed cell; its fact and wording contrasts are approximately 0.101 and 0.106. The close estimates do not establish equivalence, and the full cohorts do not establish universal wording dominance or a model ranking.

**3.6 Export quality limits interpretation of the retained graphs.** Retain identifier-collision rates, reconstruction-error contributions, and incomplete graph coverage as measurement qualifications. Clean later exports show that the answer-related findings are not restricted to collision-contaminated graphs. Neither clean identifiers nor reproducible arithmetic makes the decomposition complete. Keep technical audit detail primarily in the supplement.

**Transition:** These limitations motivate comparisons that preserve the available words while varying which country is queried and which answer label is produced.

**3.7 Matched-choice controls show a small fact association with answer dependence.** All 48 top-label decisions are correct. Report the balanced contrast of 0.0303 and the descriptive output-label contrast of 0.2827. Crucially, present the 0.0628 same-label and -0.0022 changed-label components; the balanced mean does not demonstrate answer invariance. Six blocks, not 48 graphs, determine inferential replication.

Explain the underlying comparison before the contrasts. Each cell below is the unweighted mean feature-set Jaccard across six country-pair blocks, rounded to three decimals. Word and token inventories are identical within each block; query role, order, and option mapping still vary.

| Relationship between prompts | Same answer label | Different answer label |
|---|---:|---:|
| Same queried country | 0.800 | 0.485 |
| Different queried countries | 0.738 | 0.487 |

**Interpretation:** Different-country prompts producing the same label have higher average overlap than same-country prompts producing different labels. The additional same-country overlap is apparent when the label is preserved, but not in the average changed-label comparison. These are similarity scores, not accuracy rates, causal contributions, or fractions of reasoning explained. The near-zero changed-label contrast does not establish equivalence or absence of factual knowledge. Use this table to explain Figure 5 in the text; it does not require an additional main figure.

The added exploratory direct paired difference is 0.0650 (Student-t 95% interval 0.0553–0.0746; two-sided block sign-flip p=0.03125), positive in all six blocks. Report the six-block unit and the independence and null-symmetry assumptions. The original 4,096 correspondence assignments are conditional null configurations, not independent replications. Node-location filters preserve the measured difference but are not causal ablations. Keep the four-representation audit in Supplement S6 rather than adding another main-figure storyline.

**3.8 The position pilot fails its behavioral gate.** Report 8/16 correct labels and no held-out graph collection under that protocol. This is a task/behavior limitation, not a zero graph effect. Summarize the separate local computational audit and positive-control checks; neither constitutes independent human review.

**Transition:** The failed pilot provides a bounded opportunity to ask whether graph resemblance follows the intended question or the answer actually produced.

**3.9 Wrong-answer graphs resemble correct responses with the same output.** All eight selected errors reproduce, all eight named-country controls remain correct, and all eight comparisons favor the same-output control. Mean Jaccard differences are 0.1983 for labels and 0.2649 for capital names; feature-count sensitivity preserves the direction. Include the wrong-country token-location observation as exploratory supporting evidence, not a second headline discovery. State the unresolved position-versus-negation alternative in this section.

Use one concrete example: an indirect question about France produces Berlin; directly naming France produces Paris; directly naming Germany produces Berlin. The failure graph is closer to the Germany/Berlin response than to the France/Paris response. This makes the interpretation limit understandable without implying that the graph proves how the wrong answer arose. The pattern occurs for both letters and capital names, so it is not restricted to A/B output tokens. The two response formats reuse selected cases, not independent populations.

**3.10 The final history pilot limits replication beyond the successful task.** Report 4/4 literal-label checks, 7/8 document-history decisions, and 4/8 spaceflight decisions: 15/20 against a fixed 20/20 requirement. Returned prompts and within-block token inventories passed their checks. No evaluation graphs were requested, so no historical graph-overlap effect was measured. Use a compact count table rather than a graph with empty or zero-valued effect marks. The two selected event pairs are not a general history-accuracy benchmark; the failed gate neither refutes the completed geography result nor extends it to history.

### 4 Discussion

**What the combined evidence supports.** The original association is reproducible in the archived data, stronger controls narrow its interpretation, and the failure cases demonstrate why resemblance does not certify correct factual processing. Feature overlap is informative about relationships among these prompts and outputs, but is not a standalone correctness test. Do not interpret the smaller matched-choice contrast as a percentage of the original signal explained: the studies use different prompts, populations, and contrasts.

**A possible failure to select the intended entity.** Some errors may arise when the model selects or associates the wrong entity with the question despite answering correctly when that entity is named directly. The selected capital-name failures and their wrong-country source locations are consistent with this hypothesis. History sensitivity to ordering and answer mapping is an additional behavioral clue, not evidence of a shared mechanism. Incorrect reference selection, option-position matching, mishandled negation, and answer-associated graph construction remain alternatives. Present the hypothesis here, not as an established result or an abstract headline.

**What the sensitivity checks rule out.** Answer-related differences persist after equalizing feature counts and after removing final-position nodes, late-layer nodes, or both. This rules out confinement to the removed node sets under these filters. It does not isolate a distributed causal answer circuit: the retained graphs are still constructed in relation to the output. No intervention establishes feature necessity or sufficiency.

**What is model behavior and what is a measurement property.** Wrong top-token choices are observed behavior in the hosted setup; graph resemblance is a property of the model-plus-decomposition, pruning, and similarity pipeline. Their agreement is meaningful but does not identify how much of the resemblance is intrinsic model organization versus the graph representation. Reconstruction-error weight, omitted correct logits, and incomplete source-to-output routes reinforce this boundary. The result is neither simply corrupt data nor a direct map of the model's full reasoning.

**Scope and selection.** There are three models from two families overall, but only Qwen3-4B in the stronger matched-choice and failure diagnostics; selected domains and one country pair in the diagnostic; next-token, non-thinking hosted behavior; and unequal original coverage. Correct-response inclusion conditions the overlap estimates on supported behavior. Failed pilots show why that condition cannot be assumed for other tasks. Distinguish knowing an association, selecting the intended referent, obeying the response format, and satisfying our next-token rule. For example, Gemma's earlier correct capital names but incorrect response format do not establish factual errors. Treat a study separating negation, ordinal reference, and option position as an optional future extension, not a prerequisite for the present descriptive claim or an authorized new collection round.

### 5 Conclusion

End with the measurement lesson rather than the error itself: **related factual questions share graph features in the analyzed samples, but stronger controls and selected failures show that resemblance also follows the produced answer. Attribution-graph feature overlap therefore requires matched prompts, answers, and behavioral checks before it can support an interpretation of correct factual processing.** Do not conclude that facts are absent from the model, that the graphs are useless, or that a causal shortcut has been discovered.

## Figure placement

Retain the existing figure numbering in the integrated manuscript.

The current [figure gallery](../figures/index.html) contains six main figures, six supplements, and the final history count table. All titles, labels, notes, and captions received a plain-language review on 6 October 2026. Every figure has a 300-dpi PNG and editable SVG; captions define the comparisons and explain necessary technical terms. Rebuild with `scripts/build_outline_figures_v2.py`. Wording changes are maintained in `scripts/figure_plain_language.py` and recorded in the gallery's `wording_audit.json`. Estimates, inclusion rules, earlier figures, and the sealed release are unchanged.

| Figure | Content | Purpose |
|---|---|---|
| 1 | Original comparison and the questions motivating follow-ups | Explain the study design without mixing it with sample accounting |
| 2 | Reworded questions about the same fact share more features | Establish the initial observation |
| 3 | Change the fact or change the wording | Show that both are linked to shared features |
| 4 | Replace real names with made-up names | Show that keeping the wording gives different results across models |
| 5 | Keep the available words; change the correct A/B answer | Test whether same-fact versus other-fact overlap depends on the answer letter |
| 6 | Compare errors with two kinds of correct response | Show that similar graphs do not, by themselves, establish correct processing of the intended question |

The three central findings map to Figures 2, 5, and 6. Figure 1 establishes the questions; Figures 3 and 4 address alternative explanations. Supplement S6 supports the robustness discussion without adding another claim. Keep the final history pilot as a separate Results 3.10 count table. Do not add a new figure or reopen collection to fill its absent evaluation cohort.

The revised Figure 5 has three panels: the four comparison conditions with a 0–1 overlap color scale, the same-label versus changed-label fact advantages, and the balanced fact versus output-label contrasts. Its behavioral check is expected top-label agreement, not verification of a complete reasoning process. Figure 1 now separates the three central comparisons: original related questions, answer-label controls, and selected wrong answers. The latter two are Qwen3-4B only. Figure 6 includes selected-case behavior and both response formats, with the France/Paris/Berlin example explained in its legend. Full headlines, self-contained legends, and editable figure links are collected in [the figure drafting guide](../figures/LEGENDS.md); earlier figure packages remain unchanged.

Keep the eight detailed failure neighborhood panels, token-role figure, all-case audit table, and complete edge/role data in the supplement. Explain that “chat frame” labels locate activations and do not name a formatting mechanism. The correct logit is unavailable in the failure exports, and reconstruction-error weight is not a causal percentage explained.

Figure 1 no longer contains an inclusion heatmap. It explains the comparison and follow-up questions; collected graphs, questions used, questions not used, and exclusion reasons appear in the [sample-accounting table](SAMPLE_ACCOUNTING.md). Chemistry is the only subject shared by all three original test samples. Retain history as limited subject-specific evidence, not a three-model replication. The final frozen history follow-up superseded the earlier proposal and ended at its failed 15/20 pilot gate; it does not add an evaluation graph cohort or repair the original exclusions.

## Claim boundaries

- The failure section is descriptive evidence from selected known failures, not an estimate of general failure prevalence.
- Repetition across previews and graph exports strengthens reproducibility within the hosted setup, not independent deployment replication.
- Stronger same-output similarity does not establish a position shortcut; the selected layouts also fit mishandled negation.
- The capital-name role pattern does not consistently extend to A/B responses.
- Neither absent correct logits nor a near-zero changed-label point estimate demonstrates absence of a representation.
- The original incomplete Qwen3-4B extension remains incomplete; later completed studies do not repair that cohort retrospectively.

## Working draft and evidence sources

The integrated text is in [the three-model manuscript](ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md). This outline sets the emphasis for the next prose revision: the three central findings, the four-condition explanation in Results 3.7, the concrete example in Results 3.9, and the distinction between observations and candidate mechanisms in the discussion. The terminal history outcome remains in Results 3.10.

The numerical bridge is documented in [the matched-choice results](../methods/MATCHED_CHOICE_RESULTS_FOR_MANUSCRIPT.md). Failure-case values are in the archived findings (author archive: `FINDINGS.md`; not included) and their linked run artifacts. No new graph requests, altered eligibility rules, or changes to frozen analyses are needed for this integration.

The four-condition means and direct contrast come from the six-block source table (author archive: `matched_choice_sensitivity.csv`; not included) and the saved-data audit (author archive: `STATISTICAL_AUDIT.md`; not included). The history counts and prompt-order examples are in the archived pilot responses (author archive: `pilot_responses.csv`; not included). The four-condition table summarizes existing estimates; it introduces no new inferential test.

Technical closeout is complete: figures and legends were assembled, the review PDF was visually checked, isolated same-machine reproduction passed 82 tests and reconstructed the original 23 margins, and the local versioned archive was checksum-verified. The monitor is paused. Independent scientific review, redistribution permissions, reference and author approval, and venue formatting remain human handoff items. This interpretation-focused outline revision follows the sealed local candidate; it does not modify the archived ZIP, compiled manuscript, source data, protocols, or frozen analyses.
