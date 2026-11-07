"""Retrospective saved-data audits supporting updated Qwen1.7B figure panels.

No network/model calls, no primary reanalysis, no changed eligibility. Writes only
under the dated completion's figure_audit/ directory. Original and expanded
cohorts overlap and must never be presented as independent models or samples.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch

import numpy as np
from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exploratory_confound_checks as exploratory
import whole_graph_analysis as whole
from audit_qwen17_completion import REL_OUT, digest, inside, read_csv, read_json
from complete_qwen17_controls import MODEL
from control_io import atomic_json

ROOT = Path(__file__).resolve().parents[1]
REL_AUDIT = REL_OUT/'figure_audit'
REL_ANALYSIS = REL_OUT/'analysis'
REL_OLD = Path('data/model_extension/exploratory_20260905')
REL_TOKENIZER = REL_OLD/'tokenizers'/MODEL
COHORTS = {'original50': 'original50_reconstructed', 'expanded91': 'expanded91_late_observational'}
FIELDS_QUALITY = ('ambiguous_node_id_count', 'ambiguous_incident_edge_count',
    'dangling_edge_count', 'duplicate_exact_edge_count', 'duplicate_endpoint_edge_count',
    'nonfinite_edge_count', 'error_influence_fraction', 'error_incident_edge_weight_fraction')
STATUS_LABELS = {
    'whole_answer_next_token': 'Whole expected answer in the next token',
    'multi_token_prefix_only': 'Compatible beginning; complete answer unverified',
    'whitespace_only_compatible': 'Compatible whitespace; complete answer unverified',
    'next_token_mismatch': 'Next token differs from the expected answer',
    'unresolved_tokenizer_validation': 'Tokenizer validation unresolved',
    'unresolved_token_boundary': 'Token boundary unresolved',
    'tokenizer_unavailable': 'Tokenizer unavailable',
}


def save(path, value):
    atomic_json(path, whole.json_ready(value))


def specification(root):
    inputs = [REL_ANALYSIS/'results.json', REL_ANALYSIS/'analysis_plan.json',
        REL_ANALYSIS/'representation_cache_index.json',
        REL_OUT/'audit/collection_verification.json', REL_OUT/'freeze.json',
        Path('data/publication_analysis/raw_graph_audit.json'),
        REL_OLD/'results.json', REL_OLD/'lexical_per_fact.csv',
        REL_OLD/'pairwise_lexical_and_size.csv', REL_OLD/'answer_audit.csv',
        REL_TOKENIZER/'provenance.json', REL_TOKENIZER/'tokenizer.json',
        REL_TOKENIZER/'tokenizer_config.json',
        Path('scripts/audit_qwen17_completion_figures.py'),
        Path('scripts/exploratory_confound_checks.py'), Path('scripts/whole_graph_analysis.py')]
    return dict(schema_version='qwen17-figure-audit-plan-v1',
        status='Retrospective exploratory display audit, specified before these new lexical/tokenizer calculations, after primary completion outcomes were known.',
        cohorts=dict(original50='The unchanged 50 original exports; five included evaluation facts.',
                     expanded91='The same 50 original exports plus 41 late exports; ten included evaluation facts.'),
        additional_quality_subset='Late41 only, as collection-date diagnostics, not an independent model or effect replication.',
        quality_definition='Reuse frozen whole_graph_analysis raw audits. Error burden = absolute reconstruction-error node influence / absolute nonterminal node influence; not causal output fraction.',
        lexical_definition='Reuse exploratory_confound_checks pair_table and lexical_checks unchanged; case-folded alphanumeric word-set Jaccard without stopword removal; same-domain evaluation comparators.',
        lexical_rules=['at_least_own_overlap', 'word_caliper_0.05', 'word_and_size_caliper'],
        lexical_size_caliper='Absolute log(candidate feature count / own rewording count) <= log(1.25), together with word-overlap caliper 0.05.',
        answer_definition='Reuse archived hash-verified Qwen tokenizer and answer_check. Check all available factual starting/reworded graphs, not invented-name controls and not just eligible evaluation facts.',
        expected_factual_denominators=dict(original50=30, expanded91=50),
        archived_reconciliation='Original raw quality50; original lexical15 rule rows /25 candidate pairs /5 evaluation facts; original factual token audit30.',
        no_eligibility_changes=True, no_primary_effect_recomputation=True,
        display_cautions=['Expanded91 contains original50; not a fourth model or independent replication.',
            'Unavailable lexical matches and absent history estimates are not zero effects.',
            'A compatible answer prefix is not verification of the completed answer.',
            'Tokenizer validation does not recover the exact historical hosted checkpoint revision.',
            'Other-model and crossed-design panels stay explicitly in their original cohorts.'],
        input_sha256={str(p).replace('\\', '/'): digest(inside(root, p)) for p in inputs})


def ensure_plan(root):
    out = inside(root, REL_AUDIT)
    out.mkdir(parents=True, exist_ok=True)
    path = out/'analysis_plan.json'
    spec = specification(root)
    if path.exists():
        if read_json(path)['specification'] != spec:
            raise RuntimeError('Figure audit plan/input/helper changed; explicit new version required')
    else:
        save(path, dict(recorded_at=datetime.now(timezone.utc).isoformat(), specification=spec))
    return digest(path)


def selected_rows(rows, cohort):
    return [r for r in rows if cohort == 'expanded91' or r['collection'] == 'original']


def quality_summary(rows):
    percentages = [100*float(r['error_influence_fraction']) for r in rows]
    bad = sum(r['ambiguous_node_id_count'] > 0 for r in rows)
    return dict(graph_n=len(rows), ambiguous_export_n=bad,
        ambiguous_export_rate_percent=100*bad/len(rows) if rows else None,
        error_influence_percent_values=percentages,
        error_influence_median_percent=float(np.median(percentages)) if percentages else None,
        graph_counts_with_flags={key: sum(bool(r[key]) for r in rows) for key in FIELDS_QUALITY if 'fraction' not in key},
        definition='Absolute reconstruction-error node influence divided by absolute nonterminal node influence. No causal fraction or model-ranking interpretation.')


def validate_old_quality(quality, archived):
    lookup = {(r['pair_id'], r['role']): r for r in archived if r.get('model_dir') == 'qwen3-1-7b'}
    if len(quality) != 50 or len(lookup) != 50:
        raise RuntimeError('Original quality audit must contain50 graphs')
    for row in quality:
        old = lookup[(row['pair_id'], row['role'])]
        if row['sha256'] != old['sha256']:
            raise RuntimeError('Original raw quality hash differs from archived audit')
        for key in FIELDS_QUALITY:
            a, b = row[key], old[key]
            if a != b and not (isinstance(a, (float, int)) and isinstance(b, (float, int))
                              and math.isclose(a, b, abs_tol=1e-12, rel_tol=0)):
                raise RuntimeError(f'Original quality value changed: {row["pair_id"]}/{row["role"]}/{key}')
    return len(quality)


def load_offline_tokenizer(root):
    directory = inside(root, REL_TOKENIZER)
    provenance = read_json(directory/'provenance.json')
    if provenance.get('status') != 'ok':
        raise RuntimeError('Archived offline tokenizer unavailable; do not download')
    for name, expected in provenance['file_hashes'].items():
        if digest(directory/name) != expected:
            raise RuntimeError('Archived tokenizer checksum changed')
    return Tokenizer.from_file(str(directory/'tokenizer.json')), provenance


def input_graphs(root, saved):
    """Load only factual raw graphs; frozen feature caches supply lexical comparisons."""
    cache_index = read_json(inside(root, REL_ANALYSIS/'representation_cache_index.json'))
    graphs, answers, provenance = [], [], []
    tokenizer, tokenizer_provenance = load_offline_tokenizer(root)
    factual = [r for r in saved['provenance'] if r['job']['role'] in {'target', 'positive_paraphrase'}]
    if len(factual) != 50:
        raise RuntimeError('Expected50 available factual prompt graphs')
    for index, item in enumerate(factual, 1):
        job, raw_sha = item['job'], item['raw_sha256']
        raw_path = inside(root, item['path'])
        if digest(raw_path) != raw_sha:
            raise RuntimeError('Raw graph changed since frozen completion analysis')
        cache_info = cache_index[raw_sha]
        cache_path = inside(root, cache_info['path'])
        if digest(cache_path) != cache_info['cache_sha256']:
            raise RuntimeError('Frozen feature cache checksum mismatch')
        cache = read_json(cache_path)
        if cache['raw_sha256'] != raw_sha or cache['job'] != job:
            raise RuntimeError('Feature cache provenance mismatch')
        raw = read_json(raw_path)
        metadata = raw['metadata']
        graph = dict(model=MODEL, design='controlled', status='ok', fact=job['pair_id'],
            role=job['role'], domain=job['domain'], split=job['split'], expected=job['expected_token'],
            manifest_prompt=job['prompt'], prompt=metadata['prompt'], prompt_tokens=metadata.get('prompt_tokens'),
            features={tuple(v) for v in cache['representation']['features']},
            collection=item['collection'], raw_path=str(raw_path.relative_to(root)), raw_sha256=raw_sha,
            **exploratory.logit_record(raw['nodes']))
        if graph['top_text'] != cache['representation']['top_token']:
            raise RuntimeError('Raw top token differs from frozen representation')
        answer = {k: graph[k] for k in ('model', 'design', 'status', 'fact', 'role', 'domain', 'split',
            'expected', 'prompt', 'top_id', 'top_text', 'collection', 'raw_path', 'raw_sha256')}
        answer.update(exploratory.answer_check(graph, tokenizer))
        graphs.append(graph)
        answers.append(answer)
        provenance.append(dict(raw_path=str(raw_path.relative_to(root)), raw_sha256=raw_sha,
            cache_path=str(cache_path.relative_to(root)), cache_sha256=cache_info['cache_sha256']))
        del raw
        print(f'[{index}/50] offline token/feature audit {job["pair_id"]}/{job["role"]}', flush=True)
    return graphs, answers, tokenizer_provenance, provenance


def validate_old_answers(rows, archived):
    old = {(r['fact'], r['role']): r for r in archived if r['model'] == MODEL and
           r['design'] == 'controlled' and r['role'] in {'target', 'positive_paraphrase'}}
    if len(rows) != 30 or len(old) != 30:
        raise RuntimeError('Original factual answer audit must contain30 graphs')
    for row in rows:
        before = old[(row['fact'], row['role'])]
        for key in ('answer_status', 'top_text'):
            if row[key] != before[key]:
                raise RuntimeError(f'Original token audit changed: {row["fact"]}/{row["role"]}/{key}')
        if row['top_id'] != int(before['top_id']) or row['strict_string_match'] != (before['strict_string_match'] == 'True'):
            raise RuntimeError('Original top-token ID or strict answer match changed')
    return len(rows)


def lexical_for_cohort(graphs, saved_cohort):
    with patch.object(exploratory, 'MODELS', [MODEL]):
        pairs, eligible = exploratory.pair_table(graphs, {MODEL: saved_cohort})
        per_fact, summaries = exploratory.lexical_checks(pairs)
    scatter = []
    for fact in sorted({r['target_fact'] for r in pairs}):
        candidates = [r for r in pairs if r['target_fact'] == fact]
        own = next(r for r in candidates if r['same_fact'])
        others = [r for r in candidates if not r['same_fact']]
        scatter.append(dict(fact=fact, domain=own['domain'], own_word_overlap=own['word_jaccard'],
            best_other_word_overlap=max(r['word_jaccard'] for r in others),
            other_fact_candidates=len(others),
            own_expected_answer_matches=own['same_expected_answer'],
            other_fact_same_expected_answer_n=sum(r['same_expected_answer'] for r in others)))
    summary = dict(eligible_evaluation_n=len(eligible[MODEL]), summaries=summaries, scatter=scatter,
        min_own_minus_best_other_word_overlap=min(r['own_word_overlap']-r['best_other_word_overlap'] for r in scatter) if scatter else None,
        max_own_minus_best_other_word_overlap=max(r['own_word_overlap']-r['best_other_word_overlap'] for r in scatter) if scatter else None,
        own_pairs_same_expected_answer_n=sum(r['same_fact'] and r['same_expected_answer'] for r in pairs),
        other_fact_pairs_same_expected_answer_n=sum(not r['same_fact'] and r['same_expected_answer'] for r in pairs),
        other_fact_pair_n=sum(not r['same_fact'] for r in pairs),
        note='Matching support is not an adjusted causal/semantic effect. No matching comparators means non-estimable, not zero.')
    return pairs, per_fact, summary


def validate_old_lexical(pairs, rows, archived_pairs, archived_rows):
    old_pairs = {(r['target_fact'], r['candidate_fact']): r for r in archived_pairs if r['model'] == MODEL}
    old_rows = {(r['fact'], r['rule']): r for r in archived_rows if r['model'] == MODEL}
    if len(pairs) != 25 or len(old_pairs) != 25 or len(rows) != 15 or len(old_rows) != 15:
        raise RuntimeError('Original lexical audit denominator changed')
    for row in pairs:
        before = old_pairs[(row['target_fact'], row['candidate_fact'])]
        for field in ('feature_jaccard', 'word_jaccard', 'target_n', 'candidate_n', 'own_n'):
            if not math.isclose(float(row[field]), float(before[field]), abs_tol=1e-12, rel_tol=0):
                raise RuntimeError('Original pairwise lexical/feature value changed')
    for row in rows:
        before = old_rows[(row['fact'], row['rule'])]
        if row['comparator_n'] != int(before['comparator_n']) or row['comparator_facts'] != json.loads(before['comparator_facts']):
            raise RuntimeError('Original lexical matching support changed')
        if not math.isclose(row['own_word_overlap'], float(before['own_word_overlap']), abs_tol=1e-12, rel_tol=0):
            raise RuntimeError('Original own-rewording word overlap changed')
    return dict(evaluation_facts=5, pairwise_rows=25, rule_rows=15)


def answer_summary(rows):
    counts = dict(Counter(r['answer_status'] for r in rows))
    return dict(available_factual_graph_n=len(rows), strict_matches=sum(r['strict_string_match'] for r in rows),
        statuses=counts, status_labels=STATUS_LABELS,
        tokenizer_prompt_validation_pass_n=sum(r.get('prompt_pieces_match') is True for r in rows),
        tokenizer_logit_validation_pass_n=sum(r.get('logit_decode_matches') is True for r in rows),
        by_domain={domain: dict(available_factual_graph_n=sum(r['domain'] == domain for r in rows),
            statuses=dict(Counter(r['answer_status'] for r in rows if r['domain'] == domain)))
            for domain in ('chemistry', 'geography', 'history')},
        denominator_note='All available starting and reworded factual prompts, development and evaluation. Not raw graph total, not independent facts, and not the eligible evaluation sample.')


def run(root=ROOT):
    root = Path(root).resolve()
    plan_sha = ensure_plan(root)  # Saved before any new lexical/tokenizer calculations.
    saved = read_json(inside(root, REL_ANALYSIS/'results.json'))
    if saved.get('status') != 'completed' or saved.get('original_reconstruction', {}).get('passed') is not True:
        raise RuntimeError('Validated completed analysis required')
    analysis_spec = read_json(inside(root, REL_ANALYSIS/'analysis_plan.json'))['specification']
    for name in ('scripts/whole_graph_analysis.py', 'scripts/exploratory_confound_checks.py'):
        if digest(inside(root, name)) != analysis_spec['method_sha256'][name]:
            raise RuntimeError('Analysis helper changed since frozen primary analysis')
    quality_rows = saved['graph_audits']
    if len(quality_rows) != 91:
        raise RuntimeError('Expected91 frozen raw-graph audit rows')
    quality_reconciled = validate_old_quality(selected_rows(quality_rows, 'original50'),
                                             read_json(root/'data/publication_analysis/raw_graph_audit.json'))
    graphs, answer_rows, tokenizer_provenance, raw_provenance = input_graphs(root, saved)
    answer_reconciled = validate_old_answers(selected_rows(answer_rows, 'original50'), read_csv(root/REL_OLD/'answer_audit.csv'))
    cohorts, pair_rows, lexical_rows, scatter_rows, combined_answers, combined_quality = {}, [], [], [], [], []
    lexical_reconciled = None
    for cohort, result_key in COHORTS.items():
        gs, answers, qs = [selected_rows(rows, cohort) for rows in (graphs, answer_rows, quality_rows)]
        pairs, lexical, lex_summary = lexical_for_cohort(gs, saved['cohorts'][result_key])
        if cohort == 'original50':
            lexical_reconciled = validate_old_lexical(pairs, lexical, read_csv(root/REL_OLD/'pairwise_lexical_and_size.csv'),
                                                      read_csv(root/REL_OLD/'lexical_per_fact.csv'))
        cohorts[cohort] = dict(source_analysis_cohort=result_key, quality=quality_summary(qs),
                               lexical=lex_summary, answers=answer_summary(answers))
        pair_rows.extend(dict(r, cohort=cohort) for r in pairs)
        lexical_rows.extend(dict(r, cohort=cohort) for r in lexical)
        scatter_rows.extend(dict(r, cohort=cohort) for r in lex_summary['scatter'])
        combined_answers.extend(dict(r, cohort=cohort) for r in answers)
        combined_quality.extend(dict(cohort=cohort, job_id=r['job_id'], pair_id=r['pair_id'],
            role=r['role'], domain=r['domain'], split=r['split'], collection=r['collection'],
            raw_sha256=r['raw_sha256'], error_influence_percent=100*r['error_influence_fraction'],
            **{key: r[key] for key in FIELDS_QUALITY}) for r in qs)
    result = dict(schema_version='qwen17-completion-figure-audit-v1', status='completed', retrospective_exploratory=True,
        generated_at=datetime.now(timezone.utc).isoformat(), analysis_plan_sha256=plan_sha,
        source_analysis_sha256=digest(inside(root, REL_ANALYSIS/'results.json')), model=MODEL,
        original_reconciliation=dict(passed=True, quality_graphs=quality_reconciled,
            factual_answer_graphs=answer_reconciled, **lexical_reconciled),
        cohorts=cohorts, late41_quality=quality_summary([r for r in quality_rows if r['collection'] == 'late_completion']),
        no_hosted_requests=True, primary_statistics_changed=False, eligibility_changed=False,
        tokenizer_provenance=tokenizer_provenance, raw_provenance=raw_provenance,
        reused_frozen_results=dict(path=str(REL_ANALYSIS/'results.json'), keys=['cohorts', 'equal_count_sensitivity', 'eligibility', 'collection_by_domain'],
            note='Primary/control/robustness/equal-count estimates are not rerun or changed here.'),
        interpretation=['Original50 and expanded91 overlap; do not count as a fourth model or independent replication.',
            'No changes to scientific inclusion rules, original findings, primary statistics, or frozen source files.',
            'This retrospective audit tests display consistency and available comparator/answer support, not causal mechanisms.',
            'History estimates remain unavailable; token classifications among partial history collection do not create eligible four-role fact sets.'])
    out = inside(root, REL_AUDIT)
    for name, rows in [('quality_graphs', combined_quality), ('lexical_pairs', pair_rows),
                       ('lexical_per_fact', lexical_rows), ('lexical_scatter', scatter_rows), ('answer_audit', combined_answers)]:
        whole.write_csv(out/(name+'.csv'), rows)
    save(out/'results.json', result)
    save(out/'output_checksums.json', {p.name: digest(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != 'output_checksums.json'})
    print(json.dumps(whole.json_ready(dict(original_reconciliation=result['original_reconciliation'],
        cohorts={key: dict(quality=dict(graph_n=value['quality']['graph_n'], ambiguous_export_n=value['quality']['ambiguous_export_n'],
            error_influence_median_percent=value['quality']['error_influence_median_percent']),
            lexical=value['lexical']['summaries'], answers=value['answers']) for key, value in cohorts.items()})), indent=2), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args()
    if args.plan_only:
        print(ensure_plan(ROOT))
    else:
        run()


if __name__ == '__main__':
    main()
