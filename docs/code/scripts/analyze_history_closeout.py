"""Frozen final history analysis; preserves all exclusions and the block-level estimand."""
from collections import Counter
import json

import numpy as np
from scipy.stats import t

import history_choice_closeout as design
from control_io import atomic_json
from matched_choice_controls import ROOT, digest
from run_matched_choice_controls import clean_prompt
from analyze_matched_choice_controls import contrasts, matrix_for, csv_write
from convert_model_extension import load_converter, raw_integrity, converted_integrity
from whole_graph_analysis import summarize_graph, finite_number, json_ready
from audit_paper_closeout import representations, VARIANTS

SEED=20261005


def block_statistics(values):
    a=np.asarray(values,dtype=float);n=len(a)
    if n<2:return dict(status='insufficient_blocks',n=n)
    if n>20 or not np.all(np.isfinite(a)):raise ValueError('Invalid block values')
    mean=float(a.mean());sd=float(a.std(ddof=1));half=float(t.ppf(.975,n-1)*sd/np.sqrt(n))
    rng=np.random.default_rng(SEED);boots=a[rng.integers(0,n,size=(20000,n))].mean(axis=1)
    # Enumerate exact signs in chunks without creating a 2^20 by 20 matrix at once.
    exceed=0
    for start in range(0,2**n,4096):
        ids=np.arange(start,min(start+4096,2**n),dtype=np.uint32)
        signs=((ids[:,None] >> np.arange(n,dtype=np.uint32)) & 1).astype(float)*2-1
        exceed+=int(np.sum(np.abs(signs@a/n)>=abs(mean)-1e-12))
    return dict(status='complete',n=n,mean=mean,sd=sd,positive_n=int(sum(a>0)),
                t_ci95=[mean-half,mean+half],bootstrap_ci95=np.quantile(boots,[.025,.975]).tolist(),
                exact_two_sided_sign_flip_p=exceed/(2**n),null_assignments=2**n)


def eligibility(blocks):
    supported=[b for b in blocks if b.get('correct_response_supported',False)]
    counts=Counter(b['theme'] for b in supported)
    return len(blocks)==20 and len(supported)>=16 and all(counts[x]>=6 for x in ['documents','space'])


def contrast_set(reps,metric='jaccard'):
    result=contrasts(matrix_for(reps,metric))
    result['label_condition_difference']=result['fact_same_label']-result['fact_different_label']
    return result


def analyze():
    from run_history_closeout import verify_freeze
    freeze,jobs=verify_freeze();out=design.OUT/'analysis';out.mkdir(parents=True,exist_ok=True)
    pilot=json.loads((design.OUT/'pilot_gate.json').read_text())
    if not pilot['passed']:
        result=dict(state='pilot_failed',pilot=pilot,primary=dict(status='not_run_pilot_failed'),graphs_requested=0,
                    freeze_sha256=digest(design.OUT/'freeze.json'))
        atomic_json(out/'results.json',result)
        (out/'RESULTS.md').write_text(f'# Final history study: pilot did not pass\n\n{pilot["correct"]}/20 fixed preview checks passed. No evaluation graphs were requested. This is a behavioral feasibility result, not a null graph-overlap result. No further design round is planned. See pilot_gate.json for every response.\n',encoding='utf-8')
        return result
    evaluation=[j for j in jobs if j['split']=='held_out'];convert=load_converter()
    by_block={};audits=[];hashes={};missing=0
    for job in evaluation:
        folder=design.OUT/design.MODEL/'graphs'/job['job_id'];raw=folder/'raw_graph.json';converted=folder/'converted_graph.json'
        row=dict(job_id=job['job_id'],block=job['block'],theme=job['theme'],expected_label=job['expected_label'],status='missing',correct=None)
        if not raw.exists():
            missing+=1;audits.append(row);continue
        try:
            record=json.loads((folder/'metadata.json').read_text());sha=digest(raw)
            if sha!=record['sha256']:raise ValueError('Raw checksum mismatch')
            hashes[str(raw.relative_to(ROOT))]=sha
            graph=json.loads(raw.read_text(encoding='utf-8'));meta=graph['metadata'];integ=raw_integrity(graph);row.update(integ)
            if clean_prompt(meta['prompt'])!=job['prompt'] or meta.get('scan',meta.get('model'))!=design.MODEL:raise ValueError('Prompt/model mismatch')
            if meta.get('info',{}).get('transcoder_set')!='mwhanna/qwen3-4b-transcoders':raise ValueError('Decomposition mismatch')
            settings=meta.get('generation_settings',{});pruning=meta.get('pruning_settings',{})
            if not np.isclose(meta.get('node_threshold',-1),.8) or not np.isclose(pruning.get('edge_threshold',-1),.85):raise ValueError('Pruning mismatch')
            if settings.get('max_n_logits')!=10 or not np.isclose(settings.get('desired_logit_prob',-1),.99):raise ValueError('Generation setting mismatch')
            if record.get('settings')!=freeze['settings']:raise ValueError('Requested setting mismatch')
            # Behavior is recovered separately from raw integrity whenever prompt/model provenance is valid.
            # Converted representation identifies top logit using the same tested helper as earlier cohorts.
            if not converted.exists():convert(str(raw),str(converted),prompt=None,model_id=design.MODEL,ambiguous_node_policy='drop')
            cg=json.loads(converted.read_text(encoding='utf-8'));ca,rep=summarize_graph(cg,path=converted,file_sha256=digest(converted))
            row.update(top_token=rep['top_token'],correct=str(rep['top_token']).strip()==job['expected_label'])
            if any(integ[k] for k in ['raw_missing_node_id_count','raw_ambiguous_node_id_count','raw_orphan_edge_count','raw_duplicate_endpoint_edge_count']):raise ValueError('Raw graph integrity failure')
            if any(finite_number(e.get('weight')) is None for e in graph.get('links',graph.get('edges',[]))):raise ValueError('Nonfinite raw edge')
            ci=converted_integrity(cg)
            if any(ci[k] for k in ['converted_missing_node_id_count','converted_duplicate_node_id_count','converted_orphan_edge_count','converted_duplicate_endpoint_edge_count']):raise ValueError('Converted integrity failure')
            if ca['nonfinite_edge_count'] or not rep['features']:raise ValueError('No finite eligible representation')
            variants,counts=representations(cg)
            row.update(status='ok',converted_sha256=digest(converted),feature_count=len(rep['features']),representation_counts=counts)
            hashes[str(converted.relative_to(ROOT))]=digest(converted)
            by_block.setdefault(job['block'],{})[(job['fact'],job['expected_label'],job['wording'])]=dict(rep=rep,variants=variants,correct=row['correct'],tokens=meta['prompt_tokens'])
        except Exception as error:row.update(status='invalid',error=str(error))
        audits.append(row)
    blocks=[];sens=[];rng=np.random.default_rng(SEED)
    for name in sorted({j['block'] for j in evaluation}):
        theme=next(j['theme'] for j in evaluation if j['block']==name);cells=by_block.get(name,{})
        block=dict(block=name,theme=theme,valid_graphs=len(cells),correct_response_supported=False)
        if len(cells)==8:
            bags=[Counter(c['tokens']) for c in cells.values()];balanced=bool(bags[0]) and all(b==bags[0] for b in bags)
            block.update(correct_n=sum(c['correct'] for c in cells.values()),server_tokens_matched=balanced)
            block['correct_response_supported']=balanced and block['correct_n']==8
            if balanced:
                reps={k:v['rep'] for k,v in cells.items()}
                block['jaccard']=contrast_set(reps);block['weighted_cosine']=contrast_set(reps,'weighted_cosine')
                for variant in VARIANTS:
                    vr={k:v['variants'][variant] for k,v in cells.items()};valid=all(r['features'] for r in vr.values())
                    sens.append(dict(block=name,theme=theme,variant=variant,supported=block['correct_response_supported'],status='ok' if valid else 'empty',**(contrast_set(vr) if valid else {})))
                arrays={k:sorted(r['features']) for k,r in sorted(reps.items())};k=min(map(len,arrays.values()));draws=[]
                for _ in range(200):
                    sampled={key:{'features':{arr[i] for i in rng.choice(len(arr),k,replace=False)}} for key,arr in arrays.items()}
                    draws.append(contrast_set(sampled))
                block['equal_count']=dict(k=k,runs=200,mean={key:float(np.mean([v[key] for v in draws])) for key in draws[0]},
                                         delta_resampling_range=[min(v['label_condition_difference'] for v in draws),max(v['label_condition_difference'] for v in draws)])
        blocks.append(block)
    gate=missing==0 and eligibility(blocks)
    supported=[b for b in blocks if b['correct_response_supported']]
    primary=block_statistics([b['jaccard']['label_condition_difference'] for b in supported]) if gate else dict(status='not_estimable_support_gate')
    result=dict(state='complete' if missing==0 else 'incomplete',primary=primary,retrieval_gate=gate,
                requested=160,archived=160-missing,valid=sum(r['status']=='ok' for r in audits),
                observed_top_label_n=sum(r['correct'] is not None for r in audits),correct_top_label_n=sum(r['correct'] is True for r in audits),
                supported_blocks=len(supported),support_by_theme=dict(Counter(b['theme'] for b in supported)),
                blocks=blocks,audits=audits,freeze_sha256=digest(design.OUT/'freeze.json'),
                caveat='Purposively selected date-choice blocks; conditional on all eight answers correct. No causal or broad-history claim.')
    csv_write(out/'graph_audit.csv',audits);csv_write(out/'block_results.csv',blocks);csv_write(out/'sensitivities.csv',sens)
    csv_write(design.OUT/'checksums.csv',[dict(path=p,sha256=h) for p,h in sorted(hashes.items())])
    atomic_json(out/'results.json',json_ready(result))
    plot(result,out)
    lines=['# Final history study','',f'Graphs archived: {160-missing}/160. Complete correct-response blocks: {len(supported)}/20. Primary support gate: {gate}.','',
           'The independent unit is an event-pair block. Missing or unsupported comparisons are not zero. This is a separate prospective task, not repaired inclusion in the original cohort.','',
           '```json',json.dumps(primary,indent=2),'```','',
           '| Event pair | Correct labels among valid graphs | Valid graphs | Included in correct-response analysis | Same-label minus changed-label contrast |',
           '|---|---:|---:|---|---:|']
    for b in blocks:lines.append(f'| {b["block"]} | {b.get("correct_n","unavailable")} | {b["valid_graphs"]}/8 | {b["correct_response_supported"]} | {b.get("jaccard",{}).get("label_condition_difference","unavailable")} |')
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return result


def plot(result,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    fig,ax=plt.subplots(figsize=(9,7));rows=[]
    colors={'documents':'#0072B2','space':'#CC651D'}
    for i,b in enumerate(result['blocks']):
        value=b.get('jaccard',{}).get('label_condition_difference')
        if value is None:ax.text(0,i,'unavailable',va='center',fontsize=8)
        else:ax.scatter(value,i,color=colors[b['theme']],marker='o' if b['correct_response_supported'] else 'x')
        rows.append(dict(block=b['block'],theme=b['theme'],supported=b['correct_response_supported'],value=value))
    ax.axvline(0,color='gray',ls='--');ax.set_yticks(range(20),[b['block'].replace('_',' ') for b in result['blocks']]);ax.invert_yaxis()
    ax.set_xlabel('Same-label minus changed-label same-event advantage (Jaccard)')
    ax.set_title('History follow-up: does changing the answer label reduce similarity?')
    ax.legend(handles=[Line2D([],[],color=c,marker='o',ls='',label=k) for k,c in colors.items()]+[Line2D([],[],color='gray',marker='x',ls='',label='Not all eight answers correct')],loc='best')
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(out/f'history_contrasts.{ext}',dpi=180)
    plt.close(fig);csv_write(out/'history_figure_source.csv',rows)


if __name__=='__main__':analyze()
