"""Offline package integrity and headline-value checks; standard library only.

This is not raw-graph reproduction and does not establish scientific validity.
Run: python code/verify_package.py from the paper_share directory.
"""
from pathlib import Path
import csv
import hashlib
import json
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT/'provenance/package_manifest.json').read_text(encoding='utf-8'))
for row in manifest['files']:
    p = (ROOT/row['path']).resolve()
    assert p.is_relative_to(ROOT.resolve()), row['path']
    assert p.is_file() and p.stat().st_size == row['bytes'], row['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], row['path']

def rows(name):
    with (ROOT/'tables'/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

original = rows('figure2_summary.csv')
assert [int(r['n']) for r in original] == [8, 5, 10]
assert [round(float(r['mean']), 3) for r in original] == [.170, .085, .162]
blocks = rows('figure5_block_contrasts.csv')
assert len(blocks) == 6
assert round(mean(float(r['fact_same_label']) for r in blocks), 4) == .0628
assert round(mean(float(r['fact_different_label']) for r in blocks), 4) == -.0022
pairs = {}
for r in rows('figure6_comparisons.csv'):
    pairs.setdefault(r['job_id'], {})[r['comparator']] = float(r['jaccard'])
assert len(pairs) == 8 and all(p['same_output'] > p['same_country'] for p in pairs.values())
pilot = next(r for r in rows('table_history_pilot.csv') if r['component'] == 'Overall')
assert (int(pilot['correct']), int(pilot['total'])) == (15, 20)
print(f"Verified {len(manifest['files'])} file hashes and headline values from included tables.")
print('These checks do not reproduce raw graph extraction or provide independent scientific review.')
