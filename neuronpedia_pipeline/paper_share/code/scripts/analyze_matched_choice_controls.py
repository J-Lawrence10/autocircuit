#!/usr/bin/env python3
"""Frozen within-block fact/label contrasts; auto-finalizes hosted control runs."""
from collections import Counter
import csv
import hashlib
import itertools
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from matched_choice_controls import ROOT, OUT, MODELS, make_jobs, atomic_json, digest
from run_matched_choice_controls import clean_prompt
from convert_model_extension import load_converter, raw_integrity
from whole_graph_analysis import summarize_graph, jaccard, sparse_cosine, finite_number, bootstrap_ci, json_ready

KEYS=list(itertools.product([0,1],['A','B']))
SEED=20260905


def configure_experiment(output_root,job_factory,model_specs):
    global OUT,make_jobs,MODELS
    OUT,make_jobs,MODELS=output_root,job_factory,model_specs


def contrasts(matrix):
    cats={key:[] for key in ['SS','SD','DS','DD']}
    for i,(fi,li) in enumerate(KEYS):
        for j,(fj,lj) in enumerate(KEYS):
            category=('S' if fi==fj else 'D')+('S' if li==lj else 'D')
            cats[category].append(float(matrix[i,j]))
    means={k:float(np.mean(v)) for k,v in cats.items()}
    fact_same_label=means['SS']-means['DS']
    fact_diff_label=means['SD']-means['DD']
    return {**means,'fact_effect':(fact_same_label+fact_diff_label)/2,
            'fact_same_label':fact_same_label,'fact_different_label':fact_diff_label,
            'label_effect':((means['SS']-means['SD'])+(means['DS']-means['DD']))/2}


def fact_assignment_null(matrix):
    values=[]
    for flip_a,flip_b in itertools.product([0,1],repeat=2):
        order=[KEYS.index((fact^(flip_a if label=='A' else flip_b),label)) for fact,label in KEYS]
        values.append(contrasts(matrix[:,order])['fact_effect'])
    return values


def matrix_for(reps,metric):
    def sim(a,b):
        if metric=='weighted_cosine':return sparse_cosine(a['feature_weights'],b['feature_weights'])
        key='features_with_errors' if metric=='error_inclusive_jaccard' else 'features'
        return jaccard(a[key],b[key])
    return np.array([[sim(reps[(f,l,0)],reps[(ff,ll,1)]) for ff,ll in KEYS] for f,l in KEYS])


def csv_write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        w.writerows({k:json.dumps(json_ready(v)) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows)


def analyze_model(model):
    model_dir=OUT/model;analysis=model_dir/'analysis';analysis.mkdir(parents=True,exist_ok=True)
    jobs=[j for j in make_jobs() if j['split']=='held_out']
    convert=load_converter();reps_by_block={};audits=[];hashes={}
    for job in jobs:
        folder=model_dir/'graphs'/job['job_id'];raw=folder/'raw_graph.json';converted=folder/'converted_graph.json'
        row={**job,'model':model,'raw_path':str(raw.relative_to(ROOT))}
        if not raw.exists():audits.append({**row,'status':'missing'});continue
        try:
            metadata=json.loads((folder/'metadata.json').read_text());raw_hash=digest(raw)
            if raw_hash!=metadata['sha256']:raise ValueError('Raw checksum mismatch')
            hashes[str(raw.relative_to(ROOT))]=raw_hash
            graph=json.loads(raw.read_text(encoding='utf-8'));meta=graph['metadata']
            integrity=raw_integrity(graph);row.update(integrity)
            if integrity['raw_missing_node_id_count'] or integrity['raw_orphan_edge_count']:
                raise ValueError('Raw missing node IDs or orphan edges')
            if any(finite_number(e.get('weight')) is None for e in graph.get('links',graph.get('edges',[]))):
                raise ValueError('Nonfinite raw edge weight')
            if clean_prompt(meta['prompt'])!=job['prompt'] or meta.get('scan',meta.get('model'))!=model:
                raise ValueError('Model/prompt mismatch')
            settings=meta.get('generation_settings',{});pruning=meta.get('pruning_settings',{})
            if not np.isclose(meta.get('node_threshold',-1),.8) or not np.isclose(pruning.get('edge_threshold',-1),.85):
                raise ValueError('Pruning setting mismatch')
            if settings.get('max_n_logits')!=10 or not np.isclose(settings.get('desired_logit_prob',-1),.99):
                raise ValueError('Generation setting mismatch')
            expected_source='gemma' if model=='gemma-2-2b' else 'mwhanna/qwen3-4b-transcoders'
            row['observed_transcoder_set']=meta.get('info',{}).get('transcoder_set')
            if row['observed_transcoder_set']!=expected_source:raise ValueError('Raw decomposition provenance mismatch')
            if not converted.exists():
                convert(str(raw),str(converted),prompt=None,model_id=model,ambiguous_node_policy='drop')
            graph2=json.loads(converted.read_text(encoding='utf-8'))
            audit,rep=summarize_graph(graph2,path=converted,file_sha256=digest(converted))
            if any(audit[k] for k in ['missing_node_ids','ambiguous_node_id_count','dangling_edge_count','nonfinite_edge_count']):
                raise ValueError('Converted integrity failure')
            if not rep['features']:raise ValueError('No eligible features')
            rep['prompt_tokens']=meta['prompt_tokens'];rep['correct']=str(rep['top_token']).strip()==job['expected_label']
            row.update(status='ok',correct=rep['correct'],top_token=rep['top_token'],
                       input_tokens=meta['prompt_tokens'],feature_count=len(rep['features']),converted_sha256=digest(converted))
            reps_by_block.setdefault(job['block'],{})[(job['fact'],job['expected_label'],job['wording'])]=rep
        except Exception as error:
            row.update(status='invalid',error=str(error))
        audits.append(row)
        print(f'{model} audit {job["job_id"]}: {row["status"]}',flush=True)
    blocks=[];pairwise=[];nulls={};rng=np.random.default_rng(SEED)
    for block in sorted({j['block'] for j in jobs}):
        reps=reps_by_block.get(block,{})
        rec={'block':block,'graph_n':len(reps),'complete':len(reps)==8}
        if len(reps)!=8:
            rec['retrieval_eligible']=False;blocks.append(rec);continue
        bags=[Counter(r['prompt_tokens']) for r in reps.values()]
        balanced=bool(bags[0]) and all(b==bags[0] for b in bags)
        correct=sum(r['correct'] for r in reps.values())
        rec.update(token_bags_identical=balanced,correct_n=correct,retrieval_eligible=balanced and correct==8)
        for metric in ['jaccard','weighted_cosine','error_inclusive_jaccard']:
            matrix=matrix_for(reps,metric)
            rec[metric]=contrasts(matrix)
            if metric=='jaccard':nulls[block]=fact_assignment_null(matrix)
            for i,(fact,label) in enumerate(KEYS):
                for j,(other,other_label) in enumerate(KEYS):
                    pairwise.append(dict(block=block,metric=metric,left_fact=fact,right_fact=other,left_label=label,
                                         right_label=other_label,similarity=float(matrix[i,j])))
        k=min(len(r['features']) for r in reps.values());vals=[]
        arrays={key:sorted(r['features']) for key,r in sorted(reps.items())}
        for _ in range(200):
            sampled={key:{'features':{arr[i] for i in rng.choice(len(arr),size=k,replace=False)}} for key,arr in arrays.items()}
            vals.append(contrasts(matrix_for(sampled,'jaccard'))['fact_effect'])
        rec['equal_count_sensitivity']={'k':k,'runs':200,'mean_fact_effect':float(np.mean(vals)),
                                        'resampling_range':[min(vals),max(vals)],'repetition_values':vals}
        blocks.append(rec)
    gate=len(blocks)==6 and all(r['retrieval_eligible'] for r in blocks)
    stats={'status':'not_estimable_under_full_retrieval_gate'}
    if gate:
        values=[b['jaccard']['fact_effect'] for b in blocks];observed=float(np.mean(values))
        pooled_null=[float(np.mean(combo)) for combo in itertools.product(*(nulls[b['block']] for b in blocks))]
        p=float(np.mean(np.array(pooled_null)>=observed-1e-12))
        family=json.loads((OUT/'freeze.json').read_text()).get('planned_primary_family_size',2)
        stats=dict(status='complete',n_blocks=6,mean_fact_effect=observed,
                   ci95=bootstrap_ci(values,runs=10000,seed=SEED),min_block_effect=min(values),
                   exact_conditional_assignment_p=p,planned_primary_family_size=family,bonferroni_planned_family_p=min(1,family*p),
                   null_assignments=len(pooled_null),positive_blocks=sum(v>0 for v in values))
        atomic_json(analysis/'primary_null.json',pooled_null)
    result=dict(model=model,retrieval_gate=gate,primary=stats,blocks=blocks,audits=audits,raw_hashes=hashes,
                script_sha256=digest(__file__),freeze_sha256=digest(OUT/'freeze.json'),seed=SEED,
                caveat='New forced-choice task, not proof of abstract semantics or recovery of original free-answer claims.')
    atomic_json(analysis/'results.json',json_ready(result))
    csv_write(analysis/'graph_audit.csv',audits);csv_write(analysis/'pairwise.csv',pairwise);csv_write(analysis/'block_results.csv',blocks)
    with (model_dir/'checksums.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['path','sha256']);w.writeheader();w.writerows({'path':p,'sha256':h} for p,h in hashes.items())
    plot_model(result)
    return result


def plot_model(result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.fonttype':'none','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,5))
    fig.subplots_adjust(left=.09,right=.98,bottom=.28,top=.8,wspace=.35)
    blocks=result['blocks'];labels=[b['block'].replace('_',' / ') for b in blocks]
    for i,b in enumerate(blocks):
        if 'jaccard' in b:
            for j,(key,color) in enumerate([('fact_effect','#0072B2'),('label_effect','#CC651D')]):
                axes[0].scatter(i+(j-.5)*.16,b['jaccard'][key],c=color,marker='o' if b['retrieval_eligible'] else 'x',s=45)
        axes[1].bar(i,b.get('correct_n',0),color='#009E73' if b.get('retrieval_eligible') else '#8C94A0')
        axes[1].text(i,b.get('correct_n',0)+.15,f'{b.get("correct_n",0)}/8',ha='center')
    axes[0].axhline(0,c='gray',ls='--');axes[0].set_ylabel('Cross-wording Jaccard contrast')
    axes[0].set_title('Fact (blue) and output-label (orange) effects')
    axes[1].set_ylim(0,9);axes[1].set_ylabel('Expected A/B top-label decisions');axes[1].set_title('Complete-block retrieval gate')
    for ax in axes:ax.set_xticks(range(len(blocks)),labels,rotation=40,ha='right')
    fig.suptitle(f'{result["model"]}: matched-choice controls - retrieval gate {"PASS" if result["retrieval_gate"] else "NOT MET"}',fontsize=14)
    for ext in ['png','svg']:fig.savefig(OUT/result['model']/f'control_results.{ext}',dpi=200)
    plt.close(fig)


def overview():
    status=json.loads((OUT/'status.json').read_text()) if (OUT/'status.json').exists() else {}
    lines=[f'# {OUT.name}','',
           'New, prospectively specified forced-choice controls. Original paper cohorts remain unchanged.','',
           'All words and token counts are matched within each eight-cell block; query, output label, and word order vary.','',
           '| Model | Pilot | Graphs | Analysis |','|---|---:|---:|---|']
    for model in MODELS:
        m=status.get('models',{}).get(model,{})
        gate=m.get('pilot',{})
        preview_n=len(list((OUT/model/'pilot').glob('*/response.json')))
        graph_n=len(list((OUT/model/'graphs').glob('*/raw_graph.json')))
        state=m.get('state','pending')
        if status.get('state')=='running' and status.get('current_model')==model:
            state=f'{status.get("stage","work")} running'
        pilot_label=f'{gate["correct"]}/8 correct' if 'correct' in gate else f'{preview_n}/8 archived; gate pending'
        lines.append(f'| {model} | {pilot_label} | {graph_n}/48 | {state} |')
        path=OUT/model/'analysis/results.json'
        if path.exists():
            result=json.loads(path.read_text());lines.extend(['',f'## {model}', '',f'Full retrieval gate: {result["retrieval_gate"]}.', '',json.dumps(result['primary'],indent=2)])
    lines.extend(['','Qwen3-1.7B is deferred: the hosted 10-token limit cannot fit this 29-token control design.',
                  '', 'Pilot failure stops graph generation for that model; no replacement prompts are silently substituted.',
                  '', 'For current state see status.json and stdout/stderr logs. A running process can take several hours under the shared 30-requests/hour ceiling.'])
    (OUT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--model',choices=list(MODELS))
    parser.add_argument('--experiment',choices=['matched_choice_v1','matched_choice_chat_v2'],default='matched_choice_v1');args=parser.parse_args()
    if args.experiment=='matched_choice_chat_v2':
        import matched_choice_chat_controls as design
        configure_experiment(design.OUT,design.make_jobs,design.MODELS)
    if args.model:analyze_model(args.model)
    overview()
