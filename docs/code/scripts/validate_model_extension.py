#!/usr/bin/env python3
"""Fail-closed validation of the prospective Qwen3-4B extension artifact."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT = BASE_DIR / "data" / "model_extension"


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="qwen3-4b")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Validate a disclosed incomplete cohort while still failing on inconsistencies among present artifacts.",
    )
    args = parser.parse_args()
    root = ROOT / args.model
    failures: list[str] = []

    required = [
        root / "jobs.csv",
        root / "generation_status.json",
        root / "checksums.csv",
        root / "analysis" / "conversion_audit.json",
        root / "analysis" / "graph_audit.json",
        root / "analysis" / "model_extension_results.json",
        root / "analysis" / "controlled_per_fact.csv",
        root / "analysis" / "crossed_pairwise.csv",
        root / "analysis" / "gate_summary.json",
    ]
    for path in required:
        check(path.exists(), f"missing required file: {path.relative_to(BASE_DIR)}", failures)
    if failures:
        print("VALIDATION FAILED")
        print(*[f"- {item}" for item in failures], sep="\n")
        raise SystemExit(1)

    with (root / "jobs.csv").open("r", encoding="utf-8", newline="") as handle:
        jobs = list(csv.DictReader(handle))
    check(len(jobs) == 147, f"expected 147 jobs, found {len(jobs)}", failures)
    check(len({row["job_id"] for row in jobs}) == 147, "job IDs are not unique", failures)
    check(sum(row["design"] == "controlled" for row in jobs) == 120, "controlled job count is not 120", failures)
    check(sum(row["design"] == "crossed" for row in jobs) == 27, "crossed job count is not 27", failures)
    missing_job_ids: set[str] = set()
    present_job_ids: set[str] = set()
    for job in jobs:
        raw = BASE_DIR / job["raw_graph_path"]
        if not raw.exists():
            missing_job_ids.add(job["job_id"])
            if not args.allow_incomplete:
                failures.append(f"missing raw graph: {job['job_id']}")
            continue
        present_job_ids.add(job["job_id"])
        check(raw.with_name("metadata.json").exists(), f"missing metadata: {job['job_id']}", failures)
        check(raw.with_name("converted_graph.json").exists(), f"missing converted graph: {job['job_id']}", failures)

    with (root / "checksums.csv").open("r", encoding="utf-8", newline="") as handle:
        checksums = list(csv.DictReader(handle))
    expected_checksum_count = len(present_job_ids) if args.allow_incomplete else 147
    check(
        len(checksums) == expected_checksum_count,
        f"expected {expected_checksum_count} checksums, found {len(checksums)}",
        failures,
    )
    check(all(len(row["sha256"]) == 64 for row in checksums), "invalid SHA-256 entry", failures)
    check(
        {row["job_id"] for row in checksums} == present_job_ids,
        "checksum job IDs do not match present raw graphs",
        failures,
    )

    conversion = json.loads((root / "analysis" / "conversion_audit.json").read_text(encoding="utf-8"))
    audit = json.loads((root / "analysis" / "graph_audit.json").read_text(encoding="utf-8"))
    results = json.loads((root / "analysis" / "model_extension_results.json").read_text(encoding="utf-8"))
    check(len(conversion) == 147, "conversion audit does not contain 147 rows", failures)
    conversion_ok = [row for row in conversion if row.get("status") == "ok"]
    conversion_missing = {row["job_id"] for row in conversion if row.get("status") == "missing_raw"}
    if args.allow_incomplete:
        check(conversion_missing == missing_job_ids, "conversion-audit missing jobs do not match raw missingness", failures)
    else:
        check(not conversion_missing, "conversion audit contains missing rows", failures)
    check(
        len(conversion_ok) + len(conversion_missing) == len(conversion),
        "conversion audit contains unexpected non-ok rows",
        failures,
    )
    check(
        all(row.get("converted_duplicate_node_id_count") == 0 for row in conversion_ok),
        "converted duplicate IDs remain",
        failures,
    )
    check(
        all(row.get("converted_orphan_edge_count") == 0 for row in conversion_ok),
        "converted orphan edges remain",
        failures,
    )
    check(len(audit) == 147, "graph audit does not contain 147 rows", failures)
    audit_ok = [row for row in audit if row.get("status") == "ok"]
    audit_missing = {row["job_id"] for row in audit if row.get("status") == "missing"}
    if args.allow_incomplete:
        check(audit_missing == missing_job_ids, "graph-audit missing jobs do not match raw missingness", failures)
    else:
        check(not audit_missing, "graph audit contains missing rows", failures)
    check(len(audit_ok) + len(audit_missing) == len(audit), "graph audit contains unexpected non-ok rows", failures)
    expected_ok = len(present_job_ids) if args.allow_incomplete else 147
    check(results.get("audit_counts", {}).get("ok") == expected_ok, f"result audit ok count is not {expected_ok}", failures)
    check(results.get("audit_counts", {}).get("missing") == len(missing_job_ids), "result missing count is inconsistent", failures)
    check(results.get("crossed", {}).get("graph_n") == 27, "crossed graph count is not 27", failures)
    check(len(results.get("crossed", {}).get("pairwise_records", [])) == 108, "crossed pair count is not 108", failures)
    check(set(results.get("gates", {})) == {"R1_pooled", "R2_domains", "R3_specificity", "R4_crossed"}, "gate set is incomplete", failures)

    llama_root = ROOT / "llama-3.2-1b"
    llama_raw = list(llama_root.rglob("raw_graph.json")) if llama_root.exists() else []
    check(not llama_raw, "local Llama graphs exist despite the recorded hardware deferral", failures)

    figure_root = root / "figures"
    for stem in ["figure3_model_extension", "figure4_extension_quality"]:
        for suffix in ["png", "pdf", "svg"]:
            check((figure_root / f"{stem}.{suffix}").exists(), f"missing figure: {stem}.{suffix}", failures)

    report_status = "fail" if failures else ("pass_incomplete" if missing_job_ids else "pass")
    report = {
        "status": report_status,
        "failures": failures,
        "model": args.model,
        "present_jobs": len(present_job_ids),
        "missing_jobs": sorted(missing_job_ids),
    }
    (root / "analysis" / "validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if failures:
        print("VALIDATION FAILED")
        print(*[f"- {item}" for item in failures], sep="\n")
        raise SystemExit(1)
    if missing_job_ids:
        print(f"VALIDATION PASSED (INCOMPLETE COHORT: {len(present_job_ids)}/147)")
    else:
        print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
