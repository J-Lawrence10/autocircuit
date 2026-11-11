"""Current presentation numbering; archived measurement filenames remain stable."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/model_extension/paper_review_20261111'
FIG = OUT / 'figures'
BASE = ROOT / 'data/model_extension/final_corrected_scoring_20261111/paper_figures'
HISTORY = ROOT / 'data/model_extension/history_pilot_graphs_20261110/paper_figure_v1'
NUMBER_MAP = {'3': 'S10', '4': '3', '5': '4', '6': '5', '7': '6'}
STEM_MAP = {
    'figure3_fact_and_wording': 'figureS10_fact_and_wording',
    'figure4_control_comparisons': 'figure3_control_comparisons',
    'figure5_matched_choice': 'figure4_matched_choice',
    'figure6_failure_cases': 'figure5_failure_cases',
    'figure7_history_answers': 'figure6_history_answers',
}


def renumber(text):
    return re.sub(r'\b(Figure(?:s)?) ([3-7])([a-cA-C])?(?!\d)',
                  lambda m: m[1]+' '+NUMBER_MAP[m[2]]+(m[3] or ''), text)


def catalog():
    prior = json.loads((BASE/'figure_manifest.json').read_text(encoding='utf-8'))
    history = json.loads((HISTORY/'figure_manifest.json').read_text(encoding='utf-8'))
    rows = []
    for original in prior['figures'] + [history] + prior['supplements']:
        row = dict(original)
        for key in ['files', 'script_sha256']:
            if key in row:
                row['archive_'+key] = row.pop(key)
        row['archive_stem'] = original['stem']
        row['stem'] = STEM_MAP.get(original['stem'], original['stem'])
        row['label'] = re.match(r'figure(S?\d+)_', row['stem'])[1]
        row['number'] = int(row['label'].removeprefix('S'))
        row['legend'] = renumber(row['legend'])
        rows.append(row)
    by = {r['stem']: r for r in rows}
    by['figure1_design_and_coverage'].update(
        title='Four comparisons connect feature sharing, responses, and correctness',
        legend=(
            'A, Compare a factual question with its rewording and with other-fact questions in the same subject and evaluation set. '
            'The final samples contain 8 Gemma-2-2B, 10 Qwen3-1.7B, and 12 Qwen3-4B evaluation facts. Gold is the chemical element. '
            'Gold, iron, and invented name zorium are development examples, not the evaluation questions plotted in Figure 2. '
            'B, In Qwen3-4B, vary the queried country, capital-to-A/B mapping, and wording while preserving word and token counts '
            'within each country pair. All 48 predictions across six evaluation pairs were correct. The France/Germany design '
            'example is a pilot pair excluded from evaluation. C, Compare a selected error graph with correct predictions for '
            'the intended country and for another country giving the same answer as the error. This diagnostic includes 16 '
            'graphs from one country pair and two response formats, with shared controls. D, Swap dates assigned to A and B '
            'or reverse question/context order. All 16 history graphs from two event pairs are included, with 11 correct and '
            'five incorrect predictions. The displayed Declaration of Independence example retains A while selecting 1776 '
            'or 1783. Prompts in this overview are abridged to show the comparison; Figure 6 gives exact history prompts. '
            'Answers denote highest-probability next tokens. Arrows show comparisons, not causes. Each analysis retains its '
            'own question set, inclusion rules, and unit of analysis.'))
    by['figure3_control_comparisons']['title'] = 'The invented name comparison changes the observed overlap difference'
    by['figure2_fact_signal']['legend'] = by['figure2_fact_signal']['legend'].replace(
        'The displayed arithmetic, 0.50 − 0.30 = +0.20, illustrates this subtraction.',
        'For example, overlaps of 0.50 and 0.30 give a difference of +0.20.')
    workflow = by['figureS8_feature_overlap_workflow']['legend']
    workflow = workflow.replace('Exact chemistry prompts about gold and iron, plus invented name zorium, are development examples from the manifest, not evaluation questions.',
        'Gold and invented name zorium refer to development examples from the manifest, not evaluation questions.')
    workflow = workflow.replace('; iron illustrates one comparator, not the whole pool', '')
    workflow = workflow.replace('share a and b (green), while c and d are unshared (white)', 'share a and b, while c and d are unshared')
    workflow = workflow.replace('These values do not describe the gold or iron graphs.', 'These values do not describe measured graphs.')
    workflow = workflow.replace('Arrows show analysis steps, not causal pathways;', 'The numbered steps describe the analysis, not causal pathways;')
    by['figureS8_feature_overlap_workflow']['legend'] = workflow
    by['figure5_failure_cases']['title'] = 'Error graphs share more features with correct predictions giving the same response'
    by['figure4_matched_choice']['legend'] = by['figure4_matched_choice']['legend'].replace(
        'C, Their average is the prespecified primary outcome:',
        'C, The average same-country overlap difference is the mean of the two contrasts in B and is the prespecified primary outcome:')
    by['figureS10_fact_and_wording']['title'] = 'Feature overlap varies across facts and question versions'
    # The compact supplement omits the old prompt-example inset; all prompts remain archived.
    by['figureS10_fact_and_wording']['legend'] = re.sub(
        r'The gold/iron examples use exact saved prompts\. Starting from gold alternative 1, gold original shares the fact, '
        r'iron alternative 1 shares the version label, and iron original differs in both\. ', '',
        by['figureS10_fact_and_wording']['legend'])
    for row in rows:
        row['title'] = row['title'].replace('in these samples', 'in the analyzed samples')
    return sorted(rows, key=lambda r: (r['label'].startswith('S'), r['number']))
