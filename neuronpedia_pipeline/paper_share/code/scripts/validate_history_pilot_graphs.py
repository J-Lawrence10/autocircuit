"""Verify saved history follow-up artifacts without making any model requests."""
from collections import Counter
import json
from pathlib import Path
import shutil

import numpy as np

import run_history_pilot_graphs as design
from control_io import atomic_json
from whole_graph_analysis import is_feature_node, node_identity
from run_matched_choice_controls import now


def main(finalize=False):
    freeze, jobs = design.prepare()
    out = design.OUT
    result = json.loads((out / 'analysis/results.json').read_text())
    audits = {r['job_id']: r for r in result['audits']}
    assert len(audits) == 16 and set(audits) == {j['job_id'] for j in jobs}
    assert len(result['pairs']) == 56
    assert sum(r['order_only'] for r in result['pairs']) == 8
    assert sum(r['mapping_only'] for r in result['pairs']) == 8
    sets = {}
    for job in jobs:
        key = job['job_id']
        row = audits[key]
        folder = out / design.MODEL / 'graphs' / key
        raw = folder / 'raw_graph.json'
        if raw.exists():
            assert design.digest(raw) == row['raw_sha256']
            assert row['raw_sha256'] == json.loads((folder / 'metadata.json').read_text())['sha256']
        if row['graph_eligible']:
            path = folder / 'converted_graph.json'
            assert design.digest(path) == row['converted_sha256']
            graph = json.loads(path.read_text(encoding='utf-8'))
            sets[key] = {node_identity(n) for n in graph['nodes'] if is_feature_node(n)}
            assert len(sets[key]) == row['feature_count']
            assert str(graph['metadata']['model_output']).strip() == row['observed']
            assert row['correct'] == (row['observed'] == job['expected_label'])
            assert row['prediction_changed'] == (row['observed'] != job['preview_answer'])
            assert row['prompt_tokens'] == job['preview_tokens']
    validated_pairs = 0
    for pair in result['pairs']:
        if pair['status'] == 'ok':
            a, b = sets[pair['a']], sets[pair['b']]
            observed = len(a & b) / len(a | b)
            assert np.isclose(observed, pair['jaccard'], rtol=0, atol=1e-12)
            validated_pairs += 1
        else:
            assert pair['jaccard'] is None
    for row in result['block_contrasts']:
        if row.get('variant') != 'full' or row.get('metric') != 'jaccard' or row['status'] != 'ok':
            continue
        cross = [r for r in result['pairs'] if r['block'] == row['block'] and not r['same_order']]
        assert len(cross) == 16 and all(r['status'] == 'ok' for r in cross)
        for key, fact, letter in [('SS', True, True), ('SD', True, False), ('DS', False, True), ('DD', False, False)]:
            values = [r['jaccard'] for r in cross if r['same_event'] == fact and r['same_required_letter'] == letter]
            assert len(values) == 4
            assert np.isclose(np.mean(values), row[key], rtol=0, atol=1e-12)
    for path, sha in freeze['original_hashes'].items():
        assert design.digest(design.ROOT / path) == sha, f'Original archive changed: {path}'
    events = json.loads((design.ROOT / 'data/model_extension/neuronpedia_request_ledger.json').read_text())['events']
    ids = {j['job_id'] for j in jobs}
    relevant = [(i, e) for i, e in enumerate(events) if e['kind'] == 'generate' and e['job_id'] in ids]
    attempts = Counter(e['job_id'] for _, e in relevant)
    assert all(n <= 3 for n in attempts.values())
    for i, event in relevant:
        if i:
            assert event['epoch'] - events[i - 1]['epoch'] >= 124.9
        assert sum(0 <= event['epoch'] - e['epoch'] < 3600 for e in events[:i + 1]) <= 30
    verification = dict(checked_at=now(), original_archive_unchanged=True, valid_graphs=len(sets),
                        verified_pairwise_jaccards=validated_pairs, observed=result['observed'],
                        wrong_predictions_retained=sum(r['graph_eligible'] and r['correct'] is False for r in audits.values()),
                        generation_requests=len(relevant), request_spacing_passed=True,
                        max_rolling_hour_passed=True, results_sha256=design.digest(out / 'analysis/results.json'),
                        complete=len(sets) == 16, verification_scope='Local artifact checks, not independent human review')
    atomic_json(out / 'analysis/validation.json', verification)
    for path in [Path(__file__), design.ROOT / 'scripts/analyze_history_pilot_graphs.py',
                 design.ROOT / 'scripts/plot_history_pilot_graphs.py', design.ROOT / 'scripts/reproduce_history_pilot_graphs.py',
                 design.ROOT / 'tests/test_history_pilot_graphs.py']:
        name = str(path.relative_to(design.ROOT)).replace('\\', '__').replace('/', '__')
        shutil.copy2(path, out / 'code_snapshot' / name)
    manifest_path = out / 'artifact_manifest.json'
    records = []
    for path in sorted(out.rglob('*')):
        if path.is_file() and path != manifest_path and path.suffix != '.lock' and '__pycache__' not in path.parts:
            records.append(dict(path=str(path.relative_to(out)).replace('\\', '/'), bytes=path.stat().st_size, sha256=design.digest(path)))
    if finalize:
        status_path = out / 'status.json'
        status = json.loads(status_path.read_text())
        assert status['state'] in ('collection_complete', 'collection_incomplete', 'complete', 'complete_with_exclusions')
        status.update(state='complete' if len(sets) == 16 else 'complete_with_exclusions', stage='complete',
                      valid_graphs=len(sets), correct=result['correct'], wrong=result['wrong'],
                      verified_pairwise_jaccards=validated_pairs, analysis_completed_at=now())
        atomic_json(status_path, status)
        records = [r for r in records if r['path'] != 'status.json']
        records.append(dict(path='status.json', bytes=status_path.stat().st_size, sha256=design.digest(status_path)))
    atomic_json(manifest_path, dict(created_at=now(), files=records, original_archive_unchanged=True))
    print(json.dumps(verification, indent=2))
    return verification


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize', action='store_true')
    main(parser.parse_args().finalize)
