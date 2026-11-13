"""Rebuild Supplement S6 from the archived closeout tables, without model calls."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/model_extension/final_closeout_20261005'
VARIANTS=['full','exclude_final_position','exclude_last_quarter_layers','exclude_both']
LABELS=['Full feature\nset','Remove final\nposition','Remove last\nquarter of layers','Remove\nboth']


def main(save_callback=None):
    sources=[OUT/'matched_choice_sensitivity.csv',OUT/'failure_sensitivity.csv',OUT/'statistics_audit.json']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    with sources[0].open(newline='') as f:matched=list(csv.DictReader(f))
    with sources[1].open(newline='') as f:failure=list(csv.DictReader(f))
    matched=[r for r in matched if r['metric']=='jaccard' and r['status']=='ok']
    plt.rcParams.update({'svg.fonttype':'none','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(13,5.3));fig.subplots_adjust(left=.07,right=.985,top=.78,bottom=.2,wspace=.30)
    for block in sorted({r['block'] for r in matched}):
        values=[float(next(r for r in matched if r['block']==block and r['variant']==v)['label_condition_difference']) for v in VARIANTS]
        axes[0].plot(range(4),values,color='#0072B2',alpha=.4,marker='o',lw=1,ms=4)
    means=[np.mean([float(r['label_condition_difference']) for r in matched if r['variant']==v]) for v in VARIANTS]
    axes[0].scatter(range(4),means,color='black',marker='D',s=45,zorder=4)
    axes[0].set_ylabel('Same-label minus changed-label\nsame-fact advantage (Jaccard)')
    axes[0].set_title('a  Answer-label dependence persists',loc='left',fontweight='bold')
    axes[0].legend(handles=[Line2D([],[],color='#0072B2',marker='o',label='Country pair (n=6)'),Line2D([],[],color='black',marker='D',ls='',label='Mean')],fontsize=9)
    for fmt,color,offset in [('label','#0072B2',-.05),('capital','#CC651D',.05)]:
        for name in sorted({r['job_id'] for r in failure if r['response_format']==fmt}):
            values=[float(next(r for r in failure if r['job_id']==name and r['variant']==v)['output_minus_country']) for v in VARIANTS]
            axes[1].plot(np.arange(4)+offset,values,color=color,alpha=.38,marker='o',lw=1,ms=4)
        means=[np.mean([float(r['output_minus_country']) for r in failure if r['response_format']==fmt and r['variant']==v]) for v in VARIANTS]
        axes[1].scatter(np.arange(4)+offset,means,color=color,marker='D',s=45,zorder=4)
    axes[1].set_ylabel('Same-output minus intended-country\noverlap in wrong answers (Jaccard)')
    axes[1].set_title('b  Selected errors still favor the same output',loc='left',fontweight='bold')
    axes[1].legend(handles=[Line2D([],[],color=c,marker='o',label=l) for c,l in [('#0072B2','A/B answers: 4 comparisons'),('#CC651D','Capital names: 4 comparisons')]],fontsize=9)
    for ax in axes:
        ax.axhline(0,color='gray',ls='--',lw=1);ax.set_xticks(range(4),LABELS);ax.tick_params(axis='x',labelsize=9)
    fig.suptitle('The measured differences are not confined to final-position or late-layer nodes',fontsize=14,y=.96)
    if save_callback is not None:
        save_callback(fig, 'figureS6_graph_location_sensitivity')
        return
    for ext in ['png','svg']:fig.savefig(OUT/f'figureS6_graph_location_sensitivity.{ext}',dpi=200)
    plt.close(fig)
    legend=('Supplement Figure S6. Graph-location sensitivity, specified after inspecting earlier outcomes. '
            'A, Each line is one of six country-pair blocks; black diamonds are means. '
            'B, Lines are selected, dependent failure comparisons; colored diamonds are response-format means. '
            'Filters remove feature nodes before identities are collapsed across positions. The late-layer cutoff is the last quarter of observed feature layers. '
            'All plotted representations are nonempty. Zero means equal overlap for the compared conditions, not missing data. '
            'No intervals or new population tests are attached to the filtered or selected-failure summaries. '
            'These are observational sensitivities, not causal ablations: remaining graphs are still conditioned on the generated output.')
    (OUT/'FIGURE_S6_LEGEND.md').write_text(legend+'\n',encoding='utf-8')
    outputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('figureS6*')}
    (OUT/'figureS6_manifest.json').write_text(json.dumps(dict(sources=hashes,outputs=outputs,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2),encoding='utf-8')
    print(OUT/'figureS6_graph_location_sensitivity.png')


if __name__=='__main__':main()
