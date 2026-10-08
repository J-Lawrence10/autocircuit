"""Build a PI-facing claims map from archived figure tables; no new analysis runs."""
from pathlib import Path
import csv
import hashlib
import json
from statistics import mean

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/model_extension/paper_figures_plain_language_20261006/tables'
OUT = ROOT / 'data/model_extension/paper_claims_map_20261007'
INK, MUTED, BLUE, TEAL = '#193747', '#506774', '#256B91', '#247867'
PALE, LINE, AMBER = '#F0F5F7', '#D5E0E5', '#8A522B'
SOURCES = []


def rows(name):
    p = SOURCE / name
    SOURCES.append(p)
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    original = rows('figure2_summary.csv')
    blocks = rows('figure5_block_contrasts.csv')
    failures = rows('figure6_comparisons.csv')
    behavior = rows('figure6_behavior.csv')
    history = rows('table_history_pilot.csv')
    assert [int(r['n']) for r in original] == [8, 5, 10]
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

    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none'})
    fig = plt.figure(figsize=(17, 11.5), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')
    texts = []

    def text(x, y, s, size=12, color=INK, weight='normal', ha='left', va='top'):
        t = ax.text(x, y, s, fontsize=size, color=color, weight=weight,
                    ha=ha, va=va, linespacing=1.4)
        texts.append(t)
        return t

    def box(x, y, w, h, fill=PALE, edge='none'):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.008,rounding_size=0.010',
                                   facecolor=fill, edgecolor=edge, linewidth=.9))

    text(.04, .970, 'Do similar attribution graphs reflect the fact being asked about—\nor the answer the model produces?', 24, weight='bold')
    text(.04, .883, 'We compare reworded questions, controlled answer changes, and selected wrong answers to distinguish these possibilities.', 12, MUTED)
    text(.96, .970, 'PI DISCUSSION\n8 October 2026', 10, MUTED, ha='right')
    text(.04, .844, 'Feature overlap measures shared learned components in two saved graphs—not whether an answer is correct.', 12)

    xs, width = [.04, .355, .67], .29
    headers = [
        ('01  OBSERVATION', 'Same-fact questions\nshare more features', 'Three models · n = test questions · Figure 2'),
        ('02  STRONGER CONTROL', 'The difference depends\non the answer letter', 'Qwen3-4B only · six country pairs · Figure 5'),
        ('03  FAILURE CHECK', 'Wrong-answer graphs resemble\ncorrect same-answer graphs', 'Qwen3-4B only · selected errors · Figure 6'),
    ]
    for x, (tag, title, scope) in zip(xs, headers):
        box(x, .405, width, .395)
        text(x+.016, .780, tag, 10, BLUE, 'bold')
        text(x+.016, .747, title, 17, weight='bold')
        text(x+.016, .682, scope, 9.5, MUTED)

    x = xs[0]+.016
    text(x, .640, 'Same-fact minus average other-fact overlap', 10.5, weight='bold')
    for y, r in zip([.603, .568, .533], original):
        text(x, y, r['model'], 12)
        text(xs[0]+width-.016, y, f"+{float(r['mean']):.3f}   (n={r['n']})", 12, BLUE, 'bold', ha='right')
    text(x, .484, 'Supports an association with factual prompts.\nDoes not separate the fact from shared\nwords and the expected answer.', 11)

    x = xs[1]+.016
    text(x, .640, 'Same-country minus other-country overlap', 10.5, weight='bold')
    for y, label, value in [(.601, 'Same A/B answer', same), (.555, 'Changed A/B answer', changed)]:
        text(x, y, label, 12)
        text(xs[1]+width-.016, y+.004, f'{value:+.4f}', 18, BLUE, 'bold', ha='right')
    text(x, .507, 'Same words and token counts within each pair;\nall 48 predicted answer letters were correct.', 10.5, MUTED)
    text(x, .455, 'Shared features are not independent\nof the answer being produced here.', 11, weight='bold')

    x = xs[2]+.016
    text(x, .641, f'{favored}/{len(pairs)} comparisons', 23, BLUE, 'bold')
    text(x, .592, 'favor the correct response giving the same\nanswer as the error—not the correct response\nto the intended country.', 11.5)
    text(x, .516, '16 graphs · one country pair · two answer formats', 10, MUTED)
    text(x, .477, 'An incorrect Berlin answer resembles a\ncorrect Berlin response more than the\nintended Paris response.', 11)

    for x in xs:
        ax.add_patch(FancyArrowPatch((x+width/2, .395), (x+width/2, .355),
                                     arrowstyle='-|>', mutation_scale=15, color=TEAL, linewidth=1.3))
    box(.04, .225, .92, .12, fill='#EAF4F0')
    text(.5, .325, 'CENTRAL CLAIM', 10, TEAL, 'bold', ha='center')
    text(.5, .293, 'In these experiments, graph overlap varies with the prompt and the answer.', 18, weight='bold', ha='center')
    text(.5, .254, 'On its own, it cannot certify correct factual processing or a representation independent of the answer.', 12, ha='center')

    text(.04, .194, 'SUPPORTING CHECKS', 10, TEAL, 'bold')
    text(.04, .167, 'Positive averages survive equal feature counts.\nAnswer-related differences remain after removing\nsome final-position and late-layer features.', 10.5)
    text(.355, .194, 'SCOPE LIMITS', 10, AMBER, 'bold')
    text(.355, .167, 'Facts recur across models; no model ranking.\nQwen3-4B* original collection: 145/147 graphs.\nSelected errors do not estimate failure frequency.', 10.5)
    text(.67, .194, 'NOT ESTABLISHED', 10, AMBER, 'bold')
    text(.67, .167, 'No causal circuit or proven error mechanism.\nNear-zero does not prove no factual knowledge.\nHistory pilot: 15/20; no evaluation graph result.', 10.5)

    ax.plot([.04, .96], [.070, .070], color=LINE, lw=1)
    text(.04, .053, 'Reading the map: arrows connect evidence to interpretation, not causes. Values are differences in Jaccard overlap, not percentages.', 9, MUTED)
    text(.04, .031, 'Sources: integrated paper outline; Figure 2, 5 and 6 source tables; Supplements S3/S6; frozen history-pilot outcome. Follow-ups remain separate from original cohorts.', 8.5, MUTED)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for t in texts:
        b = t.get_window_extent(renderer).transformed(ax.transAxes.inverted())
        assert 0 <= b.x0 <= b.x1 <= 1 and 0 <= b.y0 <= b.y1 <= 1, t.get_text()
    for extension in ['png', 'svg']:
        fig.savefig(OUT/f'paper_claims_map.{extension}', dpi=240, facecolor='white')
    plt.close(fig)
    SOURCES.extend([ROOT/'docs/papers/INTEGRATED_PAPER_OUTLINE.md', ROOT/'scripts/figure_plain_language.py'])
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = {'date': '2026-10-08', 'purpose': 'PI-facing evidence and claim summary; no new experiments',
                'source_hashes': {str(p.relative_to(ROOT)): sha(p) for p in SOURCES},
                'script_sha256': sha(Path(__file__)),
                'output_hashes': {p.name: sha(p) for p in OUT.iterdir() if p.suffix in ['.png', '.svg']},
                'checks': ['Original question counts 8/5/10', 'Six matched-choice blocks',
                           'Eight of eight selected failures favor same output', 'History pilot 15/20',
                           'All rendered text within canvas']}
    (OUT/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(OUT/'paper_claims_map.png')


if __name__ == '__main__':
    main()
