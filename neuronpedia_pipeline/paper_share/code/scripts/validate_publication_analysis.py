#!/usr/bin/env python3
"""Fail-closed validator for the whole-graph publication artifact."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DIR = BASE_DIR / "data" / "publication_analysis"


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis_dir", nargs="?", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    root = args.analysis_dir
    failures: list[str] = []
    warnings: list[str] = []

    required = [
        "whole_graph_results.json",
        "converted_graph_audit.json",
        "raw_graph_audit.json",
        "format_graph_audit.json",
        "gemma_per_fact.csv",
        "qwen_per_fact.csv",
        "format_pairwise.csv",
    ]
    for name in required:
        check((root / name).is_file() and (root / name).stat().st_size > 0, f"missing or empty {name}", failures)
    if failures:
        raise SystemExit("VALIDATION FAILED\n" + "\n".join(failures))

    results = json.loads((root / "whole_graph_results.json").read_text(encoding="utf-8"))
    converted = json.loads((root / "converted_graph_audit.json").read_text(encoding="utf-8"))
    raw = json.loads((root / "raw_graph_audit.json").read_text(encoding="utf-8"))
    format_audit = json.loads((root / "format_graph_audit.json").read_text(encoding="utf-8"))

    check(results.get("schema_version") == "whole-graph-publication-v1", "wrong result schema", failures)
    check(set(results.get("models", {})) == {"gemma", "qwen"}, "expected Gemma and Qwen results", failures)
    check("format_variation" in results, "missing format-variation result", failures)

    converted_status = Counter(row.get("status") for row in converted)
    check(converted_status.get("error", 0) == 0, "converted audit contains parse errors", failures)
    check(converted_status.get("prompt_mismatch", 0) == 0, "converted audit contains prompt mismatch", failures)
    check(
        all((row.get("dangling_edge_count") or 0) == 0 for row in converted if row.get("status") == "ok"),
        "converted audit contains dangling edges",
        failures,
    )
    check(
        all((row.get("duplicate_exact_edge_count") or 0) == 0 for row in converted if row.get("status") == "ok"),
        "converted audit contains exact duplicate edges",
        failures,
    )
    check(
        all(len(str(row.get("sha256", ""))) == 64 for row in converted if row.get("status") == "ok"),
        "converted audit has missing SHA-256",
        failures,
    )
    check(len(raw) == converted_status.get("ok", 0), "raw and converted present-graph counts differ", failures)
    check(all(row.get("status") == "ok" for row in raw), "raw audit contains failures", failures)
    check(all(len(str(row.get("sha256", ""))) == 64 for row in raw), "raw audit has missing SHA-256", failures)
    check(len(format_audit) == 27, "format audit must contain 27 graphs", failures)
    check(all(row.get("status") == "ok" for row in format_audit), "format audit contains failures", failures)

    required_domains = {"chemistry", "geography", "history"}
    for model, analysis in results["models"].items():
        per_fact = analysis.get("per_fact", [])
        heldout = [row for row in per_fact if row.get("split") == "held_out"]
        values = [float(row["feature_jaccard__margin_other_factual_mean"]) for row in heldout]
        stored = analysis["heldout_primary"]
        check(stored["n"] == len(values), f"{model}: held-out n mismatch", failures)
        check(
            math.isclose(stored["mean"], float(np.mean(values)), rel_tol=0, abs_tol=1e-12),
            f"{model}: held-out mean mismatch",
            failures,
        )
        check(stored["positive_n"] == sum(value > 0 for value in values), f"{model}: positive count mismatch", failures)
        present_domains = set(analysis.get("heldout_domains", {}))
        expected_gate_b = bool(
            analysis.get("pooled_confirmatory_test_pass")
            and present_domains == required_domains
            and all(summary["mean"] > 0 for summary in analysis.get("heldout_domains", {}).values())
        )
        check(
            bool(analysis.get("gate_b_confirmatory_fact_identity_pass")) == expected_gate_b,
            f"{model}: Gate B is inconsistent with required-domain rule",
            failures,
        )
        check("robustness" in analysis, f"{model}: missing robustness block", failures)
        if present_domains != required_domains:
            warnings.append(f"{model}: held-out domains are {sorted(present_domains)}, not all three domains")

    pairwise = results["format_variation"].get("pairwise_records", [])
    category_counts = Counter(row["category"] for row in pairwise)
    check(len(pairwise) == 108, "format comparison must contain 108 within-domain graph pairs", failures)
    check(category_counts["same_fact_different_format"] == 27, "wrong same-fact format count", failures)
    check(category_counts["different_fact_same_format"] == 27, "wrong same-format fact count", failures)
    check(category_counts["different_fact_different_format"] == 54, "wrong baseline pair count", failures)
    for metric, summary in results["format_variation"]["metrics"].items():
        check(summary["permutation_runs"] == 10_000, f"{metric}: wrong permutation count", failures)
        check(0 <= summary["fact_effect_permutation_p"] <= 1, f"{metric}: invalid fact p", failures)
        check(0 <= summary["format_effect_permutation_p"] <= 1, f"{metric}: invalid format p", failures)

    report = {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
        "counts": {
            "converted_status": dict(converted_status),
            "raw_graphs": len(raw),
            "format_graphs": len(format_audit),
            "format_pairwise": len(pairwise),
        },
    }
    (root / "validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if failures:
        raise SystemExit("VALIDATION FAILED\n" + "\n".join(failures))
    print("VALIDATION PASSED")
    for warning in warnings:
        print(f"WARNING: {warning}")


if __name__ == "__main__":
    main()
