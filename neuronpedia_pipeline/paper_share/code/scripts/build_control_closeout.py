"""Validate archived controls and produce figures and manuscript-ready closeout text.

Reads existing results; never makes API requests or reruns graph generation.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from matched_choice_controls import ROOT, digest
from control_io import atomic_json
from analyze_matched_choice_controls import csv_write, contrasts, KEYS
from whole_graph_analysis import bootstrap_ci

OUT=ROOT/'data/model_extension/publication_closeout_20260909'
V2=ROOT/'data/model_extension/matched_choice_chat_v2'
V3=ROOT/'data/model_extension/matched_choice_position_v3'
DOC=ROOT/'docs/papers/MATCHED_CHOICE_RESULTS_FOR_MANUSCRIPT.md'


def validate_result(path,expected):
    result=json.loads(path.read_text())
    assert len(result['audits'])==expected
    assert len(result['raw_hashes'])==expected
    for raw,sha in result['raw_hashes'].items():
        assert digest(ROOT/raw)==sha,raw
    for row in result['audits']:
        if row['status']=='ok':
            converted=(ROOT/row['raw_path']).parent/'converted_graph.json'
            assert digest(converted)==row['converted_sha256'],str(converted)
    assert result['freeze_sha256']==digest(path.parents[2]/'freeze.json')
    return result,dict(results_path=str(path.relative_to(ROOT)),results_sha256=digest(path),
                       raw_hash_matches=expected,converted_hash_matches=sum(r['status']=='ok' for r in result['audits']),
                       retrieval_gate=result['retrieval_gate'])


def verify_v2_pairs(result):
    import csv
    with (V2/'qwen3-4b/analysis/pairwise.csv').open(newline='',encoding='utf-8') as stream:
        rows=list(csv.DictReader(stream))
    for block in result['blocks']:
        matrix=np.full((4,4),np.nan)
        for r in rows:
            if r['metric']=='jaccard' and r['block']==block['block']:
                i=KEYS.index((int(r['left_fact']),r['left_label']))
                j=KEYS.index((int(r['right_fact']),r['right_label']))
                assert np.isnan(matrix[i,j]),'Duplicate pair'
                matrix[i,j]=float(r['similarity'])
        assert np.isfinite(matrix).all()
        for key,value in contrasts(matrix).items():
            assert np.isclose(value,block['jaccard'][key],rtol=0,atol=1e-12)


def summarize(result,version):
    rows=[]
    for block in result['blocks']:
        if 'jaccard' not in block:continue
        metrics=block['jaccard'] if version=='v2' else block['jaccard']['cross_position']
        rows.append(dict(experiment=version,block=block['block'],eligible=block['retrieval_eligible'],**metrics))
    return rows


def plot_components(rows,version):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,4.6),layout='constrained')
    specs=[('fact_same_label','Same A/B label','#0072B2'),
           ('fact_different_label','Changed A/B label','#D55E00')]
    for index,(key,label,color) in enumerate(specs):
        values=[r[key] for r in rows]
        if not values:continue
        x=index+np.linspace(-.10,.10,len(values))
        axes[0].scatter(x,values,color=color,s=35,alpha=.85,label='Country-pair blocks' if index==0 else None)
        ci=bootstrap_ci(values,runs=10000,seed=20260909);mean=float(np.mean(values))
        axes[0].errorbar(index+.19,mean,yerr=[[mean-ci[0]],[ci[1]-mean]],fmt='D',color='black',capsize=4)
    axes[0].set_xticks([0,1],[s[1] for s in specs]);axes[0].set_ylabel('Same-fact minus different-fact Jaccard')
    axes[0].set_title('A  Separate answer-label conditions')
    for index,(key,label,color) in enumerate([('fact_effect','Balanced fact\ncontrast','#0072B2'),
                                            ('label_effect','Answer-label\ncontrast','#CC651D')]):
        vals=[r[key] for r in rows]
        if not vals:continue
        axes[1].scatter(index+np.linspace(-.10,.10,len(vals)),vals,color=color,s=35)
        ci=bootstrap_ci(vals,runs=10000,seed=20260909);mean=float(np.mean(vals))
        axes[1].errorbar(index+.19,mean,yerr=[[mean-ci[0]],[ci[1]-mean]],fmt='D',color='black',capsize=4)
    axes[1].set_xticks([0,1],['Balanced fact\ncontrast','Answer-label\ncontrast'])
    axes[1].set_ylabel('Jaccard contrast');axes[1].set_title('B  Effect magnitudes (descriptive comparison)')
    for ax in axes:ax.axhline(0,color='gray',ls='--',lw=1);ax.set_xlim(-.4,1.5)
    subtitle='cross-wording' if version=='v2' else 'cross-wording and cross-position'
    fig.suptitle(f'Qwen3-4B {version}: {subtitle} controls\nDots: country-pair blocks; diamonds: mean and descriptive 95% block-bootstrap interval',fontsize=11)
    for ext in ['png','svg']:fig.savefig(OUT/f'{version}_answer_label_components.{ext}',dpi=220)
    plt.close(fig)


def v3_section():
    path=V3/'qwen3-4b/analysis/results.json'
    status=json.loads((V3/'status.json').read_text()) if (V3/'status.json').exists() else {}
    lines=['## Final position-balanced follow-up (v3)','',
           'Outcome-informed follow-up specified after v2. It uses the same six country pairs in a new ordinal-selection task; these are not unseen facts. Queried country, list position, answer mapping, and wording vary independently in 16 cells per block.','']
    validation=None;rows=[]
    if path.exists():
        result,validation=validate_result(path,96);rows=summarize(result,'v3')
        plot_components(rows,'v3')
        p=result['primary'];lines.append(f'Available raw graphs: 96/96. Full behavioral/integrity gate: {result["retrieval_gate"]}.')
        if p['status']=='complete':
            lines.extend(['',f'The cross-position balanced fact contrast was {p["mean_fact_effect"]:.4f} '
                          f'(95% block-bootstrap interval {p["ci95"][0]:.4f} to {p["ci95"][1]:.4f}; '
                          f'{p["positive_blocks"]}/6 positive blocks; exact conditional correspondence p={p["exact_conditional_assignment_p"]:.6g}; '
                          f'conservative four-opportunity p={p["conservative_cumulative_family_p"]:.6g}).',
                          '',f'The same-label and changed-label components were {np.mean([r["fact_same_label"] for r in rows]):.4f} '
                          f'and {np.mean([r["fact_different_label"] for r in rows]):.4f}, respectively. These components remain descriptive.'])
        else:
            lines.extend(['','The full gate was not met; no primary significance claim is made. See block and graph audit tables for the failed cells.'])
        lines.extend(['','Collection is closed for this planned follow-up. Do not generate additional designs based on whether its results are significant.',
                      '', 'This experiment concerns feature composition in a forced-choice pipeline. It does not establish a causal fact mechanism or restore the original traceback claims.'])
    elif status.get('stage')=='pilot_failed':
        gate=status['pilot'];lines.extend([f'The pilot failed: {gate["correct"]}/16 correct A/B decisions. No held-out graphs were generated.',
                      '', 'This is a task/behavior limitation, not evidence that a graph-level fact effect is zero. The fixed stopping rule closes this control round without prompt replacement.'])
    else:
        lines.extend([f'Not complete. Current saved state: {status.get("state","prepared")}; '
                      f'pilot previews archived: {status.get("pilot_archived",0)}/16; graphs archived: {status.get("graphs_complete",0)}/96.',
                      '', 'No v3 numerical result should be inserted into the paper until it is available and validated.'])
    return lines,validation,rows


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    result,validation=validate_result(V2/'qwen3-4b/analysis/results.json',48)
    verify_v2_pairs(result);validation['pairwise_contrasts_reconstructed']=True
    rows=summarize(result,'v2');plot_components(rows,'v2')
    p=result['primary'];same=float(np.mean([r['fact_same_label'] for r in rows]));different=float(np.mean([r['fact_different_label'] for r in rows]))
    label=float(np.mean([r['label_effect'] for r in rows]))
    lines=['# Matched-choice controls: results ready for manuscript integration','',
           'Original three-model cohorts remain separate. The completed matched-choice graph test is Qwen3-4B only. This is an evidence package, not a claim that the manuscript is submission-ready.','',
           '## Main result in plain language','',
           'The graphs contain a small, consistent association with which country is asked about, but a much larger association with the A/B label being produced. The fact-associated advantage is concentrated in comparisons preserving the answer label; it is not visibly retained on average when the label changes. This is not evidence of an answer-independent fact code.','',
           '## What changed and what completed','',
           '- Plain-completion Qwen3-4B passed only 4/8 pilot decisions by always choosing A; no v1 held-out graph cohort was generated.',
           '- Gemma-2-2B supplied the correct capital names on all eight pilot prompts, but 0/8 requested A/B labels; this was response-format failure, not factual-error evidence.',
           '- A separately frozen, explicitly outcome-informed Qwen official-chat revision passed 8/8 pilot decisions and 48/48 held-out decisions.',
           '- All 48 v2 raw hashes and converted-file hashes verify; archived pairwise values reconstruct the six reported block contrasts. These exports have zero raw ambiguous IDs and duplicate endpoint edges.',
           '- The v2 final status-file rename failed after output creation. An administrative recovery record documents correction without regenerating data or changing estimates.','',
           '## Manuscript-ready methods (v2)','',
           'Following failures of the plain-completion behavior pilots, we prospectively froze a Qwen3-4B chat-framed forced-choice follow-up before requesting its outcomes. Each of six country-pair blocks crossed queried country, capital-to-A/B mapping, and wording (eight graphs per block). Each block had identical word and tokenizer-ID multisets. France/Germany was a separate behavior-only pilot. All six blocks were required to have correct top A/B decisions, matched token multisets, and valid graph representations. The primary endpoint was the equally weighted mean of same-fact advantages within same-label and changed-label comparisons. Uncertainty used six blocks, not 48 independent graphs. The exact conditional fact-correspondence null contained 4096 assignments; the prespecified v2 multiplicity family comprised three model/version opportunities. These were locally frozen protocols, not public preregistrations.','',
           '## Manuscript-ready results (v2)','',
           f'All 48 held-out top-label decisions were correct. The balanced same-fact Jaccard contrast was {p["mean_fact_effect"]:.4f} '
           f'(95% block-bootstrap interval {p["ci95"][0]:.4f} to {p["ci95"][1]:.4f}), positive in all six blocks '
           f'(exact conditional correspondence p={p["exact_conditional_assignment_p"]:.6g}; multiplicity-adjusted p={p["bonferroni_planned_family_p"]:.6g}). '
           f'The descriptive output-label contrast was {label:.4f}. The same-label fact contrast was {same:.4f}, '
           f'whereas the changed-label contrast was {different:.4f}. The latter is a descriptive near-zero estimate, not an equivalence test. '
           'The average balanced fact contrast therefore does not demonstrate invariance to the produced answer label.','',
           '## Essential limitations','',
           '- Six geography blocks in one model; the paper has three models overall, but this control does not establish three-model replication.',
           '- Feature-set overlap is not topology, complete input-to-output traceback, or a causal intervention.',
           '- Output-label magnitude comparison is descriptive; ninefold larger does not mean ninefold variance explained.',
           '- Correct label depends on both the queried fact and option mapping. Thus same-label versus changed-label components are not pure fact manipulations; option mapping and entity-role binding remain possible explanations.',
           '- V2 does not separate queried identity from query order. V3 specifically tests list-position dependence in a different task, not all possible semantic confounds.',
           '- Pilot revisions, exclusions, failed controls, and incomplete original model-extension jobs must remain visible in the paper.','',
           '## Suggested paper structure','',
           '1. Original three-model association: factual paraphrases share features, within the eligible cohorts.',
           '2. Why that alone is insufficient: lexical and answer matching lacked support in the original comparisons.',
           '3. Stronger Qwen3-4B controls: identical token inventories, crossed answer mappings, and a small balanced fact-associated signal.',
           '4. The critical boundary: answer-label dependence, conditional components, and the separately reported final position test.',
           '5. Conclusion: characterize what overlap measures; do not claim abstract semantic or causal circuit recovery.','']
    extra,v3validation,v3rows=v3_section();lines.extend(extra)
    csv_write(OUT/'block_components.csv',rows+v3rows)
    text='\n'.join(lines)+'\n'
    (OUT/'RESULTS_SUMMARY.md').write_text(text,encoding='utf-8')
    DOC.write_text(text,encoding='utf-8')
    checks=dict(checked_at=datetime.now(timezone.utc).isoformat(),v2=validation,v3=v3validation,
                v3_complete=v3validation is not None,builder_sha256=digest(__file__))
    atomic_json(OUT/'validation.json',checks)
    manifest={str(p.relative_to(ROOT)):digest(p) for p in OUT.iterdir() if p.is_file() and p.name!='artifact_manifest.json'}
    manifest[str(DOC.relative_to(ROOT))]=digest(DOC)
    atomic_json(OUT/'artifact_manifest.json',manifest)
    print(f'Validated closeout package: {OUT}',flush=True)


if __name__=='__main__':main()
