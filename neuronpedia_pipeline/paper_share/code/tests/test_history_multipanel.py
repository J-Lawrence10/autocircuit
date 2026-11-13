"""Numerical and wording checks for the history multi-panel figure."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_history_multipanel as figure


def test_exact_prompt_text_is_preserved():
    _, examples, _ = figure.load_data()
    for example in examples:
        for job in example['jobs']:
            parts = figure.prompt_parts(job['plain_prompt'])
            assert ' '.join('\n'.join(parts).split()) == job['plain_prompt']


def test_real_examples_keep_order_and_outcomes_explicit():
    _, examples, _ = figure.load_data()
    assert examples[0]['wording'] == 0
    assert examples[1]['wording'] == 1
    assert examples[0]['pair']['jaccard'] == pytest.approx(.7945804195804196)
    assert examples[1]['pair']['jaccard'] == pytest.approx(.5117335352006056)
    assert [a['observed'] for a in examples[0]['audits']] == ['A', 'A']
    assert [a['predicted_year'] for a in examples[0]['audits']] == [1776, 1783]
    assert [a['observed'] for a in examples[1]['audits']] == ['A', 'B']
    assert [a['predicted_year'] for a in examples[1]['audits']] == [1776, 1776]


def test_all_eight_comparisons_per_panel_are_included():
    _, _, panels = figure.load_data()
    for panel, rows in panels.items():
        assert len(rows) == 8
        assert len({(r['a'], r['b']) for r in rows}) == 8
        assert sum(r['same_letter'] for r in rows) == 5
        assert len({i for r in rows for i in (r['a'], r['b'])}) == 16
        assert set(r['event'] for r in rows) == set(figure.EVENTS)
    for row in panels['b']:
        assert row['ordering_a'] == row['ordering_b']
        assert row['mapping_a'] != row['mapping_b']
        assert (row['correct_a'] and row['correct_b']) is not row['same_letter']
    for row in panels['c']:
        assert row['mapping_a'] == row['mapping_b']
        assert row['ordering_a'] != row['ordering_b']


def test_caption_defines_units_and_graph_reuse():
    caption = figure.caption()
    assert figure.STEM == 'figure7_history_answers'
    assert figure.TITLE.startswith('History: ')
    assert caption == f'**{figure.TITLE}.** {figure.caption_body()}'
    assert 'Panels b and c reuse the same 16 graphs' in caption
    assert '0 means none are shared' in caption
    assert '0.795–0.911' in caption and '0.512–0.532' in caption
    assert '0.766–0.808' in caption and '0.527–0.602' in caption
    assert '\u2014' not in caption
