"""Offline transport-safety tests; all network and quota operations are mocked."""
from contextlib import nullcontext
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests

from scripts import complete_qwen17_controls as runner


class Qwen17CompletionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.job = dict(job_id='france_capital__positive_paraphrase',
                        prompt='France has its capital in', domain='geography',
                        pair_id='france_capital', role='positive_paraphrase')
        self.client = SimpleNamespace(base='https://invalid.example/api', headers={},
                                      reconcile=Mock(return_value=None))
        self.post = self.enterContext(patch.object(runner.requests, 'post'))
        self.get = self.enterContext(patch.object(runner.requests, 'get'))
        self.reserve = self.enterContext(patch.object(runner, 'reserve_post'))

    def response(self, status, body):
        return SimpleNamespace(status_code=status, headers={}, text=json.dumps(body),
                               json=lambda: body)

    def save_state(self, status, **kwargs):
        runner.atomic_json(self.folder/'request_state.json',
                           dict(status=status, attempts=1,
                                payload=runner.payload_for(self.job), **kwargs))

    def graph(self):
        return dict(nodes=[{'id': 'feature'}], links=[{'source': 'feature', 'target': 'logit'}],
                    metadata=dict(scan=runner.MODEL, prompt=self.job['prompt'],
                        feature_details=dict(neuronpedia_source_set=runner.SOURCE,
                            neuronpedia_lorsa_source_set='llamascope-2-lorsa-16k-k64'),
                        generation_settings=dict(max_n_logits=10, desired_logit_prob=.99,
                            max_feature_nodes=5000, enable_qk_tracing=True,
                            qk_top_fraction=.5, qk_topk=5),
                        pruning_settings=dict(node_threshold=.8, edge_threshold=.85)))

    def test_payload_preserves_prompt_model_settings_and_fixed_slug(self):
        payload = runner.payload_for(self.job)
        self.assertEqual(payload['prompt'], self.job['prompt'])
        self.assertEqual(payload['modelId'], 'qwen3-1.7b')
        self.assertEqual(payload['sourceSetName'], 'llamascope-2-transcoder-16k-k64')
        self.assertEqual(payload['desiredLogitProb'], .99)
        self.assertEqual(payload['slug'], runner.payload_for(copy.deepcopy(self.job))['slug'])
        self.assertTrue(payload['slug'].startswith('q17-completion-20261106-'))

    def test_success_is_saved_and_resume_does_not_post_again(self):
        body = {'s3url': 'https://invalid.example/saved.json'}
        self.post.return_value = self.response(200, body)
        self.assertEqual(runner.post_once(self.client, self.job, self.folder), body)
        self.assertEqual(runner.post_once(self.client, self.job, self.folder), body)
        self.post.assert_called_once()
        self.reserve.assert_called_once()
        state = json.loads((self.folder/'request_state.json').read_text())
        self.assertEqual(state['attempts'], 1)
        self.assertEqual(state['status'], 'received')

    def test_only_explicit_length_rejection_can_be_skipped(self):
        self.post.return_value = self.response(400, {'error': 'Prompt Too Long'})
        self.assertIsNone(runner.post_once(self.client, self.job, self.folder))
        self.assertIsNone(runner.post_once(self.client, self.job, self.folder))
        self.post.assert_called_once()
        self.assertEqual(json.loads((self.folder/'request_state.json').read_text())['status'],
                         'prompt_too_long')

    def test_generic_400_is_not_a_length_exclusion(self):
        self.post.return_value = self.response(400, {'error': 'Invalid source'})
        with self.assertRaisesRegex(RuntimeError, 'Generation HTTP 400'):
            runner.post_once(self.client, self.job, self.folder)
        self.assertEqual(json.loads((self.folder/'request_state.json').read_text())['status'],
                         'http_error')
        self.post.assert_called_once()

    def test_http_500_stops_without_retry(self):
        self.post.return_value = self.response(500, {'error': 'Server busy'})
        with self.assertRaisesRegex(RuntimeError, 'Generation HTTP 500'):
            runner.post_once(self.client, self.job, self.folder)
        with self.assertRaisesRegex(RuntimeError, 'no automatic duplicate POST'):
            runner.post_once(self.client, self.job, self.folder)
        self.post.assert_called_once()
        self.reserve.assert_called_once()
        self.client.reconcile.assert_called_once()

    def test_timeout_is_persisted_and_resume_never_reposts(self):
        self.post.side_effect = requests.Timeout('simulated timeout')
        with self.assertRaisesRegex(RuntimeError, 'outcome uncertain'):
            runner.post_once(self.client, self.job, self.folder)
        self.assertEqual(json.loads((self.folder/'request_state.json').read_text())['status'],
                         'uncertain')
        with self.assertRaisesRegex(RuntimeError, 'no automatic duplicate POST'):
            runner.post_once(self.client, self.job, self.folder)
        self.post.assert_called_once()

    def test_saved_submitting_request_can_reconcile_without_post(self):
        self.save_state('submitting')
        recovered = {'s3url': 'https://invalid.example/reconciled.json'}
        self.client.reconcile.return_value = recovered
        self.assertEqual(runner.post_once(self.client, self.job, self.folder), recovered)
        self.post.assert_not_called()
        self.reserve.assert_not_called()
        self.assertTrue((self.folder/'response.json').exists())

    def test_changed_payload_on_resume_is_rejected(self):
        self.save_state('uncertain')
        changed = dict(self.job, prompt=self.job['prompt']+'!')
        with self.assertRaisesRegex(RuntimeError, 'payload mismatch'):
            runner.post_once(self.client, changed, self.folder)
        self.post.assert_not_called()
        self.client.reconcile.assert_not_called()

    def test_graph_checks_model_prompt_sources_and_settings(self):
        runner.check_graph(self.graph(), self.job)
        for key, wrong_value in [('scan', 'qwen3-4b'), ('prompt', 'A different prompt')]:
            graph = self.graph()
            graph['metadata'][key] = wrong_value
            with self.assertRaises(RuntimeError):
                runner.check_graph(graph, self.job)
        graph = self.graph()
        graph['metadata']['feature_details']['neuronpedia_lorsa_source_set'] = 'changed'
        with self.assertRaisesRegex(RuntimeError, 'Source representation changed'):
            runner.check_graph(graph, self.job)
        graph = self.graph()
        graph['metadata']['generation_settings']['desired_logit_prob'] = .95
        with self.assertRaisesRegex(RuntimeError, 'desired_logit_prob'):
            runner.check_graph(graph, self.job)

    def test_qk_tracing_must_remain_enabled(self):
        for value in [False, None]:
            graph = self.graph()
            if value is None:
                del graph['metadata']['generation_settings']['enable_qk_tracing']
            else:
                graph['metadata']['generation_settings']['enable_qk_tracing'] = value
            with self.assertRaises(RuntimeError):
                runner.check_graph(graph, self.job)

    def test_existing_response_retries_download_not_generation(self):
        with patch.object(runner, 'OUT', self.folder):
            folder = self.folder/'graphs'/self.job['job_id']
            runner.atomic_json(folder/'response.json', {'s3url': 'https://invalid.example/saved.json'})
            graph = self.graph()
            content = json.dumps(graph).encode('utf-8')
            self.get.return_value = SimpleNamespace(content=content, json=lambda: graph,
                                                    raise_for_status=lambda: None)
            self.assertEqual(runner.run_job(self.client, self.job), 'saved')
            self.assertEqual(runner.run_job(self.client, self.job), 'saved')
            self.get.assert_called_once()
            self.post.assert_not_called()
            self.reserve.assert_not_called()

    def test_main_stops_before_next_job_on_nonlength_failure(self):
        jobs = [self.job, dict(self.job, job_id='second')]
        with patch.object(runner, 'OUT', self.folder), \
             patch.object(runner, 'file_lock', return_value=nullcontext()), \
             patch.object(runner, 'prepare', return_value={'existing': [], 'missing': jobs}), \
             patch.object(runner, 'Client', return_value=self.client), \
             patch.object(runner, 'write_checksums'), \
             patch.object(runner, 'run_job', side_effect=RuntimeError('simulated service failure')) as run, \
             patch('sys.argv', ['complete_qwen17_controls.py', '--execute']):
            with self.assertRaises(SystemExit):
                runner.main()
            run.assert_called_once_with(self.client, self.job)
            self.assertEqual(json.loads((self.folder/'status.json').read_text())['state'], 'blocked')


if __name__ == '__main__':
    unittest.main()
