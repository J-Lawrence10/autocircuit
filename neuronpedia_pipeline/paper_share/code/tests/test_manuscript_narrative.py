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
        'Original controls do not separate facts from shared words and answers',
        'The overlap difference depends on the answer letter',
        'Selected wrong-answer graphs resemble correct responses with the same answer',
        'Equal feature counts preserve positive averages but not every question',
        'The history pilot limits extension beyond the tested geography task',
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
    images = re.findall(r'!\[Figure (S?\d+):', text)
    assert len(images) == 12 and len(set(images)) == 12
    assert 'No data were published or submitted externally' not in text
    assert 'GitHub submission branch' in text
    assert 'Raw Neuronpedia exports, tokenizer/model files, credentials, and downloaded reference PDFs are excluded' in text
    assert 'Sharing copy updated 8 October' not in text
