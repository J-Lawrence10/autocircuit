"""Build Neuronpedia URL mapping for feature IDs in cross-domain-circuits.html.

For Gemma features (layer < 26, feature_idx < 1e9):
    neuronpedia_id = feature_idx % 16384
    URL = https://neuronpedia.org/gemma-2-2b/{layer}-gemmascope-transcoder-16k/{neuronpedia_id}

For Qwen features (layer >= 26 or feature_idx >= 1e9):
    No individual feature page available on Neuronpedia (as of 2026-05).

Outputs data/neuronpedia_feature_urls.json.
"""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

# Ensure UTF-8 on Windows consoles.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HTML_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "cross-domain-circuits.html"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "neuronpedia_feature_urls.json"

FEATURE_RE = re.compile(r"L(\d+)_F(\d+)")
QWEN_FEATURE_THRESHOLD = 1_000_000_000  # Qwen circuit_tracer_ids are in the billions.
GEMMA_LAYER_CAP = 26  # Layers >= 26 are Qwen.
SAE_WIDTH = 16384


def classify(layer: int, feature_idx: int) -> str:
    if layer >= GEMMA_LAYER_CAP or feature_idx >= QWEN_FEATURE_THRESHOLD:
        return "qwen"
    return "gemma"


def build_gemma_url(layer: int, feature_idx: int) -> tuple[int, str]:
    neuronpedia_id = feature_idx % SAE_WIDTH
    url = f"https://neuronpedia.org/gemma-2-2b/{layer}-gemmascope-transcoder-16k/{neuronpedia_id}"
    return neuronpedia_id, url


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    feature_ids = sorted({m.group(0) for m in FEATURE_RE.finditer(html)})

    mapping: dict[str, dict] = {}
    for fid in feature_ids:
        m = FEATURE_RE.fullmatch(fid)
        assert m is not None
        layer = int(m.group(1))
        feature_idx = int(m.group(2))
        model = classify(layer, feature_idx)
        entry: dict = {
            "layer": layer,
            "circuit_tracer_id": feature_idx,
            "model": model,
        }
        if model == "gemma":
            np_id, url = build_gemma_url(layer, feature_idx)
            entry["neuronpedia_id"] = np_id
            entry["url"] = url
        else:
            entry["neuronpedia_id"] = None
            entry["url"] = None
            entry["note"] = "no individual feature page available"
        mapping[fid] = entry

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(mapping, indent=2, sort_keys=True), encoding="utf-8")

    # Console summary.
    gemma = [k for k, v in mapping.items() if v["model"] == "gemma"]
    qwen = [k for k, v in mapping.items() if v["model"] == "qwen"]
    print(f"Total feature IDs: {len(mapping)}")
    print(f"  Gemma (linkable): {len(gemma)}")
    print(f"  Qwen (no individual page): {len(qwen)}")
    print(f"Output: {OUT_PATH}")

    # Spot checks.
    print("\nSpot checks:")
    for fid in ("L0_F1813559", "L6_F2586668"):
        if fid in mapping:
            print(f"  {fid} -> {mapping[fid]['neuronpedia_id']} -> {mapping[fid]['url']}")


if __name__ == "__main__":
    main()
