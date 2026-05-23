#!/usr/bin/env python3
"""Hero figure F2: Architecture dominance.

Two-panel annotated plot that makes "architecture dominates domain" obvious
at a glance.

  Left:  Cumulative energy curves on normalized depth (0 = input, 1 = output)
         so Gemma's 26 layers and Qwen's 36 layers can overlay. Annotated
         50% thresholds (Gemma L11 / 42% depth, Qwen L28 / 78% depth) and
         the crossover region shaded.
  Right: 60x60 pairwise cosine similarity matrix of per-circuit layer-energy
         profiles (after normalized-depth resampling). Block structure:
         within-Gemma (top-left 30x30) and within-Qwen (bottom-right 30x30)
         cluster at 0.978; the two off-diagonal between-model blocks cluster
         at 0.696.

Data sources:
  data/stage_2_layer_energy/layer_energy_results.json
      -> .cumulative_energy[model]._category_summary
      -> .profile_similarity.cross_model.overall
  data/stage_2_layer_energy/per_circuit_layer_energy.json
      -> .[model] (30 circuits each, layer_energy_fraction)

Outputs:
  data/stage_2_figures/fig_architecture_dominance_hero.svg
  data/stage_2_figures/fig_architecture_dominance_hero.png
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------------------------------------------------------------------------
# Re-use the JSON loaders from the existing figure module rather than
# duplicating them. (Code-reviewer flag from Milestone C.)
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from stage_2_layer_energy_figures import load_results, load_per_circuit  # noqa: E402
from pipeline_constants import GEMMA_TOTAL_LAYERS, QWEN_TOTAL_LAYERS  # noqa: E402

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE = SCRIPT_DIR.parent
OUTPUT_DIR = BASE / 'data' / 'stage_2_figures'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Theme tokens (match site CSS — same as F1 hero / Milestone C)
# ---------------------------------------------------------------------------

COLOR_GEMMA      = '#e67e22'   # orange
COLOR_QWEN       = '#8854d0'   # purple
COLOR_NEUTRAL    = '#8b949e'
COLOR_TEXT       = '#1a1a1a'
COLOR_AXIS       = '#555555'
COLOR_MUTED      = '#6c757d'
COLOR_HIGH_SIM   = '#3273dc'   # blue, high-similarity diagonal blocks

MODEL_TOTAL_LAYERS = {'gemma-2-2b': GEMMA_TOTAL_LAYERS, 'qwen3-4b': QWEN_TOTAL_LAYERS}

# Common normalized-depth grid for pairwise similarity comparison across
# circuits of different layer counts. 64 was chosen as a smooth super-set
# of both 26 (Gemma) and 36 (Qwen) — high enough that linear interpolation
# error is negligible, low enough to keep the matrix cheap.
NORM_DEPTH_BINS = 64

# Annotation milestones, from the paper / per_circuit data.
GEMMA_50PCT_LAYER = 11
QWEN_50PCT_LAYER = 28

# ---------------------------------------------------------------------------
# Matplotlib style — matches F1 hero
# ---------------------------------------------------------------------------

plt.rcParams.update({
    'font.family': ['DM Sans', 'Helvetica', 'Arial', 'sans-serif'],
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': COLOR_AXIS,
    'axes.labelcolor': COLOR_TEXT,
    'xtick.color': COLOR_AXIS,
    'ytick.color': COLOR_AXIS,
    'text.color': COLOR_TEXT,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.transparent': False,
})


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------

def model_cumulative_curve(results: dict, model: str) -> tuple[np.ndarray, np.ndarray]:
    """Mean cumulative-energy curve for a model, averaged across all 3 categories.

    Returns (x_normalized_depth, mean_cumulative) where x is in [0, 1].
    """
    total_layers = MODEL_TOTAL_LAYERS[model]
    cat_summary = (
        results.get('cumulative_energy', {})
               .get(model, {})
               .get('_category_summary', {})
    )

    curves = []
    for cat in ('chemistry', 'geography', 'history'):
        summary = cat_summary.get(cat, {})
        if summary.get('mean_cumulative'):
            curves.append(np.asarray(summary['mean_cumulative']))

    if not curves:
        raise SystemExit(f'No cumulative-energy data for {model}.')

    overall_mean = np.mean(np.stack(curves, axis=0), axis=0)
    # Normalize layer index -> depth fraction in [0, 1].
    x = np.linspace(0.0, 1.0, total_layers)
    return x, overall_mean


def resample_to_common_depth(profile: np.ndarray, bins: int = NORM_DEPTH_BINS) -> np.ndarray:
    """Linearly interpolate a per-layer profile onto a common normalized-depth grid."""
    n = len(profile)
    src_x = np.linspace(0.0, 1.0, n)
    tgt_x = np.linspace(0.0, 1.0, bins)
    return np.interp(tgt_x, src_x, profile)


def build_similarity_matrix(per_circuit: dict) -> tuple[np.ndarray, list[str], int]:
    """Pairwise cosine similarity over all 60 circuits in normalized depth.

    Ordering: all 30 Gemma circuits first (rows/cols 0-29), then all 30 Qwen
    circuits (rows/cols 30-59). Within each model, circuits are listed in
    iteration order from the per_circuit JSON (stable for a given dump).

    Returns (sim_matrix, slugs, n_gemma).
    """
    profiles: list[np.ndarray] = []
    slugs: list[str] = []
    n_gemma = 0

    for slug, data in per_circuit.get('gemma-2-2b', {}).items():
        lef = data.get('layer_energy_fraction')
        if lef is None:
            continue
        profiles.append(resample_to_common_depth(np.asarray(lef, dtype=float)))
        slugs.append(f'gemma:{slug}')
        n_gemma += 1

    for slug, data in per_circuit.get('qwen3-4b', {}).items():
        lef = data.get('layer_energy_fraction')
        if lef is None:
            continue
        profiles.append(resample_to_common_depth(np.asarray(lef, dtype=float)))
        slugs.append(f'qwen:{slug}')

    mat = np.stack(profiles, axis=0)  # (N, bins)
    # Cosine similarity = (X X^T) / (|x_i| |x_j|).
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    normed = mat / norms
    sim = normed @ normed.T
    sim = np.clip(sim, -1.0, 1.0)
    return sim, slugs, n_gemma


def block_means(sim: np.ndarray, n_gemma: int) -> tuple[float, float]:
    """Return (within_model_mean, between_model_mean) over off-diagonal pairs."""
    n = sim.shape[0]
    iu = np.triu_indices(n, k=1)
    pairs_i, pairs_j = iu
    within_mask = ((pairs_i < n_gemma) & (pairs_j < n_gemma)) | \
                  ((pairs_i >= n_gemma) & (pairs_j >= n_gemma))
    between_mask = ~within_mask
    within = float(sim[pairs_i[within_mask], pairs_j[within_mask]].mean())
    between = float(sim[pairs_i[between_mask], pairs_j[between_mask]].mean())
    return within, between


# ---------------------------------------------------------------------------
# Plot helpers
# ---------------------------------------------------------------------------

def draw_left_panel(ax,
                    gemma_x: np.ndarray, gemma_y: np.ndarray,
                    qwen_x: np.ndarray, qwen_y: np.ndarray) -> None:
    # Where the gap between the two cumulative curves is largest — shaded
    # softly to draw the eye to the crossover region.
    common_x = np.linspace(0.0, 1.0, 200)
    gemma_interp = np.interp(common_x, gemma_x, gemma_y)
    qwen_interp = np.interp(common_x, qwen_x, qwen_y)
    diff = gemma_interp - qwen_interp
    if diff.max() > 0:
        peak_idx = int(np.argmax(diff))
        # Widen around the peak to make a visible band (+/- ~12% depth).
        half = 0.12
        lo = max(0.0, common_x[peak_idx] - half)
        hi = min(1.0, common_x[peak_idx] + half)
        ax.axvspan(lo, hi, color=COLOR_NEUTRAL, alpha=0.10, zorder=0)

    # The two cumulative-energy curves.
    ax.plot(gemma_x, gemma_y, color=COLOR_GEMMA, linewidth=2.4,
            label='Gemma-2-2B (26 layers)', zorder=3)
    ax.plot(qwen_x, qwen_y, color=COLOR_QWEN, linewidth=2.4,
            label='Qwen3-4B (36 layers)', zorder=3)

    # 50% reference line.
    ax.axhline(0.5, color=COLOR_MUTED, linestyle=(0, (4, 3)),
               linewidth=0.8, alpha=0.6, zorder=1)
    ax.text(1.005, 0.5, '50%', fontsize=8, color=COLOR_MUTED,
            va='center', ha='left')

    # 50%-threshold annotations for each model.
    gemma_depth = GEMMA_50PCT_LAYER / (MODEL_TOTAL_LAYERS['gemma-2-2b'] - 1)
    qwen_depth = QWEN_50PCT_LAYER / (MODEL_TOTAL_LAYERS['qwen3-4b'] - 1)

    ax.scatter([gemma_depth], [0.5], color=COLOR_GEMMA, s=44,
               zorder=4, edgecolor='white', linewidth=0.8)
    ax.scatter([qwen_depth], [0.5], color=COLOR_QWEN, s=44,
               zorder=4, edgecolor='white', linewidth=0.8)

    ax.annotate(
        'Gemma reaches 50%\nby L11 (42% depth)',
        xy=(gemma_depth, 0.5),
        xytext=(gemma_depth - 0.04, 0.78),
        fontsize=9.5, color=COLOR_GEMMA, fontweight='bold',
        ha='right', va='center',
        arrowprops=dict(arrowstyle='->', color=COLOR_GEMMA,
                        lw=1.0, shrinkA=0, shrinkB=4),
        zorder=5,
    )
    ax.annotate(
        'Qwen reaches 50%\nby L28 (78% depth)',
        xy=(qwen_depth, 0.5),
        xytext=(qwen_depth + 0.02, 0.22),
        fontsize=9.5, color=COLOR_QWEN, fontweight='bold',
        ha='left', va='center',
        arrowprops=dict(arrowstyle='->', color=COLOR_QWEN,
                        lw=1.0, shrinkA=0, shrinkB=4),
        zorder=5,
    )

    ax.set_xlabel('Normalized depth (0 = input, 1 = output)')
    ax.set_ylabel('Cumulative energy fraction')
    ax.set_title('Cumulative energy by depth',
                 color=COLOR_TEXT, pad=8)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.grid(True, alpha=0.18, zorder=0)

    leg = ax.legend(loc='lower right', fontsize=9, frameon=False,
                    handlelength=1.5, borderpad=0.3, labelspacing=0.3)
    for text in leg.get_texts():
        text.set_color(COLOR_TEXT)


def draw_right_panel(ax, sim: np.ndarray, n_gemma: int,
                     within_mean: float, between_mean: float) -> None:
    n = sim.shape[0]

    # Custom diverging-like colormap anchored at the between-model mean.
    # Lower bound at ~0.55 to keep the within-model blocks visually saturated.
    im = ax.imshow(sim, cmap='magma', vmin=0.55, vmax=1.0,
                   interpolation='nearest', aspect='equal', zorder=1)

    # Block dividers (between Gemma 0..29 and Qwen 30..59).
    div = n_gemma - 0.5
    ax.axhline(div, color='white', linewidth=1.6, zorder=3)
    ax.axvline(div, color='white', linewidth=1.6, zorder=3)

    # Block labels overlaid on the matrix.
    bbox_kwargs = dict(boxstyle='round,pad=0.32', facecolor='white',
                       edgecolor=COLOR_MUTED, linewidth=0.6, alpha=0.92)

    # Within-Gemma (top-left block centroid).
    ax.text((n_gemma - 1) / 2, (n_gemma - 1) / 2,
            f'Gemma×Gemma\n{within_mean:.3f}',
            fontsize=9.5, color=COLOR_TEXT, fontweight='bold',
            ha='center', va='center', bbox=bbox_kwargs, zorder=4)

    # Within-Qwen (bottom-right block centroid).
    center_q = n_gemma + (n - n_gemma - 1) / 2
    ax.text(center_q, center_q,
            f'Qwen×Qwen\n{within_mean:.3f}',
            fontsize=9.5, color=COLOR_TEXT, fontweight='bold',
            ha='center', va='center', bbox=bbox_kwargs, zorder=4)

    # Between-model (top-right block centroid).
    ax.text(center_q, (n_gemma - 1) / 2,
            f'Gemma×Qwen\n{between_mean:.3f}',
            fontsize=9.5, color=COLOR_TEXT, fontweight='bold',
            ha='center', va='center', bbox=bbox_kwargs, zorder=4)

    # Axis ticks delineating the two model blocks.
    ax.set_xticks([n_gemma / 2 - 0.5, n_gemma + (n - n_gemma) / 2 - 0.5])
    ax.set_xticklabels(['Gemma circuits (n=30)', 'Qwen circuits (n=30)'])
    ax.set_yticks([n_gemma / 2 - 0.5, n_gemma + (n - n_gemma) / 2 - 0.5])
    ax.set_yticklabels(['Gemma circuits', 'Qwen circuits'], rotation=90,
                       va='center')

    # Hide minor spines on the imshow (keep frame for the matrix).
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(COLOR_AXIS)
        spine.set_linewidth(0.8)

    ax.tick_params(length=0)
    ax.set_title('Energy profile similarity matrix',
                 color=COLOR_TEXT, pad=8)

    # Colorbar (compact, alongside the matrix).
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
    cbar.set_label('Cosine similarity', color=COLOR_TEXT, fontsize=10)
    cbar.ax.tick_params(colors=COLOR_AXIS, labelsize=9)
    cbar.outline.set_edgecolor(COLOR_AXIS)
    cbar.outline.set_linewidth(0.6)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    results = load_results()
    per_circuit = load_per_circuit()

    gemma_x, gemma_y = model_cumulative_curve(results, 'gemma-2-2b')
    qwen_x, qwen_y = model_cumulative_curve(results, 'qwen3-4b')

    sim, slugs, n_gemma = build_similarity_matrix(per_circuit)
    within_emp, between_emp = block_means(sim, n_gemma)

    # Use the paper's reported values for the in-figure labels (they were
    # computed from the exact same per-circuit profiles, just in
    # stage_2_layer_energy_main; the empirical numbers from this script
    # should match to within rounding — we print both so any drift is
    # visible at build time).
    overall = (
        results.get('profile_similarity', {})
               .get('cross_model', {})
               .get('overall', {})
    )
    within_paper = overall.get('within_model_mean', within_emp)
    between_paper = overall.get('between_model_mean', between_emp)

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, figsize=(13.2, 5.2),
        gridspec_kw=dict(width_ratios=[1.15, 1.0], wspace=0.30),
    )

    draw_left_panel(ax_left, gemma_x, gemma_y, qwen_x, qwen_y)
    draw_right_panel(ax_right, sim, n_gemma,
                     within_mean=within_paper, between_mean=between_paper)

    # Suptitle + subtitle, matching F1's positioning.
    fig.subplots_adjust(top=0.82)
    fig.suptitle('Architecture dominance', fontsize=17, fontweight='bold',
                 color=COLOR_TEXT, y=1.08, x=0.5, ha='center')
    fig.text(0.5, 1.012,
             'Energy profiles cluster 14× more tightly by architecture than by domain',
             fontsize=11.5, style='italic', color=COLOR_MUTED,
             ha='center', va='bottom')

    svg_path = OUTPUT_DIR / 'fig_architecture_dominance_hero.svg'
    png_path = OUTPUT_DIR / 'fig_architecture_dominance_hero.png'
    plt.savefig(svg_path, bbox_inches='tight')
    plt.savefig(png_path, bbox_inches='tight')
    plt.close(fig)

    print(f'  [OK] {svg_path.relative_to(BASE)}')
    print(f'  [OK] {png_path.relative_to(BASE)}')
    print(f'  Within-model cosine (empirical, this run):   {within_emp:.4f}')
    print(f'  Within-model cosine (paper / aggregated):    {within_paper:.4f}')
    print(f'  Between-model cosine (empirical, this run):  {between_emp:.4f}')
    print(f'  Between-model cosine (paper / aggregated):   {between_paper:.4f}')
    print(f'  Circuits in matrix: {len(slugs)} '
          f'(Gemma={n_gemma}, Qwen={len(slugs) - n_gemma})')


if __name__ == '__main__':
    main()
