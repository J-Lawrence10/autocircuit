"""Guard the revised narrative's scope and reported values; not scientific validation."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'docs/papers/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md'
if not SOURCE.exists():
    SOURCE = ROOT.parent/'manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md'


def manuscript():
    return SOURCE.read_text(encoding='utf-8')


def test_results_follow_question_controls_answer_errors_checks_scope():
    text = manuscript()
    headings = re.findall(r'^### 3\.\d+ (.+)$', text, re.M)
    assert headings == [
        'Reworded questions about the same fact share more features',
        'Same-fact questions share words and expected answers',
        'Same-fact overlap is higher when the answer letter stays the same',
        'Error graphs show greater overlap with answer-matched controls',
        'Greater feature sharing between same-fact questions',
        'The history pilot yields 15 of 20 correct predictions',
    ]
    assert text.index('## Supporting analyses') > text.index('## 5. Conclusion')


def test_primary_and_exploratory_outcomes_remain_distinct():
    text = manuscript()
    assert 'Their average, the prespecified primary outcome, was 0.0303' in text
    assert 'The exploratory direct paired difference' in text
    for value in ['0.0628', '-0.0022', '0.0265–0.0338', '0.000244141',
                  '0.000732422', '0.0650', '0.0553–0.0746', 'p=0.03125', '0.2827']:
        assert value in text


def test_original_results_and_limitations_are_retained():
    text = manuscript()
    for value in ['0.170', '0.085', '0.162', '0.1983', '0.2649', '0.1851',
                  '0.2361', '-0.0187', '-0.0080', '145/147', '15/20', '20/20',
                  '23.1%', '17.2–31.4%', '4.9–14.6', '8/16']:
        assert value in text
    for phrase in ['not eight independent replications', 'not an equivalence',
                   'not causal ablations', 'no evaluation graphs were requested',
                   'observationally indistinguishable', 'not verification of a complete generated answer']:
        assert phrase in text


def test_current_figures_and_public_availability_are_consistent():
    text = manuscript()
    assert '**Working manuscript — not peer reviewed.**' in text
    images = re.findall(r'!\[Figure (S?\d+):', text)
    assert len(images) == 12 and len(set(images)) == 12
    assert 'No data were published or submitted externally' not in text
    assert 'GitHub submission branch' in text
    assert 'Raw Neuronpedia exports, tokenizer/model files, credentials, and downloaded reference PDFs are excluded' in text
    assert 'Sharing copy updated 8 October' not in text


def test_reader_gets_measurement_and_bridges_before_details():
    text = manuscript()
    assert 'Feature overlap is the number shared by two graphs divided by the number of distinct features across both' in text
    assert 'Repeated occurrences of a feature at different token positions count once' in text
    assert 'The next question is what the association distinguishes' in text
    assert 'The matched-choice study used correct predictions. We next asked' in text
    assert 'Prespecified conditional correspondence test' in text
    assert 'Exploratory block sign-flip test' in text
    assert 'exchangeable conditional on the label and word inventory' in text


def test_supporting_figures_do_not_interrupt_main_results():
    text = manuscript()
    main = text.split('## Supporting analyses')[0]
    assert not re.search(r'!\[Figure S\d+:', main)
    assert '### A4 Comparison and sensitivity figures' in text
    assert '### 4.2 Scope and remaining questions' in text
    assert 'ordinary least-squares intercept with centered predictors equals' in text


def test_figure_captions_match_authoritative_wording():
    import sys
    sys.path.insert(0, str(ROOT/'scripts'))
    import figure_plain_language as wording
    text = manuscript()
    for stem, title in wording.TITLES.items():
        number = re.match(r'figure(S?\d+)', stem).group(1)
        assert f'![Figure {number}: {title}]' in text
        assert f'**Figure {number}. {title}.** {wording.CAPTIONS[stem]}' in text


def test_invented_name_controls_are_defined_and_legacy_terms_are_absent():
    text = manuscript()
    assert 'Invented name controls replace a real entity name with an invented name' in text
    assert not re.search(r'made.up|\bnonce\b|\ba invented\b', text, re.I)
    assert 'Mean differences remained positive at both sampling sizes' in text
