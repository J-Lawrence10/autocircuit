"""Validate the bounded recovery and saved-data integration; never make requests."""
from collections import Counter
import csv
import json
from pathlib import Path
import shutil

from complete_qwen4_controls import ROOT, OUT, EXPECTED, PREFIX, LEDGER, digest
from control_io import atomic_json
from run_matched_choice_controls import now

FIG = ROOT/'data/model_extension/paper_figures_qwen4_complete_20261110'
OLD_FIG = ROOT/'data/model_extension/paper_figures_plain_language_20261006'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def main():
    frozen = read(OUT/'freeze.json')
    for path, sha in frozen['dependencies'].items():
        assert digest(ROOT/path) == sha, path
    for row in frozen['original_raw']:
        assert digest(ROOT/row['path']) == row['sha256'], row['path']
    status = read(OUT/'status.json')
    assert status['state'] == 'two_attempts_finished' and status['generation_requests'] == 2
    assert set(status['jobs']) == set(EXPECTED) and set(status['jobs'].values()) == {'saved_valid'}
    for job, prompt in EXPECTED.items():
        directory = OUT/'graphs'/job
        state = read(directory/'request_state.json')
        assert state['attempts'] == 1 and state['payload']['prompt'] == prompt
        audit = read(directory/'audit.json')
        assert audit['technical_passed']
        for kind in ['raw', 'converted']:
            assert digest(directory/f'{kind}_graph.json') == audit[f'{kind}_sha256']
    starts = sorted(read(LEDGER)['events'], key=lambda e: e['epoch'])
    mine = [e for e in starts if e['job_id'].startswith(PREFIX)]
    assert Counter(e['job_id'][len(PREFIX):] for e in mine) == Counter(EXPECTED.keys())
    for i, event in enumerate(starts):
        if event['job_id'].startswith(PREFIX):
            assert i == 0 or event['epoch'] - starts[i-1]['epoch'] >= 124.999
            assert sum(0 <= event['epoch'] - e['epoch'] < 3600 for e in starts[:i+1]) <= 30
    verification = read(OUT/'analysis/verification.json')
    assert verification['original_reconstruction_passed'] and verification['primary_margins_unchanged']
    assert verification['original_primary'] == verification['current_primary']
    assert verification['heldout_facts'] == 10 and verification['heldout_history_facts'] == 0
    assert verification['complete_controlled_graphs'] + verification['complete_crossed_graphs'] == 147
    changed = {'figureS1_quality.csv', 'figureS1_influence_values.csv',
               'figureS5_answer_audit.csv', 'test_fact_inclusion_audit.csv'}
    unchanged = []
    for path in sorted((FIG/'tables').glob('*.csv')):
        if path.name in changed:
            continue
        current, original = rows(path), rows(OLD_FIG/'tables'/path.name)
        for row in original:
            if row.get('model') == 'Qwen3-4B*':
                row['model'] = 'Qwen3-4B'
        assert current == original, path.name
        unchanged.append(path.name)
    quality = rows(FIG/'tables/figureS1_quality.csv')
    assert sum(int(r['graphs']) for r in quality) == 385
    q4 = next(r for r in quality if r['cohort'] == 'Qwen4 controlled')
    assert int(q4['graphs']) == 120 and int(q4['ambiguous_raw_exports']) == 0
    display = read(OUT/'analysis/display_audit.json')
    assert display['recovered_answer']['strict_string_match'] is False
    assert display['recovered_answer']['top_text'].strip() == 'María'
    assert sum(display['answers']['statuses'].values()) == 60
    manifest = read(FIG/'figure_manifest.json')
    for path, sha in manifest['source_hashes'].items():
        assert digest(ROOT/path) == sha, path
    for path, sha in manifest['output_hashes'].items():
        assert digest(FIG/path) == sha, path
    scripts = ['analyze_qwen4_completion', 'build_qwen4_completion_figures',
               'validate_qwen4_completion', 'plot_updated_cohort_figures', 'figure_plain_language',
               'build_outline_figures_v2', 'current_cohort_accounting']
    snapshot = OUT/'analysis/code_snapshot'
    snapshot.mkdir(exist_ok=True)
    code = {}
    for script in scripts:
        source = ROOT/'scripts'/f'{script}.py'
        shutil.copy2(source, snapshot/source.name)
        code[source.relative_to(ROOT).as_posix()] = digest(source)
    result = dict(checked_at=now(), passed=True, generation_posts=2, attempts_per_job=1,
                  shared_rate_checks_passed=True, original_raw_hashes_verified=145,
                  recovered_raw_hashes_verified=2, frozen_dependencies_unchanged=True,
                  primary_estimates_unchanged=True, unchanged_figure_tables=unchanged,
                  current_graph_count=385, qwen4_graph_count=147,
                  analysis_source_hashes=code,
                  local_troubleshooting='An initial saved-data report writer failed on a dictionary key after analysis. The key access was corrected and the complete analysis reran successfully from saved files, with no new requests or scientific-rule changes.')
    atomic_json(OUT/'analysis/integration_validation.json', result)
    collection = OUT/'collection_artifact_manifest.json'
    if not collection.exists():
        shutil.copy2(OUT/'artifact_manifest.json', collection)
    files = [dict(path=p.relative_to(OUT).as_posix(), bytes=p.stat().st_size, sha256=digest(p))
             for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'artifact_manifest.json'
             and p.suffix != '.lock' and '__pycache__' not in p.parts]
    atomic_json(OUT/'artifact_manifest.json', dict(created_at=now(), files=files))
    print(json.dumps({k: result[k] for k in ['passed', 'generation_posts', 'primary_estimates_unchanged', 'current_graph_count', 'qwen4_graph_count']}, indent=2))


if __name__ == '__main__':
    main()
