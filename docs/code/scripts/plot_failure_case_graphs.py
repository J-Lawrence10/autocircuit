"""Reproducible exploratory figures and a source-grounded findings memo."""
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from failure_case_design import ROOT,OUT,MODEL,make_jobs
from control_io import atomic_json
from analyze_matched_choice_controls import csv_write


def save(fig,name):
    dest=OUT/'figures';dest.mkdir(parents=True,exist_ok=True)
    for ext in ['png','svg']:fig.savefig(dest/f'{name}.{ext}',dpi=180,bbox_inches='tight')
    plt.close(fig)


def comparison_figure(result):
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    source=[]
    for ax,fmt in zip(axes,['label','capital']):
        rows=[r for r in result['comparisons'] if r['response_format']==fmt]
        for i,r in enumerate(rows):
            if 'jaccard' not in r:continue
            v=r['jaccard'];clean=r['clean_eligible']
            ax.plot([i-.12,i+.12],[v['same_country'],v['same_output']],color='.7',zorder=1)
            for dx,key,color in [(-.12,'same_country','#0072B2'),(.12,'same_output','#D55E00')]:
                ax.scatter(i+dx,v[key],c=color,marker='o' if clean else 'x',s=65)
                if 'equal_count' in r:ax.scatter(i+dx,r['equal_count']['means'][key],facecolors='none',edgecolors=color,marker='s',s=80)
                source.append(dict(job_id=r['job_id'],comparison=key,jaccard=v[key],clean_eligible=clean,
                                   equal_count=r.get('equal_count',{}).get('means',{}).get(key)))
        ax.set_xticks(range(len(rows)),[r['case'] for r in rows],rotation=30,ha='right')
        ax.set_ylim(0,1);ax.set_ylabel('Feature-set Jaccard');ax.set_title('A/B response' if fmt=='label' else 'Capital-name response')
    fig.suptitle('Failure versus same-country (blue) and same-output (orange) controls\nSquares: equal-count sensitivity; crosses: not eligible for clean comparison',fontsize=11)
    save(fig,'feature_comparisons');csv_write(OUT/'analysis/figure_comparison_source.csv',source)


def category(row):
    if row['source_type']=='reconstruction_error':return 'Reconstruction error'
    role=row['source_role']
    if role.startswith('option_'):return 'Answer options'
    if role.startswith('country_list'):return 'Country list'
    if role.startswith('question_country'):return 'Named country in question'
    if role.startswith('ordinal_'):return 'Ordinal word'
    if role=='chat_frame':return 'Chat frame'
    if role=='unmapped':return 'Unmapped'
    return 'Other prompt tokens'


def role_figure(result):
    names=['Answer options','Country list','Named country in question','Ordinal word','Chat frame','Other prompt tokens','Reconstruction error','Unmapped']
    colors=['#0072B2','#009E73','#56B4E9','#E69F00','#999999','#CC79A7','#222222','#D55E00']
    rows=result['audits'];fig,axes=plt.subplots(1,2,figsize=(16,9),layout='constrained');source=[]
    for ax,feature_only in zip(axes,[False,True]):
        sums=[]
        for r in rows:
            groups=r.get('source_role_totals',[])
            valid=[g for g in groups if not feature_only or g['source_type']=='feature']
            total=sum(g['absolute_weight'] for g in valid)
            vals=[sum(g['absolute_weight'] for g in valid if category(g)==name)/total if total else 0 for name in names]
            sums.append(vals)
            source.extend(dict(job_id=r['job_id'],feature_only=feature_only,category=n,fraction=v if total else None,
                               absolute_denominator=total) for n,v in zip(names,vals))
        values=np.array(sums);left=np.zeros(len(rows))
        for i,(name,color) in enumerate(zip(names,colors)):
            ax.barh(range(len(rows)),values[:,i],left=left,color=color,label=name);left+=values[:,i]
        for i,r in enumerate(rows):
            if left[i]==0:ax.text(.02,i,'Unavailable or zero denominator',va='center',fontsize=8)
        ax.set_yticks(range(len(rows)),[r['job_id']+(' *' if not r['clean_eligible'] else '') for r in rows],fontsize=7)
        ax.invert_yaxis();ax.set_xlim(0,1);ax.set_xlabel('Fraction of absolute direct incoming edge weight')
        ax.set_title('Feature sources only' if feature_only else 'All source types, errors visible')
    axes[1].legend(loc='upper left',bbox_to_anchor=(1.01,1),fontsize=8)
    fig.suptitle('Observed-answer logit: source token roles (local attribution, not causal contribution)\n* marks exports not meeting clean integrity criteria')
    save(fig,'answer_source_roles');csv_write(OUT/'analysis/figure_role_source.csv',source)


def graph_panel(ax,job,audit):
    folder=OUT/MODEL/'graphs'/job['job_id'];p=folder/'local_neighborhood.json'
    ax.set_axis_off()
    title=f'{job["queried_country"]}: {job["reference"]}, {job["response_format"]}\nExpected {job["expected_label"]}; observed {audit.get("observed","unavailable")}'
    if not audit.get('clean_eligible'):title+='\nIntegrity sensitivity only'
    ax.set_title(title,fontsize=10)
    if not p.exists():ax.text(.1,.5,'No valid local graph');return
    info=json.loads(p.read_text())
    if info['status']!='ok':ax.text(.1,.5,info['status']);return
    edges=info['selected_edges'];target=info['observed_logit_id']
    direct=sorted({e['source'] for e in edges if e['depth']==1})
    upstream=sorted({e['source'] for e in edges if e['depth']==2}-set(direct)-{target})
    positions={target:(1.,.5)}
    for ids,x in [(upstream,0),(direct,.5)]:
        for n,y in zip(ids,np.linspace(.05,.95,len(ids))):positions[n]=(x,float(y))
    records={e['source']:e for e in edges}
    maximum=max([e['absolute_weight'] for e in edges],default=1) or 1
    for e in edges:
        if e['source'] not in positions or e['target'] not in positions:continue
        ax.annotate('',xy=positions[e['target']],xytext=positions[e['source']],
                    arrowprops=dict(arrowstyle='->',color='#0072B2' if e['weight']>=0 else '#D55E00',
                                    lw=.5+2*e['absolute_weight']/maximum,alpha=.55),zorder=1)
    for n,(x,y) in positions.items():
        e=records.get(n,{});error=e.get('source_type')=='reconstruction_error'
        ax.scatter(x,y,s=38,c='#222222' if error else '#009E73',zorder=3)
        label=('LOGIT '+audit.get('observed','')) if n==target else f'{e.get("source_role","unknown")}\n{n}'
        ax.text(x,y+.024,label,ha='center',va='bottom',fontsize=5.8,bbox=dict(facecolor='white',alpha=.7,edgecolor='none',pad=.2),zorder=4)
    ax.set_xlim(-.23,1.23);ax.set_ylim(-.08,1.12)
    omitted=sum(r['omitted_abs_weight'] for r in info['omitted_by_target'])
    ax.text(.5,-.055,f'Blue + / orange -; black nodes: errors\nOmitted absolute weight across displayed targets: {omitted:.3g}',ha='center',fontsize=7)


def main():
    plt.rcParams.update({'svg.fonttype':'none','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    result=json.loads((OUT/'analysis/results.json').read_text());jobs=make_jobs();byid={j['job_id']:j for j in jobs};audits={r['job_id']:r for r in result['audits']}
    comparison_figure(result);role_figure(result)
    for job in jobs:
        if job['reference']!='ordinal':continue
        fig,axes=plt.subplots(1,3,figsize=(19,9),layout='constrained')
        for ax,jid in zip(axes,[job['job_id'],job['same_country_partner'],job['same_output_partner']]):graph_panel(ax,byid[jid],audits[jid])
        fig.suptitle('Failure | same intended country | same preview output\nTwo-step retained-edge neighborhoods; descriptive, thresholded exports',fontsize=12)
        save(fig,'neighborhood_'+job['job_id'])
    clean=[r for r in result['comparisons'] if r['clean_eligible']]
    drift=sum(r.get('drift',False) for r in result['audits']);reproduced=sum(r.get('observed')==r['preview'] for r in result['audits'])
    lines=['# Findings from the failure case graphs','',
           'This is an exploratory diagnostic of selected France/Germany failures. It does not change the original experiments or establish a causal mechanism.','',
           '## Completion and integrity','',
           f'- {result["valid_graphs"]}/16 graphs were analyzable; {result["clean_graphs"]}/16 met the clean integrity criteria.',
           f'- {reproduced}/16 exported answers matched the earlier diagnostic; {drift} changed.',
           f'- {len(clean)}/8 comparison triples met integrity, wrong-answer, correct-comparator, and observed-output-matching requirements.','',
           '## Feature composition','']
    for fmt in ['label','capital']:
        rows=[r for r in clean if r['response_format']==fmt]
        if rows:
            diff=np.mean([r['jaccard']['output_minus_country'] for r in rows])
            eq=np.mean([r['equal_count']['means']['output_minus_country'] for r in rows])
            lines.append(f'- {fmt}: mean same-output minus same-country Jaccard difference {diff:.4f} across {len(rows)} selected cases; equal-count sensitivity {eq:.4f}. These are descriptive, dependent comparisons.')
        else:lines.append(f'- {fmt}: no fully eligible comparison triples; no pooled estimate reported.')
    local=[r for r in result['audits'] if r.get('local',{}).get('direct_error_fraction') is not None and r['clean_eligible']]
    lines.extend(['','## Local graph coverage',''])
    if local:
        values=[r['local']['direct_error_fraction'] for r in local]
        lines.append(f'Reconstruction-error sources contributed a median {np.median(values):.1%} of absolute direct incoming weight to the observed answer logit across {len(local)} clean graphs (range {min(values):.1%} to {max(values):.1%}). This is local exported weight, not explained variance or a causal effect.')
    else:lines.append('Clean local answer-logit attribution fractions were unavailable.')
    lines.extend(['',f'The intended correct logit was unavailable in {sum(not r.get("correct_logit_available",False) for r in result["audits"] if r["status"]=="ok")} analyzable exports. Absence is not zero influence.',
                  '', '## What the evidence can establish','',
                  'The figures and complete tables show whether the failures resemble correct same-output responses, and where the retained local answer-logit edges originate. Similarity alone cannot distinguish a position shortcut from output-conditioned structure. Token location does not establish feature semantics. Candidate mechanisms require independent review and causal intervention, not labels assigned from these pictures.',
                  '', 'All cases are shown, including drift, exclusions, and unavailable comparisons. There is one country pair, not sixteen independent replications. No confirmatory p-values or population confidence intervals are reported.',
                  '', '## Reproduction','',
                  'Run scripts/analyze_failure_case_graphs.py, scripts/plot_failure_case_graphs.py, and scripts/validate_failure_case_graphs.py using the archived environment. These stages read saved graphs and do not request new ones. The generation runner is scripts/run_failure_case_graphs.py; it reuses saved responses and verified raw files.',
                  '', 'Review analysis/graph_audit.csv, analysis/comparisons.csv, per-graph source_role_totals.csv and direct_answer_edges.csv, and all neighborhood panels before selecting any candidate intervention. No automatic follow-up collection or manuscript claim changes were made.'])
    (OUT/'FINDINGS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    atomic_json(OUT/'analysis/figure_manifest.json',{'figures':[str(p.relative_to(OUT)) for p in sorted((OUT/'figures').glob('*'))],
                'main_neighborhoods':['neighborhood_f0m1p0w0_ordinal_label','neighborhood_f0m1p0w0_ordinal_capital'],
                'note':'Main examples fixed in the plan; all eight triples retained.'})


if __name__=='__main__':main()
