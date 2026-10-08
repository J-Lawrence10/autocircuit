import unittest
from types import SimpleNamespace

from scripts.exploratory_confound_checks import (
    MODELS, answer_check, features, lexical_checks, logit_record, size_checks, words,
)


class FakeTokenizer:
    def __init__(self, encodings, decodings):
        self.encodings = encodings
        self.decodings = decodings

    def encode(self, value, add_special_tokens=False):
        return SimpleNamespace(ids=self.encodings[value])

    def decode(self, ids, skip_special_tokens=False):
        return ''.join(self.decodings[i] for i in ids)


class ExploratoryChecksTests(unittest.TestCase):
    def test_word_definition_keeps_numbers_and_splits_punctuation(self):
        self.assertEqual(words("Gold's SYMBOL, 1492!"), {'gold', 's', 'symbol', '1492'})

    def test_identity_collisions_and_errors_are_not_features(self):
        nodes = [dict(node_id='x', layer=0, feature=1, feature_type='transcoder'),
                 dict(node_id='x', layer=0, feature=-1, feature_type='error'),
                 dict(node_id='y', layer=1, feature=2, feature_type='transcoder'),
                 dict(node_id='z', layer=1, feature=2, feature_type='lorsa')]
        self.assertEqual(features(nodes), {('transcoder', 1, 2), ('lorsa', 1, 2)})

    def test_logit_uses_probability_not_node_order(self):
        nodes = [dict(feature_type='logit', feature=1, token_prob=.1, clerp='Output " A" (p=0.1)'),
                 dict(feature_type='logit', feature=2, token_prob=.8, clerp='Output " Hg" (p=0.8)')]
        self.assertEqual(logit_record(nodes)['top_text'], ' Hg')
        self.assertEqual(logit_record(nodes)['top_id'], 2)

    def test_no_matched_controls_is_missing_not_zero(self):
        common = dict(model='gemma-2-2b', domain='chemistry', target_fact='a', candidate_n=100,
                      target_n=100, own_n=100, same_expected_answer=False)
        pairs = [{**common, 'candidate_fact':'a', 'same_fact':True, 'feature_jaccard':.5, 'word_jaccard':.7},
                 {**common, 'candidate_fact':'b', 'same_fact':False, 'feature_jaccard':.2, 'word_jaccard':.3}]
        rows, summary = lexical_checks(pairs)
        self.assertTrue(all(r['margin'] is None and r['comparator_n'] == 0 for r in rows))
        self.assertTrue(all(r['mean'] is None for r in summary))

    def graph(self, top_id=2, top_text=' H'):
        return dict(prompt='p', prompt_tokens=['p'], expected='Hg', top_id=top_id, top_text=top_text)

    def test_equal_count_sampler_is_seeded_and_preserves_full_sets(self):
        graphs = [dict(model=model, status='ok', design='controlled', fact=fact, role=role,
                       features={(fact, j) for j in range(4)})
                  for model in MODELS for fact in ['a', 'b'] for role in ['target', 'positive_paraphrase']]
        eligible = {model:[dict(pair_id=f, domain='chemistry') for f in ['a','b']] for model in MODELS}
        first = size_checks(graphs, eligible, 3)
        self.assertEqual(first, size_checks(graphs, eligible, 3))
        self.assertTrue(all(r['mean_margin'] == 1 for r in first[0] if r['fraction'] == 1))
        self.assertTrue(all(r['sampled_k'] == (4 if r['fraction'] == 1 else 2) for r in first[2]))

    def test_partial_token_is_not_whole_answer(self):
        tok = FakeTokenizer({'p':[1], 'pHg':[1,4,3], 'p Hg':[1,2,3]}, {1:'p',2:' H',3:'g',4:'H'})
        result = answer_check(self.graph(), tok)
        self.assertFalse(result['strict_string_match'])
        self.assertEqual(result['answer_status'], 'multi_token_prefix_only')

    def test_whitespace_match_is_not_semantic_success(self):
        tok = FakeTokenizer({'p':[1], 'pHg':[1,4], 'p Hg':[1,2,4]}, {1:'p',2:' ',4:'Hg'})
        self.assertEqual(answer_check(self.graph(top_text=' '), tok)['answer_status'], 'whitespace_only_compatible')

    def test_tokenizer_provenance_mismatch_fails_closed(self):
        tok = FakeTokenizer({'p':[1]}, {1:'wrong',2:' H'})
        self.assertEqual(answer_check(self.graph(), tok)['answer_status'], 'unresolved_tokenizer_validation')

    def test_whole_answer_and_incompatible_output(self):
        tok = FakeTokenizer({'p':[1], 'pHg':[1,3], 'p Hg':[1,2]}, {1:'p',2:' Hg',3:'Hg',4:'a'})
        self.assertEqual(answer_check(self.graph(top_text=' Hg'), tok)['answer_status'], 'whole_answer_next_token')
        self.assertEqual(answer_check(self.graph(4, 'a'), tok)['answer_status'], 'next_token_mismatch')


if __name__ == '__main__':
    unittest.main()
