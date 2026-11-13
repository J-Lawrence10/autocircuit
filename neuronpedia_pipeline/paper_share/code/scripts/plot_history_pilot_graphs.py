"""Static source-linked figures for the bounded 16-prompt history analysis."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import run_history_pilot_graphs as design
from analyze_matched_choice_controls import csv_write

SHORT = {'US Declaration of Independence adoption': 'Declaration',
         'American Revolutionary Treaty of Paris signing': 'Treaty of Paris',
         'Sputnik 1 launch': 'Sputnik 1', 'Explorer 1 launch': 'Explorer 1'}
NAMES = {'pilot_documents': 'Declaration of Independence / Treaty of Paris',
         'pilot_space': 'Sputnik 1 / Explorer 1'}
COLORS = {'pilot_documents': '#0072B2', 'pilot_space': '#D55E00'}


def save(fig, out, stem):
    for ext in ('png', 'svg'):
        fig.savefig(out / f'{stem}.{ext}', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def main():
    out = design.OUT / 'figures'
    out.mkdir(parents=True, exist_ok=True)
    result = json.loads((design.OUT / 'analysis/results.json').read_text())
    jobs = json.loads((design.OUT / 'jobs.json').read_text())
    audits = {r['job_id']: r for r in result['audits']}
    pairs = {frozenset((r['a'], r['b'])): r for r in result['pairs']}
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), layout='constrained')
    heat_sources = []
    for ax, block in zip(axes, design.BLOCKS):
        group = [j for j in jobs if j['block'] == block]
        matrix = np.full((8, 8), np.nan)
        labels = []
        for i, j in enumerate(group):
            ar = audits[j['job_id']]
            label = f'{SHORT[j["event"]]} | need {j["expected_label"]}, got {ar["observed"] or "?"}'
            label += '*' if ar['correct'] is False else ''
            label += ' | Q first' if j['wording'] == 0 else ' | C first'
            labels.append(label)
            for k, other in enumerate(group):
                value = 1. if i == k and ar['graph_eligible'] else None
                if i != k:
                    value = pairs[frozenset((j['job_id'], other['job_id']))]['jaccard']
                matrix[i, k] = value if value is not None else np.nan
                heat_sources.append(dict(block=block, row_job=j['job_id'], column_job=other['job_id'], jaccard=value))
        cmap = plt.colormaps['viridis'].copy()
        cmap.set_bad('#dddddd')
        im = ax.imshow(matrix, vmin=0, vmax=1, cmap=cmap)
        ax.set_title(NAMES[block], fontsize=12, pad=12)
        ax.set_xticks(range(8), [str(i + 1) for i in range(8)])
        ax.set_yticks(range(8), [f'{i + 1}. {s}' for i, s in enumerate(labels)], fontsize=8)
        ax.set_xlabel('Prompt number (same order as rows)')
        for i in range(8):
            for k in range(8):
                if np.isfinite(matrix[i, k]):
                    ax.text(k, i, f'{matrix[i, k]:.2f}', ha='center', va='center', fontsize=7,
                            color='white' if matrix[i, k] < .55 else '#111111')
    colorbar = fig.colorbar(im, ax=axes, shrink=.62, pad=.025)
    colorbar.set_label('Feature overlap (Jaccard): 0 = none; 1 = identical sets')
    fig.suptitle('Feature overlap across correct and incorrect history predictions\nQwen3-4B', fontsize=16, y=1.03)
    fig.supxlabel('* Incorrect prediction. Q first: question before context. C first: context before question. Gray: unavailable graph.', fontsize=10)
    save(fig, out, 'history_all_graph_overlap')
    csv_write(out / 'history_all_graph_overlap_source.csv', heat_sources)

    fig, axes = plt.subplots(1, 3, figsize=(17, 6), layout='constrained')
    names = [('SS', 'Same event\nSame letter'), ('DS', 'Different event\nSame letter'),
             ('SD', 'Same event\nDifferent letter'), ('DD', 'Different event\nDifferent letter')]
    source_rows = []
    for index, block in enumerate(design.BLOCKS):
        row = next((r for r in result['block_contrasts'] if r['block'] == block and r.get('variant') == 'full'
                    and r.get('metric') == 'jaccard' and r['status'] == 'ok'), None)
        if row:
            xs = np.arange(4) + (index - .5) * .34
            axes[0].bar(xs, [row[k] for k, _ in names], width=.32, color=COLORS[block],
                        label='Document dates' if index == 0 else 'Launch dates')
            for key, _ in names:
                source_rows.append(dict(panel='a', block=block, category=key, n=4, jaccard=row[key]))
    axes[0].set_xticks(range(4), [name for _, name in names], fontsize=9)
    axes[0].set_ylim(0, 1)
    axes[0].set_ylabel('Mean feature overlap (Jaccard)')
    axes[0].set_title('a  Event and required answer letter', loc='left', fontsize=12)
    if axes[0].get_legend_handles_labels()[0]:
        axes[0].legend(frameon=False, fontsize=9)
    axes[0].text(.5, -.22, 'Across question orders; 4 comparisons per bar', transform=axes[0].transAxes, ha='center', fontsize=9)
    jobs_by_id = {j['job_id']: j for j in jobs}
    for ax, flag, match_key, title, subtitle in [
            (axes[1], 'order_only', 'same_predicted_letter', 'b  Reverse question/context order', 'Same event and answer mapping'),
            (axes[2], 'mapping_only', 'same_predicted_year', 'c  Swap the A/B date mapping', 'Same event and question order')]:
        rows = [r for r in result['pairs'] if r[flag]]
        labels = []
        for index, row in enumerate(rows):
            job = jobs_by_id[row['a']]
            suffix = f'need {job["expected_label"]}' if flag == 'order_only' else ('Q first' if job['wording'] == 0 else 'C first')
            labels.append(f'{SHORT[job["event"]]}: {suffix}')
            color = '#CC79A7' if row[match_key] is False else '#0072B2'
            if row['jaccard'] is not None:
                ax.scatter(row['jaccard'], index, color=color, s=60, zorder=3)
            else:
                ax.text(.03, index, 'Unavailable', va='center', fontsize=8)
            source_rows.append(dict(panel=flag, **row))
        ax.set_yticks(range(len(rows)), labels, fontsize=9)
        ax.set_ylim(len(rows) - .5, -.5)
        ax.set_xlim(0, 1)
        ax.set_xlabel('Feature overlap (Jaccard)')
        ax.set_title(title + '\n' + subtitle, fontsize=11, loc='left')
        ax.grid(axis='x', alpha=.25)
        change = 'Predicted letter changed' if flag == 'order_only' else 'Selected date changed'
        stable = 'Predicted letter unchanged' if flag == 'order_only' else 'Selected date unchanged'
        ax.legend(handles=[Line2D([], [], marker='o', color='#CC79A7', ls='', label=change),
                           Line2D([], [], marker='o', color='#0072B2', ls='', label=stable)],
                  loc='upper center', bbox_to_anchor=(.5, -.16), fontsize=8, frameon=False)
    fig.supxlabel('Q first: question before context. C first: context before question. Model tested: Qwen3-4B.', fontsize=9, y=-.06)
    save(fig, out, 'history_prompt_change_comparisons')
    csv_write(out / 'history_prompt_change_comparisons_source.csv', source_rows)
    (out / 'LEGENDS.md').write_text(
        '# History graph figure legends\n\n'
        '## Feature overlap across correct and incorrect history predictions\n\n'
        'Each panel shows all eight graphs for one event pair. Every cell is Jaccard overlap of distinct feature identities, excluding embeddings, logits, and reconstruction-error nodes. The same 0–1 color scale applies to both panels. Row labels identify the queried event, required and observed answer letters, and whether the question or context comes first. Asterisks mark incorrect predictions. Diagonal values compare each graph with itself. All incorrect predictions are retained; gray cells indicate unavailable graphs.\n\n'
        '## Feature overlap after prompt changes\n\n'
        'A, Mean cross-order overlap grouped by queried event and required answer letter, with four comparisons per bar. Required letters can differ from actual predictions. B, Each point compares two prompts differing only in question/context order; color records whether the predicted letter changed. C, Each point compares two prompts differing only in the A/B date mapping; color records whether the date selected by the model changed. The event and correct date are fixed within each point comparison. Jaccard ranges from 0 (no shared features) to 1 (identical feature sets). These are descriptive comparisons of two event pairs, not independent population replicates.\n',
        encoding='utf-8')
    manifest = dict(figures=['history_all_graph_overlap', 'history_prompt_change_comparisons'],
                    results_sha256=design.digest(design.OUT / 'analysis/results.json'),
                    plotting_script_sha256=design.digest(__file__))
    from control_io import atomic_json
    atomic_json(out / 'figure_manifest.json', manifest)
    print('Saved two source-linked figure pairs and legends.')


if __name__ == '__main__':
    main()
