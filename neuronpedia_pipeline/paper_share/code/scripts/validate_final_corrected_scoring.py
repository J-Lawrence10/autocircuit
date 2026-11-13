"""Check corrected final data, every dependent display, and manuscript consistency."""
import importlib.util
import json
from pathlib import Path
import re
import shutil
import numpy as np

from finalize_corrected_scoring import ROOT, OUT, CORRECTION, RECOVERY, PRIMARY, read
from complete_qwen4_controls import digest, read_csv
from control_io import atomic_json
from run_matched_choice_controls import now
from whole_graph_analysis import jaccard
from exploratory_confound_checks import features
from analyze_answer_spelling import accepts

FIG=OUT/'paper_figures'


def main():
    result=read(OUT/'results.json'); correction=read(CORRECTION/'results.json')
    execution=read(OUT/'execution_record.json')
    for path,sha in {**execution['source_hashes'],**execution['raw_graph_hashes']}.items():
        assert digest(ROOT/path)==sha,path
    spec=importlib.util.spec_from_file_location('final_package_verifier',ROOT/'paper_share/code/verify_package.py')
    verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    rows=lambda name:read_csv(FIG/'tables'/name)
    verifier.verify_corrected_tables(rows,result,correction)
    q17=read(ROOT/'data/model_extension/qwen17_completion_20261106/analysis/results.json')
    q17_audit=read(ROOT/'data/model_extension/qwen17_completion_20261106/figure_audit/results.json')
    verifier.verify_current_tables(rows,q17,q17_audit)
    final=result['controlled']
    included=[r for r in final['per_fact'] if r['split']=='held_out']
    jobs={(r['fact_id'],r['role']):r for r in read(RECOVERY/'analysis/combined_jobs.json') if r['design']=='controlled'}
    sets={}
    for r in included:
        for role in ['target','positive_paraphrase']:
            job=jobs[(r['pair_id'],role)]
            graph=read(ROOT/job['raw_graph_path'])
            sets[(r['pair_id'],role)]=features(graph['nodes'])
    pairs=read_csv(OUT/'lexical_pairs.csv')
    assert len(pairs)==54 and sum(r['same_fact']=='False' for r in pairs)==42
    for row in pairs:
        actual=jaccard(sets[(row['target_fact'],'target')],sets[(row['candidate_fact'],'positive_paraphrase')])
        assert np.isclose(actual,float(row['feature_jaccard']),rtol=0,atol=1e-12)
    inventory=read_csv(CORRECTION/'answer_inventory.csv')
    registry=read(ROOT/'config/answer_spelling_aliases_20261111.json')
    assert len(inventory)==170
    assert sum(accepts(r['fact'],r['expected'],r['observed'],registry) and r['strict_match']=='False' for r in inventory)==1
    assert result['answers']['statuses']['whole_answer_next_token']==50
    for folder,name in [(FIG,'figure_manifest.json'),(OUT/'claims','manifest.json')]:
        manifest=read(folder/name)
        for path,sha in manifest['source_hashes'].items():
            assert digest(ROOT/path)==sha,path
        for path,sha in manifest['output_hashes'].items():
            assert digest(folder/path)==sha,path
    text=(ROOT/'docs/papers/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md').read_text(encoding='utf-8')
    for phrase in ['0.218 for Qwen3-4B ([0.150, 0.307], n=12)',
                   '0/12 Qwen3-4B', '108 directed other-fact comparisons',
                   '30 model-specific fact observations',
                   '| Qwen3-4B | 0.218 | 0.181 [0.110, 0.267] | 0.072 | 12/12 |']:
        assert phrase in text,phrase
    for phrase in ['0.162','0.126 [0.084, 0.168]','exact-match reference',
                   'accepted-spelling sensitivity','separate sensitivity','106 directed other-fact']:
        assert phrase not in text,phrase
    assert len(re.findall(r'!\[Figure (?:S?\d+):',text))==16
    assert '\u2014' not in text
    summary=dict(passed=True,checked_at=now(),no_hosted_requests=True,
        original_raw_graphs_unchanged=True,raw_graphs_hash_verified=147,
        raw_jaccard_comparisons_independently_recomputed=54,
        final_fact_counts=[8,10,12],primary_qwen4_mean=final['heldout_primary']['mean'],
        qwen4_output_type_matched_control_n=10,qwen4_complete_answer_n=50,
        corrected_current_figures_and_text=True,comparison_history_archived=True,
        verifier_sha256=digest(Path(__file__)))
    atomic_json(OUT/'validation.json',summary)
    snapshot=OUT/'code_snapshot';snapshot.mkdir(exist_ok=True)
    for path in [Path(__file__),ROOT/'scripts/finalize_corrected_scoring.py',ROOT/'scripts/build_final_corrected_figures.py',
                 ROOT/'scripts/figure_plain_language.py',ROOT/'scripts/plot_methods_workflow.py',
                 ROOT/'scripts/build_paper_claims_map.py',ROOT/'scripts/build_paper_share_package.py',
                 ROOT/'paper_share/code/verify_package.py']:
        shutil.copy2(path,snapshot/path.name)
    atomic_json(OUT/'artifact_manifest.json',dict(files=[dict(path=p.relative_to(OUT).as_posix(),sha256=digest(p),bytes=p.stat().st_size)
        for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json' and '__pycache__' not in p.parts]))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
