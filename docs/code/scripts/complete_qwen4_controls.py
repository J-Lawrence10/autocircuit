"""One new POST for each of two missing original Qwen3-4B jobs; never retry."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
import traceback

import requests

from control_io import atomic_json, replace_with_retry
from convert_model_extension import raw_integrity, converted_integrity, load_converter
from run_matched_choice_controls import Client, clean_prompt, file_lock, now, reserve_post, LEDGER
from whole_graph_analysis import summarize_graph

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'data/model_extension/qwen3-4b'
OUT = ROOT / 'data/model_extension/qwen4_completion_20261110'
PROTOCOL = ROOT / 'docs/papers/QWEN4_COMPLETION_ATTEMPT_20261110.md'
MODEL, SOURCE = 'qwen3-4b', 'transcoder-hp'
PREFIX = 'q4-completion-20261110-'
EXPECTED = {
    'columbus_americas__positive_paraphrase': "Columbus's flagship in 1492 was the Santa",
    'columbus_americas__negative_nonce': "Torven's flagship in 2192 was the Pelorian",
}
MANIFEST_SHA = 'c2c36a46e09a4c7943ff38e537f78cf3e7d4aa27e031b011be3b6035c6106196'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def log(message):
    line = f'{now()} {message}'
    print(line, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'stdout.log').open('a', encoding='utf-8') as stream:
        stream.write(line + '\n')


def payload_for(job):
    if job['job_id'] not in EXPECTED or job['prompt'] != EXPECTED[job['job_id']]:
        raise ValueError('Job or prompt is outside the two authorized requests')
    return dict(prompt=job['prompt'], modelId=MODEL, sourceSetName=SOURCE,
                desiredLogitProb=.99, slug=(PREFIX + job['job_id']).replace('_', '-'))


def prepare():
    assert digest(ROOT / 'config/paper_control_manifest.csv') == MANIFEST_SHA
    jobs = read_csv(ORIGINAL / 'jobs.csv')
    assert len(jobs) == 147 and len({j['job_id'] for j in jobs}) == 147
    missing = [j for j in jobs if not (ROOT / j['raw_graph_path']).exists()]
    assert {j['job_id'] for j in missing} == set(EXPECTED), 'Original inventory changed'
    assert all(j['design'] == 'controlled' and j['model_id'] == MODEL and
               j['source_set'] == SOURCE and j['split'] == 'held_out' for j in missing)
    for job in missing:
        payload_for(job)
    checksums = read_csv(ORIGINAL / 'checksums.csv')
    assert len(checksums) == 145
    assert {r['job_id'] for r in checksums} == {j['job_id'] for j in jobs} - set(EXPECTED)
    log('Verifying the 145 original raw graph hashes before any new request')
    for row in checksums:
        assert digest(ROOT / row['path']) == row['sha256'], row['job_id']
    dependencies = [Path(__file__), PROTOCOL, ROOT / 'scripts/run_matched_choice_controls.py',
                    ROOT / 'scripts/control_io.py', ROOT / 'scripts/convert_model_extension.py',
                    ROOT / 'scripts/2_convert_graph.py', ROOT / 'scripts/whole_graph_analysis.py',
                    ROOT / 'scripts/analyze_model_extension.py', ROOT / 'config/model_extension.json',
                    ROOT / 'config/paper_control_manifest.csv', ORIGINAL / 'jobs.csv',
                    ORIGINAL / 'checksums.csv', ORIGINAL / 'generation_status.json',
                    ORIGINAL / 'analysis/model_extension_results.json']
    fingerprints = {p.relative_to(ROOT).as_posix(): digest(p) for p in dependencies}
    freeze_path = OUT / 'freeze.json'
    if freeze_path.exists():
        frozen = json.loads(freeze_path.read_text())
        assert frozen['dependencies'] == fingerprints, 'Frozen inputs or collector changed'
        assert frozen['jobs'] == missing and frozen['original_raw'] == checksums
        return frozen
    frozen = dict(created_at=now(), model=MODEL, source_set=SOURCE, jobs=missing,
                  payloads=[payload_for(j) for j in missing], max_new_posts_per_job=1,
                  dependencies=fingerprints, original_raw=checksums)
    snapshot = OUT / 'code_snapshot'
    snapshot.mkdir(parents=True, exist_ok=True)
    for p in dependencies:
        shutil.copy2(p, snapshot / p.relative_to(ROOT).as_posix().replace('/', '__'))
    with (OUT / 'jobs.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(missing[0]))
        writer.writeheader()
        writer.writerows(missing)
    atomic_json(freeze_path, frozen)
    return frozen


def reconcile_once(client, payload, folder):
    try:
        recovered = client.reconcile(MODEL, payload['slug'])
        atomic_json(folder / 'reconciliation.json', dict(checked_at=now(), found=bool(recovered)))
        if recovered:
            atomic_json(folder / 'response.json', recovered)
        return recovered
    except Exception as exc:
        atomic_json(folder / 'reconciliation.json', dict(checked_at=now(), found=False,
                    error_type=type(exc).__name__))
        return None


def post_once(client, job, folder):
    folder.mkdir(parents=True, exist_ok=True)
    payload = payload_for(job)
    response_path, state_path = folder / 'response.json', folder / 'request_state.json'
    if response_path.exists():
        return json.loads(response_path.read_text())
    if state_path.exists():
        state = json.loads(state_path.read_text())
        assert state['payload'] == payload and state['attempts'] == 1
        return reconcile_once(client, payload, folder)  # GET only, never another POST.
    if LEDGER.exists() and any(e['job_id'] == PREFIX + job['job_id']
                               for e in json.loads(LEDGER.read_text())['events']):
        raise RuntimeError('A request reservation already exists without local state; no duplicate POST')
    reserve_post(MODEL, PREFIX + job['job_id'], 'generate')
    state = dict(status='submitting', attempts=1, started_at=now(), payload=payload)
    atomic_json(state_path, state)
    log(f"SUBMIT {job['job_id']} (one authorized attempt)")
    try:
        response = requests.post(client.base + '/graph/generate', headers=client.headers,
                                 json=payload, timeout=(30, 360))
    except requests.RequestException as exc:
        atomic_json(state_path, dict(state, status='uncertain', error_type=type(exc).__name__, updated_at=now()))
        return reconcile_once(client, payload, folder)
    try:
        body = response.json()
    except ValueError:
        body = {'non_json_response': response.text[:2000]}
    atomic_json(folder / 'http_attempt_1.json', dict(status_code=response.status_code, body=body,
                retry_after=response.headers.get('Retry-After'), received_at=now()))
    if response.status_code == 200:
        atomic_json(response_path, body)
        atomic_json(state_path, dict(state, status='received', updated_at=now()))
        return body
    until = 0
    if response.status_code == 429:
        retry = response.headers.get('Retry-After', '')
        try:
            delay = float(retry) if retry else 3600
        except ValueError:
            from email.utils import parsedate_to_datetime
            try:
                delay = parsedate_to_datetime(retry).timestamp() - time.time()
            except (ValueError, TypeError):
                delay = 3600
        until = time.time() + max(0, delay)
    atomic_json(state_path, dict(state, status='http_error', status_code=response.status_code,
                retry_not_before=until, updated_at=now()))
    return reconcile_once(client, payload, folder)


def audit_graph(raw, job):
    graph = json.loads(raw.read_bytes())
    meta = graph.get('metadata', {})
    checks = dict(model=meta.get('scan', meta.get('model')) == MODEL,
                  prompt=clean_prompt(meta.get('prompt', '')) == job['prompt'])
    for key, expected in [('max_n_logits', 10), ('desired_logit_prob', .99), ('max_feature_nodes', 5000)]:
        checks[key] = meta.get('generation_settings', {}).get(key) == expected
    for key, expected in [('node_threshold', .8), ('edge_threshold', .85)]:
        checks[key] = meta.get('pruning_settings', {}).get(key) == expected
    audit = dict(metadata_checks=checks, raw=raw_integrity(graph), raw_sha256=digest(raw),
                 request_source_set=SOURCE, source_set_note='Requested source; raw metadata may not expose its revision.')
    if (not all(checks.values()) or not audit['raw']['raw_node_count'] or not audit['raw']['raw_edge_count']
            or audit['raw']['raw_missing_node_id_count'] or audit['raw']['raw_orphan_edge_count']):
        audit.update(technical_passed=False, reason='metadata_or_raw_integrity_failure')
        atomic_json(raw.with_name('audit.json'), audit)
        return audit
    converted = raw.with_name('converted_graph.json')
    load_converter()(str(raw), str(converted), prompt=None, model_id=MODEL, ambiguous_node_policy='drop')
    data = json.loads(converted.read_bytes())
    converted_audit = converted_integrity(data)
    summary, _ = summarize_graph(data, path=converted, file_sha256=digest(converted), raw_schema=False)
    passed = all(summary[k] == 0 for k in ['missing_node_ids', 'ambiguous_node_id_count',
                                          'dangling_edge_count', 'nonfinite_edge_count'])
    audit.update(technical_passed=passed, converted=converted_audit, summary=summary,
                 converted_sha256=digest(converted), observed=summary.get('top_token'),
                 expected=job['expected_token'], factual_answer_matches=(
                     str(summary.get('top_token') or '').strip() == job['expected_token'].strip()
                     if job['expected_token'] else None))
    atomic_json(raw.with_name('audit.json'), audit)
    return audit


def run_job(client, job):
    folder = OUT / 'graphs' / job['job_id']
    raw = folder / 'raw_graph.json'
    if not raw.exists():
        info = post_once(client, job, folder)
        if info is None:
            return json.loads((folder / 'request_state.json').read_text())['status']
        url = info.get('s3url') or info.get('s3Location') or info.get('graphUrl')
        if not isinstance(url, str) or not url.startswith('https://'):
            raise RuntimeError('No HTTPS graph URL; do not repeat the POST')
        response = requests.get(url, timeout=(30, 180))
        response.raise_for_status()
        atomic_json(folder / 'metadata.json', dict(job=job, payload=payload_for(job), received_at=now(),
                    url=url, sha256=hashlib.sha256(response.content).hexdigest(), bytes=len(response.content)))
        temp = raw.with_suffix('.json.tmp')
        temp.write_bytes(response.content)
        replace_with_retry(temp, raw)
    assert digest(raw) == json.loads((folder / 'metadata.json').read_text())['sha256']
    audit = audit_graph(raw, job)
    return 'saved_valid' if audit['technical_passed'] else 'saved_flagged'


def finalize(frozen, status):
    for row in frozen['original_raw']:
        assert digest(ROOT / row['path']) == row['sha256'], 'Original raw graph changed'
    for path, sha in frozen['dependencies'].items():
        assert digest(ROOT / path) == sha, path
    ledger = json.loads(LEDGER.read_text())['events'] if LEDGER.exists() else []
    starts = sorted(ledger, key=lambda e: e['epoch'])
    mine = [e for e in starts if e['job_id'].startswith(PREFIX)]
    counts = Counter(e['job_id'][len(PREFIX):] for e in mine)
    assert set(counts) <= set(EXPECTED) and all(n == 1 for n in counts.values())
    for i, event in enumerate(starts):
        if event['job_id'].startswith(PREFIX):
            assert i == 0 or event['epoch'] - starts[i - 1]['epoch'] >= 124.999
            assert sum(0 <= event['epoch'] - e['epoch'] < 3600 for e in starts[:i + 1]) <= 30
    raw_files = sorted((OUT / 'graphs').glob('*/raw_graph.json'))
    with (OUT / 'checksums.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['path', 'sha256', 'bytes'])
        writer.writeheader()
        for p in raw_files:
            writer.writerow(dict(path=p.relative_to(ROOT).as_posix(), sha256=digest(p), bytes=p.stat().st_size))
    status.update(finished_at=now(), generation_requests=len(mine), original_archive_unchanged=True,
                  raw_graphs_recovered=len(raw_files), shared_rate_checks_passed=True)
    atomic_json(OUT / 'status.json', status)
    files = [dict(path=p.relative_to(OUT).as_posix(), bytes=p.stat().st_size, sha256=digest(p))
             for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'artifact_manifest.json'
             and p.suffix != '.lock' and '__pycache__' not in p.parts]
    atomic_json(OUT / 'artifact_manifest.json', dict(created_at=now(), files=files))
    print(json.dumps(status, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    with file_lock(OUT / 'runner.lock'):
        frozen = prepare()
        if not args.execute:
            log('Prepared exactly two jobs; no network requests made')
            return
        client = Client()
        status = dict(state='running', started_at=now(), pid=os.getpid(), jobs={})
        atomic_json(OUT / 'status.json', status)
        for job in frozen['jobs']:
            # A previous server rate limit also governs the next distinct job.
            for state_file in (OUT / 'graphs').glob('*/request_state.json'):
                until = json.loads(state_file.read_text()).get('retry_not_before', 0)
                while until > time.time():
                    log(f'Server rate-limit wait: {until - time.time():.0f}s')
                    time.sleep(min(30, until - time.time()))
            status.update(current_job=job['job_id'], updated_at=now())
            atomic_json(OUT / 'status.json', status)
            try:
                status['jobs'][job['job_id']] = run_job(client, job)
            except Exception as exc:
                status['jobs'][job['job_id']] = 'error_after_attempt'
                with (OUT / 'stderr.log').open('a', encoding='utf-8') as stream:
                    stream.write(traceback.format_exc() + '\n')
                log(f"{job['job_id']}: {type(exc).__name__}; no additional POST permitted")
            log(f"{job['job_id']}: {status['jobs'][job['job_id']]}")
            atomic_json(OUT / 'status.json', status)
        status['state'] = 'two_attempts_finished'
        finalize(frozen, status)


if __name__ == '__main__':
    main()
