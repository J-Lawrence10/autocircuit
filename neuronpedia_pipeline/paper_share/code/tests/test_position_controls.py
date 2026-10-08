from collections import Counter
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from scripts.matched_choice_position_controls import make_jobs, validate_design
from scripts.analyze_position_controls import position_contrasts
from scripts.run_position_controls import pilot_gate
from scripts.control_io import atomic_json, replace_with_retry
from scripts.analyze_matched_choice_controls import fact_assignment_null


class PositionControlsTests(unittest.TestCase):
    def test_factorial_design_and_token_bags(self):
        jobs=make_jobs();validation=validate_design(jobs)
        self.assertEqual(len(validation),7)
        self.assertEqual(sum(j['split']=='held_out' for j in jobs),96)
        for j in jobs:
            self.assertEqual(j['country_list'][j['position']],j['queried_country'])
            self.assertEqual(j['expected_label'],'A' if j['fact']==j['mapping'] else 'B')

    def synthetic(self,feature):
        return {(f,l,p,w):{'features':{feature(f,l,p,w)}}
                for f,l,p,w in itertools.product(range(2),['A','B'],range(2),range(2))}

    def test_identical_label_position_mapping_null_controls(self):
        for feature in [lambda f,l,p,w:'all',lambda f,l,p,w:l,
                        lambda f,l,p,w:p,lambda f,l,p,w:f^(l=='B')]:
            result,_,matrix=position_contrasts(self.synthetic(feature))
            self.assertEqual(result['cross_position']['fact_effect'],0)
            self.assertEqual(fact_assignment_null(matrix),[0,0,0,0])

    def test_fact_positive_control(self):
        result,_,matrix=position_contrasts(self.synthetic(lambda f,l,p,w:f))
        self.assertEqual(result['cross_position']['fact_effect'],1)
        self.assertEqual(fact_assignment_null(matrix),[1,0,0,-1])
        self.assertEqual(result['position_effect'],0)

    def test_position_control_detects_only_position(self):
        result,_,_=position_contrasts(self.synthetic(lambda f,l,p,w:p))
        self.assertEqual(result['position_effect'],1)
        self.assertEqual(result['cross_position']['fact_effect'],0)

    def test_mapping_only_exposes_opposing_components(self):
        result,_,_=position_contrasts(self.synthetic(lambda f,l,p,w:f^(l=='B')))
        self.assertEqual(result['cross_position']['fact_same_label'],1)
        self.assertEqual(result['cross_position']['fact_different_label'],-1)

    def test_pilot_gate_requires_all_sixteen_and_balance(self):
        jobs=[j for j in make_jobs() if j['split']=='pilot']
        records=[dict(prompt=j['prompt'],input_tokens=['same','tokens'],
                      salient_logits=[dict(token=j['expected_label'],probability=1)]) for j in jobs]
        self.assertTrue(pilot_gate(records,jobs)['passed'])
        self.assertFalse(pilot_gate(records[:-1],jobs)['passed'])
        records[0]['salient_logits'][0]['token']='C'
        self.assertFalse(pilot_gate(records,jobs)['passed'])
        records[0]['salient_logits'][0]['token']=jobs[0]['expected_label']
        records[0]['input_tokens'].append('extra')
        self.assertFalse(pilot_gate(records,jobs)['passed'])

    def test_transient_replace_error_is_retried(self):
        with patch('scripts.control_io.os.replace',side_effect=[PermissionError(),None]) as replace:
            replace_with_retry('a','b',delay=0)
            self.assertEqual(replace.call_count,2)

    def test_persistent_error_is_not_silenced(self):
        with patch('scripts.control_io.os.replace',side_effect=PermissionError()):
            with self.assertRaises(PermissionError):replace_with_retry('a','b',attempts=2,delay=0)

    def test_atomic_json_preserves_previous_on_invalid_data(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'status.json';atomic_json(p,{'state':'finished'})
            with self.assertRaises(ValueError):atomic_json(p,{'value':float('nan')})
            self.assertEqual(json.loads(p.read_text()),{'state':'finished'})
            self.assertEqual(len(list(Path(folder).glob('*.tmp'))),0)

    def test_end_to_end_synthetic_analysis_and_failed_gate(self):
        import scripts.analyze_position_controls as analysis
        def audit(job,model,converter):
            f=job['fact'];label=job['expected_label']
            rep=dict(features={f'f{f}'},features_with_errors={f'f{f}'},feature_weights={f'f{f}':1.},
                     prompt_tokens=['equal','bag'],correct=True,raw_clean=True)
            return dict(job_id=job['job_id'],status='ok'),rep
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'freeze.json').write_text('{}')
            with patch.object(analysis,'OUT',root),patch.object(analysis,'load_converter',return_value=None),patch.object(analysis,'audit_graph',side_effect=audit):
                result=analysis.analyze_model()
                self.assertTrue(result['retrieval_gate'])
                self.assertEqual(result['primary']['mean_fact_effect'],1)
                self.assertEqual(result['primary']['exact_conditional_assignment_p'],1/4096)
                self.assertEqual(result['primary']['null_assignments'],4096)
            def failed(job,model,converter):
                row,rep=audit(job,model,converter)
                if job['block']=='japan_italy':rep['correct']=False
                return row,rep
            with patch.object(analysis,'OUT',root),patch.object(analysis,'load_converter',return_value=None),patch.object(analysis,'audit_graph',side_effect=failed):
                result=analysis.analyze_model()
                self.assertFalse(result['retrieval_gate'])
                self.assertNotIn('exact_conditional_assignment_p',result['primary'])


if __name__=='__main__':unittest.main()
