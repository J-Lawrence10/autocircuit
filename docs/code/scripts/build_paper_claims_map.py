"""Build a PI-facing claims map from saved results; no model or analysis runs."""
from pathlib import Path
import csv
import hashlib
import io
import json
from statistics import mean

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/model_extension/final_corrected_scoring_20261111/paper_figures/tables'
OUT = ROOT / 'data/model_extension/final_corrected_scoring_20261111/claims'
LATE = ROOT / 'data/model_extension/qwen17_completion_20261106/analysis/results.json'
REVISION = '2026-11-11'
INK, MUTED, BLUE, TEAL = '#193747', '#506774', '#256B91', '#247867'
PALE, LINE, AMBER = '#F0F5F7', '#D5E0E5', '#8A522B'
SOURCES = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_bytes(path):
    raw = path.read_bytes()
    SOURCES[path] = hashlib.sha256(raw).hexdigest()
    return raw


def rows(name):
    p = SOURCE / name
    return list(csv.DictReader(io.StringIO(source_bytes(p).decode('utf-8-sig'))))


def main():
    SOURCES.clear()
    current = rows('figure2_summary.csv')
    blocks = rows('figure5_block_contrasts.csv')
    failures = rows('figure6_comparisons.csv')
    behavior = rows('figure6_behavior.csv')
    history = rows('table_history_pilot.csv')
    assert [int(r['n']) for r in current] == [8, 10, 12]
    assert [round(float(r['mean']), 3) for r in current] == [.170, .089, .218]
    history_graphs = json.loads(source_bytes(ROOT/'data/model_extension/history_pilot_graphs_20261110/analysis/results.json'))
    assert history_graphs['valid_graphs']==16 and history_graphs['correct']==11 and history_graphs['wrong']==5
    assert len(blocks) == 6
    same = mean(float(r['fact_same_label']) for r in blocks)
    changed = mean(float(r['fact_different_label']) for r in blocks)
    pairs = {}
    for r in failures:
        pairs.setdefault(r['job_id'], {})[r['comparator']] = float(r['jaccard'])
    favored = sum(p['same_output'] > p['same_country'] for p in pairs.values())
    assert favored == len(pairs) == 8
    assert sum(int(r['correct']) for r in behavior if r['reference'] == 'named') == 8
    overall = next(r for r in history if r['component'] == 'Overall')
    assert int(overall['correct']) == 15 and int(overall['total']) == 20
    late = json.loads(source_bytes(LATE))
    assert late['status'] == 'completed' and late['original_reconstruction']['passed']
    assert late['input_counts'] == dict(original_raw=50, new_raw=41, combined_raw=91, length_rejections=29)
    qwen = late['cohorts']['expanded91_late_observational']
    geography = qwen['heldout_domains']['geography']
    pooled = qwen['heldout_primary']
    assert qwen['heldout_domains']['chemistry']['n'] == geography['n'] == 5
    assert pooled['n'] == 10
    assert abs(pooled['mean'] - float(current[1]['mean'])) < 1e-12
    assert geography['positive_n'] == 5 and pooled['positive_n'] == 10
    controls = qwen['aggregates']['held_out']['feature_jaccard']['margin_same_template_nonce']
    control_favored = controls['n'] - controls['positive_n'] - controls['zero_n']
    assert control_favored == 8 and controls['n'] == 10
    history_collection = next(r for r in late['collection_by_domain'] if r['domain'] == 'history')
    assert history_collection['available_graphs'] == 11
    assert history_collection['complete_four_role_sets'] == 0
    assert history_collection['length_rejected_jobs'] == 29
    for path in [ROOT/'docs/papers/INTEGRATED_PAPER_OUTLINE.md', ROOT/'scripts/figure_plain_language.py']:
        source_bytes(path)

    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none'})
    fig = plt.figure(figsize=(17, 14), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')
    texts = []
    contained = []

    def text(x, y, s, size=12, color=INK, weight='normal', ha='left', va='top', bounds=None):
        t = ax.text(x, y, s, fontsize=size, color=color, weight=weight,
                    ha=ha, va=va, linespacing=1.4)
        texts.append(t)
        if bounds is not None:
            contained.append((t, bounds))
        return t

    def box(x, y, w, h, fill=PALE, edge='none'):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.008,rounding_size=0.010',
                                   facecolor=fill, edgecolor=edge, linewidth=.9))

    text(.04, .970, 'Do similar attribution graphs reflect the fact being asked about,\nor the answer the model produces?', 24, weight='bold')
    text(.04, .902, 'Three models. We compare reworded questions, controlled answer changes, and selected wrong answers.', 12, MUTED)
    text(.96, .970, 'PI DISCUSSION\n11 November 2026', 10, MUTED, ha='right')
    text(.04, .866, 'Feature overlap measures shared learned components in saved graphs. It does not measure answer accuracy.', 12)

    xs, width = [.04, .355, .67], .29
    headers = [
        ('01  SAME-FACT COMPARISON', 'Same-fact questions\nshare more features', 'Three models · current samples · Figure 2'),
        ('02  STRONGER CONTROL', 'Higher same-fact overlap\nwith the same answer letter', 'Qwen3-4B only · six country pairs · Figure 5'),
        ('03  FAILURE CHECK', 'Wrong-answer graphs resemble\ncorrect same-answer graphs', 'Qwen3-4B only · selected errors · Figure 6'),
    ]
    cards = [(x+.005, .520, x+width-.005, .815) for x in xs]
    for x, bounds, (tag, title, scope) in zip(xs, cards, headers):
        box(x, .515, width, .305)
        text(x+.016, .802, tag, 10, BLUE, 'bold', bounds=bounds)
        text(x+.016, .775, title, 17, weight='bold', bounds=bounds)
        text(x+.016, .721, scope, 9.5, MUTED, bounds=bounds)

    x = xs[0]+.016
    text(x, .691, 'Same-fact minus average other-fact overlap', 10.5, weight='bold', bounds=cards[0])
    for y, r in zip([.659, .631, .603], current):
        text(x, y, r['model'], 12, bounds=cards[0])
        text(xs[0]+width-.016, y, f"+{float(r['mean']):.3f}   (n={r['n']})", 12, BLUE, 'bold', ha='right', bounds=cards[0])
    text(x, .562, 'The fact, wording, and expected answer\nremain linked in these comparisons.', 11, bounds=cards[0])

    x = xs[1]+.016
    text(x, .691, 'Same-country minus other-country overlap', 10.5, weight='bold', bounds=cards[1])
    for y, label, value in [(.648, 'Same A/B answer', same), (.606, 'Changed A/B answer', changed)]:
        text(x, y, label, 12, bounds=cards[1])
        text(xs[1]+width-.016, y+.004, f'{value:+.4f}', 18, BLUE, 'bold', ha='right', bounds=cards[1])
    text(x, .561, 'Same words and token counts within each pair;\nall 48 predicted answer letters were correct.', 10.5, MUTED, bounds=cards[1])

    x = xs[2]+.016
    text(x, .691, f'{favored}/{len(pairs)} comparisons', 23, BLUE, 'bold', bounds=cards[2])
    text(x, .655, 'favor the correct response giving the same\nanswer as the error over the correct response\nfor the intended country.', 11.5, bounds=cards[2])
    text(x, .595, '16 graphs · one country pair · shared controls', 10, MUTED, bounds=cards[2])
    text(x, .566, 'An incorrect Berlin answer resembles a correct\nBerlin response more than the intended\nParis response.', 11, bounds=cards[2])

    # Keep available graphs, included facts, and the control comparison distinct.
    box(.04, .355, .92, .135, fill='#F3F6FA', edge=LINE)
    text(.056, .477, 'CONTROLS AND COVERAGE', 10, BLUE, 'bold')
    text(.944, .477, 'Available graphs and included facts are separate counts · Figure S7', 10, MUTED, ha='right')
    strip_bounds = [(x+.005, .360, x+width-.005, .457) for x in xs]
    x = xs[0]+.016
    text(x, .448, 'Qwen3-1.7B: two included subjects', 11.5, weight='bold', bounds=strip_bounds[0])
    text(x, .424, '91/120 graphs available.\nTen evaluation facts: five chemistry,\nfive geography.', 11.5, bounds=strip_bounds[0])
    x = xs[1]+.016
    text(x, .448, 'Qwen3-1.7B wording controls', 11.5, weight='bold', bounds=strip_bounds[1])
    text(x, .424, f'{control_favored}/{controls["n"]} questions share more features with\nthe invented name control in the starting\nwording than with their factual rewording.', 11, bounds=strip_bounds[1])
    x = xs[2]+.016
    text(x, .448, 'History: complementary comparisons', 11.5, weight='bold', bounds=strip_bounds[2])
    text(x, .424, 'Qwen3-4B: two factual-completion questions;\n16 date-choice graphs, including five errors.\nQwen3-1.7B: no complete history control sets.', 10.5, bounds=strip_bounds[2])

    for x in xs:
        ax.add_patch(FancyArrowPatch((x+width/2, .343), (x+width/2, .319),
                                     arrowstyle='-|>', mutation_scale=15, color=TEAL, linewidth=1.3))
    box(.04, .205, .92, .10, fill='#EAF4F0')
    central = (.045, .210, .955, .300)
    text(.5, .292, 'CENTRAL CLAIM', 10, TEAL, 'bold', ha='center', bounds=central)
    text(.5, .268, 'In these experiments, graph overlap varies with the prompt and the answer.', 18, weight='bold', ha='center', bounds=central)
    text(.5, .231, 'On its own, it cannot certify correct factual processing or a representation independent of the answer.', 12, ha='center', bounds=central)

    text(.04, .179, 'SUPPORTING CHECKS', 10, TEAL, 'bold')
    text(.04, .153, 'Positive averages survive equal feature counts.\nAnswer-related differences remain after removing\nsome final-position and late-layer features.', 10.5)
    text(.355, .179, 'SCOPE LIMITS', 10, AMBER, 'bold')
    text(.355, .153, 'Facts recur across models; no model ranking.\nHistory examples share comparison graphs.\nSelected errors do not estimate failure frequency.', 10.5)
    text(.67, .179, 'NOT ESTABLISHED', 10, AMBER, 'bold')
    text(.67, .153, 'No causal circuit or proven error mechanism.\nThe fact remains linked to words and answers.\nNear-zero does not establish absent knowledge.', 10.5)

    ax.plot([.04, .96], [.070, .070], color=LINE, lw=1)
    text(.04, .053, 'Values are differences in Jaccard overlap, not percentages. n counts evaluation facts. Arrows connect evidence to interpretation, not causes.', 9, MUTED)
    text(.04, .031, 'Sources: Figures 2 and 5–7; Supplements S3/S6/S7/S9; final corrected scoring. One primary sample per model.', 8.5, MUTED)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for t in texts:
        assert '\u2014' not in t.get_text(), t.get_text()
        b = t.get_window_extent(renderer).transformed(ax.transAxes.inverted())
        assert 0 <= b.x0 <= b.x1 <= 1 and 0 <= b.y0 <= b.y1 <= 1, t.get_text()
    for t, bounds in contained:
        b = t.get_window_extent(renderer).transformed(ax.transAxes.inverted())
        x0, y0, x1, y1 = bounds
        assert x0 <= b.x0 <= b.x1 <= x1 and y0 <= b.y0 <= b.y1 <= y1, ('Text exceeds its box', t.get_text(), tuple(b.extents), bounds)
    for i, (first, bounds) in enumerate(contained):
        a = first.get_window_extent(renderer)
        for second, other_bounds in contained[i+1:]:
            if bounds != other_bounds:
                continue
            b = second.get_window_extent(renderer)
            assert min(a.x1, b.x1) <= max(a.x0, b.x0) or min(a.y1, b.y1) <= max(a.y0, b.y0), ('Text overlap', first.get_text(), second.get_text())
    for path, expected in SOURCES.items():
        assert sha(path) == expected, f'Source changed while building: {path}'
    for extension in ['png', 'svg']:
        fig.savefig(OUT/f'paper_claims_map.{extension}', dpi=240, facecolor='white')
    plt.close(fig)
    manifest = {'date': REVISION, 'purpose': 'PI-facing evidence and claim summary with one current sample per model; no new model requests or statistical analysis',
                'source_hashes': {str(p.relative_to(ROOT)): value for p, value in SOURCES.items()},
                'script_sha256': sha(Path(__file__)),
                'output_hashes': {p.name: sha(p) for p in OUT.iterdir() if p.suffix in ['.png', '.svg']},
                'checks': ['Current evaluation-fact counts 8/10/12; model means 0.170/0.089/0.218', 'Six matched-choice blocks',
                           'Eight of eight selected failures favor same output', 'Sixteen historical-date graphs, eleven correct and five incorrect',
                           'Three models retained; one primary sample per model',
                           'Current Qwen3-1.7B n10 mean matches Figure 2 and saved analysis',
                           'Eight of ten Qwen3-1.7B comparisons favor same-pattern invented name controls',
                           'Qwen3-1.7B incomplete history controls distinguished from Qwen3-4B available history comparisons',
                           'All rendered text within canvas and assigned boxes; no overlapping text within boxes',
                           'No em dashes in figure text', 'Sources unchanged during build']}
    (OUT/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(OUT/'paper_claims_map.png')


if __name__ == '__main__':
    main()
