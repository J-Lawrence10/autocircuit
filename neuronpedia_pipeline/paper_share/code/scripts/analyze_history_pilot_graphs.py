"""Analyze all authorized history graphs; correctness never gates inclusion."""
from __future__ import annotations

from collections import Counter, defaultdict
import contextlib
import hashlib
import io
import itertools
import json
from pathlib import Path
import re

import numpy as np

import run_history_pilot_graphs as design
from run_matched_choice_controls import clean_prompt, now
from control_io import atomic_json
from convert_model_extension import load_converter, raw_integrity, converted_integrity
from whole_graph_analysis import summarize_graph, jaccard, sparse_cosine, finite_number, json_ready
from analyze_matched_choice_controls import matrix_for, contrasts, csv_write
from audit_paper_closeout import representations, VARIANTS

OUT, MODEL, ROOT = design.OUT, design.MODEL, design.ROOT
BLOCK_NAMES = {'pilot_documents': 'Declaration of Independence / Treaty of Paris',
               'pilot_space': 'Sputnik 1 / Explorer 1'}


def selected_year(job, letter, jobs):
    if letter not in ('A', 'B'):
        return None
    years = {j['fact']: j['year'] for j in jobs if j['block'] == job['block']}
    fact = job['mapping'] if letter == 'A' else 1 - job['mapping']
    return years[fact]


def raw_prediction(graph):
    logits = [n for n in graph.get('nodes', []) if n.get('feature_type') == 'logit']
    values = []
    for node in logits:
        token = node.get('token')
        if token is None:
            match = re.search(r'(?:Output|Logit)\s+"([\s\S]*?)"\s+\(p=', node.get('clerp', ''))
            token = match.group(1) if match else None
        probability = finite_number(node.get('token_prob'))
        if token is not None and probability is not None:
            values.append((probability, str(token).strip()))
    if not values:
        return None, None
    maximum = max(v[0] for v in values)
    winners = {token for probability, token in values if probability == maximum}
    if len(winners) != 1:
        return None, maximum
    return next(iter(winners)), maximum


def analyze_graph(job, jobs, converter):
    folder = OUT / MODEL / 'graphs' / job['job_id']
    raw, converted = folder / 'raw_graph.json', folder / 'converted_graph.json'
    row = {k: job[k] for k in ('job_id', 'block', 'theme', 'fact', 'mapping', 'wording', 'event', 'year', 'expected_label')}
    row.update(status='missing', preview_answer=job['preview_answer'], preview_correct=job['preview_answer'] == job['expected_label'],
               observed=None, correct=None, prediction_changed=None, graph_eligible=False)
    if not raw.exists():
        return row, None
    try:
        row['raw_sha256'] = design.digest(raw)
        saved = json.loads((folder / 'metadata.json').read_text())
        if row['raw_sha256'] != saved['sha256']:
            raise ValueError('Raw checksum mismatch')
        graph = json.loads(raw.read_text(encoding='utf-8'))
        meta = graph.get('metadata', {})
        if meta.get('scan', meta.get('model')) != MODEL or clean_prompt(meta.get('prompt', '')) != job['prompt']:
            raise ValueError('Prompt or model mismatch')
        # Behavior remains reportable even when graph identities subsequently fail an integrity check.
        observed, probability = raw_prediction(graph)
        row.update(observed=observed, observed_probability=probability,
                   correct=(observed == job['expected_label']) if observed is not None else None,
                   prediction_changed=(observed != job['preview_answer']) if observed is not None else None,
                   predicted_year=selected_year(job, observed, jobs),
                   preview_year=selected_year(job, job['preview_answer'], jobs))
        row.update(raw_integrity(graph))
        row['prompt_tokens'] = meta.get('prompt_tokens', [])
        row['tokens_match_preview'] = row['prompt_tokens'] == job['preview_tokens']
        if not row['tokens_match_preview']:
            raise ValueError('Prompt token sequence differs from archived preview')
        if meta.get('info', {}).get('transcoder_set') != 'mwhanna/qwen3-4b-transcoders':
            raise ValueError('Transcoder provenance mismatch')
        settings, pruning = meta.get('generation_settings', {}), meta.get('pruning_settings', {})
        if not np.isclose(meta.get('node_threshold', -1), .8) or not np.isclose(pruning.get('edge_threshold', -1), .85):
            raise ValueError('Graph threshold mismatch')
        if settings.get('max_n_logits') != 10 or not np.isclose(settings.get('desired_logit_prob', -1), .99):
            raise ValueError('Logit settings mismatch')
        if settings.get('max_feature_nodes') != 5000 or saved.get('settings') != design.SETTINGS:
            raise ValueError('Generation settings mismatch')
        keys = ['raw_missing_node_id_count', 'raw_ambiguous_node_id_count', 'raw_orphan_edge_count', 'raw_duplicate_endpoint_edge_count']
        if any(row[k] for k in keys):
            raise ValueError('Raw identifier or edge-integrity failure')
        if any(finite_number(e.get('weight')) is None for e in graph.get('links', graph.get('edges', []))):
            raise ValueError('Nonfinite edge weight')
        if not converted.exists():
            with contextlib.redirect_stdout(io.StringIO()):
                converter(str(raw), str(converted), prompt=None, model_id=MODEL, ambiguous_node_policy='error')
        cg = json.loads(converted.read_text(encoding='utf-8'))
        ci = converted_integrity(cg)
        row.update(ci, converted_sha256=design.digest(converted))
        if any(ci[k] for k in ['converted_missing_node_id_count', 'converted_duplicate_node_id_count',
                              'converted_orphan_edge_count', 'converted_duplicate_endpoint_edge_count']):
            raise ValueError('Converted identity or edge-integrity failure')
        ca, rep = summarize_graph(cg, path=converted, file_sha256=row['converted_sha256'])
        if observed is None or str(rep['top_token']).strip() != observed:
            raise ValueError('Missing or inconsistent top prediction')
        if not rep['features']:
            raise ValueError('No eligible feature identities')
        if any(ca[k] for k in ['missing_node_ids', 'ambiguous_node_id_count', 'dangling_edge_count', 'nonfinite_edge_count']):
            raise ValueError('Converted summary integrity failure')
        if any(not isinstance(n.get('ctx_idx'), int) or not 0 <= n['ctx_idx'] < len(row['prompt_tokens']) for n in cg['nodes']):
            raise ValueError('Invalid node token position')
        variants, variant_info = representations(cg)
        row.update(status='ok', graph_eligible=True, feature_count=len(rep['features']),
                   error_influence_fraction=ca['error_influence_fraction'],
                   error_incident_edge_weight_fraction=ca['error_incident_edge_weight_fraction'],
                   correct_logit_available=job['expected_label'] in [str(n.get('token', '')).strip() for n in cg['nodes'] if n.get('node_type') == 'logit'],
                   exported_predictions=cg['metadata'].get('top_predictions', []),
                   variant_info=variant_info)
        return row, variants
    except Exception as error:
        row.update(status='invalid', error=str(error))
        return row, None


def pair_rows(jobs, audits, reps):
    rows = []
    for block in design.BLOCKS:
        group = [j for j in jobs if j['block'] == block]
        for a, b in itertools.combinations(group, 2):
            aid, bid = a['job_id'], b['job_id']
            ar, br = audits[aid], audits[bid]
            row = dict(block=block, a=aid, b=bid, same_event=a['fact'] == b['fact'],
                       same_required_letter=a['expected_label'] == b['expected_label'],
                       same_mapping=a['mapping'] == b['mapping'], same_order=a['wording'] == b['wording'],
                       correct_a=ar['correct'], correct_b=br['correct'], observed_a=ar['observed'], observed_b=br['observed'])
            available_outputs = ar['observed'] in ('A', 'B') and br['observed'] in ('A', 'B')
            row['same_predicted_letter'] = ar['observed'] == br['observed'] if available_outputs else None
            row['same_predicted_year'] = ar.get('predicted_year') == br.get('predicted_year') if available_outputs else None
            row['order_only'] = row['same_event'] and row['same_mapping'] and not row['same_order']
            row['mapping_only'] = row['same_event'] and row['same_order'] and not row['same_mapping']
            row['event_only'] = not row['same_event'] and row['same_order'] and row['same_mapping']
            if aid in reps and bid in reps:
                av, bv = reps[aid]['full'], reps[bid]['full']
                row.update(status='ok', jaccard=jaccard(av['features'], bv['features']),
                           weighted_cosine=sparse_cosine(av['feature_weights'], bv['feature_weights']))
            else:
                row.update(status='unavailable_graph', jaccard=None, weighted_cosine=None)
            rows.append(row)
    return rows


def stratified(rows):
    fields = ('same_event', 'same_required_letter', 'same_predicted_letter', 'same_order')
    result = []
    for block in design.BLOCKS:
        for values in itertools.product((False, True), repeat=4):
            group = [r for r in rows if r['block'] == block and all(r[k] == v for k, v in zip(fields, values))]
            valid = [r for r in group if r['status'] == 'ok']
            row = dict(block=block, **dict(zip(fields, values)), total_pairs=len(group), valid_pairs=len(valid))
            for metric in ('jaccard', 'weighted_cosine'):
                row[metric] = float(np.mean([r[metric] for r in valid])) if valid else None
            result.append(row)
    return result


def marginal_summaries(rows):
    """Descriptive group sizes and means, not adjusted or independent effects."""
    result = []
    for block in design.BLOCKS:
        for subset in ('all_pairs', 'cross_order'):
            candidates = [r for r in rows if r['block'] == block and (subset == 'all_pairs' or not r['same_order'])]
            for factor in ('same_event', 'same_required_letter', 'same_predicted_letter', 'same_predicted_year', 'same_order'):
                for value in (False, True):
                    group = [r for r in candidates if r[factor] is value]
                    valid = [r for r in group if r['status'] == 'ok']
                    row = dict(block=block, subset=subset, factor=factor, matched=value,
                               total_pairs=len(group), valid_pairs=len(valid))
                    for metric in ('jaccard', 'weighted_cosine'):
                        row[metric] = float(np.mean([r[metric] for r in valid])) if valid else None
                    result.append(row)
    return result


def cross_order(job_group, reps, metric):
    cells = {(j['fact'], j['expected_label'], j['wording']): reps[j['job_id']] for j in job_group}
    result = contrasts(matrix_for(cells, metric))
    result['same_event_difference_change'] = result['fact_same_label'] - result['fact_different_label']
    return result


def block_analysis(jobs, audits, reps):
    rows, sampling = [], []
    for block in design.BLOCKS:
        group = [j for j in jobs if j['block'] == block]
        counts = dict(block=block, available_graphs=sum(j['job_id'] in reps for j in group))
        bags = [Counter(audits[j['job_id']].get('prompt_tokens', [])) for j in group]
        balanced = bool(bags[0]) and all(b == bags[0] for b in bags)
        counts['matched_token_inventories'] = balanced
        if counts['available_graphs'] != 8 or not balanced:
            rows.append(dict(**counts, status='incomplete_or_token_mismatch'))
            continue
        for variant in VARIANTS:
            vr = {j['job_id']: reps[j['job_id']][variant] for j in group}
            for metric in ('jaccard', 'weighted_cosine'):
                if not all(r['features'] for r in vr.values()):
                    rows.append(dict(**counts, variant=variant, metric=metric, status='empty_representation'))
                    continue
                rows.append(dict(**counts, variant=variant, metric=metric, status='ok',
                                 **cross_order(group, vr, metric)))
        arrays = {j['job_id']: sorted(reps[j['job_id']]['full']['features']) for j in group}
        k = min(map(len, arrays.values()))
        for size_name, size in [('K', k), ('K_half', k // 2)]:
            seed = design.SEED + int(hashlib.sha256(f'{block}/{size_name}'.encode()).hexdigest()[:8], 16)
            rng = np.random.default_rng(seed)
            if size == 0:
                continue
            for repetition in range(200):
                sampled = {key: {'features': {a[i] for i in rng.choice(len(a), size=size, replace=False)}} for key, a in arrays.items()}
                sampling.append(dict(block=block, sample_size_name=size_name, k=size, seed=seed,
                                     repetition=repetition, **cross_order(group, sampled, 'jaccard')))
    return rows, sampling


def sampling_summary(samples):
    groups = defaultdict(list)
    for row in samples:
        groups[row['block'], row['sample_size_name']].append(row)
    result = []
    metrics = ('SS', 'SD', 'DS', 'DD', 'fact_effect', 'fact_same_label', 'fact_different_label',
               'label_effect', 'same_event_difference_change')
    for (block, name), rows in sorted(groups.items()):
        row = dict(block=block, sample_size_name=name, k=rows[0]['k'], repetitions=len(rows))
        for metric in metrics:
            values = [r[metric] for r in rows]
            row[metric] = float(np.mean(values))
            row[metric + '_positive_repetitions'] = sum(v > 0 for v in values)
            row[metric + '_range'] = [min(values), max(values)]
        result.append(row)
    return result


def summary(jobs, audits, pairs, blocks):
    result = []
    for block in design.BLOCKS:
        group = [audits[j['job_id']] for j in jobs if j['block'] == block]
        order = [r for r in pairs if r['block'] == block and r['order_only']]
        mapping = [r for r in pairs if r['block'] == block and r['mapping_only']]
        row = dict(block=block, planned=8, observed=sum(r['observed'] is not None for r in group),
                   correct=sum(r['correct'] is True for r in group),
                   wrong=sum(r['correct'] is False for r in group),
                   valid_graphs=sum(r['graph_eligible'] for r in group),
                   preview_matches=sum(r['prediction_changed'] is False for r in group),
                   order_pairs_with_outputs=sum(r['same_predicted_letter'] is not None for r in order),
                   order_answer_changes=sum(r['same_predicted_letter'] is False for r in order),
                   mapping_pairs_with_outputs=sum(r['same_predicted_year'] is not None for r in mapping),
                   mapping_selected_year_changes=sum(r['same_predicted_year'] is False for r in mapping))
        full = next((r for r in blocks if r['block'] == block and r.get('variant') == 'full' and r.get('metric') == 'jaccard'), None)
        if full and full['status'] == 'ok':
            row['cross_order_jaccard'] = {k: full[k] for k in ('SS', 'SD', 'DS', 'DD', 'fact_same_label', 'fact_different_label', 'label_effect', 'same_event_difference_change')}
        result.append(row)
    return result


def report(result):
    rows = result['block_summaries']
    lines = ['# History graph results including incorrect answers', '',
             f'{result["raw_graphs"]}/16 raw graphs archived; {result["valid_graphs"]}/16 passed the graph-analysis checks. '
             f'The newly collected predictions were correct for {result["correct"]}/{result["observed"]} observed responses. '
             f'{result["preview_matches"]}/{result["observed"]} matched the saved preview predictions.', '',
             '## Predictions and prompt changes', '',
             '| Event pair | Correct | Wrong | Preview matches | Answer changes after reversing order | Selected-date changes after swapping A/B mapping |',
             '|---|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f'| {BLOCK_NAMES[r["block"]]} | {r["correct"]}/{r["observed"]} | {r["wrong"]} | {r["preview_matches"]}/{r["observed"]} | '
                     f'{r["order_answer_changes"]}/{r["order_pairs_with_outputs"]} | {r["mapping_selected_year_changes"]}/{r["mapping_pairs_with_outputs"]} |')
    lines += ['', 'The order comparisons retain the queried event and answer mapping. The mapping comparisons retain the event and question order, but swap which date A and B represent.', '',
              '## Feature overlap across question orders', '',
              'Each entry is mean Jaccard overlap across four comparisons within the event pair. Same or different letter refers here to the required answer, not necessarily the predicted answer.', '',
              '| Event pair | Same event, same required letter | Different event, same required letter | Same event, different required letter | Different event, different required letter |',
              '|---|---:|---:|---:|---:|']
    for r in rows:
        c = r.get('cross_order_jaccard')
        if c:
            lines.append(f'| {BLOCK_NAMES[r["block"]]} | {c["SS"]:.4f} | {c["DS"]:.4f} | {c["SD"]:.4f} | {c["DD"]:.4f} |')
        else:
            lines.append(f'| {BLOCK_NAMES[r["block"]]} | Unavailable | Unavailable | Unavailable | Unavailable |')
    lines += ['', '## Overlap grouped by the answer actually predicted', '',
              'These cross-order groups include correct and incorrect predictions. Counts refer to graph pairs, not independent questions.', '',
              '| Event pair | Same predicted letter: mean overlap (pairs) | Different predicted letter: mean overlap (pairs) |',
              '|---|---:|---:|']
    for block in design.BLOCKS:
        groups = [r for r in result['marginal_summaries'] if r['block'] == block and r['subset'] == 'cross_order' and r['factor'] == 'same_predicted_letter']
        cells = {}
        for r in groups:
            cells[r['matched']] = f'{r["jaccard"]:.4f} ({r["valid_pairs"]})' if r['jaccard'] is not None else 'Unavailable (0)'
        lines.append(f'| {BLOCK_NAMES[block]} | {cells[True]} | {cells[False]} |')
    lines += ['', '## Equal feature counts', '',
              'Values below average 200 subsampling repetitions. The two columns compare same-event overlap with other-event overlap within each required-letter condition. K is the smallest feature set in that event pair; K/2 uses half that many features. Sampling repetitions are not additional questions.', '',
              '| Event pair | Features per graph | Same-event difference, same required letter | Same-event difference, different required letter | Difference between these two contrasts |',
              '|---|---:|---:|---:|---:|']
    for r in result['sampling_summary']:
        lines.append(f'| {BLOCK_NAMES[r["block"]]} | {r["sample_size_name"]}: {r["k"]} | {r["fact_same_label"]:.4f} | '
                     f'{r["fact_different_label"]:.4f} | {r["same_event_difference_change"]:.4f} |')
    lines += ['', '## Figures', '',
              '![Feature overlap for all history prompts](../figures/history_all_graph_overlap.png)', '',
              '![Comparisons after changes in order or answer mapping](../figures/history_prompt_change_comparisons.png)', '',
              '[Figure legends](../figures/LEGENDS.md)', '', '## Saved analyses', '',
              '- `graph_audit.csv`: all expected, preview, and observed predictions, correctness, and integrity results.',
              '- `all_pairs.csv`: all 56 within-pair graph comparisons, including incorrect answers.',
              '- `order_pairs.csv` and `mapping_pairs.csv`: the eight matched comparisons for each prompt change.',
              '- `stratified_overlap.csv`: overlap grouped by queried event, required letter, predicted letter, and order, with empty groups retained.',
              '- `marginal_overlap.csv`: descriptive means and counts for each matching factor separately, not adjusted effects.',
              '- `block_contrasts.csv`: cross-order contrasts, weighted-cosine results, and graph-location sensitivities.',
              '- `equal_count_samples.csv`: all 200 repetitions at each of two feature counts per event pair.',
              '- `equal_count_summary.csv`: means and repetition ranges for the feature-count sensitivities.',
              '- `results.json`: complete machine-readable results and provenance.', '',
              'Scope: these are descriptive comparisons of two fixed event pairs. All incorrect responses are retained. The original history stopping rule and geography results are unchanged.', '']
    (OUT / 'analysis' / 'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    frozen, jobs = design.prepare()
    converter = load_converter()
    audits, reps = {}, {}
    for job in jobs:
        row, variants = analyze_graph(job, jobs, converter)
        audits[job['job_id']] = row
        if variants is not None:
            reps[job['job_id']] = variants
        print(f'{job["job_id"]}: {row["status"]}; predicted={row["observed"]}; correct={row["correct"]}', flush=True)
    pairs = pair_rows(jobs, audits, reps)
    blocks, sampling = block_analysis(jobs, audits, reps)
    sampling_means = sampling_summary(sampling)
    grouped = stratified(pairs)
    marginal = marginal_summaries(pairs)
    summaries = summary(jobs, audits, pairs, blocks)
    result = dict(model=MODEL, planned=16, raw_graphs=sum('raw_sha256' in r for r in audits.values()),
                  valid_graphs=len(reps), observed=sum(r['observed'] is not None for r in audits.values()),
                  correct=sum(r['correct'] is True for r in audits.values()),
                  wrong=sum(r['correct'] is False for r in audits.values()),
                  preview_matches=sum(r['prediction_changed'] is False for r in audits.values()),
                  status='complete' if len(reps) == 16 else 'partial',
                  audits=list(audits.values()), block_summaries=summaries, block_contrasts=blocks,
                  pairs=pairs, stratified=grouped, marginal_summaries=marginal, sampling_summary=sampling_means, analysis_time=now(),
                  freeze_sha256=design.digest(OUT / 'freeze.json'), analysis_sha256=design.digest(__file__),
                  analysis_scope='Two event pairs; descriptive effect sizes; wrong answers retained; no population p-values.')
    analysis = OUT / 'analysis'
    atomic_json(analysis / 'results.json', json_ready(result))
    for name, rows in [('graph_audit', list(audits.values())), ('all_pairs', pairs), ('block_contrasts', blocks),
                       ('stratified_overlap', grouped), ('marginal_overlap', marginal), ('block_summaries', summaries),
                       ('equal_count_samples', sampling), ('equal_count_summary', sampling_means),
                       ('order_pairs', [r for r in pairs if r['order_only']]), ('mapping_pairs', [r for r in pairs if r['mapping_only']])]:
        csv_write(analysis / f'{name}.csv', rows)
    report(result)
    atomic_json(analysis / 'representation_manifest.json', {
        key: {variant: {'features': sorted(value['features']),
                        'feature_weights': [[list(k), v] for k, v in sorted(value['feature_weights'].items())]}
              for variant, value in variants.items()} for key, variants in reps.items()})
    return result


if __name__ == '__main__':
    main()
