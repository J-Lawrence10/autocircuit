"""Synthetic, no-network tests for late-completion representation and analysis."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import analyze_qwen17_completion as late


def representation(features, fact, role, domain='chemistry', split='held_out', correct=True):
    features = {('lorsa', 1, i) for i in features}
    return dict(features=features, features_with_errors=features|{('error:mlp', 1, -1)},
        feature_weights={f: 1.0 for f in features},
        feature_weights_with_errors={**{f: 1.0 for f in features}, ('error:mlp', 1, -1): .2},
        layer_profile={1: 1.0}, edge_flow={(1, 2): 1.0},
        eligible_feature_node_count=len(features), eligible_edge_count=1,
        error_influence_fraction=.1, error_incident_edge_weight_fraction=.1,
        top_token='Paris', top_token_class='alphabetic', sensitivity_only=False,
        ambiguous_node_ids_dropped=[], pair_id=fact, role=role, domain=domain, split=split,
        top_token_matches_expected=correct)


def cohort(n=3, domain='chemistry'):
    result = {}
    for i in range(n):
        fact = f'{domain}_{i}'
        for role in late.whole.REQUIRED_ROLES:
            values = [0, 10+i] if role in ('target', 'positive_paraphrase') else [50+i, 100+i]
            result[(fact, role)] = representation(values, fact, role, domain)
    return result


class LateAnalysisTests(unittest.TestCase):
    def test_raw_logit_extraction_matches_converter_order_and_multiline(self):
        graph = dict(nodes=[dict(feature_type='logit', node_id='a', token_prob=.1, token=' wrong'),
                            dict(feature_type='logit', node_id='b', token_prob=.8,
                                 clerp='Logit "\nParis" (p=0.8)'),
                            dict(feature_type='lorsa', node_id='c')], metadata={'prompt': 'p'})
        enriched = late.with_raw_predictions(graph)
        self.assertEqual(enriched['metadata']['model_output'], '\nParis')
        self.assertNotIn('model_output', graph['metadata'])
        self.assertEqual(enriched['metadata']['top_predictions'][0]['node_id'], 'b')

    def test_representation_cache_roundtrip_preserves_namespaces_and_numbers(self):
        rep = representation([1, 2], 'f', 'target')
        rep['features'].add(('transcoder', 1, 1))
        packed = json.loads(json.dumps(late.pack_representation(rep)))
        unpacked = late.unpack_representation(packed)
        self.assertEqual(unpacked, rep)

    def test_raw_converted_parity_detects_changed_feature_namespace(self):
        raw = representation([1], 'f', 'target')
        late.compare_representations(raw, copy.deepcopy(raw))
        changed = copy.deepcopy(raw)
        changed['features'] = {('transcoder', 1, 1)}
        with self.assertRaisesRegex(RuntimeError, 'identity mismatch'):
            late.compare_representations(raw, changed)

    def test_exact_method_memoization_changes_neither_margins_nor_null(self):
        reps = cohort(3)
        with patch.object(late, 'BOOTSTRAPS', 20):
            memoized = late.bounded_controlled_analysis(reps)
            direct = late.whole.analyze_controlled(reps, bootstrap_runs=20, seed=late.SEED)
        self.assertEqual(memoized['per_fact'], direct['per_fact'])
        self.assertEqual(memoized['heldout_primary'], direct['heldout_primary'])
        self.assertEqual(memoized['robustness']['exact_fact_label_permutation'], direct['robustness']['exact_fact_label_permutation'])
        self.assertNotIn('gate_b_confirmatory_fact_identity_pass', memoized)
        self.assertIn('not a new confirmatory', memoized['interpretation'])

    def test_correctness_allroles_and_same_domain_split_rules_remain(self):
        reps = cohort(3)
        reps.update(cohort(2, 'geography'))
        reps[('chemistry_0', 'target')]['top_token_matches_expected'] = False
        del reps[('geography_0', 'negative_nonce')]
        with patch.object(late, 'BOOTSTRAPS', 10):
            result = late.bounded_controlled_analysis(reps)
        self.assertEqual(result['analyzable_pair_ids'], ['chemistry_1', 'chemistry_2'])
        self.assertIn('geography_1', result['pairs_without_same_domain_split_comparator'])
        self.assertTrue(all(row['other_factual_comparator_n'] == 1 for row in result['per_fact']))
        reasons = {r['pair_id']: r['reason'] for r in result['excluded_pairs']}
        self.assertEqual(reasons['chemistry_0'], 'expected_token_not_top_prediction')
        self.assertEqual(reasons['geography_0'], 'incomplete_roles')

    def test_unrepresented_facts_are_kept_in_eligibility_audit(self):
        jobs = [dict(pair_id=fact, role=role, domain='history', split='held_out', prompt=fact, expected_token='x')
                for fact in ('absent', 'partial') for role in late.whole.REQUIRED_ROLES]
        reps = {('partial', 'target'): representation([1], 'partial', 'target', domain='history')}
        result = dict(complete_pair_ids=[], analyzable_pair_ids=[])
        rows = late.eligibility_table(jobs, reps, result, 'expanded91_late_observational', {})
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows[0]['missing_roles']), 4)
        self.assertTrue(all(r['exclusion_reason'] == 'incomplete_roles' for r in rows))

    def test_original_reconstruction_rejects_changed_numeric_results(self):
        row = dict(pair_id='f', feature_jaccard__margin_other_factual_mean=.0854227,
                   feature_influence_cosine__margin_other_factual_mean=.2)
        result = dict(per_fact=[row], heldout_primary=dict(n=5, mean=.0854227))
        archived = {'models': {'qwen': copy.deepcopy(result)}}
        self.assertTrue(late.reconstruct_original(result, archived)['passed'])
        archived['models']['qwen']['per_fact'][0]['feature_jaccard__margin_other_factual_mean'] += 1e-9
        with self.assertRaisesRegex(RuntimeError, 'reconstructed values differ'):
            late.reconstruct_original(result, archived)

    def test_fixed_plan_is_written_before_preflight_or_graph_reads(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = {'synthetic': True}
            with patch.object(late, 'plan_spec', return_value=spec), \
                 patch.object(late, 'preflight', side_effect=RuntimeError('synthetic stop')):
                with self.assertRaisesRegex(RuntimeError, 'synthetic stop'):
                    late.run(root)
            path = root/late.REL_OUT/'analysis/analysis_plan.json'
            self.assertEqual(json.loads(path.read_text())['specification'], spec)

    def test_changed_plan_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(late, 'plan_spec', return_value={'seed': 1}):
                late.ensure_plan(root)
            with patch.object(late, 'plan_spec', return_value={'seed': 2}):
                with self.assertRaisesRegex(RuntimeError, 'versioned amendment'):
                    late.ensure_plan(root)

    def test_exact_permutation_bound_fails_before_analysis(self):
        with patch.object(late, 'MAX_LABEL_PERMUTATIONS', 1):
            with self.assertRaisesRegex(RuntimeError, 'fixed design bound'):
                late.bounded_controlled_analysis(cohort(3))


if __name__ == '__main__':
    unittest.main()
