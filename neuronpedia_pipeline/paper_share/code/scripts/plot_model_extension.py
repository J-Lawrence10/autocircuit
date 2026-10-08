#!/usr/bin/env python3
"""Generate publication figures for the prospective Qwen3-4B extension."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
ORIGINAL_DIR = BASE_DIR / "data" / "publication_analysis"
EXTENSION_ROOT = BASE_DIR / "data" / "model_extension"
COLORS = {"Gemma-2-2B": "#0072B2", "Qwen3-1.7B": "#CC79A7", "Qwen3-4B": "#D55E00"}
DOMAIN_MARKERS = {"chemistry": "o", "geography": "s", "history": "^"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ["png", "pdf", "svg"]:
        fig.savefig(output_dir / f"{stem}.{suffix}", dpi=300 if suffix == "png" else None, bbox_inches="tight")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="qwen3-4b")
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()

    original = load_json(ORIGINAL_DIR / "whole_graph_results.json")
    extension_path = EXTENSION_ROOT / args.model / "analysis" / "model_extension_results.json"
    extension = load_json(extension_path)
    if not args.allow_incomplete and extension["audit_counts"]["ok"] != 147:
        raise SystemExit(f"extension cohort is incomplete: {extension['audit_counts']}")
    output_dir = EXTENSION_ROOT / args.model / "figures"

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "figure.dpi": 150,
        }
    )
    fig, axes = plt.subplots(1, 3, figsize=(11.8, 3.7), constrained_layout=True)

    # Panel a: fact-level held-out margins, preserving facts as the inferential units.
    controlled_sets = [
        ("Gemma-2-2B", original["models"]["gemma"]),
        ("Qwen3-1.7B", original["models"]["qwen"]),
        ("Qwen3-4B", extension["controlled"]),
    ]
    ax = axes[0]
    for model_index, (label, result) in enumerate(controlled_sets):
        rows = [row for row in result["per_fact"] if row["split"] == "held_out"]
        for point_index, row in enumerate(rows):
            jitter = (point_index - (len(rows) - 1) / 2) * 0.035
            ax.scatter(
                model_index + jitter,
                row["feature_jaccard__margin_other_factual_mean"],
                s=26,
                marker=DOMAIN_MARKERS[row["domain"]],
                color=COLORS[label],
                alpha=0.9,
            )
        summary = result["heldout_primary"]
        if summary.get("n", 0):
            ax.errorbar(
                model_index,
                summary["mean"],
                yerr=[[summary["mean"] - summary["ci95"][0]], [summary["ci95"][1] - summary["mean"]]],
                fmt="D",
                color="black",
                markersize=5,
                capsize=4,
                linewidth=1.2,
            )
            ax.text(model_index, summary["ci95"][1] + 0.018, f"n={summary['n']}", ha="center")
    ax.axhline(0, color="#777777", linestyle="--", linewidth=0.8)
    ax.set_xticks(range(3), [item[0] for item in controlled_sets], rotation=15, ha="right")
    ax.set_ylabel("Same-fact Jaccard advantage")
    ax.set_title("a  Held-out fact signal", loc="left")

    # Panel b: crossed fact and format effects, original Gemma versus extension Qwen.
    ax = axes[1]
    crossed_sets = [
        ("Gemma-2-2B", original["format_variation"]),
        ("Qwen3-4B", extension["crossed"]),
    ]
    positions = np.arange(2)
    width = 0.34
    for offset, effect in [(-width / 2, "fact"), (width / 2, "format")]:
        values = [item[1]["metrics"]["feature_jaccard"][f"{effect}_effect"] for item in crossed_sets]
        bars = ax.bar(
            positions + offset,
            values,
            width,
            color="#56B4E9" if effect == "fact" else "#E69F00",
            label=f"{effect.title()} effect",
        )
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.004, f"{value:.3f}", ha="center", fontsize=7)
    ax.axhline(0, color="#777777", linewidth=0.8)
    ax.set_xticks(positions, [item[0] for item in crossed_sets], rotation=15, ha="right")
    ax.set_ylabel("Jaccard effect over baseline")
    ax.set_title("b  Fact versus prompt-form effects", loc="left")
    ax.legend(frameon=False, fontsize=7, loc="upper left")

    # Panel c: eligible held-out facts by domain, making domain coverage visible.
    ax = axes[2]
    domains = ["chemistry", "geography", "history"]
    bottom = np.zeros(3)
    domain_colors = {"chemistry": "#0072B2", "geography": "#009E73", "history": "#E69F00"}
    for domain in domains:
        values = []
        for _, result in controlled_sets:
            summary = result.get("heldout_domains", {}).get(domain, {})
            values.append(summary.get("n", 0))
        ax.bar(positions if len(positions) == 3 else np.arange(3), values, bottom=bottom, color=domain_colors[domain], label=domain.title())
        bottom += np.asarray(values)
    ax.set_xticks(np.arange(3), [item[0] for item in controlled_sets], rotation=15, ha="right")
    ax.set_ylabel("Eligible held-out facts")
    ax.set_title("c  Domain coverage", loc="left")
    ax.legend(frameon=False, fontsize=7)
    save_figure(fig, output_dir, "figure3_model_extension")
    plt.close(fig)

    conversion = load_json(EXTENSION_ROOT / args.model / "analysis" / "conversion_audit.json")
    graph_audit = load_json(EXTENSION_ROOT / args.model / "analysis" / "graph_audit.json")
    ok_conversion = [row for row in conversion if row.get("status") == "ok"]
    ok_graphs = [row for row in graph_audit if row.get("status") == "ok"]

    fig, axes = plt.subplots(1, 3, figsize=(11.8, 3.6), constrained_layout=True)
    ax = axes[0]
    by_design = [
        (design, [row for row in ok_conversion if row["design"] == design])
        for design in ["controlled", "crossed"]
    ]
    rates = [100 * sum(row["raw_ambiguous_node_id_count"] > 0 for row in rows) / len(rows) for _, rows in by_design]
    bars = ax.bar(range(2), rates, color=["#D55E00", "#E69F00"], width=0.6)
    integrity_upper = max(5.0, max(rates, default=0.0) * 1.25)
    ax.set_ylim(0, integrity_upper)
    for bar, value, (_, rows) in zip(bars, rates, by_design):
        count = sum(row["raw_ambiguous_node_id_count"] > 0 for row in rows)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + integrity_upper * 0.04,
            f"{count}/{len(rows)}",
            ha="center",
        )
    ax.set_xticks(range(2), ["Controlled", "Crossed"])
    ax.set_ylabel("Exports with duplicate node IDs (%)")
    ax.set_title("a  Qwen3-4B exporter integrity", loc="left")

    ax = axes[1]
    distributions = [
        [100 * row["error_influence_fraction"] for row in ok_graphs if row["design"] == design]
        for design in ["controlled", "crossed"]
    ]
    box = ax.boxplot(distributions, patch_artist=True, widths=0.55, showfliers=False)
    for patch, color in zip(box["boxes"], ["#D55E00", "#E69F00"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.65)
    ax.set_xticks([1, 2], ["Controlled", "Crossed"])
    ax.set_ylabel("Reconstruction-error influence (%)")
    ax.set_title("b  Decomposition burden", loc="left")

    ax = axes[2]
    controlled_audits = [row for row in ok_graphs if row["design"] == "controlled" and row["role"] in {"target", "positive_paraphrase"}]
    correct = sum(row.get("top_token_matches_expected", False) for row in controlled_audits)
    incorrect = len(controlled_audits) - correct
    ax.bar([0, 1], [correct, incorrect], color=["#009E73", "#D55E00"], width=0.6)
    ax.set_xticks([0, 1], ["Expected token", "Other token"])
    ax.set_ylabel("Factual prompt graphs")
    ax.set_title("c  Output correctness", loc="left")
    for index, value in enumerate([correct, incorrect]):
        ax.text(index, value + 1, str(value), ha="center")
    save_figure(fig, output_dir, "figure4_extension_quality")
    plt.close(fig)


if __name__ == "__main__":
    main()
