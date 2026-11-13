"""No-network safety tests for the two authorized one-shot recovery requests."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import complete_qwen4_controls as recovery


@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setattr(recovery, 'OUT', tmp_path)
    monkeypatch.setattr(recovery, 'LEDGER', tmp_path / 'ledger.json')
    reservations = []
    monkeypatch.setattr(recovery, 'reserve_post', lambda *args: reservations.append(args))
    client = SimpleNamespace(base='https://test.invalid', headers={}, reconcile=lambda *args: None)
    jobs = [dict(job_id=key, prompt=prompt) for key, prompt in recovery.EXPECTED.items()]
    return client, jobs, reservations


def test_original_payload_is_unchanged_except_operational_slug(setup):
    _, jobs, _ = setup
    for job in jobs:
        payload = recovery.payload_for(job)
        assert payload.pop('slug').startswith(recovery.PREFIX)
        assert payload == dict(prompt=job['prompt'], modelId='qwen3-4b',
                               sourceSetName='transcoder-hp', desiredLogitProb=.99)


@pytest.mark.parametrize('code', [200, 400, 401, 429, 500, 502, 503, 504])
def test_response_never_causes_a_second_post(tmp_path, monkeypatch, setup, code):
    client, jobs, reservations = setup
    calls = []
    def post(*args, **kwargs):
        calls.append(kwargs['json'])
        return SimpleNamespace(status_code=code, headers={}, text='',
                               json=lambda: {'s3url': 'https://test.invalid/graph.json'})
    monkeypatch.setattr(recovery.requests, 'post', post)
    folder = tmp_path / 'job'
    recovery.post_once(client, jobs[0], folder)
    recovery.post_once(client, jobs[0], folder)
    assert len(calls) == len(reservations) == 1
    assert json.loads((folder / 'request_state.json').read_text())['attempts'] == 1


def test_timeout_does_not_trigger_retry(tmp_path, monkeypatch, setup):
    client, jobs, reservations = setup
    calls = []
    def post(*args, **kwargs):
        calls.append(1)
        raise requests.Timeout('test timeout')
    monkeypatch.setattr(recovery.requests, 'post', post)
    recovery.post_once(client, jobs[0], tmp_path / 'job')
    recovery.post_once(client, jobs[0], tmp_path / 'job')
    assert len(calls) == len(reservations) == 1
    assert json.loads((tmp_path / 'job/request_state.json').read_text())['status'] == 'uncertain'


def test_lost_request_state_does_not_allow_another_post(tmp_path, monkeypatch, setup):
    client, jobs, reservations = setup
    recovery.atomic_json(recovery.LEDGER, {'events': [{'job_id': recovery.PREFIX + jobs[0]['job_id']}]})
    monkeypatch.setattr(recovery.requests, 'post', lambda *a, **k: pytest.fail('Unexpected POST'))
    with pytest.raises(RuntimeError, match='reservation already exists'):
        recovery.post_once(client, jobs[0], tmp_path / 'job')
    assert not reservations


def test_only_two_exact_prompts_are_allowed(setup):
    _, jobs, _ = setup
    assert len(jobs) == 2
    with pytest.raises(ValueError):
        recovery.payload_for(dict(jobs[0], prompt=jobs[0]['prompt'] + '.'))
    with pytest.raises(ValueError):
        recovery.payload_for(dict(job_id='new_question', prompt='new prompt'))
