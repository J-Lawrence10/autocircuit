#!/usr/bin/env python3
"""Hero figure F3: Where the bottleneck lives.

Two-panel histogram of per-circuit average bottleneck layer across 30 Gemma
circuits (left) and 30 Qwen circuits (right). Each circuit contributes one
data point, the mean layer index of all features in that circuit with path
convergence >= 60% (the bottleneck threshold defined in section 3.2). The
peak of the histogram identifies that model's primary bottleneck layer.

Methodological note:
  We use the per-circuit *mean bottleneck layer* (one value per circuit, 30
  circuits per model) rather than the raw count of bottleneck-feature
  instances summed across circuits. The raw-count distribution is dominated
  by L0 (input embedding features that are trivially shared, since every
  traceback path begins at the inputs). The per-circuit center of mass is
  the statistic that drives the paper's "L5-7 in Gemma, L22-25 in Qwen"
  claims, and is the cleaner visual confirmation of where the computational
  bottleneck cluster lives in each architecture.

  Left:  Gemma-2-2B histogram, integer layer bins L0..L25. Orange bars
         (COLOR_BOTTLENECK), with the L5-7 modal band emphasized via a
         darker shade and stronger edges. Annotation calls out the peak.
  Right: Qwen3-4B histogram, integer layer bins L0..L35. Purple bars
         (COLOR_POSTBOTTLE), with the L22-25 modal band emphasized.

Data source:
  data/stage_2_statistical_deepdive/data_table.json
      -> [*].avg_bottleneck_layer per circuit (60 circuits, 30 each model)

Outputs:
  data/stage_2_figures/fig_bottleneck_density_hero.svg
  data/stage_2_figures/fig_bottleneck_density_hero.png
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from _hero_style import (  # noqa: E402
    setup_agg_backend,
    apply_hero_rcparams,
    save_hero_figure,
    COLOR_BOTTLENECK,
    COLOR_POSTBOTTLE,
    COLOR_TEXT,
    COLOR_AXIS,
    COLOR_MUTED,
)
from pipeline_constants import GEMMA_TOTAL_LAYERS, QWEN_TOTAL_LAYERS  # noqa: E402

setup_agg_backend()
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.colors as mcolors  # noqa: E402
import numpy as np  # noqa: E402


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE = SCRIPT_DIR.parent
OUTPUT_DIR = BASE / 'data' / 'stage_2_figures'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DATA_TABLE = BASE / 'data' / 'stage_2_statistical_deepdive' / 'data_table.json'

# Modal bottleneck bands per the paper's section 3.2 claims.
GEMMA_PEAK_RANGE = (5, 7)
QWEN_PEAK_RANGE = (22, 25)


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

apply_hero_rcparams()


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load_avg_bottleneck_layers(data_table: list[dict], model: str) -> np.ndarray:
    """Return the array of per-circuit avg_bottleneck_layer values for a model."""
    return np.asarray(
        [row['avg_bottleneck_layer'] for row in data_table
         if row.get('model') == model and row.get('avg_bottleneck_layer') is not None],
        dtype=float,
    )


def histogram_by_layer(values: np.ndarray, total_layers: int) -> np.ndarray:
    """Integer-bin counts: bin L contains values in [L - 0.5, L + 0.5)."""
    bins = np.arange(-0.5, total_layers + 0.5, 1.0)
    counts, _ = np.histogram(values, bins=bins)
    return counts


def darken(hex_color: str, factor: float = 0.72) -> str:
    """Return a darker variant of a hex color (RGB scaled toward black)."""
    rgb = np.array(mcolors.to_rgb(hex_color))
    return mcolors.to_hex(rgb * factor)


# ---------------------------------------------------------------------------
# Plot helpers
# ---------------------------------------------------------------------------

def draw_panel(
    ax,
    values: np.ndarray,
    total_layers: int,
    base_color: str,
    peak_range: tuple[int, int],
    panel_title: str,
    annotation_text: str,
    xtick_step: int,
) -> None:
    counts = histogram_by_layer(values, total_layers)
    layers = np.arange(total_layers)
    peak_lo, peak_hi = peak_range

    base_face = base_color
    peak_face = darken(base_color, 0.78)
    base_edge = 'white'
    peak_edge = COLOR_TEXT

    face_colors = [peak_face if peak_lo <= L <= peak_hi else base_face for L in layers]
    edge_colors = [peak_edge if peak_lo <= L <= peak_hi else base_edge for L in layers]
    edge_widths = [1.4 if peak_lo <= L <= peak_hi else 0.6 for L in layers]

    ax.bar(
        layers, counts,
        color=face_colors,
        edgecolor=edge_colors,
        linewidth=edge_widths,
        width=0.85,
        zorder=3,
    )

    # Light grid behind the bars.
    ax.grid(True, axis='y', alpha=0.18, zorder=0)

    # Peak band shading for extra emphasis.
    ax.axvspan(peak_lo - 0.5, peak_hi + 0.5,
               color=base_color, alpha=0.10, zorder=1)

    # Mean line as a thin marker.
    mean_val = float(np.mean(values))
    ax.axvline(mean_val, color=darken(base_color, 0.6),
               linestyle=(0, (3, 3)), linewidth=1.2, alpha=0.85, zorder=2)

    # Annotation: arrow pointing into the peak band, near the tallest bar.
    peak_slice = counts[peak_lo:peak_hi + 1]
    peak_layer = peak_lo + int(np.argmax(peak_slice)) if peak_slice.size else peak_lo
    peak_y = counts[peak_layer]
    y_max = counts.max() if counts.max() > 0 else 1

    text_x = peak_hi + max(2.5, total_layers * 0.10)
    text_y = peak_y + y_max * 0.35
    text_x = min(text_x, total_layers - 1)
    text_y = min(text_y, y_max * 1.36)

    ax.annotate(
        annotation_text,
        xy=(peak_layer, peak_y),
        xytext=(text_x, text_y),
        fontsize=10, color=darken(base_color, 0.7), fontweight='bold',
        ha='left', va='center',
        arrowprops=dict(arrowstyle='->', color=darken(base_color, 0.7),
                        lw=1.1, shrinkA=0, shrinkB=5),
        zorder=5,
    )

    # Mean label, anchored to the top of the axes to avoid bar overlap.
    ax.text(mean_val + 0.4, y_max * 1.46, f'mean = L{mean_val:.1f}',
            fontsize=9, color=darken(base_color, 0.6),
            ha='left', va='top', zorder=4)

    # Axes formatting.
    ax.set_xlim(-0.8, total_layers - 0.2)
    ax.set_ylim(0, y_max * 1.55)
    ax.set_xticks(list(range(0, total_layers, xtick_step)))
    ax.set_xlabel('Average bottleneck layer (per circuit)')
    ax.set_ylabel('Number of circuits (n = 30)')
    ax.set_title(panel_title, color=COLOR_TEXT, pad=8)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    with open(DATA_TABLE, 'r', encoding='utf-8') as f:
        data_table = json.load(f)

    gemma_vals = load_avg_bottleneck_layers(data_table, 'gemma-2-2b')
    qwen_vals = load_avg_bottleneck_layers(data_table, 'qwen3-4b')

    if gemma_vals.size == 0 or qwen_vals.size == 0:
        raise SystemExit('No avg_bottleneck_layer data found for one or both models.')

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, figsize=(13.4, 4.9),
        gridspec_kw=dict(width_ratios=[1.0, 1.30], wspace=0.24),
    )

    draw_panel(
        ax_left,
        values=gemma_vals,
        total_layers=GEMMA_TOTAL_LAYERS,
        base_color=COLOR_BOTTLENECK,
        peak_range=GEMMA_PEAK_RANGE,
        panel_title='Gemma-2-2B (26 layers)',
        annotation_text='L5-7 modal band\nprimary bottleneck',
        xtick_step=5,
    )
    draw_panel(
        ax_right,
        values=qwen_vals,
        total_layers=QWEN_TOTAL_LAYERS,
        base_color=COLOR_POSTBOTTLE,
        peak_range=QWEN_PEAK_RANGE,
        panel_title='Qwen3-4B (36 layers)',
        annotation_text='L22-25 modal band\nprimary bottleneck',
        xtick_step=5,
    )

    fig.subplots_adjust(top=0.82)
    fig.suptitle('Where the bottleneck lives', fontsize=17, fontweight='bold',
                 color=COLOR_TEXT, y=1.08, x=0.5, ha='center')
    fig.text(
        0.5, 1.012,
        'Per-circuit mean bottleneck layer (path convergence >= 60%) clusters '
        'sharply by architecture, around L5-7 in Gemma and L22-25 in Qwen',
        fontsize=11.5, style='italic', color=COLOR_MUTED,
        ha='center', va='bottom',
    )

    save_hero_figure(fig, 'fig_bottleneck_density_hero', OUTPUT_DIR,
                     base_for_display=BASE)
    plt.close(fig)

    # Receipts.
    g_counts = histogram_by_layer(gemma_vals, GEMMA_TOTAL_LAYERS)
    q_counts = histogram_by_layer(qwen_vals, QWEN_TOTAL_LAYERS)
    g_band = int(g_counts[GEMMA_PEAK_RANGE[0]:GEMMA_PEAK_RANGE[1] + 1].sum())
    q_band = int(q_counts[QWEN_PEAK_RANGE[0]:QWEN_PEAK_RANGE[1] + 1].sum())
    print(f'  Gemma circuits: n={gemma_vals.size}, '
          f'mean avg-bottleneck-layer = {gemma_vals.mean():.2f}, '
          f'median = {np.median(gemma_vals):.2f}')
    print(f'    L5-7 band holds {g_band}/{gemma_vals.size} circuits '
          f'({100 * g_band / gemma_vals.size:.0f}%)')
    print(f'  Qwen circuits: n={qwen_vals.size}, '
          f'mean avg-bottleneck-layer = {qwen_vals.mean():.2f}, '
          f'median = {np.median(qwen_vals):.2f}')
    print(f'    L22-25 band holds {q_band}/{qwen_vals.size} circuits '
          f'({100 * q_band / qwen_vals.size:.0f}%)')


if __name__ == '__main__':
    main()
