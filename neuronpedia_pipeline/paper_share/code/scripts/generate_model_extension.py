#!/usr/bin/env python3
"""Resumable, manifest-backed graph generation for prospective model extensions.

Raw graphs are written only under ``data/model_extension``. Existing legacy
graphs are never reused or overwritten, because their generation settings are
not guaranteed to match the frozen extension protocol.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
CONFIG_PATH = BASE_DIR / "config" / "model_extension.json"
CONTROL_MANIFEST = BASE_DIR / "config" / "paper_control_manifest.csv"
FORMAT_SCRIPT = SCRIPT_DIR / "stage_2_format_variation_experiment.py"
OUTPUT_ROOT = BASE_DIR / "data" / "model_extension"
NEURONPEDIA_CONFIG = BASE_DIR.parent / "config" / "neuronpedia_config.yaml"

CROSSED_EXPECTED = {
    ("chemistry", "gold"): "Au",
    ("chemistry", "sodium"): "Na",
    ("chemistry", "iron"): "Fe",
    ("geography", "france"): "Paris",
    ("geography", "japan"): "Tokyo",
    ("geography", "germany"): "Berlin",
    ("history", "wwii"): "1945",
    ("history", "moon"): "1969",
    ("history", "titanic"): "1912",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_id(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip()).strip("-")
    if not value:
        raise ValueError("empty job identifier")
    return value


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temp.replace(path)


def load_varied_prompts() -> dict[str, Any]:
    tree = ast.parse(FORMAT_SCRIPT.read_text(encoding="utf-8"), filename=str(FORMAT_SCRIPT))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "VARIED_PROMPTS"
            for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            if not isinstance(value, dict):
                break
            return value
    raise RuntimeError(f"could not find a literal VARIED_PROMPTS mapping in {FORMAT_SCRIPT}")


def controlled_jobs() -> list[dict[str, str]]:
    with CONTROL_MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    jobs = []
    for row in rows:
        jobs.append(
            {
                "design": "controlled",
                "job_id": safe_id(f"{row['pair_id']}__{row['role']}"),
                "prompt": row["prompt"],
                "expected_token": row.get("expected_token", ""),
                "domain": row["domain"],
                "split": row["split"],
                "fact_id": row["pair_id"],
                "role": row["role"],
                "format": "",
            }
        )
    if len(jobs) != 120:
        raise ValueError(f"expected 120 controlled jobs, found {len(jobs)}")
    return jobs


def crossed_jobs() -> list[dict[str, str]]:
    jobs = []
    for domain, facts in load_varied_prompts().items():
        for fact_id, formats in facts.items():
            expected = CROSSED_EXPECTED[(domain, fact_id)]
            for format_name, prompt in formats.items():
                jobs.append(
                    {
                        "design": "crossed",
                        "job_id": safe_id(f"{domain}__{fact_id}__{format_name}"),
                        "prompt": prompt,
                        "expected_token": expected,
                        "domain": domain,
                        "split": "extension",
                        "fact_id": fact_id,
                        "role": "",
                        "format": format_name,
                    }
                )
    if len(jobs) != 27:
        raise ValueError(f"expected 27 crossed jobs, found {len(jobs)}")
    return jobs


def graph_path(model_id: str, job: dict[str, str]) -> Path:
    return OUTPUT_ROOT / safe_id(model_id) / job["design"] / job["job_id"] / "raw_graph.json"


def metadata_path(model_id: str, job: dict[str, str]) -> Path:
    return graph_path(model_id, job).with_name("metadata.json")


def write_job_manifest(model_id: str, jobs: list[dict[str, str]], model_spec: dict[str, Any]) -> Path:
    model_root = OUTPUT_ROOT / safe_id(model_id)
    model_root.mkdir(parents=True, exist_ok=True)
    path = model_root / "jobs.csv"
    fields = [
        "model_id", "backend", "source_set", "design", "job_id", "prompt",
        "expected_token", "domain", "split", "fact_id", "role", "format",
        "raw_graph_path",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for job in jobs:
            writer.writerow(
                {
                    "model_id": model_id,
                    "backend": model_spec["backend"],
                    "source_set": model_spec.get("source_set", model_spec.get("transcoder_set", "")),
                    **job,
                    "raw_graph_path": str(graph_path(model_id, job).relative_to(BASE_DIR)),
                }
            )
    return path


def write_checksums(model_id: str, jobs: list[dict[str, str]]) -> Path:
    path = OUTPUT_ROOT / safe_id(model_id) / "checksums.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["design", "job_id", "sha256", "bytes", "path"])
        writer.writeheader()
        for job in jobs:
            raw_path = graph_path(model_id, job)
            if raw_path.exists():
                writer.writerow(
                    {
                        "design": job["design"],
                        "job_id": job["job_id"],
                        "sha256": sha256_file(raw_path),
                        "bytes": raw_path.stat().st_size,
                        "path": str(raw_path.relative_to(BASE_DIR)),
                    }
                )
    return path


def generate_neuronpedia(
    *,
    base_url: str,
    api_key: str,
    model_spec: dict[str, Any],
    prompt: str,
    timeout: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = {
        "prompt": prompt,
        "modelId": model_spec["model_id"],
        "sourceSetName": model_spec["source_set"],
        "desiredLogitProb": model_spec.get("desired_logit_prob", 0.99),
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-Api-Key"] = api_key
    response = requests.post(f"{base_url.rstrip('/')}/graph/generate", json=payload, headers=headers, timeout=timeout)
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        raise RuntimeError(f"rate_limited retry_after={retry_after or 'unspecified'}")
    if response.status_code != 200:
        raise RuntimeError(f"generation HTTP {response.status_code}: {response.text[:300]}")
    info = response.json()
    s3_url = info.get("s3url") or info.get("s3Location") or info.get("graphUrl")
    if not s3_url:
        raise RuntimeError("generation response did not provide a raw graph URL")
    graph_response = requests.get(s3_url, timeout=timeout)
    if graph_response.status_code != 200:
        raise RuntimeError(f"raw graph HTTP {graph_response.status_code}")
    graph = graph_response.json()
    if not graph.get("nodes") or not (graph.get("links") or graph.get("edges")):
        raise RuntimeError("downloaded graph has no nodes or edges")
    return graph, info


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", default=["qwen3-4b"])
    parser.add_argument("--design", choices=["controlled", "crossed", "both"], default="both")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--delay", type=float, default=125.0,
                        help="Seconds between requests; 125 stays below 30 requests per 60 minutes")
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--retry-base-delay", type=float, default=30.0)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    extension = load_json(CONFIG_PATH)
    if sha256_file(CONTROL_MANIFEST).upper() != extension["controlled_manifest"]["sha256"]:
        raise SystemExit("controlled manifest hash differs from the frozen extension")
    if sha256_file(FORMAT_SCRIPT).upper() != extension["crossed_prompt_source"]["sha256"]:
        raise SystemExit("crossed prompt source hash differs from the frozen extension")
    specs = {item["extension_id"]: item for item in extension["models"]}

    all_jobs = controlled_jobs() + crossed_jobs()
    if args.design != "both":
        all_jobs = [job for job in all_jobs if job["design"] == args.design]
    if args.limit is not None:
        all_jobs = all_jobs[: max(args.limit, 0)]

    np_config = yaml.safe_load(NEURONPEDIA_CONFIG.read_text(encoding="utf-8"))
    base_url = np_config["api"]["base_url"]
    api_key = np_config["api"].get("api_key", "")

    any_error = False
    for extension_id in args.models:
        if extension_id not in specs:
            raise SystemExit(f"unknown registered extension model: {extension_id}")
        spec = specs[extension_id]
        model_id = spec["extension_id"]
        jobs = list(all_jobs)
        job_manifest_path = write_job_manifest(model_id, controlled_jobs() + crossed_jobs(), spec)
        status_path = OUTPUT_ROOT / safe_id(model_id) / "generation_status.json"
        status = load_json(status_path) if status_path.exists() else {
            "schema_version": 1,
            "model": model_id,
            "backend": spec["backend"],
            "protocol": str(extension["protocol"]),
            "jobs_manifest": str(job_manifest_path.relative_to(BASE_DIR)),
            "outcomes": {},
        }
        print(f"{model_id}: selected={len(jobs)} present={sum(graph_path(model_id, j).exists() for j in jobs)}")
        if spec["backend"] != "neuronpedia":
            print(f"{model_id}: backend {spec['backend']} is handled by generate_local_extension.py")
            continue
        if not args.execute:
            for job in jobs[:30]:
                state = "EXISTS" if graph_path(model_id, job).exists() else "MISSING"
                print(f"  {state} {job['design']} {job['job_id']}")
            continue

        request_number = 0
        for index, job in enumerate(jobs, 1):
            raw_path = graph_path(model_id, job)
            if raw_path.exists() and not args.overwrite:
                print(f"[{index}/{len(jobs)}] SKIP {job['design']} {job['job_id']}", flush=True)
                continue
            if request_number:
                time.sleep(max(args.delay, 0.0))
            print(f"[{index}/{len(jobs)}] GENERATE {model_id} {job['design']} {job['job_id']}", flush=True)
            error = None
            for attempt in range(1, args.retries + 1):
                request_number += 1
                try:
                    graph, info = generate_neuronpedia(
                        base_url=base_url,
                        api_key=api_key,
                        model_spec=spec,
                        prompt=job["prompt"],
                        timeout=args.timeout,
                    )
                    raw_path.parent.mkdir(parents=True, exist_ok=True)
                    raw_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
                    metadata = {
                        **job,
                        "model_id": model_id,
                        "backend": spec["backend"],
                        "source_set": spec["source_set"],
                        "desired_logit_prob": spec.get("desired_logit_prob", 0.99),
                        "generated_at": utc_now(),
                        "raw_sha256": sha256_file(raw_path),
                        "raw_bytes": raw_path.stat().st_size,
                        "num_nodes": len(graph.get("nodes", [])),
                        "num_edges": len(graph.get("links", graph.get("edges", []))),
                        "neuronpedia_url": info.get("url"),
                        "s3_url": info.get("s3url") or info.get("s3Location") or info.get("graphUrl"),
                        "response_model_id": info.get("modelId"),
                        "slug": info.get("slug") or (info.get("url", "").split("slug=")[-1] if "slug=" in info.get("url", "") else None),
                    }
                    write_json(metadata_path(model_id, job), metadata)
                    status["outcomes"][job["job_id"]] = {"status": "ok", "attempt": attempt, **metadata}
                    error = None
                    print(f"  OK nodes={metadata['num_nodes']} edges={metadata['num_edges']}", flush=True)
                    break
                except Exception as exc:
                    error = str(exc)
                    print(f"  attempt {attempt}/{args.retries}: {error}", flush=True)
                    if attempt < args.retries:
                        cooldown = args.retry_base_delay * (2 ** (attempt - 1))
                        time.sleep(max(cooldown, 1.0))
            if error is not None:
                any_error = True
                status["outcomes"][job["job_id"]] = {
                    "status": "error", "error": error, "updated_at": utc_now(), **job
                }
            status["updated_at"] = utc_now()
            write_json(status_path, status)
            write_checksums(model_id, controlled_jobs() + crossed_jobs())

        complete_jobs = controlled_jobs() + crossed_jobs()
        print(
            f"{model_id}: complete={sum(graph_path(model_id, j).exists() for j in complete_jobs)}/147; "
            f"status={status_path}",
            flush=True,
        )

    if any_error:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
