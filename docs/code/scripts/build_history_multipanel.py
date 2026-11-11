"""Build the three-panel, source-linked history figure from saved results only."""
from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/model_extension/history_pilot_graphs_20261110'
OUT = DATA / 'paper_figure_v1'
STEM = 'figure7_history_answers'
TITLE = 'History: similar graphs can accompany different selected years'
INK = '#182B3A'
MUTED = '#516170'
RULE = '#CDD6DD'
BLUE = '#0072B2'
ORANGE = '#CC681B'
GREEN = '#177556'
RED = '#B33748'
EVENTS = {
    'US Declaration of Independence adoption': ('Declaration of Independence', BLUE, 'o'),
    'American Revolutionary Treaty of Paris signing': ('Treaty of Paris', BLUE, 's'),
    'Sputnik 1 launch': ('Sputnik 1', ORANGE, 'D'),
    'Explorer 1 launch': ('Explorer 1', ORANGE, '^'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prompt_parts(text):
    match = re.fullmatch(r'(Reply only A or B\.) (A: \d+\. B: \d+\.) (.+)', text)
    if not match:
        raise ValueError('Unexpected prompt format; do not paraphrase silently')
    instruction, options, body = match.groups()
    first, second = body.split('; ', 1)
    display = '\n'.join(textwrap.wrap(first + ';', 44) + textwrap.wrap(second, 44))
    assert ' '.join((instruction + '\n' + options + '\n' + display).split()) == text
    return instruction, options, display


def load_data():
    result = json.loads((DATA / 'analysis/results.json').read_text())
    validation = json.loads((DATA / 'analysis/validation.json').read_text())
    assert validation['complete'] and validation['results_sha256'] == sha(DATA / 'analysis/results.json')
    assert result['valid_graphs'] == 16 and result['wrong'] == 5
    jobs = {j['job_id']: j for j in json.loads((DATA / 'jobs.json').read_text())}
    audits = {r['job_id']: r for r in result['audits']}
    examples = []
    for wording, group in [(0, 'Same letter, different selected year'), (1, 'Different letter, same selected year')]:
        ids = [f'pilot_documents__f0m{mapping}w{wording}' for mapping in (0, 1)]
        pair = next(r for r in result['pairs'] if {r['a'], r['b']} == set(ids))
        assert pair['status'] == 'ok' and pair['mapping_only']
        examples.append(dict(group=group, wording=wording, pair=pair,
                             jobs=[jobs[i] for i in ids], audits=[audits[i] for i in ids]))
    panels = {}
    for panel, flag in [('b', 'mapping_only'), ('c', 'order_only')]:
        rows = []
        for pair in result['pairs']:
            if not pair[flag]:
                continue
            assert pair['status'] == 'ok'
            a, b = jobs[pair['a']], jobs[pair['b']]
            ar, br = audits[pair['a']], audits[pair['b']]
            assert a['event'] == b['event']
            if panel == 'b':
                assert a['wording'] == b['wording'] and a['mapping'] != b['mapping']
                assert pair['same_predicted_year'] is not pair['same_predicted_letter']
            else:
                assert a['mapping'] == b['mapping'] and a['wording'] != b['wording']
            rows.append(dict(panel=panel, event=a['event'], event_label=EVENTS[a['event']][0],
                             a=pair['a'], b=pair['b'], jaccard=pair['jaccard'],
                             same_letter=pair['same_predicted_letter'], same_year=pair['same_predicted_year'],
                             observed_a=ar['observed'], observed_b=br['observed'],
                             selected_year_a=ar['predicted_year'], selected_year_b=br['predicted_year'],
                             correct_a=ar['correct'], correct_b=br['correct'],
                             ordering_a=a['wording'], ordering_b=b['wording'],
                             mapping_a=a['mapping'], mapping_b=b['mapping']))
        assert len(rows) == 8 and sum(r['same_letter'] for r in rows) == 5
        panels[panel] = rows
    return result, examples, panels


def box(ax, x, y, w, h, **kwargs):
    patch = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.004,rounding_size=0.009',
                          linewidth=.8, edgecolor=RULE, facecolor='white', **kwargs)
    ax.add_patch(patch)
    return patch


def prompt_card(ax, x, y, job, audit, after=False):
    width, height = .365, .39
    box(ax, x, y, width, height)
    instruction, options, body = prompt_parts(job['plain_prompt'])
    ax.text(x + .012, y + height + .014, 'After swapping the dates' if after else 'Before swapping the dates',
            fontsize=10.5, weight='bold', color=MUTED, va='bottom')
    ax.text(x + .012, y + .366, instruction, va='top', fontsize=11.2, color=INK)
    ax.add_patch(Rectangle((x + .009, y + .268), width - .018, .058,
                           facecolor='#FFF1D8' if after else '#EEF3F7', edgecolor='none'))
    ax.text(x + .016, y + .297, options, va='center', fontsize=12, weight='bold', color=INK)
    ax.text(x + .012, y + .250, body, va='top', fontsize=10.7, linespacing=1.18, color=INK)
    ax.plot([x + .012, x + width - .012], [y + .081, y + .081], color=RULE, lw=.6)
    ax.text(x + .012, y + .042, f'Predicts {audit["observed"]}  →  selects {audit["predicted_year"]}',
            fontsize=11.2, weight='bold', color=INK, va='center')
    correct = audit['correct']
    ax.text(x + width - .012, y + .042, 'Correct' if correct else 'Incorrect',
            ha='right', va='center', fontsize=10.5, weight='bold', color=GREEN if correct else RED)


def draw_examples(ax, examples):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0, 1.06, 'a', fontsize=17, weight='bold', color=INK, va='bottom')
    ax.text(.035, 1.06, 'Real prompts separate the response letter from the selected year',
            fontsize=14, weight='bold', color=INK, va='bottom')
    ax.text(.035, 1.005, 'Only the dates assigned to A and B change within each row.', fontsize=11.5, color=MUTED)
    for row, example in enumerate(examples):
        y = .525 if row == 0 else .045
        ax.text(.002, y + .354, 'Same letter,\ndifferent year' if row == 0 else 'Different letter,\nsame year',
                fontsize=14, weight='bold', color=INK, va='top', linespacing=1.3)
        ax.text(.002, y + .218, 'Question first' if row == 0 else 'Context first', fontsize=11, color=MUTED)
        ax.text(.002, y + .112, f'{example["pair"]["jaccard"]:.3f}', fontsize=25, weight='bold', color=BLUE)
        ax.text(.002, y + .060, 'Feature overlap', fontsize=10.5, color=MUTED)
        prompt_card(ax, .205, y, example['jobs'][0], example['audits'][0])
        prompt_card(ax, .630, y, example['jobs'][1], example['audits'][1], after=True)
        arrow = FancyArrowPatch((.583, y + .205), (.616, y + .205), arrowstyle='-|>',
                                mutation_scale=17, lw=1.4, color=MUTED)
        ax.add_patch(arrow)


def scatter_panel(ax, panel, rows):
    ax.set_ylim(0, 1.04)
    ax.set_xlim(-.48, 1.48)
    ax.set_yticks(np.linspace(0, 1, 6))
    ax.set_ylabel('Feature overlap (Jaccard)', fontsize=12, color=INK, labelpad=8)
    ax.tick_params(axis='both', labelsize=11, colors=INK, length=0, pad=8)
    ax.grid(axis='y', color='#E0E5E9', lw=.7, zorder=0)
    for edge in ('top', 'right'):
        ax.spines[edge].set_visible(False)
    for edge in ('left', 'bottom'):
        ax.spines[edge].set_color('#9FADB8')
        ax.spines[edge].set_linewidth(.8)
    plotted = []
    for x, matched in enumerate((True, False)):
        group = [r for r in rows if r['same_letter'] is matched]
        group.sort(key=lambda r: (list(EVENTS).index(r['event']), r['a']))
        offsets = np.linspace(-.18, .18, len(group))
        for offset, row in zip(offsets, group):
            _, color, marker = EVENTS[row['event']]
            ax.scatter(x + offset, row['jaccard'], s=105, marker=marker, facecolor=color,
                       edgecolor='white', linewidth=.7, zorder=3)
            plotted.append(dict(**row, plot_x=float(x + offset), plot_y=row['jaccard']))
        ax.text(x, .99, f'{len(group)} comparisons', ha='center', va='center', fontsize=11, color=MUTED)
    if panel == 'b':
        labels = ['Same letter\nDifferent selected year', 'Different letter\nSame selected year']
    else:
        labels = ['Same predicted\nletter', 'Different predicted\nletters']
    ax.set_xticks([0, 1], labels)
    return plotted


def caption_body():
    return (
        'Qwen3-4B attribution graphs for 16 historical-date prompts, including 11 correct and five incorrect predictions. '
        '**a,** Two real pairs asking for the year of adoption of the US Declaration of Independence. Within each row, '
        'the dates assigned to A and B are swapped while the question and context remain unchanged. When the question comes first, '
        'the model predicts A in both prompts, selecting 1776 in one and 1783 in the other; feature overlap is 0.795. '
        'When context comes first, the model changes from A to B to retain the correct year, 1776; overlap is 0.512. '
        'The exact user-prompt text is shown with added line breaks; the model chat wrapper is not shown. '
        '**b,** All eight comparisons that swap the A/B date assignments while holding the queried event and question/context order fixed. '
        'The five same-letter comparisons select different years, with one correct and one incorrect prediction per pair '
        '(Jaccard 0.795–0.911). The three different-letter comparisons retain the same correct year (0.512–0.532). '
        '**c,** All eight comparisons that reverse question/context order while holding the event and A/B date assignments fixed. '
        'Overlap is 0.766–0.808 when predictions retain the same letter and 0.527–0.602 when the letter changes. '
        'Each point represents a pair of graphs; marker shapes and colors identify the queried event. '
        'Panels b and c reuse the same 16 graphs from two event pairs. '
        'Jaccard overlap is the number of shared feature identities divided by the number present in either graph; '
        '0 means none are shared and 1 means the feature sets are identical. '
        'Feature identities exclude embeddings, output nodes, and reconstruction-error nodes. '
        'The panels report descriptive comparisons without treating graph pairs as independent replications.'
    )


def caption():
    return f'**{TITLE}.** {caption_body()}'


def main():
    result, examples, panels = load_data()
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'svg.fonttype': 'none',
                         'axes.unicode_minus': False, 'savefig.facecolor': 'white'})
    fig = plt.figure(figsize=(13, 12), facecolor='white')
    fig.text(.045, .974, TITLE, fontsize=21, weight='bold', color=INK, va='top')
    fig.text(.045, .939, 'Model tested: Qwen3-4B   |   16 prompts; 11 correct and 5 incorrect predictions',
             fontsize=12, color=MUTED)
    fig.lines.append(Line2D([.045, .955], [.922, .922], transform=fig.transFigure, color=RULE, lw=.8))
    ax_a = fig.add_axes([.045, .49, .91, .38])
    draw_examples(ax_a, examples)
    ax_b = fig.add_axes([.085, .18, .365, .235])
    ax_c = fig.add_axes([.585, .18, .365, .235])
    fig.text(.045, .461, 'b', fontsize=17, weight='bold', color=INK)
    fig.text(.085, .461, 'High overlap despite a different selected year', fontsize=12.8, weight='bold', color=INK)
    fig.text(.085, .431, 'Swap the dates assigned to A and B.\nKeep question/context order fixed.', fontsize=10.8, color=MUTED, linespacing=1.3)
    fig.text(.545, .461, 'c', fontsize=17, weight='bold', color=INK)
    fig.text(.585, .461, 'Lower overlap when the predicted letter changes', fontsize=12.8, weight='bold', color=INK)
    fig.text(.585, .431, 'Reverse the question and context.\nKeep the A/B date assignments fixed.', fontsize=10.8, color=MUTED, linespacing=1.3)
    plotted = scatter_panel(ax_b, 'b', panels['b']) + scatter_panel(ax_c, 'c', panels['c'])
    handles = [Line2D([], [], ls='', marker=marker, color=color, markersize=8, label=label)
               for label, color, marker in EVENTS.values()]
    fig.legend(handles=handles, ncol=4, loc='lower center', bbox_to_anchor=(.5, .083), frameon=False,
               fontsize=11.5, columnspacing=1.7, handletextpad=.5)
    fig.text(.5, .058, 'Each point is one pair of graphs. Panels b and c use the same 16 graphs.',
             ha='center', fontsize=10.5, color=MUTED)
    fig.text(.5, .037, 'Jaccard overlap: 0 = no shared features; 1 = identical feature sets.',
             ha='center', fontsize=10.5, color=MUTED)
    for extension in ('png', 'svg'):
        fig.savefig(OUT / f'{STEM}.{extension}', dpi=240, bbox_inches=None)
    plt.close(fig)
    with (OUT / f'{STEM}_source.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)
    example_source = [dict(group=e['group'], jaccard=e['pair']['jaccard'],
                           prompts=[dict(job_id=j['job_id'], exact_prompt=j['plain_prompt'],
                                         predicted_letter=a['observed'], selected_year=a['predicted_year'],
                                         correct=a['correct']) for j, a in zip(e['jobs'], e['audits'])]) for e in examples]
    (OUT / 'prompt_examples.json').write_text(json.dumps(example_source, indent=2), encoding='utf-8')
    legend = caption()
    (OUT / 'CAPTION.md').write_text(legend + '\n', encoding='utf-8')
    caption_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html.escape(legend))
    (OUT / 'index.html').write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{TITLE}</title><style>body{{font-family:Arial,sans-serif;margin:28px auto;max-width:1400px;padding:0 20px;color:#182b3a}}'
        'img{width:100%;height:auto}p{max-width:1000px;line-height:1.65}a{color:#0072b2}</style>'
        f'<img src="{STEM}.png" alt="Three-panel history graph figure with real prompt pairs and all option-swap and order comparisons">'
        f'<p><a href="{STEM}.svg">Editable SVG</a> · <a href="{STEM}.png">High-resolution PNG</a> · '
        f'<a href="{STEM}_source.csv">Plotted data</a> · <a href="prompt_examples.json">Exact prompt examples</a></p>'
        f'<p>{caption_html}</p></html>', encoding='utf-8')
    shutil.copy2(__file__, OUT / Path(__file__).name)
    test = ROOT / 'tests/test_history_multipanel.py'
    if test.exists():
        shutil.copy2(test, OUT / test.name)
    manifest = dict(label='7', stem=STEM, title=TITLE, legend=caption_body(), model='qwen3-4b',
                    source_results_sha256=sha(DATA / 'analysis/results.json'),
                    source_jobs_sha256=sha(DATA / 'jobs.json'), script_sha256=sha(__file__),
                    graph_count=16, wrong_graphs_included=5, panels={'a': 2, 'b': 8, 'c': 8},
                    data_changed=False, files=[dict(path=p.name, sha256=sha(p)) for p in sorted(OUT.iterdir())
                                               if p.is_file() and p.name != 'figure_manifest.json'])
    (OUT / 'figure_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Saved {OUT / (STEM + ".png")}')


if __name__ == '__main__':
    main()
