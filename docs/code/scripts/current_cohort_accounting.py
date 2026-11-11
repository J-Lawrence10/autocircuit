"""Render current inclusion counts from frozen decisions; do not rerun eligibility.

Gemma/Qwen4 historical rows are preserved verbatim. Only Qwen1.7 rows use the
completed saved analysis. A strict-token mismatch remains an audit string, not
a claim about the correctness of a full response. Missing roles take priority
exactly as recorded by the saved analysis, including for empty history sets.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = Path('data/model_extension/paper_figures_draft_20261005/tables/test_fact_inclusion_audit.csv')
ANALYSIS = Path('data/model_extension/qwen17_completion_20261106/analysis/results.json')
FROZEN = {
    ORIGINAL.as_posix(): '39a11d7928456bfad760bae386d4614386fcd3f04dfc10d89f4b986fffe9740d',
    ANALYSIS.as_posix(): '7b7c6ecf14c027c868a8eb6553c1b1f66bf2acf4397dd4318ec7d0fee11d477b',
}
MODEL = 'Qwen3-1.7B'
COHORT = 'expanded91_late_observational'
FIELDS = ['model', 'domain', 'pair_id', 'available_graphs', 'planned_graphs',
          'included', 'reason', 'observed_mismatched_tokens']
ROLES = {'target', 'positive_paraphrase', 'negative_same_template', 'negative_nonce'}


def input_hashes(root=ROOT):
    hashes = {name: hashlib.sha256((Path(root)/name).read_bytes()).hexdigest() for name in FROZEN}
    assert hashes == FROZEN, 'Frozen inclusion inputs changed; do not silently reinterpret the cohort.'
    return hashes


def reconcile_rows(original, analysis):
    assert analysis['status'] == 'completed' and analysis['original_reconstruction']['passed']
    assert len(original) == 45 and len({(r['model'], r['pair_id']) for r in original}) == 45
    assert {r['model'] for r in original} == {'Gemma-2-2B', MODEL, 'Qwen3-4B*'}
    saved = [r for r in analysis['eligibility'] if r['cohort'] == COHORT and r['split'] == 'held_out']
    assert len(saved) == 15 and len({r['pair_id'] for r in saved}) == 15
    lookup = {r['pair_id']: r for r in saved}
    original_qwen = [r for r in original if r['model'] == MODEL]
    assert {r['pair_id'] for r in original_qwen} == set(lookup)
    output = []
    for row in original:
        if row['model'] != MODEL:
            output.append(dict(row))
            continue
        saved_row = lookup[row['pair_id']]
        assert row['domain'] == saved_row['domain']
        present, missing = set(saved_row['present_roles']), set(saved_row['missing_roles'])
        assert present.isdisjoint(missing) and present | missing == ROLES
        assert len(present) == len(saved_row['present_roles'])
        mismatches = {role: saved_row['factual_outputs'][role]
                      for role in saved_row['incorrect_factual_roles']}
        assert all(value is not None for value in mismatches.values())
        output.append(dict(model=MODEL, domain=row['domain'], pair_id=row['pair_id'],
                           available_graphs=str(len(present)), planned_graphs='4',
                           included=str(saved_row['included_in_comparisons']),
                           reason=saved_row['exclusion_reason'],
                           observed_mismatched_tokens=json.dumps(mismatches, sort_keys=True)))
    assert len(output) == 45
    qwen = [r for r in output if r['model'] == MODEL]
    assert sum(r['included'] == 'True' for r in qwen) == 10
    assert [sum(r['included'] == 'True' for r in qwen if r['domain'] == d)
            for d in ['chemistry', 'geography', 'history']] == [5, 5, 0]
    history = [r for r in qwen if r['domain'] == 'history']
    assert sorted(int(r['available_graphs']) for r in history) == [0, 0, 1, 2, 2]
    assert all(r['reason'] == 'incomplete_roles' for r in history)
    return output


def current_rows(root=ROOT):
    root = Path(root)
    input_hashes(root)
    with (root/ORIGINAL).open(encoding='utf-8-sig', newline='') as handle:
        original = list(csv.DictReader(handle))
    analysis = json.loads((root/ANALYSIS).read_text(encoding='utf-8'))
    return reconcile_rows(original, analysis)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT/'data/model_extension/paper_figures_plain_language_20261006/tables/test_fact_inclusion_audit.csv')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output not in {(ROOT/ORIGINAL).resolve(), (ROOT/ANALYSIS).resolve()}, 'Cannot overwrite frozen inputs.'
    rows = current_rows()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote {len(rows)} current inclusion rows from frozen decisions: {output}')


if __name__ == '__main__':
    main()
