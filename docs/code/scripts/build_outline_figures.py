"""Draft six outline-led figures from saved results; no remote or model calls.

Run with .venv-paper-checks/Scripts/python.exe scripts/build_outline_figures.py.
Archived figures and frozen analysis files are never modified.
"""
from pathlib import Path
import csv
import html
import json
import platform
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
import numpy as np

import build_three_model_figure_pack as old

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/model_extension/paper_figures_draft_20261005'
BLUE, ORANGE, GREEN, INK = '#0072B2', '#D55E00', '#009E73', '#203544'
FIGURES = []
HISTORY_COVERAGE = []
TITLES = {
 'figure1_design_and_coverage': 'How we test what shared graph features reflect',
 'figure2_fact_signal': 'Reworded questions about the same fact share more features in the analyzed sample',
 'figure3_fact_and_wording': 'Both the fact and its wording are associated with shared features',
 'figure4_control_comparisons': 'Keeping the wording does not consistently remove the same-fact advantage',
 'figure5_matched_choice': 'The same-fact advantage is smaller when the answer label changes',
 'figure6_failure_cases': 'Selected wrong-answer graphs resemble correct responses producing the same answer',
}
CAPTIONS = {
 'figure1_design_and_coverage': 'A, Illustration of the original comparison: compare a question with a reworded version asking about the same fact and with questions about other facts in the same subject and evaluation split. Extra overlap is the first similarity minus the average of the others. Feature-set Jaccard is the number of shared feature identities divided by their union; zero means no shared features and one means identical feature sets. The wording shown is schematic, not an additional experimental prompt. The original design also includes controls that replace real entities with made-up names. B, Three separate Qwen3-4B follow-ups test answer-label dependence, position-instruction performance, and similarity in selected wrong answers. Arrows show the study sequence, not a causal pathway. The position pilot failed its behavioral gate, motivating the exploratory failure comparison; those selected failures do not estimate population error rates. Original comparisons span three models with uneven subject coverage; panel B was not repeated in all three. Collection counts and exclusion reasons are reported in the separate sample-accounting table. Box colors distinguish labeled comparisons and do not encode numerical magnitudes.',
 'figure2_fact_signal': 'A, Each small point is a test fact included under the fixed comparison rules; the color-and-shape legend identifies subjects. Black diamonds are model-cohort means, with archived 95% intervals from 10,000 fact-bootstrap resamples. The outcome is target-to-own-paraphrase Jaccard minus the mean target-to-other-factual-paraphrase Jaccard within the same domain and split. B, Domain-specific means and corresponding archived fact-bootstrap intervals show uneven coverage. Counts are facts rather than graph pairs, and the same facts recur across models. Means are 0.170 (Gemma-2-2B, n=8), 0.085 (Qwen3-1.7B, n=5), and 0.162 (available Qwen3-4B cases, n=10). These associations do not isolate factual content from shared words or output identity. Different domain compositions preclude a model ranking. The asterisk denotes the incomplete original Qwen3-4B extension. Equal-feature-count sensitivity is reported separately in the supplement and does not preserve positive direction for every Gemma fact.',
 'figure3_fact_and_wording': 'A, Feature-set Jaccard contrasts. B, Exported-influence-weighted cosine contrasts. Each pipeline has 27 crossed graphs: three facts, three formulations, and three domains. The fact contrast subtracts different-fact/different-wording similarity from same-fact/different-wording similarity; the wording contrast uses different-fact/same-wording similarity against the same baseline. Colored points are domain-specific contrasts, not independent replications or confidence intervals. Black diamonds are equally weighted domain means; connecting lines emphasize their descriptive ordering. Pooled Jaccard fact/wording contrasts are 0.074/0.118 in Gemma and 0.101/0.064 in Qwen3-4B. These unfiltered cohorts include differing, incomplete, or non-answer top tokens. Only Qwen3-4B geography meets the strict expected-token rule in all nine cells; its fact and wording contrasts are approximately 0.101 and 0.106. The pooled ordering is not a formal model-by-effect interaction or evidence that one factor universally dominates. Qwen3-1.7B has no crossed cohort.',
 'figure4_control_comparisons': 'A, Prompts using a made-up name in the original wording. B, Prompts using a made-up name in reworded questions. These are the nonce controls; the model-color legend applies to both panels. The outcome is target-to-own-factual-paraphrase Jaccard minus target-to-nonce Jaccard. Positive values favor the factual paraphrase; negative values favor the nonce control. Small points are held-out facts, diamonds are means, and bars are archived descriptive 95% bootstrap intervals. Counts above each group give the number of included test facts for that control, not graphs. Matching uses only broad top-token classes: alphanumeric, whitespace, or punctuation/symbol. It does not equate semantic answer type, exact output identity, confidence, or answer correctness. Same-template means are -0.069 (n=2), -0.014 (n=4), and +0.096 (n=10) for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B, respectively. Small subsets and different domain coverage prevent a universal template explanation. The asterisk denotes the incomplete original Qwen3-4B extension.',
 'figure5_matched_choice': 'Separately frozen, outcome-informed Qwen3-4B chat-framed follow-up. Six country-pair blocks each cross queried country, capital-to-A/B mapping, and wording, with identical word and tokenizer-ID multisets within a block. All 48 top-label decisions match their intended labels. A, Small points and connecting lines show each block\'s balanced fact-associated contrast and descriptive output-label contrast. Diamonds show means. The sole interval is the archived 95% block-bootstrap interval for the primary balanced fact contrast: 0.0303 [0.0265, 0.0338]; the output-label mean is 0.2827. B, The same six blocks decompose the fact contrast into comparisons preserving or changing the output label. Means are 0.0628 and -0.0022, respectively; their equally weighted average is the primary contrast. Diamonds are descriptive means, and no intervals are inferred for these components. Point colors match their x-axis category labels in each panel, rather than representing numerical magnitudes. Panel B uses an expanded vertical scale. Six blocks, not 48 graphs or individual graph pairs, supply inferential replication. The changed-label point estimate is not an equivalence test; the larger output contrast is not a fraction of variance explained. Token inventory matching does not remove all query-order or entity-role binding alternatives.',
 'figure6_failure_cases': 'Exploratory diagnostic of four selected France/Germany cases in hosted Qwen3-4B under the non-thinking next-token setup. A, Correct next-token answers in the 16 new exports: each response format has four prompts naming the country (for example, France) and four naming its position (for example, first). The panel A legend identifies response format; the separate legend for B-C identifies the two correct-response controls and the feature-count check. All eight controls remain correct and all eight selected errors reproduce. These selected cases do not estimate general failure prevalence. B-C, Each ordinal failure is compared with a correct named-country graph preserving the intended country (blue) or the observed output (orange), while keeping the option mapping and country-list order fixed. Circles show feature-set Jaccard; open squares show mean equal-feature-count sensitivity over 200 repetitions. Each connector joins the two comparisons for the same failure. Mean same-output minus same-country differences are 0.1983 for A/B responses and 0.2649 for capital names (equal-count: 0.1851 and 0.2361). All 16 exports and eight triples pass integrity and output-matching checks. Cases and controls are dependent; no population confidence intervals or confirmatory p-values are shown. Named and ordinal prompts are not token-inventory matched. Position matching, mishandled negation, and answer-conditioned structure remain alternative explanations. The intended correct logit is absent from the eight failure exports, not assigned zero attribution.',
}


def save(fig, stem, title=None, caption=None):
    clarify_labels(fig, stem)
    title, caption = TITLES[stem], CAPTIONS[stem]
    fig.suptitle(textwrap.fill(title, 88), x=.055, y=.987, ha='left', va='top',
                 fontsize=14, fontweight='bold', color=INK)
    fig.canvas.draw()
    for ext in ['png', 'svg']:
        fig.savefig(OUT/f'{stem}.{ext}', dpi=220, facecolor='white')
    FIGURES.append(dict(stem=stem, number=len(FIGURES)+1, title=title, legend=caption))
    plt.close(fig)


def clarify_labels(fig, stem):
    """Presentation-only overrides for reused plots; numerical data stay untouched."""
    if stem == 'figure2_fact_signal':
        fig.axes[0].set_title('a  Same-fact advantage for each test fact',loc='left')
        fig.axes[1].set_title('b  Average advantage by subject',loc='left')
        for ax in fig.axes:
            ax.set_ylabel('Extra feature overlap for the same fact\n(Jaccard difference)')
        fig.subplots_adjust(bottom=.25)
        fig.legends[0].set_title('Subject (color and shape)')
        fig.legends[0].set_bbox_to_anchor((.5,.04))
        fig.text(.07,.025,'Points: test facts. Diamonds: means. Bars: 95% intervals. n = number of facts; absent groups are not zero effects.',fontsize=8.5)
    elif stem == 'figure3_fact_and_wording':
        fig.axes[0].set_title('a  Feature overlap',loc='left')
        fig.axes[1].set_title('b  Similarity weighted by feature influence',loc='left',fontsize=11)
        fig.axes[0].set_ylabel('Extra feature overlap\n(Jaccard difference)')
        fig.axes[1].set_ylabel('Extra influence-weighted similarity\n(cosine difference)')
        for ax in fig.axes:
            ax.set_xticklabels(['Same fact','Same wording','Same fact','Same wording'])
        fig.subplots_adjust(bottom=.31)
        fig.legends[0].set_title('Subject (color and shape); black diamonds show the mean')
        fig.legends[0].set_bbox_to_anchor((.5,.06))
        fig.text(.07,.025,'Baseline: different fact AND different wording. Includes non-answer outputs; Qwen3-1.7B was not collected here.',fontsize=8.5)
    elif stem == 'figure4_control_comparisons':
        for ax,t in zip(fig.axes,['a  Made-up name, original wording','b  Made-up name, reworded question']):
            ax.set_title(t,loc='left',fontsize=11)
            ax.set_ylabel('Factual-paraphrase overlap minus\nmade-up-name overlap (Jaccard difference)')
        fig.subplots_adjust(bottom=.29)
        fig.legend(handles=[Line2D([],[],marker='o',ls='',color=c,label=l) for c,l in zip(old.MODEL_COLORS,old.LABELS)],
                   title='Model (color)',loc='lower center',bbox_to_anchor=(.5,.075),ncol=3,frameon=False,fontsize=9)
        fig.texts[0].set_text('Above zero: the factual paraphrase shares more features. Controls match only the broad next-token class.')
        fig.texts[0].set_fontsize(8.5)
    elif stem == 'figure5_matched_choice':
        for ax in fig.axes:
            ax.set_ylabel('Difference in feature overlap\n(Jaccard difference)')
            for tick in ax.get_xticklabels():
                tick.set_color(BLUE if tick.get_position()[0] == 0 else ORANGE)
        fig.axes[0].set_title('a  Same-fact and same-answer advantages',loc='left',fontsize=11)
        fig.axes[1].set_title('b  Same-fact advantage by answer label',loc='left',fontsize=11)
        fig.axes[0].set_xticklabels(['Same fact\n(averaged across labels)','Same answer\nlabel'])
        fig.texts[0].set_text('Colors match the x-axis categories. Points: six country pairs. Diamonds: means. Panel b has a different y-axis scale.')
        fig.texts[0].set_fontsize(8.5)
    elif stem == 'figure6_failure_cases':
        fig.axes[0].set_xticklabels(['Country named\n(e.g., France)','Position named\n(e.g., first)'])
        fig.axes[0].set_ylabel('Correct next-token answers (count)')
        for ax in fig.axes[1:]:
            ax.set_ylabel('Feature overlap (Jaccard)\n0 = none; 1 = identical feature sets')


def box(ax, x, y, w, h, label, color='#EDF3F6', fontsize=10):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012',
                              facecolor=color,edgecolor='#CBD5DC'))
    ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=fontsize,color=INK)


def design(results, matched, failure):
    fig,axes=plt.subplots(1,2,figsize=(12.8,6.5),gridspec_kw={'width_ratios':[1,1.05]})
    fig.subplots_adjust(left=.06,right=.96,bottom=.17,top=.82,wspace=.22)
    ax=axes[0];ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
    ax.set_title('a  Compare the same fact with other facts',loc='left',pad=15,fontsize=11)
    box(ax,.02,.76,.96,.19,'Target question\nThe chemical symbol for gold is ...')
    box(ax,.02,.39,.44,.23,'Same fact\nGold has the\nchemical symbol ...','#E6F2EE')
    box(ax,.54,.39,.44,.23,'Other fact\nIron has the\nchemical symbol ...','#FCEDDF')
    for x in [.24,.76]:ax.annotate('',xy=(x,.64),xytext=(.5,.75),arrowprops=dict(arrowstyle='->',color=INK))
    box(ax,.02,.04,.96,.22,'Extra overlap = similarity to the same fact\nminus average similarity to other facts',fontsize=10)
    ax.text(.5,.31,'Compare questions within the same subject',ha='center',fontsize=9)
    ax=axes[1];ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
    ax.set_title('b  Ask what else could explain the overlap',loc='left',pad=15,fontsize=11)
    box(ax,.035,.73,.93,.22,'Answer-label controls\nDoes the same-fact advantage remain\nwhen the A/B answer label changes?',fontsize=10)
    box(ax,.035,.40,.93,.22,'Position-instruction check\nCan the model correctly select a country\nwhen asked for the first or second one?',fontsize=10)
    box(ax,.035,.07,.93,.22,'Selected wrong-answer comparisons\nDoes overlap follow the intended question\nor the answer actually produced?',fontsize=10)
    for upper,lower in [(.71,.64),(.38,.31)]:
        ax.annotate('',xy=(.5,lower),xytext=(.5,upper),arrowprops=dict(arrowstyle='->',color=INK))
    fig.text(.06,.08,'Original comparisons: three model pipelines, with different subject coverage. Follow-ups in panel b: Qwen3-4B only.',fontsize=9)
    fig.text(.06,.035,'Sample counts, missing graphs, and exclusion reasons are reported separately in the sample-accounting table.',fontsize=9)
    coverage=np.array([[r.get('heldout_domains',{}).get(d,{}).get('n',0) for d in old.DOMAINS] for r in results])
    old.table('figure1_coverage',[dict(model=old.LABELS[i],domain=d,eligible_facts=int(coverage[i,j])) for i in range(3) for j,d in enumerate(old.DOMAINS)])
    old.table('figure1_followups',[dict(study='matched_choice',graphs=48,correct_top_labels=sum(b['correct_n'] for b in matched['blocks'])),dict(study='position_pilot',graphs=0,correct_top_labels=8,behavioral_n=16),dict(study='failure_diagnostic',graphs=failure['valid_graphs'],correct_top_labels=sum(a['correct'] for a in failure['audits']))])
    save(fig,'figure1_design_and_coverage')

def matched_figure(result):
    blocks=sorted(result['blocks'],key=lambda b:b['block'])
    fig,axes=plt.subplots(1,2,figsize=(12,6));fig.subplots_adjust(left=.09,right=.97,bottom=.22,top=.83,wspace=.33)
    specs=[('fact_effect','label_effect'),('fact_same_label','fact_different_label')]
    rows=[]
    for panel,(ax,keys) in enumerate(zip(axes,specs)):
        means=[]
        for i,b in enumerate(blocks):
            offset=(i-2.5)*.034;v=[b['jaccard'][key] for key in keys]
            ax.plot(np.array([0,1])+offset,v,color='#BDC7CE',lw=1,zorder=1)
            for j,(key,val) in enumerate(zip(keys,v)):
                ax.scatter(j+offset,val,color=[BLUE,ORANGE][j],s=36,alpha=.8,zorder=2)
                rows.append(dict(block=b['block'],panel=panel,contrast=key,value=val))
        for j,key in enumerate(keys):
            mean=float(np.mean([b['jaccard'][key] for b in blocks]));means.append(mean)
            ax.scatter(j,mean,c=INK,marker='D',s=50,zorder=4)
            label_y=max(b['jaccard'][key] for b in blocks)+(.016 if panel==0 else .008)
            ax.text(j,label_y,f'{mean:.4f}',ha='center',fontweight='bold',fontsize=11)
        if panel==0:
            lo,hi=result['primary']['ci95'];ax.errorbar(0,means[0],yerr=[[means[0]-lo],[hi-means[0]]],fmt='none',color=INK,capsize=5,zorder=5)
        ax.axhline(0,color='#7A8790',ls='--',lw=1);ax.set_xlim(-.45,1.45)
        ax.set_ylabel('Jaccard contrast');ax.grid(axis='y',alpha=.14)
    axes[0].set(ylim=(-.012,.34),xticks=[0,1],xticklabels=['Balanced fact\ncontrast','Output-label\ncontrast'])
    axes[1].set(ylim=(-.015,.10),xticks=[0,1],xticklabels=['Same answer\nlabel','Changed answer\nlabel'])
    axes[0].set_title('a  Fact and output contrasts',loc='left',pad=12)
    axes[1].set_title('b  Fact contrast by label condition',loc='left',pad=12)
    fig.text(.09,.065,'Small points: six country-pair blocks   •   Diamonds: means   •   Panel b uses an expanded vertical scale',fontsize=9)
    fig.text(.09,.025,'48/48 correct next-token answers. A near-zero estimate does not prove no effect; these differences are not variance explained.',fontsize=8.5)
    old.table('figure5_block_contrasts',rows);save(fig,'figure5_matched_choice')


def failure_figure(result,jobs):
    fig,axes=plt.subplots(1,3,figsize=(14,6),gridspec_kw={'width_ratios':[.75,1,1]})
    fig.subplots_adjust(left=.055,right=.985,bottom=.27,top=.81,wspace=.36)
    audits=result['audits'];ax=axes[0];behavior=[]
    for i,ref in enumerate(['named','ordinal']):
        for j,fmt in enumerate(['label','capital']):
            rows=[a for a in audits if a['reference']==ref and a['response_format']==fmt];correct=sum(a['correct'] for a in rows)
            x=i+(j-.5)*.3;ax.bar(x,correct,width=.26,color=[BLUE,GREEN][j]);ax.text(x,correct+.12,f'{correct}/{len(rows)}',ha='center',fontsize=10)
            behavior.append(dict(reference=ref,response_format=fmt,correct=correct,n=len(rows)))
    ax.set(ylim=(0,4.9),xticks=[0,1],xticklabels=['Named\ncountry','Ordinal\nreference'],ylabel='Correct top-token decisions')
    ax.set_title('a  Selected-case behavior',loc='left',pad=12)
    ax.legend(handles=[Line2D([],[],marker='s',ls='',color=c,label=l) for c,l in [(BLUE,'A/B'),(GREEN,'Capital name')]],frameon=False,fontsize=9,loc='upper right')
    source=[]
    byid={j['job_id']:j for j in jobs}
    order=['f0m1p0w0','f0m0p1w0','f1m0p0w0','f1m1p1w0']
    for ax,fmt,letter in zip(axes[1:],['label','capital'],['b','c']):
        rows=sorted([r for r in result['comparisons'] if r['response_format']==fmt],key=lambda r:order.index(r['case']))
        for i,r in enumerate(rows):
            assert r['clean_eligible'];j=byid[r['job_id']]
            vals=r['jaccard'];ax.plot([i-.12,i+.12],[vals['same_country'],vals['same_output']],c='#AEBBC4',lw=1.5)
            for dx,key,col in [(-.12,'same_country',BLUE),(.12,'same_output',ORANGE)]:
                ax.scatter(i+dx,vals[key],color=col,s=40,zorder=3)
                eq=r['equal_count']['means'][key];ax.scatter(i+dx,eq,facecolors='none',edgecolors=col,marker='s',s=45,zorder=3)
                source.append(dict(job_id=r['job_id'],case=r['case'],format=fmt,comparator=key,jaccard=vals[key],equal_count=eq))
        ax.set(ylim=(0,1),xticks=range(4),xticklabels=['France\nfirst','France\nsecond','Germany\nfirst','Germany\nsecond'],ylabel='Feature-set Jaccard')
        ax.tick_params(axis='x',labelsize=8);ax.set_title(f'{letter}  '+('A/B response' if fmt=='label' else 'Capital-name response'),loc='left',pad=12)
        ax.grid(axis='y',alpha=.14)
    fig.legend(handles=[Line2D([],[],color=BLUE,marker='o',ls='',label='Correct response to the intended country'),Line2D([],[],color=ORANGE,marker='o',ls='',label='Correct response giving the same answer'),Line2D([],[],color=INK,marker='s',markerfacecolor='none',ls='',label='Matched feature counts')],loc='lower center',bbox_to_anchor=(.55,.12),ncol=3,frameon=False,fontsize=8.5)
    fig.text(.055,.06,'One country pair; selected known failures, not a prevalence estimate. Prompts contain requested and excluded positions.',fontsize=9)
    fig.text(.055,.025,'Same-output resemblance does not distinguish position matching from negation errors or output-conditioned structure.',fontsize=9)
    old.table('figure6_behavior',behavior);old.table('figure6_comparisons',source);save(fig,'figure6_failure_cases')


def audit_coverage(results):
    """Explain sample exclusions without changing the frozen inclusion decisions."""
    manifest_path=ROOT/'config/paper_control_manifest.csv'
    old.SOURCES[str(manifest_path.relative_to(ROOT))]=old.digest(manifest_path)
    with manifest_path.open(encoding='utf-8',newline='') as handle:
        planned=[r for r in csv.DictReader(handle) if r['role']=='target' and r['split']=='held_out']
    raw=old.load(old.ORIGINAL/'raw_graph_audit.json')
    ext=old.load(old.EXTENSION/'analysis/graph_audit.json')
    all_rows=[];summary=[];HISTORY_COVERAGE.clear()
    for i,(label,result) in enumerate(zip(old.LABELS,results)):
        graphs=([r for r in raw if r.get('model_dir')==['gemma-2-2b','qwen3-1-7b'][i]]
                if i<2 else [r for r in ext if r.get('design')=='controlled'])
        excluded={r['pair_id']:r for r in result['excluded_pairs']}
        included={r['pair_id'] for r in old.heldout(result)}
        no_comparator=set(result['pairs_without_same_domain_split_comparator'])
        for fact in planned:
            pair=fact['pair_id'];available=[g for g in graphs if g.get('pair_id')==pair and g.get('status')=='ok']
            reason=('included' if pair in included else 'no_graphs_collected' if not available
                    else 'no_same_subject_test_comparator' if pair in no_comparator
                    else excluded[pair]['reason'])
            all_rows.append(dict(model=label,domain=fact['domain'],pair_id=pair,available_graphs=len(available),
                                 planned_graphs=4,included=pair in included,reason=reason,
                                 observed_mismatched_tokens=json.dumps(excluded.get(pair,{}).get('observed_top_tokens',{}))))
        for domain in old.DOMAINS:
            rows=[r for r in all_rows if r['model']==label and r['domain']==domain]
            row=dict(model=label,domain=domain,planned_test_facts=len(rows),planned_test_graphs=4*len(rows),
                     available_test_graphs=sum(r['available_graphs'] for r in rows),included_test_facts=sum(r['included'] for r in rows))
            assert row['included_test_facts']==result.get('heldout_domains',{}).get(domain,{}).get('n',0)
            summary.append(row)
            if domain=='history':HISTORY_COVERAGE.append(row)
    old.table('test_fact_inclusion_audit',all_rows);old.table('test_graph_coverage',summary)
    accounting=['# Questions and graphs available for the original comparison','',
                'This table separates data collection from analysis inclusion. Each subject has five evaluation questions, with four required prompt/control graphs per question. Questions used plus questions not used always equals five. These are not accuracy scores. Development questions and the later follow-up studies are not included in this table.','',
                '| Model | Subject | Graphs available | Graphs planned | Questions used | Questions not used | Reasons questions were not used |',
                '|---|---|---:|---:|---:|---:|---|']
    reason_names={'no_graphs_collected':'No graphs collected','incomplete_roles':'Incomplete prompt/control set',
                  'expected_token_not_top_prediction':'Expected next-token check failed','no_same_subject_test_comparator':'No qualifying comparison question'}
    for row in summary:
        excluded=[r for r in all_rows if r['model']==row['model'] and r['domain']==row['domain'] and not r['included']]
        reasons='; '.join(f'{label}: {sum(r["reason"]==key for r in excluded)}' for key,label in reason_names.items() if any(r['reason']==key for r in excluded)) or 'None'
        accounting.append(f'| {row["model"]} | {row["domain"].title()} | {row["available_test_graphs"]} | {row["planned_test_graphs"]} | {row["included_test_facts"]} | {row["planned_test_facts"]-row["included_test_facts"]} | {reasons} |')
    accounting.extend(['','A failed next-token check does not necessarily mean a wrong completed answer: partial words and alternative continuations can fail this rule. A complete question can still be unused if no second qualifying question remains in its subject and evaluation split.','',
                       'The original Qwen3-4B extension remains incomplete at 145 of 147 total graphs. The asterisk marks this status. Existing results and inclusion rules are unchanged.','',
                       f'[Per-question audit]({(OUT/"tables/test_fact_inclusion_audit.csv").as_posix()})',''])
    (ROOT/'docs/papers/SAMPLE_ACCOUNTING.md').write_text('\n'.join(accounting),encoding='utf-8')


def write_gallery():
    md=['# Draft figure headlines and legends','', '5 October 2026. Six figures follow the integrated outline. Results are drawn from archived analyses; no new experiments or inferential tests were run. PNG files are high-resolution previews; SVG files retain editable vector text and shapes.','',
        'Writing approach: concrete examples before formal comparisons, result-led headlines, explicit controls, and interpretation limits. These principles follow the three papers in docs/writing/references; their wording and causal claims are not copied.','']
    sections=[]
    for f in FIGURES:
        p=(OUT/(f['stem']+'.png')).as_posix();svg=(OUT/(f['stem']+'.svg')).as_posix()
        md.extend([f'## Figure {f["number"]} {f["title"]}','',f'![Figure {f["number"]}]({p})','',f['legend'],'',f'[Editable SVG]({svg})',''])
        sections.append(f'<section><h2>Figure {f["number"]}. {html.escape(f["title"])}</h2><img src="{f["stem"]}.png" alt="{html.escape(f["title"])}"><p>{html.escape(f["legend"])}</p><a href="{f["stem"]}.svg">Editable SVG</a></section>')
    audit_dir=ROOT/'data/model_extension/final_closeout_20261005'
    if (audit_dir/'FIGURE_S6_LEGEND.md').exists():
        md.extend(['## Supplement S6: graph-location sensitivity','',
                   f'![Supplement S6]({(audit_dir/"figureS6_graph_location_sensitivity.png").as_posix()})','',
                   (audit_dir/'FIGURE_S6_LEGEND.md').read_text(encoding='utf-8'),'',
                   'This additional saved-data audit is exploratory. Rebuild with `scripts/plot_closeout_audit.py`; its separate manifest and source tables are in the closeout directory.',''])
    md.extend(['## What the history gaps mean','',f'[Full sample-accounting table]({(ROOT/"docs/papers/SAMPLE_ACCOUNTING.md").as_posix()})','',
               'The separate sample-accounting table distinguishes collected graphs from questions used in the comparison; neither count is model accuracy. Each subject had five planned test facts with four prompt/control graphs per fact. A test fact was reserved for evaluation; this does not mean it was absent from model training.','',
               '| Model | History test graphs available | Test facts included |','|---|---:|---:|'])
    for row in HISTORY_COVERAGE:
        md.append(f'| {row["model"]} | {row["available_test_graphs"]}/{row["planned_test_graphs"]} | {row["included_test_facts"]}/{row["planned_test_facts"]} |')
    md.extend(['', 'Gemma has all 20 history test graphs, and three facts pass the comparison rules. Qwen3-1.7B has no history control set. Qwen3-4B has 18 of 20 graphs, but three facts fail the strict expected-next-token check and the Columbus fact lacks two graphs. The remaining complete fact (the start of World War I) has no qualifying history test comparator. That produces zero included comparisons, not a measured zero effect.','',
               'Some excluded outputs are partial words or alternative continuations (for example, `Bast` rather than `Bastille`); exclusion is not proof of a wrong completed answer. History therefore does not support a three-model comparison in the original main analysis. Keeping that limitation visible is preferable to relaxing the frozen rules after seeing the results.','',
               f'[Per-fact inclusion audit]({(OUT/"tables/test_fact_inclusion_audit.csv").as_posix()}) · [Collected versus included counts]({(OUT/"tables/test_graph_coverage.csv").as_posix()})','',
               'The separately frozen final history follow-up does not change these original counts. Its status and outcome are recorded under `data/model_extension/history_choice_final_v1` and must be reported as a separate cohort.','',
               '## Color and scale conventions','',
               'Figure 1 is a schematic: its boxes are labeled directly and do not encode numerical magnitudes. Sample counts and exclusion reasons are in a separate table, not a heatmap. Figures 2–3 use category legends for subjects, Figure 4 uses a model legend, Figure 5 matches point colors to the labeled x-axis categories, and Figure 6 identifies response formats and comparison groups in separate legends. Category colors have no numerical scale. Jaccard overlap ranges from zero (no shared features) to one (identical feature sets); a Jaccard difference can be negative, and zero means equal overlap for the compared conditions.','',
               '## Reproduction and scope','', 'Run `.venv-paper-checks/Scripts/python.exe scripts/build_outline_figures.py` from the repository root. The figure manifest records source and script hashes, arithmetic checks, dependencies, and output hashes. Source tables contain the values shown in each panel. Existing raw graphs, frozen analyses, and earlier figures are unchanged. Supplemental technical figures remain in their archived packages.','', 'Figure 5 replaces the earlier retrieval-gate wording with expected top-label agreement and adds the conditional fact contrasts. Figure 6 replaces opaque case identifiers with country and requested position; its full identifiers remain in the source tables.',''])
    (ROOT/'docs/writing/FIGURE_HEADLINES_AND_LEGENDS.md').write_text('\n'.join(md),encoding='utf-8')
    (OUT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Draft paper figures</title><style>body{max-width:1250px;margin:35px auto;padding:0 24px;font:17px/1.6 system-ui;color:#203544}h1,h2{line-height:1.25}section{margin:45px 0;padding-top:24px;border-top:1px solid #d8e1e7}img{width:100%;height:auto}a{color:#0072b2}p{max-width:1000px}</style><h1>Draft paper figures and legends</h1><p>5 October 2026 · Archived results · Original figures preserved · No new model runs</p>'+''.join(sections)+'</html>',encoding='utf-8')


def main():
    OUT.mkdir(parents=True,exist_ok=True);old.OUT=OUT;old.SOURCES.clear();old.TABLES.clear();FIGURES.clear()
    old.style();plt.rcParams.update({'axes.titleweight':'semibold','text.color':INK,'axes.labelcolor':INK})
    original=old.load(old.ORIGINAL/'whole_graph_results.json');ext=old.load(old.EXTENSION/'analysis/model_extension_results.json')
    matched=old.load(ROOT/'data/model_extension/matched_choice_chat_v2/qwen3-4b/analysis/results.json')
    failure=old.load(ROOT/'data/model_extension/failure_case_graphs_v1/analysis/results.json')
    jobs=old.load(ROOT/'data/model_extension/failure_case_graphs_v1/jobs.json')
    position=old.load(ROOT/'data/model_extension/position_artifact_diagnostic_20261001/local_audit.json')
    assert position['correct']==8 and position['n_pilot']==16
    results=[original['models']['gemma'],original['models']['qwen'],ext['controlled']]
    crossed=[('Gemma-2-2B',original['format_variation']),('Qwen3-4B',ext['crossed'])]
    checks=old.validate_arithmetic(results,crossed)
    assert len(matched['blocks'])==6 and sum(b['correct_n'] for b in matched['blocks'])==48
    assert all(b['token_bags_identical'] and b['retrieval_eligible'] for b in matched['blocks'])
    for b in matched['blocks']:
        v=b['jaccard'];assert np.isclose((v['fact_same_label']+v['fact_different_label'])/2,v['fact_effect'],atol=1e-12)
    assert np.isclose(np.mean([b['jaccard']['fact_effect'] for b in matched['blocks']]),matched['primary']['mean_fact_effect'],atol=1e-12)
    assert failure['clean_graphs']==16 and failure['clean_comparisons']==8
    assert all(not a['drift'] and a['correct']==(a['reference']=='named') for a in failure['audits'])
    checks.extend(['Matched-choice block arithmetic, token matching and 48/48 top-label agreement verified','Position pilot: 8/16 verified from local audit','Failure diagnostic: 16 clean graphs, eight valid triples, reproduced behavior verified'])
    old.save=save
    audit_coverage(results)
    checks.append('Collected graph counts and per-fact exclusion reasons reconcile with all nine model/subject inclusion counts')
    design(results,matched,failure);old.signal_figure(results);old.crossed_figure(crossed);old.control_figure(results)
    matched_figure(matched);failure_figure(failure,jobs);write_gallery()
    assert len(FIGURES)==6
    for path,h in old.SOURCES.items():assert old.digest(ROOT/path)==h,'Input changed during plotting'
    outputs={str(p.relative_to(OUT)):old.digest(p) for p in OUT.rglob('*') if p.is_file() and p.name!='figure_manifest.json'}
    for f in FIGURES:
        for extn in ['png','svg']:assert (OUT/f'{f["stem"]}.{extn}').stat().st_size>1000
    manifest=dict(date='2026-10-05',source_hashes=old.SOURCES,script_sha256=old.digest(Path(__file__)),
                  helper_sha256=old.digest(Path(old.__file__)),python=platform.python_version(),numpy=np.__version__,matplotlib=matplotlib.__version__,
                  checks=checks,figures=FIGURES,output_hashes=outputs,notes=['Saved-data visual redesign only; no new inferential analysis.','Raw and frozen result artifacts unchanged.'])
    (OUT/'figure_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Built {len(FIGURES)} PNG/SVG figures with source tables and legends: {OUT}')


if __name__=='__main__':main()
