# Cross-Domain Website Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Bring `docs/cross-domain-circuits.html` to submission-ready public-release quality with high-impact figures, canonical academic structure, three-touch reinforcement of named concepts, and full Neuronpedia interactive coverage.

**Architecture:** Pure static HTML edits on an existing Bulma 0.9.4 scaffold + matplotlib SVG re-export + 2 redesigned hero matplotlib figures + 1 new hand-crafted inline SVG schematic. No new runtime dependencies. Each milestone produces a committable unit so work can pause and resume across sessions.

**Tech Stack:** HTML5, Bulma 0.9.4, DM Sans / DM Mono, Font Awesome 6.5.1, Academicons; matplotlib for data plots (SVG output); hand-written inline SVG for one schematic.

**Source design:** `docs/plans/2026-05-23-cross-domain-website-upgrade-design.md`

**Target file:** `docs/cross-domain-circuits.html` (949 lines as of `a95e9ad`)

---

## Resume protocol

If returning to this plan mid-stream:

1. Run `git log --oneline -10 docs/cross-domain-circuits.html docs/plans/` to see last commit
2. Read the most recent milestone's "Verification checkpoint" section
3. Run the checkpoint command — it tells you exactly what state the page should be in
4. Resume at the next un-committed milestone

Milestones are independent enough that you can ship some without others (e.g., SVG export milestone alone is a complete, committable improvement).

---

## Milestone A — Section restructure to canonical order (~1 hr)

**Why first:** All later content edits reference anchor IDs from the restructured page. Doing this first prevents rework.

**Files:**
- Modify: `docs/cross-domain-circuits.html` (lines 252–933)
- Create: `docs/cross-domain-circuits.html.bak` (one-time safety backup before any edits)

### Task A1: Create safety backup

**Step 1:** Copy the current file as a one-time backup
```bash
cp ../docs/cross-domain-circuits.html ../docs/cross-domain-circuits.html.bak
```

**Step 2:** Verify backup matches original
```bash
diff ../docs/cross-domain-circuits.html ../docs/cross-domain-circuits.html.bak
```
Expected: no output (files identical).

**Step 3:** Add `.bak` to `.gitignore` if not already
```bash
grep -q "*.bak" ../.gitignore || echo "*.bak" >> ../.gitignore
```

**Step 4:** Commit gitignore if changed
```bash
git -C .. add .gitignore && git -C .. commit -m "chore: ignore .bak safety backups" || echo "no change"
```

### Task A2: Add section IDs to existing H2 blocks (zero structural change yet)

**Why:** Adding stable `id` attributes BEFORE moving content lets us track which content goes where.

**Step 1:** For each `<section class="section">` block currently at lines 310, 330, 386, 461, 535, 578, 636, 671, 709, 775, 809, 830, 852, 895, 919 — add an explicit `id` attribute mapped to the new canonical structure:

| Current H2 | Current line | Add `id` |
|------------|--------------|----------|
| Abstract | 310 | `id="abstract"` |
| Key Findings | 330 | `id="key-findings"` |
| Method: Traceback Graphing | 386 | `id="methods"` |
| 1. Architecture Dominates Domain | 461 | `id="results-architecture"` |
| 2. The Bottleneck Tax | 535 | `id="results-bottleneck-tax"` |
| 3. Universal Bottleneck Features | 578 | `id="results-universal"` |
| 4. Output Convergence vs Path Divergence | 636 | `id="results-output-convergence"` |
| 5. Circuit Redundancy | 671 | `id="results-redundancy"` |
| 6. Causal Steering — Three-Tier Dissociation | 709 | `id="results-steering"` |
| 7. Format Variation | 775 | `id="results-format"` |
| Limitations | 809 | `id="limitations"` |
| Conclusion | 830 | `id="conclusions"` |
| Supplementary Materials | 852 | (already has `id="supplementary"`) |
| References | 895 | `id="references"` |
| BibTeX | 919 | `id="bibtex"` |

Use Edit tool with `replace_all=false` per section. Pattern:

```
old: <section class="section" style="padding-top:1rem;">
new: <section class="section" style="padding-top:1rem;" id="results-bottleneck-tax">
```

Note: there are multiple sections with identical opening tags — make `old_string` unique by including 2–3 surrounding context lines (e.g., the `<h2>` text on the next non-blank line).

**Step 2:** Verify all 14 sections now have unique IDs
```bash
grep -c 'id="' ../docs/cross-domain-circuits.html
```
Expected: ≥ 15 (the hero section may also have an id).

**Step 3:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: add stable section IDs for canonical-structure migration"
```

### Task A3: Wrap the 7 numbered findings into a single "3. Results" H2 section

The current 7 numbered sections (lines 461, 535, 578, 636, 671, 709, 775) need to become H3 subsections inside a wrapping H2 "3. Results" section.

**Step 1:** Insert a new H2 "3. Results" opening block immediately before line 461 (current "1. Architecture Dominates Domain" section):

```html
<section class="section" style="padding-top:1rem;" id="results">
  <div class="container is-max-desktop">
    <div class="content">
      <h2 class="title is-4">3. Results</h2>
      <p class="subtitle is-6" style="color:var(--text-muted);">Seven findings, in narrative order: from architecture-level structure (§3.1–§3.2) to specific feature behavior (§3.3–§3.4) to mechanistic interpretation (§3.5–§3.6) to causal validation (§3.7–§3.8).</p>
```

**Step 2:** For each of the 7 finding sections, perform two transformations:
- Change the outer `<section class="section" ...>` opening to `<div class="results-subsection">`
- Change matching `</section>` close to `</div>`
- Change `<h2 class="title is-4">N. Finding Title</h2>` → `<h3 class="title is-5">3.{N+1}. Finding Title</h3>` (Results is §3, so finding 1 becomes §3.2 if §3.1 is within-domain convergence; adjust per design doc table in §4.1)

| Current title | New title |
|---------------|-----------|
| (new) Within-Category Circuit Convergence | 3.1 Within-domain convergence |
| 1. Architecture Dominates Domain | 3.2 Architecture dominance |
| 3. Universal Bottleneck Features | 3.3 Universal bottlenecks |
| 4. Output Convergence vs Path Divergence | 3.4 Output convergence |
| 2. The Bottleneck Tax | 3.5 The bottleneck tax |
| 5. Circuit Redundancy | 3.6 Circuit redundancy |
| 6. Causal Steering — Three-Tier Dissociation | 3.7 Causal steering |
| 7. Format Variation | 3.8 Format variation |

Note the **reorder**: the bottleneck tax moves from current §2 to §3.5 (logically after universal bottlenecks). Verify against design doc §4.1.

**Step 3:** Add a closing `</div></div></section>` after the last finding (current line 804) to close the wrapping Results section.

**Step 4:** Add a "3.1 Within-domain convergence" stub H3 at the top of the Results section — content is currently embedded under "1. Architecture" but the design assigns it its own subsection. Pull the relevant paragraphs out.

**Step 5:** Test the page loads cleanly
```bash
python -c "import bs4, pathlib; bs4.BeautifulSoup(pathlib.Path('../docs/cross-domain-circuits.html').read_text(encoding='utf-8'), 'html.parser')" && echo "HTML parses OK"
```
Expected: `HTML parses OK`

**Step 6:** Open in browser, verify:
- Title still renders
- Theme toggle still works
- All 7 findings appear as H3 under "3. Results"
- No visual breakage

**Step 7:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: wrap 7 findings as H3 subsections under canonical \"3. Results\""
```

### Task A4: Renumber the remaining H2s to canonical order

**Step 1:** Rename remaining H2 titles:
- "Method: Traceback Graphing" → "2. Methodology"
- "Limitations" → "5. Limitations"
- "Conclusion" → "6. Conclusions"

**Step 2:** Insert a new "1. Introduction" H2 section after "Key Findings" and before "2. Methodology". Use H3 subsections 1.1 Motivation, 1.2 Research Questions, 1.3 Contributions, mirroring the markdown paper. Source content from `docs/papers/CROSS_DOMAIN_CIRCUIT_PAPER.md` lines 25–55.

**Step 3:** Insert a new "4. Discussion" H2 section between "3. Results" and "5. Limitations". Use H3 subsections 4.1 Architecture vs domain, 4.2 Universal features as routing, 4.3 Bottleneck tax interpretation, 4.4 Three-tier dissociation. Source content from `docs/papers/CROSS_DOMAIN_CIRCUIT_PAPER.md` §6.

**Step 4:** Verify section order with one command:
```bash
grep -n '<h2 class="title is-4">' ../docs/cross-domain-circuits.html
```
Expected sequence:
1. Abstract
2. Key Findings
3. 1. Introduction
4. 2. Methodology
5. 3. Results
6. 4. Discussion
7. 5. Limitations
8. 6. Conclusions
9. Supplementary Materials
10. References
11. BibTeX

**Step 5:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: complete canonical section structure (1.Intro - 6.Conclusions)"
```

### Verification checkpoint — Milestone A

Run:
```bash
grep -c '<h2 class="title is-4">' ../docs/cross-domain-circuits.html
```
Expected: `11`

Run:
```bash
python -c "import bs4, pathlib; soup = bs4.BeautifulSoup(pathlib.Path('../docs/cross-domain-circuits.html').read_text(encoding='utf-8'), 'html.parser'); h2s = [h.get_text(strip=True) for h in soup.find_all('h2')]; print('\n'.join(h2s))"
```
Expected output order matches the table above.

If both pass, Milestone A is complete and safely committed.

---

## Milestone B — SVG export of 5 existing figures (~30 min)

**Why:** Fast win. Re-running matplotlib with `.svg` extension produces scalable versions of every data plot without changing the data.

**Files:**
- Modify: `scripts/stage_2_layer_energy_figures.py` (figures 18, 19, 20)
- Modify: `scripts/stage_2_paper_figures.py` (figures 2, 3, 10, 41) — verify path
- Create: `data/stage_2_figures/*.svg` (5 new files)
- Modify: `docs/cross-domain-circuits.html` (5 `<img>` `src=` attributes)

### Task B1: Patch matplotlib scripts to also export SVG

**Step 1:** For each `plt.savefig(..., 'figXX.png', ...)` call, add a sibling line for SVG:

In `scripts/stage_2_layer_energy_figures.py` line 244:
```python
# old:
plt.savefig(OUTPUT_DIR / 'fig18_layer_confidence_correlation.png', bbox_inches='tight')
# new:
plt.savefig(OUTPUT_DIR / 'fig18_layer_confidence_correlation.png', bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'fig18_layer_confidence_correlation.svg', bbox_inches='tight')
```

Repeat for lines 302 (fig19), 382 (fig20).

**Step 2:** Locate which script generates fig2, fig3, fig10, fig41
```bash
grep -l "fig2_\|fig3_\|fig10_\|fig41_" scripts/
```

**Step 3:** Patch each found script the same way (add `.svg` sibling savefig calls).

**Step 4:** Run the patched scripts
```bash
python scripts/stage_2_layer_energy_figures.py
python scripts/stage_2_paper_figures.py  # or whichever scripts handle the other 4
```

**Step 5:** Verify 5 new SVG files exist
```bash
ls data/stage_2_figures/fig{2,3,10,18,19,20,41}*.svg
```
Expected: 7 SVG files listed.

**Step 6:** Commit (figures, not HTML yet)
```bash
git add scripts/stage_2_layer_energy_figures.py scripts/stage_2_paper_figures.py data/stage_2_figures/*.svg
git commit -m "figures: add SVG sibling exports for paper figures 2, 3, 10, 18, 19, 20, 41"
```

### Task B2: Repoint HTML `<img>` tags to SVG

**Step 1:** For each of the 9 current `<img src="...png" ...>` in `docs/cross-domain-circuits.html`, change `.png` → `.svg` IF an SVG version exists. Use Edit `replace_all=false` per image.

Lines to edit per earlier inspection:
- 472 (fig20_profile_similarity.png → .svg)
- 485 (fig19_cumulative_energy.png → .svg)
- 506 (fig3_bottleneck_depth.png → .svg)
- 525 (fig2_jaccard_heatmaps.png → .svg)
- 560 (fig18_layer_confidence_correlation.png → .svg)
- 659 (fig10_output_path.png → .svg)
- 697 (fig41_reduction_breakdown.png → .svg)

Leave the steering figures (lines 727, 740) as PNG for now — they'll be replaced wholesale in Milestone G.

**Step 2:** Open the page in browser, verify all figures still display.

**Step 3:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: repoint 7 figures to SVG for scalable rendering"
```

### Verification checkpoint — Milestone B

Run:
```bash
grep -c "\.svg\"" ../docs/cross-domain-circuits.html
```
Expected: `≥ 7`

Open `../docs/cross-domain-circuits.html` in browser. Zoom to 200%. All figures should remain crisp.

---

## Milestone C — Hero figure F1: Bottleneck tax (~1.5 hr)

**Why:** The single most important figure. Currently a generic per-layer correlation scatter; redesign as an annotated 2-panel hero.

**Files:**
- Create: `scripts/fig_bottleneck_tax_hero.py`
- Create: `data/stage_2_figures/fig_bottleneck_tax_hero.svg`
- Modify: `docs/cross-domain-circuits.html` (replace F1 `<img>` reference)

### Task C1: Write the hero figure script

**Step 1:** Create `scripts/fig_bottleneck_tax_hero.py` with the following structure:

```python
#!/usr/bin/env python3
"""Hero figure F1: The bottleneck tax.

Two-panel annotated plot. Left: per-layer Spearman correlation between
activation energy fraction and output confidence across 30 Gemma circuits,
with L6 negative dip highlighted. Right: scatter of L6 energy fraction vs
output probability for the 30 circuits, with regression line.
"""
import json
import sys, io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = Path(__file__).parent.parent
DATA_FILE = BASE / 'data' / 'stage_2_analysis' / 'per_layer_correlations.json'
OUTPUT_DIR = BASE / 'data' / 'stage_2_figures'

# theme tokens (match site CSS)
COLOR_BOTTLENECK = '#e67e22'   # orange — phase 1 / bottleneck
COLOR_POSTBOTTLE = '#8854d0'   # purple — post-bottleneck
COLOR_NEUTRAL    = '#8b949e'
COLOR_TEXT       = '#1a1a1a'
COLOR_AXIS       = '#555555'

plt.rcParams.update({
    'font.family': 'DM Sans, Helvetica, Arial, sans-serif',
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': COLOR_AXIS,
    'axes.labelcolor': COLOR_TEXT,
    'xtick.color': COLOR_AXIS,
    'ytick.color': COLOR_AXIS,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.transparent': True,
})

def main():
    # ... two-panel layout, left=correlation-per-layer with L6 annotation,
    # right=L6 energy fraction vs output prob scatter with regression line ...
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(11, 4.5))
    # Left panel
    # ...
    # Right panel
    # ...
    fig.suptitle('The bottleneck tax', fontsize=14, fontweight='bold', y=1.02)
    plt.savefig(OUTPUT_DIR / 'fig_bottleneck_tax_hero.svg', bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig_bottleneck_tax_hero.png', bbox_inches='tight')
    print('  [OK] fig_bottleneck_tax_hero.svg + .png')

if __name__ == '__main__':
    main()
```

**Step 2:** Inspect what data is available
```bash
ls data/stage_2_analysis/ | grep -i "layer\|correlation\|confidence"
```
The script needs per-layer correlation values for Gemma (we already have r = −0.684 for L6, etc., in §5.5.3). If a JSON dump doesn't exist, generate one from the existing analysis pipeline.

**Step 3:** Fill in the actual plot code with these specific design choices:
- **Left panel:** bar chart of r values for layers 0–25, bar colors driven by sign (orange for negative ≤ −0.3, purple for positive ≥ +0.3, grey otherwise). Vertical dashed line at L6 with "L6 — bottleneck" annotation. Horizontal guides at ±0.6 (Bonferroni threshold).
- **Right panel:** scatter of 30 Gemma circuits (x = L6 energy fraction, y = output probability), regression line, r and p values in a text box.
- Subtitle in subdued color: "More L6 activation → lower output confidence"

**Step 4:** Run the script
```bash
python scripts/fig_bottleneck_tax_hero.py
```
Expected output: `[OK] fig_bottleneck_tax_hero.svg + .png`

**Step 5:** Open SVG in browser and verify rendering. Check:
- Title visible and bold
- Both panels labeled clearly
- L6 annotation present and unambiguous
- Numbers readable at default zoom

If anything looks off, iterate. **Do not commit until the figure stands on its own as a "3-second punchline."**

**Step 6:** Commit
```bash
git add scripts/fig_bottleneck_tax_hero.py data/stage_2_figures/fig_bottleneck_tax_hero.svg data/stage_2_figures/fig_bottleneck_tax_hero.png
git commit -m "figures: add hero figure F1 (bottleneck tax) — 2-panel annotated SVG"
```

### Task C2: Wire F1 into the HTML

**Step 1:** In `docs/cross-domain-circuits.html`, in the §3.5 "The bottleneck tax" subsection (formerly line 560), replace:
```html
<img src="../neuronpedia_pipeline/data/stage_2_figures/fig18_layer_confidence_correlation.svg" alt="Per-layer energy-confidence correlation" class="paper-figure">
```
with:
```html
<img src="../neuronpedia_pipeline/data/stage_2_figures/fig_bottleneck_tax_hero.svg" alt="Bottleneck tax — two-panel annotated hero figure" class="paper-figure paper-figure-hero" id="fig-bottleneck-tax">
```

**Step 2:** Replace the figure caption with the punchline-led version from design doc §4.3.1 Touch 3:
> **Figure 1: The bottleneck tax.** Per-layer Spearman correlation between activation energy fraction and output confidence across 30 Gemma circuits. **Bottleneck layer L6 shows a strong negative correlation (r = −0.684, p < 0.0001):** circuits concentrating more activation at L6 produce *less* confident predictions. Post-bottleneck layers L13, L16 reverse the sign (r ≈ +0.60), consistent with information bottleneck framing — heavier compression at intermediate layers reduces information available for downstream evidence accumulation.

**Step 3:** Open HTML in browser, verify figure displays and caption renders.

**Step 4:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: replace fig18 with hero figure F1 (bottleneck tax) + punchline caption"
```

### Verification checkpoint — Milestone C

Run:
```bash
grep "fig_bottleneck_tax_hero" ../docs/cross-domain-circuits.html
```
Expected: at least 1 match.

Open the page. The bottleneck tax figure should be visually distinguishable from the other figures (intentionally larger / more prominent / clearly annotated).

---

## Milestone D — Hero figure F2: Architecture dominance (~1.5 hr)

**Files:**
- Create: `scripts/fig_architecture_dominance_hero.py`
- Create: `data/stage_2_figures/fig_architecture_dominance_hero.svg`
- Modify: `docs/cross-domain-circuits.html` (replace F2/F3 image references)

### Task D1: Write the script

Same structure as Task C1. Two-panel:
- **Left panel:** Cumulative energy curves — Gemma front-loading (54% by L12) vs Qwen back-loading (31% by L17). Two stacked area plots or line plots with shaded regions; clear crossover annotation.
- **Right panel:** Energy profile cosine similarity matrix (30 × 30 circuits, color-coded by within-model 0.978 block vs between-model 0.696 off-diagonal). Annotate the two block means in the figure.

**Step 1:** Create the script following Task C1 pattern. Use the data already produced by `stage_2_layer_energy_figures.py` (figures 19 and 20).

**Step 2:** Run, verify SVG renders clean.

**Step 3:** Commit
```bash
git add scripts/fig_architecture_dominance_hero.py data/stage_2_figures/fig_architecture_dominance_hero.*
git commit -m "figures: add hero figure F2 (architecture dominance) — combined 2-panel SVG"
```

### Task D2: Wire F2 into HTML

**Step 1:** In §3.2 of the HTML, replace the two current figures (fig19 cumulative, fig20 similarity) with one F2 reference. Punchline caption from design doc §4.3.3 Touch 3.

**Step 2:** Verify the page still flows narratively (don't end up with §3.2 totally figure-less or with a redundant figure).

**Step 3:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: replace fig19+fig20 with hero figure F2 (architecture dominance) + punchline caption"
```

### Verification checkpoint — Milestone D

```bash
grep -c "fig_architecture_dominance_hero\|fig_bottleneck_tax_hero" ../docs/cross-domain-circuits.html
```
Expected: `≥ 2`

---

## Milestone E — New schematic F8: Three-tier dissociation (~1 hr)

**Files:**
- Modify: `docs/cross-domain-circuits.html` (insert inline SVG into §3.7 / §4.4)

### Task E1: Hand-craft inline SVG schematic

**Step 1:** Open the upstream `docs/index.html` and inspect Olalekan's phase-flow SVG for style reference (the three-box vertical flow with arrows).

**Step 2:** Draft the schematic. Concept: three horizontal tiers, each with a label, an effect metric, and an example.

```html
<figure id="fig-three-tier" class="paper-figure-svg">
  <svg viewBox="0 0 800 360" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:auto;">
    <!-- TIER 1 -->
    <rect x="40" y="20" width="720" height="90" rx="8"
          fill="var(--phase1-bg)" stroke="var(--svg-box-orange-stroke)" stroke-width="1.5"/>
    <text x="60" y="50" fill="var(--text)" font-size="16" font-weight="700">Tier 1 · Essential-pathway topology</text>
    <text x="60" y="75" fill="var(--text-muted)" font-size="12">Governs distributional perturbation strength · mean KL = 1.448</text>
    <text x="60" y="95" fill="var(--text-muted)" font-size="11" font-style="italic">Example: L25_F50014975 amplification → KL = 12.72 ("Tokyo")</text>

    <!-- TIER 2 -->
    <rect x="40" y="135" width="720" height="90" rx="8"
          fill="var(--phase2-bg)" stroke="var(--svg-box-blue-stroke)" stroke-width="1.5"/>
    <text x="60" y="165" fill="var(--text)" font-size="16" font-weight="700">Tier 2 · Cross-circuit frequency</text>
    <text x="60" y="190" fill="var(--text-muted)" font-size="12">Statistically common · causally weak · does NOT predict steering effect</text>
    <text x="60" y="210" fill="var(--text-muted)" font-size="11" font-style="italic">Example: L2_F25751073 (highest frequency, 11 circuits) → 0% text changes</text>

    <!-- TIER 3 -->
    <rect x="40" y="250" width="720" height="90" rx="8"
          fill="var(--phase3-bg)" stroke="var(--svg-bar-purple)" stroke-width="1.5"/>
    <text x="60" y="280" fill="var(--text)" font-size="16" font-weight="700">Tier 3 · Output determinism by domain</text>
    <text x="60" y="305" fill="var(--text-muted)" font-size="12">Governs text-level susceptibility · chemistry 0% · geography 20% · history 60%</text>
    <text x="60" y="325" fill="var(--text-muted)" font-size="11" font-style="italic">Attribution graphs do NOT capture this tier</text>
  </svg>
  <figcaption>
    <strong>Figure 8: The three-tier dissociation.</strong> Three independent dimensions of feature importance, none of which alone predicts behavior. Tier 1 governs how strongly a steering perturbation alters the next-token distribution. Tier 2 reflects statistical co-occurrence, not causation. Tier 3 — output entropy by knowledge domain — governs whether perturbation survives 94% circuit redundancy to flip the argmax token.
  </figcaption>
</figure>
```

**Step 3:** Insert this block inside §3.7 (Causal Steering) at the end of the steering results, just before the closing `</div></div></section>`.

**Step 4:** Open the page. Verify:
- All three tier boxes render with correct phase colors
- Text is readable in both light and dark theme
- Figure scales with browser width

**Step 5:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: add new schematic F8 (three-tier dissociation) as inline SVG in section 3.7"
```

### Verification checkpoint — Milestone E

```bash
grep -c "fig-three-tier" ../docs/cross-domain-circuits.html
```
Expected: `≥ 1`

Theme toggle test: switch to light mode, then dark mode. Schematic should remain legible in both.

---

## Milestone F — Three-touch reinforcement for 4 named concepts (~45 min)

**Files:**
- Modify: `docs/cross-domain-circuits.html` (Abstract block; Key Findings block; figure captions already done in Milestones C/D/E)

### Task F1: Revise the Abstract

**Step 1:** Locate the Abstract block (lines 310–325, post-restructure may differ — find by `id="abstract"`).

**Step 2:** Apply the four Abstract revisions from design doc §4.3 Touch 1 for: bottleneck tax, three-tier dissociation, architecture dominance, universal bottleneck features. Each is a precise one-line edit to add an em-dash inline gloss the first time the term appears.

**Step 3:** Run a sanity check
```bash
grep -E "bottleneck tax|three-tier dissociation|architecture dominance|universal bottleneck" ../docs/cross-domain-circuits.html | head -10
```
Should appear in Abstract block.

**Step 4:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: define 4 named concepts inline on first Abstract mention"
```

### Task F2: Expand the Key Findings callout

**Step 1:** Locate the Key Findings block (`id="key-findings"`).

**Step 2:** Replace existing bullet list with a structured 4-bullet callout, one per named concept, each with "[Jump to §X →]" anchor link. Source from design doc §4.3 Touch 2.

```html
<ul class="key-findings-list">
  <li><strong>Architecture dominance.</strong> Across 60 circuits, model architecture explains ~14× more variance in layer-energy profiles than knowledge domain. Gemma front-loads 54% of energy into early layers; Qwen back-loads with 31%. <a href="#results-architecture">[Jump to §3.2 →]</a></li>
  <li><strong>Universal bottleneck features.</strong> Six Gemma and 15 Qwen features participate in circuits across chemistry, geography, AND history. Zero cross-architecture overlap. Function: routing infrastructure, not knowledge stores. <a href="#results-universal">[Jump to §3.3 →]</a></li>
  <li><strong>The bottleneck tax.</strong> More activation at Gemma's bottleneck layer L6 predicts <em>worse</em> output confidence (r = −0.684, Bonferroni-significant). Consistent with information bottleneck theory. <a href="#results-bottleneck-tax">[Jump to §3.5 →]</a></li>
  <li><strong>The three-tier dissociation.</strong> 80 steering experiments reveal that pathway topology, cross-circuit frequency, and text-level behavior each measure different things. Essential-pathway features perturb distributions strongest (KL = 1.448) but 94% circuit redundancy absorbs them. <a href="#results-steering">[Jump to §3.7 →]</a></li>
</ul>
```

**Step 3:** Add accompanying CSS in the existing `<style>` block:
```css
.key-findings-list { list-style: none; padding-left: 0; }
.key-findings-list li {
  padding: 0.75em 1em;
  margin-bottom: 0.5em;
  background: var(--finding-bg);
  border-left: 3px solid var(--finding-bdr);
  border-radius: 4px;
}
.key-findings-list a { color: var(--link); font-weight: 500; }
```

**Step 4:** Open the page, verify all 4 anchor links work (click each, browser should scroll to the target section).

**Step 5:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: expand Key Findings into 4 named-concept callouts with section anchors"
```

### Verification checkpoint — Milestone F

Click each "Jump to" link in the browser. Verify all 4 navigate correctly.

---

## Milestone G — Neuronpedia link sweep + Glossary deep-links (~1.25 hr)

**Files:**
- Modify: `docs/cross-domain-circuits.html`
- Create: `docs/glossary.html` (if not already present — convert GLOSSARY.md or link to PDF)

### Task G1: Build Neuronpedia URL list

**Step 1:** Compile list of every named feature in the HTML body. Use:
```bash
grep -oE "L[0-9]+_F[0-9]+" ../docs/cross-domain-circuits.html | sort -u
```
Expected: ~25–35 unique feature IDs.

**Step 2:** Build URL mapping. Format:
- Gemma: `https://neuronpedia.org/gemma-2-2b/{layer}-gemmascope-transcoder-16k/{feature_idx_mod_16384}`
- Qwen: `https://neuronpedia.org/qwen3-4b/{layer}-...` (verify SAE slug name from existing 3 links)

Save to a file `data/neuronpedia_feature_urls.json` for reuse.

### Task G2: Apply hyperlinks

**Step 1:** For each `L{n}_F{m}` occurrence in the body, wrap in `<a href="...neuronpedia.org/..." target="_blank">...</a>`.

This can be scripted — write a small Python utility that reads `neuronpedia_feature_urls.json` and does the substitution outside code blocks:

```python
import re, json, pathlib
urls = json.loads(pathlib.Path('data/neuronpedia_feature_urls.json').read_text())
html = pathlib.Path('../docs/cross-domain-circuits.html').read_text(encoding='utf-8')
# preserve existing <a> wraps + code blocks
# ... safe substitution logic ...
```

**Step 2:** Run the utility. Verify with:
```bash
grep -c "neuronpedia.org" ../docs/cross-domain-circuits.html
```
Expected: ≥ 30.

**Step 3:** Open page, click 3 random Neuronpedia links, verify they load the correct feature dashboards.

**Step 4:** Commit
```bash
git add docs/cross-domain-circuits.html data/neuronpedia_feature_urls.json
git commit -m "html: hyperlink all named feature IDs to Neuronpedia dashboards"
```

### Task G3: Glossary deep-links

**Step 1:** Add CSS for ⓘ icons:
```css
.gloss-link {
  font-size: 0.7em;
  vertical-align: super;
  color: var(--text-muted);
  text-decoration: none;
  margin-left: 2px;
}
.gloss-link:hover { color: var(--link); }
```

**Step 2:** Decide glossary destination — either:
- Convert `docs/papers/GLOSSARY.md` to `docs/glossary.html` (use existing PDF generator pattern, or pandoc)
- Link to the PDF directly: `pdf/GLOSSARY.pdf#bottleneck-tax`

Recommendation: HTML conversion for in-browser anchor jumps. Use a quick markdown-to-HTML conversion.

**Step 3:** On first body mention of each of these 8 concepts, append `<a href="glossary.html#anchor" class="gloss-link">ⓘ</a>`:
- bottleneck tax
- three-tier dissociation
- architecture dominance
- universal bottleneck features
- activation energy
- Jaccard similarity
- traceback graphing
- direct logit attribution

**Step 4:** Commit
```bash
git add docs/cross-domain-circuits.html docs/glossary.html
git commit -m "html: add glossary deep-link icons on first body mention of 8 concepts"
```

### Verification checkpoint — Milestone G

```bash
grep -c "neuronpedia.org" ../docs/cross-domain-circuits.html
grep -c "gloss-link" ../docs/cross-domain-circuits.html
```
Expected: ≥ 30 Neuronpedia links and ≥ 8 glossary icons.

---

## Milestone H — Author LinkedIn + project-page badge row (~15 min)

### Task H1: Add Joseph's LinkedIn

**Step 1:** Confirm LinkedIn URL with user (if still unknown, leave placeholder `[JOSEPH_LINKEDIN_URL]`).

**Step 2:** Edit the `author-block` for Joseph Lawrence to wrap in an `<a href="...">` tag matching the Konstantinos pattern.

**Step 3:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: add Joseph's LinkedIn URL to author block"
```

### Task H2: Add project-page badge row

**Step 1:** Add HTML immediately below the title block, above the authors:

```html
<div class="paper-badges" style="display:flex; gap:0.75em; justify-content:center; flex-wrap:wrap; margin: 1em 0;">
  <a href="pdf/CROSS_DOMAIN_CIRCUIT_PAPER.pdf" class="badge"><i class="fas fa-file-pdf"></i> Paper (PDF)</a>
  <a href="glossary.html" class="badge"><i class="fas fa-book"></i> Glossary</a>
  <a href="https://github.com/J-Lawrence10/autocircuit" class="badge"><i class="fab fa-github"></i> Code</a>
  <a href="https://neuronpedia.org/" class="badge"><i class="fas fa-link"></i> Neuronpedia</a>
</div>
```

Plus CSS:
```css
.badge {
  display: inline-flex; align-items: center; gap: 0.4em;
  padding: 0.45em 0.9em; border-radius: 6px;
  background: var(--bg2); color: var(--text);
  text-decoration: none; font-size: 0.9em; font-weight: 500;
  border: 1px solid var(--border);
  transition: background 0.15s;
}
.badge:hover { background: var(--bg3); color: var(--link); }
```

**Step 2:** Commit
```bash
git add docs/cross-domain-circuits.html
git commit -m "html: add project-page badge row (Paper, Glossary, Code, Neuronpedia)"
```

### Verification checkpoint — Milestone H

Open the page. Hero section should now display the badge row directly below the title.

---

## Milestone I — Final QA pass (~30 min)

### Task I1: Manual browser QA

**Step 1:** Open in Chrome at default zoom. Verify:
- [ ] Title and author block render
- [ ] Badge row displays correctly
- [ ] Theme toggle works (try light → dark → light)
- [ ] All 8 figures display
- [ ] All Key Findings "[Jump to]" links work
- [ ] At least 3 Neuronpedia links work
- [ ] Glossary ⓘ icons hover and link correctly

**Step 2:** Open at mobile viewport (DevTools > Toggle device toolbar > iPhone 12). Verify:
- [ ] Layout doesn't horizontally overflow
- [ ] Figures scale down
- [ ] Badge row wraps cleanly
- [ ] Text remains readable

**Step 3:** Open in Firefox. Same checks. Note any browser-specific issues.

### Task I2: Automated link check

**Step 1:** Install link checker (one-time):
```bash
pip install linkchecker
```

**Step 2:** Run:
```bash
linkchecker --no-warnings ../docs/cross-domain-circuits.html
```

Fix any broken links. Common issues: dead Neuronpedia URLs (re-derive), missing `glossary.html` anchors.

**Step 3:** Re-run until clean.

### Task I3: HTML lint

**Step 1:**
```bash
python -c "import bs4, pathlib; soup = bs4.BeautifulSoup(pathlib.Path('../docs/cross-domain-circuits.html').read_text(encoding='utf-8'), 'html.parser'); print(soup.prettify()[:200])"
```
Expected: no parser errors.

**Step 2:** Check that PDF is up to date with any underlying MD changes:
```bash
python scripts/generate_pdfs.py 2>&1 | tail -5
```

**Step 3:** Commit any regenerated PDF + final HTML polish:
```bash
git add docs/papers/pdf/ docs/cross-domain-circuits.html
git commit -m "qa: regenerate PDF and final HTML polish after website upgrade"
```

### Final verification checkpoint — Milestone I

```bash
git log --oneline submission..HEAD | wc -l
```
Expected: ~10–15 commits (one per task), all on `submission` branch.

```bash
git log --oneline -20
```
Sequence should show milestones A → I in commit messages.

If all checks pass, the upgrade is complete and ready to push.

---

## Final step — push to origin

When user explicitly approves push:
```bash
git push origin submission
```

Verify on GitHub that the `submission` branch reflects all milestones.

---

## Recovery from interruption

| If interrupted during… | Resume by… |
|------------------------|------------|
| Milestone A (restructure) | Check `git log` — if Task A4 committed, proceed to B; otherwise re-run Task A3 verification |
| Milestone B (SVG export) | Re-run `python scripts/stage_2_*.py` ; SVGs are idempotent |
| Milestone C/D (hero figs) | Each script is self-contained; safe to re-run |
| Milestone E (schematic) | HTML edit only; use `git diff` to see partial state |
| Milestone F (3-touch) | Per-concept; check which named concepts appear in Abstract |
| Milestone G (links) | Re-run the URL substitution utility |
| Milestone H (badges) | Single commit; check HTML for `.paper-badges` div |
| Milestone I (QA) | Restart the QA checklist from the top |
