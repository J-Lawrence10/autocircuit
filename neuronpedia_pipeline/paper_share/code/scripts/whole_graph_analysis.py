#!/usr/bin/env python3
"""Collision-safe, error-aware whole-graph publication analysis.

This script implements docs/papers/WHOLE_GRAPH_ANALYSIS_PROTOCOL.md. It does
not consume traceback outputs or traceback-derived labels.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import os
import platform
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from control_manifest import REQUIRED_ROLES, load_control_manifest  # noqa: E402
from path_manager import PathManager  # noqa: E402

SCHEMA_VERSION = "whole-graph-publication-v1"
PROTOCOL_PATH = BASE_DIR / "docs" / "papers" / "WHOLE_GRAPH_ANALYSIS_PROTOCOL.md"
DEFAULT_MANIFEST = BASE_DIR / "config" / "paper_control_manifest.csv"
DEFAULT_OUTDIR = BASE_DIR / "data" / "publication_analysis"
FORMAT_DIR = BASE_DIR / "data" / "stage_2_format_variation"
FORMAT_RESULTS = FORMAT_DIR / "generation_results.json"


def normalize_prompt(prompt: str) -> str:
    return (
        prompt.replace("<bos>", "")
        .replace("<|im_end|>", "")
        .replace("<|endoftext|>", "")
        .strip()
        .casefold()
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_json_with_hash(path: Path) -> tuple[dict[str, Any], str]:
    payload = path.read_bytes()
    return json.loads(payload), sha256_bytes(payload)


def maybe_release_cloud_file(path: Path) -> None:
    """Keep OneDrive inputs unpinned after streaming them on Windows."""
    if os.name != "nt":
        return
    try:
        subprocess.run(
            ["attrib", "+U", "-P", str(path)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


def finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def feature_family(node_type: Any) -> str:
    value = str(node_type or "feature").strip().casefold()
    if value == "lorsa":
        return "lorsa"
    if "transcoder" in value:
        return "transcoder"
    return value or "feature"


def is_error_node(node: Mapping[str, Any]) -> bool:
    node_type = str(node.get("node_type", node.get("feature_type", ""))).casefold()
    return "error" in node_type or node.get("feature_id", node.get("feature")) == -1


def is_feature_node(node: Mapping[str, Any]) -> bool:
    node_type = str(node.get("node_type", node.get("feature_type", ""))).casefold()
    feature_id = node.get("feature_id", node.get("feature"))
    layer = node.get("layer")
    try:
        layer_value = int(layer)
        feature_value = int(feature_id)
    except (TypeError, ValueError):
        return False
    return (
        layer_value >= 0
        and feature_value >= 0
        and not is_error_node(node)
        and node_type not in {"embedding", "logit"}
    )


def node_identity(node: Mapping[str, Any]) -> tuple[str, int, int]:
    return (
        feature_family(node.get("node_type", node.get("feature_type"))),
        int(node["layer"]),
        int(node.get("feature_id", node.get("feature"))),
    )


def sparse_cosine(a: Mapping[Any, float], b: Mapping[Any, float]) -> float:
    if not a or not b:
        return 0.0
    shared = set(a).intersection(b)
    numerator = sum(float(a[key]) * float(b[key]) for key in shared)
    norm_a = math.sqrt(sum(float(value) ** 2 for value in a.values()))
    norm_b = math.sqrt(sum(float(value) ** 2 for value in b.values()))
    return numerator / (norm_a * norm_b) if norm_a and norm_b else 0.0


def jaccard(a: set[Any], b: set[Any]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def classify_token(token: Any) -> str:
    if token is None:
        return "missing"
    token = str(token)
    if not token:
        return "empty"
    if token.isspace():
        return "whitespace"
    stripped = token.strip()
    if not stripped:
        return "whitespace"
    if any(char.isalnum() for char in stripped):
        return "alphanumeric"
    return "punctuation_or_symbol"


def normalize_profile(values: Mapping[Any, float]) -> dict[Any, float]:
    total = sum(abs(float(value)) for value in values.values())
    return {key: abs(float(value)) / total for key, value in values.items()} if total else {}


def _node_id(node: Mapping[str, Any]) -> str:
    return str(node.get("id", node.get("node_id", "")))


def summarize_graph(
    graph: Mapping[str, Any],
    *,
    path: Path,
    file_sha256: str,
    raw_schema: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    nodes = list(graph.get("nodes", []))
    edges = list(graph.get("edges", graph.get("links", [])))
    ids = [_node_id(node) for node in nodes]
    id_counts = Counter(ids)
    ambiguous_ids = {node_id for node_id, count in id_counts.items() if node_id and count > 1}
    missing_ids = sum(not node_id for node_id in ids)
    valid_ids = set(ids) - ambiguous_ids - {""}
    all_ids = set(ids) - {""}
    orphan_edges = sum(
        str(edge.get("source")) not in all_ids or str(edge.get("target")) not in all_ids
        for edge in edges
    )
    ambiguous_incident_edges = sum(
        str(edge.get("source")) in ambiguous_ids or str(edge.get("target")) in ambiguous_ids
        for edge in edges
    )
    duplicate_exact_edges = len(edges) - len(
        {
            (str(edge.get("source")), str(edge.get("target")), finite_number(edge.get("weight")))
            for edge in edges
        }
    )
    duplicate_endpoint_edges = len(edges) - len(
        {(str(edge.get("source")), str(edge.get("target"))) for edge in edges}
    )

    eligible_nodes = [node for node in nodes if _node_id(node) in valid_ids and is_feature_node(node)]
    eligible_ids = {_node_id(node) for node in eligible_nodes}
    error_nodes = [node for node in nodes if _node_id(node) in valid_ids and is_error_node(node)]
    error_ids = {_node_id(node) for node in error_nodes}
    nonterminal_nodes = [
        node
        for node in nodes
        if str(node.get("node_type", node.get("feature_type", ""))).casefold()
        not in {"embedding", "logit"}
        and _node_id(node) in valid_ids
    ]

    feature_set: set[tuple[str, int, int]] = set()
    feature_weights: dict[tuple[str, int, int], float] = defaultdict(float)
    layer_profile: dict[int, float] = defaultdict(float)
    for node in eligible_nodes:
        identity = node_identity(node)
        feature_set.add(identity)
        influence = finite_number(node.get("influence")) or 0.0
        feature_weights[identity] += abs(influence)
        layer_profile[int(node["layer"])] += abs(influence)

    features_with_errors: set[Any] = set(feature_set)
    feature_weights_with_errors: dict[Any, float] = dict(feature_weights)
    for node in error_nodes:
        error_type = str(node.get("node_type", node.get("feature_type", "error"))).casefold()
        try:
            error_layer = int(node.get("layer", -1))
        except (TypeError, ValueError):
            error_layer = -1
        identity = (f"error:{error_type}", error_layer, -1)
        features_with_errors.add(identity)
        feature_weights_with_errors[identity] = feature_weights_with_errors.get(identity, 0.0) + abs(
            finite_number(node.get("influence")) or 0.0
        )

    edge_flow: dict[tuple[int, int], float] = defaultdict(float)
    eligible_node_by_id = {_node_id(node): node for node in eligible_nodes}
    eligible_edge_count = 0
    eligible_edge_weight = 0.0
    error_incident_weight = 0.0
    nonterminal_edge_weight = 0.0
    node_types = {
        _node_id(node): str(node.get("node_type", node.get("feature_type", ""))).casefold()
        for node in nodes
        if _node_id(node) in valid_ids
    }
    for edge in edges:
        source = str(edge.get("source"))
        target = str(edge.get("target"))
        weight = finite_number(edge.get("weight"))
        if weight is None or source not in valid_ids or target not in valid_ids:
            continue
        abs_weight = abs(weight)
        if source in eligible_ids and target in eligible_ids:
            source_layer = int(eligible_node_by_id[source]["layer"])
            target_layer = int(eligible_node_by_id[target]["layer"])
            edge_flow[(source_layer, target_layer)] += abs_weight
            eligible_edge_count += 1
            eligible_edge_weight += abs_weight
        if node_types.get(source) not in {"embedding", "logit"} and node_types.get(target) not in {
            "embedding",
            "logit",
        }:
            nonterminal_edge_weight += abs_weight
            if source in error_ids or target in error_ids:
                error_incident_weight += abs_weight

    total_influence = sum(abs(finite_number(node.get("influence")) or 0.0) for node in nonterminal_nodes)
    error_influence = sum(abs(finite_number(node.get("influence")) or 0.0) for node in error_nodes)
    top_predictions = graph.get("metadata", {}).get("top_predictions", [])
    top_token = graph.get("metadata", {}).get("model_output")
    if top_token is None and top_predictions:
        top_token = top_predictions[0].get("token")

    metadata = graph.get("metadata", {})
    audit = {
        "path": str(path),
        "sha256": file_sha256,
        "raw_schema": raw_schema,
        "prompt": metadata.get("prompt"),
        "model": metadata.get("model", metadata.get("scan")),
        "node_threshold": metadata.get("node_threshold"),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "missing_node_ids": missing_ids,
        "ambiguous_node_id_count": len(ambiguous_ids),
        "ambiguous_node_ids": sorted(ambiguous_ids),
        "metadata_ambiguous_ids_dropped": metadata.get("ambiguous_node_ids_dropped", []),
        "dangling_edge_count": orphan_edges,
        "ambiguous_incident_edge_count": ambiguous_incident_edges,
        "duplicate_exact_edge_count": duplicate_exact_edges,
        "duplicate_endpoint_edge_count": duplicate_endpoint_edges,
        "nonfinite_edge_count": sum(finite_number(edge.get("weight")) is None for edge in edges),
        "eligible_feature_node_count": len(eligible_nodes),
        "unique_feature_identity_count": len(feature_set),
        "error_node_count": len(error_nodes),
        "feature_families": dict(Counter(identity[0] for identity in feature_set)),
        "top_token": top_token,
        "top_token_class": classify_token(top_token),
        "error_influence_fraction": error_influence / total_influence if total_influence else None,
        "error_incident_edge_weight_fraction": (
            error_incident_weight / nonterminal_edge_weight if nonterminal_edge_weight else None
        ),
        "eligible_edge_count": eligible_edge_count,
        "eligible_edge_weight": eligible_edge_weight,
        "sensitivity_only": bool(metadata.get("sensitivity_only", False)),
    }
    representation = {
        "features": feature_set,
        "feature_weights": dict(feature_weights),
        "features_with_errors": features_with_errors,
        "feature_weights_with_errors": feature_weights_with_errors,
        "layer_profile": normalize_profile(layer_profile),
        "edge_flow": normalize_profile(edge_flow),
        "eligible_feature_node_count": len(eligible_nodes),
        "eligible_edge_count": eligible_edge_count,
        "error_influence_fraction": audit["error_influence_fraction"],
        "error_incident_edge_weight_fraction": audit["error_incident_edge_weight_fraction"],
        "top_token": top_token,
        "top_token_class": audit["top_token_class"],
        "sensitivity_only": bool(metadata.get("sensitivity_only", False)),
        "ambiguous_node_ids_dropped": list(metadata.get("ambiguous_node_ids_dropped", [])),
    }
    return audit, representation


def exact_sign_flip_p(values: Iterable[float], alternative: str = "greater") -> float:
    values = np.asarray(list(values), dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return math.nan
    if len(values) > 20:
        raise ValueError(
            "Exact sign-flip enumeration is limited to 20 units; use a declared "
            "Monte Carlo test or mark the pooled result descriptive."
        )
    observed = float(values.mean())
    extreme = 0
    total = 1 << len(values)
    for mask in range(total):
        signed_mean = sum(
            value if mask & (1 << index) else -value for index, value in enumerate(values)
        ) / len(values)
        if alternative == "greater":
            extreme += signed_mean >= observed - 1e-15
        elif alternative == "two-sided":
            extreme += abs(signed_mean) >= abs(observed) - 1e-15
        else:
            raise ValueError(f"Unsupported alternative: {alternative}")
    return extreme / total


def bootstrap_ci(
    values: Iterable[float], *, runs: int, seed: int, confidence: float = 0.95
) -> list[float]:
    values = np.asarray(list(values), dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return [math.nan, math.nan]
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(runs, len(values)))
    estimates = values[indices].mean(axis=1)
    alpha = (1.0 - confidence) / 2.0
    return [float(np.quantile(estimates, alpha)), float(np.quantile(estimates, 1.0 - alpha))]


def summarize_values(
    values: Iterable[float], *, bootstrap_runs: int, seed: int, run_exact_test: bool = True
) -> dict[str, Any]:
    values = [float(value) for value in values if math.isfinite(float(value))]
    return {
        "n": len(values),
        "mean": float(np.mean(values)) if values else math.nan,
        "median": float(np.median(values)) if values else math.nan,
        "positive_n": sum(value > 0 for value in values),
        "zero_n": sum(value == 0 for value in values),
        "ci95": bootstrap_ci(values, runs=bootstrap_runs, seed=seed),
        "exact_one_sided_sign_flip_p": (
            exact_sign_flip_p(values, "greater") if run_exact_test else math.nan
        ),
        "values": values,
    }


def holm_adjust(p_values: list[float]) -> list[float]:
    adjusted = [math.nan] * len(p_values)
    finite = [(index, float(value)) for index, value in enumerate(p_values) if math.isfinite(value)]
    finite.sort(key=lambda item: item[1])
    running = 0.0
    count = len(finite)
    for rank, (index, value) in enumerate(finite):
        running = max(running, min(1.0, (count - rank) * value))
        adjusted[index] = running
    return adjusted


def converted_path_for(prompt: str, model_dir: str, variant: str) -> tuple[Path, Path]:
    manager = PathManager()
    raw_path = manager.raw_graph_path(prompt, model_id=model_dir)
    converted = raw_path.parent.parent / "2_conversion" / raw_path.name.replace(
        "_raw_graph.json", f"_converted_graph_v3{variant}.json"
    )
    return raw_path, converted


def load_controlled_cohort(
    *,
    manifest_rows: list[dict[str, str]],
    model_dir: str,
    variant: str,
    audit_raw: bool,
) -> tuple[dict[tuple[str, str], dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    representations: dict[tuple[str, str], dict[str, Any]] = {}
    audits: list[dict[str, Any]] = []
    raw_audits: list[dict[str, Any]] = []
    for index, row in enumerate(manifest_rows, 1):
        raw_path, converted_path = converted_path_for(row["prompt"], model_dir, variant)
        record_base = {
            "model_dir": model_dir,
            "pair_id": row["pair_id"],
            "role": row["role"],
            "domain": row["domain"],
            "split": row["split"],
            "manifest_prompt": row["prompt"],
            "expected_token": row["expected_token"],
        }
        if not converted_path.exists():
            audits.append({**record_base, "path": str(converted_path), "status": "missing"})
            continue
        try:
            graph, digest = read_json_with_hash(converted_path)
            audit, representation = summarize_graph(
                graph, path=converted_path, file_sha256=digest, raw_schema=False
            )
            normalized_graph_prompt = normalize_prompt(str(audit.get("prompt") or ""))
            status = "ok" if normalized_graph_prompt == normalize_prompt(row["prompt"]) else "prompt_mismatch"
            audit.update(record_base)
            audit["status"] = status
            expected = row["expected_token"].strip()
            top_token_matches_expected = (
                bool(expected) and str(audit.get("top_token") or "").strip() == expected
            ) if row["role"] in {"target", "positive_paraphrase"} else None
            audit["top_token_matches_expected"] = top_token_matches_expected
            audits.append(audit)
            if status == "ok" and audit["ambiguous_node_id_count"] == 0 and audit["dangling_edge_count"] == 0:
                representation.update(record_base)
                representation["converted_path"] = str(converted_path)
                representation["top_token_matches_expected"] = top_token_matches_expected
                representations[(row["pair_id"], row["role"])] = representation
        except Exception as error:  # preserve the failure in the machine-readable audit
            audits.append({**record_base, "path": str(converted_path), "status": "error", "error": repr(error)})
        finally:
            maybe_release_cloud_file(converted_path)

        if audit_raw and raw_path.exists():
            try:
                raw_graph, raw_digest = read_json_with_hash(raw_path)
                raw_audit, _ = summarize_graph(
                    raw_graph, path=raw_path, file_sha256=raw_digest, raw_schema=True
                )
                raw_audit.update(record_base)
                raw_audit["status"] = "ok"
                raw_audits.append(raw_audit)
            except Exception as error:
                raw_audits.append(
                    {**record_base, "path": str(raw_path), "status": "error", "error": repr(error)}
                )
            finally:
                maybe_release_cloud_file(raw_path)
        elif audit_raw:
            raw_audits.append({**record_base, "path": str(raw_path), "status": "missing"})
        print(
            f"[{model_dir} {index:03d}/{len(manifest_rows):03d}] {row['pair_id']} {row['role']}",
            flush=True,
        )
    return representations, audits, raw_audits


SIMILARITIES = {
    "feature_jaccard": lambda a, b: jaccard(a["features"], b["features"]),
    "feature_influence_cosine": lambda a, b: sparse_cosine(a["feature_weights"], b["feature_weights"]),
    "layer_profile_cosine": lambda a, b: sparse_cosine(a["layer_profile"], b["layer_profile"]),
    "edge_flow_cosine": lambda a, b: sparse_cosine(a["edge_flow"], b["edge_flow"]),
}


def complete_pair_ids(representations: Mapping[tuple[str, str], Any]) -> tuple[list[str], list[dict[str, Any]]]:
    pair_roles: dict[str, set[str]] = defaultdict(set)
    for pair_id, role in representations:
        pair_roles[pair_id].add(role)
    eligible: list[str] = []
    excluded: list[dict[str, Any]] = []
    for pair_id in sorted(pair_roles):
        roles = pair_roles[pair_id]
        if roles != REQUIRED_ROLES:
            excluded.append(
                {
                    "pair_id": pair_id,
                    "reason": "incomplete_roles",
                    "present_roles": sorted(roles),
                    "missing_roles": sorted(REQUIRED_ROLES - roles),
                }
            )
            continue
        incorrect_roles = [
            role
            for role in ["target", "positive_paraphrase"]
            if not representations[(pair_id, role)].get("top_token_matches_expected", False)
        ]
        if incorrect_roles:
            excluded.append(
                {
                    "pair_id": pair_id,
                    "reason": "expected_token_not_top_prediction",
                    "incorrect_roles": incorrect_roles,
                    "observed_top_tokens": {
                        role: representations[(pair_id, role)].get("top_token")
                        for role in incorrect_roles
                    },
                }
            )
            continue
        eligible.append(pair_id)
    return eligible, excluded


def analyze_controlled(
    representations: Mapping[tuple[str, str], dict[str, Any]],
    *,
    bootstrap_runs: int,
    seed: int,
) -> dict[str, Any]:
    complete, excluded = complete_pair_ids(representations)
    robustness_similarities = {
        "feature_jaccard_with_errors": lambda a, b: jaccard(
            a["features_with_errors"], b["features_with_errors"]
        ),
        "feature_influence_cosine_with_errors": lambda a, b: sparse_cosine(
            a["feature_weights_with_errors"], b["feature_weights_with_errors"]
        ),
    }

    def build_rows(pair_ids: list[str], include_robustness: bool = True) -> tuple[list[dict[str, Any]], list[str]]:
        rows: list[dict[str, Any]] = []
        without_comparators: list[str] = []
        metrics = dict(SIMILARITIES)
        if include_robustness:
            metrics.update(robustness_similarities)
        for pair_id in pair_ids:
            target = representations[(pair_id, "target")]
            positive = representations[(pair_id, "positive_paraphrase")]
            same_template = representations[(pair_id, "negative_same_template")]
            nonce = representations[(pair_id, "negative_nonce")]
            other_positive = [
                representations[(other_id, "positive_paraphrase")]
                for other_id in pair_ids
                if other_id != pair_id
                and representations[(other_id, "positive_paraphrase")]["domain"] == target["domain"]
                and representations[(other_id, "positive_paraphrase")]["split"] == target["split"]
            ]
            if not other_positive:
                without_comparators.append(pair_id)
                continue
            record: dict[str, Any] = {
                "pair_id": pair_id,
                "domain": target["domain"],
                "split": target["split"],
                "other_factual_comparator_n": len(other_positive),
                "target_top_token": target["top_token"],
                "target_top_token_class": target["top_token_class"],
                "positive_top_token": positive["top_token"],
                "positive_top_token_class": positive["top_token_class"],
                "same_template_top_token": same_template["top_token"],
                "same_template_top_token_class": same_template["top_token_class"],
                "nonce_top_token": nonce["top_token"],
                "nonce_top_token_class": nonce["top_token_class"],
                "target_error_influence_fraction": target["error_influence_fraction"],
                "positive_error_influence_fraction": positive["error_influence_fraction"],
                "target_feature_count": len(target["features"]),
                "positive_feature_count": len(positive["features"]),
                "other_factual_feature_count_mean": float(
                    np.mean([len(other["features"]) for other in other_positive])
                ),
                "target_export_clean": not target.get("sensitivity_only", False),
                "positive_export_clean": not positive.get("sensitivity_only", False),
                "same_template_output_type_matches_target": (
                    same_template["top_token_class"] == target["top_token_class"]
                ),
                "nonce_output_type_matches_target": nonce["top_token_class"] == target["top_token_class"],
            }
            for metric, similarity in metrics.items():
                target_positive = similarity(target, positive)
                target_same_template = similarity(target, same_template)
                target_nonce = similarity(target, nonce)
                factual_values = [similarity(target, other) for other in other_positive]
                record.update(
                    {
                        f"{metric}__target_positive": target_positive,
                        f"{metric}__target_same_template_nonce": target_same_template,
                        f"{metric}__target_paraphrased_nonce": target_nonce,
                        f"{metric}__other_factual_mean": float(np.mean(factual_values)),
                        f"{metric}__other_factual_max": float(np.max(factual_values)),
                        f"{metric}__margin_other_factual_mean": target_positive
                        - float(np.mean(factual_values)),
                        f"{metric}__margin_other_factual_max": target_positive
                        - float(np.max(factual_values)),
                        f"{metric}__margin_same_template_nonce": target_positive - target_same_template,
                        f"{metric}__margin_paraphrased_nonce": target_positive - target_nonce,
                    }
                )
            rows.append(record)
        return rows, without_comparators

    per_fact, without_comparators = build_rows(complete)

    aggregates: dict[str, Any] = {}
    secondary_keys: list[tuple[str, str]] = []
    secondary_p: list[float] = []
    for split in ["development", "held_out", "all"]:
        rows = per_fact if split == "all" else [row for row in per_fact if row["split"] == split]
        split_results: dict[str, Any] = {}
        for metric in SIMILARITIES:
            metric_results: dict[str, Any] = {}
            for contrast in [
                "margin_other_factual_mean",
                "margin_other_factual_max",
                "margin_same_template_nonce",
                "margin_paraphrased_nonce",
            ]:
                key = f"{metric}__{contrast}"
                summary = summarize_values(
                    [row[key] for row in rows],
                    bootstrap_runs=bootstrap_runs,
                    seed=seed + sum(map(ord, f"{split}:{key}")),
                    run_exact_test=split != "all",
                )
                metric_results[contrast] = summary
                if split == "held_out" and not (
                    metric == "feature_jaccard" and contrast == "margin_other_factual_mean"
                ):
                    secondary_keys.append((metric, contrast))
                    secondary_p.append(summary["exact_one_sided_sign_flip_p"])
            split_results[metric] = metric_results
        aggregates[split] = split_results

    adjusted = holm_adjust(secondary_p)
    for (metric, contrast), q_value in zip(secondary_keys, adjusted):
        aggregates["held_out"][metric][contrast]["holm_adjusted_p"] = q_value

    primary = aggregates.get("held_out", {}).get("feature_jaccard", {}).get(
        "margin_other_factual_mean", {}
    )
    heldout_domains = {
        domain: summarize_values(
            [
                row["feature_jaccard__margin_other_factual_mean"]
                for row in per_fact
                if row["split"] == "held_out" and row["domain"] == domain
            ],
            bootstrap_runs=bootstrap_runs,
            seed=seed + sum(map(ord, domain)),
        )
        for domain in sorted({row["domain"] for row in per_fact if row["split"] == "held_out"})
    }
    required_domains = {"chemistry", "geography", "history"}
    pooled_primary_pass = bool(
        primary
        and primary["exact_one_sided_sign_flip_p"] <= 0.05
        and primary["ci95"][0] > 0
    )
    primary_pass = bool(
        pooled_primary_pass
        and set(heldout_domains) == required_domains
        and all(summary["mean"] > 0 for summary in heldout_domains.values())
    )

    heldout_rows = [row for row in per_fact if row["split"] == "held_out"]
    primary_key = "feature_jaccard__margin_other_factual_mean"
    leave_one_out = {
        row["pair_id"]: float(
            np.mean([other[primary_key] for other in heldout_rows if other["pair_id"] != row["pair_id"]])
        )
        for row in heldout_rows
        if len(heldout_rows) > 1
    }

    clean_pairs = [
        pair_id
        for pair_id in complete
        if not representations[(pair_id, "target")].get("sensitivity_only", False)
        and not representations[(pair_id, "positive_paraphrase")].get("sensitivity_only", False)
    ]
    clean_rows, clean_without_comparators = build_rows(clean_pairs, include_robustness=False)
    clean_heldout = [row[primary_key] for row in clean_rows if row["split"] == "held_out"]
    clean_summary = summarize_values(
        clean_heldout,
        bootstrap_runs=bootstrap_runs,
        seed=seed + 991,
        run_exact_test=0 < len(clean_heldout) <= 20,
    )

    error_inclusive = {
        metric: summarize_values(
            [row[f"{metric}__margin_other_factual_mean"] for row in heldout_rows],
            bootstrap_runs=bootstrap_runs,
            seed=seed + sum(map(ord, metric)),
        )
        for metric in robustness_similarities
    }

    output_type_matched = {}
    for control, flag in [
        ("same_template_nonce", "same_template_output_type_matches_target"),
        ("paraphrased_nonce", "nonce_output_type_matches_target"),
    ]:
        values = [
            row[f"feature_jaccard__margin_{control}"]
            for row in heldout_rows
            if row[flag]
        ]
        output_type_matched[control] = summarize_values(
            values,
            bootstrap_runs=bootstrap_runs,
            seed=seed + sum(map(ord, control)),
            run_exact_test=0 < len(values) <= 20,
        )

    # Exact within-domain fact-label permutation for the held-out matched pairing.
    domain_pair_ids: list[list[str]] = []
    for domain in sorted({row["domain"] for row in heldout_rows}):
        ids = sorted(row["pair_id"] for row in heldout_rows if row["domain"] == domain)
        if ids:
            domain_pair_ids.append(ids)
    observed_match = float(
        np.mean(
            [
                jaccard(
                    representations[(pair_id, "target")]["features"],
                    representations[(pair_id, "positive_paraphrase")]["features"],
                )
                for ids in domain_pair_ids
                for pair_id in ids
            ]
        )
    ) if domain_pair_ids else math.nan
    permuted_matches: list[float] = []
    permutation_groups = [list(itertools.permutations(ids)) for ids in domain_pair_ids]
    for permutation_choice in itertools.product(*permutation_groups):
        similarities = []
        for ids, permuted_ids in zip(domain_pair_ids, permutation_choice):
            similarities.extend(
                jaccard(
                    representations[(target_id, "target")]["features"],
                    representations[(positive_id, "positive_paraphrase")]["features"],
                )
                for target_id, positive_id in zip(ids, permuted_ids)
            )
        permuted_matches.append(float(np.mean(similarities)))
    label_permutation = {
        "observed_matched_similarity": observed_match,
        "exact_permutation_count": len(permuted_matches),
        "exact_one_sided_p": (
            sum(value >= observed_match - 1e-15 for value in permuted_matches) / len(permuted_matches)
            if permuted_matches
            else math.nan
        ),
        "null_mean": float(np.mean(permuted_matches)) if permuted_matches else math.nan,
    }

    # OLS with HC1 heteroskedasticity-robust covariance. Each row is one fact,
    # so the inference unit remains the fact. Covariates are centered log sizes.
    size_regression: dict[str, Any]
    if len(heldout_rows) >= 5:
        y = np.asarray([row[primary_key] for row in heldout_rows], dtype=float)
        target_size = np.log1p([row["target_feature_count"] for row in heldout_rows])
        positive_size = np.log1p([row["positive_feature_count"] for row in heldout_rows])
        x = np.column_stack(
            [np.ones(len(y)), target_size - target_size.mean(), positive_size - positive_size.mean()]
        )
        bread = np.linalg.pinv(x.T @ x)
        beta = bread @ x.T @ y
        residuals = y - x @ beta
        meat = sum(
            residuals[index] ** 2 * np.outer(x[index], x[index]) for index in range(len(y))
        )
        scale = len(y) / max(1, len(y) - x.shape[1])
        covariance = scale * bread @ meat @ bread
        standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0.0))
        size_regression = {
            "n_facts": len(y),
            "coefficients": {
                "adjusted_mean_at_centered_sizes": float(beta[0]),
                "log_target_feature_count": float(beta[1]),
                "log_positive_feature_count": float(beta[2]),
            },
            "hc1_standard_errors": {
                "adjusted_mean_at_centered_sizes": float(standard_errors[0]),
                "log_target_feature_count": float(standard_errors[1]),
                "log_positive_feature_count": float(standard_errors[2]),
            },
        }
    else:
        size_regression = {"n_facts": len(heldout_rows), "status": "insufficient_n"}

    weighted_primary = aggregates["held_out"]["feature_influence_cosine"][
        "margin_other_factual_mean"
    ]
    gate_c = bool(
        clean_summary["n"] > 0
        and clean_summary["mean"] > 0
        and leave_one_out
        and min(leave_one_out.values()) > 0
        and weighted_primary["mean"] > 0
    )
    return {
        "complete_pair_ids": complete,
        "complete_pair_n": len(complete),
        "analyzable_pair_ids": [row["pair_id"] for row in per_fact],
        "analyzable_pair_n": len(per_fact),
        "pairs_without_same_domain_split_comparator": without_comparators,
        "excluded_pairs": excluded,
        "per_fact": per_fact,
        "aggregates": aggregates,
        "heldout_primary": primary,
        "heldout_domains": heldout_domains,
        "pooled_confirmatory_test_pass": pooled_primary_pass,
        "gate_b_confirmatory_fact_identity_pass": primary_pass,
        "gate_b_required_domains": sorted(required_domains),
        "robustness": {
            "clean_export_pair_ids": clean_pairs,
            "clean_export_pairs_without_comparator": clean_without_comparators,
            "clean_export_heldout_primary": clean_summary,
            "error_inclusive_heldout": error_inclusive,
            "leave_one_fact_out_primary_means": leave_one_out,
            "output_type_matched_controls": output_type_matched,
            "exact_fact_label_permutation": label_permutation,
            "graph_size_adjusted_regression": size_regression,
        },
        "gate_c_robustness_pass": gate_c,
    }


def raw_format_representation(graph: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = dict(graph)
    # summarize_graph understands both converted and raw field names. Ambiguous
    # node ids are excluded, along with all edges incident to them.
    return summarize_graph(payload, path=Path("<in-memory-format-graph>"), file_sha256="", raw_schema=True)


def permutation_p(observed: float, null_values: list[float], alternative: str = "greater") -> float:
    if alternative == "greater":
        extreme = sum(value >= observed - 1e-15 for value in null_values)
    else:
        extreme = sum(abs(value) >= abs(observed) - 1e-15 for value in null_values)
    return (extreme + 1) / (len(null_values) + 1)


def analyze_format_variation(
    *, permutation_runs: int, seed: int
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    generation = json.loads(FORMAT_RESULTS.read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    representations: dict[tuple[str, str, str], dict[str, Any]] = {}
    print("[format] loading 27 crossed fact/format graphs", flush=True)
    for model, model_data in generation.items():
        for domain, facts in model_data.items():
            for fact, formats in facts.items():
                for format_name, metadata in formats.items():
                    path = FORMAT_DIR / metadata["slug"] / "raw_graph.json"
                    base = {
                        "model": model,
                        "domain": domain,
                        "fact": fact,
                        "format": format_name,
                        "prompt": metadata["prompt"],
                    }
                    try:
                        graph, digest = read_json_with_hash(path)
                        audit, representation = summarize_graph(
                            graph, path=path, file_sha256=digest, raw_schema=True
                        )
                        audit.update(base)
                        audit["status"] = "ok"
                        audits.append(audit)
                        if audit["dangling_edge_count"] == 0:
                            representations[(domain, fact, format_name)] = representation
                    except Exception as error:
                        audits.append({**base, "path": str(path), "status": "error", "error": repr(error)})
                    finally:
                        maybe_release_cloud_file(path)

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
    for metric in ["feature_jaccard", "feature_influence_cosine"]:
        print(f"[format] {metric}: {permutation_runs} label permutations", flush=True)
        representation_keys = sorted(representations)
        similarity_matrix: dict[
            tuple[tuple[str, str, str], tuple[str, str, str]], float
        ] = {}
        for left_key, right_key in itertools.combinations(representation_keys, 2):
            if metric == "feature_jaccard":
                value = jaccard(
                    representations[left_key]["features"], representations[right_key]["features"]
                )
            else:
                value = sparse_cosine(
                    representations[left_key]["feature_weights"],
                    representations[right_key]["feature_weights"],
                )
            similarity_matrix[(left_key, right_key)] = value

        def matrix_similarity(
            left_key: tuple[str, str, str], right_key: tuple[str, str, str]
        ) -> float:
            if left_key == right_key:
                return 1.0
            ordered = (left_key, right_key) if left_key < right_key else (right_key, left_key)
            return similarity_matrix[ordered]

        category_summary = {
            category: {
                "n_pairs": sum(row["category"] == category for row in records),
                "mean": float(np.mean([row[metric] for row in records if row["category"] == category])),
                "domain_means": {
                    domain: float(
                        np.mean(
                            [
                                row[metric]
                                for row in records
                                if row["category"] == category and row["domain"] == domain
                            ]
                        )
                    )
                    for domain in sorted({row["domain"] for row in records})
                },
            }
            for category in [
                "same_fact_different_format",
                "different_fact_same_format",
                "different_fact_different_format",
            ]
        }
        fact_effect = statistic(
            records, metric, "same_fact_different_format", "different_fact_different_format"
        )
        format_effect = statistic(
            records, metric, "different_fact_same_format", "different_fact_different_format"
        )
        null_fact: list[float] = []
        null_format: list[float] = []
        domains = sorted({key[0] for key in representations})
        for _ in range(permutation_runs):
            # Assign permuted labels to original graph keys. Similarities between
            # original graphs are precomputed once above; permutations therefore
            # change labels only and do not repeat expensive set intersections.
            fact_permuted: dict[
                tuple[str, str, str], tuple[str, str, str]
            ] = {}
            format_permuted: dict[
                tuple[str, str, str], tuple[str, str, str]
            ] = {}
            for domain in domains:
                facts = sorted({key[1] for key in representations if key[0] == domain})
                formats = sorted({key[2] for key in representations if key[0] == domain})
                # Break fact identity while preserving each format's graph distribution.
                for fmt in formats:
                    shuffled = facts[:]
                    rng.shuffle(shuffled)
                    for old_fact, new_fact in zip(facts, shuffled):
                        fact_permuted[(domain, new_fact, fmt)] = (domain, old_fact, fmt)
                # Break format identity while preserving each fact's graph distribution.
                for fact in facts:
                    shuffled_formats = formats[:]
                    rng.shuffle(shuffled_formats)
                    for old_fmt, new_fmt in zip(formats, shuffled_formats):
                        format_permuted[(domain, fact, new_fmt)] = (domain, fact, old_fmt)

            def pair_rows(
                assignment: Mapping[tuple[str, str, str], tuple[str, str, str]]
            ) -> list[dict[str, Any]]:
                permuted_rows = []
                for domain in domains:
                    keys = sorted(key for key in assignment if key[0] == domain)
                    for left_key, right_key in itertools.combinations(keys, 2):
                        _, lf, lfmt = left_key
                        _, rf, rfmt = right_key
                        if lf == rf and lfmt != rfmt:
                            category = "same_fact_different_format"
                        elif lf != rf and lfmt == rfmt:
                            category = "different_fact_same_format"
                        elif lf != rf and lfmt != rfmt:
                            category = "different_fact_different_format"
                        else:
                            continue
                        value = matrix_similarity(assignment[left_key], assignment[right_key])
                        permuted_rows.append({"domain": domain, "category": category, metric: value})
                return permuted_rows

            fact_rows = pair_rows(fact_permuted)
            format_rows = pair_rows(format_permuted)
            null_fact.append(
                statistic(
                    fact_rows, metric, "same_fact_different_format", "different_fact_different_format"
                )
            )
            null_format.append(
                statistic(
                    format_rows, metric, "different_fact_same_format", "different_fact_different_format"
                )
            )
        metrics[metric] = {
            "categories": category_summary,
            "fact_effect": fact_effect,
            "fact_effect_permutation_p": permutation_p(fact_effect, null_fact),
            "format_effect": format_effect,
            "format_effect_permutation_p": permutation_p(format_effect, null_format),
            "permutation_runs": permutation_runs,
        }
        print(f"[format] {metric}: complete", flush=True)
    return {"metrics": metrics, "pairwise_records": records}, audits


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_ready(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(payload), indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
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


def environment_record() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "command": sys.argv,
        "cwd": str(Path.cwd()),
        "protocol_path": str(PROTOCOL_PATH),
        "protocol_sha256": hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--models", nargs="+", choices=["gemma", "qwen"], default=["gemma", "qwen"])
    parser.add_argument("--audit-raw", action="store_true")
    parser.add_argument(
        "--resume-controlled",
        action="store_true",
        help="Reuse completed *.partial.json controlled audits and run only the unfinished format/finalization stage",
    )
    parser.add_argument("--skip-format", action="store_true")
    parser.add_argument("--bootstrap-runs", type=int, default=10_000)
    parser.add_argument("--permutation-runs", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260714)
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    if args.resume_controlled:
        run_record = json.loads((args.outdir / "controlled_results.partial.json").read_text())
        all_audits = json.loads((args.outdir / "converted_graph_audit.partial.json").read_text())
        raw_partial = args.outdir / "raw_graph_audit.partial.json"
        all_raw_audits = json.loads(raw_partial.read_text()) if raw_partial.exists() else []
        print("[resume] loaded completed controlled results and audits", flush=True)
    else:
        rows = load_control_manifest(args.manifest)
        run_record = {
            "schema_version": SCHEMA_VERSION,
            "environment": environment_record(),
            "seed": args.seed,
            "bootstrap_runs": args.bootstrap_runs,
            "permutation_runs": args.permutation_runs,
            "models": {},
        }
        all_audits = []
        all_raw_audits = []
        model_specs = {
            "gemma": ("gemma-2-2b", "_drop_ambiguous"),
            "qwen": ("qwen3-1-7b", ""),
        }
        for model_name in args.models:
            model_dir, variant = model_specs[model_name]
            representations, audits, raw_audits = load_controlled_cohort(
                manifest_rows=rows,
                model_dir=model_dir,
                variant=variant,
                audit_raw=args.audit_raw,
            )
            analysis = analyze_controlled(
                representations, bootstrap_runs=args.bootstrap_runs, seed=args.seed
            )
            run_record["models"][model_name] = analysis
            all_audits.extend(audits)
            all_raw_audits.extend(raw_audits)
            write_csv(args.outdir / f"{model_name}_per_fact.csv", analysis["per_fact"])

        # Persist the controlled-cohort gate before the independent format analysis
        # so a later failure cannot discard an already completed audit.
        write_json(args.outdir / "controlled_results.partial.json", run_record)
        write_json(args.outdir / "converted_graph_audit.partial.json", all_audits)
        if args.audit_raw:
            write_json(args.outdir / "raw_graph_audit.partial.json", all_raw_audits)

    format_audits: list[dict[str, Any]] = []
    if not args.skip_format:
        format_analysis, format_audits = analyze_format_variation(
            permutation_runs=args.permutation_runs, seed=args.seed
        )
        run_record["format_variation"] = format_analysis
        write_csv(args.outdir / "format_pairwise.csv", format_analysis["pairwise_records"])

    write_json(args.outdir / "whole_graph_results.json", run_record)
    write_json(args.outdir / "converted_graph_audit.json", all_audits)
    if args.audit_raw:
        write_json(args.outdir / "raw_graph_audit.json", all_raw_audits)
    if format_audits:
        write_json(args.outdir / "format_graph_audit.json", format_audits)
    write_csv(args.outdir / "converted_graph_audit.csv", all_audits)
    if args.audit_raw:
        write_csv(args.outdir / "raw_graph_audit.csv", all_raw_audits)
    print(f"Wrote publication analysis to {args.outdir}")


if __name__ == "__main__":
    main()
