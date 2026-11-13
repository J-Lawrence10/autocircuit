#!/usr/bin/env python3
"""Rebuild the three-model paper figure pack from archived results; no model/API calls.

Preserves original estimates. Validates tabular arithmetic and records source hashes.
Optional --verify-raw checks every archived raw file against the recorded checksum.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
import numpy as np
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'data/publication_analysis'
EXTENSION = ROOT / 'data/model_extension/qwen3-4b'
OUT = ROOT / 'data/model_extension/paper_figures'
LABELS = ['Gemma-2-2B', 'Qwen3-1.7B', 'Qwen3-4B*']
MODEL_COLORS = ['#0072B2', '#A6558C', '#CC651D']
DOMAINS = ['chemistry', 'geography', 'history']
DOMAIN_COLORS = ['#0072B2', '#009E73', '#CC651D']
MARKERS = ['o', 's', '^']
PRIMARY = 'feature_jaccard__margin_other_factual_mean'
SOURCES = {}
TABLES = {}
FIGURES = []


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    data = path.read_bytes()
    SOURCES[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return json.loads(data)


def table(name, rows):
    TABLES[name] = rows
    path = OUT / 'tables' / f'{name}.csv'
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def release_status(audits):
    """Statistical thresholds cannot override missing registered inputs."""
    counts = {d: sum(r.get('design') == d and r.get('status') == 'ok' for r in audits)
              for d in ['controlled', 'crossed']}
    unique_jobs = len({r.get('job_id') for r in audits}) == len(audits)
    complete = counts == {'controlled': 120, 'crossed': 27} and len(audits) == 147 and unique_jobs
    return {'controlled_ok': counts['controlled'], 'crossed_ok': counts['crossed'],
            'full_cohort_complete': complete,
            'interpretation': 'complete' if complete else 'incomplete_extension',
            'missing_or_failed_jobs': [r['job_id'] for r in audits if r.get('status') != 'ok']}


def style():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
        'axes.titlesize': 12, 'axes.labelsize': 10, 'xtick.labelsize': 9,
        'ytick.labelsize': 9, 'axes.spines.top': False, 'axes.spines.right': False,
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
        'savefig.facecolor': 'white'})


def save(fig, stem, title, caption):
    fig.savefig(OUT / f'{stem}.png', dpi=220)
    fig.savefig(OUT / f'{stem}.pdf')
    fig.savefig(OUT / f'{stem}.svg')
    FIGURES.append({'stem': stem, 'title': title, 'caption': caption})
    plt.close(fig)


def interval(ax, x, s, color='black', label=None):
    if not s.get('n'):
        return
    lo, hi = s['ci95']
    ax.errorbar(x, s['mean'], yerr=[[s['mean']-lo], [hi-s['mean']]],
                fmt='D', color=color, capsize=4, markersize=6, lw=1.5, label=label, zorder=5)


def heldout(result):
    return [r for r in result['per_fact'] if r['split'] == 'held_out']


def validate_arithmetic(results, crossed):
    checks = []
    for label, r in zip(LABELS, results):
        rows = heldout(r)
        s = r['heldout_primary']
        assert len(rows) == s['n'], label
        assert np.isclose(np.mean([v[PRIMARY] for v in rows]), s['mean'], atol=1e-12), label
        assert sum(v[PRIMARY] > 0 for v in rows) == s['positive_n'], label
        for control, flag in [('same_template_nonce', 'same_template_output_type_matches_target'),
                              ('paraphrased_nonce', 'nonce_output_type_matches_target')]:
            values = [v[f'feature_jaccard__margin_{control}'] for v in rows if v[flag]]
            s2 = r['robustness']['output_type_matched_controls'][control]
            assert len(values) == s2['n']
            assert np.isclose(np.mean(values), s2['mean'], atol=1e-12)
        checks.append(f'{label}: held-out and control table arithmetic consistent')
    for label, r in crossed:
        for metric, s in r['metrics'].items():
            cats = s['categories']
            base = cats['different_fact_different_format']['domain_means']
            for effect, category in [('fact', 'same_fact_different_format'), ('format', 'different_fact_same_format')]:
                v = np.mean([cats[category]['domain_means'][d] - base[d] for d in DOMAINS])
                assert np.isclose(v, s[f'{effect}_effect'], atol=1e-12)
        checks.append(f'{label}: crossed effect arithmetic consistent')
    return checks


def design_figure(results, original_audit, extension_audit):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.7), gridspec_kw={'width_ratios': [1.15, 1]})
    fig.subplots_adjust(left=.06, right=.98, bottom=.16, top=.86, wspace=.32)
    ax = axes[0]; ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title('a  What is the fair comparison?', loc='left', pad=18)
    boxes = [(.03,.72,.93,.19, 'Target: The chemical symbol for gold is', '#EAF2F7'),
             (.03,.41,.43,.21, 'Same fact, new wording\nGold has the chemical symbol', '#E5F2EC'),
             (.53,.41,.43,.21, 'Other facts, new wording\nIron has the chemical symbol', '#F4ECF1'),
             (.03,.07,.93,.20, 'Fact margin = similarity to own paraphrase\nminus mean similarity to other factual paraphrases', '#F1F3F5')]
    for x,y,w,h,t,c in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.01',facecolor=c,edgecolor='#C8D0D7'))
        ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=9.5,wrap=True)
    for x in [.245,.745]:
        ax.annotate('', xy=(x,.64), xytext=(.495,.71), arrowprops={'arrowstyle':'->','color':'#455566'})
        ax.annotate('', xy=(.495,.285), xytext=(x,.4), arrowprops={'arrowstyle':'->','color':'#455566'})
    ax = axes[1]
    coverage = np.array([[r.get('heldout_domains',{}).get(d,{}).get('n',0) for d in DOMAINS] for r in results])
    ax.imshow(coverage, cmap='Blues', vmin=0, vmax=5, aspect='auto')
    for i in range(3):
        for j in range(3):
            ax.text(j,i,str(coverage[i,j]) if coverage[i,j] else 'No eligible\ncomparison',
                    ha='center',va='center',color='white' if coverage[i,j]>=4 else '#263645',fontsize=10)
    ax.set_xticks(range(3),[d.title() for d in DOMAINS]); ax.set_yticks(range(3),LABELS)
    ax.set_title('b  Eligible held-out facts',loc='left',pad=18)
    fig.text(.06,.04,'Comparators stay within domain and split.  *Qwen3-4B: 118/120 controlled + 27/27 crossed graphs.',fontsize=10)
    table('figure1_domain_coverage', [{'model':LABELS[i],'domain':d,'heldout_n':int(coverage[i,j])} for i in range(3) for j,d in enumerate(DOMAINS)])
    save(fig,'figure1_design_and_coverage','Study design and the evidence actually available',
         'Schematic uses illustrative prompts from the manifest. The controlled test compares each target with its own paraphrase and the mean of other eligible factual paraphrases in the same domain and split. All four prompt roles and exact expected top-token agreement for target and paraphrase are required. Counts are facts, not graphs. Zero denotes no eligible comparison; Qwen3-1.7B lacks complete non-chemistry control sets. Qwen3-4B remains an incomplete extension (145/147 graphs).')


def signal_figure(results):
    fig, axes = plt.subplots(1,2,figsize=(12,5.5))
    fig.subplots_adjust(left=.07,right=.98,bottom=.2,top=.86,wspace=.3)
    ax=axes[0]; summary_rows=[]; point_rows=[]
    for i,(label,r) in enumerate(zip(LABELS,results)):
        rows=heldout(r)
        for j,row in enumerate(rows):
            di=DOMAINS.index(row['domain'])
            ax.scatter(i-.22+.44*j/max(1,len(rows)-1),row[PRIMARY],color=DOMAIN_COLORS[di],marker=MARKERS[di],s=35)
            point_rows.append({'model':label,**row})
        s=r['heldout_primary']; interval(ax,i,s)
        ax.text(i,.58,f'n={s["n"]}\nmean {s["mean"]:.3f}',ha='center',va='top')
        summary_rows.append({'model':label,**{k:s[k] for k in ['n','mean','positive_n','exact_one_sided_sign_flip_p']},'ci_low':s['ci95'][0],'ci_high':s['ci95'][1]})
    ax.set_ylim(-.02,.62); ax.axhline(0,color='gray',ls='--',lw=1)
    ax.set_xticks(range(3),LABELS,rotation=12); ax.set_ylabel('Same-fact advantage (Jaccard difference)')
    ax.set_title('a  Positive margins in all eligible facts',loc='left')
    axes[1].set_title('b  Domain estimates reveal uneven coverage',loc='left')
    ax=axes[1]
    for i,r in enumerate(results):
        for j,d in enumerate(DOMAINS):
            s=r['heldout_domains'].get(d,{})
            if s.get('n'):
                interval(ax,i+(j-1)*.20,s,DOMAIN_COLORS[j])
                ax.annotate(f'n={s["n"]}',(i+(j-1)*.2,s['ci95'][1]),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
    ax.axhline(0,color='gray',ls='--',lw=1); ax.set_ylim(-.02,.56)
    ax.set_xticks(range(3),LABELS,rotation=12); ax.set_ylabel('Same-fact advantage (Jaccard difference)')
    handles=[Line2D([],[],marker=MARKERS[j],color=DOMAIN_COLORS[j],ls='',label=d.title()) for j,d in enumerate(DOMAINS)]
    fig.legend(handles=handles,loc='lower center',ncol=3,bbox_to_anchor=(.5,.005),frameon=False)
    table('figure2_summary',summary_rows); table('figure2_fact_level',point_rows)
    save(fig,'figure2_fact_signal','A fact-associated feature signal appears in three models',
         'Dots are individual held-out facts; diamonds and bars are means and archived 10,000-resample fact-bootstrap 95% intervals. Exact one-sided sign-flip p-values are 0.00390625 (Gemma), 0.03125 (Qwen3-1.7B), and 0.0009765625 (Qwen3-4B available cases). Exact within-domain label permutations provide a complementary specificity test. Domain/sample composition differs across models, so pooled effect heights are not a model ranking. *The Qwen3-4B controlled cohort is incomplete; positive statistical criteria do not constitute a full completion-gate pass.')


def crossed_figure(crossed):
    fig,axes=plt.subplots(1,2,figsize=(12,5.6)); fig.subplots_adjust(left=.07,right=.98,bottom=.23,top=.86,wspace=.28)
    rows=[]
    for ax,(metric,metric_label) in zip(axes,[('feature_jaccard','Jaccard'),('feature_influence_cosine','Influence-weighted cosine')]):
        for i,(label,r) in enumerate(crossed):
            s=r['metrics'][metric]; cats=s['categories']; base=cats['different_fact_different_format']['domain_means']
            for j,(effect,cat) in enumerate([('fact','same_fact_different_format'),('format','different_fact_same_format')]):
                x=i*3+j; values=[]
                for di,d in enumerate(DOMAINS):
                    value=cats[cat]['domain_means'][d]-base[d]; values.append(value)
                    ax.scatter(x+(di-1)*.12,value,color=DOMAIN_COLORS[di],marker=MARKERS[di],s=45,zorder=4)
                    rows.append({'model':label,'metric':metric,'effect':effect,'domain':d,'effect_value':value,
                        'pooled_effect':s[f'{effect}_effect'],'permutation_p_raw':s[f'{effect}_effect_permutation_p']})
                ax.scatter(x,np.mean(values),marker='D',c='black',s=40,zorder=5)
                ax.text(x,.23,f'{np.mean(values):.3f}',ha='center',fontsize=10)
            ax.plot([i*3,i*3+1],[s['fact_effect'],s['format_effect']],color='#8C96A0',lw=1)
        ax.axhline(0,color='gray',ls='--',lw=1); ax.set_ylim(-.01,.26)
        ax.set_xticks([0,1,3,4],['Fact','Wording','Fact','Wording']); ax.set_ylabel(f'Effect above baseline ({metric_label})')
        ax.set_title(('a  ' if metric=='feature_jaccard' else 'b  ')+metric_label,loc='left')
        ax.text(.5,-.16,'Gemma-2-2B',transform=ax.get_xaxis_transform(),ha='center')
        ax.text(3.5,-.16,'Qwen3-4B',transform=ax.get_xaxis_transform(),ha='center')
    handles=[Line2D([],[],marker=MARKERS[j],color=DOMAIN_COLORS[j],ls='',label=d.title()) for j,d in enumerate(DOMAINS)]
    handles.append(Line2D([],[],marker='D',color='black',ls='',label='Across-domain mean'))
    fig.legend(handles=handles,ncol=4,loc='lower center',frameon=False)
    table('figure3_crossed_effects',rows)
    save(fig,'figure3_fact_and_wording','Both fact and wording contribute; the pooled ordering differs',
         'Each pipeline has 27 graphs (three domains x three facts x three formulations). Fact effect: same fact/different formulation minus different fact/different formulation. Wording effect: different fact/same formulation minus that baseline. Colored points are domain effects, not confidence intervals; black diamonds are domain means. In Gemma, binary fact/wording effects are 0.074/0.118; in Qwen3-4B they are 0.101/0.064. Ordering is descriptive, without a formal model-by-effect interaction test. These crossed graphs are not filtered by successful full-answer retrieval, and output format can differ. Qwen3-1.7B has no crossed cohort.')


def control_figure(results):
    fig,axes=plt.subplots(1,2,figsize=(12,5.2)); fig.subplots_adjust(left=.07,right=.98,bottom=.21,top=.84,wspace=.28)
    rows=[]
    for ax,(control,title) in zip(axes,[('same_template_nonce','a  Nonce keeps target wording'),('paraphrased_nonce','b  Nonce uses paraphrased wording')]):
        for i,r in enumerate(results):
            s=r['robustness']['output_type_matched_controls'][control]
            interval(ax,i,s,MODEL_COLORS[i])
            for j,v in enumerate(s['values']):
                ax.scatter(i-.14+.28*j/max(1,s['n']-1),v,color=MODEL_COLORS[i],alpha=.6,s=20)
            ax.text(i,.295,f'n={s["n"]}',ha='center')
            rows.append({'model':LABELS[i],'control':control,'mean':s['mean'],'n':s['n'],'ci_low':s['ci95'][0],'ci_high':s['ci95'][1],
                         'matching_rule':'same broad token class; not same semantic output'})
        ax.axhline(0,color='gray',ls='--',lw=1); ax.set_ylim(-.13,.33)
        ax.set_xticks(range(3),LABELS,rotation=12); ax.set_title(title,loc='left'); ax.set_ylabel('Own-paraphrase similarity minus nonce similarity')
    fig.text(.07,.04,'Positive: own factual paraphrase is more similar.  Matching groups all alphanumeric tokens together.',fontsize=10)
    table('figure4_controls',rows)
    save(fig,'figure4_control_comparisons','Same-template controls do not have a universal effect',
         'Held-out comparisons restricted to controls with the same broad top-token class as the target. Classes distinguish alphanumeric, whitespace, and punctuation/symbol tokens; they do not match semantic answer type, exact token, or token probability. Diamonds/bars show archived means/bootstrap 95% intervals; dots show facts. Same-template margins are -0.069 (n=2), -0.014 (n=4), and +0.096 (n=10). Small original subsets and different domain coverage preclude a general claim that templates erase factual similarity. Error bars are descriptive; negative intervals here are not a preregistered two-sided rejection test.')


def quality_figure(raw,fmt,conv,ext_audit):
    groups=[('Gemma\ncontrolled',[r for r in raw if r.get('model_dir')=='gemma-2-2b']),
            ('Qwen1.7\ncontrolled',[r for r in raw if r.get('model_dir')=='qwen3-1-7b']),
            ('Gemma\ncrossed',fmt),
            ('Qwen4\ncontrolled',[r for r in ext_audit if r.get('status')=='ok' and r['design']=='controlled']),
            ('Qwen4\ncrossed',[r for r in ext_audit if r.get('status')=='ok' and r['design']=='crossed'])]
    assert [len(g[1]) for g in groups]==[120,50,27,118,27]
    fig,axes=plt.subplots(1,2,figsize=(12,5.1)); fig.subplots_adjust(left=.07,right=.98,bottom=.22,top=.86,wspace=.28)
    audit_rows=[]
    for i,(label,rows) in enumerate(groups):
        if i<3:
            bad=sum(r['ambiguous_node_id_count']>0 for r in rows)
        else:
            design='controlled' if i==3 else 'crossed'
            bad=sum(r.get('raw_ambiguous_node_id_count',0)>0 for r in conv if r['design']==design and r['status']=='ok')
        rate=100*bad/len(rows); axes[0].bar(i,rate,color=['#0072B2','#A6558C','#56B4E9','#CC651D','#E69F00'][i])
        axes[0].text(i,rate+2,f'{bad}/{len(rows)}',ha='center',fontsize=9)
        vals=[100*r['error_influence_fraction'] for r in rows]
        axes[1].boxplot([vals],positions=[i],widths=.5,showfliers=True,
                        flierprops={'markersize':2},medianprops={'color':'black'})
        audit_rows.append({'cohort':label.replace('\n',' '),'graphs':len(rows),'ambiguous_raw_exports':bad,
                           'error_influence_median_percent':float(np.median(vals))})
    for ax in axes: ax.set_xticks(range(5),[g[0] for g in groups])
    axes[0].set_ylim(0,85); axes[0].set_ylabel('Raw exports with ambiguous node IDs (%)'); axes[0].set_title('a  Export identity audit',loc='left')
    axes[1].set_ylabel('Reconstruction-error node influence (%)'); axes[1].set_title('b  Residual influence differs by pipeline',loc='left')
    table('figureS1_quality',audit_rows)
    save(fig,'figureS1_export_and_error','Exporter ambiguity and reconstruction error bound interpretation',
         'Ambiguity rates use raw exports; zero means none detected in the available files. Boxplots show medians, quartiles, 1.5-IQR whiskers, and outliers. Original distributions use raw-audit definitions; the Qwen3-4B converted graphs have no ambiguous IDs removed. Error influence is a fraction of absolute nonterminal node influence, not a causal fraction of output explained. Results are model-exporter-decomposition comparisons and cannot isolate architecture or parameter-count effects.')


def robustness_figure(results):
    specs=[('Primary',lambda r:r['heldout_primary']),
           ('Errors included',lambda r:r['robustness']['error_inclusive_heldout']['feature_jaccard_with_errors']),
           ('Clean exports',lambda r:r['robustness']['clean_export_heldout_primary']),
           ('Hardest other fact',lambda r:r['aggregates']['held_out']['feature_jaccard']['margin_other_factual_max'])]
    fig,axes=plt.subplots(1,3,figsize=(12,5));fig.subplots_adjust(left=.07,right=.98,bottom=.23,top=.83,wspace=.3)
    rows=[]
    for i,(ax,r) in enumerate(zip(axes,results)):
        for j,(label,fn) in enumerate(specs):
            s=fn(r);interval(ax,j,s,MODEL_COLORS[i]);ax.text(j,s['ci95'][1]+.018,f'n={s["n"]}',ha='center',fontsize=8)
            rows.append({'model':LABELS[i],'sensitivity':label,'n':s['n'],'mean':s['mean'],'ci_low':s['ci95'][0],'ci_high':s['ci95'][1]})
        ax.axhline(0,c='gray',ls='--',lw=1);ax.set_ylim(-.03,.36);ax.set_xlim(-.35,3.35)
        ax.set_xticks(range(4),[s[0] for s in specs],rotation=35,ha='right');ax.set_title(LABELS[i],loc='left');ax.set_ylabel('Same-fact advantage (Jaccard difference)')
    table('figureS2_robustness',rows)
    save(fig,'figureS2_robustness','The positive direction survives representation checks',
         'Archived held-out Jaccard means and fact-bootstrap 95% intervals. The hardest-other-fact contrast subtracts the maximum comparator similarity. Clean-export-only analysis recomputes eligible comparators, reducing Gemma to two facts; its positive direction is weak standalone evidence. The centered size-regression intercept is deliberately omitted: with an intercept and centered predictors it equals the unadjusted sample mean and is not an independent demonstration that graph size cannot explain the signal.')


def booklet():
    styles=getSampleStyleSheet(); normal=styles['BodyText'];normal.fontSize=10;normal.leading=14
    c=canvas.Canvas(str(OUT/'paper_figure_booklet.pdf'),pagesize=(842,595))
    for n,f in enumerate(FIGURES,1):
        c.setFillColor(colors.HexColor('#18354A'));c.setFont('Helvetica-Bold',18)
        c.drawString(36,558,f['title'])
        path=OUT/(f['stem']+'.png'); img=ImageReader(str(path));w,h=img.getSize()
        scale=min(770/w,355/h);c.drawImage(img,36+(770-w*scale)/2,187+(355-h*scale)/2,width=w*scale,height=h*scale)
        para=Paragraph(html.escape(f['caption']),normal);pw,ph=para.wrap(770,140);assert ph<145,(f['stem'],ph)
        para.drawOn(c,36,170-ph)
        c.setFillColor(colors.HexColor('#687786'));c.setFont('Helvetica',9)
        c.drawString(36,24,'Three-model paper working figures | 5 September 2026 | Qwen3-4B incomplete: 145/147')
        c.drawRightString(806,24,f'{n}/{len(FIGURES)}');c.showPage()
    c.save()
    body=''.join(f'<section><h2>{html.escape(f["title"])}</h2><img src="{f["stem"]}.png"><p>{html.escape(f["caption"])}</p></section>' for f in FIGURES)
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Three-model paper figures</title><style>body{max-width:1150px;margin:40px auto;font:17px/1.55 system-ui;color:#18354a;padding:0 24px}img{width:100%}section{margin:48px 0;border-top:1px solid #ccd5dc}h1,h2{line-height:1.2}p{color:#344b5b}</style><h1>Fact and wording in attribution graphs</h1><p>Working figure set, 5 September 2026. Three models, two families. Qwen3-4B is an incomplete prospective extension. All figures are generated from archived results; no model inference was run.</p>'+body,encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify-raw',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);style()
    original=load(ORIGINAL/'whole_graph_results.json');ext=load(EXTENSION/'analysis/model_extension_results.json')
    raw=load(ORIGINAL/'raw_graph_audit.json');fmt=load(ORIGINAL/'format_graph_audit.json')
    conv=load(EXTENSION/'analysis/conversion_audit.json');audit=load(EXTENSION/'analysis/graph_audit.json')
    results=[original['models']['gemma'],original['models']['qwen'],ext['controlled']]
    crossed=[('Gemma-2-2B',original['format_variation']),('Qwen3-4B',ext['crossed'])]
    checks=validate_arithmetic(results,crossed);release=release_status(audit)
    raw_check={'performed':False}
    if args.verify_raw:
        with (EXTENSION/'checksums.csv').open(encoding='utf-8',newline='') as f: recorded=list(csv.DictReader(f))
        SOURCES[str((EXTENSION/'checksums.csv').relative_to(ROOT))]=digest(EXTENSION/'checksums.csv')
        entries=[(Path(r['path']),r['sha256']) for r in raw+fmt if r.get('status')=='ok']
        entries += [(ROOT/r['path'],r['sha256']) for r in recorded]
        failures=[]
        for i,(path,expected) in enumerate(entries,1):
            if not path.is_file() or digest(path)!=expected: failures.append(str(path))
            if i%50==0:print(f'Raw checksum verification {i}/{len(entries)}',flush=True)
        raw_check={'performed':True,'checked':len(entries),'failures':failures}
        if failures:raise RuntimeError(f'Raw checksum failures: {failures}')
    design_figure(results,raw,audit);signal_figure(results);crossed_figure(crossed)
    control_figure(results);quality_figure(raw,fmt,conv,audit);robustness_figure(results);booklet()
    table('extension_status',[{**{k:v for k,v in release.items() if not isinstance(v,list)},'missing_jobs':';'.join(release['missing_or_failed_jobs'])}])
    report={'source_hashes':SOURCES,'script_sha256':digest(Path(__file__)),'python':platform.python_version(),
            'matplotlib':matplotlib.__version__,'numpy':np.__version__,'checks':checks,'raw_verification':raw_check,
            'extension_release_status':release,'figures':FIGURES,
            'notes':['Estimates unchanged; no new primary tests.', 'Statistical criteria and cohort completion are distinct.',
                     'Output-class matching is coarse; correctness is exact top-token agreement.',
                     'Figure 3 domain points are descriptive and are not independent-sample CIs.']}
    (OUT/'figure_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(f'Built {len(FIGURES)} figures, source tables, HTML and PDF booklet at {OUT}',flush=True)


if __name__=='__main__':main()
