"""Descriptive, integrity-gated comparisons and local signed edge evidence."""
from collections import Counter,defaultdict
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from failure_case_design import ROOT,OUT,MODEL,SEED,make_jobs,token_roles,digest
from control_io import atomic_json
from convert_model_extension import raw_integrity,load_converter
from whole_graph_analysis import summarize_graph,jaccard,sparse_cosine,is_feature_node,is_error_node,finite_number,json_ready
from analyze_matched_choice_controls import csv_write


def source_type(node):
    if is_error_node(node):return 'reconstruction_error'
    if is_feature_node(node):return 'feature'
    return str(node.get('node_type','unknown'))


def clean_export(raw_audit,converted_audit):
    return not(raw_audit['raw_ambiguous_node_id_count'] or raw_audit['raw_duplicate_endpoint_edge_count']
               or converted_audit['duplicate_endpoint_edge_count'])


def local_edges(graph,roles,observed):
    nodes={str(n['id']):n for n in graph['nodes']};edges=graph['edges']
    targets=[key for key,n in nodes.items() if n.get('node_type')=='logit' and str(n.get('token','')).strip()==observed]
    # Multiple token IDs can decode identically after trimming: do not silently pick one.
    if len(targets)!=1:return dict(status='missing_or_ambiguous_observed_logit',targets=targets),[],[],[],[]
    target=targets[0];incoming=defaultdict(list)
    for e in edges:incoming[str(e['target'])].append(e)
    role_lookup={r['token_index']:r['role'] for r in roles}
    def annotate(e,depth):
        n=nodes[str(e['source'])];idx=n.get('ctx_idx')
        return dict(source=str(e['source']),target=str(e['target']),weight=float(e['weight']),
                    absolute_weight=abs(float(e['weight'])),depth=depth,source_type=source_type(n),
                    source_role=role_lookup.get(idx,'unmapped'),source_ctx_idx=idx,
                    source_layer=n.get('layer'),source_feature_id=n.get('feature_id'),
                    source_has_no_incoming=not incoming.get(str(e['source'])))
    direct=[annotate(e,1) for e in incoming[target]]
    parents={r['source'] for r in direct}
    upstream=[annotate(e,2) for p in sorted(parents) for e in incoming[p]]
    total=sum(r['absolute_weight'] for r in direct)
    groups=defaultdict(list)
    for r in direct:groups[(r['source_type'],r['source_role'])].append(r)
    totals=[dict(source_type=t,source_role=role,edge_count=len(rs),signed_weight=sum(r['weight'] for r in rs),
                 absolute_weight=sum(r['absolute_weight'] for r in rs),
                 fraction=sum(r['absolute_weight'] for r in rs)/total if total else None)
            for (t,role),rs in sorted(groups.items())]
    def top(rs):return sorted(rs,key=lambda r:(-r['absolute_weight'],r['source'],r['target']))[:10]
    chosen=top(direct);selected=list(chosen);omitted=[]
    omitted.append(dict(target=target,depth=1,omitted_abs_weight=total-sum(r['absolute_weight'] for r in chosen)))
    visible_parents={r['source'] for r in chosen}
    candidates=[x for x in upstream if x['target'] in visible_parents]
    keep=top(candidates);selected.extend(keep)
    omitted.append(dict(target='displayed_direct_predecessors',depth=2,
                        omitted_abs_weight=sum(x['absolute_weight'] for x in candidates)-sum(x['absolute_weight'] for x in keep)))
    feature_total=sum(r['absolute_weight'] for r in direct if r['source_type']=='feature')
    for row in totals:
        row['feature_only_fraction']=row['absolute_weight']/feature_total if row['source_type']=='feature' and feature_total else None
    info=dict(status='ok',observed_logit_id=target,direct_edge_n=len(direct),direct_abs_weight=total,
              direct_signed_weight=sum(r['weight'] for r in direct),
              direct_error_fraction=sum(r['absolute_weight'] for r in direct if r['source_type']=='reconstruction_error')/total if total else None,
              direct_source_without_incoming_fraction=sum(r['absolute_weight'] for r in direct if r['source_has_no_incoming'])/total if total else None,
              omitted_by_target=omitted,selected_edges=selected,
              display_rule='Top ten direct edges; top ten upstream edges into those displayed direct predecessors, globally ranked by absolute weight then IDs.')
    return info,direct,upstream,totals,list(nodes.values())


def analyze_graph(job,converter):
    folder=OUT/MODEL/'graphs'/job['job_id'];raw=folder/'raw_graph.json';converted=folder/'converted_graph.json'
    row=dict(job_id=job['job_id'],arm=job['arm'],case=job['case'],response_format=job['response_format'],
             reference=job['reference'],expected=job['expected_label'],preview=job['preview_answer'],
             status='invalid',clean_eligible=False)
    try:
        meta_saved=json.loads((folder/'metadata.json').read_text());row['raw_sha256']=digest(raw)
        if row['raw_sha256']!=meta_saved['sha256']:raise ValueError('Raw checksum mismatch')
        g=json.loads(raw.read_text(encoding='utf-8'));meta=g['metadata'];audit=raw_integrity(g);row.update(audit)
        if meta.get('scan',meta.get('model'))!=MODEL or meta.get('prompt')!=job['prompt']:raise ValueError('Model or prompt mismatch')
        roles=token_roles(job)
        if meta['prompt_tokens']!=[r['token'] for r in roles]:raise ValueError('Exact token sequence mismatch')
        if meta.get('info',{}).get('transcoder_set')!='mwhanna/qwen3-4b-transcoders':raise ValueError('Decomposition source mismatch')
        settings=meta.get('generation_settings',{});pruning=meta.get('pruning_settings',{})
        if not np.isclose(meta.get('node_threshold',-1),.8) or not np.isclose(pruning.get('edge_threshold',-1),.85):raise ValueError('Threshold mismatch')
        if settings.get('max_n_logits')!=10 or not np.isclose(settings.get('desired_logit_prob',-1),.99):raise ValueError('Logit settings mismatch')
        if settings.get('max_feature_nodes')!=5000:raise ValueError('Feature-node limit mismatch')
        if audit['raw_missing_node_id_count'] or audit['raw_orphan_edge_count']:raise ValueError('Missing raw IDs/endpoints')
        if any(finite_number(e.get('weight')) is None for e in g.get('links',g.get('edges',[]))):raise ValueError('Nonfinite edge weight')
        if not converted.exists():converter(str(raw),str(converted),prompt=None,model_id=MODEL,ambiguous_node_policy='drop')
        row['converted_sha256']=digest(converted);graph=json.loads(converted.read_text(encoding='utf-8'))
        ca,rep=summarize_graph(graph,path=converted,file_sha256=row['converted_sha256'])
        if any(ca[k] for k in ['missing_node_ids','ambiguous_node_id_count','dangling_edge_count','nonfinite_edge_count']):raise ValueError('Converted integrity failure')
        if not rep['features']:raise ValueError('No usable feature identities')
        positions=[n.get('ctx_idx') for n in graph['nodes']]
        if any(not isinstance(p,int) or p<0 or p>=len(roles) for p in positions):raise ValueError('Node token position outside verified prompt')
        observed=str(rep['top_token']).strip()
        info,direct,upstream,groups,_=local_edges(graph,roles,observed)
        target_tokens=[str(n.get('token','')).strip() for n in graph['nodes'] if n.get('node_type')=='logit']
        row.update(status='ok',observed=observed,correct=observed==job['expected_label'],
                   drift=observed!=job['preview_answer'],feature_n=len(rep['features']),
                   clean_eligible=clean_export(audit,ca),
                   correct_logit_available=job['expected_label'] in target_tokens,
                   error_influence_fraction=ca['error_influence_fraction'],error_incident_edge_weight_fraction=ca['error_incident_edge_weight_fraction'],
                   local={k:v for k,v in info.items() if k not in ['selected_edges','omitted_by_target']})
        atomic_json(folder/'local_neighborhood.json',info)
        csv_write(folder/'token_roles.csv',roles);csv_write(folder/'nodes.csv',graph['nodes']);csv_write(folder/'edges.csv',graph['edges'])
        csv_write(folder/'direct_answer_edges.csv',direct);csv_write(folder/'upstream_answer_edges.csv',upstream)
        csv_write(folder/'source_role_totals.csv',groups)
        csv_write(folder/'layer_profile.csv',[dict(layer=l,influence_fraction=v) for l,v in sorted(rep['layer_profile'].items())])
        csv_write(folder/'edge_layer_profile.csv',[dict(source_layer=k[0],target_layer=k[1],absolute_weight_fraction=v) for k,v in sorted(rep['edge_flow'].items())])
        row['source_role_totals']=groups
        return row,rep
    except Exception as error:
        row['error']=str(error);return row,None


def compare_triple(job,audits,reps):
    ids=[job['job_id'],job['same_country_partner'],job['same_output_partner']]
    row=dict(job_id=ids[0],same_country_partner=ids[1],same_output_partner=ids[2],case=job['case'],response_format=job['response_format'])
    if any(i not in reps for i in ids):return {**row,'status':'missing_or_invalid_graph','clean_eligible':False}
    a,b,c=[reps[i] for i in ids];ar,br,cr=[audits[i] for i in ids]
    output_match=ar['observed']==cr['observed'];correct_controls=br['correct'] and cr['correct']
    clean=all(r['clean_eligible'] for r in [ar,br,cr]) and output_match and correct_controls and not ar['correct']
    row.update(status='ok',clean_eligible=clean,output_match=output_match,correct_controls=correct_controls,
               failure_reproduced=not ar['correct'],drift=any(r['drift'] for r in [ar,br,cr]))
    for name,key in [('jaccard','features'),('error_inclusive_jaccard','features_with_errors')]:
        sc=jaccard(a[key],b[key]);so=jaccard(a[key],c[key])
        row[name]=dict(same_country=sc,same_output=so,output_minus_country=so-sc)
    sc=sparse_cosine(a['feature_weights'],b['feature_weights']);so=sparse_cosine(a['feature_weights'],c['feature_weights'])
    row['weighted_cosine']=dict(same_country=sc,same_output=so,output_minus_country=so-sc)
    # Per-triple seed makes resuming/graph order irrelevant to the sensitivity.
    import hashlib
    seed=SEED+int(hashlib.sha256(ids[0].encode()).hexdigest()[:8],16)
    rng=np.random.default_rng(seed);arrays=[sorted(r['features']) for r in [a,b,c]];k=min(map(len,arrays));samples=[]
    for _ in range(200):
        sets=[{arr[i] for i in rng.choice(len(arr),size=k,replace=False)} for arr in arrays]
        sc=jaccard(sets[0],sets[1]);so=jaccard(sets[0],sets[2]);samples.append(dict(same_country=sc,same_output=so,output_minus_country=so-sc))
    row['equal_count']=dict(k=k,seed=seed,repetitions=200,means={key:float(np.mean([x[key] for x in samples])) for key in samples[0]},samples=samples)
    return row


def main():
    jobs=make_jobs();converter=load_converter();audits={};reps={}
    for job in jobs:
        row,rep=analyze_graph(job,converter);audits[job['job_id']]=row
        if rep is not None:reps[job['job_id']]=rep
        print(f'{job["job_id"]}: {row["status"]}',flush=True)
    triples=[compare_triple(j,audits,reps) for j in jobs if j['reference']=='ordinal']
    result=dict(model=MODEL,audits=list(audits.values()),comparisons=triples,
                valid_graphs=sum(r['status']=='ok' for r in audits.values()),
                clean_graphs=sum(r['clean_eligible'] for r in audits.values()),
                clean_comparisons=sum(r['clean_eligible'] for r in triples),planned_graphs=16,
                seed=SEED,freeze_sha256=digest(OUT/'freeze.json'),analysis_sha256=digest(__file__),
                caveat='Exploratory selected failures in one country pair. Associations are not causal effects; no p-values or population confidence intervals.')
    analysis=OUT/'analysis';atomic_json(analysis/'results.json',json_ready(result))
    csv_write(analysis/'graph_audit.csv',result['audits'])
    csv_write(analysis/'comparisons.csv',[{k:v for k,v in r.items() if k!='equal_count'} for r in triples])
    csv_write(analysis/'equal_count_samples.csv',[dict(job_id=r['job_id'],repetition=i,**x) for r in triples if 'equal_count' in r for i,x in enumerate(r['equal_count']['samples'])])
    csv_write(OUT/'checksums.csv',[dict(job_id=r['job_id'],raw_sha256=r.get('raw_sha256'),converted_sha256=r.get('converted_sha256')) for r in audits.values()])
    return result


if __name__=='__main__':main()
