"""Shared style and setup for hero figures.

Centralizes the pieces previously duplicated across
`fig_bottleneck_tax_hero.py` and `fig_architecture_dominance_hero.py`:

  * Windows stdout/stderr UTF-8 wrappers (so glyphs like the OK box don't
    blow up cp1252 consoles).
  * Theme color constants — must stay in sync with the site CSS used by
    docs/cross-domain-circuits.html.
  * `apply_hero_rcparams()` — the matplotlib rcParams both heroes share.
  * `save_hero_figure(fig, slug, output_dir)` — saves both `.svg` and `.png`
    with matching `bbox_inches='tight'` kwargs and prints an [OK] receipt.
  * `setup_agg_backend()` — must be called *before* `import matplotlib.pyplot`.

Usage at the top of a hero script:

    from _hero_style import setup_agg_backend
    setup_agg_backend()
    import matplotlib.pyplot as plt
    from _hero_style import (
        apply_hero_rcparams, save_hero_figure,
        COLOR_BOTTLENECK, COLOR_POSTBOTTLE, COLOR_NEUTRAL,
        COLOR_TEXT, COLOR_AXIS, COLOR_MUTED, COLOR_REGLINE,
    )
    apply_hero_rcparams()
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Windows stdout/stderr UTF-8 shim
# ---------------------------------------------------------------------------

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ---------------------------------------------------------------------------
# Theme color tokens — must match docs/cross-domain-circuits.html CSS
# ---------------------------------------------------------------------------

COLOR_BOTTLENECK = '#e67e22'   # orange — phase 1 / bottleneck / Gemma
COLOR_POSTBOTTLE = '#8854d0'   # purple — post-bottleneck / Qwen
COLOR_NEUTRAL    = '#8b949e'   # grey
COLOR_TEXT       = '#1a1a1a'
COLOR_AXIS       = '#555555'
COLOR_MUTED      = '#8b949e'
COLOR_REGLINE    = '#3273dc'   # blue — regression line / high-sim matrix cells

# Convenience aliases used by individual heroes.
COLOR_GEMMA    = COLOR_BOTTLENECK
COLOR_QWEN     = COLOR_POSTBOTTLE
COLOR_HIGH_SIM = COLOR_REGLINE
COLOR_SCATTER  = COLOR_TEXT


# ---------------------------------------------------------------------------
# Matplotlib helpers
# ---------------------------------------------------------------------------

def setup_agg_backend() -> None:
    """Select the non-interactive Agg backend.

    Must be called before `import matplotlib.pyplot as plt`; otherwise the
    backend is locked to whatever was active at first import (often Qt on
    dev machines, which fails on CI / headless servers).
    """
    import matplotlib
    matplotlib.use('Agg')


def apply_hero_rcparams() -> None:
    """Apply the shared matplotlib rcParams used by the hero figures."""
    # Local import so this module can be imported before plt is loaded if
    # the caller hasn't yet called setup_agg_backend().
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        # DM Sans is loaded by the site; matplotlib will fall back gracefully
        # if it isn't installed locally.
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
# Saving helper
# ---------------------------------------------------------------------------

def save_hero_figure(fig, slug: str, output_dir: Path,
                     base_for_display: Path | None = None) -> tuple[Path, Path]:
    """Save `fig` as both `{slug}.svg` and `{slug}.png` and print an [OK].

    Uses `bbox_inches='tight'` for both formats so the cropping is consistent.
    Returns the (svg_path, png_path) tuple.

    `base_for_display` is the base directory to display paths relative to —
    if omitted, the absolute paths are printed.
    """
    import matplotlib.pyplot as plt
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    svg_path = output_dir / f'{slug}.svg'
    png_path = output_dir / f'{slug}.png'
    fig.savefig(svg_path, bbox_inches='tight')
    fig.savefig(png_path, bbox_inches='tight')

    if base_for_display is not None:
        try:
            svg_display = svg_path.relative_to(base_for_display)
            png_display = png_path.relative_to(base_for_display)
        except ValueError:
            svg_display = svg_path
            png_display = png_path
    else:
        svg_display = svg_path
        png_display = png_path

    print(f'  [OK] {svg_display}')
    print(f'  [OK] {png_display}')
    return svg_path, png_path
