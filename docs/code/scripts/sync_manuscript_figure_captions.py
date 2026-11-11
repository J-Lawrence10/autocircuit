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


def reconcile(text, figure_root=None, reviewed=False):
    if reviewed:
        from review_figure_catalog import catalog
        entries = catalog()
        titles = {r['stem']: r['title'] for r in entries}
        captions = {r['stem']: r['legend'] for r in entries}
    else:
        titles, captions = wording.TITLES, wording.CAPTIONS
    seen = []
    def replace(match):
        number, path, stem = match.groups()
        if stem not in titles or stem not in captions:
            raise ValueError(f'Unreviewed figure: {stem}')
        expected = re.fullmatch(r'figure(S?\d+)_.+', stem).group(1)
        if number != expected or stem in seen:
            raise ValueError(f'Duplicate or inconsistent figure: {stem}')
        seen.append(stem)
        if figure_root is not None and (reviewed or number != '7'):
            path = (figure_root / f'{stem}.png').as_posix()
        title, caption = titles[stem], captions[stem]
        return f'![Figure {number}: {title}]({path})\n\n**Figure {number}. {title}.** {caption}\n'
    updated = PATTERN.sub(replace, text)
    if set(seen) != set(titles):
        raise ValueError(f'Figure set differs: {set(seen) ^ set(titles)}')
    return updated, len(seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--reviewed', action='store_true', help='Use the approved six-main-figure, ten-supplement edition.')
    parser.add_argument('--figure-root', type=Path, help='Current figure directory; legacy mode preserves the archived history figure.')
    args = parser.parse_args()
    text = MANUSCRIPT.read_text(encoding='utf-8')
    updated, count = reconcile(text, args.figure_root.resolve() if args.figure_root else None, args.reviewed)
    if updated != text:
        if not args.write:
            raise SystemExit('Caption wording differs; review and run with --write to synchronize.')
        MANUSCRIPT.write_text(updated, encoding='utf-8')
    print(f'Checked {count} reviewed figure titles and captions; body prose preserved.')


if __name__ == '__main__':
    main()
