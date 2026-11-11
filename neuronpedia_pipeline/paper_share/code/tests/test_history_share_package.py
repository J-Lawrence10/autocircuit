"""The portable history figure retains every saved comparison and every error."""
from copy import deepcopy
import csv
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / 'paper_share/code/verify_package.py'
if not VERIFY.exists():
    VERIFY = ROOT / 'verify_package.py'
spec = importlib.util.spec_from_file_location('history_package_verifier', VERIFY)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


@pytest.fixture
def evidence():
    data = ROOT / 'data/model_extension/history_pilot_graphs_20261110'
    if data.exists():
        result = data / 'analysis/results.json'
        examples = data / 'paper_figure_v1/prompt_examples.json'
        source = data / 'paper_figure_v1/figure7_history_answers_source.csv'
        all_pairs = data / 'analysis/all_pairs.csv'
    else:
        result = ROOT.parent / 'provenance/history_results.json'
        examples = ROOT.parent / 'provenance/history_prompt_examples.json'
        source = ROOT.parent / 'tables/figure7_history_answers_source.csv'
        all_pairs = ROOT.parent / 'tables/history_all_pairs.csv'
    def read_csv(path):
        with path.open(encoding='utf-8', newline='') as stream:
            return list(csv.DictReader(stream))
    tables = {'figure7_history_answers_source.csv': read_csv(source),
              'history_all_pairs.csv': read_csv(all_pairs)}
    return tables, json.loads(result.read_text()), json.loads(examples.read_text())


def test_history_source_rows_match_saved_results(evidence):
    tables, result, examples = evidence
    verify.verify_history_figure(tables.__getitem__, result, examples)


@pytest.mark.parametrize('field,value', [('jaccard', '0'), ('same_letter', 'False'),
                                       ('selected_year_a', '1900'), ('correct_a', 'False')])
def test_changed_history_values_are_rejected(evidence, field, value):
    tables, result, examples = deepcopy(evidence)
    row = next(r for r in tables['figure7_history_answers_source.csv']
               if r['panel'] == 'b' and r['a'] == 'pilot_documents__f0m0w0')
    assert row[field] != value
    row[field] = value
    with pytest.raises(AssertionError):
        verify.verify_history_figure(tables.__getitem__, result, examples)


def test_missing_or_duplicated_comparisons_are_rejected(evidence):
    tables, result, examples = deepcopy(evidence)
    tables['figure7_history_answers_source.csv'][0] = tables['figure7_history_answers_source.csv'][1]
    with pytest.raises(AssertionError):
        verify.verify_history_figure(tables.__getitem__, result, examples)


def test_wrong_predictions_cannot_be_omitted(evidence):
    tables, result, examples = deepcopy(evidence)
    result['audits'] = [r for r in result['audits'] if r['correct']]
    with pytest.raises(AssertionError):
        verify.verify_history_figure(tables.__getitem__, result, examples)
