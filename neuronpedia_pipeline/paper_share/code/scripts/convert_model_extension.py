#!/usr/bin/env python3
"""Convert and audit registered model-extension graphs without touching legacy data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
OUTPUT_ROOT = BASE_DIR / "data" / "model_extension"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_converter():
    path = SCRIPT_DIR / "2_convert_graph.py"
    spec = importlib.util.spec_from_file_location("extension_converter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.convert_neuronpedia_graph


def raw_integrity(graph: dict[str, Any]) -> dict[str, Any]:
    nodes = list(graph.get("nodes", []))
    edges = list(graph.get("links", graph.get("edges", [])))
    ids = [str(node.get("node_id", node.get("id", ""))) for node in nodes]
    counts = Counter(ids)
    ambiguous = {node_id for node_id, count in counts.items() if node_id and count > 1}
    all_ids = set(ids) - {""}
    endpoints = [(str(edge.get("source")), str(edge.get("target"))) for edge in edges]
    return {
        "raw_node_count": len(nodes),
        "raw_edge_count": len(edges),
        "raw_missing_node_id_count": sum(not node_id for node_id in ids),
        "raw_ambiguous_node_id_count": len(ambiguous),
        "raw_ambiguous_node_ids": sorted(ambiguous),
        "raw_ambiguous_incident_edge_count": sum(
            source in ambiguous or target in ambiguous for source, target in endpoints
        ),
        "raw_orphan_edge_count": sum(source not in all_ids or target not in all_ids for source, target in endpoints),
        "raw_duplicate_endpoint_edge_count": len(endpoints) - len(set(endpoints)),
    }


def converted_integrity(graph: dict[str, Any]) -> dict[str, Any]:
    nodes = list(graph.get("nodes", []))
    edges = list(graph.get("edges", []))
    ids = [str(node.get("id", "")) for node in nodes]
    counts = Counter(ids)
    all_ids = set(ids) - {""}
    endpoints = [(str(edge.get("source")), str(edge.get("target"))) for edge in edges]
    return {
        "converted_node_count": len(nodes),
        "converted_edge_count": len(edges),
        "converted_missing_node_id_count": sum(not node_id for node_id in ids),
        "converted_duplicate_node_id_count": sum(count > 1 for node_id, count in counts.items() if node_id),
        "converted_orphan_edge_count": sum(
            source not in all_ids or target not in all_ids for source, target in endpoints
        ),
        "converted_duplicate_endpoint_edge_count": len(endpoints) - len(set(endpoints)),
    }


def write_outputs(model_root: Path, rows: list[dict[str, Any]]) -> None:
    analysis_dir = model_root / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    (analysis_dir / "conversion_audit.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8"
    )
    flat_rows = []
    for row in rows:
        flat_rows.append(
            {
                key: json.dumps(value, sort_keys=True) if isinstance(value, (list, dict)) else value
                for key, value in row.items()
            }
        )
    fields = sorted({key for row in flat_rows for key in row})
    with (analysis_dir / "conversion_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(flat_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", default=["qwen3-4b"])
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    convert = load_converter()
    any_failure = False
    for model in args.models:
        model_root = OUTPUT_ROOT / model
        jobs_path = model_root / "jobs.csv"
        if not jobs_path.exists():
            raise SystemExit(f"missing job manifest: {jobs_path}")
        with jobs_path.open("r", encoding="utf-8", newline="") as handle:
            jobs = list(csv.DictReader(handle))
        if len(jobs) != 147:
            raise SystemExit(f"{model}: expected 147 jobs, found {len(jobs)}")
        rows: list[dict[str, Any]] = []
        for index, job in enumerate(jobs, 1):
            raw_path = BASE_DIR / job["raw_graph_path"]
            converted_path = raw_path.with_name("converted_graph.json")
            base = {
                "model_id": model,
                "design": job["design"],
                "job_id": job["job_id"],
                "fact_id": job["fact_id"],
                "role": job["role"],
                "format": job["format"],
                "domain": job["domain"],
                "split": job["split"],
                "prompt": job["prompt"],
                "expected_token": job["expected_token"],
                "raw_path": str(raw_path.relative_to(BASE_DIR)),
                "converted_path": str(converted_path.relative_to(BASE_DIR)),
            }
            if not raw_path.exists():
                rows.append({**base, "status": "missing_raw"})
                continue
            try:
                raw = json.loads(raw_path.read_text(encoding="utf-8"))
                raw_audit = raw_integrity(raw)
                if raw_audit["raw_missing_node_id_count"] or raw_audit["raw_orphan_edge_count"]:
                    raise ValueError("raw graph has missing IDs or orphan edges")
                if args.overwrite or not converted_path.exists():
                    convert(
                        str(raw_path),
                        str(converted_path),
                        prompt=None,
                        model_id=model,
                        ambiguous_node_policy="drop",
                    )
                converted = json.loads(converted_path.read_text(encoding="utf-8"))
                converted_audit = converted_integrity(converted)
                if (
                    converted_audit["converted_missing_node_id_count"]
                    or converted_audit["converted_duplicate_node_id_count"]
                    or converted_audit["converted_orphan_edge_count"]
                ):
                    raise ValueError("converted graph failed identifier or endpoint checks")
                rows.append(
                    {
                        **base,
                        **raw_audit,
                        **converted_audit,
                        "raw_sha256": sha256_file(raw_path),
                        "converted_sha256": sha256_file(converted_path),
                        "ambiguous_policy": "drop",
                        "sensitivity_only": bool(raw_audit["raw_ambiguous_node_id_count"]),
                        "status": "ok",
                    }
                )
            except Exception as error:
                any_failure = True
                rows.append({**base, "status": "error", "error": repr(error)})
            print(f"[{model} {index:03d}/147] {job['design']} {job['job_id']} {rows[-1]['status']}", flush=True)
        write_outputs(model_root, rows)
        ok = sum(row["status"] == "ok" for row in rows)
        missing = sum(row["status"] == "missing_raw" for row in rows)
        print(f"{model}: converted={ok}/147 missing_raw={missing}")
        if args.require_complete and ok != 147:
            any_failure = True
    if any_failure:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
