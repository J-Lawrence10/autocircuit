import unittest

from scripts.control_manifest import validate_control_manifest


class ControlManifestTests(unittest.TestCase):
    def test_complete_pair_passes(self):
        rows = [
            {'pair_id': 'p', 'domain': 'd', 'split': 'development', 'role': 'target', 'prompt': 'a', 'expected_token': 'x'},
            {'pair_id': 'p', 'domain': 'd', 'split': 'development', 'role': 'positive_paraphrase', 'prompt': 'b', 'expected_token': 'x'},
            {'pair_id': 'p', 'domain': 'd', 'split': 'development', 'role': 'negative_same_template', 'prompt': 'c', 'expected_token': ''},
            {'pair_id': 'p', 'domain': 'd', 'split': 'development', 'role': 'negative_nonce', 'prompt': 'd', 'expected_token': ''},
        ]
        validate_control_manifest(rows)

    def test_missing_negative_fails(self):
        rows = [
            {'pair_id': 'p', 'domain': 'd', 'split': 'development', 'role': 'target', 'prompt': 'a', 'expected_token': 'x'},
            {'pair_id': 'p', 'domain': 'd', 'split': 'development', 'role': 'positive_paraphrase', 'prompt': 'b', 'expected_token': 'x'},
            {'pair_id': 'p', 'domain': 'd', 'split': 'development', 'role': 'negative_same_template', 'prompt': 'c', 'expected_token': ''},
        ]
        with self.assertRaises(ValueError):
            validate_control_manifest(rows)


if __name__ == '__main__':
    unittest.main()
