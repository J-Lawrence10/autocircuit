"""Frozen v3 cross-position analysis; all output summaries retain component contrasts."""
from collections import Counter
import itertools
import json

import numpy as np

from matched_choice_position_controls import ROOT, OUT, SEED, make_jobs, digest
from control_io import atomic_json
from run_matched_choice_controls import clean_prompt
from analyze_matched_choice_controls import KEYS, contrasts, fact_assignment_null, csv_write
from convert_model_extension import load_converter, raw_integrity
from whole_graph_analysis import summarize_graph, jaccard, sparse_cosine, finite_number, bootstrap_ci, json_ready


def matrix_for(reps, metric, left_position, right_position):
    def sim(a,b):
        if metric=='weighted_cosine':
            return sparse_cosine(a['feature_weights'],b['feature_weights'])
        key='features_with_errors' if metric=='error_inclusive_jaccard' else 'features'
        return jaccard(a[key],b[key])
    return np.array([[sim(reps[(f,l,left_position,0)],reps[(ff,ll,right_position,1)])
                      for ff,ll in KEYS] for f,l in KEYS])


def position_contrasts(reps, metric='jaccard'):
    matrices={(p,q):matrix_for(reps,metric,p,q) for p,q in itertools.product(range(2),repeat=2)}
    cross=(matrices[(0,1)]+matrices[(1,0)])/2
    within=(matrices[(0,0)]+matrices[(1,1)])/2
    return dict(cross_position=contrasts(cross),within_position=contrasts(within),
                position_effect=float(within.mean()-cross.mean())), matrices, cross


def audit_graph(job, model, converter):
    folder=OUT/model/'graphs'/job['job_id'];raw=folder/'raw_graph.json'
    converted=folder/'converted_graph.json'
    row={**job,'model':model,'raw_path':str(raw.relative_to(ROOT))}
    try:
        metadata=json.loads((folder/'metadata.json').read_text())
        row['raw_sha256']=digest(raw)
        if row['raw_sha256']!=metadata['sha256']:raise ValueError('Raw checksum mismatch')
        graph=json.loads(raw.read_text(encoding='utf-8'));meta=graph['metadata']
        integrity=raw_integrity(graph);row.update(integrity)
        if integrity['raw_missing_node_id_count'] or integrity['raw_orphan_edge_count']:
            raise ValueError('Missing raw IDs or orphan edges')
        if any(finite_number(e.get('weight')) is None for e in graph.get('links',graph.get('edges',[]))):
            raise ValueError('Nonfinite raw weights')
        if clean_prompt(meta['prompt'])!=job['prompt'] or meta.get('scan',meta.get('model'))!=model:
            raise ValueError('Raw model/prompt mismatch')
        settings=meta.get('generation_settings',{});pruning=meta.get('pruning_settings',{})
        if not np.isclose(meta.get('node_threshold',-1),.8) or not np.isclose(pruning.get('edge_threshold',-1),.85):
            raise ValueError('Pruning mismatch')
        if settings.get('max_n_logits')!=10 or not np.isclose(settings.get('desired_logit_prob',-1),.99):
            raise ValueError('Generation settings mismatch')
        if meta.get('info',{}).get('transcoder_set')!='mwhanna/qwen3-4b-transcoders':
            raise ValueError('Decomposition source mismatch')
        if not converted.exists():
            converter(str(raw),str(converted),prompt=None,model_id=model,ambiguous_node_policy='drop')
        row['converted_sha256']=digest(converted)
        audit,rep=summarize_graph(json.loads(converted.read_text(encoding='utf-8')),
                                  path=converted,file_sha256=row['converted_sha256'])
        if any(audit[k] for k in ['missing_node_ids','ambiguous_node_id_count','dangling_edge_count','nonfinite_edge_count']):
            raise ValueError('Converted integrity failure')
        if not rep['features']:raise ValueError('No eligible features')
        rep.update(prompt_tokens=meta['prompt_tokens'],correct=str(rep['top_token']).strip()==job['expected_label'],
                   raw_clean=not(integrity['raw_ambiguous_node_id_count'] or integrity['raw_duplicate_endpoint_edge_count']))
        row.update(status='ok',correct=rep['correct'],raw_clean=rep['raw_clean'],top_token=rep['top_token'],
                   input_tokens=meta['prompt_tokens'],feature_count=len(rep['features']))
        return row,rep
    except Exception as error:
        return {**row,'status':'invalid','error':str(error)},None


def analyze_model(model='qwen3-4b'):
    analysis=OUT/model/'analysis';analysis.mkdir(parents=True,exist_ok=True)
    converter=load_converter();jobs=[j for j in make_jobs() if j['split']=='held_out']
    groups={};audits=[];hashes={};pairwise=[]
    for job in jobs:
        row,rep=audit_graph(job,model,converter);audits.append(row)
        if 'raw_sha256' in row:hashes[row['raw_path']]=row['raw_sha256']
        if rep is not None:
            groups.setdefault(job['block'],{})[(job['fact'],job['expected_label'],job['position'],job['wording'])]=rep
        print(f'v3 audit {job["job_id"]}: {row["status"]}',flush=True)
    blocks=[];nulls={};rng=np.random.default_rng(SEED)
    for block in sorted({j['block'] for j in jobs}):
        reps=groups.get(block,{})
        rec=dict(block=block,graph_n=len(reps),complete=len(reps)==16,retrieval_eligible=False)
        if len(reps)!=16:blocks.append(rec);continue
        bags=[Counter(r['prompt_tokens']) for r in reps.values()]
        balance=bool(bags[0]) and all(b==bags[0] for b in bags)
        correct=sum(r['correct'] for r in reps.values());clean=all(r['raw_clean'] for r in reps.values())
        rec.update(correct_n=correct,token_bags_identical=balance,raw_clean=clean,
                   retrieval_eligible=balance and clean and correct==16)
        for metric in ['jaccard','weighted_cosine','error_inclusive_jaccard']:
            result,matrices,cross=position_contrasts(reps,metric);rec[metric]=result
            if metric=='jaccard':nulls[block]=fact_assignment_null(cross)
            for (p,q),matrix in matrices.items():
                for i,(f,l) in enumerate(KEYS):
                    for j,(ff,ll) in enumerate(KEYS):
                        pairwise.append(dict(block=block,metric=metric,left_position=p,right_position=q,
                                             left_fact=f,right_fact=ff,left_label=l,right_label=ll,
                                             similarity=float(matrix[i,j])))
        arrays={key:sorted(rep['features']) for key,rep in sorted(reps.items())}
        k=min(map(len,arrays.values()));vals=[]
        for _ in range(200):
            sampled={key:{'features':{arr[i] for i in rng.choice(len(arr),size=k,replace=False)}} for key,arr in arrays.items()}
            result,_,_=position_contrasts(sampled)
            vals.append(result['cross_position']['fact_effect'])
        rec['equal_count_sensitivity']=dict(k=k,runs=200,mean_fact_effect=float(np.mean(vals)),
                                           resampling_range=[min(vals),max(vals)],repetition_values=vals)
        blocks.append(rec)
    gate=len(blocks)==6 and all(b['retrieval_eligible'] for b in blocks)
    stats={'status':'not_estimable_under_full_retrieval_gate'}
    if gate:
        values=[b['jaccard']['cross_position']['fact_effect'] for b in blocks]
        observed=float(np.mean(values))
        null=[float(np.mean(combo)) for combo in itertools.product(*(nulls[b['block']] for b in blocks))]
        p=float(np.mean(np.array(null)>=observed-1e-12))
        stats=dict(status='complete',n_blocks=6,mean_fact_effect=observed,
                   ci95=bootstrap_ci(values,runs=10000,seed=SEED),min_block_effect=min(values),
                   positive_blocks=sum(v>0 for v in values),exact_conditional_assignment_p=p,
                   conservative_cumulative_family_p=min(1,4*p),null_assignments=len(null))
        atomic_json(analysis/'primary_null.json',null)
    result=dict(model=model,experiment=OUT.name,retrieval_gate=gate,primary=stats,blocks=blocks,
                audits=audits,raw_hashes=hashes,freeze_sha256=digest(OUT/'freeze.json'),script_sha256=digest(__file__),seed=SEED,
                caveat='Outcome-informed task follow-up using previously studied countries; not an unseen-facts replication or causal semantic-circuit test.')
    atomic_json(analysis/'results.json',json_ready(result))
    csv_write(analysis/'graph_audit.csv',audits);csv_write(analysis/'pairwise.csv',pairwise)
    csv_write(analysis/'block_results.csv',blocks)
    csv_write(OUT/model/'checksums.csv',[dict(path=p,sha256=h) for p,h in hashes.items()])
    return result
