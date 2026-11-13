import json
from pathlib import Path
import tempfile
import unittest
import contextlib
import io
from unittest.mock import Mock,patch

from scripts.failure_case_design import make_jobs,token_roles,layout,digest
from scripts.analyze_failure_case_graphs import local_edges,compare_triple,clean_export
import run_matched_choice_controls as transport


class FailureGraphTests(unittest.TestCase):
    def test_manifest_and_partner_matching(self):
        jobs=make_jobs();byid={j['job_id']:j for j in jobs}
        self.assertEqual(len(jobs),16)
        for j in jobs:
            if j['reference']!='ordinal':continue
            same=byid[j['same_country_partner']];other=byid[j['same_output_partner']]
            self.assertEqual(same['queried_country'],j['queried_country'])
            self.assertNotEqual(other['queried_country'],j['queried_country'])
            self.assertEqual(layout(other['plain_prompt']),layout(j['plain_prompt']))
            self.assertEqual(other['preview_answer'],j['preview_answer'])
            self.assertTrue(same['preview_correct'] and other['preview_correct'])

    def test_token_alignment_preserves_occurrences(self):
        for j in make_jobs():
            rows=token_roles(j);roles={r['role'] for r in rows}
            self.assertIn('chat_frame',roles)
            self.assertIn('option_A_label',roles);self.assertIn('option_B_label',roles)
            self.assertEqual(sum(role.startswith('country_list_') for role in roles),2)
            if j['reference']=='named':self.assertIn('question_country_'+j['queried_country'],roles)
            else:self.assertTrue({'ordinal_first','ordinal_second'}<=roles)
            self.assertEqual(''.join(r['token'] for r in rows),j['prompt'])

    def graph(self):
        nodes=[dict(id='e',node_type='embedding',layer=-1,feature_id=0,ctx_idx=0),
               dict(id='r',node_type='error',layer=1,feature_id=-1,ctx_idx=1),
               dict(id='f',node_type='transcoder',layer=1,feature_id=2,ctx_idx=1),
               dict(id='l',node_type='logit',layer=2,feature_id=32,ctx_idx=1,token='A')]
        edges=[dict(source='e',target='f',weight=.5),dict(source='e',target='l',weight=1),
               dict(source='r',target='l',weight=4),dict(source='f',target='l',weight=-2)]
        return dict(nodes=nodes,edges=edges)

    def test_signed_and_absolute_weights_and_coverage(self):
        info,direct,upstream,groups,_=local_edges(self.graph(),[dict(token_index=0,role='ordinal_first'),dict(token_index=1,role='option_A_capital_Berlin')],'A')
        self.assertEqual(info['direct_signed_weight'],3)
        self.assertEqual(info['direct_abs_weight'],7)
        self.assertAlmostEqual(info['direct_error_fraction'],4/7)
        self.assertAlmostEqual(sum(g['fraction'] for g in groups),1)
        self.assertEqual(len(upstream),1)
        self.assertTrue(any(e['weight']<0 for e in info['selected_edges']))
        self.assertEqual(sum(g['feature_only_fraction'] or 0 for g in groups),1)

    def test_missing_logit_and_zero_denominator_not_zero_effect(self):
        g=self.graph()
        info,*_=local_edges(g,[],'B');self.assertEqual(info['status'],'missing_or_ambiguous_observed_logit')
        g['edges']=[];info,*_=local_edges(g,[],'A');self.assertIsNone(info['direct_error_fraction'])
        g['nodes'].append({**g['nodes'][-1],'id':'l2','token':' A'})
        info,*_=local_edges(g,[],'A');self.assertEqual(info['status'],'missing_or_ambiguous_observed_logit')

    def test_collision_or_duplicate_never_clean(self):
        clean=dict(raw_ambiguous_node_id_count=0,raw_duplicate_endpoint_edge_count=0)
        self.assertTrue(clean_export(clean,dict(duplicate_endpoint_edge_count=0)))
        for key in clean:self.assertFalse(clean_export({**clean,key:1},dict(duplicate_endpoint_edge_count=0)))
        self.assertFalse(clean_export(clean,dict(duplicate_endpoint_edge_count=1)))

    def test_wrong_answer_kept_and_output_drift_excluded(self):
        job=next(j for j in make_jobs() if j['reference']=='ordinal')
        ids=[job['job_id'],job['same_country_partner'],job['same_output_partner']]
        rows={i:dict(clean_eligible=True,observed='A',correct=True,drift=False) for i in ids}
        rows[ids[0]]['correct']=False
        reps={i:dict(features={1,2},features_with_errors={1,2},feature_weights={1:1,2:1}) for i in ids}
        result=compare_triple(job,rows,reps)
        self.assertTrue(result['clean_eligible'])
        self.assertEqual(result['jaccard']['output_minus_country'],0)
        self.assertEqual(result['equal_count']['means']['output_minus_country'],0)
        rows[ids[2]]['observed']='B'
        self.assertFalse(compare_triple(job,rows,reps)['clean_eligible'])

    def test_resume_reuses_verified_raw_and_rejects_changed_bytes(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(transport,'OUT',Path(folder)):
            job={'job_id':'test'};dest=Path(folder)/'qwen3-4b/graphs/test';dest.mkdir(parents=True)
            raw=dest/'raw_graph.json';raw.write_text('{"nodes":[]}')
            meta={'sha256':digest(raw)};(dest/'metadata.json').write_text(json.dumps(meta))
            client=Mock()
            self.assertEqual(transport.graph_job(client,'qwen3-4b',job,{}),meta)
            client.post.assert_not_called()
            raw.write_text('{}')
            with self.assertRaisesRegex(RuntimeError,'Checksum mismatch'):transport.graph_job(client,'qwen3-4b',job,{})
            client.post.assert_not_called()

    def test_raw_conversion_and_analysis_preserve_failure(self):
        import scripts.analyze_failure_case_graphs as analysis
        from convert_model_extension import load_converter
        job=next(j for j in make_jobs() if j['reference']=='ordinal')
        roles=token_roles(job)
        g=self.graph()
        nodes=[]
        for n in g['nodes']:
            nodes.append(dict(node_id=n['id'],feature_type=n['node_type'],layer=str(n['layer']),
                              feature=n['feature_id'],ctx_idx=n['ctx_idx'],token=n.get('token'),
                              token_prob=1 if n['node_type']=='logit' else 0,influence=1,
                              clerp='',activation=1,is_target_logit=n['node_type']=='logit'))
        # Set the observed token to the previously wrong answer, independent of fixture label A.
        nodes[-1]['token']=job['preview_answer']
        raw=dict(nodes=nodes,links=g['edges'],metadata=dict(prompt=job['prompt'],prompt_tokens=[r['token'] for r in roles],
                 scan='qwen3-4b',slug='synthetic-test-only',node_threshold=.8,
                 info={'transcoder_set':'mwhanna/qwen3-4b-transcoders'},
                 generation_settings=dict(max_n_logits=10,desired_logit_prob=.99,max_feature_nodes=5000),
                 pruning_settings={'edge_threshold':.85}))
        with tempfile.TemporaryDirectory() as folder,patch.object(analysis,'OUT',Path(folder)),contextlib.redirect_stdout(io.StringIO()):
            dest=Path(folder)/'qwen3-4b/graphs'/job['job_id'];dest.mkdir(parents=True)
            p=dest/'raw_graph.json';p.write_text(json.dumps(raw))
            (dest/'metadata.json').write_text(json.dumps({'sha256':digest(p)}))
            row,rep=analysis.analyze_graph(job,load_converter())
            self.assertEqual(row['status'],'ok',row.get('error'))
            self.assertFalse(row['correct']);self.assertFalse(row['drift'])
            self.assertTrue(row['clean_eligible']);self.assertIsNotNone(rep)
            self.assertTrue((dest/'upstream_answer_edges.csv').exists())
            self.assertEqual(row['local']['direct_signed_weight'],3)

    def test_complete_synthetic_pipeline_without_remote_calls(self):
        import scripts.analyze_failure_case_graphs as analysis
        import scripts.plot_failure_case_graphs as plots
        import scripts.validate_failure_case_graphs as validation
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()):
            root=Path(folder)
            (root/'freeze.json').write_text(json.dumps({'code_hashes':{}}))
            for job in make_jobs():
                dest=root/'qwen3-4b/graphs'/job['job_id'];dest.mkdir(parents=True)
                roles=token_roles(job);nodes=[]
                for n in self.graph()['nodes']:
                    nodes.append(dict(node_id=n['id'],feature_type=n['node_type'],layer=str(n['layer']),feature=n['feature_id'],
                                      ctx_idx=n['ctx_idx'],token=job['preview_answer'] if n['node_type']=='logit' else n.get('token'),
                                      token_prob=1 if n['node_type']=='logit' else 0,influence=1,activation=1))
                graph=dict(nodes=nodes,links=self.graph()['edges'],metadata=dict(scan='qwen3-4b',slug='SYNTHETIC-TEST-ONLY',
                           prompt=job['prompt'],prompt_tokens=[r['token'] for r in roles],node_threshold=.8,
                           info={'transcoder_set':'mwhanna/qwen3-4b-transcoders'},pruning_settings={'edge_threshold':.85},
                           generation_settings=dict(max_n_logits=10,desired_logit_prob=.99,max_feature_nodes=5000)))
                raw=dest/'raw_graph.json';raw.write_text(json.dumps(graph))
                (dest/'metadata.json').write_text(json.dumps({'sha256':digest(raw)}))
            with patch.object(analysis,'OUT',root),patch.object(plots,'OUT',root),patch.object(validation,'OUT',root):
                result=analysis.main()
                self.assertEqual(result['valid_graphs'],16)
                self.assertEqual(result['clean_comparisons'],8)
                plots.main()
                report=validation.main()
                self.assertTrue(report['passed'])
                self.assertEqual(len(list((root/'figures').glob('*.png'))),10)
                self.assertIn('Similarity alone cannot distinguish a position shortcut',(root/'FINDINGS.md').read_text())
                self.assertIn('No confirmatory p-values',(root/'FINDINGS.md').read_text())


if __name__=='__main__':unittest.main()
