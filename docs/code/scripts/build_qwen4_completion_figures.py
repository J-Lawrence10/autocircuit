"""Reconcile current displays with two recovered graphs, preserving older figures.

Saved-data only. Reuse the frozen exact-token rule and archived tokenizer audit;
do not add accepted answers, tests, or inference calls. Primary figures retain
the same included facts and numerical estimates.
"""
import csv
import json
from pathlib import Path

from tokenizers import Tokenizer

import build_outline_figures_v2 as figures
import exploratory_confound_checks as exploratory
from complete_qwen4_controls import ROOT, OUT as RECOVERY, digest
from control_io import atomic_json

OUT = ROOT / 'data/model_extension/paper_figures_qwen4_complete_20261110'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def display_audit():
    verification = read(RECOVERY/'analysis/verification.json')
    assert verification['primary_margins_unchanged'] and verification['heldout_facts'] == 10
    assert verification['complete_controlled_graphs'] == 120
    directory = exploratory.OUT/'tokenizers/qwen3-4b'
    provenance = read(directory/'provenance.json')
    assert provenance['status'] == 'ok'
    for name, sha in provenance['file_hashes'].items():
        assert digest(directory/name) == sha, name
    tokenizer = Tokenizer.from_file(str(directory/'tokenizer.json'))
    folder = RECOVERY/'graphs/columbus_americas__positive_paraphrase'
    raw = read(folder/'raw_graph.json')
    recorded = read(folder/'audit.json')
    assert digest(folder/'raw_graph.json') == recorded['raw_sha256']
    graph = dict(prompt=raw['metadata']['prompt'], prompt_tokens=raw['metadata']['prompt_tokens'],
                 expected=recorded['expected'], **exploratory.logit_record(raw['nodes']))
    new_answer = dict(job_id='columbus_americas__positive_paraphrase', **graph,
                      **exploratory.answer_check(graph, tokenizer))
    assert new_answer['prompt_pieces_match'] and new_answer['logit_decode_matches']
    assert new_answer['answer_status'] == 'next_token_mismatch'
    assert new_answer['top_text'].strip() == 'María' and new_answer['expected'] == 'Maria'
    old = read(exploratory.OUT/'results.json')
    answer = next(r for r in old['answers'] if r['model'] == 'qwen3-4b' and r['design'] == 'controlled')
    statuses = dict(answer['statuses'])
    assert statuses.pop('missing_graph') == 1
    statuses[new_answer['answer_status']] += 1
    assert sum(statuses.values()) == 60
    assert statuses == {'whole_answer_next_token': 49, 'multi_token_prefix_only': 5, 'next_token_mismatch': 6}
    result = dict(answers=dict(statuses=statuses, available_factual_graph_n=60),
                  recovered_answer=new_answer, tokenizer_provenance=provenance,
                  note='One exact-text mismatch is the accented spelling María, not evidence of an incorrect historical answer.',
                  source_hashes={str(p.relative_to(ROOT)): digest(p) for p in [
                      RECOVERY/'analysis/verification.json', folder/'raw_graph.json',
                      exploratory.OUT/'results.json', directory/'provenance.json',
                      directory/'tokenizer.json', Path(exploratory.__file__)]})
    atomic_json(RECOVERY/'analysis/display_audit.json', result)
    return result


def inclusion_rows(original):
    analysis = read(RECOVERY/'analysis/model_extension_results.json')['controlled']
    audits = read(RECOVERY/'analysis/graph_audit.json')
    included = {r['pair_id'] for r in analysis['per_fact']}
    excluded = {r['pair_id']: r for r in analysis['excluded_pairs']}
    no_comparator = set(analysis['pairs_without_same_domain_split_comparator'])
    output = []
    for row in original:
        item = dict(row)
        if item['model'] != 'Qwen3-4B*':
            output.append(item)
            continue
        rows = [r for r in audits if r['design'] == 'controlled' and r['pair_id'] == item['pair_id']]
        assert len(rows) == 4 and all(r['status'] == 'ok' for r in rows)
        decision = excluded.get(item['pair_id'], {})
        reason = decision.get('reason', 'no_same_subject_test_comparator' if item['pair_id'] in no_comparator else 'included')
        item.update(model='Qwen3-4B', available_graphs='4', included=str(item['pair_id'] in included),
                    reason=reason, observed_mismatched_tokens=json.dumps(decision.get('observed_top_tokens', {}), sort_keys=True))
        assert item['included'] == row['included'], 'Recovered graphs unexpectedly changed included facts.'
        if item['pair_id'] != 'columbus_americas':
            assert item['reason'] == row['reason']
            assert json.loads(item['observed_mismatched_tokens']) == json.loads(row['observed_mismatched_tokens'])
        output.append(item)
    return output


def completed_caption(text):
    stale = [
        ' *The Qwen3-4B collection contains 145/147 planned graphs.',
        ' *The Qwen3-4B collection is incomplete (145/147 graphs).',
        ' *Qwen3-4B remains incomplete (145/147 graphs).',
        ' *The Qwen3-4B collection is incomplete.',
    ]
    for sentence in stale:
        text = text.replace(sentence, '')
    return text


def main():
    display = display_audit()
    figures.OUT = OUT
    figures.REVISION = '2026-11-10'
    figures.base.EXTENSION = RECOVERY
    figures.base.LABELS[-1] = figures.updated_plots.LABELS[-1] = 'Qwen3-4B'
    figures.CAPTIONS = {key: completed_caption(value) for key, value in figures.CAPTIONS.items()}
    caption = figures.CAPTIONS['figureS5_answer_audit']
    caption = caption.replace('49, five, and five, respectively, among 59', '49, five, and six, respectively, among 60')
    caption = caption.replace('Qwen3-4B is missing one factual graph and one invented name control graph.',
                              'One Qwen3-4B exact-text mismatch is María rather than Maria, an accented spelling variant rather than evidence of a wrong historical answer.')
    figures.CAPTIONS['figureS5_answer_audit'] = caption
    current_class = figures.updated_plots.CurrentFigures
    figures.updated_plots.CurrentFigures = lambda source, table: current_class(source, table, qwen4_completion=display)
    current_rows = figures.accounting.current_rows
    figures.accounting.current_rows = lambda root: inclusion_rows(current_rows(root))
    gallery = figures.gallery

    def current_gallery(supplements, history):
        gallery(supplements, history)
        # Only current presentation files are edited; earlier figure sets remain intact.
        for path in [OUT/'LEGENDS.md', OUT/'index.html', ROOT/'docs/writing/FIGURE_HEADLINES_AND_LEGENDS.md']:
            text = path.read_text(encoding='utf-8')
            text = text.replace('7 November 2026', '10 November 2026')
            text = text.replace('An asterisk on Qwen3-4B marks the incomplete original collection (145/147 graphs), not the separate completed follow-ups.',
                                'Qwen3-4B now has all 147 planned question/control and fact/wording graphs. Its ten included evaluation facts and overlap estimates are unchanged.')
            text = text.replace('No evaluation graphs were requested, so no history graph-overlap effect was measured.',
                                'The planned 160 evaluation graphs were not requested. The separate 16-graph historical-date analysis is shown as Figure 7 in the paper sharing package.')
            text = text.replace('There is no new historical graph-overlap estimate, not a measured zero effect.',
                                'See Figure 7 in the paper sharing package for the separate 16-graph analysis.')
            text = text.replace('scripts/build_outline_figures_v2.py', 'scripts/build_qwen4_completion_figures.py')
            path.write_text(text, encoding='utf-8')
        figures.source(RECOVERY/'analysis/display_audit.json')
        figures.source(RECOVERY/'analysis/verification.json')
        figures.source(Path(__file__))

    figures.gallery = current_gallery
    figures.main()
    # Verify unchanged point estimates, not merely rounded summaries.
    with (OUT/'tables/figure2_summary.csv').open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    qwen = next(r for r in rows if r['model'] == 'Qwen3-4B')
    primary = read(RECOVERY/'analysis/verification.json')['current_primary']
    assert float(qwen['mean']) == primary['mean'] and int(qwen['n']) == primary['n']
    print('Completed Qwen3-4B collection: display counts updated; primary estimates unchanged.')


if __name__ == '__main__':
    main()
