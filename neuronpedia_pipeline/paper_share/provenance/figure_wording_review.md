# Wording and visual review — 6 October 2026

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
