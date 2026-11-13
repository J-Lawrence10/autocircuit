#!/usr/bin/env python3
"""Render supplemental exploratory figures from saved tables, without model calls."""
import csv
import hashlib
import html
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/model_extension/exploratory_20260905'
MODELS = ['gemma-2-2b', 'qwen3-1.7b', 'qwen3-4b']
LABELS = ['Gemma-2-2B', 'Qwen3-1.7B', 'Qwen3-4B*']
COLORS = ['#0072B2', '#A6558C', '#CC651D']


def csv_rows(name):
    return list(csv.DictReader((OUT / (name + '.csv')).open(encoding='utf-8', newline='')))


def main(save_callback=None):
    r = json.loads((OUT / 'results.json').read_text())
    original = json.loads((ROOT / 'data/publication_analysis/whole_graph_results.json').read_text())
    extension = json.loads((ROOT / 'data/model_extension/qwen3-4b/analysis/model_extension_results.json').read_text())
    sources = [original['models']['gemma'], original['models']['qwen'], extension['controlled']]
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10, 'axes.spines.top':False,
                         'axes.spines.right':False, 'svg.fonttype':'none'})
    figures = []

    def save(fig, stem, caption):
        if save_callback is not None:
            save_callback(fig, stem, caption)
            return
        for ext in ['png', 'svg']:
            fig.savefig(OUT / f'{stem}.{ext}', dpi=220, facecolor='white')
        plt.close(fig)
        figures.append(dict(stem=stem, caption=caption))

    size = csv_rows('size_per_fact')
    fig, axes = plt.subplots(1,3,figsize=(12,5.4),sharey=True)
    fig.subplots_adjust(left=.075,right=.98,bottom=.21,top=.82,wspace=.15)
    for i,(ax,model,source) in enumerate(zip(axes,MODELS,sources)):
        primary = {x['pair_id']:x['feature_jaccard__margin_other_factual_mean'] for x in source['per_fact'] if x['split']=='held_out'}
        subset = [x for x in size if x['model']==model]
        for fact in sorted(primary):
            vals=[primary[fact]]+[float(next(x['mean_margin'] for x in subset if x['fact']==fact and float(x['fraction'])==f)) for f in [1,.5]]
            ax.plot(range(3),vals,color=COLORS[i],alpha=.35,lw=.7,marker='o',ms=3)
        stats=[{'mean':source['heldout_primary']['mean'],'ci95_descriptive':source['heldout_primary']['ci95']}]+[next(x for x in r['size'] if x['model']==model and x['fraction']==f) for f in [1,.5]]
        for x,s in enumerate(stats):
            lo,hi=s['ci95_descriptive']
            ax.errorbar(x,s['mean'],yerr=[[s['mean']-lo],[hi-s['mean']]],fmt='D',c='black',capsize=4,zorder=5)
            ax.text(x,.55,f'{s["mean"]:.3f}',ha='center')
        ax.set_ylim(-.045,.6);ax.set_xlim(-.35,2.35);ax.axhline(0,c='gray',ls='--',lw=1)
        ax.set_xticks(range(3),['Original','Equal count K','Equal count K/2'],rotation=18)
        ax.set_title(f'{LABELS[i]} (n={len(primary)})',loc='left')
    axes[0].set_ylabel('Own-paraphrase advantage (Jaccard difference)')
    fig.text(.075,.93,'Pooled advantage remains after equalizing feature counts',fontsize=16,weight='bold')
    fig.text(.075,.04,'Exploratory. Lines = facts; diamonds = means. *Qwen3-4B extension incomplete (145/147 graphs).',fontsize=9)
    save(fig,'figureS3_equal_feature_counts','Independent uniform subsampling to the same K within each model/domain/held-out block, or floor(K/2), across 200 repetitions. Each sampled graph is reused across comparisons in a repetition. Points/lines show the original fact margins and each fact\'s mean subsampled margin. Error bars are descriptive fact-bootstrap 95% intervals of those means, not confidence intervals across resampling runs. Seven of eight Gemma facts and all eligible Qwen facts retain positive averaged margins. Cardinality is equalized; feature-selection bias, lexical content, and answer identity are not removed. Lower Jaccard magnitudes after thinning are not percentages of explained signal.')

    pairs = csv_rows('pairwise_lexical_and_size')
    fig,axes=plt.subplots(1,3,figsize=(12,5.4),sharex=True,sharey=True)
    fig.subplots_adjust(left=.075,right=.98,bottom=.18,top=.81,wspace=.17)
    for i,(ax,model) in enumerate(zip(axes,MODELS)):
        facts=sorted({x['target_fact'] for x in pairs if x['model']==model})
        for fact in facts:
            ps=[x for x in pairs if x['model']==model and x['target_fact']==fact]
            own=float(next(x['word_jaccard'] for x in ps if x['same_fact']=='True'))
            best=max(float(x['word_jaccard']) for x in ps if x['same_fact']=='False')
            ax.scatter(own,best,color=COLORS[i],s=48,alpha=.7)
        x=np.linspace(0,1,100)
        ax.fill_between(x,np.maximum(0,x-.05),np.minimum(1,x+.05),color='#DDE6EA',label='Within 0.05')
        ax.plot(x,x,c='gray',ls='--',lw=1)
        ax.set_title(f'{LABELS[i]}: 0/{len(facts)} matched',loc='left')
        ax.set_xlim(0,1);ax.set_ylim(0,1)
        ax.set_xlabel('Word overlap with own paraphrase')
    axes[0].set_ylabel('Highest word overlap with another fact')
    fig.text(.075,.93,'The present controls cannot separate shared words from fact identity',fontsize=15,weight='bold')
    fig.text(.075,.04,'Each point = a held-out fact (points may overlap). Shaded band = declared 0.05 word-overlap caliper.',fontsize=9)
    save(fig,'figureS4_lexical_support','Word overlap is case-folded alphanumeric word-set Jaccard, without stopword removal. The most lexically similar other factual paraphrase remains more than 0.05 below the own paraphrase for every held-out fact. Consequently no fact has support under the at-least-own-overlap, 0.05-caliper, or joint word/size-caliper rules. This is a non-estimable matched comparison, not a zero effect or evidence that words fully explain feature overlap. The same-fact label also shares the expected answer. The dataset does not identify a lexical- or answer-independent semantic effect.')

    fig,axes=plt.subplots(1,2,figsize=(12,5.6),gridspec_kw={'width_ratios':[1.1,1]})
    fig.subplots_adjust(left=.075,right=.91,bottom=.23,top=.81,wspace=.38)
    cats=['whole_answer_next_token','multi_token_prefix_only','next_token_mismatch']
    catlabels=['Whole expected answer in next token','Compatible prefix; answer unverified','Different next token']
    catcolors=['#009E73','#E69F00','#8C94A0']
    ax=axes[0]
    for i,model in enumerate(MODELS[1:]):
        s=next(x for x in r['answers'] if x['model']==model and x['design']=='controlled')
        bottom=0
        for key,color in zip(cats,catcolors):
            value=s['statuses'].get(key,0)
            ax.bar(i,value,bottom=bottom,color=color,width=.55)
            if value:ax.text(i,bottom+value/2,str(value),ha='center',va='center',color='black')
            bottom+=value
        ax.text(i,bottom+1.5,f'n={bottom}',ha='center')
    ax.set_xticks([0,1],LABELS[1:]);ax.set_ylim(0,65);ax.set_ylabel('Available factual prompt graphs')
    ax.set_title('a  Qwen tokenizer-aware audit',loc='left')
    ax=axes[1]
    matrix=np.array([[next(x['strict_match_n'] for x in r['crossed_output_support'] if x['model']==m and x['domain']==d) for d in ['chemistry','geography','history']] for m in [MODELS[0],MODELS[2]]])
    heat=ax.imshow(matrix,cmap='Blues',vmin=0,vmax=9,aspect='auto')
    scale=fig.colorbar(heat,ax=ax,fraction=.045,pad=.04,ticks=[0,3,6,9])
    scale.set_label('Matching next tokens (out of 9)',fontsize=9)
    for i in range(2):
        for j in range(3):ax.text(j,i,f'{matrix[i,j]}/9',ha='center',va='center',color='white' if matrix[i,j]>=6 else 'black',fontsize=13)
    ax.set_xticks(range(3),['Chemistry','Geography','History']);ax.set_yticks(range(2),['Gemma-2-2B','Qwen3-4B'])
    ax.set_title('b  Crossed strict answer agreement',loc='left')
    fig.text(.075,.93,'Next-token agreement is not equivalent to verified factual retrieval',fontsize=15,weight='bold')
    fig.legend([plt.Rectangle((0,0),1,1,color=c) for c in catcolors],catlabels,loc='lower center',ncol=1,frameon=False,fontsize=9)
    save(fig,'figureS5_answer_audit','Panel a includes development and held-out factual prompts, including target-only Qwen3-1.7B geography graphs; it is not the controlled eligible sample. Qwen3-4B has one missing factual graph and one missing nonce graph. Exact official Qwen tokenizer revisions validate against all observed prompt pieces and top logit decodings; seven controlled mismatches across the two Qwen models are compatible multi-token prefixes, not verified complete answers. Gemma tokenizer access returned HTTP 401, so its tokenizer-aware audit is unresolved. Panel b uses the original trimmed-string rule, which remains unchanged: only Qwen3-4B geography has all nine cells matching. Its binary fact/wording effects are 0.101/0.106; these single-domain descriptive estimates cannot establish dominance. Historical checkpoint-tokenizer revision identity is not fully recoverable.')

    if save_callback is not None:
        return
    body=''.join(f'<section><h2>{html.escape(f["stem"])}</h2><img src="{f["stem"]}.png"><p>{html.escape(f["caption"])}</p></section>' for f in figures)
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Exploratory confound checks</title><style>body{max-width:1150px;margin:40px auto;padding:0 24px;font:17px/1.5 system-ui;color:#18354a}img{width:100%}section{border-top:1px solid #ccd5dc;margin:40px 0}</style><h1>What survives, and what the dataset cannot separate</h1><p>Exploratory follow-up, 5 September 2026. Primary results unchanged.</p>'+body,encoding='utf-8')
    manifest={'figures':figures,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'results.json',OUT/'size_per_fact.csv',OUT/'pairwise_lexical_and_size.csv',ROOT/'data/publication_analysis/whole_graph_results.json',ROOT/'data/model_extension/qwen3-4b/analysis/model_extension_results.json']}}
    (OUT/'figure_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Built {len(figures)} exploratory figures and caption gallery at {OUT}')


if __name__=='__main__':
    main()
