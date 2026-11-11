"""Technical collection verification only; no eligibility, effects, or inference.

Reads the dated Qwen1.7B attempt and original hashes. The only permitted outputs
are derived audit files inside that attempt's audit/ directory.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from complete_qwen17_controls import (  # import does not run collection
    MANIFEST_SHA, MODEL, SOURCE, SETTINGS, check_graph, payload_for,
)
from control_io import atomic_json
from convert_model_extension import raw_integrity
from path_manager import PathManager

ROOT = Path(__file__).resolve().parents[1]
REL_OUT = Path('data/model_extension/qwen17_completion_20261106')
PREFIX = 'q17-completion-20261106-'
ROLES = {'target', 'positive_paraphrase', 'negative_same_template', 'negative_nonce'}
DEPENDENCIES = {
    'scripts/complete_qwen17_controls.py',
    'docs/papers/QWEN17_COMPLETION_ATTEMPT_20261106.md',
    'scripts/run_matched_choice_controls.py', 'scripts/control_io.py',
    'scripts/control_manifest.py', 'scripts/path_manager.py',
}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_bytes())


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def inside(root, relative):
    root = Path(root).resolve()
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f'Path escapes workspace: {relative}')
    return candidate


def original_relative(job):
    pm = PathManager.__new__(PathManager)
    slug = 'qwen3-1-7b_' + pm.slugify(job['prompt'])
    return Path('data/prompts')/slug/'1_generation'/(
        pm._get_file_prefix(job['prompt'], MODEL) + '_raw_graph.json')


def finite(value):
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and math.isfinite(value))


def integrity_audit(graph):
    """Preserve raw defects; never repair, deduplicate, or filter the export."""
    result = raw_integrity(graph)
    nodes = graph.get('nodes', [])
    edges = graph.get('links', graph.get('edges', []))
    result['null_or_empty_node_ids'] = sum(
        node.get('node_id', node.get('id')) in (None, '') for node in nodes)
    result['invalid_or_nonfinite_edge_weights'] = sum(not finite(e.get('weight')) for e in edges)
    exact = [(str(e.get('source')), str(e.get('target')),
              json.dumps(e.get('weight'), sort_keys=True)) for e in edges]
    result['duplicate_exact_edge_count'] = len(exact) - len(set(exact))
    for field in ('activation', 'influence', 'token_prob'):
        result[f'null_present_{field}_count'] = sum(field in n and n[field] is None for n in nodes)
        result[f'invalid_or_nonfinite_present_{field}_count'] = sum(
            field in n and n[field] is not None and not finite(n[field]) for n in nodes)
    defects = [k for k in (
        'raw_missing_node_id_count', 'null_or_empty_node_ids',
        'raw_ambiguous_node_id_count', 'raw_orphan_edge_count',
        'raw_duplicate_endpoint_edge_count', 'duplicate_exact_edge_count',
        'invalid_or_nonfinite_edge_weights',
        'invalid_or_nonfinite_present_activation_count',
        'invalid_or_nonfinite_present_influence_count',
        'invalid_or_nonfinite_present_token_prob_count',
    ) if result[k]]
    result['flagged_fields'] = defects
    result['nullable_field_note'] = 'Present null node fields are counted separately, not presumed invalid without a field-specific schema; null edge weights are invalid.'
    result['clean_under_reported_checks'] = not defects
    return result


def ledger_audit(events, job_ids):
    failures = []
    valid = []
    for event in events:
        if not finite(event.get('epoch')):
            failures.append('Ledger contains invalid epoch')
        else:
            valid.append(event)
    valid.sort(key=lambda e: e['epoch'])
    target = [e for e in valid if str(e.get('job_id', '')).startswith(PREFIX)]
    counts = Counter(e['job_id'][len(PREFIX):] for e in target)
    for job_id, count in counts.items():
        if job_id not in job_ids:
            failures.append(f'Unplanned completion request: {job_id}')
        if count != 1:
            failures.append(f'Multiple request reservations: {job_id} ({count})')
    if any(e.get('model') != MODEL or e.get('kind') != 'generate' for e in target):
        failures.append('Completion ledger model/kind mismatch')
    gaps, peak, interleaved = [], 0, []
    if target:
        start, end = target[0]['epoch'], target[-1]['epoch']
        left = 0
        for i, event in enumerate(valid):
            timestamp = event['epoch']
            while valid[left]['epoch'] <= timestamp - 3600:
                left += 1
            if start <= timestamp <= end:
                peak = max(peak, i-left+1)
                if i:
                    gaps.append(timestamp-valid[i-1]['epoch'])
                if not str(event.get('job_id', '')).startswith(PREFIX):
                    interleaved.append(event)
        if gaps and min(gaps) < 125 - 1e-6:
            failures.append('Shared ledger start spacing below 125 seconds')
        if peak > 30:
            failures.append('Shared ledger exceeds 30 requests per rolling hour')
    return dict(reservations=len(target), per_job=dict(counts),
                minimum_shared_start_gap_seconds=min(gaps) if gaps else None,
                peak_shared_rolling_hour=peak, interleaved_requests=interleaved,
                first_start_utc=target[0].get('utc') if target else None,
                last_start_utc=target[-1].get('utc') if target else None,
                note='Ledger reservations conservatively count attempted POSTs; not server execution counts.',
                failures=failures)


def audit_job(root, job, claimed_status, reservations, checksums):
    folder = inside(root, REL_OUT/'graphs'/job['job_id'])
    record = dict(job_id=job['job_id'], pair_id=job['pair_id'], domain=job['domain'],
                  role=job['role'], split=job['split'], prompt=job['prompt'],
                  claimed_status=claimed_status, raw_present=False, failures=[])
    errors = record['failures']
    state_path, raw_path = folder/'request_state.json', folder/'raw_graph.json'
    try:
        state = read_json(state_path) if state_path.exists() else {}
        if state:
            if state.get('payload') != payload_for(job) or state.get('attempts') != 1:
                errors.append('Request payload or bounded attempt count mismatch')
            if reservations != 1:
                errors.append('Attempted job does not have exactly one ledger reservation')
        elif reservations:
            errors.append('Ledger reservation without request state')
        record['request_status'] = state.get('status', 'not_attempted')
        archive_path = folder/'http_attempt_1.json'
        archive = read_json(archive_path) if archive_path.exists() else {}
        record['http_status_code'] = archive.get('status_code')
        if len(list(folder.glob('http_attempt_*.json'))) > 1:
            errors.append('More than one archived HTTP attempt')
        if raw_path.exists():
            record['raw_present'] = True
            raw_sha = digest(raw_path)
            graph = read_json(raw_path)
            metadata = read_json(folder/'metadata.json')
            response = read_json(folder/'response.json')
            validation = read_json(folder/'transport_validation.json')
            raw_relative = str(raw_path.relative_to(Path(root).resolve())).replace('\\', '/')
            row = checksums.get(raw_relative)
            if not row or row['sha256'] != raw_sha or int(row['bytes']) != raw_path.stat().st_size:
                errors.append('Checksum table mismatch or missing row')
            if metadata.get('raw_sha256') != raw_sha or metadata.get('raw_bytes') != raw_path.stat().st_size:
                errors.append('Raw metadata checksum/size mismatch')
            if metadata.get('job') != job or metadata.get('model') != MODEL or metadata.get('source') != SOURCE or metadata.get('settings') != SETTINGS:
                errors.append('Saved metadata job/model/source/settings mismatch')
            if metadata.get('exported_metadata') != graph.get('metadata', {}):
                errors.append('Saved exported metadata differs from raw graph')
            response_url = response.get('s3url') or response.get('s3Location') or response.get('graphUrl')
            if not response_url or response_url != metadata.get('url'):
                errors.append('Saved response/raw URL mismatch')
            reconciled = bool(response.get('reconciled_metadata'))
            if not reconciled and (archive.get('status_code') != 200 or archive.get('body') != response):
                errors.append('Saved graph lacks matching successful HTTP archive or reconciliation metadata')
            if validation.get('passed') is not True:
                errors.append('Missing positive transport validation')
            if not state or state.get('status') == 'prompt_too_long':
                errors.append('Saved graph has inconsistent request state')
            check_graph(graph, job)
            integrity = integrity_audit(graph)
            record.update(collection_status='saved', raw_sha256=raw_sha,
                          raw_bytes=raw_path.stat().st_size, integrity=integrity,
                          exporter=graph.get('metadata', {}).get('info', {}).get('generator', {}),
                          source_metadata=graph.get('metadata', {}).get('feature_details', {}),
                          generation_metadata=graph.get('metadata', {}).get('generation_settings', {}),
                          pruning_metadata=graph.get('metadata', {}).get('pruning_settings', {}))
            if not integrity['clean_under_reported_checks']:
                errors.append('Raw integrity flags: '+', '.join(integrity['flagged_fields']))
        elif state.get('status') == 'prompt_too_long':
            body = archive.get('body')
            if archive.get('status_code') != 400 or not isinstance(body, dict) or body.get('error') != 'Prompt Too Long':
                errors.append('Length exclusion lacks explicit archived server rejection')
            if (folder/'response.json').exists() or (folder/'metadata.json').exists():
                errors.append('Length exclusion unexpectedly has response/raw metadata')
            record['collection_status'] = 'prompt_too_long'
        else:
            record['collection_status'] = state.get('status', 'not_attempted')
            errors.append('Job has no terminal saved graph or explicit length rejection')
        if claimed_status != record['collection_status']:
            errors.append('Aggregate status disagrees with job artifacts')
    except Exception as exc:
        record.setdefault('collection_status', 'audit_error')
        errors.append(f'{type(exc).__name__}: {exc}')
    record['technical_checks_pass'] = not errors
    return record


def audit_collection(root=ROOT):
    root = Path(root).resolve()
    out = inside(root, REL_OUT)
    report = dict(schema_version='qwen17-completion-technical-audit-v1',
                  created_at=datetime.now(timezone.utc).isoformat(),
                  scope='Technical collection verification only; no correctness, scientific eligibility, effects or significance tests.',
                  metadata_limit='Exporter/source/version matching does not prove unchanged hosted weights.',
                  failures=[], original=[], jobs=[])
    errors = report['failures']
    try:
        frozen, status = read_json(out/'freeze.json'), read_json(out/'status.json')
        report['runner_state'] = status.get('state')
        manifest = read_csv(root/'config/paper_control_manifest.csv')
        if digest(root/'config/paper_control_manifest.csv') != MANIFEST_SHA or frozen.get('manifest_sha256') != MANIFEST_SHA:
            errors.append('Frozen prompt manifest hash mismatch')
        if frozen.get('model') != MODEL or frozen.get('source') != SOURCE or frozen.get('settings') != SETTINGS:
            errors.append('Frozen model/source/settings mismatch')
        dependencies = {k.replace('\\', '/'): v for k, v in frozen['dependencies'].items()}
        if set(dependencies) != DEPENDENCIES:
            errors.append('Unexpected frozen dependency inventory')
        report['dependency_checks'] = {}
        for relative, expected in dependencies.items():
            actual = digest(inside(root, relative))
            snapshot = out/'code_snapshot'/relative.replace('/', '__')
            ok = actual == expected and snapshot.exists() and digest(snapshot) == expected
            report['dependency_checks'][relative] = dict(expected=expected, actual=actual, passed=ok)
            if not ok:
                errors.append(f'Frozen dependency/snapshot changed: {relative}')
        snapshot_manifest = out/'code_snapshot/config__paper_control_manifest.csv'
        if not snapshot_manifest.exists() or digest(snapshot_manifest) != MANIFEST_SHA:
            errors.append('Snapshot prompt manifest hash mismatch')
        existing, missing = frozen['existing'], frozen['missing']
        if len(existing) != 50 or len(missing) != 70:
            errors.append('Frozen inventory is not 50 original and 70 missing')
        if read_csv(out/'jobs.csv') != missing:
            errors.append('Dated jobs.csv differs from frozen missing rows')
        manifest_jobs = {f'{j["pair_id"]}__{j["role"]}': dict(j, job_id=f'{j["pair_id"]}__{j["role"]}') for j in manifest}
        frozen_jobs = [e['job'] for e in existing] + missing
        if len(manifest_jobs) != 120 or len({j['job_id'] for j in frozen_jobs}) != 120 or {j['job_id']: j for j in frozen_jobs} != manifest_jobs:
            errors.append('Frozen original/missing partition differs from fixed 120 prompts')
        available = set()
        for item in existing:
            expected_path = original_relative(item['job'])
            path = inside(root, item['path'])
            ok = (path == inside(root, expected_path) and digest(path) == item['sha256']
                  and path.stat().st_size == item['bytes'])
            report['original'].append(dict(job_id=item['job']['job_id'], unchanged=ok))
            if ok:
                available.add(item['job']['job_id'])
            else:
                errors.append(f'Original graph changed: {item["job"]["job_id"]}')
        for job in missing:
            if inside(root, original_relative(job)).exists():
                errors.append(f'Formerly missing original appeared: {job["job_id"]}')
        expected_ids = {j['job_id'] for j in missing}
        folder_ids = {p.name for p in (out/'graphs').iterdir() if p.is_dir()} if (out/'graphs').exists() else set()
        if folder_ids - expected_ids:
            errors.append('Unplanned job folders: '+', '.join(sorted(folder_ids-expected_ids)))
        ledger = ledger_audit(read_json(root/'data/model_extension/neuronpedia_request_ledger.json')['events'], expected_ids)
        report['request_ledger'] = ledger
        errors.extend(ledger['failures'])
        checksum_rows = read_csv(out/'checksums.csv')
        checksums = {r['path'].replace('\\', '/'): r for r in checksum_rows}
        if len(checksums) != len(checksum_rows):
            errors.append('Duplicate checksum-table paths')
        actual_raw_paths = {str(p.relative_to(root)).replace('\\', '/') for p in (out/'graphs').glob('*/raw_graph.json')}
        if set(checksums) != actual_raw_paths:
            errors.append('Checksum table does not exactly cover saved raw files')
        status_jobs = status.get('jobs', {})
        if set(status_jobs) != expected_ids:
            errors.append('Aggregate status does not account for all 70 missing jobs')
        for job in missing:
            row = audit_job(root, job, status_jobs.get(job['job_id']), ledger['per_job'].get(job['job_id'], 0), checksums)
            report['jobs'].append(row)
            if row['raw_present']:
                available.add(job['job_id'])
            if row['failures']:
                errors.append(f'{job["job_id"]}: '+ '; '.join(row['failures']))
        counts = dict(Counter(j['collection_status'] for j in report['jobs']))
        report['collection_counts'] = counts
        if counts != status.get('counts', {}):
            errors.append('Aggregate status counts disagree with audited artifacts')
        if status.get('state') != 'attempt_finished':
            errors.append('Runner has not declared the complete bounded attempt finished')
        report['by_domain'] = {}
        for domain in sorted({j['domain'] for j in manifest}):
            new = [j for j in report['jobs'] if j['domain'] == domain]
            report['by_domain'][domain] = dict(original_graphs=sum(e['job']['domain'] == domain for e in existing),
                planned_missing=len(new), new_collection_statuses=dict(Counter(j['collection_status'] for j in new)),
                new_raw_files=sum(j['raw_present'] for j in new),
                new_raws_clean_under_reported_checks=sum(j.get('integrity', {}).get('clean_under_reported_checks', False) for j in new))
        pairs = defaultdict(list)
        for job in manifest_jobs.values():
            pairs[job['pair_id']].append(job)
        report['four_role_file_availability'] = []
        for pair_id, rows in sorted(pairs.items()):
            present = {r['role'] for r in rows if r['job_id'] in available}
            report['four_role_file_availability'].append(dict(pair_id=pair_id, domain=rows[0]['domain'],
                split=rows[0]['split'], available_roles=sorted(present), missing_roles=sorted(ROLES-present),
                all_four_files_available=present == ROLES))
        report['availability_note'] = 'File availability only, not integrity acceptance, correctness, or scientific eligibility; original files must match frozen hashes.'
        report['exporter_counts'] = dict(Counter(
            json.dumps(j.get('exporter', {}), sort_keys=True) for j in report['jobs'] if 'exporter' in j))
        report['original_graphs_verified_unchanged'] = sum(r['unchanged'] for r in report['original'])
    except Exception as exc:
        errors.append(f'Audit setup failed: {type(exc).__name__}: {exc}')
    report['technical_verification_passed'] = not errors
    report['auditor_sha256'] = digest(Path(__file__))
    report['audit_dependency_sha256'] = {
        name: digest(Path(__file__).parent/name)
        for name in ('complete_qwen17_controls.py', 'convert_model_extension.py',
                     'control_io.py', 'path_manager.py')
    }
    return report


def write_report(report, root=ROOT):
    attempt = inside(Path(root).resolve(), REL_OUT)
    destination = inside(attempt, 'audit')
    destination.mkdir(parents=True, exist_ok=True)
    atomic_json(destination/'collection_verification.json', report)
    rows = report.get('jobs', [])
    if rows:
        fields = sorted({key for row in rows for key in row})
        with (destination/'collection_verification_jobs.csv').open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v
                              for k, v in row.items()} for row in rows)
    return destination/'collection_verification.json'


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = audit_collection()
    path = write_report(report)
    print(json.dumps(dict(technical_verification_passed=report['technical_verification_passed'],
        counts=report.get('collection_counts', {}), original_hashes_verified=report.get('original_graphs_verified_unchanged', 0),
        failure_count=len(report['failures']), report=str(path)), indent=2))
    if not report['technical_verification_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
