"""Plot the separately audited Qwen3-1.7B completion from saved results only.

This module appends Supplement S7 through build_outline_figures_v2.py. It does
not modify the original cohorts, run inference, or recompute statistical tests.
"""
from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'data/model_extension/qwen17_completion_20261106/analysis/results.json'
STEM = 'figureS7_qwen17_completion'
PRIMARY = 'feature_jaccard__margin_other_factual_mean'
DOMAINS = ['chemistry', 'geography', 'history']
INK, OLD, NEW = '#203544', '#9AA8B3', '#007F5F'


def build(source_callback, table_callback, save_callback):
    """Render verified collection accounting and evaluation-domain estimates."""
    source_callback(RESULTS)
    result = json.loads(RESULTS.read_text(encoding='utf-8'))
    assert result['status'] == 'completed'
    assert result['original_reconstruction']['passed'] is True
    original = result['cohorts']['original50_reconstructed']
    expanded = result['cohorts']['expanded91_late_observational']
    collection = result['collection_by_domain']
    assert [r['domain'] for r in collection] == DOMAINS
    assert sum(r['original_graphs'] for r in collection) == 50
    assert sum(r['new_graphs'] for r in collection) == 41
    assert sum(r['available_graphs'] for r in collection) == 91
    assert sum(r['length_rejected_jobs'] for r in collection) == 29
    assert all(r['original_graphs'] + r['new_graphs'] == r['available_graphs'] for r in collection)
    assert collection[2]['complete_four_role_sets'] == 0
    assert original['heldout_primary']['n'] == 5
    assert round(original['heldout_primary']['mean'], 3) == .085

    # Reused chemistry facts remain a single set of observations in this panel.
    included = [r for r in expanded['per_fact'] if r['split'] == 'held_out']
    original_facts = {r['pair_id']: r[PRIMARY] for r in original['per_fact']
                      if r['split'] == 'held_out'}
    chemistry = {r['pair_id']: r[PRIMARY] for r in included if r['domain'] == 'chemistry'}
    assert chemistry.keys() == original_facts.keys()
    assert all(np.isclose(chemistry[k], original_facts[k], atol=1e-12, rtol=0)
               for k in chemistry)
    assert not any(r['domain'] == 'history' for r in included)

    summary = []
    for domain in DOMAINS:
        rows = [r for r in included if r['domain'] == domain]
        # Keep the original interval as well as the original chemistry points.
        # The expanded analyzer's domain bootstrap uses a different seed offset.
        stats = original['heldout_primary'] if domain == 'chemistry' else expanded['heldout_domains'].get(domain)
        if rows:
            assert stats is not None and stats['n'] == len(rows)
            assert np.isclose(np.mean([r[PRIMARY] for r in rows]), stats['mean'], atol=1e-12, rtol=0)
            lo, hi = stats['ci95']
            summary.append(dict(domain=domain, included_evaluation_facts=len(rows),
                                mean=stats['mean'], ci95_low=lo, ci95_high=hi,
                                interval_source='original50_reconstructed.heldout_primary' if domain == 'chemistry'
                                else f'expanded91_late_observational.heldout_domains.{domain}',
                                status='estimated', sample='reused original chemistry' if domain == 'chemistry'
                                else 'newly completed geography'))
        else:
            summary.append(dict(domain=domain, included_evaluation_facts=0,
                                mean=None, ci95_low=None, ci95_high=None,
                                interval_source=None,
                                status='unavailable', sample='no complete four-role sets' if domain == 'history'
                                else 'no evaluation facts pass inclusion rules'))
    table_callback('figureS7_collection', collection)
    table_callback('figureS7_domain_summary', summary)
    table_callback('figureS7_per_fact', [dict(pair_id=r['pair_id'], domain=r['domain'],
                                            split=r['split'], margin=r[PRIMARY]) for r in included])

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.5),
                             gridspec_kw={'width_ratios': [1, 1.16]})
    fig.subplots_adjust(left=.105, right=.985, top=.79, bottom=.28, wspace=.42)
    y = np.arange(3)
    ax = axes[0]
    old = np.array([r['original_graphs'] for r in collection])
    new = np.array([r['new_graphs'] for r in collection])
    ax.barh(y, old, height=.50, color=OLD, label='Previously available')
    ax.barh(y, new, left=old, height=.50, color=NEW, label='Newly collected')
    for i, row in enumerate(collection):
        for start, count, text_color in [(0, old[i], INK), (old[i], new[i], 'white')]:
            if count:
                ax.text(start + count / 2, i, str(count), ha='center', va='center',
                        color=text_color, fontweight='bold', fontsize=10)
        ax.text(row['available_graphs'] + 1, i,
                f"{row['available_graphs']}/{row['planned_graphs']}",
                va='center', fontsize=10, color=INK)
    ax.set(yticks=y, yticklabels=['Chemistry', 'Geography', 'History'],
           ylim=(2.65, -.65), xlim=(0, 51), xticks=[0, 10, 20, 30, 40],
           xlabel='Raw graphs available (count)')
    ax.set_title('a  Collection by subject', loc='left', pad=16, fontsize=11)
    ax.legend(loc='upper left', bbox_to_anchor=(-.04, -.18), ncol=2, frameon=False, fontsize=8.5)
    ax.grid(axis='x', alpha=.15)
    ax.set_axisbelow(True)

    ax = axes[1]
    for i, (domain, s) in enumerate(zip(DOMAINS, summary)):
        vals = [r[PRIMARY] for r in included if r['domain'] == domain]
        if not vals:
            reason = ('No complete four-prompt sets' if domain == 'history'
                      else 'No evaluation facts pass inclusion rules')
            ax.text(.02, i, reason, transform=ax.get_yaxis_transform(),
                    va='center', color='#6A7882', fontsize=9.5,
                    bbox=dict(facecolor='white', edgecolor='none', pad=2), zorder=5)
            continue
        color = OLD if domain == 'chemistry' else NEW
        offsets = np.linspace(-.13, .13, len(vals))
        ax.scatter(vals, i + offsets, color=color, s=40, zorder=3)
        ax.errorbar(s['mean'], i, xerr=[[s['mean'] - s['ci95_low']],
                                      [s['ci95_high'] - s['mean']]],
                    fmt='D', color=INK, ms=5, capsize=4, zorder=4)
        ax.text(.98, i - .31, f"mean = {s['mean']:.3f}; n={len(vals)}", ha='right',
                transform=ax.get_yaxis_transform(), fontsize=9.5, color=INK)
    ax.axvline(0, color='#7A8790', lw=1, ls='--', zorder=1)
    ax.set(yticks=y, yticklabels=['Chemistry\n(original facts)', 'Geography\n(added coverage)', 'History'],
           ylim=(2.65, -.65), xlabel='Difference in feature overlap\n(same fact minus other facts)')
    ax.set_title('b  Included evaluation questions', loc='left', pad=16, fontsize=11)
    ax.grid(axis='x', alpha=.15)
    fig.text(.105, .115, 'Collection: 50 reused + 41 new graphs. All 29 unavailable history jobs exceeded the hosted token limit.',
             fontsize=9, color=INK)
    fig.text(.105, .068, 'Points = evaluation facts; diamonds = means; bars = descriptive 95% fact-bootstrap intervals. History is unavailable, not zero.',
             fontsize=9, color=INK)
    fig.text(.105, .025, 'Separate late completion. Figure 2 retains the original Qwen3-1.7B sample of five chemistry facts.',
             fontsize=9, color=INK)
    save_callback(fig, STEM)
