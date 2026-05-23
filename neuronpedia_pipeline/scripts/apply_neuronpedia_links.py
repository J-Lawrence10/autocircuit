"""Apply Neuronpedia hyperlinks to Gemma feature IDs in cross-domain-circuits.html.

Reads the URL mapping built by build_neuronpedia_urls.py (or rebuilds it inline)
and wraps each Gemma feature ID (e.g. L0_F1813559) with an <a> tag pointing to
the Neuronpedia dashboard. Qwen IDs are left alone (they remain inside <code>
tags which is fine).

Skip rules:
- Already inside an <a> tag (avoid double-linking).
- Inside an SVG <text> or <desc> element (accessibility / not clickable as HTML).
- Inside the <head> (titles, meta).

Both plain L{n}_F{m} and <code>L{n}_F{m}</code> are wrapped:
    plain        ->  <a ...>L{n}_F{m}</a>
    <code>...    ->  <a ...><code>L{n}_F{m}</code></a>
This keeps the existing code-styled badge while making it clickable.
"""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HTML_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "cross-domain-circuits.html"
MAP_PATH = Path(__file__).resolve().parent.parent / "data" / "neuronpedia_feature_urls.json"

FEATURE_RE = re.compile(r"L(\d+)_F(\d+)")
QWEN_FEATURE_THRESHOLD = 1_000_000_000
GEMMA_LAYER_CAP = 26
SAE_WIDTH = 16384


def load_mapping() -> dict[str, str]:
    """Return {feature_id: url} for Gemma features only."""
    if MAP_PATH.exists():
        data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        return {fid: entry["url"] for fid, entry in data.items() if entry.get("url")}
    # Fallback: derive from scratch.
    html = HTML_PATH.read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    for m in FEATURE_RE.finditer(html):
        layer = int(m.group(1))
        feature_idx = int(m.group(2))
        if layer >= GEMMA_LAYER_CAP or feature_idx >= QWEN_FEATURE_THRESHOLD:
            continue
        np_id = feature_idx % SAE_WIDTH
        url = f"https://neuronpedia.org/gemma-2-2b/{layer}-gemmascope-transcoder-16k/{np_id}"
        mapping[m.group(0)] = url
    return mapping


# Regions to skip: anything between <text ...>...</text>, <desc>...</desc>,
# <head>...</head>, or inside an existing <a ...>...</a>.
SKIP_BLOCK_RE = re.compile(
    r"<text\b[^>]*>.*?</text>"
    r"|<desc\b[^>]*>.*?</desc>"
    r"|<head\b[^>]*>.*?</head>"
    r"|<a\b[^>]*>.*?</a>",
    re.IGNORECASE | re.DOTALL,
)


def compute_skip_ranges(html: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in SKIP_BLOCK_RE.finditer(html)]


def is_inside(pos: int, ranges: list[tuple[int, int]]) -> bool:
    for start, end in ranges:
        if start <= pos < end:
            return True
        if start > pos:
            break
    return False


# Match either <code>L{n}_F{m}</code> or a bare L{n}_F{m}.
TARGET_RE = re.compile(r"(<code>)?L(\d+)_F(\d+)(</code>)?")


def apply_links(html: str, url_map: dict[str, str]) -> tuple[str, int]:
    skip_ranges = compute_skip_ranges(html)
    out_parts: list[str] = []
    last = 0
    count = 0
    for m in TARGET_RE.finditer(html):
        start, end = m.span()
        if is_inside(start, skip_ranges):
            continue
        open_code, layer_s, fid_s, close_code = m.group(1), m.group(2), m.group(3), m.group(4)
        # Only wrap if both opening and closing code tags are present or both absent.
        if bool(open_code) != bool(close_code):
            continue
        feature_id = f"L{layer_s}_F{fid_s}"
        url = url_map.get(feature_id)
        if not url:
            continue  # Qwen, or unknown.
        out_parts.append(html[last:start])
        inner = m.group(0)  # Either bare or wrapped in <code>.
        out_parts.append(
            f'<a href="{url}" target="_blank" rel="noopener">{inner}</a>'
        )
        last = end
        count += 1
    out_parts.append(html[last:])
    return "".join(out_parts), count


def main() -> None:
    url_map = load_mapping()
    print(f"Loaded {len(url_map)} Gemma URLs.")
    html = HTML_PATH.read_text(encoding="utf-8")
    new_html, count = apply_links(html, url_map)
    if new_html == html:
        print("No changes.")
        return
    HTML_PATH.write_text(new_html, encoding="utf-8")
    print(f"Wrapped {count} feature ID occurrences with Neuronpedia links.")
    print(f"Wrote {HTML_PATH}")


if __name__ == "__main__":
    main()
