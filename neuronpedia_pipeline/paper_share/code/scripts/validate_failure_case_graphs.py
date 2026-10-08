"""Validate completed artifacts, provenance and numerical denominator identities."""
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from failure_case_design import ROOT,OUT,MODEL,digest,make_jobs
from control_io import atomic_json


def main():
    results=json.loads((OUT/'analysis/results.json').read_text());jobs=make_jobs();errors=[]
    if len(results['audits'])!=16 or len(results['comparisons'])!=8:errors.append('Unexpected audit/comparison count')
    freeze=json.loads((OUT/'freeze.json').read_text())
    for p,sha in freeze['code_hashes'].items():
        if digest(ROOT/p)!=sha:errors.append('Code/protocol hash mismatch: '+p)
    if results['freeze_sha256']!=digest(OUT/'freeze.json'):errors.append('Analysis freeze mismatch')
    for row in results['audits']:
        folder=OUT/MODEL/'graphs'/row['job_id']
        raw=folder/'raw_graph.json'
        if not raw.exists():errors.append('Missing raw: '+row['job_id']);continue
        if digest(raw)!=row.get('raw_sha256'):errors.append('Raw hash mismatch: '+row['job_id'])
        if row['status']!='ok':continue
        if digest(folder/'converted_graph.json')!=row['converted_sha256']:errors.append('Converted hash mismatch: '+row['job_id'])
        vals=[r['fraction'] for r in row['source_role_totals'] if r['fraction'] is not None]
        if vals and abs(sum(vals)-1)>1e-9:errors.append('Source fractions do not sum to one: '+row['job_id'])
    figures=list((OUT/'figures').glob('*.png'))
    if len(figures)!=10:errors.append('Expected ten PNG figures including all eight neighborhoods')
    if not (OUT/'FINDINGS.md').exists():errors.append('Missing findings memo')
    record=dict(passed=not errors,errors=errors,graphs_received=sum((OUT/MODEL/'graphs'/j['job_id']/'raw_graph.json').exists() for j in jobs),
                valid_graphs=results['valid_graphs'],clean_graphs=results['clean_graphs'],
                clean_comparisons=results['clean_comparisons'],note='Artifact validation is not scientific or causal validation.')
    atomic_json(OUT/'validation.json',record)
    files=[p for p in OUT.rglob('*') if p.is_file() and p.suffix in ['.json','.csv','.png','.svg','.md','.py']
           and p.name not in ['artifact_manifest.json','status.json']]
    atomic_json(OUT/'artifact_manifest.json',{str(p.relative_to(OUT)):digest(p) for p in files})
    if errors:raise RuntimeError('; '.join(errors))
    print(json.dumps(record,indent=2));return record


if __name__=='__main__':main()
