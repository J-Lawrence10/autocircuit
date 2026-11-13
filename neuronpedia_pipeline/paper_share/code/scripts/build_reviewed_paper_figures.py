"""Print-sized figures from immutable saved tables, without inference or new statistics."""
import csv
import hashlib
import json
import shutil
import textwrap
from collections import defaultdict
from pathlib import Path
from statistics import mean

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
from matplotlib.text import Text
from matplotlib.ticker import FuncFormatter
import numpy as np

from review_figure_catalog import ROOT, OUT, FIG, BASE, HISTORY, catalog

WIDTH = 180 / 25.4
INK, MUTED, GRID = '#203544', '#526774', '#D6E0E6'
BLUE, ORANGE, GREEN, PURPLE = '#0072B2', '#CC651D', '#009E73', '#A65393'
MODELS = ['Gemma-2-2B', 'Qwen3-1.7B', 'Qwen3-4B']
COLORS = dict(zip(MODELS, [BLUE, PURPLE, ORANGE]))
DOMAINS = ['chemistry', 'geography', 'history']
DC = dict(zip(DOMAINS, [BLUE, GREEN, ORANGE]))
DM = dict(zip(DOMAINS, ['o', 's', '^']))
PRIMARY = 'feature_jaccard__margin_other_factual_mean'
SOURCES, QA, USED = {}, {}, defaultdict(list)
CAT = {r['stem']: r for r in catalog()}
OVERLAP_LABEL = 'Feature overlap (%)'
DIFFERENCE_LABEL = 'Difference in feature overlap\n(percentage points)'


def percent_axis(ax, axis='y', label=None):
    """Display 100 times native Jaccard coordinates; never rescale saved data.

    Multiplying both raw overlap and its differences by 100 changes only units:
    raw overlap is percent, and subtractions are percentage points. Cosine
    metrics, counts, p-values, and quantities already in percent do not use this.
    """
    target = ax.xaxis if axis == 'x' else ax.yaxis
    target.set_major_formatter(FuncFormatter(lambda value, _: f'{100*value:g}'))
    if label:
        (ax.set_xlabel if axis == 'x' else ax.set_ylabel)(label)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    path = Path(path)
    SOURCES[path.relative_to(ROOT).as_posix()] = sha(path)
    return path


def rows(name, figure=None, directory=None):
    path = record((directory or BASE/'tables') / (name+'.csv'))
    if figure:
        USED[figure].append(name+'.csv')
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def grouped(data, key):
    out = defaultdict(list)
    for r in data:
        out[key(r)].append(r)
    return out


def model_name(value):
    return next(m for m in MODELS if m.lower() == value.lower())


def setup():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'svg.fonttype': 'none', 'font.size': 8,
        'axes.labelsize': 8, 'axes.titlesize': 9, 'xtick.labelsize': 7.5,
        'ytick.labelsize': 7.5, 'legend.fontsize': 7.5, 'axes.spines.top': False,
        'axes.spines.right': False, 'text.color': INK, 'axes.labelcolor': INK,
        'xtick.color': INK, 'ytick.color': INK, 'figure.facecolor': 'white',
        'axes.titleweight': 'bold',
    })


def title(fig, stem, subtitle=None):
    fig.suptitle(textwrap.fill(CAT[stem]['title'], 66), x=.055, y=.98,
                 ha='left', va='top', fontsize=11, weight='bold')
    if subtitle:
        fig.text(.055, .90, subtitle, fontsize=7.5, color=MUTED)


def panel(ax, letter, label):
    ax.set_title(letter+'  '+label, loc='left', pad=9, fontsize=8.5)


def zero(ax):
    ax.axhline(0, color=MUTED, ls='--', lw=.8)
    ax.grid(axis='y', color=GRID, lw=.45, alpha=.75)
    ax.set_axisbelow(True)


def ci(ax, x, row, color=INK, horizontal=False):
    value, lo, hi = [float(row[k]) for k in ('mean', 'ci_low', 'ci_high')]
    if horizontal:
        ax.errorbar(value, x, xerr=[[value-lo], [hi-value]], marker='D',
                    color=color, capsize=3, ms=5, lw=1.1, zorder=5)
    else:
        ax.errorbar(x, value, yerr=[[value-lo], [hi-value]], marker='D',
                    color=color, capsize=3, ms=5, lw=1.1, zorder=5)


def finish(fig, stem):
    title(fig, stem)
    fig.set_dpi(300)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    width, height = fig.bbox.width, fig.bbox.height
    visible = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    # Tick labels outside the selected axis limits are not drawn by Matplotlib.
    ticks = set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            low, high = sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks():
                if tick.get_loc() < low or tick.get_loc() > high:
                    ticks.update([tick.label1, tick.label2])
    visible = [t for t in visible if t not in ticks]
    minimum = min(t.get_fontsize() for t in visible)
    assert minimum >= 7.0, (stem, minimum)
    clipped = []
    for t in visible:
        b = t.get_window_extent(renderer)
        if b.x0 < -2 or b.y0 < -2 or b.x1 > width+2 or b.y1 > height+2:
            clipped.append(t.get_text())
    if clipped:
        raise AssertionError((stem, 'Text outside canvas', clipped))
    QA[stem] = dict(width_mm=180, height_mm=round(fig.get_figheight()*25.4, 1),
                    minimum_font_pt=minimum, text_outside_canvas=clipped)
    for ext in ('png', 'svg'):
        fig.savefig(FIG/f'{stem}.{ext}', dpi=300, facecolor='white')
    plt.close(fig)


def card(ax, x, y, w, h, heading, body, fill='#F0F5F8', size=7.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.008,rounding_size=.014',
                               facecolor=fill, edgecolor=GRID, lw=.7))
    ax.text(x+w/2, y+h-.035, heading, ha='center', va='top', fontsize=8,
            weight='bold', linespacing=1.2)
    ax.text(x+w/2, y+h/2-.035, body, ha='center', va='center',
            fontsize=size, linespacing=1.3)


def design():
    stem = 'figure1_design_and_coverage'
    data = rows('figure1_coverage', stem)
    counts = {m: sum(int(r['eligible_facts']) for r in data if r['model'] == m) for m in MODELS}
    assert list(counts.values()) == [8, 10, 12]
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH, 8.35))
    fig.subplots_adjust(left=.055, right=.975, top=.875, bottom=.08, wspace=.12, hspace=.15)
    for ax in axes.flat:
        ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.axis('off')
    ax = axes[0, 0]
    panel(ax, 'a', 'Reword the same fact')
    ax.text(0, .985, 'Models tested: Gemma-2-2B, Qwen3-1.7B,\nQwen3-4B', fontsize=7.5, va='top')
    ax.text(0, .875, 'Evaluation facts: '+ ' / '.join(str(counts[m]) for m in MODELS), fontsize=7.5, weight='bold')
    card(ax, .02, .665, .96, .18, 'Starting question', 'The chemical symbol for gold is')
    card(ax, .02, .445, .96, .18, 'Same fact, reworded', 'Gold has the chemical symbol')
    card(ax, .02, .225, .96, .18, 'Different fact', 'Iron has the chemical symbol')
    ax.text(.5, .18, 'Compare the starting graph with each graph.', ha='center', fontsize=7.5)
    ax.text(.5, .09, 'Invented name controls replace gold with\nzorium in the starting or reworded prompt.', ha='center', fontsize=7.5)
    ax = axes[0, 1]
    panel(ax, 'b', 'Change the answer letter')
    ax.text(0, .985, 'Model tested: Qwen3-4B\nSix country pairs; 48 correct predictions', fontsize=7.5, va='top')
    card(ax, .02, .57, .96, .28, 'Same factual question', 'France’s capital?\nA: Paris. B: Berlin.\nCorrect response: A')
    card(ax, .02, .22, .96, .28, 'Swap the answer labels', 'France’s capital?\nA: Berlin. B: Paris.\nCorrect response: B')
    ax.annotate('', (.5, .51), (.5, .565), arrowprops=dict(arrowstyle='->', color=MUTED))
    ax.text(.5, .12, 'Also compare different queried countries.\nWord and token counts stay the same\nwithin each complete country-pair design.', ha='center', va='center', fontsize=7.5)
    ax = axes[1, 0]
    panel(ax, 'c', 'Examine selected errors')
    ax.text(0, .985, 'Model tested: Qwen3-4B\nOne country pair; 16 graphs', fontsize=7.5, va='top')
    card(ax, .02, .54, .96, .31, 'Position-based question', 'Return the capital name.\nCountries: France, Germany. A: Berlin. B: Paris.\nCapital of the first country, not the second?\nPredicted capital: Berlin (incorrect)', fill='#FFF2E7')
    card(ax, .02, .285, .96, .20, 'Correct answer for the intended country', 'France → Paris')
    card(ax, .02, .035, .96, .20, 'Same answer in a correct context', 'Germany → Berlin')
    ax = axes[1, 1]
    panel(ax, 'd', 'Distinguish letters from years')
    ax.text(0, .985, 'Model tested: Qwen3-4B\nTwo event pairs; 16 graphs (11 correct)', fontsize=7.5, va='top')
    card(ax, .02, .55, .96, .30, 'Declaration of Independence adopted?', 'A: 1776. B: 1783.\nPredicts A → selects 1776\nCorrect', fill='#EFF7F3')
    card(ax, .02, .19, .96, .30, 'Swap the dates', 'A: 1783. B: 1776.\nPredicts A → selects 1783\nIncorrect', fill='#FFF2E7')
    ax.annotate('', (.5, .50), (.5, .545), arrowprops=dict(arrowstyle='->', color=MUTED))
    ax.text(.5, .09, 'Same letter, different year.\nAlso reverse question/context order.', ha='center', va='center', fontsize=7.5)
    fig.text(.055, .035, 'Prompts are abridged examples. Panel a uses development facts; panel b uses an excluded pilot pair.\nPanel c shows a selected error. Panel d uses a real history comparison. Full definitions are in the caption.', fontsize=7)
    finish(fig, stem)


def primary():
    stem = 'figure2_fact_signal'
    data, summaries, domains = [rows(n, stem) for n in ('figure2_fact_level', 'figure2_summary', 'figure2_domain_summary')]
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 4.7))
    fig.subplots_adjust(left=.09, right=.985, top=.78, bottom=.26, wspace=.32)
    for i, m in enumerate(MODELS):
        subset = [r for r in data if r['model'] == m]
        for x, r in zip(np.linspace(i-.16, i+.16, len(subset)), subset):
            axes[0].scatter(x, float(r[PRIMARY]), color=DC[r['domain']], marker=DM[r['domain']], s=23)
        stat = next(r for r in summaries if r['model'] == m)
        ci(axes[0], i, stat)
        axes[0].text(i, .69, f'n={stat["n"]}\n{100*float(stat["mean"]):.2f} pp', ha='center', va='top', fontsize=7.5)
        for j, d in enumerate(DOMAINS):
            found = [r for r in domains if r['model'] == m and r['domain'] == d]
            if not found:
                continue
            r, x = found[0], i+(j-1)*.21
            if r['ci_low']:
                ci(axes[1], x, r, DC[d])
                y = float(r['ci_high'])
            else:
                y = float(r['mean'])
                axes[1].scatter(x, y, marker='D', color=DC[d], s=24)
            axes[1].annotate('n='+r['n'], (x, y), xytext=(0, 7), textcoords='offset points', ha='center', fontsize=7)
    for ax in axes:
        zero(ax)
        ax.set(xticks=range(3), xticklabels=['Gemma\n2-2B', 'Qwen3\n1.7B', 'Qwen3\n4B'], ylim=(-.025, .73))
        percent_axis(ax, label=DIFFERENCE_LABEL)
    panel(axes[0], 'a', 'Each evaluation fact')
    panel(axes[1], 'b', 'Average by subject')
    fig.text(.09, .86, 'Same-fact minus other-fact overlap; pp = percentage points.', fontsize=7.5)
    handles = [Line2D([], [], color=DC[d], marker=DM[d], ls='', label=d.title()) for d in DOMAINS]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .09), ncol=3, frameon=False)
    fig.text(.09, .055, 'Diamonds: means. Bars: descriptive 95% intervals. Qwen3-4B history: two dependent facts,\nshown without a subject interval. Unavailable groups are not zero effects.', fontsize=7)
    finish(fig, stem)


def controls():
    stem = 'figure3_control_comparisons'
    stats, data = rows('figure4_controls', stem), rows('figure2_fact_level', stem)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 4.5))
    fig.subplots_adjust(left=.10, right=.985, bottom=.22, top=.77, wspace=.33)
    for ax, control, flag, label in zip(axes, ['same_template_nonce', 'paraphrased_nonce'],
            ['same_template_output_type_matches_target', 'nonce_output_type_matches_target'],
            ['Original wording', 'Reworded question']):
        for i, m in enumerate(MODELS):
            subset = [r for r in data if r['model'] == m and r[flag] == 'True']
            ax.scatter(np.linspace(i-.16, i+.16, len(subset)), [float(r['feature_jaccard__margin_'+control]) for r in subset],
                       color=COLORS[m], s=20, alpha=.7)
            r = next(r for r in stats if r['model'] == m and r['control'] == control)
            ci(ax, i, r, COLORS[m])
            ax.text(i, .295, 'n='+r['n'], ha='center', fontsize=7.5)
        zero(ax)
        ax.set(xticks=range(3), xticklabels=['Gemma\n2-2B', 'Qwen3\n1.7B', 'Qwen3\n4B'], ylim=(-.12, .33), xlim=(-.4, 2.4))
        percent_axis(ax, label=DIFFERENCE_LABEL)
        panel(ax, 'a' if ax is axes[0] else 'b', label)
    fig.text(.10, .10, 'Above zero: greater overlap with the factual rewording. Diamonds: means; bars: 95% intervals.\nControls match broad next-token type, not the exact answer. Samples differ by comparison.', fontsize=7)
    finish(fig, stem)


def matched():
    stem = 'figure4_matched_choice'
    data = rows('figure5_block_contrasts', stem)
    primary_result = json.loads(record(ROOT/'data/model_extension/matched_choice_chat_v2/qwen3-4b/analysis/results.json').read_text(encoding='utf-8'))['primary']
    (FIG/'tables/matched_choice_primary.json').write_text(json.dumps(primary_result, indent=2), encoding='utf-8')
    USED[stem].append('matched_choice_primary.json')
    fig = plt.figure(figsize=(WIDTH, 6.0))
    gs = fig.add_gridspec(2, 2, left=.10, right=.98, top=.81, bottom=.17, hspace=.55, wspace=.40)
    a, info, b, c = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    matrix = np.array([[mean(float(r[k]) for r in data) for k in ('SS', 'SD')],
                       [mean(float(r[k]) for r in data) for k in ('DS', 'DD')]])
    im = a.imshow(matrix, vmin=0, vmax=1, cmap='Blues', aspect='auto')
    for i in range(2):
        for j in range(2):
            a.text(j, i, f'{100*matrix[i,j]:.2f}%', ha='center', va='center', fontsize=10,
                   color='white' if matrix[i,j]>.65 else INK, weight='bold')
    a.set(xticks=[0, 1], xticklabels=['Same letter', 'Different letter'], yticks=[0, 1], yticklabels=['Same\ncountry', 'Different\ncountries'])
    panel(a, 'a', 'Feature overlap in each comparison')
    cb = fig.colorbar(im, ax=a, orientation='horizontal', pad=.24, fraction=.09, ticks=[0, .5, 1])
    cb.ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f'{100*value:g}'))
    cb.set_label('Feature overlap (%): 0 = none; 100 = identical sets', fontsize=7)
    info.axis('off')
    info.text(0, .98, 'Model tested: Qwen3-4B', va='top', weight='bold', fontsize=9)
    info.text(0, .77, 'Six country pairs\n48 / 48 correct A/B predictions\n\nSame word and token counts\nwithin each country pair.\n\nCompare different wordings\nin all four conditions.', va='top', fontsize=8, linespacing=1.4)
    for r in data:
        b.plot([0, 1], [float(r['fact_same_label']), float(r['fact_different_label'])], color='#9BAFBB', lw=.8, alpha=.8)
        c.plot([0, 1], [float(r['fact_effect']), float(r['label_effect'])], color='#9BAFBB', lw=.8, alpha=.8)
    for ax, keys in [(b, ['fact_same_label', 'fact_different_label']), (c, ['fact_effect', 'label_effect'])]:
        for i, k in enumerate(keys):
            values = [float(r[k]) for r in data]
            ax.scatter(np.linspace(i-.07, i+.07, len(values)), values, color=[BLUE, ORANGE][i], s=20, zorder=3)
            v = mean(values)
            ax.scatter(i, v, color=INK, marker='D', s=30, zorder=4)
            ax.annotate(f'{100*v:.2f} pp', (i, v), xytext=(0, 12), textcoords='offset points', ha='center', fontsize=8, weight='bold')
        zero(ax)
        ax.set_xlim(-.35, 1.35)
        percent_axis(ax, label=DIFFERENCE_LABEL)
    b.set(xticks=[0, 1], xticklabels=['Same answer\nletter', 'Different answer\nletters'], ylim=(-.015, .10))
    c.set(xticks=[0, 1], xticklabels=['Average same-country\noverlap difference', 'Average same-letter\noverlap difference'], ylim=(-.01, .35))
    assert abs(primary_result['mean_fact_effect']-mean(float(r['fact_effect']) for r in data)) < 1e-12
    ci(c, 0, dict(mean=primary_result['mean_fact_effect'], ci_low=primary_result['ci95'][0], ci_high=primary_result['ci95'][1]))
    panel(b, 'b', 'Same-country minus other-country')
    panel(c, 'c', 'Average country and letter contrasts')
    fig.text(.10, .055, 'Each line: one country pair. Diamonds: means. Only the primary country mean in c has a 95% interval.\nPanels b and c use different scales; pp = percentage points, not accuracy or variance explained.', fontsize=7)
    finish(fig, stem)


def failures():
    stem = 'figure5_failure_cases'
    data, behavior = rows('figure6_comparisons', stem), rows('figure6_behavior', stem)
    fig = plt.figure(figsize=(WIDTH, 6.0))
    gs = fig.add_gridspec(2, 2, left=.10, right=.98, top=.81, bottom=.20, hspace=.55, wspace=.33)
    a, note, b, c = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]
    for j, fmt in enumerate(['label', 'capital']):
        subset = [r for r in behavior if r['response_format'] == fmt]
        for i, ref in enumerate(['named', 'ordinal']):
            r = next((r for r in subset if r['reference'] == ref), None)
            if r is None:
                r = next(r for r in subset if r['reference'] != 'named')
            x, v = i+(j-.5)*.27, int(r['correct'])
            a.bar(x, v, width=.25, color=[BLUE, GREEN][j])
            a.text(x, v+.12, f'{v}/{r["n"]}', ha='center', fontsize=7.5)
    a.set(xticks=[0, 1], xticklabels=['Country named', 'Position named'], ylim=(0, 4.8), yticks=range(5), ylabel='Correct next-token predictions')
    panel(a, 'a', 'Selected questions')
    a.legend(handles=[Line2D([], [], marker='s', ls='', color=BLUE, label='A/B'), Line2D([], [], marker='s', ls='', color=GREEN, label='Capital name')], frameon=False)
    note.axis('off')
    note.text(0, .98, 'Model tested: Qwen3-4B\nOne country pair; 16 graphs', va='top', fontsize=8.5, weight='bold')
    note.text(0, .69, 'Selected error: France → Berlin\nCorrect intended answer: France → Paris\nCorrect same response: Germany → Berlin\n\nCompare each error graph with\nboth correct-answer graphs.', va='top', fontsize=7.5, linespacing=1.5)
    for ax, fmt, letter, name in [(b, 'label', 'b', 'A/B responses'), (c, 'capital', 'c', 'Capital-name responses')]:
        cases = grouped([r for r in data if r['format'] == fmt], lambda r: r['case'])
        for i, pair in enumerate(cases.values()):
            pair = sorted(pair, key=lambda r: r['comparator'] != 'same_country')
            ax.plot([i-.12, i+.12], [float(r['jaccard']) for r in pair], color='#9BAFBB', lw=1)
            for j, r in enumerate(pair):
                ax.scatter(i+(j-.5)*.24, float(r['jaccard']), s=24, color=[BLUE, ORANGE][j])
                ax.scatter(i+(j-.5)*.24, float(r['equal_count']), s=24, marker='s', facecolors='white', edgecolors=[BLUE, ORANGE][j])
        ax.set(ylim=(0, 1), xticks=range(4), xticklabels=['France\nfirst', 'France\nsecond', 'Germany\nfirst', 'Germany\nsecond'])
        percent_axis(ax, label=OVERLAP_LABEL)
        ax.grid(axis='y', color=GRID, lw=.5)
        panel(ax, letter, name)
    handles = [Line2D([], [], marker='o', color=BLUE, ls='', label='Correct answer for the intended country'),
               Line2D([], [], marker='o', color=ORANGE, ls='', label='Correct prediction giving the same response'),
               Line2D([], [], marker='s', markerfacecolor='white', color=INK, ls='', label='Equal feature counts')]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .025), frameon=False, ncol=1)
    finish(fig, stem)


def history():
    stem = 'figure6_history_answers'
    data = rows('figure7_history_answers_source', stem, HISTORY)
    examples = json.loads(record(HISTORY/'prompt_examples.json').read_text(encoding='utf-8'))
    fig = plt.figure(figsize=(WIDTH, 8.6))
    a = fig.add_axes([.055, .39, .92, .45])
    a.axis('off')
    fig.text(.055, .875, 'a  Real prompts separate the letter from the selected year', fontsize=8.5, weight='bold')
    for i, example in enumerate(examples):
        y = .55 if i == 0 else .02
        a.text(0, y+.47, f'{example["group"]}  |  Feature overlap {100*example["jaccard"]:.1f}%', fontsize=8, weight='bold')
        for j, prompt in enumerate(example['prompts']):
            x = .01 if j == 0 else .53
            a.add_patch(FancyBboxPatch((x, y), .45, .43, boxstyle='round,pad=.008', facecolor='#F3F7FA', edgecolor=GRID))
            text = textwrap.fill(prompt['exact_prompt'], 45)
            a.text(x+.02, y+.405, text, fontsize=7.5, va='top', linespacing=1.25)
            status = 'Correct' if prompt['correct'] else 'Incorrect'
            a.text(x+.02, y+.035, f'Predicts {prompt["predicted_letter"]} → selects {prompt["selected_year"]}\n{status}', fontsize=7.5, weight='bold',
                   color=GREEN if prompt['correct'] else '#B62E41', va='bottom')
        a.annotate('', (.52, y+.22), (.47, y+.22), arrowprops=dict(arrowstyle='->', color=MUTED))
    b, c = fig.add_axes([.10, .13, .37, .22]), fig.add_axes([.60, .13, .37, .22])
    events = ['Declaration of Independence', 'Treaty of Paris', 'Sputnik 1', 'Explorer 1']
    styles = dict(zip(events, [(BLUE, 'o'), (BLUE, 's'), (ORANGE, 'D'), (ORANGE, '^')]))
    for ax, name, letter, heading in [(b, 'b', 'b', 'Swap A/B date assignments'), (c, 'c', 'c', 'Reverse question/context order')]:
        subset = [r for r in data if r['panel'] == name]
        for r in subset:
            color, marker = styles[r['event_label']]
            ax.scatter(float(r['plot_x']), float(r['jaccard']), color=color, marker=marker, s=28)
        ax.set(xticks=[0, 1], xlim=(-.35, 1.35), ylim=(0, 1.05))
        percent_axis(ax, label=OVERLAP_LABEL)
        labels = ['Same letter\nDifferent year', 'Different letter\nSame year'] if name == 'b' else ['Same predicted\nletter', 'Different predicted\nletters']
        ax.set_xticklabels(labels)
        ax.grid(axis='y', color=GRID, lw=.5)
        for x, n in [(0, 5), (1, 3)]:
            ax.text(x, .98, f'n={n}', ha='center', fontsize=7.5)
        panel(ax, letter, heading)
    handles = [Line2D([], [], marker=m, color=c, ls='', label=e) for e, (c, m) in styles.items()]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .02), frameon=False, ncol=2)
    fig.text(.055, .91, 'Model tested: Qwen3-4B. All 16 graphs included: 11 correct and 5 incorrect predictions.', fontsize=7.5)
    finish(fig, stem)


def quality():
    stem = 'figureS1_export_and_error'
    stats, data = rows('figureS1_quality', stem), rows('figureS1_influence_values', stem)
    labels = ['Gemma\n2-2B\nControls', 'Qwen3\n1.7B\nControls', 'Gemma\n2-2B\nVersions', 'Qwen3\n4B\nControls', 'Qwen3\n4B\nVersions']
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 4.6))
    fig.subplots_adjust(left=.08, right=.985, bottom=.23, top=.77, wspace=.33)
    for i, r in enumerate(stats):
        v = 100*int(r['ambiguous_raw_exports'])/int(r['graphs'])
        axes[0].bar(i, v, color=BLUE)
        axes[0].text(i, v+2.5, f'{r["ambiguous_raw_exports"]}/{r["graphs"]}', ha='center', fontsize=7)
    axes[0].set(ylim=(0, 85), ylabel='Files with conflicting node IDs (%)')
    values = [[float(v['error_influence_percent']) for v in data if v['cohort'] == r['cohort']] for r in stats]
    axes[1].boxplot(values, positions=range(5), widths=.6, flierprops=dict(marker='.', markersize=2))
    axes[1].set_ylabel('Reconstruction-error influence (%)')
    for ax in axes:
        ax.set_xticks(range(5), labels)
        ax.tick_params(axis='x', labelsize=7)
    panel(axes[0], 'a', 'Conflicting node identities')
    panel(axes[1], 'b', 'Approximation-error contribution')
    fig.text(.08, .055, 'Controls: factual questions and invented names. Versions: the question-version comparison.\nZero conflicts means none detected, not zero graphs. Approximation error is not an answer-error rate.\nEach set retains its own denominator and audit definition.', fontsize=7)
    finish(fig, stem)


def robustness():
    stem = 'figureS2_robustness'
    data = rows('figureS2_robustness', stem)
    names = ['Primary', 'Errors included', 'Clean exports', 'Hardest other fact']
    labels = ['Main\nanalysis', 'Include\nerror nodes', 'Clean\nexports', 'Most similar\nother fact']
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 4.25), sharey=True)
    fig.subplots_adjust(left=.09, right=.98, bottom=.28, top=.74, wspace=.22)
    for ax, m in zip(axes, MODELS):
        for i, name in enumerate(names):
            r = next(r for r in data if r['model'] == m and r['sensitivity'] == name)
            ci(ax, i, r, COLORS[m])
            ax.annotate('n='+r['n'], (i, float(r['ci_high'])), xytext=(0, 7), textcoords='offset points', ha='center', fontsize=7)
        ax.set_title(m, fontsize=8.5)
        ax.set(xticks=range(4), xticklabels=labels, ylim=(-.025, .365), xlim=(-.5, 3.5))
        ax.tick_params(axis='x', labelsize=7, rotation=30)
        zero(ax)
        percent_axis(ax)
    axes[0].set_ylabel(DIFFERENCE_LABEL)
    fig.text(.09, .07, 'Diamonds: means. Bars: descriptive 95% question-bootstrap intervals.\nThe clean-export Gemma comparison contains only two facts.', fontsize=7)
    finish(fig, stem)


def equal_counts():
    stem = 'figureS3_equal_feature_counts'
    data, stats = rows('figureS3_per_fact', stem), rows('figureS3_equal_counts', stem)
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 4.2), sharey=True)
    fig.subplots_adjust(left=.09, right=.98, bottom=.25, top=.75, wspace=.23)
    for ax, m in zip(axes, MODELS):
        subset = [r for r in data if model_name(r['model']) == m]
        for r in subset:
            ax.plot(range(3), [float(r[k]) for k in ['full_set', 'equal_count', 'half_count']], color=COLORS[m], alpha=.45, lw=.8, marker='o', ms=2.5)
        for i, k in enumerate(['full_set', 'equal_count', 'half_count']):
            r = next(r for r in stats if model_name(r['model']) == m and r['comparison'] == k)
            ci(ax, i, r)
            ax.text(i, .67, f'{100*float(r["mean"]):.1f} pp', ha='center', fontsize=7)
        ax.set_title(f'{m} (n={len(subset)})', fontsize=8)
        ax.set(xticks=range(3), xticklabels=['Full\nset', 'Equal\ncounts K', 'Half\ncounts K/2'], ylim=(-.045, .71), xlim=(-.35, 2.35))
        zero(ax)
        percent_axis(ax)
    axes[0].set_ylabel(DIFFERENCE_LABEL)
    fig.text(.09, .075, 'Lines: individual facts. Diamonds: means. Bars: descriptive 95% intervals; pp = percentage points.\nEach subsampled value averages 200 draws; these draws are not additional observations.', fontsize=7)
    finish(fig, stem)


def lexical():
    stem = 'figureS4_lexical_support'
    data = rows('figureS4_lexical_scatter', stem)
    rows('figureS4_lexical_support', stem)
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 4.15), sharex=True, sharey=True)
    fig.subplots_adjust(left=.09, right=.98, bottom=.28, top=.73, wspace=.20)
    for ax, m in zip(axes, MODELS):
        a = [r for r in data if model_name(r['model']) == m]
        ax.scatter([float(r['own_word_overlap']) for r in a], [float(r['best_other_word_overlap']) for r in a], color=COLORS[m], s=24, alpha=.65)
        x = np.linspace(0, 1, 100)
        ax.plot(x, x, ls='--', color=MUTED, lw=.8)
        ax.fill_between(x, x-.05, x+.05, color=GRID, alpha=.7)
        ax.set(xlim=(0, 1), ylim=(0, 1))
        percent_axis(ax, 'x', 'Word overlap with\nsame-fact rewording (%)')
        percent_axis(ax)
        ax.set_title(f'{m}\n0/{len(a)} have a matched control', fontsize=8)
    axes[0].set_ylabel('Highest word overlap\nwith another fact (%)')
    fig.text(.09, .08, 'Axes: word-set Jaccard as percent. Band: within 5 percentage points of equal overlap.\nPoints may overlap. No qualifying match is available; this is not a measured zero feature-overlap effect.', fontsize=7)
    finish(fig, stem)


def answers():
    stem = 'figureS5_answer_audit'
    data = rows('figureS5_answer_audit', stem)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 4.7))
    fig.subplots_adjust(left=.08, right=.92, bottom=.30, top=.76, wspace=.54)
    keys = ['whole_answer_next_token', 'multi_token_prefix_only', 'mismatch']
    colors = [GREEN, '#E69F00', '#8D97A3']
    for i, m in enumerate(MODELS[1:]):
        subset = [r for r in data if model_name(r['model']) == m]
        bottom = 0
        for j, key in enumerate(keys):
            r = next((r for r in subset if r['category'] == key), None)
            if r is None:
                r = next(r for r in subset if r['category'] not in keys[:2])
            n = int(r['count'])
            axes[0].bar(i, n, bottom=bottom, color=colors[j], width=.55)
            axes[0].text(i, bottom+n/2, str(n), ha='center', va='center', fontsize=8)
            bottom += n
        axes[0].text(i, bottom+2, f'n={bottom}', ha='center', fontsize=7.5)
    axes[0].set(xticks=[0, 1], xticklabels=MODELS[1:], ylabel='Factual-question graphs checked', ylim=(0, 67))
    # Frozen exact-token counts from the crossed-output audit, separate from accepted-spelling totals.
    audit = json.loads(record(ROOT/'data/model_extension/exploratory_20260905/results.json').read_text(encoding='utf-8'))
    support = audit['crossed_output_support']
    expected = np.array([[next(r['strict_match_n'] for r in support
                               if model_name(r['model']) == m and r['domain'] == d)
                          for d in DOMAINS] for m in [MODELS[0], MODELS[2]]])
    assert all(r['graphs'] == 9 for r in support)
    USED[stem].append('figureS5_crossed_expected_tokens.csv')
    out = FIG/'tables/figureS5_crossed_expected_tokens.csv'
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['model', 'domain', 'matching', 'total'])
        w.writeheader()
        for i, m in enumerate([MODELS[0], MODELS[2]]):
            for j, d in enumerate(DOMAINS):
                w.writerow(dict(model=m, domain=d, matching=int(expected[i,j]), total=9))
    im = axes[1].imshow(expected, vmin=0, vmax=9, cmap='Blues', aspect='auto')
    for i in range(2):
        for j in range(3):
            axes[1].text(j, i, f'{expected[i,j]}/9', ha='center', va='center', fontsize=9, color='white' if expected[i,j]>5 else INK)
    axes[1].set(xticks=range(3), xticklabels=['Chemistry', 'Geography', 'History'], yticks=[0,1], yticklabels=[MODELS[0], MODELS[2]])
    cb = fig.colorbar(im, ax=axes[1], fraction=.05, pad=.04, ticks=[0,3,6,9])
    cb.set_label('Exact token matches / 9', fontsize=7)
    panel(axes[0], 'a', 'Complete answers and partial tokens')
    panel(axes[1], 'b', 'Question-version set')
    labels = ['Complete accepted answer in the first token', 'Compatible beginning; whole answer unverified', 'Other first token']
    fig.legend(handles=[Line2D([],[], marker='s', color=c, ls='', label=l) for c,l in zip(colors,labels)], loc='lower center', bbox_to_anchor=(.5,.035), frameon=False)
    finish(fig, stem)


def location():
    stem = 'figureS6_graph_location_sensitivity'
    path = ROOT/'data/model_extension/final_closeout_20261005'
    matched_data, failed = [rows(n, stem, path) for n in ('matched_choice_sensitivity', 'failure_sensitivity')]
    record(path/'statistics_audit.json')
    USED[stem].append('statistics_audit.json')
    variants = ['full', 'exclude_final_position', 'exclude_last_quarter_layers', 'exclude_both']
    labels = ['All\nfeatures', 'Remove last\ntoken position', 'Remove last\nquarter\nof layers', 'Remove\nboth']
    fig, axes = plt.subplots(1,2, figsize=(WIDTH,4.4))
    fig.subplots_adjust(left=.10, right=.98, top=.75, bottom=.25, wspace=.34)
    matched_data = [r for r in matched_data if r['metric']=='jaccard' and r['status']=='ok']
    for block, a in grouped(matched_data, lambda r:r['block']).items():
        axes[0].plot(range(4), [float(next(r for r in a if r['variant']==v)['label_condition_difference']) for v in variants], color=BLUE, alpha=.45, marker='o', ms=2.5, lw=.8)
    axes[0].scatter(range(4), [mean(float(r['label_condition_difference']) for r in matched_data if r['variant']==v) for v in variants], color=INK, marker='D', s=24)
    for fmt,color in [('label',BLUE),('capital',ORANGE)]:
        a=[r for r in failed if r['response_format']==fmt]
        for _, group in grouped(a,lambda r:r['job_id']).items():
            axes[1].plot(range(4),[float(next(r for r in group if r['variant']==v)['output_minus_country']) for v in variants],color=color,alpha=.45,marker='o',ms=2.5,lw=.8)
        axes[1].scatter(range(4),[mean(float(r['output_minus_country']) for r in a if r['variant']==v) for v in variants],color=color,marker='D',s=24)
    for ax in axes:
        ax.set_xticks(range(4),labels)
        ax.tick_params(axis='x', labelsize=7)
        zero(ax)
        percent_axis(ax, label=DIFFERENCE_LABEL)
    panel(axes[0],'a','Answer-letter difference remains')
    panel(axes[1],'b','Same-response overlap remains higher')
    fig.legend(handles=[Line2D([],[],color=BLUE,marker='o',label='A/B responses'),Line2D([],[],color=ORANGE,marker='o',label='Capital names')],loc='lower center',bbox_to_anchor=(.65,.06),frameon=False,ncol=2)
    fig.text(.10,.025,'Filters change saved graphs, not the model. Lines: blocks or selected comparisons; diamonds: means.',fontsize=7)
    finish(fig,stem)


def completion():
    stem='figureS7_qwen17_completion'
    collection, stats, data=[rows(n,stem) for n in ('figureS7_collection','figureS7_domain_summary','figureS7_per_fact')]
    fig,axes=plt.subplots(1,2,figsize=(WIDTH,4.4))
    fig.subplots_adjust(left=.13,right=.98,top=.76,bottom=.23,wspace=.37)
    for i,d in enumerate(DOMAINS):
        r=next(r for r in collection if r['domain']==d)
        axes[0].barh(i,int(r['available_graphs']),color=DC[d],height=.5)
        axes[0].text(int(r['available_graphs'])+1,i,f'{r["available_graphs"]}/{r["planned_graphs"]}',va='center',fontsize=7.5)
        a=[r for r in data if r['domain']==d]
        if a:
            axes[1].scatter([float(r['margin']) for r in a],np.linspace(i-.12,i+.12,len(a)),color=DC[d],s=22)
            stat=next(r for r in stats if r['domain']==d)
            ci(axes[1],i,dict(mean=stat['mean'],ci_low=stat['ci95_low'],ci_high=stat['ci95_high']),horizontal=True)
        else:
            axes[1].text(.003,i,'No complete question/control sets\nNo overlap estimate',va='center',fontsize=7,color=MUTED)
    for ax in axes:
        ax.set(yticks=range(3),yticklabels=[d.title() for d in DOMAINS],ylim=(2.5,-.5))
    axes[0].set(xlim=(0,50),xlabel='Available raw graphs')
    axes[1].set_xlim(-.005,.13)
    percent_axis(axes[1], 'x', DIFFERENCE_LABEL)
    axes[1].axvline(0,color=MUTED,ls='--',lw=.8)
    panel(axes[0],'a','Collection by subject')
    panel(axes[1],'b','Five facts per included subject')
    fig.text(.13,.065,'91 graphs total. The 29 missing history jobs exceeded the hosted input limit, not an accuracy test.\nDiamonds: means; bars: descriptive 95% intervals. Missing history is not a zero effect.',fontsize=7)
    finish(fig,stem)


def workflow():
    stem='figureS8_feature_overlap_workflow'
    fig,axes=plt.subplots(3,2,figsize=(WIDTH,7.2))
    fig.subplots_adjust(left=.055,right=.975,top=.87,bottom=.10,hspace=.18,wspace=.10)
    contents=[
        ('1  Prepare four prompt roles','Starting factual question\nSame fact, reworded\nInvented name, starting wording\nInvented name, reworded\n\nGold and zorium are development examples.'),
        ('2  Export attribution graphs','Neuronpedia runs the model remotely.\nSave raw graphs, settings, and checksums.\n\nNo local model inference.'),
        ('3  Apply inclusion rules','All four graphs available.\nBoth factual top next tokens give\na complete accepted answer.\nAnother included fact is available\nin the same model, subject, and set.\nRegistered spellings are accepted.'),
        ('4  Keep unique learned features','Identity = family + layer + feature ID.\nCollapse repeated token positions.\nKeep layers distinct.\n\nOmit embeddings, output/error nodes,\nand missing or duplicated node IDs.'),
        ('5  Calculate one difference per fact','Jaccard = shared / all distinct features.\nMultiply by 100 to show percent.\nCompare the starting question with its\nown rewording, then average overlap with\nALL other included factual rewordings.\nSubtract to get percentage points.'),
        ('6  Summarize across facts','Illustrative feature sets:\n{a, b, c} and {a, b, d} → 2 / 4 = 50%.\nIllustrative other-fact mean = 30%.\nDifference: 50% − 30% = +20 pp.\npp = percentage points.\nMeans, descriptive bootstrap intervals,\nand within-subject permutations.')]
    for ax,(heading,body) in zip(axes.flat,contents):
        ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
        card(ax,.025,.04,.95,.88,heading,body,size=7.5)
    fig.text(.055,.045,'Examples and scores are illustrative, not measured results. Invented name controls form a separate\ncomparison, not the other-fact baseline. Facts are the summary units, not graph pairs or subsampling draws.',fontsize=7)
    finish(fig,stem)


def history_facts():
    stem='figureS9_answer_spelling'
    data, samples=rows('figureS9_history_comparisons',stem),rows('figureS9_history_equal_counts',stem)
    facts=['columbus_americas','wwi_start'];labels=['Columbus’s\nflagship','Franz\nFerdinand']
    fig,axes=plt.subplots(1,2,figsize=(WIDTH,4.7))
    fig.subplots_adjust(left=.15,right=.98,top=.75,bottom=.28,wspace=.38)
    for i,fact in enumerate(facts):
        subset=[r for r in data if r['fact']==fact]
        own=float(next(r for r in subset if r['comparison']=='same_fact')['jaccard'])
        other=float(next(r for r in subset if r['comparison']!='same_fact')['jaccard'])
        axes[0].plot([other,own],[i,i],color='#AAB5BD',lw=1.2)
        for val,col,marker,offset in [(own,BLUE,'o',9),(other,ORANGE,'s',-16)]:
            axes[0].scatter(val,i,color=col,marker=marker,s=25)
            axes[0].annotate(f'{100*val:.1f}%',(val,i),xytext=(0 if marker=='o' else 10,offset),textcoords='offset points',ha='center' if marker=='o' else 'left',fontsize=7)
        for j,(name,col,marker) in enumerate([('Full set',INK,'o'),('Equal count (K)',BLUE,'s'),('Half count (K/2)',GREEN,'^')]):
            val=float(next(r for r in samples if r['fact']==fact and r['comparison']==name)['margin'])
            axes[1].scatter(i+(j-1)*.16,val,color=col,marker=marker,s=27,label=name if i==0 else None)
    axes[0].set(yticks=[0,1],yticklabels=labels,ylim=(1.5,-.5),xlim=(0,1))
    percent_axis(axes[0], 'x', OVERLAP_LABEL)
    axes[1].set(xticks=[0,1],xticklabels=labels,ylim=(-.025,.67),xlim=(-.4,1.4))
    percent_axis(axes[1], label=DIFFERENCE_LABEL)
    zero(axes[1])
    panel(axes[0],'a','Same-fact and other-fact overlap')
    panel(axes[1],'b','Equal-feature-count check')
    axes[0].legend(handles=[Line2D([],[],color=BLUE,marker='o',ls='',label='Same fact, reworded'),Line2D([],[],color=ORANGE,marker='s',ls='',label='Other history fact')],loc='upper left',bbox_to_anchor=(-.12,-.20),frameon=False)
    axes[1].legend(loc='upper left',bbox_to_anchor=(-.04,-.20),frameon=False)
    fig.text(.08,.025,'Qwen3-4B: two facts that use each other as comparators. Maria and María name the same flagship.',fontsize=7)
    finish(fig,stem)


def versions():
    stem='figureS10_fact_and_wording'
    data=rows('figure3_crossed_effects',stem)
    fig,axes=plt.subplots(1,2,figsize=(WIDTH,4.7))
    fig.subplots_adjust(left=.095,right=.98,top=.74,bottom=.29,wspace=.34)
    for ax,metric,letter,heading in [(axes[0],'feature_jaccard','a','Feature-set overlap'),(axes[1],'feature_influence_cosine','b','Influence-weighted similarity')]:
        for mi,m in enumerate([MODELS[0],MODELS[2]]):
            means=[]
            for j,effect in enumerate(['fact','format']):
                a=[r for r in data if r['model']==m and r['metric']==metric and r['effect']==effect]
                x=mi*3+j
                for r in a:
                    ax.scatter(x,float(r['effect_value']),color=DC[r['domain']],marker=DM[r['domain']],s=23)
                v=mean(float(r['effect_value']) for r in a);means.append(v)
                ax.scatter(x,v,color=INK,marker='D',s=25)
            ax.plot([mi*3,mi*3+1],means,color=INK,lw=.8)
        ax.set(xticks=[0,1,3,4],xticklabels=['Same\nfact','Same\nversion label','Same\nfact','Same\nversion label'],xlim=(-.4,4.4))
        if metric == 'feature_jaccard':
            percent_axis(ax, label=DIFFERENCE_LABEL)
        else:
            ax.set_ylabel('Difference in cosine similarity\n(native units)')
        zero(ax);panel(ax,letter,heading)
        ax.text(.2,-.28,'Gemma-2-2B',transform=ax.transAxes,ha='center',fontsize=7.5)
        ax.text(.8,-.28,'Qwen3-4B',transform=ax.transAxes,ha='center',fontsize=7.5)
    fig.legend(handles=[Line2D([],[],color=DC[d],marker=DM[d],ls='',label=d.title()) for d in DOMAINS],loc='lower center',bbox_to_anchor=(.5,.045),ncol=3,frameon=False)
    fig.text(.095,.83,'Version labels are original, alternative 1, and alternative 2. They do not hold wording constant.',fontsize=7.5)
    finish(fig,stem)


def main():
    FIG.mkdir(parents=True,exist_ok=True);(FIG/'tables').mkdir(exist_ok=True)
    SOURCES.clear();QA.clear();USED.clear()
    before={p.relative_to(ROOT).as_posix():sha(p) for p in (BASE/'tables').glob('*.csv')}
    for p in sorted((BASE/'tables').glob('*.csv')):
        shutil.copy2(record(p),FIG/'tables'/p.name)
    closeout=ROOT/'data/model_extension/final_closeout_20261005'
    for name in ['matched_choice_sensitivity.csv','failure_sensitivity.csv','statistics_audit.json']:
        shutil.copy2(record(closeout/name),FIG/'tables'/name)
    shutil.copy2(record(HISTORY/'figure7_history_answers_source.csv'),FIG/'tables/figure7_history_answers_source.csv')
    setup()
    for draw in [design,primary,controls,matched,failures,history,quality,robustness,equal_counts,lexical,answers,location,completion,workflow,history_facts,versions]:
        draw()
    for path,value in before.items():
        assert sha(ROOT/path)==value,path
    rows_catalog=catalog()
    for r in rows_catalog:
        r['source_tables']=sorted(set(USED[r['stem']]))
    for p in [Path(__file__),ROOT/'scripts/review_figure_catalog.py',BASE/'figure_manifest.json',HISTORY/'figure_manifest.json']:
        record(p)
    manifest=dict(date='2026-11-13',presentation='Print-sized figures; Jaccard percentages and percentage-point contrasts',
        presentation_units=dict(stored_jaccard='native 0–1 scale, unchanged', displayed_overlap='percent (100 × Jaccard)',
            displayed_difference='percentage points (100 × native contrast)', lexical_overlap='percent (100 × word-set Jaccard)',
            cosine_metrics='native units, unchanged', counts_and_p_values='unchanged',
            method='Tick formatting and annotation conversion only; plotted data coordinates and saved measurements unchanged'),
        figures=[r for r in rows_catalog if not r['label'].startswith('S')],
        supplements=[r for r in rows_catalog if r['label'].startswith('S')],
        source_hashes=SOURCES,checks=['Source measurements unchanged','Six main figures and ten supplements',
        'Current sample counts read from tables','Every figure is 180 mm wide','All visible text at least 7 pt',
        'Jaccard display scaled by 100; source measurements and statistics unchanged'],
        layout_checks=QA,output_hashes={p.relative_to(FIG).as_posix():sha(p) for p in FIG.rglob('*') if p.is_file() and p.name not in ['figure_manifest.json','VISUAL_QA.md']})
    (FIG/'figure_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(dict(figures=len(QA),main=len(manifest['figures']),supplements=len(manifest['supplements']),
                         minimum_font_pt=min(r['minimum_font_pt'] for r in QA.values()),source_measurements_unchanged=True,output=str(FIG)),indent=2))


if __name__=='__main__':
    main()
