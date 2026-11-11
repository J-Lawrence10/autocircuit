#!/usr/bin/env python3
"""Generate the publication figures from validated whole-graph results."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ANALYSIS = BASE_DIR / "data" / "publication_analysis"

DOMAIN_COLORS = {
    "chemistry": "#0072B2",
    "geography": "#009E73",
    "history": "#D55E00",
}
DOMAIN_MARKERS = {"chemistry": "o", "geography": "s", "history": "^"}
MODEL_COLORS = {"gemma": "#0072B2", "qwen": "#CC79A7"}


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.labelsize": 9,
            "axes.titlesize": 9.5,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.7,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.dpi": 400,
        }
    )


def save_all(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ["png", "pdf", "svg"]:
        fig.savefig(output_dir / f"{stem}.{suffix}", bbox_inches="tight", facecolor="white")


def p_label(value: float) -> str:
    return f"p={value:.4f}" if value >= 0.001 else "p<0.001"


def plot_main(results: dict, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.35), gridspec_kw={"wspace": 0.36})

    ax = axes[0]
    for model_index, model in enumerate(["gemma", "qwen"]):
        analysis = results["models"][model]
        heldout = [row for row in analysis["per_fact"] if row["split"] == "held_out"]
        offsets = np.linspace(-0.12, 0.12, len(heldout)) if heldout else []
        for offset, row in zip(offsets, sorted(heldout, key=lambda item: (item["domain"], item["pair_id"]))):
            ax.scatter(
                model_index + offset,
                row["feature_jaccard__margin_other_factual_mean"],
                s=31,
                marker=DOMAIN_MARKERS[row["domain"]],
                facecolor=DOMAIN_COLORS[row["domain"]],
                edgecolor="white",
                linewidth=0.45,
                alpha=0.92,
                zorder=3,
            )
        primary = analysis["heldout_primary"]
        ax.errorbar(
            model_index,
            primary["mean"],
            yerr=[[primary["mean"] - primary["ci95"][0]], [primary["ci95"][1] - primary["mean"]]],
            fmt="D",
            markersize=5,
            color="black",
            capsize=3,
            linewidth=1.2,
            zorder=4,
        )
        ax.text(
            model_index,
            primary["ci95"][1] + 0.025,
            f"n={primary['n']}; {p_label(primary['exact_one_sided_sign_flip_p'])}",
            ha="center",
            va="bottom",
            fontsize=7.2,
        )
    ax.axhline(0, color="#777777", linewidth=0.8, linestyle="--", zorder=1)
    ax.set_xticks([0, 1], ["Gemma-2-2B", "Qwen3-1.7B"])
    ax.set_ylabel("Same-fact Jaccard advantage")
    ax.set_title("a  Held-out fact signal", loc="left")
    ax.set_ylim(-0.08, 0.56)
    handles = [
        mpl.lines.Line2D(
            [], [], linestyle="", marker=DOMAIN_MARKERS[domain], color=DOMAIN_COLORS[domain], label=domain.title()
        )
        for domain in ["chemistry", "geography", "history"]
    ]
    ax.legend(handles=handles, frameon=False, loc="upper right")

    categories = [
        "different_fact_different_format",
        "same_fact_different_format",
        "different_fact_same_format",
    ]
    labels = ["Different fact\nDifferent format", "Same fact\nDifferent format", "Different fact\nSame format"]
    for panel_index, metric in enumerate(["feature_jaccard", "feature_influence_cosine"], start=1):
        ax = axes[panel_index]
        metric_data = results["format_variation"]["metrics"][metric]
        for domain in ["chemistry", "geography", "history"]:
            values = [metric_data["categories"][category]["domain_means"][domain] for category in categories]
            ax.plot(
                range(3),
                values,
                color=DOMAIN_COLORS[domain],
                marker=DOMAIN_MARKERS[domain],
                linewidth=1.0,
                markersize=4.2,
                alpha=0.8,
                label=domain.title(),
            )
        means = [metric_data["categories"][category]["mean"] for category in categories]
        ax.scatter(range(3), means, marker="D", s=28, color="black", zorder=4, label="Across-domain mean")
        ax.set_xticks(range(3), labels)
        ax.set_ylabel("Feature Jaccard" if metric == "feature_jaccard" else "Influence-weighted cosine")
        ax.set_title(
            ("b  Crossed fact × format" if panel_index == 1 else "c  Weighted sensitivity"),
            loc="left",
        )
        ax.grid(axis="y", linewidth=0.45, color="#D0D0D0")
        fact_p = metric_data["fact_effect_permutation_p"]
        format_p = metric_data["format_effect_permutation_p"]
        ax.text(
            0.02,
            0.98,
            f"Fact effect {metric_data['fact_effect']:.3f} ({p_label(fact_p)})\n"
            f"Format effect {metric_data['format_effect']:.3f} ({p_label(format_p)})",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=7.2,
        )
    axes[1].set_ylim(0.10, 0.46)
    axes[2].set_ylim(0.20, 0.71)
    fig.text(
        0.5,
        -0.02,
        "Points are fact-level units in a and domain means in b–c; black diamonds are means. Error bars are fact-bootstrap 95% CIs.",
        ha="center",
        va="top",
        fontsize=7.4,
    )
    save_all(fig, output_dir, "figure1_fact_and_format")
    plt.close(fig)


def plot_quality(results: dict, converted: list[dict], raw: list[dict], format_audit: list[dict], output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.25), gridspec_kw={"wspace": 0.38})

    ax = axes[0]
    positions = []
    labels = []
    position = 0
    for model in ["gemma", "qwen"]:
        robustness = results["models"][model]["robustness"]["output_type_matched_controls"]
        for control in ["same_template_nonce", "paraphrased_nonce"]:
            summary = robustness[control]
            positions.append(position)
            labels.append("Same template" if control == "same_template_nonce" else "Paraphrased nonce")
            if summary["n"]:
                ax.errorbar(
                    position,
                    summary["mean"],
                    yerr=[[summary["mean"] - summary["ci95"][0]], [summary["ci95"][1] - summary["mean"]]],
                    fmt="o",
                    color=MODEL_COLORS[model],
                    capsize=3,
                    linewidth=1.2,
                    markersize=5,
                )
                ax.text(position, summary["ci95"][1] + 0.012, f"n={summary['n']}", ha="center", fontsize=7)
            position += 1
        position += 0.55
    ax.axhline(0, color="#777777", linewidth=0.8, linestyle="--")
    ax.set_xticks(positions, labels, rotation=25, ha="right")
    ax.set_ylabel("Paraphrase Jaccard advantage")
    ax.set_title("a  Output-type-matched controls", loc="left")
    ax.text(0.22, -0.34, "Gemma", transform=ax.transAxes, ha="center", color=MODEL_COLORS["gemma"], fontsize=7.5)
    ax.text(0.80, -0.34, "Qwen", transform=ax.transAxes, ha="center", color=MODEL_COLORS["qwen"], fontsize=7.5)

    ax = axes[1]
    raw_groups = {
        "Gemma\ncontrolled": [row for row in raw if row.get("model_dir") == "gemma-2-2b"],
        "Qwen\ncontrolled": [row for row in raw if row.get("model_dir") == "qwen3-1-7b"],
        "Gemma\nformat": format_audit,
    }
    ambiguity_rates = [
        100 * sum((row.get("ambiguous_node_id_count") or 0) > 0 for row in rows) / len(rows)
        for rows in raw_groups.values()
    ]
    bars = ax.bar(range(3), ambiguity_rates, color=["#0072B2", "#CC79A7", "#009E73"], width=0.62)
    for bar, value, rows in zip(bars, ambiguity_rates, raw_groups.values()):
        count = sum((row.get("ambiguous_node_id_count") or 0) > 0 for row in rows)
        label = f"{count}/{len(rows)}"
        if count == 0:
            label += "\nnone detected"
        ax.text(bar.get_x() + bar.get_width() / 2, value + 2, label, ha="center", fontsize=7.3)
    ax.set_xticks(range(3), raw_groups.keys())
    ax.set_ylabel("Exports with duplicate node IDs (%)")
    ax.set_ylim(0, 82)
    ax.set_title("b  Raw exports with duplicate node IDs", loc="left")
    ax.grid(axis="y", linewidth=0.45, color="#D0D0D0")

    ax = axes[2]
    distributions = []
    distribution_labels = []
    colors = []
    for label, rows, color in [
        ("Gemma\ncontrolled", [r for r in converted if r.get("model_dir") == "gemma-2-2b" and r.get("status") == "ok"], "#0072B2"),
        ("Qwen\ncontrolled", [r for r in converted if r.get("model_dir") == "qwen3-1-7b" and r.get("status") == "ok"], "#CC79A7"),
        ("Gemma\nformat", format_audit, "#009E73"),
    ]:
        distributions.append([100 * row["error_influence_fraction"] for row in rows])
        distribution_labels.append(label)
        colors.append(color)
    box = ax.boxplot(distributions, patch_artist=True, widths=0.55, showfliers=False, medianprops={"color": "black"})
    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.65)
        patch.set_edgecolor(color)
    ax.set_xticks(range(1, 4), distribution_labels)
    ax.set_ylabel("Reconstruction-error influence (%)")
    ax.set_title("c  Decomposition burden", loc="left")
    ax.grid(axis="y", linewidth=0.45, color="#D0D0D0")
    save_all(fig, output_dir, "figure2_controls_and_quality")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output_dir = args.output_dir or args.analysis_dir / "figures"
    configure_style()
    results = json.loads((args.analysis_dir / "whole_graph_results.json").read_text())
    converted = json.loads((args.analysis_dir / "converted_graph_audit.json").read_text())
    raw = json.loads((args.analysis_dir / "raw_graph_audit.json").read_text())
    format_audit = json.loads((args.analysis_dir / "format_graph_audit.json").read_text())
    plot_main(results, output_dir)
    plot_quality(results, converted, raw, format_audit, output_dir)
    print(f"Wrote figures to {output_dir}")


if __name__ == "__main__":
    main()
