"""Presentation regression checks; no model calls or new scientific estimates."""
from pathlib import Path
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT/'data/model_extension/paper_review_20261111/figures'
FIG = LOCAL if LOCAL.exists() else ROOT.parent/'figures'
TABLES = FIG/'tables' if LOCAL.exists() else ROOT.parent/'tables'
MANIFEST = (FIG/'figure_manifest.json' if LOCAL.exists()
            else ROOT.parent/'provenance/final_figure_manifest.json')
MANUSCRIPT = (ROOT/'docs/papers/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md' if LOCAL.exists()
              else ROOT.parent/'manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md')


def manifest():
    return json.loads(MANIFEST.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_six_main_figures_ten_supplements_have_editable_assets():
    data = manifest()
    assert [r['label'] for r in data['figures']] == list('123456')
    assert [r['label'] for r in data['supplements']] == [f'S{i}' for i in range(1, 11)]
    for row in data['figures'] + data['supplements']:
        for ext in ['png', 'svg']:
            assert (FIG/f'{row["stem"]}.{ext}').is_file()
        assert all((TABLES/name).is_file() for name in row['source_tables'])


def test_print_dimensions_font_floor_and_canvas_checks():
    checks = manifest()['layout_checks']
    assert len(checks) == 16
    for stem, check in checks.items():
        assert check['width_mm'] == 180
        assert check['minimum_font_pt'] >= 7
        assert not check['text_outside_canvas']
        svg = ET.parse(FIG/f'{stem}.svg').getroot()
        width_pt = float(svg.attrib['width'].removesuffix('pt'))
        assert abs(width_pt*25.4/72-180) < .01
        texts = [t for t in svg.iter() if t.tag.endswith('}text')]
        assert texts, 'Text must remain editable, not converted to paths'
        for text in texts:
            size = re.search(r'font-size: ([\d.]+)px', text.attrib.get('style', ''))
            if size:
                assert float(size[1]) >= 7


def test_overview_reads_final_counts_and_includes_history():
    svg = (FIG/'figure1_design_and_coverage.svg').read_text(encoding='utf-8')
    assert 'Evaluation facts: 8 / 10 / 12' in svg
    assert '8 / 10 / 10' not in svg
    assert 'Distinguish letters from years' in svg
    assert '16 graphs (11 correct)' in svg
    assert 'Prompts are abridged examples.' in svg


def test_source_measurements_are_unchanged_and_s6_is_bundled():
    data = manifest()
    if LOCAL.exists():
        base = ROOT/'data/model_extension/final_corrected_scoring_20261111/paper_figures/tables'
        for source in base.glob('*.csv'):
            assert sha(source) == sha(TABLES/source.name)
        for name, expected in data['source_hashes'].items():
            assert sha(ROOT/name) == expected, name
    s6 = next(r for r in data['supplements'] if r['label'] == 'S6')
    assert {'matched_choice_sensitivity.csv', 'failure_sensitivity.csv', 'statistics_audit.json'} <= set(s6['source_tables'])
    primary = json.loads((TABLES/'matched_choice_primary.json').read_text(encoding='utf-8'))
    assert abs(primary['mean_fact_effect']-.030319246701048918) < 1e-15
    assert primary['ci95'] == [.02645935094413981, .03379145674905178]


def test_crossed_token_counts_come_from_the_saved_audit():
    with (TABLES/'figureS5_crossed_expected_tokens.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    assert [int(r['matching']) for r in rows] == [7, 4, 0, 8, 9, 0]
    assert all(int(r['total']) == 9 for r in rows)


def test_approved_title_narrative_and_abstract_preservation():
    text = MANUSCRIPT.read_text(encoding='utf-8')
    assert 'title: "Feature sharing in attribution graphs tracks predicted responses"' in text
    assert 'subtitle:' not in text
    assert 'Does greater feature overlap still distinguish questions about the same fact when the predicted response changes?' in text
    assert 'Graph construction retains features according to their influence on the outputs being explained [1].' in text
    methods = text.split('### 2.7 ', 1)[1].split('### 2.8 ', 1)[0]
    assert 'Primary mean: 0.0303' not in methods
    assert 'Paired mean difference: 0.0650' not in methods
    assert 'Primary mean: 3.03' not in methods
    assert 'Paired mean difference: 6.50' not in methods
    main = text.split('## Supporting analyses', 1)[0]
    assert '![Figure S10:' not in main
    assert '![Figure S10:' in text.split('### A4 ', 1)[1]
    assert '### A8 Data, code, and reproducibility records' in text
    abstract = text.split('## Abstract\n\n', 1)[1].split('\n\n## 1.', 1)[0].strip()
    # Preserve the approved scientific wording byte-for-byte after reversing
    # only the three explicitly authorized display-unit substitutions.
    changes = {
        '3.03 percentage points (95% block-bootstrap interval 2.65–3.38)':
            '0.0303 (95% block-bootstrap interval 0.0265–0.0338)',
        '6.28 percentage points when': '0.0628 when',
        '(-0.22 percentage points)': '(-0.0022)',
    }
    restored = abstract
    for displayed, original in changes.items():
        assert displayed in abstract
        restored = restored.replace(displayed, original)
    assert hashlib.sha256(restored.encode()).hexdigest() == '32f6ffd09ab8d8c733e9f348ae7a949377d3faf6f6ec1005c7b3a60a540d0673'
    assert '\u2014' not in main


def test_current_sharing_guide_uses_current_figure_numbers():
    share = ROOT/'paper_share' if LOCAL.exists() else ROOT.parent
    readme = (share/'README.md').read_text(encoding='utf-8')
    assert 'six main figures and ten supplements' in readme
    assert 'Seven main' not in readme and 'Figure 7' not in readme
    claims = (share/'claims/paper_claims_map.svg').read_text(encoding='utf-8')
    assert 'Figures 2 and 4–6' in claims
    assert 'Figures 2 and 5–7' not in claims


def test_descriptive_legends_preserve_statistics_without_unplotted_results():
    rows = manifest()['figures'] + manifest()['supplements']
    by_label = {r['label']: r['legend'] for r in rows}
    assert '10,000 fact-level resamples' in by_label['2']
    assert 'subject mean is shown without an interval' in by_label['2']
    assert 'n=2, 9, and 10 in A and n=7, 10, and 10 in B' in by_label['3']
    assert '95% block-bootstrap interval, resampling country pairs (n=6)' in by_label['4']
    assert 'eight selected error cases' in by_label['5']
    assert 'Panels B and C reuse the same 16 graphs' in by_label['6']
    assert '1.5 interquartile ranges' in by_label['S1']
    assert 'n=2' in by_label['S2']
    assert 'resampling facts, not the 200 repetitions' in by_label['S3']
    assert 'n=50' in by_label['S5'] and 'n=60' in by_label['S5']
    assert '0.101/0.106' not in by_label['S5']
    assert 'tokenizer access' not in by_label['S5'].lower()
    assert 'illustrative, not measured results' in by_label['S8']
    assert 'two facts use each other as comparators' in by_label['S9']
    assert 'not confidence limits' in by_label['S10']
    for legend in by_label.values():
        assert '\u2014' not in legend


def test_caption_only_sync_preserves_artwork_and_measurement_metadata():
    import sys
    from copy import deepcopy
    sys.path.insert(0, str(ROOT/'scripts'))
    from sync_manuscript_figure_captions import reconcile_manifest
    original = dict(figures=[dict(label='1', stem='figure1_test', title='Unchanged title',
                                 legend='Previous wording', source_tables=['saved.csv'])], supplements=[],
                    source_hashes={'scripts/review_figure_catalog.py': 'old', 'saved.csv': 'datahash'},
                    output_hashes={'figure1_test.svg': 'imagehash'}, layout_checks={'fixed': True})
    before = deepcopy(original)
    entries = [dict(label='1', stem='figure1_test', title='Unchanged title', legend='Revised wording')]
    updated, changed = reconcile_manifest(original, entries, 'new')
    assert original == before
    assert changed == ['1']
    assert updated['output_hashes'] == before['output_hashes']
    assert updated['layout_checks'] == before['layout_checks']
    assert updated['source_hashes']['saved.csv'] == 'datahash'
    assert updated['figures'][0]['source_tables'] == ['saved.csv']
    assert not updated['legend_edit_history'][-1]['artwork_regenerated']


def test_caption_only_sync_rejects_title_changes():
    import sys
    import pytest
    sys.path.insert(0, str(ROOT/'scripts'))
    from sync_manuscript_figure_captions import reconcile_manifest
    original = dict(figures=[dict(label='1', stem='figure1_test', title='Original', legend='Before')],
                    supplements=[], source_hashes={})
    entries = [dict(label='1', stem='figure1_test', title='New artwork title', legend='After')]
    with pytest.raises(ValueError, match='titles or identity changed'):
        reconcile_manifest(original, entries, 'new')

