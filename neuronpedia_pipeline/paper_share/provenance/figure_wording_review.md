# Wording and visual review — 6 October 2026

## Question-version labels, 7 November 2026

Figure 3 now distinguishes saved question-version labels from identical sentence patterns, following the approved Section 2.3 clarification. Its headline, axes, explanation, and caption refer to original/alternative-1/alternative-2 groups. Exact gold and iron prompts illustrate a same-label pair with different sentence patterns. The rebuilt 3960-by-2550 PNG was visually inspected; headings, examples, axis labels, model names, and legend remain readable without clipping. Plotted numbers are unchanged by the presentation edits. All 22 source tables, both frozen Qwen3-1.7B result files, and the other 13 figure PNGs are byte-identical to the pre-edit versions. The focused suite passed 53 tests, including an exact-prompt and numerical-fingerprint regression check. These are assistant and automated checks, not independent human review.

## Methods reference diagram, 7 November 2026

Added Figure S8, "How questions become a feature-overlap comparison," without renumbering the six main figures or seven earlier supplements. The diagram uses exact chemistry development prompts from the manifest and declared illustrative feature sets and scores. It distinguishes four prompt roles, hosted exports, factual-token and availability requirements, feature-identity deduplication, all-other-fact averaging, separate invented name controls, and fact-level summaries. Numerical feature IDs in different families or layers remain distinct; repeated token positions do not create additional identities. M_i matches the manuscript's notation.

The final 4500-by-3000 PNG was inspected visually. Text is centered in its assigned boxes, labels and arrows remain readable, the color/letter key distinguishes shared and unshared example features, and no clipping or text overlap was observed. Text-bound checks enforce a minimum nine-point label size and reserve space for the headline. The SVG retains editable text. Five new diagram tests verify exact prompts, set arithmetic, feature identity behavior, layout bounds, and caption scope.

The 165-test relevant suite passed; 36 focused tests passed again after final wording synchronization. All 13 pre-existing PNG figures and all 22 canonical plotted-data tables match the preceding review ZIP byte for byte. The current gallery has 14 figures and self-contained synchronized captions. No model requests, new empirical estimates, or changes to frozen inputs were made. This is assistant rendering and consistency verification, not independent human scientific review.

Reviewed the titles, panel headings, axes, tick labels, color scales, legends, notes, and captions of all six main figures and six supplements. Rebuilt every PNG at 300 dpi and every editable SVG from saved data. Reviewed all 12 PNGs and rechecked changed layouts after rendering repairs. No clipped or overlapping labels remained in the reviewed images.

The writing pass puts the comparison before the technical detail. Necessary measurement and statistical terms remain, with definitions in captions and the gallery introduction. It distinguishes graph-approximation errors from wrong answers, unavailable comparisons from measured zero effects, and first-token matches from complete answers. The word-overlap check says that comparable controls are missing, not that the questions share no words. Model names are written in full.

Validation:

- All 10 plotted tables shared with the previous outline figure package are byte-identical.
- Numerical fingerprints of lines, points, heatmaps, and bars remain unchanged by wording edits in all 12 figures.
- All output hashes in the figure manifest verified, with zero mismatches.
- Three presentation regression tests passed, including the check that new tick labels survive rendering.
- Original samples, exclusions, estimates, archived figure folders, compiled manuscript, and sealed release were not changed by this figure revision.

The audit of retained and revised figure text is in `wording_audit.json`. Captions and headlines are maintained in `scripts/figure_plain_language.py`; the integrated outline and current figure guide point to this package. This is an assistant review, not independent human review or a new scientific analysis.

## Follow-up explanation pass

Figure 1 now labels each model row “Models Tested:” and includes shortened examples of starting questions, reworded facts, other facts, made-up names, changed A/B answers, and selected failures with both correct-response comparisons. Gold is explicitly the chemical element. Development and pilot examples are distinguished from the test samples; the new source hashes record their saved prompt files.

Figures 2 and 3 now define their distinct subtraction baselines directly above the plots. Figure 2 includes explicitly illustrative arithmetic, not a new estimate. Figure 3 illustrates same-fact/new-wording, new-fact/same-pattern, and both-changed comparisons. Axis labels spell out both factors. Re-rendered and visually checked Figures 1–3; the final Figure 3 labels use additional line breaks and horizontal space to avoid collisions. Four presentation tests now pass. Plotted estimates remain unchanged.

## Figure 1 visual polish

Replaced centered paragraphs with left-aligned examples, bold comparison labels, small panel badges, and aligned starting-question/comparison/study-question cards. A restrained blue/green palette distinguishes labeled sections; the incorrect response is explicitly labeled and accented in rust. Kept the model labels, examples, sample sizes, and interpretation limits. Rechecked the final PNG and added a rendered-text bounds assertion for all Figure 1 panel text; no horizontal overflow remains. Four presentation tests pass. The gallery and editable SVG contain the revised design.

At the author's subsequent request, centered all text within Figure 1's cards, including multiline examples and section labels. Panel headings and model rows remain left-aligned. Rebuilt PNG/SVG and gallery, checked the rendered figure, and passed the panel-text bounds and unchanged-numerical-data assertions. Content is unchanged.

## Terminology consistency — 7 October 2026

Replaced “extra overlap” with “difference in feature overlap,” stating the subtraction in the figure definitions and captions. Weighted cosine differences remain distinct from feature-set overlap. Figure 1 asks whether questions share more features instead of introducing a metric label. Applied the same wording to the separate Figure 1 mockups, the working manuscript definition, and the integrated outline; archived figures and the compiled manuscript remain unchanged.

Visually checked the revised Figures 2, 3, 5, S2, S3 and preferred Figure 1 option C after rendering. The revised labels fit without clipping or overlap. Five presentation regression tests passed, including a check that reviewed labels and captions no longer use “extra” as a metric. This wording review does not change scientific results or constitute independent human review.

## Findings-led captions — 28 October 2026

Shortened the six main captions by consolidating repeated qualifications while retaining comparison definitions, sample sizes, plotted values, uncertainty, color/marker keys, first-token scope, and study-specific limitations. Figure 5 now states that same-fact overlap is higher when the answer letter stays the same. Figure 6 states that selected error graphs share more features with correct predictions giving the same answer. The wording reports associations without assigning a causal mechanism.

Rebuilt all 12 figures from saved estimates. All 12 plotted-data tables are byte-identical to the pre-edit copies; all 18 scientific input-file hashes are unchanged (the nineteenth source is the concurrently revised narrative outline). The builder's before/after numerical fingerprint assertions passed for every figure, and the output hashes in its manifest verified. The five figure-wording regression tests passed. Visually inspected the two changed figure headlines in the final PNGs; neither clips or overlaps the panels. Other plotted layouts are unchanged. No new model requests or scientific tests were performed. This is an assistant editorial and rendering check, not independent scientific review.

## Separate Qwen3-1.7B completion supplement, 7 November 2026

Added Supplement S7 from the completed, separately validated analysis of the `qwen17_completion_20261106` collection. Panel A distinguishes previously available from newly collected raw graphs and reports the 29 length-rejected history jobs separately from model accuracy. Panel B shows the original five chemistry facts alongside five newly analyzable geography facts. The original chemistry points and their original confidence interval are reused. History has no complete four-prompt sets and no plotted effect estimate.

The full figure build now contains six main figures and seven supplements. All 12 pre-existing plotted-data tables and all 12 pre-existing PNGs are byte-identical to the copies captured before this integration. All 18 pre-existing scientific input-file hashes remain unchanged; the narrative outline was revised, and the completed Qwen3-1.7B analysis results were added as a new source. Three S7 source tables were added. Supplement identities are now explicit S1 through S7 in the manifest, correcting the former repeated numeric field without renumbering the figures.

Seven figure-wording tests passed. All 13 figures passed the builder's numerical before/after wording checks, and all 44 output hashes verified. S7 was visually inspected: the title, panel labels, collection legend, counts, effect estimates, uncertainty bars, history-unavailable annotation, and notes fit without clipping or overlap. Collection bar labels use dark text on gray and white text on dark green. No raw graph generation or statistical analysis is performed by the plotting build. This is assistant rendering and consistency verification, not independent scientific review.

## Approved control terminology — 28 October 2026

Updated current presentation text to "invented name control" and rebuilt the figures and Figure 1 mockups. Legacy data identifiers and frozen protocols remain unchanged. Visually inspected Figure 4 and preferred Figure 1 option C: the longer labels fit without overlap or clipping. Fourteen combined manuscript and figure-wording tests pass, including current terminology and caption synchronization checks. Plot numerical fingerprints remain unchanged.

## Expanded-sample figure integration, 7 November 2026

Updated the current figure set to include the separately analyzed late Qwen3-1.7B completion wherever the collected data support the existing comparison. Figure 1 identifies the expanded chemistry/geography coverage. Figure 2 retains original panels A and B and adds panel C with reused chemistry, added geography, and their combined estimate. Figure 4 retains original panels A and B and adds the two expanded, token-type-matched controls in C. Supplements S1 through S5 add the expanded graph audit, feature-overlap checks, equal-count check, word-overlap support, and first-token audit. The expanded sample is explicitly overlapping with the original sample, not a fourth model or independent replication.

All 15 pre-update scientific source tables are byte-identical, including the original 12 tables and the three S7 tables. Eleven separately named expanded-sample tables were added. The PNGs for Figures 3, 5, 6, S6, and S7 are byte-identical to their pre-update versions. Other PNGs intentionally changed to display added data or coverage, while their original observations and estimates remain intact. The builder fingerprints original plotted numbers before and after wording edits, validates the new panel arithmetic separately, checks completed analysis/audit status and their linked hashes, and verifies retained table hashes after rendering.

Checked all eight changed figures visually, including panel headings, axis labels, counts, categorical keys, and uncertainty bars. Repaired a Figure 2C note collision and removed a divider crossing its axis label. Increased canvas width instead of reducing original panel font sizes. Figure 2C explicitly labels its narrower vertical scale. In S3 and S4, footer lines have sufficient separation and bottom margin. No remaining label clipping or overlap was observed in the final reviewed layouts. The newly added and scope-adjusted labels are included in the wording audit.

Denominators are separated: the primary expanded sample has ten evaluation questions; the matched controls use nine and ten; the file audit uses 91 graphs; and the first-token audit uses 50 available factual-question graphs, including development and partial history sets. The history collection has no complete four-role sets and therefore no new history overlap estimate. S2 refers only to the displayed feature-set overlap checks, not all graph metrics. S5 retains the original token-category counts and adds the expanded 42 whole-answer tokens, four compatible beginnings, and four different tokens without summing overlapping samples.

Ten figure-wording regression tests passed. All manifest source and output hashes verified after the final build. No hosted model requests, new inferential tests, or changes to eligibility were made by this plotting revision. This is assistant rendering and consistency verification, not independent human review.

### S4 footer padding follow-up

The original-resolution expanded S4 PNG retained the complete second footer line but left only 22 blank pixels below it. Added 0.30 inch of bottom canvas padding so the footer is comfortably visible in image viewers and document layouts. Panel dimensions, plotted coordinates, wording, and source tables are unchanged. Rebuilt the full set and rechecked source/output hashes. Eleven figure-wording tests pass, including a new assertion that padding preserves panel size and scientific values while moving the footer above the minimum bottom margin.

## Unified current-cohort presentation, 7 November 2026

At the author's request, the current paper now presents one dataset per model rather than placing older and combined Qwen3-1.7B samples side by side. Figures 2 and 4 have two panels, each with three model groups. Supplements S2, S3, and S4 have three model panels; S1 has five distinct collection/design groups; S5 has one factual-token bar per Qwen model. Figure 1 states the current 8/10/10 evaluation counts. S7 reports total Qwen3-1.7B collection and subject coverage: 40/40 chemistry, 40/40 geography, 11/40 history raw graphs, with five chemistry and five geography evaluation questions and no history estimate.

Current Qwen3-1.7B values are drawn directly from the completed saved 91-graph analysis and reconciled display audit. Its main mean is 0.0894397 (n=10); matched controls use n=9 and n=10; the raw-file audit uses 91 graphs; and the factual-token audit uses 50 available factual graphs with counts 42/4/4. Figure captions distinguish these units, retain incomplete-collection and first-token limits, and do not imply that all graph metrics agree. Chemistry domain uncertainty now uses the saved current-cohort domain interval consistently with the current Figure 2 table.

Canonical figure tables now describe the current cohort. Eleven superseded comparison-view CSVs were moved to the bounded `figure_table_archive_20261107_separate_expansion` folder; prior figure packages and frozen scientific analyses remain archived. The current tables include a 45-row inclusion audit produced from frozen saved decisions. The independent package-verification code reconciles the actual generated tables with the saved statistics and audits, including exclusion reasons and unavailable history values. No analysis was rerun and no inclusion rule changed.

Visually reviewed all nine changed figures (1, 2, 4, S1, S2, S3, S4, S5, S7). Titles, model labels, category keys, sample sizes, intervals, and unavailable-history annotations fit without observed clipping or overlap. S4 retains additional bottom padding. Figures 3, 5, 6, and S6 retain their previous PNGs and numerical data. Seven unaffected study tables remain byte-identical. Eleven figure-wording tests pass; completed-analysis assertions, arithmetic checks, per-figure wording fingerprints, and input/output hash verification pass. This is assistant rendering and consistency verification, not independent human scientific review.

Final verification checked 51 output hashes, 22 input hashes, and seven helper hashes. The four unchanged PNGs were compared byte-for-byte with `attribution_graph_paper_review_20261107_methods_discussion.zip`, not only with a transient working copy. The frozen source analysis and display-audit JSONs retain their previously verified hashes. The current folder contains 22 canonical CSV tables and no superseded `_expanded.csv` tables.
