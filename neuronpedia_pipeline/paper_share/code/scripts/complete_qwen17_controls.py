"""Bounded late collection of missing original prompts; never mutate old graphs."""
import argparse
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from control_manifest import load_control_manifest
from control_io import atomic_json, replace_with_retry
from path_manager import PathManager
from run_matched_choice_controls import Client, clean_prompt, file_lock, now, reserve_post

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/model_extension/qwen17_completion_20261106'
MANIFEST = ROOT / 'config/paper_control_manifest.csv'
PROTOCOL = ROOT / 'docs/papers/QWEN17_COMPLETION_ATTEMPT_20261106.md'
MODEL = 'qwen3-1.7b'
SOURCE = 'llamascope-2-transcoder-16k-k64'
MANIFEST_SHA = 'c2c36a46e09a4c7943ff38e537f78cf3e7d4aa27e031b011be3b6035c6106196'
SETTINGS = dict(maxNLogits=10, desiredLogitProb=.99, nodeThreshold=.8,
                edgeThreshold=.85, maxFeatureNodes=5000, qkTopFraction=.5, qkTopk=5)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def original_path(row):
    # Same naming as PathManager, without creating missing original directories.
    pm = PathManager.__new__(PathManager)
    slug = f'qwen3-1-7b_{pm.slugify(row["prompt"])}'
    return ROOT/'data/prompts'/slug/'1_generation'/f'{pm._get_file_prefix(row["prompt"], MODEL)}_raw_graph.json'


def prepare():
    if digest(MANIFEST) != MANIFEST_SHA:
        raise RuntimeError('Frozen prompt manifest changed')
    freeze_path = OUT/'freeze.json'
    dependencies = [Path(__file__), PROTOCOL, ROOT/'scripts/run_matched_choice_controls.py',
                    ROOT/'scripts/control_io.py', ROOT/'scripts/control_manifest.py', ROOT/'scripts/path_manager.py']
    fingerprints = {str(p.relative_to(ROOT)): digest(p) for p in dependencies}
    if freeze_path.exists():
        frozen = json.loads(freeze_path.read_text())
        if frozen['dependencies'] != fingerprints or frozen['settings'] != SETTINGS:
            raise RuntimeError('Frozen code, protocol, or settings changed')
        for item in frozen['existing']:
            if digest(ROOT/item['path']) != item['sha256']:
                raise RuntimeError('An original raw graph changed')
        for job in frozen['missing']:
            if original_path(job).exists():
                raise RuntimeError('A formerly missing original appeared; reconcile before requesting')
        return frozen
    existing, missing = [], []
    for row in load_control_manifest(MANIFEST):
        p = original_path(row)
        job = dict(row, job_id=f'{row["pair_id"]}__{row["role"]}')
        if p.exists():
            existing.append(dict(job=job, path=str(p.relative_to(ROOT)), sha256=digest(p), bytes=p.stat().st_size))
        else:
            missing.append(job)
    if len(existing) != 50 or len(missing) != 70:
        raise RuntimeError(f'Unexpected inventory: existing={len(existing)}, missing={len(missing)}')
    frozen = dict(created_at=now(), model=MODEL, source=SOURCE, settings=SETTINGS,
                  manifest_sha256=MANIFEST_SHA, dependencies=fingerprints, existing=existing, missing=missing)
    OUT.mkdir(parents=True, exist_ok=True)
    snapshot = OUT/'code_snapshot'; snapshot.mkdir(exist_ok=True)
    for p in dependencies + [MANIFEST]:
        shutil.copy2(p, snapshot/str(p.relative_to(ROOT)).replace('\\', '__').replace('/', '__'))
    with (OUT/'jobs.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(missing[0])); writer.writeheader(); writer.writerows(missing)
    atomic_json(freeze_path, frozen)
    return frozen


def payload_for(job):
    return dict(modelId=MODEL, sourceSetName=SOURCE, prompt=job['prompt'],
                slug=f'q17-completion-20261106-{job["job_id"]}'.replace('_', '-'), **SETTINGS)


def post_once(client, job, folder):
    response_path, state_path = folder/'response.json', folder/'request_state.json'
    payload = payload_for(job)
    if response_path.exists():
        return json.loads(response_path.read_text())
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if state.get('payload') != payload:
            raise RuntimeError('Stored request payload mismatch')
        if state['status'] == 'prompt_too_long':
            return None
        if state['status'] in ('submitting', 'uncertain', 'http_error'):
            recovered = client.reconcile(MODEL, payload['slug'])
            if recovered:
                atomic_json(response_path, recovered)
                return recovered
        raise RuntimeError('Previously attempted request: no automatic duplicate POST permitted')
    reserve_post(MODEL, 'q17-completion-20261106-'+job['job_id'], 'generate')
    state = dict(status='submitting', attempts=1, started_at=now(), payload=payload)
    atomic_json(state_path, state)
    try:
        response = requests.post(client.base+'/graph/generate', headers=client.headers,
                                 json=payload, timeout=(30, 360))
    except requests.RequestException as exc:
        atomic_json(state_path, dict(state, status='uncertain', error=type(exc).__name__, updated_at=now()))
        raise RuntimeError('Request outcome uncertain; no automatic retry') from exc
    try:
        body = response.json()
    except ValueError:
        body = {'non_json_response': response.text[:2000]}
    atomic_json(folder/'http_attempt_1.json', dict(status_code=response.status_code, body=body,
                retry_after=response.headers.get('Retry-After'), received_at=now()))
    if response.status_code == 200:
        atomic_json(response_path, body)
        atomic_json(state_path, dict(state, status='received', updated_at=now()))
        return body
    too_long = response.status_code == 400 and isinstance(body, dict) and body.get('error') == 'Prompt Too Long'
    atomic_json(state_path, dict(state, status='prompt_too_long' if too_long else 'http_error',
                status_code=response.status_code, updated_at=now()))
    if too_long:
        return None
    raise RuntimeError(f'Generation HTTP {response.status_code}; stopped, response archived')


def check_graph(graph, job):
    m = graph.get('metadata', {})
    if m.get('scan', m.get('model')) != MODEL or clean_prompt(m.get('prompt', '')) != job['prompt']:
        raise RuntimeError('Model or prompt mismatch')
    details = m.get('feature_details', {})
    if details.get('neuronpedia_source_set') != SOURCE or details.get('neuronpedia_lorsa_source_set') != 'llamascope-2-lorsa-16k-k64':
        raise RuntimeError('Source representation changed; retain raw but do not continue')
    settings = m.get('generation_settings', {})
    for key, value in [('max_n_logits', 10), ('desired_logit_prob', .99), ('max_feature_nodes', 5000),
                       ('qk_top_fraction', .5), ('qk_topk', 5), ('enable_qk_tracing', True)]:
        if settings.get(key) != value:
            raise RuntimeError(f'Returned generation setting differs: {key}')
    pruning = m.get('pruning_settings', {})
    if pruning.get('node_threshold') != .8 or pruning.get('edge_threshold') != .85:
        raise RuntimeError('Returned pruning settings changed')
    if not graph.get('nodes') or not graph.get('links', graph.get('edges')):
        raise RuntimeError('Empty graph')
    return m


def run_job(client, job):
    folder = OUT/'graphs'/job['job_id']; folder.mkdir(parents=True, exist_ok=True)
    raw, meta = folder/'raw_graph.json', folder/'metadata.json'
    if not raw.exists():
        response = post_once(client, job, folder)
        if response is None:
            return 'prompt_too_long'
        url = response.get('s3url') or response.get('s3Location') or response.get('graphUrl')
        if not url or not url.startswith('https://'):
            raise RuntimeError('Response lacks HTTPS graph URL; no further POST')
        downloaded = requests.get(url, timeout=(30, 180)); downloaded.raise_for_status()
        graph = downloaded.json()
        record = dict(job=job, model=MODEL, source=SOURCE, settings=SETTINGS, url=url,
                      received_at=now(), raw_sha256=hashlib.sha256(downloaded.content).hexdigest(),
                      raw_bytes=len(downloaded.content), exported_metadata=graph.get('metadata', {}))
        atomic_json(meta, record)
        temp = raw.with_suffix('.json.tmp'); temp.write_bytes(downloaded.content); replace_with_retry(temp, raw)
    record = json.loads(meta.read_text())
    if record['raw_sha256'] != digest(raw):
        raise RuntimeError('Raw checksum mismatch')
    graph = json.loads(raw.read_bytes())
    check_graph(graph, job)
    atomic_json(folder/'transport_validation.json', dict(passed=True, checked_at=now(),
                note='Model, prompt, source and settings checks only; not scientific eligibility or full graph audit.'))
    return 'saved'


def write_checksums():
    with (OUT/'checksums.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['path', 'sha256', 'bytes']); writer.writeheader()
        for p in sorted((OUT/'graphs').glob('*/raw_graph.json')):
            writer.writerow(dict(path=str(p.relative_to(ROOT)), sha256=digest(p), bytes=p.stat().st_size))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    with file_lock(OUT/'runner.lock'):
        frozen = prepare()
        print(json.dumps(dict(existing=len(frozen['existing']), missing=len(frozen['missing']),
                             missing_by_subject=dict(Counter(j['domain'] for j in frozen['missing'])))), flush=True)
        if not args.execute:
            return
        client = Client()
        state = dict(state='running', started_at=now(), pid=os.getpid(), jobs={})
        status_path = OUT/'status.json'
        if status_path.exists():
            state['jobs'] = json.loads(status_path.read_text()).get('jobs', {})
        atomic_json(status_path, state)
        try:
            for job in frozen['missing'][:args.limit]:
                state.update(current_job=job['job_id'], updated_at=now())
                atomic_json(status_path, state)
                state['jobs'][job['job_id']] = run_job(client, job)
                state['counts'] = dict(Counter(state['jobs'].values()))
                atomic_json(status_path, state)
                write_checksums()
                print(f'{job["job_id"]}: {state["jobs"][job["job_id"]]} {state["counts"]}', flush=True)
            state['state'] = 'attempt_finished' if args.limit is None else 'bounded_attempt_finished'
        except Exception as exc:
            state.update(state='blocked', error=str(exc))
            print(f'BLOCKED: {exc}', flush=True)
        finally:
            write_checksums()
            state['updated_at'] = now()
            atomic_json(status_path, state)
        if state['state'] == 'blocked':
            raise SystemExit(1)


if __name__ == '__main__':
    main()
