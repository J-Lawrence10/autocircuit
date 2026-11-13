"""Reject stale pre-correction numbers in final displays; use saved data only."""
from copy import deepcopy
import csv
import importlib.util
import json
from pathlib import Path
import pytest

BASE=Path(__file__).resolve().parents[1]
SCRIPT=BASE/'paper_share/code/verify_package.py'
if not SCRIPT.exists():
    SCRIPT=BASE/'verify_package.py'
spec=importlib.util.spec_from_file_location('final_verifier',SCRIPT)
verify=importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
DATA=BASE/'data/model_extension/final_corrected_scoring_20261111'
if DATA.exists():
    TABLES=DATA/'paper_figures/tables'
    FINAL=DATA/'results.json'
    SPELLING=BASE/'data/model_extension/answer_spelling_20261111/results.json'
else:
    TABLES=BASE.parent/'tables'
    FINAL=BASE.parent/'provenance/final_scoring_results.json'
    SPELLING=BASE.parent/'provenance/answer_spelling_results.json'


def fixture():
    tables={p.name:list(csv.DictReader(p.open(encoding='utf-8-sig',newline=''))) for p in TABLES.glob('*.csv')}
    return tables,json.loads(FINAL.read_text(encoding='utf-8')),json.loads(SPELLING.read_text(encoding='utf-8'))


def test_final_tables_match_corrected_analysis():
    tables,final,spelling=fixture()
    verify.verify_corrected_tables(tables.__getitem__,final,spelling)


@pytest.mark.parametrize('table,column,value,model',[
    ('figure2_summary.csv','n','10','Qwen3-4B'),
    ('figure2_summary.csv','mean','0.1623679257326506','Qwen3-4B'),
    ('figureS2_robustness.csv','n','10','Qwen3-4B'),
    ('figureS3_equal_counts.csv','mean','0.126','qwen3-4b'),
    ('figureS4_lexical_support.csv','eligible_n','10','qwen3-4b'),
    ('figureS5_answer_audit.csv','count','49','qwen3-4b'),
])
def test_stale_figures_are_rejected(table,column,value,model):
    tables,final,spelling=fixture()
    row=next(r for r in tables[table] if r['model']==model)
    row[column]=value
    with pytest.raises(AssertionError):
        verify.verify_corrected_tables(tables.__getitem__,final,spelling)


def test_accent_does_not_exclude_flagship_from_final_sample():
    tables,final,spelling=fixture()
    row=next(r for r in tables['test_fact_inclusion_audit.csv'] if r['model']=='Qwen3-4B' and r['pair_id']=='columbus_americas')
    assert row['included']=='True' and row['reason']=='included'
    row['included']='False'
    with pytest.raises(AssertionError):
        verify.verify_corrected_tables(tables.__getitem__,final,spelling)


def test_output_matched_controls_are_not_inflated_to_twelve():
    tables,final,spelling=fixture()
    row=next(r for r in tables['figure4_controls.csv'] if r['model']=='Qwen3-4B')
    assert int(row['n'])==10
    row['n']='12'
    with pytest.raises(AssertionError):
        verify.verify_corrected_tables(tables.__getitem__,final,spelling)
