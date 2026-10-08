#!/usr/bin/env python3
"""Registered whole-graph analysis for prospective model-extension cohorts."""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from whole_graph_analysis import (  # noqa: E402
    analyze_controlled,
    holm_adjust,
    jaccard,
    json_ready,
    normalize_prompt,
    permutation_p,
    read_json_with_hash,
    sparse_cosine,
    summarize_graph,
)

OUTPUT_ROOT = BASE_DIR / "data" / "model_extension"
PROTOCOL = BASE_DIR / "docs" / "papers" / "MODEL_EXTENSION_PROTOCOL.md"
SEED = 20260830


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(payload), indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(json_ready(value), sort_keys=True)
                    if isinstance(value, (dict, list, tuple, set))
                    else value
                    for key, value in row.items()
                }
            )


def load_jobs(model_root: Path) -> list[dict[str, str]]:
    with (model_root / "jobs.csv").open("r", encoding="utf-8", newline="") as handle:
        jobs = list(csv.DictReader(handle))
    if len(jobs) != 147:
        raise ValueError(f"expected 147 registered jobs, found {len(jobs)}")
    return jobs


def load_representations(
    model: str, jobs: list[dict[str, str]]
) -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[str, str, str], dict[str, Any]],
    list[dict[str, Any]],
]:
    controlled: dict[tuple[str, str], dict[str, Any]] = {}
    crossed: dict[tuple[str, str, str], dict[str, Any]] = {}
    audits: list[dict[str, Any]] = []
    for index, job in enumerate(jobs, 1):
        raw_path = BASE_DIR / job["raw_graph_path"]
        path = raw_path.with_name("converted_graph.json")
        base = {
            "model_id": model,
            "design": job["design"],
            "job_id": job["job_id"],
            "pair_id": job["fact_id"],
            "fact_id": job["fact_id"],
            "role": job["role"],
            "format": job["format"],
            "domain": job["domain"],
            "split": job["split"],
            "manifest_prompt": job["prompt"],
            "expected_token": job["expected_token"],
            "path": str(path.relative_to(BASE_DIR)),
        }
        if not path.exists():
            audits.append({**base, "status": "missing"})
            continue
        try:
            graph, digest = read_json_with_hash(path)
            audit, representation = summarize_graph(
                graph, path=path, file_sha256=digest, raw_schema=False
            )
            prompt_matches = normalize_prompt(str(audit.get("prompt") or "")) == normalize_prompt(job["prompt"])
            integrity_ok = (
                audit["missing_node_ids"] == 0
                and audit["ambiguous_node_id_count"] == 0
                and audit["dangling_edge_count"] == 0
                and audit["nonfinite_edge_count"] == 0
            )
            status = "ok" if prompt_matches and integrity_ok else (
                "prompt_mismatch" if not prompt_matches else "integrity_failure"
            )
            top_matches = str(audit.get("top_token") or "").strip() == job["expected_token"].strip()
            audit.update(base)
            audit["status"] = status
            audit["top_token_matches_expected"] = top_matches
            audits.append(audit)
            if status != "ok":
                continue
            representation.update(base)
            representation["top_token_matches_expected"] = top_matches
            if job["design"] == "controlled":
                controlled[(job["fact_id"], job["role"])] = representation
            else:
                crossed[(job["domain"], job["fact_id"], job["format"])] = representation
        except Exception as error:
            audits.append({**base, "status": "error", "error": repr(error)})
        print(f"[{model} {index:03d}/147] {job['job_id']} {audits[-1]['status']}", flush=True)
    return controlled, crossed, audits


def crossed_analysis(
    representations: Mapping[tuple[str, str, str], dict[str, Any]],
    *,
    permutation_runs: int,
    seed: int,
) -> dict[str, Any]:
    if len(representations) != 27:
        return {"status": "incomplete", "graph_n": len(representations), "metrics": {}, "pairwise_records": []}
    records: list[dict[str, Any]] = []
    for domain in sorted({key[0] for key in representations}):
        keys = sorted(key for key in representations if key[0] == domain)
        for left_key, right_key in itertools.combinations(keys, 2):
            _, left_fact, left_format = left_key
            _, right_fact, right_format = right_key
            if left_fact == right_fact and left_format != right_format:
                category = "same_fact_different_format"
            elif left_fact != right_fact and left_format == right_format:
                category = "different_fact_same_format"
            elif left_fact != right_fact and left_format != right_format:
                category = "different_fact_different_format"
            else:
                continue
            records.append(
                {
                    "domain": domain,
                    "left_fact": left_fact,
                    "right_fact": right_fact,
                    "left_format": left_format,
                    "right_format": right_format,
                    "category": category,
                    "feature_jaccard": jaccard(
                        representations[left_key]["features"], representations[right_key]["features"]
                    ),
                    "feature_influence_cosine": sparse_cosine(
                        representations[left_key]["feature_weights"],
                        representations[right_key]["feature_weights"],
                    ),
                }
            )

    def statistic(rows: list[dict[str, Any]], metric: str, category_a: str, category_b: str) -> float:
        per_domain = []
        for domain in sorted({row["domain"] for row in rows}):
            a = [row[metric] for row in rows if row["domain"] == domain and row["category"] == category_a]
            b = [row[metric] for row in rows if row["domain"] == domain and row["category"] == category_b]
            per_domain.append(float(np.mean(a)) - float(np.mean(b)))
        return float(np.mean(per_domain))

    rng = random.Random(seed)
    metrics: dict[str, Any] = {}
    keys = sorted(representations)
    domains = sorted({key[0] for key in keys})
    for metric in ["feature_jaccard", "feature_influence_cosine"]:
        similarity_matrix = {}
        for left_key, right_key in itertools.combinations(keys, 2):
            if metric == "feature_jaccard":
                value = jaccard(representations[left_key]["features"], representations[right_key]["features"])
            else:
                value = sparse_cosine(
                    representations[left_key]["feature_weights"], representations[right_key]["feature_weights"]
                )
            similarity_matrix[(left_key, right_key)] = value

        def matrix_similarity(left_key, right_key):
            ordered = (left_key, right_key) if left_key < right_key else (right_key, left_key)
            return similarity_matrix[ordered]

        categories = {}
        for category in [
            "same_fact_different_format",
            "different_fact_same_format",
            "different_fact_different_format",
        ]:
            category_rows = [row for row in records if row["category"] == category]
            categories[category] = {
                "n_pairs": len(category_rows),
                "mean": float(np.mean([row[metric] for row in category_rows])),
                "domain_means": {
                    domain: float(np.mean([row[metric] for row in category_rows if row["domain"] == domain]))
                    for domain in domains
                },
            }
        fact_effect = statistic(
            records, metric, "same_fact_different_format", "different_fact_different_format"
        )
        format_effect = statistic(
            records, metric, "different_fact_same_format", "different_fact_different_format"
        )
        null_fact: list[float] = []
        null_format: list[float] = []
        for _ in range(permutation_runs):
            fact_assignment = {}
            format_assignment = {}
            for domain in domains:
                facts = sorted({key[1] for key in keys if key[0] == domain})
                formats = sorted({key[2] for key in keys if key[0] == domain})
                for fmt in formats:
                    shuffled = facts[:]
                    rng.shuffle(shuffled)
                    for old_fact, new_fact in zip(facts, shuffled):
                        fact_assignment[(domain, new_fact, fmt)] = (domain, old_fact, fmt)
                for fact in facts:
                    shuffled = formats[:]
                    rng.shuffle(shuffled)
                    for old_format, new_format in zip(formats, shuffled):
                        format_assignment[(domain, fact, new_format)] = (domain, fact, old_format)

            def assigned_rows(assignment):
                output = []
                for domain in domains:
                    assigned_keys = sorted(key for key in assignment if key[0] == domain)
                    for left_key, right_key in itertools.combinations(assigned_keys, 2):
                        _, left_fact, left_format = left_key
                        _, right_fact, right_format = right_key
                        if left_fact == right_fact and left_format != right_format:
                            category = "same_fact_different_format"
                        elif left_fact != right_fact and left_format == right_format:
                            category = "different_fact_same_format"
                        elif left_fact != right_fact and left_format != right_format:
                            category = "different_fact_different_format"
                        else:
                            continue
                        output.append(
                            {
                                "domain": domain,
                                "category": category,
                                metric: matrix_similarity(assignment[left_key], assignment[right_key]),
                            }
                        )
                return output

            fact_rows = assigned_rows(fact_assignment)
            format_rows = assigned_rows(format_assignment)
            null_fact.append(
                statistic(fact_rows, metric, "same_fact_different_format", "different_fact_different_format")
            )
            null_format.append(
                statistic(format_rows, metric, "different_fact_same_format", "different_fact_different_format")
            )
        metrics[metric] = {
            "categories": categories,
            "fact_effect": fact_effect,
            "fact_effect_permutation_p": permutation_p(fact_effect, null_fact),
            "format_effect": format_effect,
            "format_effect_permutation_p": permutation_p(format_effect, null_format),
            "permutation_runs": permutation_runs,
        }
    return {"status": "complete", "graph_n": 27, "metrics": metrics, "pairwise_records": records}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", default=["qwen3-4b"])
    parser.add_argument("--bootstrap-runs", type=int, default=10_000)
    parser.add_argument("--permutation-runs", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    all_results: dict[str, Any] = {
        "schema_version": "model-extension-v1",
        "protocol": str(PROTOCOL.relative_to(BASE_DIR)),
        "seed": args.seed,
        "bootstrap_runs": args.bootstrap_runs,
        "permutation_runs": args.permutation_runs,
        "models": {},
    }
    loaded: dict[str, tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]] = {}
    for model in args.models:
        model_root = OUTPUT_ROOT / model
        jobs = load_jobs(model_root)
        controlled, crossed, audits = load_representations(model, jobs)
        if args.require_complete and (len(controlled) != 120 or len(crossed) != 27):
            raise SystemExit(f"{model}: incomplete converted cohort controlled={len(controlled)} crossed={len(crossed)}")
        controlled_result = analyze_controlled(
            controlled, bootstrap_runs=args.bootstrap_runs, seed=args.seed
        )
        crossed_result = crossed_analysis(
            crossed, permutation_runs=args.permutation_runs, seed=args.seed
        )
        loaded[model] = (controlled_result, crossed_result, audits)

    # Multiplicity is applied across completed extension models. Deferred models
    # are retained in the protocol but do not contribute an unobserved p-value.
    model_order = list(args.models)
    primary_p = [loaded[m][0]["heldout_primary"].get("exact_one_sided_sign_flip_p", math.nan) for m in model_order]
    specificity_p = [
        loaded[m][0]["robustness"]["exact_fact_label_permutation"].get("exact_one_sided_p", math.nan)
        for m in model_order
    ]
    primary_q = holm_adjust(primary_p)
    specificity_q = holm_adjust(specificity_p)

    crossed_tests: list[tuple[str, str, str, float]] = []
    for model in model_order:
        crossed = loaded[model][1]
        for metric, summary in crossed.get("metrics", {}).items():
            crossed_tests.extend(
                [
                    (model, metric, "fact", summary["fact_effect_permutation_p"]),
                    (model, metric, "format", summary["format_effect_permutation_p"]),
                ]
            )
    crossed_q = holm_adjust([item[3] for item in crossed_tests])
    crossed_adjusted = {
        (model, metric, effect): q
        for (model, metric, effect, _), q in zip(crossed_tests, crossed_q)
    }

    for index, model in enumerate(model_order):
        controlled, crossed, audits = loaded[model]
        domains = {
            domain: summary
            for domain, summary in controlled.get("heldout_domains", {}).items()
            if summary.get("n", 0) >= 2
        }
        gate_r1 = bool(
            controlled["heldout_primary"].get("mean", math.nan) > 0
            and controlled["heldout_primary"].get("ci95", [math.nan])[0] > 0
            and primary_q[index] <= 0.05
        )
        gate_r2 = bool(len(domains) >= 2 and all(summary["mean"] > 0 for summary in domains.values()))
        gate_r3 = bool(specificity_q[index] <= 0.05)
        crossed_effects = []
        for metric, summary in crossed.get("metrics", {}).items():
            crossed_effects.extend(
                [
                    summary["fact_effect"] > 0 and crossed_adjusted[(model, metric, "fact")] <= 0.05,
                    summary["format_effect"] > 0 and crossed_adjusted[(model, metric, "format")] <= 0.05,
                ]
            )
            summary["fact_effect_holm_p"] = crossed_adjusted[(model, metric, "fact")]
            summary["format_effect_holm_p"] = crossed_adjusted[(model, metric, "format")]
        gate_r4 = bool(crossed_effects and all(crossed_effects))
        controlled["extension_holm_primary_p"] = primary_q[index]
        controlled["extension_holm_specificity_p"] = specificity_q[index]
        all_results["models"][model] = {
            "controlled": controlled,
            "crossed": crossed,
            "gates": {"R1_pooled": gate_r1, "R2_domains": gate_r2, "R3_specificity": gate_r3, "R4_crossed": gate_r4},
            "audit_counts": {
                "registered": 147,
                "ok": sum(row["status"] == "ok" for row in audits),
                "missing": sum(row["status"] == "missing" for row in audits),
                "error": sum(row["status"] == "error" for row in audits),
            },
        }
        analysis_dir = OUTPUT_ROOT / model / "analysis"
        write_json(analysis_dir / "model_extension_results.json", all_results["models"][model])
        write_json(analysis_dir / "graph_audit.json", audits)
        write_csv(analysis_dir / "graph_audit.csv", audits)
        write_csv(analysis_dir / "controlled_per_fact.csv", controlled["per_fact"])
        write_csv(analysis_dir / "crossed_pairwise.csv", crossed.get("pairwise_records", []))
        write_json(analysis_dir / "gate_summary.json", all_results["models"][model]["gates"])
    write_json(OUTPUT_ROOT / "model_extension_results.json", all_results)


if __name__ == "__main__":
    main()
