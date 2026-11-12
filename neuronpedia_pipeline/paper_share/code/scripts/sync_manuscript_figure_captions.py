"""Synchronize figure captions to the reviewed wording without editing body prose.

Use --write for this mechanical formatting operation; the default only checks.
No data analysis, graph generation, or scientific-value changes are performed.
"""
from pathlib import Path
import argparse
from copy import deepcopy
import difflib
import hashlib
import html
import json
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


def reconcile_manifest(manifest, entries, catalog_hash):
    """Update legend text without regenerating artwork or statistical outputs."""
    updated = deepcopy(manifest)
    rows = updated['figures'] + updated['supplements']
    by_stem = {row['stem']: row for row in entries}
    if {row['stem'] for row in rows} != set(by_stem):
        raise ValueError('Caption-only updates cannot add or remove figures')
    changed = []
    for row in rows:
        entry = by_stem[row['stem']]
        if any(row[key] != entry[key] for key in ['title', 'label', 'stem']):
            raise ValueError('Figure titles or identity changed; rebuild artwork separately')
        if row['legend'] != entry['legend']:
            changed.append(row['label'])
            row['legend'] = entry['legend']
    updated['source_hashes']['scripts/review_figure_catalog.py'] = catalog_hash
    if changed:
        updated.setdefault('legend_edit_history', []).append({
            'figures': changed, 'artwork_regenerated': False,
            'measurements_reestimated': False, 'catalog_sha256': catalog_hash})
    return updated, changed


def word_diff(old, new):
    left, right = old.split(), new.split()
    pieces = []
    for operation, _, _, start, end in difflib.SequenceMatcher(None, left, right, autojunk=False).get_opcodes():
        content = html.escape(' '.join(right[start:end]))
        if not content:
            continue
        pieces.append(content if operation == 'equal' else f'<mark>{content}</mark>')
    return ' '.join(pieces)


def write_review(folder, old, new, figure_root):
    """Generate a local read-only review with all artwork and highlighted edits."""
    import os
    folder = folder.resolve()
    if not folder.is_relative_to((ROOT/'data/model_extension').resolve()):
        raise ValueError('Keep editorial review files in the local project archive')
    if (folder/'index.html').exists():
        raise FileExistsError('Choose a fresh review folder to preserve the prior comparison')
    folder.mkdir(parents=True, exist_ok=True)
    previous = {row['stem']: row for row in old['figures'] + old['supplements']}
    articles, changes, links = [], [], []
    for row in new['figures'] + new['supplements']:
        before = previous[row['stem']]
        label = row['label']
        image = Path(os.path.relpath(figure_root/f'{row["stem"]}.svg', folder)).as_posix()
        title = f'Figure {label}. {row["title"]}'
        links.append(f'<a href="#figure-{label}">{label}</a>')
        articles.append(
            f'<article id="figure-{label}"><h2>{html.escape(title)}</h2>'
            f'<a href="{image}" target="_blank" rel="noopener"><img src="{image}" '
            f'alt="{html.escape(title)}" loading="lazy"></a><h3>Revised legend</h3>'
            f'<p>{word_diff(before["legend"], row["legend"])}</p>'
            f'<details><summary>Previous legend</summary><p>{html.escape(before["legend"])}</p></details></article>')
        changes.append(dict(label=label, title=row['title'], previous=before['legend'], revised=row['legend'],
                            previous_words=len(before['legend'].split()), revised_words=len(row['legend'].split())))
    css = ('body{max-width:1100px;margin:35px auto;padding:0 22px;font:17px/1.65 system-ui;color:#193747}'
           'h1,h2,h3{line-height:1.25}nav{display:flex;gap:8px;flex-wrap:wrap;margin:24px 0}'
           'nav a{padding:5px 12px;background:#edf4f8;border:1px solid #bed0da;border-radius:5px}'
           'a{color:#155b7d}article{margin:45px 0;padding-top:20px;border-top:2px solid #c6d5dd}'
           'article img{display:block;max-width:100%;width:760px;height:auto;margin:20px auto;border:1px solid #c6d5dd}'
           'mark{background:#fff1b8;color:inherit}details{padding:12px 18px;background:#f1f5f8;border-radius:6px}'
           'summary{cursor:pointer;font-weight:600}p{overflow-wrap:anywhere}'
           '@media print{nav,details{display:none}mark{background:none}}')
    document = ('<!doctype html><html lang="en-US"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>All 16 revised figure legends</title><style>{css}</style></head><body>'
                '<h1>All 16 revised figure legends</h1>'
                '<p>Yellow highlights identify new or rewritten wording. Expand “Previous legend” to compare. '
                'Click any figure to open its vector artwork. Figure titles, artwork, data, and statistical results are unchanged.</p>'
                f'<nav aria-label="Figures">{"".join(links)}</nav>{"".join(articles)}</body></html>')
    (folder/'index.html').write_text(document, encoding='utf-8')
    (folder/'changes.json').write_text(json.dumps(changes, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


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
    parser.add_argument('--update-reviewed-manifest', action='store_true', help='Synchronize legend metadata without rerendering figures.')
    parser.add_argument('--review-output', type=Path, help='Fresh local folder for an illustrated, highlighted legend review.')
    args = parser.parse_args()
    if args.review_output and not args.update_reviewed_manifest:
        parser.error('--review-output requires --update-reviewed-manifest')
    pending = None
    if args.update_reviewed_manifest:
        if not args.reviewed or not args.write:
            parser.error('--update-reviewed-manifest requires --reviewed --write')
        from review_figure_catalog import FIG, catalog
        manifest_path = FIG/'figure_manifest.json'
        original = json.loads(manifest_path.read_text(encoding='utf-8'))
        for source, expected in original['source_hashes'].items():
            if source != 'scripts/review_figure_catalog.py':
                assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest() == expected, source
        for output, expected in original['output_hashes'].items():
            assert hashlib.sha256((FIG/output).read_bytes()).hexdigest() == expected, output
        updated_manifest, changed = reconcile_manifest(original, catalog(),
            hashlib.sha256((ROOT/'scripts/review_figure_catalog.py').read_bytes()).hexdigest())
        pending = manifest_path, updated_manifest, changed
        if args.review_output and changed:
            write_review(args.review_output, original, updated_manifest, FIG)
    text = MANUSCRIPT.read_text(encoding='utf-8')
    updated, count = reconcile(text, args.figure_root.resolve() if args.figure_root else None, args.reviewed)
    if updated != text:
        if not args.write:
            raise SystemExit('Caption wording differs; review and run with --write to synchronize.')
        MANUSCRIPT.write_text(updated, encoding='utf-8')
    if pending:
        path, value, changed = pending
        path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
        print(f'Updated legend metadata for {len(changed)} figures; artwork and source tables unchanged.')
    print(f'Checked {count} reviewed figure titles and captions; body prose preserved.')


if __name__ == '__main__':
    main()
