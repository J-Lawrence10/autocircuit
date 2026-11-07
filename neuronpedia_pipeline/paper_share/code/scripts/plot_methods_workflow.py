"""Draw the primary feature-overlap workflow without inference or new analyses.

Only prompt text is read from data. All lettered feature sets and numerical
scores are a deliberately small teaching example, never empirical results.
"""
from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean
from textwrap import fill

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/model_extension/methods_diagram_20261107"
STEM = "figureS8_feature_overlap_workflow"
TITLE = "How questions become a feature-overlap comparison"
INPUT_PATHS = (
    "config/paper_control_manifest.csv",
    "scripts/whole_graph_analysis.py",
    "scripts/analyze_model_extension.py",
)
ILLUSTRATION_NOTICE = "Illustrative feature sets and scores, not measured results"
CAPTION = (
    "Primary feature-overlap workflow for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B. "
    "The four prompt roles are starting factual, same fact reworded, "
    "invented name in the starting sentence pattern, and invented name reworded. "
    "Exact chemistry prompts about gold and iron, plus invented name zorium, "
    "are development examples from the manifest, not evaluation questions. "
    "Hosted Neuronpedia graph exports are analyzed locally without local model "
    "inference. Eligibility requires four available representations after "
    "export/integrity checks, both factual highest-probability next tokens "
    "matching the expected token after trimming whitespace, and another "
    "eligible fact in the same model, subject, and development/evaluation set. "
    "Unique learned-feature identities are (family, layer, feature ID): "
    "positions collapse, but layers remain distinct. Embeddings, logits, "
    "reconstruction-error nodes, and nodes with missing or duplicated node IDs "
    "are omitted. Jaccard overlap J is shared unique features divided by "
    "distinct features in either set. Each starting set T_i is compared with "
    "its own rewording P_i and every other included factual rewording P_j in "
    "the same model/subject/set. The baseline is the mean of all those Jaccard "
    "overlaps, excluding i; iron illustrates one comparator, not the whole "
    "pool. Subtraction yields one difference per fact, M_i. Summaries, "
    "bootstrap intervals, and permutations within the same subject area concern facts, not "
    "graph pairs. Invented-name comparisons are separate controls, not the "
    "other-fact baseline; broad output-token-type matching is not the primary "
    "eligibility rule. Illustrative feature sets and scores, not measured "
    "results: {a,b,c} and {a,b,d} share a and b (green), while c and d are "
    "unshared (white), giving 2/4=0.50; an illustrative baseline of 0.30 gives "
    "+0.20. These values do not describe the gold or iron graphs. Letters "
    "denote identities, not concepts. Arrows show analysis steps, not causal "
    "pathways; overlap alone does not establish causal use or answer correctness."
)

INK = "#213747"
MUTED = "#607481"
BLUE = "#246B8B"
GREEN = "#397C6B"
RULE = "#D2DEE4"
PALE_BLUE = "#EFF5F8"
PALE_GREEN = "#EEF6F2"
PALE_GRAY = "#F6F8F9"
WHITE = "#FFFFFF"

# This synthetic example is intentionally independent of model outputs.
ILLUSTRATIVE_TARGET = frozenset("abc")
ILLUSTRATIVE_OWN = frozenset("abd")
ILLUSTRATIVE_OTHER = (frozenset("aef"), frozenset("abef"))


def source_paths() -> tuple[Path, ...]:
    """Return the manifest and implementation sources for provenance."""
    return tuple(ROOT / relative for relative in INPUT_PATHS)


def prompt_examples() -> dict[tuple[str, str], dict[str, str]]:
    """Read exact development examples, rejecting changed or absent roles."""
    keys = {
        ("gold_symbol", "target"),
        ("gold_symbol", "positive_paraphrase"),
        ("gold_symbol", "negative_same_template"),
        ("gold_symbol", "negative_nonce"),
        ("iron_symbol", "positive_paraphrase"),
    }
    with (ROOT / INPUT_PATHS[0]).open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle)
                if (row["pair_id"], row["role"]) in keys]
    examples = {(row["pair_id"], row["role"]): row for row in rows}
    assert len(rows) == len(examples) == len(keys), "Missing or duplicated example role"
    assert all(row["domain"] == "chemistry" and row["split"] == "development"
               for row in rows), "Examples must remain chemistry development prompts"
    return examples


def illustrative_jaccard(left, right) -> float:
    """Set arithmetic only; this function never reads an empirical graph."""
    left, right = set(left), set(right)
    return len(left & right) / len(left | right) if left | right else 0.0


def illustrative_scores() -> tuple[float, float, float]:
    """Toy two-comparator arithmetic, not the actual size of any baseline."""
    own = illustrative_jaccard(ILLUSTRATIVE_TARGET, ILLUSTRATIVE_OWN)
    other = mean(illustrative_jaccard(ILLUSTRATIVE_TARGET, values)
                 for values in ILLUSTRATIVE_OTHER)
    return own, other, own - other


def _box(ax, bounds, *, fill=WHITE, edge=RULE, lw=0.9, dashed=False):
    x, y, w, h = bounds
    patch = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0,rounding_size=0.009",
        facecolor=fill, edgecolor=edge, linewidth=lw,
        linestyle=(0, (4, 3)) if dashed else "solid", zorder=1,
    )
    ax.add_patch(patch)
    return patch


def _text(ax, x, y, text, *, size=10, color=INK, bold=False,
          ha="center", region=None, **kwargs):
    artist = ax.text(
        x, y, text, ha=ha, va="center", multialignment=ha, fontsize=size,
        color=color, fontweight="bold" if bold else "normal",
        linespacing=1.3, zorder=5, **kwargs,
    )
    if region is not None:
        ax.figure._methods_text_regions.append((artist, region))
    return artist


def _arrow(ax, start, end, *, color=MUTED, dashed=False, curve=0):
    arrow = FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=12,
        color=color, linewidth=1.15,
        linestyle=(0, (4, 3)) if dashed else "solid",
        connectionstyle=f"arc3,rad={curve}", zorder=2,
    )
    ax.add_patch(arrow)


def _tile(ax, x, y, value, *, shared=False, w=.025, h=.035):
    bounds = (x - w / 2, y - h / 2, w, h)
    _box(ax, bounds, fill=PALE_GREEN if shared else WHITE,
         edge=GREEN if shared else RULE)
    _text(ax, x, y, value, size=12, bold=True,
          color=GREEN if shared else BLUE, region=bounds)


def _graph_icon(ax, cx, cy):
    """Schematic export icon, not an empirical attribution graph."""
    points = [(cx-.045, cy+.025), (cx-.045, cy-.035),
              (cx, cy+.05), (cx, cy-.008), (cx, cy-.06),
              (cx+.045, cy+.025), (cx+.045, cy-.04)]
    for a, b in [(0, 2), (0, 3), (1, 3), (1, 4), (2, 5), (3, 5), (3, 6), (4, 6)]:
        ax.plot([points[a][0], points[b][0]], [points[a][1], points[b][1]],
                color=RULE, lw=1.6, zorder=2)
    for index, (x, y) in enumerate(points):
        # Ellipse correction keeps circles circular on the wide canvas.
        ax.scatter([x], [y], s=70, color=BLUE if index % 2 else GREEN,
                   edgecolor=WHITE, linewidth=1, zorder=3)


def _heading(ax, number, x, title):
    _text(ax, x, .878, f"{number}  {title}", size=12, bold=True, color=BLUE)


def build_figure():
    """Return a title-free Figure; the standard paper builder adds its title."""
    examples = prompt_examples()
    own, baseline, difference = illustrative_scores()
    with plt.rc_context({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                         "pdf.fonttype": 42, "ps.fonttype": 42}):
        fig = plt.figure(figsize=(15, 10), facecolor=WHITE)
        fig._methods_text_regions = []
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.axis("off")
        _text(ax, .5, .939,
              "PRIMARY FEATURE-OVERLAP ANALYSIS  |  Gemma-2-2B · Qwen3-1.7B · Qwen3-4B",
              size=10, color=MUTED)

        _heading(ax, 1, .17, "Four prompt roles")
        _heading(ax, 2, .425, "Export graphs")
        _heading(ax, 3, .65, "Check eligibility")
        _heading(ax, 4, .8875, "Keep unique features")

        # Exact prompt strings are wrapped for display, never shortened.
        prompt_roles = [
            ("target", "Starting factual question", BLUE, PALE_BLUE),
            ("positive_paraphrase", "Same fact, reworded", BLUE, PALE_BLUE),
            ("negative_same_template", "Invented name, same pattern", GREEN, PALE_GREEN),
            ("negative_nonce", "Invented name, reworded", GREEN, PALE_GREEN),
        ]
        for i, (role, label, color, bg) in enumerate(prompt_roles):
            y = .782 - i * .069
            bounds = (.025, y, .29, .062)
            _box(ax, bounds, fill=bg)
            _text(ax, .17, y+.047, label, size=9, bold=True, color=color, region=bounds)
            prompt = examples[("gold_symbol", role)]["prompt"]
            _text(ax, .17, y+.021, fill(prompt, width=33), size=10.2, region=bounds)
        _text(ax, .17, .551, "Gold + zorium: development examples", size=9, color=MUTED)

        export = (.35, .575, .15, .269)
        _box(ax, export, fill=PALE_GRAY)
        _text(ax, .425, .813, "Neuronpedia", size=12, bold=True, region=export)
        _text(ax, .425, .788, "exported graph files", size=9.5, region=export)
        _graph_icon(ax, .425, .707)
        _text(ax, .425, .616, "No local\nmodel inference", size=10, color=MUTED, region=export)
        _arrow(ax, (.319, .71), (.346, .71))

        eligibility = (.535, .575, .23, .269)
        _box(ax, eligibility)
        eligibility_rows = [
            (.793, "All four graphs available", "after export / integrity checks"),
            (.711, "Both factual top next tokens", "match the expected token\nafter trimming whitespace"),
            (.620, "Another eligible fact", "in the same model, subject, and set"),
        ]
        for n, (y, header, detail) in enumerate(eligibility_rows, 1):
            _text(ax, .65, y+.012, header, size=10.1, bold=True, region=eligibility)
            _text(ax, .65, y-.018, detail, size=9.2, color=MUTED, region=eligibility)
            if n < 3:
                ax.plot([.555, .745], [y-.049, y-.049], color=RULE, lw=.8)
        _arrow(ax, (.504, .71), (.531, .71))

        features = (.80, .575, .175, .269)
        _box(ax, features, fill=PALE_BLUE)
        _text(ax, .8875, .812, "Identity =", size=10, color=MUTED, region=features)
        _text(ax, .8875, .782, "family · layer · feature ID", size=10, bold=True, region=features)
        _text(ax, .8875, .752, "Retain the layer", size=9.5, color=BLUE, region=features)
        repeat_left = (.815, .682, .065, .047)
        repeat_right = (.895, .682, .065, .047)
        for bounds, position in [(repeat_left, 2), (repeat_right, 5)]:
            _box(ax, bounds, fill=WHITE)
            _text(ax, bounds[0]+bounds[2]/2, .705, f"a, position {position}",
                  size=9, region=bounds)
        _arrow(ax, (.8475, .680), (.877, .650), color=BLUE)
        _arrow(ax, (.9275, .680), (.898, .650), color=BLUE)
        _tile(ax, .8875, .638, "a", shared=True)
        _text(ax, .8875, .598, "Count each identity once", size=9.2, region=features)
        _arrow(ax, (.769, .71), (.796, .71))

        _text(ax, .65, .551,
              "Omit embeddings, logits, reconstruction-error nodes,\nand nodes with missing or duplicated node IDs.",
              size=9.2, color=MUTED)
        ax.plot([.025, .975], [.520, .520], color=RULE, lw=.8)
        _text(ax, .025, .490, "5  Compare each starting factual set", size=12,
              bold=True, color=BLUE, ha="left")
        _text(ax, .975, .490,
              "Same model · same subject · same development/evaluation set", size=10,
              color=MUTED, ha="right")

        target = (.025, .254, .17, .171)
        _box(ax, target, fill=PALE_BLUE)
        _text(ax, .11, .397, "Starting question", size=10.6, bold=True, region=target)
        _text(ax, .11, .366, r"Feature set $T_i$", size=11, region=target)
        for x, letter in zip([.074, .11, .146], "abc"):
            _tile(ax, x, .318, letter, shared=letter in "ab")
        _text(ax, .11, .276, "Gold example", size=9.2, color=MUTED, region=target)

        same = (.255, .347, .285, .112)
        _box(ax, same, fill=PALE_GREEN, edge="#BFD8CE")
        _text(ax, .3975, .435, r"Same fact, reworded $P_i$", size=11, bold=True, region=same)
        for x, letter in zip([.294, .330, .366], "abd"):
            _tile(ax, x, .389, letter, shared=letter in "ab")
        _text(ax, .461, .399, f"2 / 4 = {own:.2f}", size=14, bold=True, color=GREEN, region=same)
        _text(ax, .461, .371, "Jaccard overlap", size=9, color=MUTED, region=same)

        other = (.255, .151, .285, .155)
        _box(ax, other, fill=PALE_GRAY)
        _text(ax, .3975, .282, r"ALL other included factual rewordings $P_j$",
              size=10.2, bold=True, region=other)
        _text(ax, .3975, .247,
              examples[("iron_symbol", "positive_paraphrase")]["prompt"],
              size=10.2, region=other)
        _text(ax, .3975, .219, "Iron: one example from the pool; exclude fact i",
              size=9, color=MUTED, region=other)
        _text(ax, .3975, .179, rf"Mean $J(T_i, P_j)$ = {baseline:.2f}",
              size=13, bold=True, color=BLUE, region=other)
        _arrow(ax, (.196, .34), (.251, .402), color=GREEN)
        _arrow(ax, (.196, .34), (.251, .231), color=BLUE)

        result = (.605, .234, .17, .17)
        _box(ax, result, fill=PALE_GREEN, edge=GREEN, lw=1.1)
        _text(ax, .690, .378, "One difference per fact", size=10.5, bold=True, region=result)
        _text(ax, .690, .337, rf"$M_i$ = {own:.2f} − {baseline:.2f}",
              size=12, region=result)
        _text(ax, .690, .289, f"{difference:+.2f}", size=25, bold=True, color=GREEN, region=result)
        _text(ax, .690, .251, "same fact − other-fact mean", size=9, color=MUTED, region=result)
        _arrow(ax, (.542, .402), (.601, .331), color=GREEN)
        _arrow(ax, (.542, .23), (.601, .305), color=BLUE)

        summary = (.815, .217, .16, .212)
        _box(ax, summary)
        _text(ax, .895, .400, "6  Summarize across facts", size=10.5, bold=True,
              color=BLUE, region=summary)
        _text(ax, .895, .370, "Not graph pairs", size=10, bold=True, region=summary)
        _text(ax, .895, .326, r"$M_1\quad M_2\quad\cdots\quad M_n$",
              size=14, color=GREEN, region=summary)
        _text(ax, .895, .270, "Mean + bootstrap intervals\nWithin-subject permutations",
              size=9.5, color=MUTED, region=summary)
        _arrow(ax, (.777, .32), (.811, .32))

        control = (.025, .116, .17, .091)
        _box(ax, control, fill=PALE_GREEN, edge=GREEN, dashed=True)
        _text(ax, .11, .184, "Invented-name comparisons", size=9.6, bold=True,
              color=GREEN, region=control)
        _text(ax, .11, .148, "Separate control branch\nNot the other-fact baseline", size=9.1, region=control)
        _arrow(ax, (.11, .252), (.11, .209), color=GREEN, dashed=True)

        # The notice explicitly covers all letter labels and numerical examples.
        _text(ax, .615, .119, ILLUSTRATION_NOTICE, size=10, bold=True, color=GREEN)
        _text(ax, .615, .092, "Shared: a, b (green). Not shared: c, d (white). Letters stand for feature identities, not concepts.",
              size=9, color=MUTED)
        ax.plot([.025, .975], [.067, .067], color=RULE, lw=.8)
        _text(ax, .025, .039,
              r"$M_i = J(T_i, P_i) - \mathrm{mean}_{j\ne i}\,J(T_i, P_j)$",
              size=11, ha="left")
        _text(ax, .975, .039, "Arrows show analysis steps, not causal pathways.", size=9.5,
              color=MUTED, ha="right")
    return fig


def validate_figure(fig) -> None:
    """Check physical text bounds, card fit, and title headroom after rendering."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        for artist in ax.texts:
            bounds = artist.get_window_extent(renderer)
            assert artist.get_fontsize() >= 9, artist.get_text()
            assert bounds.x0 >= 0 and bounds.x1 <= fig.bbox.width, artist.get_text()
            assert bounds.y0 >= 0 and bounds.y1 <= fig.bbox.height * .958, artist.get_text()
    for artist, (x, y, w, h) in fig._methods_text_regions:
        bounds = artist.get_window_extent(renderer)
        left, bottom = artist.axes.transData.transform((x, y))
        right, top = artist.axes.transData.transform((x+w, y+h))
        assert bounds.x0 >= left and bounds.x1 <= right, artist.get_text()
        assert bounds.y0 >= bottom and bounds.y1 <= top, artist.get_text()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig = build_figure()
    validate_figure(fig)
    fig.suptitle(TITLE, x=.025, y=.985, ha="left", fontsize=20,
                 fontweight="bold", color=INK)
    with plt.rc_context({"svg.fonttype": "none"}):
        for extension in ("png", "svg"):
            path = OUT / f"{STEM}.{extension}"
            fig.savefig(path, dpi=300, facecolor=WHITE)
            print(path)
    plt.close(fig)


if __name__ == "__main__":
    main()
