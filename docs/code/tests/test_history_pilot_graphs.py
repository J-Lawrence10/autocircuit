"""Guard the bounded additional collection and inclusion of incorrect predictions."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_history_pilot_graphs as run
import run_matched_choice_controls as transport
import analyze_history_pilot_graphs as analysis
import pytest


def test_exact_sixteen_prompts_include_wrong_previews():
    jobs = run.load_jobs()
    assert len(jobs) == 16
    assert {j['block'] for j in jobs} == set(run.BLOCKS)
    assert all(j['split'] == 'pilot' for j in jobs)
    assert sum(j['expected_label'] == j['preview_answer'] for j in jobs) == 11
    assert sum(j['expected_label'] != j['preview_answer'] for j in jobs) == 5
    assert run.OUT != run.ORIGINAL
    assert all(len(j['preview_tokens']) + 1 <= 64 for j in jobs)


def test_saved_preview_order_comparisons():
    jobs = run.load_jobs()
    cells = {(j['block'], j['fact'], j['mapping'], j['wording']): j for j in jobs}
    flips = 0
    for block in run.BLOCKS:
        for fact in range(2):
            for mapping in range(2):
                a, b = [cells[block, fact, mapping, w] for w in range(2)]
                assert a['expected_label'] == b['expected_label']
                flips += a['preview_answer'] != b['preview_answer']
    assert flips == 3


def test_shared_spacing_and_hourly_quota():
    assert transport.rate_delay([{'epoch': 100}], 101) == 124
    assert transport.rate_delay([{'epoch': i * 100} for i in range(30)], 3000) >= 601
    assert transport.rate_delay([], 100) == 0


def synthetic_graph_records():
    jobs = run.load_jobs()
    audits, reps = {}, {}
    for job in jobs:
        key = job['job_id']
        observed = 'B' if job['expected_label'] == 'A' else 'A'
        audits[key] = dict(observed=observed, correct=False, prediction_changed=True,
                           graph_eligible=True, predicted_year=analysis.selected_year(job, observed, jobs),
                           prompt_tokens=['same', 'tokens'])
        feature_set = {'shared', job['expected_label']}
        reps[key] = {v: dict(features=feature_set, feature_weights={f: 1. for f in feature_set}) for v in analysis.VARIANTS}
    return jobs, audits, reps


def test_wrong_answers_are_retained_in_every_pair_and_contrast():
    jobs, audits, reps = synthetic_graph_records()
    pairs = analysis.pair_rows(jobs, audits, reps)
    assert len(pairs) == 56
    assert all(r['status'] == 'ok' and r['correct_a'] is False and r['correct_b'] is False for r in pairs)
    assert sum(r['order_only'] for r in pairs) == 8
    assert sum(r['mapping_only'] for r in pairs) == 8
    assert sum(r['event_only'] for r in pairs) == 8
    blocks, sampling = analysis.block_analysis(jobs, audits, reps)
    assert len(blocks) == 16
    assert all(r['status'] == 'ok' for r in blocks)
    assert len(sampling) == 800
    sampled = analysis.sampling_summary(sampling)
    assert len(sampled) == 4 and all(r['repetitions'] == 200 for r in sampled)
    assert all(r['fact_effect'] == pytest.approx(0) for r in sampled if r['sample_size_name'] == 'K')
    for r in blocks:
        assert r['fact_effect'] == pytest.approx(0)
        assert r['same_event_difference_change'] == pytest.approx(0)
        if r['metric'] == 'jaccard':
            assert r['SS'] == pytest.approx(1)
            assert r['SD'] == pytest.approx(1 / 3)
            assert r['label_effect'] == pytest.approx(2 / 3)


def test_required_and_predicted_letters_remain_distinct():
    jobs, audits, reps = synthetic_graph_records()
    for row in audits.values():
        row['observed'] = 'A'
    pairs = analysis.pair_rows(jobs, audits, reps)
    assert all(p['same_predicted_letter'] for p in pairs)
    assert any(not p['same_required_letter'] for p in pairs)
    groups = analysis.stratified(pairs)
    assert sum(r['total_pairs'] for r in groups) == 56
    assert any(r['total_pairs'] == 0 and r['jaccard'] is None for r in groups)


def test_invalid_graph_is_accounted_for_not_a_zero_overlap():
    jobs, audits, reps = synthetic_graph_records()
    del reps[jobs[0]['job_id']]
    pairs = analysis.pair_rows(jobs, audits, reps)
    assert len(pairs) == 56
    assert sum(r['status'] != 'ok' for r in pairs) == 7
    assert all(r['jaccard'] is None for r in pairs if r['status'] != 'ok')
    blocks, samples = analysis.block_analysis(jobs, audits, reps)
    assert blocks[0]['status'] == 'incomplete_or_token_mismatch'
    assert len(samples) == 400


def test_decoding_distinguishes_letter_from_selected_year():
    jobs = run.load_jobs()
    for job in jobs:
        assert analysis.selected_year(job, job['expected_label'], jobs) == job['year']
        other = 'B' if job['expected_label'] == 'A' else 'A'
        assert analysis.selected_year(job, other, jobs) != job['year']
        assert analysis.selected_year(job, 'unknown', jobs) is None


def test_raw_prediction_tie_is_not_arbitrarily_broken():
    nodes = [dict(feature_type='logit', token=t, token_prob=.5) for t in ['A', 'B']]
    assert analysis.raw_prediction(dict(nodes=nodes)) == (None, .5)
    nodes[0]['token_prob'] = .75
    assert analysis.raw_prediction(dict(nodes=nodes)) == ('A', .75)
