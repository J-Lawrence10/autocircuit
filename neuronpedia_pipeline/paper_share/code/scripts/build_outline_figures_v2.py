"""Build the revised outline figure set from saved estimates, without model calls.

Run .venv-final-reproduction/Scripts/python.exe scripts/build_outline_figures_v2.py.
Earlier figure directories, analyses, manuscript exports, and release ZIP stay intact.
"""
from pathlib import Path
import csv
import html
import json
import platform
import shutil
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import build_outline_figures as draft
import build_three_model_figure_pack as base
import figure_plain_language as wording
import plot_exploratory_confound_checks as exploratory_plots
import plot_closeout_audit as closeout_plots

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/model_extension/paper_figures_plain_language_20261006'
BLUE, ORANGE, INK = draft.BLUE, draft.ORANGE, draft.INK
FIGURES = []
TITLES = dict(draft.TITLES)
CAPTIONS = dict(draft.CAPTIONS)
TITLES['figure1_design_and_coverage'] = 'Three comparisons distinguish related questions from correct answers'
TITLES['figure2_fact_signal'] = 'Questions about the same fact share more features in the analyzed samples'
TITLES['figure5_matched_choice'] = 'The same-fact advantage depends on whether the answer label stays the same'
TITLES['figure6_failure_cases'] = 'Selected wrong-answer graphs resemble correct graphs producing the same answer'
CAPTIONS['figure1_design_and_coverage'] = (
    'A, The original comparison asks whether a target shares more features with its own factual paraphrase '
    'than with other facts in the same subject and evaluation split. The gold/iron wording is schematic. '
    'These cohorts span three models with different subject coverage; sample accounting is separate. '
    'B, A Qwen3-4B follow-up keeps the word and token inventories identical within each of six country-pair '
    'blocks while crossing queried country, answer mapping, and wording. All 48 top-label decisions are correct. '
    'The comparison separates the same-fact advantage within preserved-label and changed-label conditions; '
    'it does not isolate abstract meaning from query order or entity-role binding. '
    'C, After a position-instruction pilot failed, a separate exploratory study compares selected wrong answers '
    'with correct responses preserving either the intended country or the produced answer. There are 16 graphs '
    'from one country pair and two response formats, not 16 independent replications. The final history pilot '
    'is reported separately as a count table because no evaluation graphs were collected. Boxes show comparisons, '
    'not causal pathways; their colors are categorical and their labels carry the meaning.')
CAPTIONS['figure5_matched_choice'] = (
    'Qwen3-4B only; six country-pair blocks and 48/48 correct top-label decisions in the separately frozen, '
    'outcome-informed matched-choice follow-up. A, Unweighted block means for the four cross-wording comparison '
    'conditions. The color scale is Jaccard overlap from 0 (no shared feature identities) to 1 (identical sets). '
    'Same-country/same-label, same-country/changed-label, different-country/same-label, and different-country/'
    'changed-label means are 0.8005, 0.4853, 0.7377, and 0.4874. These are overlap scores, not accuracies. '
    'B, Within each answer-label condition, subtract different-country overlap from same-country overlap. '
    'Small points and connecting lines show the six blocks; black diamonds show means: 0.0628 and -0.0022. '
    'Their direct paired difference is 0.0650 (exploratory Student-t 95% interval 0.0553 to 0.0746; '
    'two-sided block sign-flip p=0.03125, assuming independent blocks and symmetric null contrasts). '
    'C, The balanced fact contrast averages the two components in B (0.0303, archived 95% block-bootstrap '
    'interval 0.0265 to 0.0338); the descriptive output-label contrast is 0.2827. Only the balanced contrast '
    'has an interval drawn in C. Colors in B and C identify the directly labeled categories, not a magnitude '
    'scale. Panels use different vertical scales. Six blocks supply inferential replication, not 48 graphs '
    'or 4,096 conditional null assignments. A near-zero changed-label estimate is not an equivalence test. '
    'Contrasts do not partition variance or prove a causal mechanism. Fixed token inventories do not remove '
    'query-order and entity-role alternatives. Graph-location sensitivity appears in Supplement S6.')
CAPTIONS['figure6_failure_cases'] += (
    ' For example, with France first in the country list and options A: Berlin and B: Paris, an indirect '
    'question about France produces Berlin, whereas naming France produces Paris and naming Germany produces '
    'Berlin. The failure graph resembles the Germany/Berlin response more closely. This illustrates the '
    'comparison, not a proven failure mechanism. Equal feature counts and graph-location filters preserve '
    'the same-output advantage; see Supplement S6 for the latter.')

TITLES.update(wording.TITLES)
CAPTIONS.update(wording.CAPTIONS)


def source(path):
    base.SOURCES[str(path.relative_to(ROOT))] = base.digest(path)
    return path


def save(fig, stem, *unused):
    numbers_before = wording.numeric_signature(fig)
    if stem not in ['figure1_design_and_coverage', 'figure5_matched_choice']:
        draft.clarify_labels(fig, stem)
    wording.clarify(fig, stem)
    fig.suptitle(textwrap.fill(TITLES[stem], 93), x=.035 if stem=='figure1_design_and_coverage' else .055,
                 y=.975 if stem=='figure1_design_and_coverage' else .985, ha='left', va='top',
                 fontsize=19 if stem=='figure1_design_and_coverage' else 14, fontweight='bold', color=INK)
    fig.canvas.draw()
    if stem == 'figure1_design_and_coverage':
        renderer = fig.canvas.get_renderer()
        for ax in fig.axes:
            for label in ax.texts:
                bounds = label.get_window_extent(renderer)
                assert bounds.x0 >= ax.bbox.x0 - 2 and bounds.x1 <= ax.bbox.x1 + 2, label.get_text()
    assert wording.numeric_signature(fig) == numbers_before, f'Wording changed plotted values: {stem}'
    for ext in ['png', 'svg']:
        fig.savefig(OUT/f'{stem}.{ext}', dpi=300, facecolor='white')
    FIGURES.append(dict(number=len(FIGURES)+1, stem=stem, title=TITLES[stem], legend=CAPTIONS[stem]))
    plt.close(fig)


def design():
    source(ROOT/'config/paper_control_manifest.csv')
    source(ROOT/'data/model_extension/matched_choice_chat_v2/jobs.json')
    fig, axes = plt.subplots(1, 3, figsize=(17, 10))
    fig.subplots_adjust(left=.035, right=.975, top=.895, bottom=.16, wspace=.105)
    muted, border, accent = '#5B6D7A', '#D8E2E9', '#236C88'

    def text(ax, y, value, size=10.4, bold=False, color=INK, x=None):
        alignment = 'center' if x is None else 'left'
        ax.text(.499 if x is None else x, y, value, ha=alignment, multialignment=alignment, va='top', fontsize=size,
                fontweight='bold' if bold else 'normal', color=color, linespacing=1.45)

    def card(ax, bottom, height, fill='white', edge=border):
        ax.add_patch(draft.FancyBboxPatch((.008, bottom), .982, height,
                     boxstyle='round,pad=0.008,rounding_size=0.015',
                     facecolor=fill, edgecolor=edge, linewidth=.8))

    headers = [
        ('a', 'Reword a factual question', 'Gemma-2-2B / Qwen3-1.7B / Qwen3-4B',
         'Original question and control sets'),
        ('b', 'Change the correct A/B answer', 'Qwen3-4B', '48 graphs · six country pairs'),
        ('c', 'Examine selected wrong answers', 'Qwen3-4B', '16 graphs · one country pair · two answer formats')]
    questions = [
        'Do reworded questions about the same fact\nshare more features than other-fact questions?',
        'Does the same-fact comparison still show\nmore overlap when the answer letter changes?',
        'Is the error graph more similar to the\nFrance/Paris graph or the Germany/Berlin graph?']
    for ax, (letter, title, models, scope), question in zip(axes, headers, questions):
        ax.axis('off'); ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.text(.035, .986, letter, va='top', ha='center', color='white', fontsize=11,
                fontweight='bold', bbox=dict(boxstyle='round,pad=.33', fc=accent, ec='none'))
        text(ax, .989, title, 12.1, True, x=.105)
        text(ax, .933, 'Models Tested:', 9, True, muted, x=.008)
        text(ax, .933, models, 8.4, color=muted, x=.27)
        text(ax, .902, scope, 9, color=muted, x=.008)
        card(ax, .641, .204, '#F1F6F9')
        text(ax, .823, 'STARTING QUESTION', 8.1, True, accent)
        card(ax, .210, .381)
        text(ax, .568, 'COMPARISONS', 8.1, True, accent)
        card(ax, .015, .137, '#EAF3EF', '#C9DDD3')
        text(ax, .132, 'WHAT WE ASK', 8.1, True, '#32644F')
        text(ax, .094, question, 10.4, True)
        for top, bottom in [(.631, .603), (.200, .164)]:
            ax.annotate('', xy=(.5, bottom), xytext=(.5, top),
                        arrowprops=dict(arrowstyle='-|>', color='#8CA3AF', lw=1.1, mutation_scale=11))

    ax = axes[0]
    text(ax, .785, 'About the element gold', 10.3, True)
    text(ax, .748, '“The chemical symbol for gold is ...”', 11)
    text(ax, .693, 'Expected answer: Au', 10.2, color=accent)
    text(ax, .528, 'Same fact, reworded', 10.2, True)
    text(ax, .499, '“Gold has the chemical symbol ...” → Au')
    text(ax, .445, 'Other fact', 10.2, True)
    text(ax, .416, '“Iron has the chemical symbol ...” → Fe')
    text(ax, .360, 'Made-up name (control)', 10.2, True)
    text(ax, .330, '“The chemical symbol for zorium is ...”\n“Zorium has the chemical symbol ...”')

    ax = axes[1]
    text(ax, .785, 'A: Paris.  B: Berlin.', 10.3, True)
    text(ax, .748, '“For France rather than Germany,\nwhat is the capital?”', 11)
    text(ax, .680, 'Correct answer: A', 10.2, color=accent)
    text(ax, .528, 'Same fact, changed answer letter', 10.2, True)
    text(ax, .499, 'A: Berlin. B: Paris. Ask about France → B', 10)
    text(ax, .445, 'Different fact, same answer letter', 10.2, True)
    text(ax, .416, 'A: Berlin. B: Paris. Ask about Germany → A', 10)
    text(ax, .360, 'Reword the question too', 10.2, True)
    text(ax, .330, '“What is the capital for France\nrather than Germany?”')

    ax = axes[2]
    text(ax, .785, 'Countries: France, Germany.  A: Berlin. B: Paris.', 9.6)
    text(ax, .748, '“What is the capital for the first country,\nnot the second?”', 11)
    text(ax, .680, 'Produced answer: Berlin (wrong)', 10.2, True, '#9D4F2B')
    text(ax, .528, 'Correct response to the intended country', 10.2, True)
    text(ax, .493, '“What is the capital for France?” → Paris')
    text(ax, .418, 'Correct response giving the same answer\nas the error', 10.2, True)
    text(ax, .352, '“What is the capital for Germany?” → Berlin')
    text(ax, .283, 'Keep the country list and A/B choices fixed.', 9.7, color=muted)

    fig.add_artist(plt.Line2D([.035, .975], [.123, .123], transform=fig.transFigure,
                             color=border, linewidth=.8))
    fig.text(.035, .094, 'Feature overlap measures shared graph components—not answer correctness.', fontsize=11, fontweight='bold', color=INK)
    fig.text(.035, .063, 'Gold means the chemical element. Examples are shortened: A uses development questions; B uses a pilot country pair; C shows a collected failure.', fontsize=9, color=muted)
    fig.text(.035, .038, 'Arrows show comparison steps, not causes. Full prompts and collection/exclusion counts are provided in the saved data and captions.', fontsize=9, color=muted)
    save(fig, 'figure1_design_and_coverage')


def matched_figure(result):
    path=source(ROOT/'data/model_extension/final_closeout_20261005/matched_choice_sensitivity.csv')
    with path.open(encoding='utf-8', newline='') as handle:
        rows=sorted([r for r in csv.DictReader(handle) if r['variant']=='full' and r['metric']=='jaccard'], key=lambda r:r['block'])
    blocks=sorted(result['blocks'], key=lambda b:b['block'])
    assert [r['block'] for r in rows] == [b['block'] for b in blocks] and len(rows)==6
    for r,b in zip(rows,blocks):
        for key in ['fact_effect','label_effect','fact_same_label','fact_different_label']:
            assert np.isclose(float(r[key]), b['jaccard'][key], atol=1e-12, rtol=0)
        assert np.isclose(float(r['SS'])-float(r['DS']), float(r['fact_same_label']), atol=1e-12, rtol=0)
        assert np.isclose(float(r['SD'])-float(r['DD']), float(r['fact_different_label']), atol=1e-12, rtol=0)
    base.table('figure5_four_conditions_by_block', rows)
    means={k:float(np.mean([float(r[k]) for r in rows])) for k in ['SS','SD','DS','DD']}
    base.table('figure5_four_condition_means', [dict(condition=k,mean=v,blocks=6) for k,v in means.items()])
    fig,axes=plt.subplots(1,3,figsize=(15.5,6.5),gridspec_kw={'width_ratios':[1.05,1,1]})
    fig.subplots_adjust(left=.105,right=.98,top=.79,bottom=.30,wspace=.53)
    matrix=np.array([[means['SS'],means['SD']],[means['DS'],means['DD']]])
    heat=axes[0].imshow(matrix,cmap='Blues',vmin=0,vmax=1,aspect='auto')
    for i in range(2):
        for j in range(2):axes[0].text(j,i,f'{matrix[i,j]:.3f}',ha='center',va='center',fontsize=16,
                                     color='white' if matrix[i,j]>.65 else INK,fontweight='bold')
    axes[0].set_xticks([0,1],['Same answer\nlabel','Changed answer\nlabel'])
    axes[0].set_yticks([0,1],['Same\ncountry','Different\ncountries'])
    axes[0].set_title('a  What overlaps with what?',loc='left',pad=15,fontsize=11)
    pos=axes[0].get_position(); cax=fig.add_axes([pos.x0,.155,pos.width,.021])
    cb=fig.colorbar(heat,cax=cax,orientation='horizontal',ticks=[0,.5,1])
    cb.set_label('Feature overlap (Jaccard): none to identical',fontsize=8.5)
    for ax,keys,ylim,title,labels in [
        (axes[1],['fact_same_label','fact_different_label'],(-.015,.10),'b  Same-fact advantage',
         ['Same answer\nlabel','Changed answer\nlabel']),
        (axes[2],['fact_effect','label_effect'],(-.012,.34),'c  Average contrasts',
         ['Same fact\n(averaged over labels)','Same answer\nlabel'])]:
        for i,b in enumerate(blocks):
            offset=(i-2.5)*.035; vals=[b['jaccard'][k] for k in keys]
            ax.plot(np.array([0,1])+offset,vals,c='#BDC7CE',lw=1,zorder=1)
            ax.scatter(np.array([0,1])+offset,vals,c=[BLUE,ORANGE],s=36,zorder=2)
        for j,key in enumerate(keys):
            avg=float(np.mean([b['jaccard'][key] for b in blocks]))
            ax.scatter(j,avg,marker='D',s=48,c=INK,zorder=3)
            ax.text(j,max(b['jaccard'][key] for b in blocks)+(.008 if ax==axes[1] else .018),
                    f'{avg:.4f}',ha='center',fontsize=11,fontweight='bold')
        ax.set(ylim=ylim,xlim=(-.4,1.4),xticks=[0,1],xticklabels=labels)
        ax.set_ylabel('Extra feature overlap\n(Jaccard difference)');ax.set_title(title,loc='left',pad=15,fontsize=11)
        ax.axhline(0,c='#7A8790',ls='--',lw=1);ax.grid(axis='y',alpha=.15)
        for tick,col in zip(ax.get_xticklabels(),[BLUE,ORANGE]):tick.set_color(col)
    mean=result['primary']['mean_fact_effect'];lo,hi=result['primary']['ci95']
    axes[2].errorbar(0,mean,yerr=[[mean-lo],[hi-mean]],fmt='none',c=INK,capsize=4,zorder=4)
    fig.text(.48,.165,'B-C: each line = one country pair; diamonds = means.\nOnly the balanced fact mean in C has a 95% interval.',fontsize=9)
    fig.text(.05,.065,'Qwen3-4B only. Six country pairs; 48/48 correct top-label decisions. B and C use different vertical scales.',fontsize=9)
    fig.text(.05,.025,'Near-zero is not proof of no effect. Similarity is not accuracy, variance explained, or a causal mechanism.',fontsize=9)
    base.table('figure5_block_contrasts',[dict(block=b['block'],**b['jaccard']) for b in blocks])
    save(fig,'figure5_matched_choice')


def supplements():
    result=[]
    def save_supp(fig, stem, *unused):
        save(fig, stem)
        result.append(FIGURES.pop())
    base.save=save_supp
    original=base.load(base.ORIGINAL/'whole_graph_results.json')
    ext=base.load(base.EXTENSION/'analysis/model_extension_results.json')
    base.quality_figure(base.load(base.ORIGINAL/'raw_graph_audit.json'),
                       base.load(base.ORIGINAL/'format_graph_audit.json'),
                       base.load(base.EXTENSION/'analysis/conversion_audit.json'),
                       base.load(base.EXTENSION/'analysis/graph_audit.json'))
    base.robustness_figure([original['models']['gemma'],original['models']['qwen'],ext['controlled']])
    for p in [exploratory_plots.OUT/'results.json', exploratory_plots.OUT/'size_per_fact.csv',
              exploratory_plots.OUT/'pairwise_lexical_and_size.csv', closeout_plots.OUT/'matched_choice_sensitivity.csv',
              closeout_plots.OUT/'failure_sensitivity.csv', closeout_plots.OUT/'statistics_audit.json']:
        source(p)
    exploratory_plots.main(save_callback=save_supp)
    closeout_plots.main(save_callback=save_supp)
    base.save=save
    return result


def gallery(supp,history):
    lines=['# Figures for the integrated paper outline','',
           '6 October 2026. Plain-language review of all six main figures and six supplements. Saved estimates, inclusion rules, and conclusions are unchanged; no new model runs or statistical tests.','',
           '## How to read these figures','',
           'A feature is a learned component represented in the exported graph, not a verified concept or a complete reasoning step. Feature overlap counts which components appear in both graphs; it does not compare all their connections. Jaccard overlap divides the number shared by the total number of distinct features across the two graphs: 0 means none shared, and 1 means identical sets. A difference in feature overlap subtracts one overlap score from another; each figure specifies the comparison. It can be positive, zero, or negative. Zero means equal overlap, not missing data.','',
           'A test question was reserved for evaluation rather than for developing the analysis. A token is one unit of predicted text; it may be a whole word, part of a word, or a symbol. A/B answer means the letter produced, not necessarily the same capital city. Category colors are explained by labels or legends; numerical colors have a scale. An asterisk on Qwen3-4B marks the incomplete original collection (145/147 graphs), not the separate completed follow-ups.','']
    sections=[]
    for i,f in enumerate(FIGURES+supp):
        prefix=f'Figure {i+1}' if i<6 else f'Supplement S{i-5}'
        lines.extend([f'## {prefix} {f["title"]}','',f'![{prefix}]({(OUT/(f["stem"]+".png")).as_posix()})','',f['legend'],'',f'[Editable SVG]({(OUT/(f["stem"]+".svg")).as_posix()})',''])
        sections.append(f'<section><h2>{html.escape(prefix+": "+f["title"])}</h2><img src="{f["stem"]}.png" alt="{html.escape(f["title"])}"><p>{html.escape(f["legend"])}</p><a href="{f["stem"]}.svg">Editable SVG</a></section>')
    pilot=[dict(component='Literal A/B instructions',correct=4,total=4),
           dict(component='Document-history pilot',correct=history['blocks']['pilot_documents']['correct'],total=8),
           dict(component='Spaceflight pilot',correct=history['blocks']['pilot_space']['correct'],total=8)]
    assert history['correct']==15 and history['n']==20 and not history['passed']
    assert sum(r['correct'] for r in pilot)==15
    base.table('table_history_pilot',pilot+[dict(component='Overall',correct=15,total=20)])
    lines.extend(['## Final history pilot','', '| Checks | Correct | Required |','|---|---:|---:|']+[f'| {r["component"]} | {r["correct"]}/{r["total"]} | {r["total"]}/{r["total"]} |' for r in pilot]+['| Overall | 15/20 | 20/20 |','',
                  'The fixed pilot failed. No evaluation graphs were requested, so no history graph-overlap effect was measured. This is not a history-accuracy benchmark. The original history exclusions remain unchanged.',''])
    table='<table><tr><th>Pilot checks</th><th>Correct</th><th>Required</th></tr>'+''.join(f'<tr><td>{r["component"]}</td><td>{r["correct"]}/{r["total"]}</td><td>{r["total"]}/{r["total"]}</td></tr>' for r in pilot)+'<tr><td>Overall</td><td>15/20</td><td>20/20</td></tr></table>'
    sections.append('<section><h2>Final history pilot</h2>'+table+'<p>The fixed pilot failed. No evaluation graphs were requested. There is no new historical graph-overlap estimate, not a measured zero effect.</p></section>')
    lines.extend(['## Reproduction and source data','',
                  'Run `.venv-final-reproduction/Scripts/python.exe scripts/build_outline_figures_v2.py`. All 12 figures are rebuilt from saved data as 300-dpi PNGs and editable SVGs. The wording is maintained in `scripts/figure_plain_language.py`; the label review is recorded in `wording_audit.json`.','',
                  'The manifest records input, builder, helper, and output hashes; plotted source tables are in `tables`. Figure 5 shows six blocks, not 48 independent observations. Category colors are directly labeled or keyed in legends; the numerical heatmap has a 0–1 color scale. Missing groups are unavailable, never effect-size zeros.','',
                  'Earlier figures, the compiled manuscript, and the sealed release archive remain unchanged. This is a figure revision for author review, not a new scientific analysis.',''])
    (OUT/'LEGENDS.md').write_text('\n'.join(lines),encoding='utf-8')
    (ROOT/'docs/writing/FIGURE_HEADLINES_AND_LEGENDS.md').write_text('\n'.join(lines),encoding='utf-8')
    intro=''.join('<p>'+html.escape(lines[i])+'</p>' for i in [6,8])
    (OUT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Paper figures and legends</title><style>body{max-width:1350px;margin:32px auto;padding:0 24px;font:17px/1.55 system-ui;color:#203544}img{width:100%;height:auto}h1,h2{line-height:1.25}section{margin:45px 0;border-top:1px solid #d8e1e7;padding-top:20px}table{border-collapse:collapse}td,th{border:1px solid #ccd5dc;padding:8px 18px}p{max-width:1100px}</style><h1>Figures for the integrated paper outline</h1><p>Wording reviewed 6 October 2026. Six main figures, six supplements, and the stopped history pilot. Saved results only.</p>'+intro+''.join(sections)+'</html>',encoding='utf-8')


def main():
    OUT.mkdir(parents=True,exist_ok=True);base.OUT=OUT;draft.OUT=OUT
    base.SOURCES.clear();base.TABLES.clear();FIGURES.clear();wording.AUDIT.clear();base.style()
    plt.rcParams.update({'axes.titleweight':'semibold','text.color':INK,'axes.labelcolor':INK})
    original=base.load(base.ORIGINAL/'whole_graph_results.json')
    ext=base.load(base.EXTENSION/'analysis/model_extension_results.json')
    matched=base.load(ROOT/'data/model_extension/matched_choice_chat_v2/qwen3-4b/analysis/results.json')
    failure=base.load(ROOT/'data/model_extension/failure_case_graphs_v1/analysis/results.json')
    jobs=base.load(ROOT/'data/model_extension/failure_case_graphs_v1/jobs.json')
    history=base.load(ROOT/'data/model_extension/history_choice_final_v1/pilot_gate.json')
    source(ROOT/'docs/papers/INTEGRATED_PAPER_OUTLINE.md')
    results=[original['models']['gemma'],original['models']['qwen'],ext['controlled']]
    crossed=[('Gemma-2-2B',original['format_variation']),('Qwen3-4B',ext['crossed'])]
    checks=base.validate_arithmetic(results,crossed)
    assert len(matched['blocks'])==6 and sum(b['correct_n'] for b in matched['blocks'])==48
    assert all(b['token_bags_identical'] and b['retrieval_eligible'] for b in matched['blocks'])
    assert failure['clean_graphs']==16 and failure['clean_comparisons']==8
    assert all(not a['drift'] and a['correct']==(a['reference']=='named') for a in failure['audits'])
    base.save=save;draft.save=save
    design();base.signal_figure(results);base.crossed_figure(crossed);base.control_figure(results)
    matched_figure(matched);draft.failure_figure(failure,jobs)
    supp=supplements();gallery(supp,history)
    assert len(FIGURES)==6 and len(supp)==6
    for path,digest in base.SOURCES.items():assert base.digest(ROOT/path)==digest
    for f in FIGURES+supp:
        for extn in ['png','svg']:assert (OUT/f'{f["stem"]}.{extn}').stat().st_size>1000
    checks+=['Six-block four-condition means reconcile with frozen contrasts to 1e-12',
             '48/48 matched-choice decisions, 16 clean failure graphs, eight valid comparisons',
             'History pilot 15/20; no history graph effect plotted','All supplements rebuilt using the same saved-data plotting functions',
             'Plotted lines, points, heatmaps, and bars unchanged by wording edits in all 12 figures']
    (OUT/'wording_audit.json').write_text(json.dumps(wording.AUDIT,indent=2),encoding='utf-8')
    manifest=dict(date='2026-10-06',figures=FIGURES,supplements=supp,checks=checks,
                  source_hashes=base.SOURCES,script_sha256=base.digest(Path(__file__)),
                  helper_hashes={str(Path(m.__file__).relative_to(ROOT)):base.digest(Path(m.__file__)) for m in [draft,base,wording,exploratory_plots,closeout_plots]},
                  python=platform.python_version(),numpy=np.__version__,matplotlib=matplotlib.__version__,
                  output_hashes={str(p.relative_to(OUT)):base.digest(p) for p in OUT.rglob('*') if p.is_file() and p.name not in ['figure_manifest.json','VISUAL_QA.md']})
    (OUT/'figure_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Built six main figures, six supplements, source tables and legends: {OUT}')


if __name__=='__main__':main()
