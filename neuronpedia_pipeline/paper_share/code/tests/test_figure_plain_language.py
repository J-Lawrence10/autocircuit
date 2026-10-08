"""Presentation regression tests; no data collection or inference."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import figure_plain_language as wording


def test_tick_changes_survive_render_without_changing_values():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [.0628, -.0022])
    ax.set_xticks([0, 1], ['Same answer\nlabel', 'Changed answer\nlabel'])
    before = wording.numeric_signature(fig)
    wording.clarify(fig, 'figure5_matched_choice')
    fig.canvas.draw()
    assert [x.get_text() for x in ax.get_xticklabels()] == ['Same A/B\nanswer', 'Changed A/B\nanswer']
    assert wording.numeric_signature(fig) == before
    plt.close(fig)


def test_all_twelve_figures_have_reviewed_headlines_and_captions():
    assert len(wording.TITLES) == len(wording.CAPTIONS) == 12
    assert wording.TITLES.keys() == wording.CAPTIONS.keys()
    assert all(wording.CAPTIONS[stem] for stem in wording.TITLES)


def test_reconstruction_error_label_is_not_model_error_label():
    assert wording.REPLACE['Errors included'] == 'Include graph-\napproximation errors'
    assert 'not wrong model answers' in wording.CAPTIONS['figureS2_robustness']


def test_overlap_difference_definitions_and_illustrations_are_qualified():
    assert 'chemical element' in wording.CAPTIONS['figure1_design_and_coverage']
    assert 'not the test questions plotted in Figure 2' in wording.CAPTIONS['figure1_design_and_coverage']
    assert 'These example numbers are not measured results' in wording.CAPTIONS['figure2_fact_signal']
    assert 'same sentence pattern, not an identical prompt' in wording.CAPTIONS['figure3_fact_and_wording']
    assert 'both fact and wording' in wording.CAPTIONS['figure3_fact_and_wording']


def test_reviewed_labels_do_not_use_extra_as_a_metric():
    import re
    visible = [*wording.TITLES.values(), *wording.CAPTIONS.values(), *wording.REPLACE.values()]
    assert all(not re.search(r'\bextra\b', text, re.IGNORECASE) for text in visible)
    assert 'difference in feature overlap' in wording.CAPTIONS['figure2_fact_signal']
    assert 'minus similarity in that baseline' in wording.CAPTIONS['figure3_fact_and_wording']
