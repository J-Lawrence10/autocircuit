"""CPU-only fresh-environment verification; no remote model requests or frozen-output writes."""
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/model_extension/final_closeout_20261005/reproduction'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cfg=Path(sys.prefix)/'pyvenv.cfg'
    if sys.prefix==sys.base_prefix or not cfg.exists() or 'include-system-site-packages = false' not in cfg.read_text():
        raise RuntimeError('Run in a fresh isolated virtual environment, without system site packages')
    commands=[]
    for name,args in [('environment',['-m','pip','freeze']),('dependency_check',['-m','pip','check']),('tests',['-m','pytest','tests','-q'])]:
        run=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True)
        (OUT/f'{name}.log').write_text(run.stdout+'\n'+run.stderr,encoding='utf-8')
        commands.append(dict(name=name,command=[sys.executable,*args],returncode=run.returncode))
        if run.returncode:raise RuntimeError(f'{name} failed; inspect {OUT/name}')
    import audit_paper_closeout as audit
    baseline=json.loads((audit.OUT/'statistics_audit.json').read_text())
    audit.OUT=OUT/'audit';audit.main()
    reproduced=json.loads((audit.OUT/'statistics_audit.json').read_text())
    if baseline!=reproduced:raise AssertionError('Fresh-environment audit differs from baseline')
    # Re-read original raw features into a new cache and reconstruct all 23 original margins.
    # No tokenizer download, graph request, or primary eligibility change.
    import exploratory_confound_checks as old
    old.OUT=OUT/'original_reconstruction';old.OUT.mkdir(parents=True,exist_ok=True)
    specs=old.inventory()
    for row in specs:
        if row['sha256'] and audit.digest(old.local_path(row['path']))!=row['sha256']:
            raise AssertionError('Original raw hash changed')
    graphs=old.load_graphs(specs);saved=old.primary_results()
    pairs,eligible=old.pair_table(graphs,saved)
    counts={m:len(rows) for m,rows in eligible.items()}
    if sum(counts.values())!=23:raise AssertionError('Original primary sample changed')
    old.write_csv('pairwise_reconstruction',pairs)
    result=dict(status='passed',python=sys.version,executable=sys.executable,isolated=True,commands=commands,
                closeout_audit_exact_match=True,original_margins_reconstructed=counts,
                planned_graph_records=len(specs),available_raw_n=sum(bool(r['sha256']) for r in specs),original_source_hashes=old.SOURCES,
                limitations=['Same machine and interpreter; not independent human or hosted-model replication.',
                             'Reconstructs original margins and closeout contrasts, not every historical estimator or all stochastic sensitivities.'])
    (OUT/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='original_source_hashes'},indent=2))


if __name__=='__main__':main()
