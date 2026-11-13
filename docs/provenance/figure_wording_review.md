# Approved presentation review

## Percentage display update, 13 November 2026

Jaccard feature overlap and word overlap now display as percentages. Differences and their intervals display in percentage points. Tick labels and numerical annotations are multiplied by 100; plotted source coordinates and saved analysis tables remain unchanged. Cosine similarity, p-values, counts, and existing reconstruction-error percentages retain their original units.

The updated Figures 2 and 4 and Supplements S4, S7, S8, and S10 were inspected as PNGs for the new units, annotations, color scales, and layout. All 16 regenerated figures passed the 180-mm width, minimum 7-point text, and canvas-boundary checks. Regression tests verify exact percentage conversion, native cosine units, unchanged lexical thresholds, and unmodified source-table hashes. This is a presentation check, not a new scientific analysis or independent review.

## Original presentation review

All six main figures and ten supplements were inspected as rendered PNGs in the author workspace. This is an assistant-assisted presentation check, not independent scientific review.

The review checked titles, panel order, labels, legends, color-scale definitions, visible missing-data notices, sample counts, and consistency with the saved tables. It corrected overlapping history headings, crowded audit labels, long titles, and colorbar clipping. Figure 1 uses the final 8/10/12 counts and includes history; the descriptive question-version comparison is Supplement S10. Current captions describe the rebuilt panels, not removed insets. Exact history prompts remain in Figure 6; Figure 1 labels its examples as abridged.

Automated checks use the 300-dpi rendering canvas. All 16 figures are 180 mm wide, all visible labels are at least 7 points at that size, and no visible text extends beyond the canvas. Editable SVG text and PNG exports are retained. Source CSVs are copied byte-for-byte; unrounded saved values determine plotted points and intervals. The primary interval is read from the saved analysis JSON, and the crossed expected-token counts are read from the saved audit. No new statistical estimates or model outputs were generated.

The figure manifest records source and output hashes and per-figure source-table mappings. Original filenames in the derived-data archive remain stable despite the new presentation numbering. Supplement S6 includes both sensitivity tables and its statistics record. Missing comparisons remain unavailable, not zero effects; dependent history and selected-error comparisons remain descriptive. Final typography and pagination should be checked again after a journal format is selected.
