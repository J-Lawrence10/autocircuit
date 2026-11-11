"""Collect only the 16 authorized historical pilot graphs, regardless of accuracy."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import traceback

import run_matched_choice_controls as transport
from control_io import atomic_json
from matched_choice_controls import ROOT, digest
from analyze_matched_choice_controls import csv_write

OUT = ROOT / 'data/model_extension/history_pilot_graphs_20261110'
ORIGINAL = ROOT / 'data/model_extension/history_choice_final_v1'
PLAN = ROOT / 'docs/papers/HISTORY_PILOT_GRAPH_FOLLOWUP.md'
MODEL = 'qwen3-4b'
SOURCE = 'transcoder-hp'
SEED = 20261110
BLOCKS = ('pilot_documents', 'pilot_space')
SETTINGS = dict(maxNLogits=10, desiredLogitProb=.99, nodeThreshold=.8,
                edgeThreshold=.85, maxFeatureNodes=5000)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load_jobs():
    all_jobs = json.loads((ORIGINAL / 'jobs.json').read_text(encoding='utf-8'))
    original_freeze = json.loads((ORIGINAL / 'freeze.json').read_text())
    if canonical_sha(all_jobs) != original_freeze['jobs_sha256']:
        raise ValueError('Original archived jobs differ from their freeze')
    jobs = sorted((j.copy() for j in all_jobs if j['split'] == 'pilot'), key=lambda j: j['job_id'])
    expected = {f'{b}__f{f}m{m}w{w}' for b in BLOCKS for f, m, w in itertools.product(range(2), repeat=3)}
    if len(jobs) != 16 or {j['job_id'] for j in jobs} != expected:
        raise ValueError('Only the exact 16 historical pilot prompts are authorized')
    for job in jobs:
        response_path = ORIGINAL / MODEL / 'pilot' / job['job_id'] / 'response.json'
        response = json.loads(response_path.read_text(encoding='utf-8'))
        if transport.clean_prompt(response.get('prompt', '')) != job['prompt']:
            raise ValueError(f'Archived prompt mismatch: {job["job_id"]}')
        if hashlib.sha256(job['prompt'].encode()).hexdigest() != job['prompt_sha256']:
            raise ValueError('Prompt hash mismatch')
        top = max(response['salient_logits'], key=lambda r: r['probability'])
        job.update(preview_answer=str(top['token']).strip(), preview_probability=top['probability'],
                   preview_tokens=response['input_tokens'], preview_sha256=digest(response_path),
                   source_response_path=str(response_path.relative_to(ROOT)))
    for block in BLOCKS:
        rows = [j for j in jobs if j['block'] == block]
        bags = [Counter(j['preview_tokens']) for j in rows]
        if not bags[0] or any(b != bags[0] for b in bags):
            raise ValueError('Archived block token inventories do not match')
        if any(len(j['preview_tokens']) + 1 > 64 for j in rows):
            raise ValueError('Archived prompt exceeds the 64-token limit')
    return jobs


def prepare():
    jobs = load_jobs()
    files = [PLAN, Path(__file__), ROOT / 'scripts/run_matched_choice_controls.py',
             ROOT / 'scripts/control_io.py', ROOT / 'scripts/matched_choice_controls.py',
             ROOT / 'scripts/convert_model_extension.py', ROOT / 'scripts/2_convert_graph.py',
             ROOT / 'scripts/whole_graph_analysis.py', ROOT / 'scripts/analyze_matched_choice_controls.py',
             ROOT / 'scripts/audit_paper_closeout.py']
    sources = [ORIGINAL / name for name in ('jobs.json', 'freeze.json', 'pilot_gate.json', 'status.json')]
    sources += [ROOT / j['source_response_path'] for j in jobs]
    record = dict(authorization_date='2026-11-10', model=MODEL, source=SOURCE, settings=SETTINGS,
                  graph_jobs=16, jobs_sha256=canonical_sha(jobs), seed=SEED,
                  post_interval_seconds=125, requests_per_rolling_hour=30, max_attempts_per_job=3,
                  correctness_is_inclusion_gate=False,
                  analysis_status='additional_analysis_after_observing_preview_answers_before_graphs',
                  file_hashes={str(p.relative_to(ROOT)): digest(p) for p in files},
                  original_hashes={str(p.relative_to(ROOT)): digest(p) for p in sources})
    target = OUT / 'freeze.json'
    if target.exists():
        existing = json.loads(target.read_text())
        candidate = dict(existing)
        candidate.pop('frozen_at')
        if candidate != record:
            raise ValueError('Frozen collection or original source changed; inspect without overwriting')
        return existing, jobs
    record['frozen_at'] = transport.now()
    OUT.mkdir(parents=True, exist_ok=True)
    atomic_json(target, record)
    atomic_json(OUT / 'jobs.json', jobs)
    csv_write(OUT / 'jobs.csv', jobs)
    snapshot = OUT / 'code_snapshot'
    snapshot.mkdir(exist_ok=True)
    for path in files:
        shutil.copy2(path, snapshot / str(path.relative_to(ROOT)).replace('\\', '__').replace('/', '__'))
    for job in jobs:
        dest = OUT / 'previews' / job['job_id']
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / job['source_response_path'], dest / 'response.json')
    atomic_json(OUT / 'status.json', dict(state='prepared', planned=16, graphs_complete=0,
                                        frozen_at=record['frozen_at']))
    return record, jobs


def inventory(jobs):
    rows = []
    for job in jobs:
        folder = OUT / MODEL / 'graphs' / job['job_id']
        raw, meta, state_path = folder / 'raw_graph.json', folder / 'metadata.json', folder / 'request_state.json'
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
        row = dict(job_id=job['job_id'], raw_present=raw.exists(), request_status=state.get('status'),
                   attempts=state.get('attempts', 0), raw_sha256=None, checksum_verified=False)
        if raw.exists():
            if not meta.exists():
                raise ValueError(f'Missing metadata for existing raw graph: {job["job_id"]}')
            row['raw_sha256'] = digest(raw)
            row['checksum_verified'] = row['raw_sha256'] == json.loads(meta.read_text())['sha256']
            if not row['checksum_verified']:
                raise ValueError(f'Checksum mismatch: {job["job_id"]}')
        rows.append(row)
    csv_write(OUT / 'checksums.csv', rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    record, jobs = prepare()
    rows = inventory(jobs)
    if not args.execute:
        print(f'Frozen 16 unchanged history jobs. Archived: {sum(r["checksum_verified"] for r in rows)}/16. No requests made.')
        return
    transport.OUT = OUT
    transport.MODELS = {MODEL: SOURCE}
    with transport.file_lock(OUT / 'runner.lock'):
        status = dict(state='running', stage='generation', pid=os.getpid(), started_at=transport.now(),
                      planned=16, graphs_complete=sum(r['checksum_verified'] for r in rows), errors=[])
        def save(**updates):
            status.update(updated_at=transport.now(), **updates)
            atomic_json(OUT / 'status.json', status)
        try:
            client = transport.Client()
            for job in jobs:
                save(current_job=job['job_id'])
                try:
                    transport.graph_job(client, MODEL, job, record['settings'])
                except Exception as error:
                    state_path = OUT / MODEL / 'graphs' / job['job_id'] / 'request_state.json'
                    state = json.loads(state_path.read_text()) if state_path.exists() else {}
                    status['errors'].append(dict(job_id=job['job_id'], error=str(error)))
                    if state.get('status') in ('uncertain', 'submitting'):
                        raise
                    # An explicit failure is retained; other authorized jobs can still be attempted.
                    print(f'Job failure retained: {job["job_id"]}: {error}', flush=True)
                rows = inventory(jobs)
                save(graphs_complete=sum(r['checksum_verified'] for r in rows))
                print(f'Archived {status["graphs_complete"]}/16: {job["job_id"]}', flush=True)
            complete = status['graphs_complete'] == 16
            save(state='collection_complete' if complete else 'collection_incomplete', stage='awaiting_analysis',
                 finished_at=transport.now())
        except Exception as error:
            save(state='blocked', error=str(error), traceback=traceback.format_exc())
            raise


if __name__ == '__main__':
    main()
