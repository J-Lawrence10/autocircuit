"""Assemble one final analysis with corrected accepted-answer scoring.

Saved data only. Preserve previous scoring results as audit inputs, never as a
second current cohort. Recalculate dependent lexical and equal-count summaries.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import json
import numpy as np

from analyze_answer_spelling import ROOT, OUT as CORRECTION, PRIMARY, read
from analyze_model_extension import write_csv
from complete_qwen4_controls import OUT as RECOVERY, digest, read_csv
from control_io import atomic_json
import exploratory_confound_checks as exploratory
from run_matched_choice_controls import now
from whole_graph_analysis import jaccard, json_ready

OUT = ROOT/'data/model_extension/final_corrected_scoring_20261111'
PREVIOUS = CORRECTION/'paper_figures_v1'
MODEL = 'qwen3-4b'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = [CORRECTION/'results.json', CORRECTION/'plan.json',
               CORRECTION/'equal_count_repetitions.csv', CORRECTION/'answer_inventory.csv',
               CORRECTION/'eligibility_comparison.csv', RECOVERY/'analysis/combined_jobs.json',
               ROOT/'scripts/exploratory_confound_checks.py', Path(__file__)]
    fingerprints = {p.relative_to(ROOT).as_posix(): digest(p) for p in sources}
    frozen = read(CORRECTION/'plan.json')
    for path, sha in {**frozen['inputs'], **frozen['raw_graph_hashes'], **frozen['converted_graph_hashes']}.items():
        assert digest(ROOT/path) == sha, path
    correction = read(CORRECTION/'results.json')
    result = deepcopy(correction['accepted_spelling'])
    selected = [r for r in result['per_fact'] if r['split'] == 'held_out']
    assert Counter(r['domain'] for r in selected) == {'chemistry': 5, 'geography': 5, 'history': 2}
    jobs = [r for r in read(RECOVERY/'analysis/combined_jobs.json') if r['design']=='controlled']
    lookup = {(r['fact_id'], r['role']): r for r in jobs}
    sets = {}
    for row in selected:
        for role in ['target', 'positive_paraphrase']:
            job = lookup[(row['pair_id'], role)]
            sets[(row['pair_id'], role)] = exploratory.features(read(ROOT/job['raw_graph_path'])['nodes'])
    pairs = []
    for row in selected:
        fact = row['pair_id']
        target, own = lookup[(fact, 'target')], lookup[(fact, 'positive_paraphrase')]
        for other in selected:
            if row['domain'] != other['domain']:
                continue
            candidate = lookup[(other['pair_id'], 'positive_paraphrase')]
            pairs.append(dict(model=MODEL, domain=row['domain'], target_fact=fact,
                candidate_fact=other['pair_id'], same_fact=fact==other['pair_id'],
                feature_jaccard=jaccard(sets[(fact,'target')], sets[(other['pair_id'],'positive_paraphrase')]),
                word_jaccard=jaccard(exploratory.words(target['prompt']), exploratory.words(candidate['prompt'])),
                target_n=len(sets[(fact,'target')]), candidate_n=len(sets[(other['pair_id'],'positive_paraphrase')]),
                own_n=len(sets[(fact,'positive_paraphrase')]),
                same_expected_answer=target['expected_token']==candidate['expected_token']))
        local = [p for p in pairs if p['target_fact']==fact]
        own_overlap = next(p['feature_jaccard'] for p in local if p['same_fact'])
        other_overlap = np.mean([p['feature_jaccard'] for p in local if not p['same_fact']])
        assert np.isclose(own_overlap-other_overlap, row[PRIMARY], rtol=0, atol=1e-12)
    lexical_rows, summaries = exploratory.lexical_checks(pairs)
    summaries = [r for r in summaries if r['model']==MODEL]
    scatter = []
    for row in selected:
        local = [p for p in pairs if p['target_fact']==row['pair_id']]
        own = next(p for p in local if p['same_fact'])
        best = max(p['word_jaccard'] for p in local if not p['same_fact'])
        scatter.append(dict(fact=row['pair_id'], domain=row['domain'],
                            own_word_overlap=own['word_jaccard'], best_other_word_overlap=best,
                            word_overlap_gap=own['word_jaccard']-best))
    # Use all twelve corrected per-fact estimates from the completed 200-repeat
    # feature-sampling run, including unchanged chemistry/geography membership.
    equal_rows = [dict(model=MODEL, fact=r['fact'], domain=r['domain'], fraction=r['fraction'],
                       runs=r['repetitions'], mean_margin=r['mean'], resampling_sd=r['sd'])
                  for r in correction['equal_count']['per_fact']]
    repetitions = read_csv(CORRECTION/'equal_count_repetitions.csv')
    equal_summary = []
    for fraction in [1.0, .5]:
        means = [r['mean_margin'] for r in equal_rows if r['fraction']==fraction]
        pooled = [np.mean([float(r['margin']) for r in repetitions
                          if float(r['fraction'])==fraction and int(r['repetition'])==rep]) for rep in range(200)]
        equal_summary.append(dict(model=MODEL, fraction=fraction, **exploratory.brief(means),
            resampling_mean_range=[float(min(pooled)), float(max(pooled))],
            resampling_95pct_range=list(map(float, np.quantile(pooled,[.025,.975])))))
    # One current inclusion table, with rejected partial answers still rejected.
    inclusion = read_csv(PREVIOUS/'tables/test_fact_inclusion_audit.csv')
    corrected_eligibility = {r['fact']: r for r in read_csv(CORRECTION/'eligibility_comparison.csv')
                             if r['rule']=='accepted_spelling' and r['split']=='held_out'}
    for row in inclusion:
        if row['model']=='Qwen3-4B':
            decision = corrected_eligibility[row['pair_id']]
            row['included'], row['reason'] = decision['included'], decision['reason']
            if row['included']=='True':
                row['observed_mismatched_tokens'] = '{}'
    assert Counter(r['model'] for r in inclusion if r['included']=='True') == {'Gemma-2-2B':8,'Qwen3-1.7B':10,'Qwen3-4B':12}
    audit_counts = read(RECOVERY/'analysis/display_audit.json')['answers']
    audit_counts = deepcopy(audit_counts)
    audit_counts['statuses']['whole_answer_next_token'] += 1
    audit_counts['statuses']['next_token_mismatch'] -= 1
    assert audit_counts['statuses'] == {'whole_answer_next_token':50,'multi_token_prefix_only':5,'next_token_mismatch':5}
    final = dict(status='completed', presentation='one final corrected cohort per model',
        model=MODEL, controlled=result, lexical=dict(per_fact=lexical_rows, summaries=summaries, scatter=scatter,
        other_fact_pair_n=sum(not p['same_fact'] for p in pairs),
        same_answer_other_fact_n=sum(p['same_expected_answer'] for p in pairs if not p['same_fact']),
        min_word_overlap_gap=min(r['word_overlap_gap'] for r in scatter)),
        equal_count=dict(rows=equal_rows, summaries=equal_summary, groups=correction['equal_count']['groups']),
        answers=audit_counts, history_comparisons=correction['history_comparisons'],
        no_hosted_requests=True, original_inputs_unchanged=True,
        scoring_correction=dict(accepted_spellings=['Maria','María'], fact='columbus_americas',
            classification_changes=1, outputs_checked=170,
            audit_status='Correction identified after collection; original scoring and gates retained in the audit archive, not presented as a second final sample.'))
    atomic_json(OUT/'results.json', json_ready(final))
    for name, rows in [('controlled_per_fact',result['per_fact']),('lexical_pairs',pairs),
                       ('lexical_per_fact',lexical_rows),('lexical_summary',summaries),
                       ('lexical_scatter',scatter),('equal_count_per_fact',equal_rows),
                       ('equal_count_summary',equal_summary),('test_fact_inclusion_audit',inclusion)]:
        write_csv(OUT/f'{name}.csv', rows)
    for path, sha in fingerprints.items():
        assert digest(ROOT/path)==sha
    atomic_json(OUT/'execution_record.json', dict(finished_at=now(), no_hosted_requests=True,
        raw_graphs_hash_verified=147, converted_graphs_hash_verified=147,
        raw_feature_overlaps_recomputed=len(pairs), source_hashes=fingerprints,
        raw_graph_hashes=frozen['raw_graph_hashes']))
    print(json.dumps(json_ready(dict(primary=result['heldout_primary'], equal_count=equal_summary,
        lexical=final['lexical'], answer_counts=audit_counts)), indent=2))


if __name__=='__main__':
    main()
