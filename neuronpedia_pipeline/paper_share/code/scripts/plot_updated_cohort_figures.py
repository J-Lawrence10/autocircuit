"""Plot the current three-model cohorts from validated saved results only.

Qwen3-1.7B uses 91 available graphs and ten included evaluation facts.
Collection history remains in provenance, not duplicated display groups.
"""
import hashlib
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
COMPLETION=ROOT/'data/model_extension/qwen17_completion_20261106'
PRIMARY='feature_jaccard__margin_other_factual_mean'
INK='#203544'
MODELS=['gemma-2-2b','qwen3-1.7b','qwen3-4b']
LABELS=['Gemma-2-2B','Qwen3-1.7B','Qwen3-4B*']
COLORS=['#0072B2','#A6558C','#CC651D']
DOMAINS=['chemistry','geography','history']
DOMAIN_COLORS=['#0072B2','#009E73','#CC651D']
CURRENT='expanded91_late_observational'


def validate_stats(stats,values):
    """Check saved summaries without recomputing intervals or tests."""
    assert stats['n']==len(values) and values
    assert np.isclose(stats['mean'],np.mean(values),rtol=0,atol=1e-12)
    lo,hi=stats.get('ci95',stats.get('ci95_descriptive'))
    assert lo<=stats['mean']<=hi
    if 'positive_n' in stats:assert stats['positive_n']==sum(v>0 for v in values)


def flat_stats(model,comparison,stats):
    lo,hi=stats.get('ci95',stats.get('ci95_descriptive'))
    return dict(model=model,comparison=comparison,n=stats['n'],mean=stats['mean'],ci_low=lo,ci_high=hi)


def interval(ax,x,stats,color=INK):
    lo,hi=stats.get('ci95',stats.get('ci95_descriptive'))
    ax.errorbar(x,stats['mean'],yerr=[[stats['mean']-lo],[hi-stats['mean']]],fmt='D',color=color,capsize=4,markersize=6,lw=1.5,zorder=5)


def add_bottom_padding(fig,inches):
    """Add lower canvas margin without resizing panels or changing numbers."""
    width,height=fig.get_size_inches();new_height=height+inches
    fig.set_size_inches(width,new_height)
    for ax in fig.axes:
        p=ax.get_position();ax.set_position([p.x0,(p.y0*height+inches)/new_height,p.width,p.height*height/new_height])
    for text in fig.texts:text.set_y((text.get_position()[1]*height+inches)/new_height)
    for artist in fig.artists:
        if isinstance(artist,plt.Line2D) and artist.get_transform() is fig.transFigure:
            artist.set_ydata((np.asarray(artist.get_ydata())*height+inches)/new_height)


class CurrentFigures:
    def __init__(self,source,table,qwen4_completion=None):
        self.table=table
        self.qwen4_completion=qwen4_completion
        path=source(COMPLETION/'analysis/results.json')
        self.result=json.loads(path.read_text(encoding='utf-8'))
        assert self.result['status']=='completed' and self.result['original_reconstruction']['passed'] is True
        self.current=self.result['cohorts'][CURRENT]
        self.rows=[r for r in self.current['per_fact'] if r['split']=='held_out']
        assert [sum(r['domain']==d for r in self.rows) for d in DOMAINS]==[5,5,0]
        validate_stats(self.current['heldout_primary'],[r[PRIMARY] for r in self.rows])
        for key,flag in [('same_template_nonce','same_template_output_type_matches_target'),('paraphrased_nonce','nonce_output_type_matches_target')]:
            validate_stats(self.current['robustness']['output_type_matched_controls'][key],[r[f'feature_jaccard__margin_{key}'] for r in self.rows if r[flag]])
        audit_path=source(COMPLETION/'figure_audit/results.json')
        self.audit=json.loads(audit_path.read_text(encoding='utf-8'))
        assert self.audit['status']=='completed' and self.audit['original_reconciliation']['passed'] is True
        assert self.audit['source_analysis_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        self.display=self.audit['cohorts']['expanded91']
        assert self.display['quality']['graph_n']==91
        assert self.display['answers']['available_factual_graph_n']==50
        assert self.display['lexical']['eligible_evaluation_n']==10
        self.checks=['Current Qwen3-1.7B figures use 91 available graphs and ten included evaluation questions',
                     'Current Qwen3-1.7B plotted summaries reconcile with completed hash-linked saved analyses']

    def quality(self,raw,fmt,conv,ext_audit,save):
        groups=[('Gemma\ncontrolled',[r for r in raw if r.get('model_dir')=='gemma-2-2b']),
                ('Qwen1.7\ncontrolled',None),('Gemma\ncrossed',fmt),
                ('Qwen4\ncontrolled',[r for r in ext_audit if r.get('status')=='ok' and r['design']=='controlled']),
                ('Qwen4\ncrossed',[r for r in ext_audit if r.get('status')=='ok' and r['design']=='crossed'])]
        fig,axes=plt.subplots(1,2,figsize=(12,5.1));fig.subplots_adjust(left=.07,right=.98,bottom=.22,top=.86,wspace=.28)
        exports=[];influence=[]
        for i,(label,rows) in enumerate(groups):
            if i==1:
                stats=self.display['quality'];n=stats['graph_n'];bad=stats['ambiguous_export_n'];vals=stats['error_influence_percent_values']
                assert len(vals)==n and np.isclose(np.median(vals),stats['error_influence_median_percent'])
            else:
                n=len(rows);vals=[100*r['error_influence_fraction'] for r in rows]
                if i<3:bad=sum(r['ambiguous_node_id_count']>0 for r in rows)
                else:
                    design='controlled' if i==3 else 'crossed'
                    bad=sum(r.get('raw_ambiguous_node_id_count',0)>0 for r in conv if r['design']==design and r['status']=='ok')
            rate=100*bad/n;axes[0].bar(i,rate,color=['#0072B2','#A6558C','#56B4E9','#CC651D','#E69F00'][i])
            axes[0].text(i,rate+2,f'{bad}/{n}',ha='center',fontsize=9)
            axes[1].boxplot([vals],positions=[i],widths=.5,showfliers=True,flierprops={'markersize':2},medianprops={'color':'black'})
            exports.append(dict(cohort=label.replace('\n',' '),graphs=n,ambiguous_raw_exports=bad,error_influence_median_percent=float(np.median(vals))))
            influence.extend(dict(cohort=label.replace('\n',' '),graph_index=j,error_influence_percent=v) for j,v in enumerate(vals))
        assert [r['graphs'] for r in exports]==[120,91,27,120 if self.qwen4_completion else 118,27]
        for ax in axes:ax.set_xticks(range(5),[g[0] for g in groups])
        axes[0].set(ylim=(0,85),ylabel='Raw exports with ambiguous node IDs (%)');axes[0].set_title('a  Export identity audit',loc='left')
        axes[1].set_ylabel('Reconstruction-error node influence (%)');axes[1].set_title('b  Residual influence differs by pipeline',loc='left')
        self.table('figureS1_quality',exports);self.table('figureS1_influence_values',influence);save(fig,'figureS1_export_and_error')

    def exploratory(self,sources,saved,size,pairs,save):
        self.equal_counts(sources,saved,size,save);self.lexical(saved,pairs,save);self.answers(saved,save)

    def equal_counts(self,sources,saved,size,save):
        fig,axes=plt.subplots(1,3,figsize=(12,5.7),sharey=True);fig.subplots_adjust(left=.075,right=.98,bottom=.24,top=.82,wspace=.15)
        summaries=[];points=[]
        for i,(ax,model,source) in enumerate(zip(axes,MODELS,sources)):
            included=[r for r in source['per_fact'] if r['split']=='held_out']
            if i==1:
                equal=self.result['equal_count_sensitivity'][CURRENT];assert equal['status']=='computed'
                subset=equal['rows'];sensitivity=equal['summaries']
            else:
                subset=[r for r in size if r['model']==model];sensitivity=[r for r in saved['size'] if r['model']==model]
            block=[]
            for row in sorted(included,key=lambda r:r['pair_id']):
                vals=[row[PRIMARY]]+[float(next(r['mean_margin'] for r in subset if r['fact']==row['pair_id'] and float(r['fraction'])==f)) for f in [1,.5]]
                ax.plot(range(3),vals,color=COLORS[i],alpha=.35,lw=.7,marker='o',ms=3)
                block.append(dict(model=model,fact=row['pair_id'],domain=row['domain'],full_set=vals[0],equal_count=vals[1],half_count=vals[2]))
            stats=[source['heldout_primary']]+[next(s for s in sensitivity if float(s['fraction'])==f) for f in [1,.5]]
            for j,(s,key) in enumerate(zip(stats,['full_set','equal_count','half_count'])):
                validate_stats(s,[r[key] for r in block]);interval(ax,j,s);ax.text(j,.55,f'{s['mean']:.3f}',ha='center')
                summaries.append(flat_stats(model,key,s))
            points.extend(block)
            ax.set(ylim=(-.045,.6),xlim=(-.35,2.35),xticks=range(3),xticklabels=['Full set','Same count\n(K features)','Half that count\n(K/2 features)'])
            ax.tick_params(axis='x',rotation=18,labelsize=9);ax.axhline(0,c='gray',ls='--',lw=1);ax.set_title(f'{LABELS[i]} (n={len(included)})',loc='left')
        axes[0].set_ylabel('Difference in feature overlap\n(same fact minus other facts)')
        fig.text(.075,.065,'Lines = test questions; diamonds = averages; bars = descriptive 95% intervals.',fontsize=9)
        footer='Sampling features does not remove shared words or answers.'
        if not self.qwen4_completion:footer='*Qwen3-4B: 145/147 planned graphs. '+footer
        fig.text(.075,.025,footer,fontsize=9)
        self.table('figureS3_equal_counts',summaries);self.table('figureS3_per_fact',points);save(fig,'figureS3_equal_feature_counts')

    def lexical(self,saved,pairs,save):
        fig,axes=plt.subplots(1,3,figsize=(12,5.7),sharex=True,sharey=True);fig.subplots_adjust(left=.075,right=.98,bottom=.24,top=.74,wspace=.17)
        scatter=[];support=[]
        for i,(ax,model) in enumerate(zip(axes,MODELS)):
            if i==1:rows=self.display['lexical']['scatter'];summaries=self.display['lexical']['summaries']
            else:
                rows=[]
                for fact in sorted({r['target_fact'] for r in pairs if r['model']==model}):
                    subset=[r for r in pairs if r['model']==model and r['target_fact']==fact];own=next(r for r in subset if r['same_fact']=='True')
                    rows.append(dict(fact=fact,domain=own['domain'],own_word_overlap=float(own['word_jaccard']),best_other_word_overlap=max(float(r['word_jaccard']) for r in subset if r['same_fact']=='False')))
                summaries=[r for r in saved['lexical'] if r['model']==model]
            assert all(r['best_other_word_overlap']<r['own_word_overlap'] for r in rows)
            matched=next(s['n'] for s in summaries if s['rule']=='word_caliper_0.05')
            assert matched==sum(abs(r['own_word_overlap']-r['best_other_word_overlap'])<=.05 for r in rows)
            ax.scatter([r['own_word_overlap'] for r in rows],[r['best_other_word_overlap'] for r in rows],color=COLORS[i],s=48,alpha=.7)
            x=np.linspace(0,1,100);ax.fill_between(x,np.maximum(0,x-.05),np.minimum(1,x+.05),color='#DDE6EA',zorder=0);ax.plot(x,x,c='gray',ls='--',lw=1)
            ax.set(xlim=(0,1),ylim=(0,1),xlabel='Word overlap with the\nsame question reworded')
            ax.set_title(f'{LABELS[i]}\n{matched}/{len(rows)} have a control with\nsimilar word overlap',loc='left',fontsize=10)
            scatter.extend(dict(model=model,**{k:r[k] for k in ['fact','domain','own_word_overlap','best_other_word_overlap']}) for r in rows);support.extend(summaries)
        axes[0].set_ylabel('Highest word overlap with\na question about another fact')
        fig.text(.075,.075,'Each point = one test question (points may overlap). Shading = within 0.05 of equal word overlap.',fontsize=9)
        fig.text(.075,.035,'No matched comparison is available under the saved rules; this is not a measured zero effect.',fontsize=9)
        self.table('figureS4_lexical_scatter',scatter);self.table('figureS4_lexical_support',support);save(fig,'figureS4_lexical_support')

    def answers(self,saved,save):
        fig,axes=plt.subplots(1,2,figsize=(12,5.6),gridspec_kw={'width_ratios':[1.1,1]});fig.subplots_adjust(left=.075,right=.91,bottom=.23,top=.81,wspace=.38)
        cats=['whole_answer_next_token','multi_token_prefix_only','next_token_mismatch']
        labels=['Whole expected answer in the first token','Only the beginning matches; whole answer unverified','Different first token'];colors=['#009E73','#E69F00','#8C94A0'];exports=[]
        for i,model in enumerate(MODELS[1:]):
            if i==0:
                answer=self.display['answers'];statuses=answer['statuses'];total=answer['available_factual_graph_n'];assert set(statuses).issubset(cats)
            else:
                answer=self.qwen4_completion['answers'] if self.qwen4_completion else next(r for r in saved['answers'] if r['model']==model and r['design']=='controlled')
                statuses=answer['statuses'];total=sum(statuses.get(cat,0) for cat in cats)
            assert total==[50,60 if self.qwen4_completion else 59][i];bottom=0
            for cat,color in zip(cats,colors):
                value=statuses.get(cat,0);axes[0].bar(i,value,bottom=bottom,color=color,width=.55)
                if value:axes[0].text(i,bottom+value/2,str(value),ha='center',va='center',color='black')
                bottom+=value;exports.append(dict(model=model,category=cat,count=value,unit='available factual-question graphs',total=total))
            assert bottom==total;axes[0].text(i,total+1.5,f'n={total}',ha='center')
        axes[0].set(xticks=[0,1],xticklabels=LABELS[1:],ylim=(0,65),ylabel='Available factual prompt graphs');axes[0].set_title('a  Qwen tokenizer-aware audit',loc='left')
        matrix=np.array([[next(r['strict_match_n'] for r in saved['crossed_output_support'] if r['model']==model and r['domain']==domain) for domain in DOMAINS] for model in [MODELS[0],MODELS[2]]])
        heat=axes[1].imshow(matrix,cmap='Blues',vmin=0,vmax=9,aspect='auto');scale=fig.colorbar(heat,ax=axes[1],fraction=.045,pad=.04,ticks=[0,3,6,9]);scale.set_label('Expected first-token matches (out of 9)',fontsize=9)
        for i in range(2):
            for j in range(3):axes[1].text(j,i,f'{matrix[i,j]}/9',ha='center',va='center',color='white' if matrix[i,j]>=6 else 'black',fontsize=13)
        axes[1].set(xticks=range(3),xticklabels=['Chemistry','Geography','History'],yticks=range(2),yticklabels=['Gemma-2-2B','Qwen3-4B']);axes[1].set_title('b  Expected first-token matches',loc='left')
        fig.legend([plt.Rectangle((0,0),1,1,color=c) for c in colors],labels,loc='lower center',ncol=1,frameon=False,fontsize=9)
        self.table('figureS5_answer_audit',exports);save(fig,'figureS5_answer_audit')

    def collection(self,save):
        collection=[{k:r[k] for k in ['domain','planned_graphs','available_graphs','length_rejected_jobs','complete_four_role_sets']} for r in self.result['collection_by_domain']]
        assert [r['domain'] for r in collection]==DOMAINS and [r['available_graphs'] for r in collection]==[40,40,11]
        assert sum(r['length_rejected_jobs'] for r in collection)==29
        summary=[]
        for domain in DOMAINS:
            rows=[r for r in self.rows if r['domain']==domain]
            if rows:
                stats=self.current['heldout_domains'][domain];validate_stats(stats,[r[PRIMARY] for r in rows])
                summary.append(dict(domain=domain,included_evaluation_facts=len(rows),mean=stats['mean'],ci95_low=stats['ci95'][0],ci95_high=stats['ci95'][1],status='estimated'))
            else:summary.append(dict(domain=domain,included_evaluation_facts=0,mean=None,ci95_low=None,ci95_high=None,status='unavailable'))
        self.table('figureS7_collection',collection);self.table('figureS7_domain_summary',summary)
        self.table('figureS7_per_fact',[dict(pair_id=r['pair_id'],domain=r['domain'],split=r['split'],margin=r[PRIMARY]) for r in self.rows])
        fig,axes=plt.subplots(1,2,figsize=(13.2,6.5),gridspec_kw={'width_ratios':[1,1.16]});fig.subplots_adjust(left=.105,right=.985,top=.79,bottom=.28,wspace=.42)
        y=np.arange(3);ax=axes[0];ax.barh(y,[r['available_graphs'] for r in collection],height=.50,color=DOMAIN_COLORS)
        for i,row in enumerate(collection):ax.text(row['available_graphs']+1,i,f"{row['available_graphs']}/{row['planned_graphs']}",va='center',fontsize=10,color=INK)
        ax.set(yticks=y,yticklabels=[d.title() for d in DOMAINS],ylim=(2.65,-.65),xlim=(0,51),xticks=[0,10,20,30,40],xlabel='Raw graphs available (count)');ax.set_title('a  Graph collection by subject',loc='left',pad=16,fontsize=11);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
        ax=axes[1]
        for i,(domain,s) in enumerate(zip(DOMAINS,summary)):
            vals=[r[PRIMARY] for r in self.rows if r['domain']==domain]
            if not vals:
                ax.text(.02,i,'No complete question/control sets\nNo overlap estimate',transform=ax.get_yaxis_transform(),va='center',color='#6A7882',fontsize=9.5,bbox=dict(facecolor='white',edgecolor='none',pad=2),zorder=5);continue
            ax.scatter(vals,i+np.linspace(-.13,.13,len(vals)),color=DOMAIN_COLORS[i],s=40,zorder=3)
            ax.errorbar(s['mean'],i,xerr=[[s['mean']-s['ci95_low']],[s['ci95_high']-s['mean']]],fmt='D',color=INK,ms=5,capsize=4,zorder=4)
            ax.text(.98,i-.31,f"mean = {s['mean']:.3f}; n={len(vals)}",ha='right',transform=ax.get_yaxis_transform(),fontsize=9.5,color=INK)
        ax.axvline(0,color='#7A8790',lw=1,ls='--',zorder=1)
        ax.set(yticks=y,yticklabels=[d.title() for d in DOMAINS],ylim=(2.65,-.65),xlabel='Difference in feature overlap\n(same fact minus other facts)');ax.set_title('b  Included test questions',loc='left',pad=16,fontsize=11);ax.grid(axis='x',alpha=.15)
        fig.text(.105,.115,'91 raw graphs. Chemistry and geography each include five test questions; history has no complete sets.',fontsize=9,color=INK)
        fig.text(.105,.068,'Points = test questions; diamonds = means; bars = descriptive 95% question-bootstrap intervals.',fontsize=9,color=INK)
        fig.text(.105,.025,'The 29 unavailable history jobs exceeded the hosted token limit. History is unavailable, not a zero effect.',fontsize=9,color=INK)
        save(fig,'figureS7_qwen17_completion')
