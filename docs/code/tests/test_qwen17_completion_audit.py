"""Synthetic-only checks for the late-collection auditor; no real graphs read."""
from collections import Counter
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_qwen17_completion as audit


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding='utf-8')


def save_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class CompletionAuditTests(unittest.TestCase):
    def clean_graph(self, job):
        return dict(nodes=[dict(node_id='feature', feature_type='lorsa', feature=1,
                               layer=1, influence=.1, activation=.5),
                           dict(node_id='logit', feature_type='logit', feature=2,
                                layer=27, token_prob=.8)],
                    links=[dict(source='feature', target='logit', weight=.2)],
                    metadata=dict(scan=audit.MODEL, prompt=job['prompt'],
                        feature_details=dict(neuronpedia_source_set=audit.SOURCE,
                            neuronpedia_lorsa_source_set='llamascope-2-lorsa-16k-k64'),
                        generation_settings=dict(max_n_logits=10, desired_logit_prob=.99,
                            max_feature_nodes=5000, enable_qk_tracing=True,
                            qk_top_fraction=.5, qk_topk=5),
                        pruning_settings=dict(node_threshold=.8, edge_threshold=.85),
                        info=dict(generator=dict(name='synthetic', version='test'))))

    def fixture(self, root):
        out = root/audit.REL_OUT
        rows = [dict(pair_id=f'{domain}_{i}', domain=domain,
                     split='development' if i < 5 else 'held_out', role=role,
                     prompt=f'{domain} fact {i} {role}', expected_token='x')
                for domain in ('chemistry', 'geography', 'history')
                for i in range(10) for role in sorted(audit.ROLES)]
        manifest = root/'config/paper_control_manifest.csv'
        save_csv(manifest, rows)
        manifest_sha = audit.digest(manifest)
        existing, missing = [], []
        for row in rows:
            job = dict(row, job_id=f'{row["pair_id"]}__{row["role"]}')
            if row['domain'] == 'chemistry' or (row['domain'] == 'geography' and row['role'] == 'target'):
                relative = audit.original_relative(job)
                save_json(root/relative, {'synthetic_original': True})
                existing.append(dict(job=job, path=str(relative), sha256=audit.digest(root/relative),
                                     bytes=(root/relative).stat().st_size))
            else:
                missing.append(job)
        dependencies = {}
        for relative in audit.DEPENDENCIES:
            path = root/relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('synthetic frozen dependency', encoding='utf-8')
            dependencies[relative] = audit.digest(path)
            snapshot = out/'code_snapshot'/relative.replace('/', '__')
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(path.read_bytes())
        (out/'code_snapshot/config__paper_control_manifest.csv').write_bytes(manifest.read_bytes())
        frozen = dict(model=audit.MODEL, source=audit.SOURCE, settings=audit.SETTINGS,
                      manifest_sha256=manifest_sha, dependencies=dependencies,
                      existing=existing, missing=missing)
        save_json(out/'freeze.json', frozen)
        save_csv(out/'jobs.csv', missing)
        events = []
        for i, job in enumerate(missing):
            folder = out/'graphs'/job['job_id']
            save_json(folder/'request_state.json', dict(status='prompt_too_long', attempts=1,
                                                       payload=audit.payload_for(job)))
            save_json(folder/'http_attempt_1.json', dict(status_code=400, body={'error': 'Prompt Too Long'}))
            events.append(dict(epoch=10000+i*125, job_id=audit.PREFIX+job['job_id'],
                               kind='generate', model=audit.MODEL, utc=f'synthetic-{i}'))
        save_json(root/'data/model_extension/neuronpedia_request_ledger.json', {'events': events})
        save_json(out/'status.json', dict(state='attempt_finished', counts={'prompt_too_long': 70},
                  jobs={j['job_id']: 'prompt_too_long' for j in missing}))
        save_csv(out/'checksums.csv', [], fields=['path', 'sha256', 'bytes'])
        return out, frozen, manifest_sha

    def test_integrity_flags_collisions_duplicates_orphans_and_nonfinite(self):
        graph = self.clean_graph({'prompt': 'p'})
        self.assertTrue(audit.integrity_audit(graph)['clean_under_reported_checks'])
        graph['nodes'].append(dict(graph['nodes'][0]))
        graph['nodes'].append({'node_id': None, 'influence': float('nan')})
        graph['links'].append(dict(graph['links'][0]))
        graph['links'].append({'source': 'missing', 'target': 'logit', 'weight': float('inf')})
        result = audit.integrity_audit(graph)
        self.assertEqual(result['raw_ambiguous_node_id_count'], 1)
        self.assertEqual(result['null_or_empty_node_ids'], 1)
        self.assertEqual(result['raw_orphan_edge_count'], 1)
        self.assertEqual(result['duplicate_exact_edge_count'], 1)
        self.assertEqual(result['invalid_or_nonfinite_edge_weights'], 1)
        self.assertEqual(result['invalid_or_nonfinite_present_influence_count'], 1)
        self.assertFalse(result['clean_under_reported_checks'])

    def test_nullable_node_fields_reported_without_assuming_corruption(self):
        graph = self.clean_graph({'prompt': 'p'})
        graph['nodes'][1]['activation'] = None
        result = audit.integrity_audit(graph)
        self.assertEqual(result['null_present_activation_count'], 1)
        self.assertTrue(result['clean_under_reported_checks'])

    def test_ledger_counts_other_requests_and_rejects_spacing_and_duplicates(self):
        events = [dict(epoch=1000+i*125, job_id=audit.PREFIX+str(i), model=audit.MODEL, kind='generate')
                  for i in range(40)]
        result = audit.ledger_audit(events, {str(i) for i in range(40)})
        self.assertEqual(result['failures'], [])
        self.assertEqual(result['peak_shared_rolling_hour'], 29)
        events.insert(1, dict(epoch=1001, job_id='unrelated', model='other', kind='generate'))
        events.append(dict(events[-1], epoch=events[-1]['epoch']+125))
        result = audit.ledger_audit(events, {str(i) for i in range(40)})
        self.assertEqual(len(result['interleaved_requests']), 1)
        self.assertTrue(any('spacing' in x for x in result['failures']))
        self.assertTrue(any('Multiple' in x for x in result['failures']))

    def test_ledger_detects_rolling_hour_limit(self):
        events = [dict(epoch=1000+i, job_id=audit.PREFIX+str(i), model=audit.MODEL, kind='generate')
                  for i in range(31)]
        result = audit.ledger_audit(events, {str(i) for i in range(31)})
        self.assertTrue(any('rolling hour' in x for x in result['failures']))

    def test_complete_length_rejections_are_accounted_not_eligible_facts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, frozen, sha = self.fixture(root)
            with patch.object(audit, 'MANIFEST_SHA', sha):
                report = audit.audit_collection(root)
            self.assertTrue(report['technical_verification_passed'], report['failures'])
            self.assertEqual(report['original_graphs_verified_unchanged'], 50)
            self.assertEqual(report['collection_counts'], {'prompt_too_long': 70})
            complete = Counter(p['domain'] for p in report['four_role_file_availability'] if p['all_four_files_available'])
            self.assertEqual(dict(complete), {'chemistry': 10})
            self.assertEqual(report['by_domain']['history']['planned_missing'], 40)
            before = {str(p.relative_to(root)): audit.digest(p) for p in root.rglob('*') if p.is_file()}
            audit.write_report(report, root)
            for path, saved_sha in before.items():
                self.assertEqual(audit.digest(root/path), saved_sha)
            self.assertTrue((out/'audit/collection_verification.json').exists())
            self.assertTrue(all(str(p.relative_to(out/'audit')) for p in (out/'audit').iterdir()))

    def test_changed_original_dependency_and_false_length_rejection_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, frozen, sha = self.fixture(root)
            (root/frozen['existing'][0]['path']).write_text('changed', encoding='utf-8')
            (root/'scripts/control_io.py').write_text('changed', encoding='utf-8')
            job = frozen['missing'][0]
            save_json(out/'graphs'/job['job_id']/'http_attempt_1.json', dict(status_code=500, body={'error': 'Server busy'}))
            with patch.object(audit, 'MANIFEST_SHA', sha):
                report = audit.audit_collection(root)
            self.assertFalse(report['technical_verification_passed'])
            self.assertTrue(any('Original graph changed' in f for f in report['failures']))
            self.assertTrue(any('dependency' in f for f in report['failures']))
            self.assertTrue(any('explicit archived server rejection' in f for f in report['failures']))

    def test_saved_raw_metadata_and_exporter_are_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, frozen, sha = self.fixture(root)
            job = frozen['missing'][0]
            folder = out/'graphs'/job['job_id']
            graph = self.clean_graph(job)
            save_json(folder/'raw_graph.json', graph)
            raw = folder/'raw_graph.json'
            raw_sha = audit.digest(raw)
            url = 'https://invalid.example/raw.json'
            save_json(folder/'request_state.json', dict(status='received', attempts=1, payload=audit.payload_for(job)))
            save_json(folder/'response.json', {'s3url': url})
            save_json(folder/'http_attempt_1.json', dict(status_code=200, body={'s3url': url}))
            save_json(folder/'metadata.json', dict(job=job, model=audit.MODEL, source=audit.SOURCE,
                settings=audit.SETTINGS, url=url, raw_sha256=raw_sha, raw_bytes=raw.stat().st_size,
                exported_metadata=graph['metadata']))
            save_json(folder/'transport_validation.json', {'passed': True})
            save_csv(out/'checksums.csv', [dict(path=str(raw.relative_to(root)), sha256=raw_sha, bytes=raw.stat().st_size)])
            status = json.loads((out/'status.json').read_text())
            status['jobs'][job['job_id']] = 'saved'
            status['counts'] = {'saved': 1, 'prompt_too_long': 69}
            save_json(out/'status.json', status)
            with patch.object(audit, 'MANIFEST_SHA', sha):
                report = audit.audit_collection(root)
            self.assertTrue(report['technical_verification_passed'], report['failures'])
            self.assertEqual(report['jobs'][0]['exporter'], {'name': 'synthetic', 'version': 'test'})
            self.assertEqual(report['by_domain']['geography']['new_raws_clean_under_reported_checks'], 1)

    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                audit.inside(Path(temp), '../escape')


if __name__ == '__main__':
    unittest.main()
