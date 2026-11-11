import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch


def load_converter_module():
    path = Path(__file__).parent.parent / 'scripts' / '2_convert_graph.py'
    spec = importlib.util.spec_from_file_location('converter_under_test', path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ConverterTests(unittest.TestCase):
    def test_rejects_ambiguous_duplicate_node_ids(self):
        raw = {
            'metadata': {'prompt': 'x', 'slug': 'x', 'scan': 'test', 'node_threshold': 0.8},
            'nodes': [
                {'node_id': 'same', 'feature_type': 'cross layer transcoder'},
                {'node_id': 'same', 'feature_type': 'mlp reconstruction error'},
            ],
            'links': [],
        }
        module = load_converter_module()
        with patch('builtins.open', mock_open(read_data=json.dumps(raw))):
            with self.assertRaisesRegex(ValueError, 'ambiguous duplicate node'):
                module.convert_neuronpedia_graph('raw.json', 'converted.json')

    def test_preserves_embedding_and_logit_nodes(self):
        raw = {
            'metadata': {
                'prompt': 'The answer is',
                'slug': 'the-answer-is',
                'scan': 'test-model',
                'node_threshold': 0.8,
            },
            'nodes': [
                {
                    'node_id': 'E_1_0', 'feature': None, 'layer': 'E',
                    'ctx_idx': 0, 'feature_type': 'embedding', 'token': 'The',
                    'activation': None, 'influence': 0.1,
                },
                {
                    'node_id': '0_2_0', 'feature': 2, 'layer': '0',
                    'ctx_idx': 0, 'feature_type': 'cross layer transcoder',
                    'activation': 1.0, 'influence': 0.5,
                },
                {
                    'node_id': '2_3_0', 'feature': 3, 'layer': '2',
                    'ctx_idx': 0, 'feature_type': 'logit', 'token': ' yes',
                    'token_prob': 0.9, 'is_target_logit': True,
                    'activation': None, 'influence': None,
                },
            ],
            'links': [
                {'source': 'E_1_0', 'target': '0_2_0', 'weight': 0.5},
                {'source': '0_2_0', 'target': '2_3_0', 'weight': -0.7},
            ],
        }
        module = load_converter_module()
        file_mock = mock_open(read_data=json.dumps(raw))
        with patch('builtins.open', file_mock):
            converted = module.convert_neuronpedia_graph('raw.json', 'converted.json')

        self.assertEqual(len(converted['nodes']), 3)
        self.assertEqual(len(converted['edges']), 2)
        types = {node['node_type'] for node in converted['nodes']}
        self.assertEqual(types, {'embedding', 'cross layer transcoder', 'logit'})
        self.assertEqual(converted['metadata']['model_output'], ' yes')
        self.assertEqual(converted['metadata']['output_probability'], 0.9)


if __name__ == '__main__':
    unittest.main()
