"""Read-only audit of archived matched-choice and selected-failure graphs.

Writes a separate exploratory package, never overwrites frozen estimates.
"""
import itertools
import json
from pathlib import Path
import sys

import numpy as np
from scipy.stats import t

sys.path.insert(0,str(Path(__file__).resolve().parent))
from matched_choice_controls import ROOT, digest
from control_io import atomic_json
from analyze_matched_choice_controls import contrasts, matrix_for, csv_write
from whole_graph_analysis import is_feature_node, node_identity, jaccard, sparse_cosine

OUT=ROOT/'data/model_extension/final_closeout_20261005'
V2=ROOT/'data/model_extension/matched_choice_chat_v2/qwen3-4b/analysis/results.json'
FAIL=ROOT/'data/model_extension/failure_case_graphs_v1'
VARIANTS=['full','exclude_final_position','exclude_last_quarter_layers','exclude_both']
SOURCES={}


def load(path):
    SOURCES[str(path.relative_to(ROOT))]=digest(path)
    return json.loads(path.read_text(encoding='utf-8'))


def summary(values,seed=20261005):
    a=np.asarray(values,dtype=float);n=len(a)
    if n<2: return {'n':n,'status':'insufficient_blocks'}
    rng=np.random.default_rng(seed)
    means=a[rng.integers(0,n,size=(20000,n))].mean(axis=1)
    observed=float(a.mean());se=float(a.std(ddof=1)/np.sqrt(n))
    null=np.array([np.mean(a*np.array(s)) for s in itertools.product([-1,1],repeat=n)]) if n<=20 else None
    return dict(n=n,mean=observed,sd=float(a.std(ddof=1)),positive_n=int(sum(a>0)),
                bootstrap_ci95=np.quantile(means,[.025,.975]).tolist(),
                t_ci95=[observed-float(t.ppf(.975,n-1))*se,observed+float(t.ppf(.975,n-1))*se],
                two_sided_sign_flip_p=float(np.mean(np.abs(null)>=abs(observed)-1e-12)) if null is not None else None,
                sign_flip_assumption='Independent blocks with symmetric block contrasts under the zero-centered null; not a randomized causal test.')


def representations(graph):
    nodes=[n for n in graph['nodes'] if is_feature_node(n)]
    positions=[n['ctx_idx'] for n in graph['nodes'] if n.get('node_type')=='logit']
    assert positions and len(set(positions))==1
    final=positions[0];last=max(n['layer'] for n in nodes);cut=int(np.floor(.75*(last+1)))
    result={}
    for variant in VARIANTS:
        kept=[n for n in nodes if not (variant in ['exclude_final_position','exclude_both'] and n['ctx_idx']==final)
              and not (variant in ['exclude_last_quarter_layers','exclude_both'] and n['layer']>=cut)]
        weights={}
        for node in kept:
            ident=node_identity(node);weights[ident]=weights.get(ident,0)+abs(float(node.get('influence') or 0))
        result[variant]={'features':set(weights),'feature_weights':weights}
    return result,dict(final_position=final,max_feature_layer=last,late_layer_cutoff=cut,
                       counts={v:len(r['features']) for v,r in result.items()})


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    result=load(V2);blocks={};audits=[]
    for row in result['audits']:
        raw=ROOT/row['raw_path'];assert digest(raw)==result['raw_hashes'][row['raw_path']]
        SOURCES[str(raw.relative_to(ROOT))]=digest(raw)
        path=raw.parent/'converted_graph.json';assert digest(path)==row['converted_sha256']
        reps,info=representations(load(path))
        blocks.setdefault(row['block'],{})[(row['fact'],row['expected_label'],row['wording'])]=reps
        audits.append(dict(study='matched_choice',job_id=row['job_id'],**info))
    rows=[];summaries={}
    for variant in VARIANTS:
        for metric in ['jaccard','weighted_cosine']:
            vals=[]
            for block,cells in sorted(blocks.items()):
                reps={key:value[variant] for key,value in cells.items()}
                valid=all(r['features'] for r in reps.values())
                if not valid:
                    rows.append(dict(block=block,variant=variant,metric=metric,status='empty_representation'));continue
                c=contrasts(matrix_for(reps,metric));c['label_condition_difference']=c['fact_same_label']-c['fact_different_label']
                if variant=='full':
                    archived=next(b for b in result['blocks'] if b['block']==block)[metric]
                    assert all(np.isclose(c[k],v,rtol=0,atol=1e-12) for k,v in archived.items())
                rows.append(dict(block=block,variant=variant,metric=metric,status='ok',**c));vals.append(c)
            summaries[f'{variant}/{metric}']={k:summary([v[k] for v in vals]) for k in
                ['fact_effect','fact_same_label','fact_different_label','label_effect','label_condition_difference']}
    failure=load(FAIL/'analysis/results.json');jobs=load(FAIL/'jobs.json');f_reps={}
    for row in failure['audits']:
        folder=FAIL/'qwen3-4b/graphs'/row['job_id'];raw=folder/'raw_graph.json';path=folder/'converted_graph.json'
        assert digest(raw)==row['raw_sha256'];SOURCES[str(raw.relative_to(ROOT))]=digest(raw)
        assert digest(path)==row['converted_sha256']
        f_reps[row['job_id']],info=representations(load(path));audits.append(dict(study='failure',job_id=row['job_id'],**info))
    frows=[]
    for job in jobs:
        if job['reference']!='ordinal':continue
        for variant in VARIANTS:
            a,b,c=[f_reps[k][variant] for k in [job['job_id'],job['same_country_partner'],job['same_output_partner']]]
            valid=all(x['features'] for x in [a,b,c])
            r=dict(job_id=job['job_id'],response_format=job['response_format'],variant=variant,status='ok' if valid else 'empty_representation')
            if valid:
                r.update(same_country=jaccard(a['features'],b['features']),same_output=jaccard(a['features'],c['features']))
                r['output_minus_country']=r['same_output']-r['same_country']
                if variant=='full':
                    old=next(x for x in failure['comparisons'] if x['job_id']==job['job_id'])['jaccard']
                    assert all(np.isclose(r[k],v,rtol=0,atol=1e-12) for k,v in old.items())
            frows.append(r)
    csv_write(OUT/'matched_choice_sensitivity.csv',rows);csv_write(OUT/'failure_sensitivity.csv',frows)
    csv_write(OUT/'representation_counts.csv',audits)
    results=dict(status='complete',analysis_status='exploratory_after_outcome_inspection',matched_choice=summaries,
                 inference_caveat='Six block contrasts are the sample; original 4096 correspondence assignments are null configurations, not independent observations.',
                 filter_caveat='Remove nodes at the final prediction context position and/or the last quarter of observed feature layers before collapsing feature identity. Not causal ablation; retained graphs remain output-conditioned.',
                 sources=SOURCES,script_sha256=digest(__file__))
    atomic_json(OUT/'statistics_audit.json',results)
    s=summaries['full/jaccard']['label_condition_difference']
    lines=['# Final statistical and graph-location audit','',
           'Exploratory saved-data analysis, specified after inspecting earlier outcomes. Frozen results remain unchanged.','',
           f'The direct same-label minus changed-label fact contrast is {s["mean"]:.6f} across {s["n"]} blocks. Its descriptive block-bootstrap 95% interval is {s["bootstrap_ci95"]}; Student-t interval is {s["t_ci95"]}; two-sided block sign-flip p={s["two_sided_sign_flip_p"]}. These summaries require block independence; the sign-flip test additionally assumes null symmetry.','',
           'The original exact correspondence test uses 4096 reassigned graph correspondences within six blocks. It tests that conditional null, not population replication across 4096 samples. It is not evidence of a randomized causal effect.','',
           '| Representation | Balanced fact contrast | Same-label minus changed-label contrast | Output-label contrast |','|---|---:|---:|---:|']
    for v in VARIANTS:
        x=summaries[v+'/jaccard'];lines.append(f'| {v} | {x["fact_effect"].get("mean",float("nan")):.6f} | {x["label_condition_difference"].get("mean",float("nan")):.6f} | {x["label_effect"].get("mean",float("nan")):.6f} |')
    lines+=['','Filters are sensitivity analyses, not interventions. Empty representations are unavailable rather than scored as zero. Selected failure comparisons remain descriptive and dependent; no population p-values are attached.','',
            '| Failure response format | Representation | Comparisons available | Favor same output | Mean overlap difference |','|---|---|---:|---:|---:|']
    for fmt in ['label','capital']:
        for v in VARIANTS:
            values=[r['output_minus_country'] for r in frows if r['response_format']==fmt and r['variant']==v and r['status']=='ok']
            lines.append(f'| {fmt} | {v} | {len(values)} | {sum(x>0 for x in values)} | {np.mean(values) if values else float("nan"):.6f} |')
    (OUT/'STATISTICAL_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    for path,sha in SOURCES.items():assert digest(ROOT/path)==sha
    print(json.dumps(s,indent=2),flush=True)
    print(f'Saved audit: {OUT}',flush=True)


if __name__=='__main__':main()
