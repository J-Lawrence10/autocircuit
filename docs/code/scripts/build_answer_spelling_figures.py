"""Update the answer audit and add the accepted-spelling sensitivity figure."""
from copy import deepcopy
import csv
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from analyze_answer_spelling import ROOT, OUT as ANALYSIS, PRIMARY
from analyze_model_extension import write_csv
from complete_qwen4_controls import digest
from control_io import atomic_json
import figure_plain_language as wording

PREVIOUS = ROOT/'data/model_extension/paper_figures_qwen4_complete_20261110'
OUT = ANALYSIS/'paper_figures_v1'
INK = '#203544'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(fig, stem):
    fig.suptitle(wording.TITLES[stem], x=.045, y=.98, ha='left', va='top', fontsize=16, fontweight='bold', color=INK)
    for extension in ['png', 'svg']:
        fig.savefig(OUT/f'{stem}.{extension}', dpi=300, facecolor='white')
    plt.close(fig)


def answer_audit(result):
    with (PREVIOUS/'tables/figureS5_answer_audit.csv').open(encoding='utf-8', newline='') as handle:
        old = list(csv.DictReader(handle))
    stats = {model: {r['category']: int(r['count']) for r in old if r['model'] == model}
             for model in ['qwen3-1.7b', 'qwen3-4b']}
    assert len(result['changed_outputs']) == 1 and result['changed_outputs'][0]['model'] == 'qwen3-4b'
    stats['qwen3-4b']['next_token_mismatch'] -= 1
    stats['qwen3-4b']['accepted_spelling_variant'] = 1
    categories = ['whole_answer_next_token', 'accepted_spelling_variant', 'multi_token_prefix_only', 'next_token_mismatch']
    labels = ['Exact expected answer in the first token', 'Correct spelling variant of the complete answer',
              'Only the beginning matches; whole answer unverified', 'Other first token']
    colors = ['#009E73', '#0072B2', '#E69F00', '#8C94A0']
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.4), gridspec_kw={'width_ratios': [1.1, 1]})
    fig.subplots_adjust(left=.08, right=.91, bottom=.29, top=.81, wspace=.42)
    source = []
    for i, model in enumerate(stats):
        bottom = 0
        for category, color in zip(categories, colors):
            count = stats[model].get(category, 0)
            axes[0].bar(i, count, bottom=bottom, color=color, width=.55)
            if count > 1:
                axes[0].text(i, bottom+count/2, str(count), ha='center', va='center')
            elif count == 1:
                axes[0].annotate('1', (i+.28, bottom+.5), xytext=(9, 0), textcoords='offset points', va='center', color=color,
                                 arrowprops={'arrowstyle': '-', 'color': color, 'lw': 1})
            bottom += count
            source.append(dict(model=model, category=category, count=count, total=sum(stats[model].values()), unit='available factual-question graphs'))
        assert bottom == [50, 60][i]
        axes[0].text(i, bottom+1.5, f'n={bottom}', ha='center')
    axes[0].set(xticks=[0, 1], xticklabels=['Qwen3-1.7B', 'Qwen3-4B'], ylim=(0, 65), ylabel='Factual-question graphs checked', xlim=(-.6, 1.65))
    axes[0].set_title('a  What does the first token confirm?', loc='left', fontsize=12, fontweight='bold')
    saved = read(ROOT/'data/model_extension/exploratory_20260905/results.json')
    domains = ['chemistry', 'geography', 'history']
    matrix = np.array([[next(r['strict_match_n'] for r in saved['crossed_output_support'] if r['model'] == model and r['domain'] == domain)
                        for domain in domains] for model in ['gemma-2-2b', 'qwen3-4b']])
    heat = axes[1].imshow(matrix, cmap='Blues', vmin=0, vmax=9, aspect='auto')
    scale = fig.colorbar(heat, ax=axes[1], fraction=.045, pad=.04, ticks=[0, 3, 6, 9])
    scale.set_label('Exact first-token matches (out of 9)', fontsize=9)
    for i in range(2):
        for j in range(3):
            axes[1].text(j, i, f'{matrix[i,j]}/9', ha='center', va='center', color='white' if matrix[i,j]>=6 else 'black', fontsize=13)
    axes[1].set(xticks=range(3), xticklabels=[d.title() for d in domains], yticks=range(2), yticklabels=['Gemma-2-2B', 'Qwen3-4B'])
    axes[1].set_title('b  Fact/wording question sets', loc='left', fontsize=12, fontweight='bold')
    fig.legend([plt.Rectangle((0, 0), 1, 1, color=c) for c in colors], labels, loc='lower center', ncol=1, frameon=False, fontsize=9)
    write_csv(OUT/'tables/figureS5_answer_audit.csv', source)
    save(fig, 'figureS5_answer_audit')


def sensitivity(result):
    after, before = result['accepted_spelling'], result['exact_match']
    facts = ['columbus_americas', 'wwi_start']
    labels = ['Columbus’s\nflagship', 'Franz\nFerdinand']
    history = {r['pair_id']: r for r in after['per_fact'] if r['domain'] == 'history' and r['split'] == 'held_out'}
    assert set(history) == set(facts)
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 6.3), gridspec_kw={'width_ratios': [1.2, 1, .9]})
    fig.subplots_adjust(left=.10, right=.985, bottom=.28, top=.78, wspace=.43)
    colors = ['#0072B2', '#CC651D']
    for i, fact in enumerate(facts):
        own = history[fact]['feature_jaccard__target_positive']
        other = history[fact]['feature_jaccard__other_factual_mean']
        axes[0].plot([other, own], [i, i], c='#AAB5BD', lw=2, zorder=1)
        axes[0].scatter(own, i, c=colors[0], marker='o', s=65, label='Same fact, reworded' if i==0 else None, zorder=2)
        axes[0].scatter(other, i, c=colors[1], marker='s', s=55, label='Other history fact' if i==0 else None, zorder=2)
        axes[0].annotate(f'{own:.3f}', (own, i), xytext=(0, 12), textcoords='offset points', ha='center', fontsize=9)
        axes[0].annotate(f'{other:.3f}', (other, i), xytext=(0, -19), textcoords='offset points', ha='center', fontsize=9)
    axes[0].set(yticks=[0, 1], yticklabels=labels, ylim=(1.6, -.6), xlim=(0, 1), xlabel='Feature overlap (Jaccard)')
    axes[0].set_title('a  Two history facts can be compared', loc='left', fontsize=11, fontweight='bold', pad=13)
    axes[0].legend(loc='lower left', bbox_to_anchor=(-.13, -.36), frameon=False, fontsize=9)
    points = []
    style = [('Full set', None, '#203544', 'o'), ('Equal count (K)', 1.0, '#0072B2', 's'), ('Half count (K/2)', .5, '#009E73', '^')]
    for i, fact in enumerate(facts):
        for j, (label, fraction, color, marker) in enumerate(style):
            value = history[fact][PRIMARY] if fraction is None else next(r['mean'] for r in result['equal_count']['per_fact'] if r['fact']==fact and r['fraction']==fraction)
            axes[1].scatter(i+(j-1)*.18, value, color=color, marker=marker, s=55, label=label if i==0 else None)
            points.append(dict(fact=fact, comparison=label, margin=value))
    axes[1].axhline(0, color='gray', ls='--', lw=1)
    axes[1].set(xticks=[0, 1], xticklabels=labels, ylabel='Same-fact minus other-fact overlap', xlim=(-.5, 1.5))
    axes[1].set_title('b  Check with equal feature counts', loc='left', fontsize=11, fontweight='bold', pad=13)
    axes[1].legend(loc='lower left', bbox_to_anchor=(-.03, -.36), frameon=False, fontsize=9)
    pooled = []
    for i, (label, data) in enumerate([('Exact\nmatching', before), ('Accepted\nspelling', after)]):
        stats = data['heldout_primary']; low, high = stats['ci95']
        axes[2].errorbar(i, stats['mean'], yerr=[[stats['mean']-low], [high-stats['mean']]], fmt='D', color=['#667987', '#0072B2'][i], capsize=4)
        axes[2].annotate(f"{stats['mean']:.3f}\nn={stats['n']}", (i, high), xytext=(0, 10), textcoords='offset points', ha='center', fontsize=10)
        pooled.append(dict(rule=label.replace('\n', ' '), n=stats['n'], mean=stats['mean'], ci_low=low, ci_high=high))
    upper = max(r['ci_high'] for r in pooled)
    axes[2].set(xticks=[0, 1], xticklabels=['Exact\nmatching', 'Accepted\nspelling'], xlim=(-.5, 1.5), ylim=(0, upper*1.45), ylabel='Mean overlap difference')
    axes[2].set_title('c  Overall Qwen3-4B estimate', loc='left', fontsize=11, fontweight='bold', pad=13)
    fig.text(.10, .08, 'María and Maria name the same ship. The other history question asks who was assassinated before World War I: Franz Ferdinand.', fontsize=9.5, color=INK)
    fig.text(.10, .035, 'Saved-data sensitivity: the two history facts share comparators. The 12-fact sample includes the original 10; it is not independent replication.', fontsize=9, color=INK)
    write_csv(OUT/'tables/figureS9_history_comparisons.csv', result['history_comparisons'])
    write_csv(OUT/'tables/figureS9_history_equal_counts.csv', points)
    write_csv(OUT/'tables/figureS9_pooled_estimates.csv', pooled)
    save(fig, 'figureS9_answer_spelling')


def main():
    result = read(ANALYSIS/'results.json')
    assert result['status'] == 'completed' and result['post_hoc'] and result['no_hosted_requests']
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'tables').mkdir(exist_ok=True)
    prior = read(PREVIOUS/'figure_manifest.json')
    for path in list(PREVIOUS.glob('*.png'))+list(PREVIOUS.glob('*.svg'))+list((PREVIOUS/'tables').glob('*.csv')):
        shutil.copy2(path, OUT/path.relative_to(PREVIOUS))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'text.color': INK, 'axes.labelcolor': INK})
    answer_audit(result)
    sensitivity(result)
    manifest = deepcopy(prior)
    for fig in manifest['figures']+manifest['supplements']:
        fig['title'], fig['legend'] = wording.TITLES[fig['stem']], wording.CAPTIONS[fig['stem']]
    manifest['supplements'].append(dict(number=9, label='S9', stem='figureS9_answer_spelling',
                                       title=wording.TITLES['figureS9_answer_spelling'], legend=wording.CAPTIONS['figureS9_answer_spelling']))
    manifest['date'] = '2026-11-11'
    manifest['previous_figure_manifest_sha256'] = digest(PREVIOUS/'figure_manifest.json')
    manifest['source_hashes'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in [
        ANALYSIS/'results.json', ANALYSIS/'plan.json', PREVIOUS/'figure_manifest.json', Path(__file__), Path(wording.__file__)]}
    manifest['checks'] += ['Exact-match primary figures retained; accepted-spelling sensitivity is separate in S9',
                           'S5 distinguishes one complete accepted spelling from five other Qwen3-4B mismatches']
    manifest['output_hashes'] = {p.relative_to(OUT).as_posix(): digest(p) for p in sorted(OUT.rglob('*'))
                               if p.is_file() and p.name not in {'figure_manifest.json', 'VISUAL_QA.md'}}
    atomic_json(OUT/'figure_manifest.json', manifest)
    print(f'Updated answer audit and added S9: {OUT}')


if __name__ == '__main__':
    main()
