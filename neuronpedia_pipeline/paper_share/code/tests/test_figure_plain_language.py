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


def test_all_fourteen_figures_have_reviewed_headlines_and_captions():
    assert len(wording.TITLES) == len(wording.CAPTIONS) == 14
    assert wording.TITLES.keys() == wording.CAPTIONS.keys()
    assert all(wording.CAPTIONS[stem] for stem in wording.TITLES)
    assert list(wording.TITLES)[-1] == 'figureS8_feature_overlap_workflow'


def test_reconstruction_error_label_is_not_model_error_label():
    assert wording.REPLACE['Errors included'] == 'Include graph-\napproximation errors'
    assert 'not wrong model answers' in wording.CAPTIONS['figureS2_robustness']


def test_overlap_difference_definitions_and_illustrations_are_qualified():
    assert 'chemical element' in wording.CAPTIONS['figure1_design_and_coverage']
    assert 'not the test questions plotted in Figure 2' in wording.CAPTIONS['figure1_design_and_coverage']
    assert 'These example numbers are not measured results' in wording.CAPTIONS['figure2_fact_signal']
    assert 'Shared version labels did not imply identical sentence patterns across facts' in wording.CAPTIONS['figure3_fact_and_wording']
    assert 'both fact and version label' in wording.CAPTIONS['figure3_fact_and_wording']
    assert 'this is not an exact-wording control' in wording.CAPTIONS['figure3_fact_and_wording']


def test_reviewed_labels_do_not_use_extra_as_a_metric():
    import re
    visible = [*wording.TITLES.values(), *wording.CAPTIONS.values(), *wording.REPLACE.values()]
    assert all(not re.search(r'\bextra\b', text, re.IGNORECASE) for text in visible)
    assert 'difference in feature overlap' in wording.CAPTIONS['figure2_fact_signal']
    assert 'minus similarity in that baseline' in wording.CAPTIONS['figure3_fact_and_wording']


def test_crossed_labels_use_version_groups_and_exact_saved_prompts():
    import ast
    source = Path(__file__).resolve().parents[1] / 'scripts/stage_2_format_variation_experiment.py'
    # The small experiment module may be absent from the portable package.
    if source.exists():
        tree = ast.parse(source.read_text(encoding='utf-8-sig'))
        prompts = next(ast.literal_eval(node.value) for node in tree.body
                       if isinstance(node, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == 'VARIED_PROMPTS' for t in node.targets))
        chemistry = prompts['chemistry']
    else:
        chemistry = {'gold': {'original': 'The chemical symbol for gold is',
                              'alt1': 'Gold is represented by the chemical symbol'},
                     'iron': {'original': 'The chemical symbol for iron is',
                              'alt1': 'Iron is denoted by the symbol'}}
    fig, axes = plt.subplots(1, 2)
    for ax in axes:
        ax.plot([0, 1, 3, 4], [.074, .118, .101, .064])
    before = wording.numeric_signature(fig)
    wording.clarify(fig, 'figure3_fact_and_wording')
    fig.canvas.draw()
    visible = '\n'.join(t.get_text() for t in fig.texts)
    for fact in ['gold', 'iron']:
        for version in ['original', 'alt1']:
            assert chemistry[fact][version] in visible
    assert 'A shared label does not mean identical sentence patterns' in visible
    assert all('same wording' not in label.get_text() for ax in axes for label in ax.get_xticklabels())
    assert wording.numeric_signature(fig) == before
    plt.close(fig)


def test_invented_name_control_is_used_in_current_visible_wording():
    import re
    visible = [*wording.TITLES.values(), *wording.CAPTIONS.values(), *wording.REPLACE.values()]
    assert all(not re.search(r'made.up|\bnonce\b|\ba invented\b', text, re.IGNORECASE) for text in visible)
    assert 'Invented name controls' in wording.TITLES['figure4_control_comparisons']
    assert wording.REPLACE['a  Made-up name, original wording'] == 'a  Invented name control, original wording'


def test_qwen17_completion_distinguishes_collection_from_evaluation():
    caption = wording.CAPTIONS['figureS7_qwen17_completion']
    for phrase in ['91 graphs total', '40/40', '11/40',
                   '29 unavailable history jobs', 'not counted as wrong model answers',
                   'five chemistry and five geography', 'History has no plotted estimate']:
        assert phrase in caption
    assert chr(0x2014) not in caption


def test_current_figures_use_one_cohort_per_model_and_explicit_units():
    signal = wording.CAPTIONS['figure2_fact_signal']
    assert '0.089 for Qwen3-1.7B (10)' in signal
    assert 'C,' not in signal and 'expanded' not in signal.lower()
    assert 'n=9' in wording.CAPTIONS['figure4_control_comparisons']
    assert '0/91' in wording.CAPTIONS['figureS1_export_and_error']
    assert 'not every graph metric' in wording.CAPTIONS['figureS2_robustness']
    assert 'edge-flow cosine result is inconclusive' in wording.CAPTIONS['figureS2_robustness']
    assert '0/10 for Qwen3-1.7B' in wording.CAPTIONS['figureS4_lexical_support']
    answer = wording.CAPTIONS['figureS5_answer_audit']
    assert '50 available factual-question graphs' in answer
    assert 'not the included evaluation counts in Figure 2' in answer
    assert 'Qwen3-4B has 49, five, and five' in answer
    assert not any('expanded' in s.lower() for s in wording.CAPTIONS.values())
    assert all(chr(0x2014) not in s for s in [*wording.TITLES.values(), *wording.CAPTIONS.values()])


def test_saved_summary_validation_rejects_changed_values():
    import pytest
    from plot_updated_cohort_figures import validate_stats
    stats = dict(n=2, mean=.2, ci95=[.1,.3], positive_n=2)
    validate_stats(stats, [.1,.3])
    with pytest.raises(AssertionError):
        validate_stats(stats, [.1,.4])
    with pytest.raises(AssertionError):
        validate_stats(stats, [.2])


def test_current_model_list_does_not_duplicate_qwen():
    from plot_updated_cohort_figures import MODELS, LABELS
    assert len(MODELS)==len(LABELS)==3
    assert len(set(MODELS))==3
    assert MODELS.count('qwen3-1.7b')==1


def test_footer_padding_preserves_panel_size_and_data():
    import numpy as np
    from plot_updated_cohort_figures import add_bottom_padding
    fig, ax = plt.subplots(figsize=(8,5.4))
    ax.plot([0,1],[.085,.162])
    footer=fig.text(.055,.018,'No matched comparison is available.',fontsize=8.5)
    before=wording.numeric_signature(fig)
    panel_height=ax.get_position().height*fig.get_size_inches()[1]
    add_bottom_padding(fig,.30)
    fig.canvas.draw()
    assert np.isclose(fig.get_size_inches()[1],5.7)
    assert np.isclose(ax.get_position().height*fig.get_size_inches()[1],panel_height)
    assert wording.numeric_signature(fig)==before
    assert footer.get_window_extent(fig.canvas.get_renderer()).y0 > .30*fig.dpi
    plt.close(fig)
