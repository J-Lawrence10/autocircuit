# Cross-Domain Circuits Website Upgrade — Design

**Date:** 2026-05-23
**Author:** Joseph Lawrence
**Status:** Approved — ready for implementation plan
**Target file:** `docs/cross-domain-circuits.html` (sibling to `docs/index.html`, the upstream Olalekan/Krampis paper site)

---

## 1. Goal

Bring `docs/cross-domain-circuits.html` to **submission-ready public-release quality** with full visual and structural parity to the upstream Olalekan/Krampis paper site at https://kkrampis.github.io/autocircuit/, while **leading with the paper's actual punchlines** rather than mimicking upstream's editorial decisions.

Done = the page is something we can link from an arXiv submission, a job application, or a conference talk without further polishing.

---

## 2. Current state (baseline)

- 949 lines, identical Bulma 0.9.4 + DM Sans + Font Awesome scaffold as upstream
- Dark/light theme toggle works
- 14 H2 sections organized as 7 numbered findings + auxiliary
- 9 PNG matplotlib data plots referenced via `<img>` tags
- 8 HTML tables
- 3 Neuronpedia interactive feature links
- 2 authors (Joseph Lawrence, Konstantinos Krampis); only Konstantinos has LinkedIn

## 3. Gap analysis vs. upstream

| Element | Ours | Upstream | Gap |
|---------|------|----------|-----|
| H2 sections | 14 (results-forward) | 9 (canonical) | Restructure |
| Inline `<svg>` | 1 | 3 | Visual mismatch |
| `<img>` PNG | 9 | 0 | Visual mismatch |
| Tables | 8 | 19 | Less scannable |
| Neuronpedia links | 3 | 6+ | Half coverage |
| Author LinkedIn | 1/2 | 2/4 | Add Joseph's |

---

## 4. Design decisions

### 4.1 Section structure — adopt canonical academic order

Restructure into the canonical six-section flow used by upstream and standard for submission. The 7 numbered findings move down one level, becoming H3 subsections (3.2–3.8) inside Results.

| H2 | H3 subsections |
|----|----------------|
| Abstract | (none) |
| 1. Introduction | 1.1 Motivation · 1.2 Research Questions · 1.3 Contributions |
| 2. Methodology | 2.1 Attribution Graph Generation · 2.2 Traceback Graphing · 2.3 Cross-Circuit Comparison · 2.4 Statistical Framework |
| 3. Results | 3.1 Within-domain convergence · 3.2 Architecture dominance · 3.3 Universal bottlenecks · 3.4 Output convergence · 3.5 Bottleneck tax · 3.6 Circuit redundancy · 3.7 Causal steering · 3.8 Format variation |
| 4. Discussion | 4.1 Architecture vs domain · 4.2 Universal features as routing · 4.3 Bottleneck tax interpretation · 4.4 Three-tier dissociation |
| 5. Limitations | (numbered list) |
| 6. Conclusions | (numbered list + Future Work) |
| Supplementary Materials | Links to GLOSSARY, SUPPLEMENTARY_MATERIALS, PDF |
| BibTeX | (existing) |

Rationale: matches upstream and academic convention at the H2 level, but the 7-findings results-forward identity survives at the H3 level (§3.2–§3.8).

### 4.2 Figure plan — high-impact, not upstream-mimicking

User directive: *"we don't have to mimic their figure style we shouldn't limit our work based on them. We want high quality, high impact, clear punchline figures."*

Final figure set: **8 figures, all SVG, all punchline-led captions**.

| # | Title | Type | Section | Source |
|---|-------|------|---------|--------|
| F1 | **Bottleneck tax (HERO)** | New 2-panel annotated SVG | §3.5 | Redesigned matplotlib from fig18 data |
| F2 | **Architecture dominance (HERO)** | New combined 2-panel SVG (cumulative energy + cosine similarity) | §3.2 | Combined fig19 + fig20 data |
| F3 | Within-domain Jaccard heatmaps | SVG export | §3.1 | fig2 |
| F4 | Bottleneck depth by domain | SVG export | §3.2 (inline) | fig3 |
| F5 | Output vs path convergence | SVG export | §3.4 | fig10 |
| F6 | Circuit redundancy & essential pathway | SVG export | §3.6 | fig41 |
| F7 | Causal steering combined panel | SVG, combined | §3.7 | fig43 + fig45 |
| F8 | **Three-tier dissociation schematic (NEW)** | Hand-crafted inline SVG | §3.7 / §4.4 | New |

Demoted to supplementary: fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig21–fig29 (already not in main paper site; remain in PDF supplementary).

### 4.3 Named-concept reinforcement — three-touch ladder

Four named concepts get the same reinforcement pattern: **Abstract inline definition → Key Findings callout bullet → punchline-led figure caption** (plus optional Glossary ⓘ deep-link icon on first body mention).

#### 4.3.1 Bottleneck tax

**Touch 1 — Abstract revision:**
> *We term this pattern the "bottleneck tax" — heavier activation concentration at the bottleneck layer predicting lower downstream confidence — and interpret it through information bottleneck theory (Tishby & Zaslavsky, 2015).*

**Touch 2 — Key Findings callout:**
> **The bottleneck tax.** Across 30 Gemma circuits, more activation at the bottleneck layer L6 predicts *worse* output confidence (r = −0.684, Bonferroni-significant). Counter-intuitive correlation consistent with information bottleneck theory. [Jump to §3.5 →]

**Touch 3 — Figure F1 caption:**
> **Figure 1: The bottleneck tax.** Per-layer Spearman correlation between activation energy fraction and output confidence across 30 Gemma circuits. **Bottleneck layer L6 shows a strong negative correlation (r = −0.684, p < 0.0001):** circuits concentrating more activation at L6 produce *less* confident predictions. Post-bottleneck layers L13, L16 reverse the sign (r ≈ +0.60), consistent with information bottleneck framing — heavier compression at intermediate layers reduces information available for downstream evidence accumulation.

#### 4.3.2 Three-tier dissociation

**Touch 1 — Abstract revision:**
> *We name this pattern the "three-tier dissociation" — essential-pathway topology predicts distributional perturbation strength (KL divergence), cross-circuit frequency does not predict causal influence, and text-level output changes are governed by output entropy rather than feature-selection criteria.*

**Touch 2 — Key Findings callout:**
> **The three-tier dissociation.** 80 steering experiments reveal that pathway topology, cross-circuit frequency, and text-level behavior each measure different things. Essential-pathway features perturb distributions strongest (KL = 1.448) but 94% circuit redundancy absorbs them. [Jump to §3.7 →]

**Touch 3 — Figure F8 caption (new schematic):**
> **Figure 8: The three-tier dissociation.** Three independent dimensions of feature importance, none of which alone predicts behavior. **Tier 1 (essential-pathway topology)** governs distributional perturbation strength. **Tier 2 (cross-circuit frequency)** is statistically common but causally weak. **Tier 3 (output determinism by domain)** governs text-level susceptibility (chemistry 0%, geography 20%, history 60%). Attribution graphs capture Tier 1 but not Tier 3.

#### 4.3.3 Architecture dominance

**Touch 1 — Abstract revision:**
> *We document "architecture dominance" — within-model energy profile similarity clusters 14× more tightly than between-model similarity (cosine 0.978 vs 0.696), even after depth normalization. Knowledge domain modulates this profile by less than 2%.*

**Touch 2 — Key Findings callout:**
> **Architecture dominance.** Across 60 circuits, model architecture explains ~14× more variance in layer-energy profiles than knowledge domain. Gemma front-loads 54% of energy into early layers; Qwen back-loads with 31%. Both produce comparable factual recall. [Jump to §3.2 →]

**Touch 3 — Figure F2 caption (hero):**
> **Figure 2: Architecture dominance.** **Left:** Cumulative energy profiles show Gemma front-loads 54% of activation into the first half of layers while Qwen back-loads with only 31% — fundamentally different computational strategies, comparable factual recall. **Right:** Energy profile cosine similarity matrix. Within-model pairs cluster at 0.978 (lower-left and upper-right blocks); between-model pairs drop to 0.696 (off-diagonal blocks). Architecture explains ~14× more variance than knowledge domain.

#### 4.3.4 Universal bottleneck features

**Touch 1 — Abstract revision:**
> *We identify "universal bottleneck features" — features serving as bottlenecks across all three knowledge domains. Six in Gemma and 15 in Qwen, with zero overlap between architectures. Their dominant categories (CODE 20%, LANGUAGE 20%) suggest they act as routing infrastructure rather than knowledge stores.*

**Touch 2 — Key Findings callout:**
> **Universal bottleneck features.** Six Gemma and 15 Qwen features participate in circuits across chemistry, geography, AND history. Zero cross-architecture overlap. Function: routing infrastructure, not knowledge stores. [Jump to §3.3 →]

**Touch 3 — Figure (table-driven, not image):** Already present as a table in §3.3; no new figure needed. Just promote the table styling.

### 4.4 Author block

```html
<span class="author-block">
  <a href="[JOSEPH_LINKEDIN_URL]" target="_blank">Joseph Lawrence</a> ·
  <a href="https://linkedin.com/in/kkrampis/" target="_blank">Konstantinos Krampis</a>
</span>
```

`[JOSEPH_LINKEDIN_URL]` to be filled in by user before publish.

### 4.5 Project-page header badge row (new)

Add immediately below title, before authors:

```html
<div class="paper-badges">
  <a href="pdf/CROSS_DOMAIN_CIRCUIT_PAPER.pdf">📄 Paper (PDF)</a>
  <a href="pdf/GLOSSARY.pdf">📊 Glossary</a>
  <a href="https://github.com/J-Lawrence10/autocircuit">💻 Code</a>
  <a href="https://neuronpedia.org/...">🔗 Neuronpedia</a>
</div>
```

Mirrors upstream convention for project pages.

### 4.6 Neuronpedia link expansion

Hyperlink every named feature ID in the body to its Neuronpedia page:
- Universal bottleneck features (6 Gemma + 15 Qwen = 21 features) in §3.3 table
- Steered features in §3.7 (15 features across D4/D5/D6 batches)
- All named features in figure captions

Format:
```
Gemma: https://neuronpedia.org/gemma-2-2b/{layer}-gemmascope-transcoder-16k/{feature_idx}
Qwen:  https://neuronpedia.org/qwen3-4b/{layer}-?/{feature_idx}
```

Total target: ~35+ Neuronpedia links.

### 4.7 Glossary ⓘ deep-links

On first body mention of each named concept, add a small superscript icon linking to the matching `GLOSSARY.html#anchor`. CSS:

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

Concepts: bottleneck tax, three-tier dissociation, architecture dominance, universal bottleneck features, activation energy, Jaccard similarity, traceback graphing, direct logit attribution.

### 4.8 Prose polish pass

- Strengthen all 8 figure captions to lead with findings (already specced in §4.2/§4.3).
- Tighten Abstract from current 6 paragraphs to 3.
- Verify §X.Y format and Gemma/Qwen casing already applied in MD propagate to HTML.
- Standardize all in-page anchors (`id="..."`) for browser back-button + TOC linking.
- Ensure every figure has unique `id` for direct linking from Key Findings callouts.

---

## 5. Execution order (~6.5 hours)

| # | Task | Time |
|---|------|------|
| 1 | Section restructure (H2/H3 reorganization in HTML) | 1 hr |
| 2 | Re-export 5 existing figures as SVG via matplotlib `savefig` | 30 min |
| 3 | New hero figure F1: Bottleneck tax (2-panel annotated SVG) | 1.5 hr |
| 4 | New hero figure F2: Architecture dominance (2-panel combined) | 1.5 hr |
| 5 | New schematic F8: Three-tier dissociation (hand-crafted inline SVG) | 1 hr |
| 6 | Caption rewrites (all 8 figures, punchline-led) | 30 min |
| 7 | Three-touch reinforcement: Abstract revisions + Key Findings callouts | 45 min |
| 8 | Neuronpedia link sweep (3 → 35+ links) | 45 min |
| 9 | Glossary ⓘ deep-links (8 concepts × ~3 mentions each) | 30 min |
| 10 | Author LinkedIn + project-page badge row | 15 min |
| 11 | Final QA: theme toggle, anchors, mobile viewport, broken links | 30 min |

**Total: ~9 hours** (revised up from initial ~6-8 estimate after design fleshed out)

---

## 6. Out of scope (explicitly NOT in this design)

- Adopting upstream's editorial SVG style verbatim (user directive: don't mimic)
- Replacing matplotlib data plots with hand-drawn equivalents (loses data fidelity)
- Restructuring the underlying `CROSS_DOMAIN_CIRCUIT_PAPER.md` (HTML is the deliverable; MD already has the relevant content)
- Adding co-authors beyond Joseph + Konstantinos (user decision)
- Building a new domain or hosting infrastructure (page lives at existing `docs/` path)

---

## 7. Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| Matplotlib SVG export produces visually dense files (every tick is a path) | Use `mpl.style.use('seaborn-v0_8-white')` or custom minimal stylesheet; strip non-essential SVG elements post-export |
| Section reorder breaks existing inbound anchor links (if any external sites link to specific findings) | Add HTML comment listing old anchors → new anchors mapping; consider 301-style redirect anchors if needed |
| New hero figures take longer than estimated | F1 (bottleneck tax) is highest priority; F2 can fall back to simple SVG-export of fig19+fig20 separately if time-constrained |
| Joseph's LinkedIn URL not yet provided | Leave placeholder `[JOSEPH_LINKEDIN_URL]`; site can publish without it and update later |

---

## 8. Success criteria

- [ ] All 6 canonical H2 sections present in correct order
- [ ] 8 figures, all SVG, all with punchline-led captions
- [ ] 4 named concepts each get three-touch reinforcement (Abstract + Key Findings + Figure caption)
- [ ] 35+ Neuronpedia feature hyperlinks
- [ ] Joseph's LinkedIn linked (or clearly marked TODO)
- [ ] Project-page badge row present
- [ ] Glossary ⓘ icons on first body mention of 8 concepts
- [ ] Dark/light theme toggle works on every new element
- [ ] No broken links, anchors, or images
- [ ] Renders cleanly on mobile viewport
- [ ] PDF regenerated to reflect any MD changes (mostly the bottleneck-tax inline definition)

---

## 9. Next step

Invoke `superpowers:writing-plans` to produce a sequenced, file-and-line-level implementation plan that can be executed step by step.
