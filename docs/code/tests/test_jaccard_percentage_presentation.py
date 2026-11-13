"""Percent display is a reversible unit change, not a new scientific analysis."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / 'data/model_extension/paper_review_20261111/figures'
FIG = LOCAL if LOCAL.exists() else ROOT.parent / 'figures'
TABLES = FIG / 'tables' if LOCAL.exists() else ROOT.parent / 'tables'
MANIFEST = (FIG / 'figure_manifest.json' if LOCAL.exists()
            else ROOT.parent / 'provenance/final_figure_manifest.json')


def figure_text(stem, group=None):
    svg = ET.parse(FIG / (stem + '.svg')).getroot()
    root = svg if group is None else next(node for node in svg.iter() if node.get('id') == group)
    return [''.join(node.itertext()).strip() for node in root.iter() if node.tag.endswith('}text')]


def read_rows(name):
    with (TABLES / name).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def test_manifest_declares_display_only_scaling_and_native_cosine():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    units = manifest['presentation_units']
    assert units['stored_jaccard'] == 'native 0–1 scale, unchanged'
    assert units['displayed_overlap'] == 'percent (100 × Jaccard)'
    assert units['displayed_difference'] == 'percentage points (100 × native contrast)'
    assert units['lexical_overlap'] == 'percent (100 × word-set Jaccard)'
    assert units['cosine_metrics'] == 'native units, unchanged'
    assert units['counts_and_p_values'] == 'unchanged'
    assert 'plotted data coordinates and saved measurements unchanged' in units['method']


def test_formatter_multiplies_ticks_without_mutating_artists():
    # Extract only the presentation helper, so this also runs in the portable
    # code package without requiring the excluded full author archive.
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    from matplotlib.ticker import FuncFormatter
    source = ROOT / 'scripts/build_reviewed_paper_figures.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'percent_axis')
    scope = {'FuncFormatter': FuncFormatter}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
    fig, ax = plt.subplots()
    line, = ax.plot([0, 1], [.8005, .4853])
    before = line.get_ydata().copy()
    scope['percent_axis'](ax, label='Feature overlap (%)')
    assert list(line.get_ydata()) == list(before) == [.8005, .4853]
    formatter = ax.yaxis.get_major_formatter()
    assert formatter(.8005, 0) == '80.05'
    assert formatter(.4853, 0) == '48.53'
    assert formatter(.0303, 0) == '3.03'
    assert formatter(-.0022, 0) == '-0.22'
    assert formatter(0, 0) == '0'
    assert formatter(1, 0) == '100'
    plt.close(fig)


def test_matched_choice_percent_cells_colorbar_and_percentage_point_contrasts():
    labels = figure_text('figure4_matched_choice')
    assert {'80.05%', '48.53%', '73.77%', '48.74%'} <= set(labels)
    assert {'6.28 pp', '-0.22 pp', '3.03 pp', '28.27 pp'} <= set(labels)
    assert 'Feature overlap (%): 0 = none; 100 = identical sets' in labels
    assert {'0', '50', '100'} <= set(figure_text('figure4_matched_choice', 'axes_5'))
    assert labels.count('(percentage points)') == 2
    assert not {'0.0303', '0.0628', '-0.0022', '0.2827', '0.801', '0.485'} & set(labels)
    assert '48 / 48 correct A/B predictions' in labels


def test_all_jaccard_difference_panels_name_percentage_points():
    for stem in [
        'figure2_fact_signal', 'figure3_control_comparisons', 'figure4_matched_choice',
        'figureS2_robustness', 'figureS3_equal_feature_counts',
        'figureS6_graph_location_sensitivity', 'figureS7_qwen17_completion',
        'figureS9_answer_spelling', 'figureS10_fact_and_wording',
    ]:
        labels = figure_text(stem)
        assert 'Difference in feature overlap' in labels, stem
        assert '(percentage points)' in labels, stem
    for stem in ['figure5_failure_cases', 'figure6_history_answers', 'figureS9_answer_spelling']:
        assert 'Feature overlap (%)' in figure_text(stem), stem


def test_word_overlap_percent_display_retains_native_matching_threshold():
    labels = figure_text('figureS4_lexical_support')
    assert 'same-fact rewording (%)' in labels and 'with another fact (%)' in labels
    assert {'0', '20', '40', '60', '80', '100'} <= set(labels)
    assert any('within 5 percentage points' in text for text in labels)
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    legend = next(row['legend'] for row in manifest['supplements'] if row['label'] == 'S4')
    assert '±5 percentage points' in legend and '±0.05 on the native Jaccard scale' in legend
    tree = ast.parse((ROOT / 'scripts/build_reviewed_paper_figures.py').read_text(encoding='utf-8'))
    lexical = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'lexical')
    band = next(node for node in ast.walk(lexical) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute) and node.func.attr == 'fill_between')
    assert isinstance(band.args[1], ast.BinOp) and isinstance(band.args[1].op, ast.Sub)
    assert isinstance(band.args[2], ast.BinOp) and isinstance(band.args[2].op, ast.Add)
    assert band.args[1].right.value == band.args[2].right.value == .05


def test_workflow_example_uses_percent_and_percentage_points():
    labels = figure_text('figureS8_feature_overlap_workflow')
    assert '{a, b, c} and {a, b, d} → 2 / 4 = 50%.' in labels
    assert 'Illustrative other-fact mean = 30%.' in labels
    assert 'Difference: 50% − 30% = +20 pp.' in labels
    assert 'pp = percentage points.' in labels
    assert any('illustrative, not measured results' in text for text in labels)


def test_cosine_panel_keeps_native_scale_and_label():
    overlap = figure_text('figureS10_fact_and_wording', 'axes_1')
    cosine = figure_text('figureS10_fact_and_wording', 'axes_2')
    assert '(percentage points)' in overlap
    assert {'0', '5', '10', '15', '20'} <= set(overlap)
    assert 'Difference in cosine similarity' in cosine and '(native units)' in cosine
    assert {'0.000', '0.050', '0.100', '0.150', '0.200'} <= set(cosine)
    assert not any('%' in text or 'percentage points' in text for text in cosine)


def test_saved_tables_counts_and_p_values_remain_unscaled():
    if LOCAL.exists():
        original = ROOT / 'data/model_extension/final_corrected_scoring_20261111/paper_figures/tables'
        sources = list(original.glob('*.csv'))
        assert sources
        for source in sources:
            assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256((TABLES/source.name).read_bytes()).digest()
    summaries = read_rows('figure2_summary.csv')
    assert [int(row['n']) for row in summaries] == [8, 10, 12]
    assert [float(row['mean']) for row in summaries] == [
        .17035573839323534, .08943970371340235, .21832503734816042]
    assert [float(row['exact_one_sided_sign_flip_p']) for row in summaries] == [1/256, 1/1024, 1/4096]
    primary = json.loads((TABLES/'matched_choice_primary.json').read_text(encoding='utf-8'))
    assert primary['mean_fact_effect'] == .030319246701048918
    assert primary['ci95'] == [.02645935094413981, .03379145674905178]
    assert primary['exact_conditional_assignment_p'] == 1/4096
    assert primary['bonferroni_planned_family_p'] == 3/4096
    assert primary['n_blocks'] == primary['positive_blocks'] == 6
    assert primary['null_assignments'] == 4096
    counts = read_rows('figureS5_crossed_expected_tokens.csv')
    assert [int(row['matching']) for row in counts] == [7, 4, 0, 8, 9, 0]
    assert {int(row['total']) for row in counts} == {9}
