# Manuscript clarity and logical flow revision

## 7 November 2026 approved GitHub review edition

The author requested committing and pushing the accumulated paper updates. This review edition includes the current three-model samples and figures, approved introduction and Methods revisions through the first paragraph of Section 2.3, the methods diagram, the question-version clarification, and accompanying code snapshots, tests, derived tables, and provenance. The latest proposed rewrite of the invented name controls paragraph remains unapproved and is not inserted. Earlier local-edition notes below describe the authorization and verification status at the time those revisions were made.

Only the curated `paper_share` folder and its package-builder source are included in this push. Raw graphs, tokenizer/model files, reference PDFs, credentials, local release ZIPs, and unrelated working-tree changes remain excluded. The edition is `approved_methods`; the previous review archives remain intact. This is a working-paper update, not a journal submission or a claim of independent validation.

## 7 November 2026 Section 2.3 question-version comparison (local)

The author approved the revised first paragraph of Section 2.3 and its consistency correction to Figure 3. The manuscript now states that the 27-graph design groups original, alternative 1, and alternative 2 versions rather than assuming identical sentence patterns across facts. Results Section 3.2, Figure 3's headline, axis labels, examples, and caption use the same distinction. The illustrated gold and iron prompts are exact saved prompts, including the alternative-1 pair whose sentence patterns differ. This clarifies what the existing comparisons measure; no comparison, numerical result, or statistical test was changed.

The next paragraph on invented name controls remains under author review. The sharing edition is `methods_2_3_versions`, preserving earlier review archives. No new experiment, commit, or GitHub push is included.

Verification: 53 focused manuscript, caption, diagram, figure-wording, and current-package tests passed. All 22 plotted-data tables, both frozen Qwen3-1.7B result files, and the 13 unchanged figure PNGs are byte-identical to their pre-edit versions. Figure 3 was rendered and visually checked; its numeric fingerprint is unchanged by the label edits, and a regression test checks the exact saved example prompts. All 14 captions are synchronized. These are automated and assistant checks, not independent human review.

## 7 November 2026 Methods terminology and statistical detail (local)

The author approved introducing the standard name "Jaccard similarity" while retaining the plain-language explanation of feature overlap, "rewording," and "invented name controls." Section 2.2 now defines T_i and P_i as graph-derived feature sets, excludes i explicitly from the other-fact mean, and separates the unchanged inclusion rule into readable sentences. Leading and trailing whitespace is explained with examples. The statistical description specifies the mean, descriptive 95% percentile bootstrap interval, 10,000 resamples of calculated fact-level differences with replacement, and exact one-sided sign-flip test direction. Existing dependence and next-token limitations are retained.

References to "within-subject" comparisons in the current manuscript and methods-diagram caption now say "within the same subject area" to distinguish chemistry, geography, and history from repeated measurements on participants. Fact-level bootstrap and sign-flip-test terminology is consistent in the relevant methods and supporting text. No prompts, inclusion rules, statistical code, results, or figure data changed. The local sharing edition is `methods_terminology`, preserving previous archives; no commit or push is included.

The next paragraph, Section 2.3, remains under author review. Checking its wording against the saved prompts showed that the original/alt1/alt2 groups do not consistently share identical sentence patterns across facts. A proposed clarification will distinguish saved wording labels from exact wording matches; related Figure 3 descriptions need the same review. No new analysis or changed comparison is implied by that clarification.

Verification: 51 focused manuscript, caption, methods-diagram, figure-wording, and current-package tests passed. All 14 figure PNGs, 22 plotted-data tables, and the two frozen Qwen3-1.7B result files are byte-identical to their pre-edit versions. All 14 manuscript captions remain synchronized. These are same-host automated and assistant checks, not independent scientific review.

## 7 November 2026 methods reference diagram (local)

The author approved the plain-language explanation of the primary same-fact minus average other-fact comparison and requested a methods diagram. Section 2.2 now puts that explanation before the equation, retains the same inclusion rules and interpretation, and cites new Figure S8. The diagram covers the primary question/control workflow only: four prompt roles, hosted exports, inclusion checks, unique learned-feature identities, the Jaccard comparison, and fact-level summaries. Invented name comparisons remain separate from the all-other-fact baseline. Exact chemistry development prompts illustrate the roles; illustrative feature sets and arithmetic are explicitly not measured findings. Figure 1 retains the broader study overview, and the other experiments keep their own rules.

The new diagram has an editable source and caption, is included in the gallery and sharing package, and does not renumber existing results figures. It adds no observations or empirical analyses. Raw data, frozen results, prompts, eligibility rules, and previous review archives remain unchanged. The new local sharing edition is `methods_diagram`; no GitHub push is authorized.

Verification: 165 relevant tests passed, excluding the unrelated legacy traceback module. After final terminology and caption synchronization, 36 focused manuscript, caption, figure, and diagram tests passed again. All 13 preceding PNG figures and all 22 canonical source tables are byte-identical to the previous review archive. The final methods diagram was visually inspected, its exact prompts checked against the manifest, its illustrative arithmetic tested, and its text bounds checked automatically. All 14 captions are synchronized. These are assistant and automated checks, not independent human review.

## 7 November 2026 paragraph-by-paragraph Methods review (local)

The author approved renaming Section 2.2 to "Measuring feature overlap" and opening with "We measured feature sharing between questions using Jaccard overlap." The definition, range, and distinction between feature sets and connections remain unchanged. Subsequent paragraphs are being reviewed separately; unapproved proposed wording is not inserted into the manuscript. This editorial change alters no data, analyses, figures, findings, or limitations. The `methods_review_2_2` sharing edition preserves the completed `unified_current_data` archive.

The author then approved the feature-counting paragraph with the exact `(feature family, layer, feature ID)` tuple. It distinguishes reused numerical feature IDs from missing or duplicated graph-node identifiers, explains collapsing repeated feature occurrences across input positions, defines the excluded node categories, and retains within-model comparisons. The repeated Jaccard formula and repeated scope statement were removed from that paragraph because the preceding paragraph already defines the measure and its scope. This wording was checked against the implementation; no exclusion or analysis rule changed. The `methods_review_2_2_features` edition preserves the preceding review archive.

## 7 November 2026 unified current-data presentation (local)

The author requested one up-to-date presentation of the available data rather than parallel original and expanded Qwen3-1.7B results. All applicable main and supplementary figures, plotted tables, manuscript results, Methods, outline, claims map, findings summary, and sample accounting now use the same combined Qwen3-1.7B sample: 91 collected graphs and ten evaluation facts, comprising five chemistry and five geography facts. The main mean difference is 0.0894, with a descriptive 95% interval of [0.0820, 0.0976]. The three-model comparison contains 8, 10, and 10 model-specific evaluation observations, not 28 unique independent facts.

The corresponding output-type-matched control comparisons use nine same-pattern and ten reworded invented name controls. The exporter audit uses 91 Qwen3-1.7B graphs, and its next-token audit uses 50 available factual prompts, including development and incomplete-history prompts. These denominators are not interchangeable. The inclusion audit now reports all 45 model-by-evaluation-fact combinations, including the incomplete history sets. History collection failures remain visible and are not converted to zero effects or incorrect-answer counts.

The former five-fact subset is preserved in the underlying archive and reconstruction records, not shown as another model, replication, or additional current panel. Obsolete expanded-only presentation tables are archived outside the current figure and sharing folders. The Qwen3-4B answer-letter, selected-error, and history-pilot experiments and the Gemma/Qwen3-4B fact-by-wording experiment retain their own samples and results. The Discussion's proposed mechanism tests remain future research, not completed analyses.

This update consolidates already-computed evidence. It makes no model requests, changes no frozen analyses or raw files, and does not alter prompts, hypotheses, eligibility rules, or limitations. A brief Methods statement retains the exploratory status of the combined Qwen3-1.7B analysis; collection chronology is kept in reproducibility records rather than repeated through the narrative. Earlier dated review ZIPs remain intact, and this package uses the `unified_current_data` edition. No commit or GitHub push is part of this update.

Verification: 159 publication-analysis, collection-safety, control, manuscript, caption, figure, and current-cohort accounting tests passed; the unrelated legacy traceback test module was excluded. All 13 manuscript captions match their authoritative figure text. The current plotted tables reconcile with the saved results, including the 45-row evaluation-inclusion audit. The nine changed figures were visually inspected, and the frozen Qwen3-1.7B analysis and display-audit result hashes are unchanged. These are automated and assistant checks, not independent human scientific review.

## 7 November 2026 Methods and future-research update (local)

The author requested that the unresolved explanation for answer-associated overlap be framed as Discussion and future research rather than another experiment round. Section 4.3 now distinguishes shared answer-producing activity from answer-dependent selection of graph features, allowing both to contribute. It explains why the existing count and location filters do not separate these possibilities. Proposed comparisons hold the model run fixed while changing the attribution target and measure activity before answer-dependent selection; a further causal study would use held-out questions, unchanged-model and matched-random controls, and multiple intervention strengths. Saved exports cannot supply the complete proposed comparison.

Section 4.2 retains the sample limits, statistical assumptions, and unresolved reference-selection, position, and negation explanations, while moving the graph-selection discussion into the new section. The author then requested that Methods also reflect the added data. Section 2.1 now explicitly distinguishes the original five chemistry evaluation facts from the overlapping ten-fact expanded sample. New Section 2.8 describes the completed collection's settings and source checks, reconstruction of original estimates, inference and secondary multiplicity rules, control and sensitivity analyses, and the retrospective audits with their distinct 91-graph, ten-fact, and 50-factual-prompt denominators. These methods are verified against the archived analysis and audit plans; they do not introduce another analysis or include the proposed future experiments.

Results, numerical findings, figure captions, conclusion, eligibility rules, and frozen protocols remain unchanged. The outline and local sharing copy follow the same structure. No experiment is started, no independent review is claimed, and no GitHub push is authorized. The new `methods_discussion` review archive preserves the earlier `updated_figures` edition.

Verification: 139 tests passed in the publication-analysis suite, excluding the unrelated legacy traceback test module. All 13 figure PNGs and 26 plotted-data tables are byte-identical to the pre-edit versions. All 13 captions match their source, and figure/claims-map provenance hashes were refreshed after the outline change. The Abstract and Introduction, Results, Conclusion, and supporting analyses match the prior review archive after normalizing line endings and portable link targets. These are automated and assistant checks, not independent human scientific review.

## 7 November 2026 figure-wide expanded-sample update (local)

After accepting the recommendation to leave remaining history coverage incomplete for this paper, the author requested that all current figures reflect the added data. The original scientific estimates remain fixed, but the current figures now make the late Qwen3-1.7B sample visible in the relevant main and supplementary panels, not only S7. Original and expanded samples are labeled separately; the ten expanded evaluation facts include the original five chemistry facts and do not constitute a fourth model or an independent replication.

The expanded result is 0.0894, compared with the original chemistry mean of 0.0854. The main change is broader subject coverage, not a reversal or a materially different average. The eight-of-ten same-pattern invented name control preference and the positive reworded-control comparison remain visible. The Qwen3-4B-only answer-letter and selected-error results, and the original fact-by-wording comparison, are not recomputed or expanded with these data.

A separately recorded retrospective display audit reuses the original word-matching, tokenizer, and export-audit definitions. It reproduces the old Qwen3-1.7B audit results before extending them: no ambiguous IDs in 91 graphs, median approximation-error influence of 6.06%, no qualifying word-matched comparator for any of ten evaluation facts, and 42 whole expected next tokens, four compatible beginnings, and four different next tokens among 50 available factual prompts. The latter are not full-answer accuracy counts and do not change inclusion. All raw files, the frozen primary analysis, and earlier analysis plans remain untouched; no hosted requests or local inference are made.

The claims map, captions, figure gallery, manuscript cross-references, and sharing overview are updated together. A caption synchronization script prevents the manuscript legends from drifting from the figure source. New plotted tables have separate names, retaining original tables and estimates. Earlier `late_completion` and November 6 review ZIPs remain archived; the new package uses the `updated_figures` edition. The public GitHub package remains the November 3 release, with no commit or push authorized here.

Verification: 137 publication-analysis, collection-safety, control, manuscript, caption, and figure tests passed; the unrelated legacy traceback test module was excluded. All 15 previously plotted tables were compared byte for byte with the November 7 `late_completion` ZIP and are unchanged. Eleven separately named expanded-sample tables were added. Figures 3, 5, 6, S6, and S7 retain their prior PNGs; the remaining layouts were updated and visually checked. All 13 manuscript captions match the figure source. These are same-host automated and assistant checks, not independent human review.

## 7 November 2026 late Qwen3-1.7B completion integration (local)

The author reopened only the missing original Qwen3-1.7B requests on November 6, then requested analysis and integration. All 70 missing prompts were attempted once with unchanged wording: 30 geography and 11 history graphs were saved; 29 history requests were rejected for input length. The late sample has 91/120 graphs, including the 50 unchanged original files. This does not reopen the stopped Qwen3-4B history pilot or introduce another model.

The original five chemistry evaluation facts and all original estimates remain intact. Five newly analyzable geography facts all show positive same-fact overlap differences, mean 0.0935; the expanded ten-fact mean is 0.0894. The same-pattern invented name controls remain a counterpoint: eight of ten expanded comparisons favor that control over the factual rewording, whereas all ten favor the factual rewording over the reworded control. The weighted and equal-count feature checks remain positive; the coarse edge-flow comparison is inconclusive. These outcomes extend subject coverage and retain the control-dependent interpretation, rather than claiming isolated factual meaning.

Methods 2.1, Results 3.1–3.2, Discussion 4.2, and Supporting analysis A5 now distinguish original and expanded samples. A5 retains all exclusions, the nominal and conditional tests with dependence assumptions, the 15-test Holm family, negative controls, and alternative-metric results. New Figure S7 separates raw collection counts from included evaluation facts. Original Figures 1–6 and S1–S6 remain unchanged. The outline, findings summary, sample accounting, and local sharing package follow the same separation.

The late analysis records its settings before computing new overlap estimates, reproduces all original raw/converted representations and per-fact contrasts, and preserves raw inputs and checksums. Its automated code review and checks ran on the same host, not on an independent machine or by an independent human reviewer. Shorter history prompts are only a feasibility draft: naturalness and control symmetry need improvement, and multi-token expected answers require an explicit analysis decision. No shorter-prompt collection has run.

The updated package uses a separate November 7 `late_completion` archive, preserving earlier dated ZIPs. The public GitHub package remains the November 3 release. No new commit or push is part of this integration.

Verification: 124 publication-analysis, collection-safety, control, manuscript, and figure tests passed; the unrelated legacy traceback test module was excluded. All 12 original figure PNGs and all 12 original plotted-data tables were compared byte for byte with the pre-integration November 6 ZIP and are unchanged. S7 was rendered and visually checked, and its source counts and estimates reconcile with the saved analysis. These are same-host automated and assistant checks, not independent human review.

## 6 November 2026 paragraph-by-paragraph introduction revision (local)

The author approved a direct explanation of attribution graphs, a plain-language definition of Jaccard overlap, and connected explanations of the original comparison, the A/B answer manipulation, and the selected-error comparisons. Country names and answer options are introduced before comparisons are described. The France/Paris example distinguishes a requested fact from the letter used to answer it; the France/Paris and Germany/Berlin controls explain how both comparison predictions can be correct. The findings interpretation explicitly states that, when the required letters differed, same-country comparisons had nearly the same average overlap as different-country comparisons even though the factual answer remained unchanged within the same-country comparisons.

The author requested and authorized a broad-to-narrow introduction reorganization. Six paragraphs now develop the broader computational question, tools and prior research, the France/Paris interpretation problem, the original hypothesis and measurement, the later comparisons, and the contribution. The original hypothesis concerns same-fact feature overlap; the later answer-letter interpretation is not presented as its prespecified starting hypothesis. The approved detailed explanations have been relocated, not discarded: Jaccard to Methods 2.2, the A/B manipulation to Methods 2.5, and the incorrect-prediction/control example to Methods 2.6. The approved two-sentence changed-letter finding is retained verbatim in Results 3.3. The actual pilot chronology and selection details remain in Methods. References [1], [2], and [5] ground the introductory background; position-retrieval reference [7] now accompanies the relevant Methods analysis. The abstract is unchanged and remains for later revision.

The author approved the first five reorganized introduction paragraphs unchanged and requested a shorter ending. The final paragraph now contains one contribution statement followed by a direct transition into Methods. The fuller findings remain in the Abstract and Results, with interpretation and causal boundaries in the Discussion.

The author approved the Methods overview with a concrete explanation of changing A/B answer assignments. The term "error graph" is now defined as an attribution graph for an incorrect prediction before its first shorthand use. The correct-answer comparator is described as giving the same answer as the error in a context where that answer is correct.

The author approved the model-description paragraph in Methods 2.1. It now explains the common Jaccard measure and feature-exclusion rules, with comparisons conducted separately within each model. This replaces an overly broad statement implying that pruning and analysis filtering differed across models. Model-specific feature representations and question coverage still limit architecture or size comparisons; the within-model scope and non-ranking interpretation remain explicit elsewhere in the manuscript.

The author approved a separate question-design paragraph describing the 30 facts across three subjects, four question versions per fact, and the five development/five evaluation facts per subject. Invented name controls and the purpose of the two sets are now explained directly. All versions of each fact stay in the same split; no randomized split is claimed.

The author approved a collection paragraph distinguishing the 120-question design from the additional 27-graph fact-by-wording experiment. It reports Gemma's 120 collected graphs, Qwen3-1.7B's 50 graphs, and Qwen3-4B's 118/120 plus 27/27 graphs without changing counts or exclusions. The incomplete-extension status, unmet three-subject requirement, and Llama resource exclusion remain explicit. In response to a collection-history question, the saved Qwen3-1.7B chemistry logs show a 40-job run temporarily halted by three server-busy HTTP 500 errors, then completed on resumption (22 generated, 18 existing). These logs do not establish why the remaining subjects were not subsequently completed; no unverified reason is added to the manuscript.

The author also requested American English spelling and no em dashes. These style changes are applied to the current manuscript, outline, and local sharing overview. The remaining em dash in Figure 1's footer is replaced with a comma; the figure retains "error graph" now that the term is defined in the preceding text. Numerical ranges and frozen protocols are unchanged.

This local editorial update changes no experiments, source tables, estimates, scientific methods, results, or limitations. The GitHub package remains the 3 November release until a later explicitly requested push.

## 3 November 2026 public review-package update

This release packages the author-approved 28 October editorial revision at the existing GitHub review-package and manuscript paths. The manuscript retains its editorial date and now carries an explicit working-manuscript, not-peer-reviewed label. No findings, estimates, eligibility rules, or experimental protocols were changed for this release. The archived reproduction evidence remains historical; the release checks concern editorial consistency, portable links, file integrity, and reported table values. Git history records the published revision.

## 28 October 2026 reader-centered revision

This editorial pass applies the author's grant-writing principle: build the reader's mental picture before introducing detail, explain why each comparison is needed, and connect its result to the next question. Findings are stated directly; qualifications are attached to the claims they constrain rather than repeated as general disclaimers.

The principle was recovered from the October 27 discussion in **Review grant application docs** and its saved grant-project writing conventions. It is a writing preference, not scientific evidence or an external validation of this manuscript.

### What changed

- The author-approved term is now **invented name control**, with a concrete gold-to-zorium definition. Current manuscript, figure labels, captions, and Figure 1 mockups use it; archived `nonce` data identifiers and frozen protocols are unchanged. Results headings 3.2, 3.4, 3.5, and 3.6 use the author's approved finding-led wording. Section 3.5 retains its average-level interpretation and the individual reversal in the body.
- The introduction opens with the France/Paris comparison so the reader can distinguish a shared fact, shared words, and a shared answer before encountering technical details.
- Feature overlap is explicitly defined as shared features divided by distinct features, with repeated token-position occurrences counted once.
- Results now connect the original association, the original controls, the answer-letter comparison, and selected errors. Each major comparison has a purpose before its estimates appear.
- The abstract, discussion, conclusion, and findings summary foreground the observed answer-associated pattern. They distinguish this contribution from both a generic warning about similarity and a causal mechanism claim.
- The two matched-choice tests have separate questions and reference distributions in Methods. The prespecified average remains primary; the later between-condition difference remains exploratory. The exchangeability and dependence assumptions remain open to independent statistical review.
- Discussion separates interpretation from scope and remaining questions. Necessary limits are retained, including selected/dependent errors, one-model stronger controls, near-zero not being equivalence, incomplete collection, and the failed history gate.
- All supplementary figures now follow the conclusion. S4, S3, S6 and the historical regression-intercept correction are in Supporting analysis A4 rather than interrupting the main result sequence.
- Figures 5 and 6 use direct observational headlines. All six main captions are shorter while preserving definitions, sample units, uncertainties, and qualifications needed to read them independently.

### Verification and release status

No hosted requests, new experiments, re-estimation, eligibility changes, or new scientific results are part of this revision. The figure rebuild uses saved results; the source tables and plotted numerical values are checked against the prior package. The source manuscript, outline, local sharing folder and dated ZIP are synchronized after editorial tests and the package verifier pass. At completion on 28 October, this revision was local; Git history records subsequent release updates.

Fourteen narrative and figure-wording tests passed after the approved terminology and heading updates. All 13 packaged data tables match the previously pushed package byte for byte, and every decimal value reported in the previous manuscript remains present. The package rebuild resolved 103 local links, and its offline verifier checked 133 file hashes and headline arithmetic. Figures 5 and 6 were visually checked after their headline changes; Figure 4 and the preferred Figure 1 option C were checked after the invented name control label update. These checks verify editorial consistency and packaging, not independent scientific validity.

The October 5 82-test same-machine reproduction and the October 15 package checks below are historical evidence, not fresh independent scientific validation. The preferred Figure 1 option C remains a labeled alternative; its promotion is outside this prose revision.

## 15 October 2026 revision

15 October 2026. This revision changes presentation, not experiments, eligibility rules, estimates, uncertainty calculations, or scientific conclusions.

## Changes

- The introduction states the research question directly and explains that facts, words, and answers can all contribute to shared graph features.
- The abstract prioritizes the original association, the stronger answer-control comparison, and selected wrong-answer evidence.
- Results now proceed from the original association to the limits of its controls, the answer-letter comparison, selected errors, equal-feature-count checks, and the failed history pilot.
- Each major comparison is explained before its numerical result. The failure section opens with the France–Berlin example.
- The prespecified average of the two answer-letter conditions remains the primary matched-choice outcome. The later direct difference test remains explicitly exploratory.
- Detailed next-token, exporter, and failure-source audits are retained as Supporting analyses A1–A3, with qualifications beside the main findings.
- The source manuscript and sharing copy use the same current figure captions. The existing figure numbering and image contents are unchanged.
- The availability statement now identifies the public review package and distinguishes it from excluded raw exports, tokenizer/model files, credentials, and reference PDFs.
- The outline and portable sharing package follow the revised manuscript. Earlier ZIPs and compiled PDFs are not overwritten.

## Boundaries retained

Three models contribute to the original samples, but only Qwen3-4B contributes to the stronger controls and selected-error diagnostic. Six country pairs, not 48 independent graphs, underpin the matched-choice comparison. The selected error comparisons share a single country pair and overlapping controls. The original Qwen3-4B extension remains incomplete at 145/147 graphs; the final history pilot passed 15/20 against a required 20/20 and produced no evaluation graphs.

Near-zero overlap differences are not equivalence tests or evidence of absent knowledge. Graph similarity, source locations, and filtering of saved graphs do not establish a causal mechanism. Next-token agreement does not independently verify complete generated answers. Independent scientific review and redistribution permissions for excluded materials remain outstanding.

The historical 82-test same-machine reproduction remains historical evidence, not a newly performed independent replication. This revision runs presentation and package-integrity checks only; it does not make model requests or rerun scientific analyses.

## Editorial verification

Nine narrative and figure-wording regression checks passed. The rebuilt package resolved all 103 checked local links. Its offline verifier checked 133 file hashes and the headline arithmetic from the included source tables. Figures, figure tables, and claims-map files are byte-identical to the previously shared version. These checks support consistency of the editorial revision, not independent scientific validation.
