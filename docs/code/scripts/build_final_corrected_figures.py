"""Build final paper figures from corrected scoring; no model requests."""
from copy import deepcopy
from pathlib import Path
import shutil
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from finalize_corrected_scoring import ROOT, OUT as ANALYSIS, PREVIOUS, MODEL, PRIMARY, read
from complete_qwen4_controls import digest, read_csv
from control_io import atomic_json
from analyze_model_extension import write_csv
import build_three_model_figure_pack as base
import build_outline_figures as draft
import plot_updated_cohort_figures as updated
import plot_methods_workflow as methods
import figure_plain_language as wording

OUT = ANALYSIS/'paper_figures'
SOURCES = {}
INK = '#203544'


def source(path):
    SOURCES[path.relative_to(ROOT).as_posix()] = digest(path)
    return path


def table(name, rows):
    write_csv(OUT/'tables'/f'{name}.csv', rows)


def save(fig, stem, *unused):
    if stem in {'figureS2_robustness','figureS3_equal_feature_counts','figureS4_lexical_support','figureS5_answer_audit'}:
        wording.clarify(fig, stem)
    if stem=='figureS3_equal_feature_counts':
        for ax in fig.axes:
            ax.set_ylim(-.045,.70)
            for t in ax.texts:
                if t.get_position()[1]==.55:
                    t.set_y(.65)
    if stem=='figureS4_lexical_support':
        updated.add_bottom_padding(fig,.20)
    if stem=='figureS5_answer_audit':
        for legend in fig.legends:
            for t in legend.get_texts():
                if t.get_text()=='Whole expected answer in the first token':
                    t.set_text('Complete accepted answer in the first token')
    fig.suptitle(textwrap.fill(wording.TITLES[stem], 94), x=.04, y=.98, ha='left', va='top',
                 fontsize=16 if stem!='figureS8_feature_overlap_workflow' else 20,
                 fontweight='bold', color=INK)
    for ext in ['png','svg']:
        fig.savefig(OUT/f'{stem}.{ext}', dpi=300, facecolor='white')
    plt.close(fig)


def signal(results):
    fig, axes=plt.subplots(1,2,figsize=(13.2,7.2))
    fig.subplots_adjust(left=.075,right=.98,bottom=.23,top=.72,wspace=.25)
    summary, points, domains=[],[],[]
    for i,(name,result) in enumerate(zip(updated.LABELS,results)):
        rows=base.heldout(result); stats=result['heldout_primary']
        for j,row in enumerate(rows):
            d=base.DOMAINS.index(row['domain'])
            axes[0].scatter(i-.22+.44*j/max(1,len(rows)-1),row[PRIMARY],
                color=base.DOMAIN_COLORS[d],marker=base.MARKERS[d],s=37)
            points.append(dict(model=name,**row))
        base.interval(axes[0],i,stats,INK)
        axes[0].text(i,.675,f'n={stats["n"]}\nmean {stats["mean"]:.3f}',ha='center',va='top',fontsize=10)
        summary.append(dict(model=name,**{k:stats[k] for k in ['n','mean','positive_n','exact_one_sided_sign_flip_p']},
                            ci_low=stats['ci95'][0],ci_high=stats['ci95'][1]))
        for j,domain in enumerate(base.DOMAINS):
            s=result['heldout_domains'].get(domain,{})
            if not s.get('n'):
                continue
            x=i+(j-1)*.22
            # The two history facts share their only comparator. Show their mean,
            # not an apparently population-level two-fact uncertainty interval.
            if name=='Qwen3-4B' and domain=='history':
                axes[1].scatter(x,s['mean'],marker='D',color=base.DOMAIN_COLORS[j],s=45,zorder=5)
                label_y=s['mean'];lo=hi=None
            else:
                base.interval(axes[1],x,s,base.DOMAIN_COLORS[j]);label_y=s['ci95'][1]
                lo,hi=s['ci95']
            axes[1].annotate(f'n={s["n"]}',(x,label_y),xytext=(0,8),textcoords='offset points',ha='center',fontsize=9)
            domains.append(dict(model=name,domain=domain,n=s['n'],mean=s['mean'],ci_low=lo,ci_high=hi))
    for ax in axes:
        ax.set(ylim=(-.025,.71),xticks=range(3),xticklabels=updated.LABELS,
               ylabel='Difference in feature overlap\n(same fact minus other facts)')
        ax.axhline(0,color='gray',ls='--',lw=1)
    axes[0].set_title('a  Overlap difference for each test question',loc='left',fontsize=11,pad=12)
    axes[1].set_title('b  Average overlap difference by subject',loc='left',fontsize=11,pad=12)
    handles=[Line2D([],[],marker=base.MARKERS[j],color=base.DOMAIN_COLORS[j],ls='',label=d.title())
             for j,d in enumerate(base.DOMAINS)]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.09),ncol=3,frameon=False,title='Subject')
    fig.text(.075,.905,'Difference in feature overlap = overlap with the same fact, reworded',fontsize=11,fontweight='bold')
    fig.text(.075,.865,'minus average overlap with other facts in the same subject and test set.',fontsize=10)
    fig.text(.075,.815,'Illustration only: 0.50 − 0.30 = +0.20. Positive values mean greater same-fact overlap, not a percentage increase.',fontsize=9)
    fig.text(.075,.065,'Points = test questions; diamonds = means; bars = descriptive 95% intervals; n = questions.',fontsize=9)
    fig.text(.075,.025,'Qwen3-4B history: two facts share comparison graphs, so only their mean is shown. Missing groups are not zero effects.',fontsize=9)
    table('figure2_summary',summary);table('figure2_fact_level',points);table('figure2_domain_summary',domains)
    save(fig,'figure2_fact_signal')


def history(result):
    rows={r['pair_id']:r for r in result['controlled']['per_fact'] if r['domain']=='history' and r['split']=='held_out'}
    facts=['columbus_americas','wwi_start'];labels=['Columbus’s\nflagship','Franz\nFerdinand']
    fig,axes=plt.subplots(1,2,figsize=(12,6.7),gridspec_kw={'width_ratios':[1.15,1]})
    fig.subplots_adjust(left=.15,right=.98,bottom=.30,top=.79,wspace=.34)
    points=[]
    for i,fact in enumerate(facts):
        own,other=rows[fact]['feature_jaccard__target_positive'],rows[fact]['feature_jaccard__other_factual_mean']
        axes[0].plot([other,own],[i,i],color='#AAB5BD',lw=2)
        for value,color,marker,label,dy in [(own,'#0072B2','o','Same fact, reworded',12),(other,'#CC651D','s','Other history fact',-20)]:
            axes[0].scatter(value,i,color=color,marker=marker,s=60,label=label if i==0 else None,zorder=3)
            axes[0].annotate(f'{value:.3f}',(value,i),xytext=(0,dy),textcoords='offset points',ha='center',fontsize=10)
        for j,(label,fraction,color,marker) in enumerate([('Full set',None,INK,'o'),('Equal count (K)',1.,'#0072B2','s'),('Half count (K/2)',.5,'#009E73','^')]):
            val=rows[fact][PRIMARY] if fraction is None else next(r['mean_margin'] for r in result['equal_count']['rows'] if r['fact']==fact and r['fraction']==fraction)
            axes[1].scatter(i+(j-1)*.18,val,color=color,marker=marker,s=60,label=label if i==0 else None)
            points.append(dict(fact=fact,comparison=label,margin=val))
    axes[0].set(yticks=[0,1],yticklabels=labels,ylim=(1.6,-.6),xlim=(0,1),xlabel='Feature overlap (Jaccard)')
    axes[0].set_title('a  Same-fact and other-fact overlap',loc='left',fontsize=11,pad=14)
    axes[1].set(xticks=[0,1],xticklabels=labels,xlim=(-.5,1.5),ylim=(-.025,.67),ylabel='Same-fact minus other-fact overlap')
    axes[1].axhline(0,color='gray',ls='--',lw=1)
    axes[1].set_title('b  Check with equal feature counts',loc='left',fontsize=11,pad=14)
    for ax in axes:
        ax.legend(loc='upper left',bbox_to_anchor=(-.02,-.18),frameon=False,fontsize=9)
    fig.text(.07,.055,'Qwen3-4B: both history facts are included in Figure 2. Each uses the other as its comparison partner.',fontsize=9)
    fig.text(.07,.02,'The flagship predictions are Maria and María; both name the same ship. The other question asks about Franz Ferdinand.',fontsize=9)
    table('figureS9_history_comparisons',result['history_comparisons'])
    table('figureS9_history_equal_counts',points)
    save(fig,'figureS9_answer_spelling')


def main():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'tables').mkdir(exist_ok=True)
    result=read(source(ANALYSIS/'results.json'))
    prior=read(source(PREVIOUS/'figure_manifest.json'))
    # Keep unrelated designs byte-identical; redraw every affected measurement.
    changed={'figure2_fact_signal','figureS2_robustness','figureS3_equal_feature_counts',
             'figureS4_lexical_support','figureS5_answer_audit','figureS8_feature_overlap_workflow','figureS9_answer_spelling'}
    for row in prior['figures']+prior['supplements']:
        if row['stem'] not in changed:
            for ext in ['png','svg']:
                path=source(PREVIOUS/f'{row["stem"]}.{ext}')
                shutil.copy2(path,OUT/path.name)
    for path in (PREVIOUS/'tables').glob('*.csv'):
        if path.name.startswith('figureS9_'):
            continue
        source(path);shutil.copy2(path,OUT/'tables'/path.name)
    base.OUT=OUT;base.table=table;base.save=save
    base.LABELS[:]=updated.LABELS[:]=['Gemma-2-2B','Qwen3-1.7B','Qwen3-4B']
    base.style();plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,'axes.labelcolor':INK})
    current=updated.CurrentFigures(source,table,qwen4_completion={'answers':result['answers']})
    gemma=read(source(ROOT/'data/publication_analysis/whole_graph_results.json'))['models']['gemma']
    results=[gemma,current.current,result['controlled']]
    for r in results:
        updated.validate_stats(r['heldout_primary'],[x[PRIMARY] for x in base.heldout(r)])
    signal(results);base.robustness_figure(results)
    saved=read(source(ROOT/'data/model_extension/exploratory_20260905/results.json'))
    size=read_csv(source(ROOT/'data/model_extension/exploratory_20260905/size_per_fact.csv'))
    saved['size']=[r for r in saved['size'] if r['model']!=MODEL]+result['equal_count']['summaries']
    size=[r for r in size if r['model']!=MODEL]+result['equal_count']['rows']
    current.equal_counts(results,saved,size,save)
    pairs=read_csv(source(ROOT/'data/model_extension/exploratory_20260905/pairwise_lexical_and_size.csv'))
    pairs=[r for r in pairs if r['model']!=MODEL]+read_csv(source(ANALYSIS/'lexical_pairs.csv'))
    saved['lexical']=[r for r in saved['lexical'] if r['model']!=MODEL]+result['lexical']['summaries']
    current.lexical(saved,pairs,save);current.answers(saved,save)
    fig=methods.build_figure();methods.validate_figure(fig);save(fig,methods.STEM)
    history(result)
    table('test_fact_inclusion_audit',read_csv(source(ANALYSIS/'test_fact_inclusion_audit.csv')))
    # Any legacy coverage table must reflect the same final sample.
    coverage=[dict(model=name,domain=d,eligible_facts=r['heldout_domains'].get(d,{}).get('n',0))
              for name,r in zip(updated.LABELS,results) for d in base.DOMAINS]
    table('figure1_coverage',coverage)
    for module in [base,draft,updated,methods,wording]:
        source(Path(module.__file__))
    source(Path(__file__))
    manifest=deepcopy(prior)
    for row in manifest['figures']+manifest['supplements']:
        row['title'],row['legend']=wording.TITLES[row['stem']],wording.CAPTIONS[row['stem']]
    manifest.update(date='2026-11-11',presentation='Final corrected answer scoring in all primary displays',
        checks=['One final sample per model: 8/10/12 evaluation facts',
                'No before/after scoring cohorts displayed',
                'Output-type matched Qwen3-4B controls retain ten facts',
                'History raw comparisons and equal-count points agree with saved corrected analysis'],
        source_hashes=SOURCES,script_sha256=digest(Path(__file__)),helper_hashes={},
        output_hashes={p.relative_to(OUT).as_posix():digest(p) for p in sorted(OUT.rglob('*'))
                       if p.is_file() and p.name not in {'figure_manifest.json','VISUAL_QA.md'}})
    atomic_json(OUT/'figure_manifest.json',manifest)
    print(f'Final corrected figures: {OUT}')


if __name__=='__main__':
    main()
