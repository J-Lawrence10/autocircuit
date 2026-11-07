"""Synchronize figure captions to the reviewed wording without editing body prose.

Use --write for this mechanical formatting operation; the default only checks.
No data analysis, graph generation, or scientific-value changes are performed.
"""
from pathlib import Path
import argparse
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figure_plain_language as wording

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT/'docs/papers/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md'
PATTERN = re.compile(
    r'!\[Figure (S?\d+): [^\]\n]*\]\(([^\n]+/(figure[^/]+)\.png)\)'
    r'\n\n\*\*Figure \1\.[^\n]+\n'
)


def reconcile(text):
    seen = []
    def replace(match):
        number, path, stem = match.groups()
        if stem not in wording.TITLES or stem not in wording.CAPTIONS:
            raise ValueError(f'Unreviewed figure: {stem}')
        expected = re.fullmatch(r'figure(S?\d+)_.+', stem).group(1)
        if number != expected or stem in seen:
            raise ValueError(f'Duplicate or inconsistent figure: {stem}')
        seen.append(stem)
        title, caption = wording.TITLES[stem], wording.CAPTIONS[stem]
        return f'![Figure {number}: {title}]({path})\n\n**Figure {number}. {title}.** {caption}\n'
    updated = PATTERN.sub(replace, text)
    if set(seen) != set(wording.TITLES):
        raise ValueError(f'Figure set differs: {set(seen) ^ set(wording.TITLES)}')
    return updated, len(seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    text = MANUSCRIPT.read_text(encoding='utf-8')
    updated, count = reconcile(text)
    if updated != text:
        if not args.write:
            raise SystemExit('Caption wording differs; review and run with --write to synchronize.')
        MANUSCRIPT.write_text(updated, encoding='utf-8')
    print(f'Checked {count} reviewed figure titles and captions; body prose preserved.')


if __name__ == '__main__':
    main()
