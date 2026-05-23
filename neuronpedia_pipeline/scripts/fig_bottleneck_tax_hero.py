#!/usr/bin/env python3
"""Hero figure F1: The bottleneck tax.

Two-panel annotated plot.
  Left:  per-layer Spearman correlation between activation energy fraction
         and output confidence across 30 Gemma circuits. Sign-coloured bars
         (orange for r <= -0.3, purple for r >= +0.3, grey otherwise) with
         L6 highlighted via an annotated vertical guide. Horizontal guides
         at +/-0.6 mark a rough Bonferroni-significance band for visual
         reference.
  Right: scatter of the 30 Gemma circuits, x = L6 energy fraction,
         y = output probability. A regression line plus an r/p text box
         drives the punchline home.

Data sources:
  data/stage_2_layer_energy/layer_energy_results.json
      -> .layer_confidence_correlation['gemma-2-2b'].per_layer
  data/stage_2_layer_energy/per_circuit_layer_energy.json
      -> .['gemma-2-2b'] (30 circuits)

Outputs:
  data/stage_2_figures/fig_bottleneck_tax_hero.svg
  data/stage_2_figures/fig_bottleneck_tax_hero.png
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make sibling modules in scripts/ importable, then bring in shared style.
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from _hero_style import (  # noqa: E402
    setup_agg_backend,
    apply_hero_rcparams,
    save_hero_figure,
    COLOR_BOTTLENECK,
    COLOR_POSTBOTTLE,
    COLOR_NEUTRAL,
    COLOR_TEXT,
    COLOR_AXIS,
    COLOR_MUTED,
    COLOR_REGLINE,
    COLOR_SCATTER,
)

setup_agg_backend()
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE = SCRIPT_DIR.parent
LAYER_ENERGY_DIR = BASE / 'data' / 'stage_2_layer_energy'
OUTPUT_DIR = BASE / 'data' / 'stage_2_figures'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_FILE = LAYER_ENERGY_DIR / 'layer_energy_results.json'
PER_CIRCUIT_FILE = LAYER_ENERGY_DIR / 'per_circuit_layer_energy.json'

# Visual threshold for sign-based bar coloring (separate from Bonferroni).
SIGN_THRESHOLD = 0.3
BONFERRONI_GUIDE = 0.6  # horizontal guide lines

# Bottleneck layer of interest in Gemma circuits.
BOTTLENECK_LAYER = 6

# ---------------------------------------------------------------------------
# Matplotlib style
# ---------------------------------------------------------------------------

apply_hero_rcparams()

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_per_layer_correlations(results: dict) -> tuple[list[int], list[float], list[float]]:
    """Return (layers, spearman_r, spearman_p) for Gemma."""
    lc = results['layer_confidence_correlation']['gemma-2-2b']
    per_layer = lc['per_layer']
    layers = [entry['layer'] for entry in per_layer]
    r_values = [entry['spearman_r'] for entry in per_layer]
    p_values = [entry['spearman_p'] for entry in per_layer]
    return layers, r_values, p_values


def load_l6_scatter(per_circuit: dict) -> tuple[np.ndarray, np.ndarray]:
    """Return (l6_energy_fraction, output_probability) for the 30 Gemma circuits."""
    gemma = per_circuit['gemma-2-2b']
    l6_frac = []
    output_prob = []
    for slug, data in gemma.items():
        lef = data.get('layer_energy_fraction')
        op = data.get('output_probability')
        if lef is None or op is None:
            continue
        if len(lef) <= BOTTLENECK_LAYER:
            continue
        l6_frac.append(lef[BOTTLENECK_LAYER])
        output_prob.append(op)
    return np.asarray(l6_frac), np.asarray(output_prob)


# ---------------------------------------------------------------------------
# Plot helpers
# ---------------------------------------------------------------------------

def bar_color(r: float) -> str:
    if r <= -SIGN_THRESHOLD:
        return COLOR_BOTTLENECK
    if r >= SIGN_THRESHOLD:
        return COLOR_POSTBOTTLE
    return COLOR_NEUTRAL


def draw_left_panel(ax, layers: list[int], r_values: list[float]) -> None:
    colors = [bar_color(r) for r in r_values]

    bars = ax.bar(layers, r_values, color=colors, width=0.78,
                  edgecolor='white', linewidth=0.6, zorder=3)

    # Highlight L6 specifically: thicker edge.
    for layer, bar in zip(layers, bars):
        if layer == BOTTLENECK_LAYER:
            bar.set_edgecolor(COLOR_TEXT)
            bar.set_linewidth(1.6)

    # Zero line + Bonferroni-style horizontal guides at +/- 0.6.
    ax.axhline(0, color=COLOR_AXIS, linewidth=0.7, zorder=2)
    for y in (BONFERRONI_GUIDE, -BONFERRONI_GUIDE):
        ax.axhline(y, color=COLOR_MUTED, linestyle=(0, (4, 3)),
                   linewidth=0.8, alpha=0.6, zorder=1)
    ax.text(max(layers) + 0.4, BONFERRONI_GUIDE, '+0.6',
            fontsize=8, color=COLOR_MUTED, va='center', ha='left')
    ax.text(max(layers) + 0.4, -BONFERRONI_GUIDE, '−0.6',
            fontsize=8, color=COLOR_MUTED, va='center', ha='left')

    # Vertical dashed line at L6 with annotation.
    ax.axvline(BOTTLENECK_LAYER, color=COLOR_BOTTLENECK,
               linestyle=(0, (3, 3)), linewidth=1.2, alpha=0.85, zorder=2)

    # Annotation arrow pointing to L6.
    r_l6 = r_values[BOTTLENECK_LAYER]
    ax.annotate(
        'L6 — bottleneck',
        xy=(BOTTLENECK_LAYER, r_l6),
        xytext=(BOTTLENECK_LAYER + 5.0, r_l6 - 0.18),
        fontsize=10, color=COLOR_BOTTLENECK, fontweight='bold',
        arrowprops=dict(arrowstyle='->', color=COLOR_BOTTLENECK,
                        lw=1.1, shrinkA=0, shrinkB=4),
        zorder=5,
    )

    # Axes formatting.
    ax.set_xlabel('Layer')
    ax.set_ylabel('Spearman r (energy fraction vs output prob)')
    ax.set_title('Per-layer correlation across 30 Gemma circuits',
                 color=COLOR_TEXT, pad=8)
    ax.set_xlim(-0.7, max(layers) + 1.4)
    ax.set_ylim(-1.0, 1.0)
    ax.set_xticks([0, 5, 10, 15, 20, 25])
    ax.grid(True, axis='y', alpha=0.18, zorder=0)

    # Mini legend (color key) in the upper-left corner.
    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, color=COLOR_BOTTLENECK,
                      label='r ≤ −0.3 (bottleneck-like)'),
        plt.Rectangle((0, 0), 1, 1, color=COLOR_POSTBOTTLE,
                      label='r ≥ +0.3 (post-bottleneck)'),
        plt.Rectangle((0, 0), 1, 1, color=COLOR_NEUTRAL,
                      label='|r| < 0.3'),
    ]
    leg = ax.legend(handles=legend_handles, loc='lower left',
                    fontsize=8, frameon=False, handlelength=1.2,
                    handleheight=0.8, borderpad=0.3, labelspacing=0.3)
    for text in leg.get_texts():
        text.set_color(COLOR_TEXT)


def draw_right_panel(ax, l6_frac: np.ndarray, output_prob: np.ndarray) -> None:
    # Regression statistics (Spearman to match the left panel + line via OLS).
    sp_r, sp_p = stats.spearmanr(l6_frac, output_prob)
    slope, intercept, r_pearson, p_pearson, _ = stats.linregress(l6_frac, output_prob)

    # Scatter
    ax.scatter(l6_frac, output_prob,
               s=42, color=COLOR_SCATTER, edgecolor='white',
               linewidth=0.7, alpha=0.85, zorder=3)

    # Regression line across the observed x-range.
    x_line = np.linspace(l6_frac.min(), l6_frac.max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, color=COLOR_REGLINE, linewidth=2.0,
            alpha=0.85, zorder=2, label='OLS fit')

    # Stats text box.
    p_str = f'p = {sp_p:.2e}' if sp_p < 1e-3 else f'p = {sp_p:.4f}'
    textstr = f'Spearman r = {sp_r:.3f}\n{p_str}\nn = {len(l6_frac)} circuits'
    ax.text(0.97, 0.97, textstr, transform=ax.transAxes,
            fontsize=10, va='top', ha='right', color=COLOR_TEXT,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                      edgecolor=COLOR_MUTED, linewidth=0.6, alpha=0.95),
            zorder=5)

    ax.set_xlabel('L6 energy fraction (per circuit)')
    ax.set_ylabel('Output probability')
    ax.set_title('L6 energy fraction vs output confidence',
                 color=COLOR_TEXT, pad=8)
    ax.grid(True, alpha=0.18, zorder=0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        results = json.load(f)
    with open(PER_CIRCUIT_FILE, 'r', encoding='utf-8') as f:
        per_circuit = json.load(f)

    layers, r_values, p_values = load_per_layer_correlations(results)
    l6_frac, output_prob = load_l6_scatter(per_circuit)

    if len(l6_frac) == 0:
        raise SystemExit('No Gemma circuits with L6 data found.')

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, figsize=(12.5, 4.8),
        gridspec_kw=dict(width_ratios=[1.35, 1.0], wspace=0.28),
    )

    draw_left_panel(ax_left, layers, r_values)
    draw_right_panel(ax_right, l6_frac, output_prob)

    # Title + subtitle anchored to the figure.
    # Reserve headroom so neither overlaps the panel titles.
    fig.subplots_adjust(top=0.82)
    fig.suptitle('The bottleneck tax', fontsize=17, fontweight='bold',
                 color=COLOR_TEXT, y=1.08, x=0.5, ha='center')
    fig.text(0.5, 1.012, 'More L6 activation → lower output confidence',
             fontsize=11.5, style='italic', color=COLOR_MUTED,
             ha='center', va='bottom')

    save_hero_figure(fig, 'fig_bottleneck_tax_hero', OUTPUT_DIR,
                     base_for_display=BASE)
    plt.close(fig)

    print(f'  L6 Spearman r = {r_values[BOTTLENECK_LAYER]:.4f}  '
          f'(scatter: r = {stats.spearmanr(l6_frac, output_prob).correlation:.4f}, '
          f'n = {len(l6_frac)})')


if __name__ == '__main__':
    main()
