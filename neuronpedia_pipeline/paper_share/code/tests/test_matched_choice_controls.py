from collections import Counter
import itertools
import unittest
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import threading

from scripts.matched_choice_controls import make_jobs, word_bag, validate_design
from scripts.run_matched_choice_controls import rate_delay, pilot_gate, file_lock
from scripts.analyze_matched_choice_controls import KEYS, contrasts, fact_assignment_null


class MatchedChoiceTests(unittest.TestCase):
    def test_offline_balance_and_token_limit(self):
        result=validate_design(make_jobs())
        self.assertEqual(len(result['blocks']),7)
        self.assertTrue(all(r['qwen_token_multiset_identical'] for r in result['blocks']))

    def test_chat_revision_preserves_content_and_balance(self):
        from scripts.matched_choice_chat_controls import make_jobs as chat_jobs, TOKENIZER_DIR
        from tokenizers import Tokenizer
        tokenizer=Tokenizer.from_file(str(TOKENIZER_DIR/'tokenizer.json'))
        jobs=chat_jobs()
        self.assertEqual(len(jobs),56)
        for block in {j['block'] for j in jobs}:
            rows=[j for j in jobs if j['block']==block]
            encoded=[tokenizer.encode(j['prompt'],add_special_tokens=False).ids for j in rows]
            self.assertTrue(all(Counter(x)==Counter(encoded[0]) for x in encoded))
            self.assertLessEqual(max(map(len,encoded))+1,64)
            self.assertTrue(all(j['plain_prompt'] in j['prompt'] for j in rows))

    def test_word_bag_and_label_balance(self):
        jobs=make_jobs()
        for block in {j['block'] for j in jobs}:
            rows=[j for j in jobs if j['block']==block]
            self.assertTrue(all(word_bag(j['prompt'])==word_bag(rows[0]['prompt']) for j in rows))
            for fact in [0,1]:
                self.assertEqual(Counter(j['expected_label'] for j in rows if j['fact']==fact),{'A':2,'B':2})

    def test_rate_limit_counts_failures_and_recent_reservations(self):
        events=[{'epoch':float(i)} for i in range(30)]
        self.assertGreater(rate_delay(events,100),3500)
        self.assertEqual(rate_delay([{'epoch':100}],200),25)
        self.assertEqual(rate_delay([{'epoch':100}],3701),0)

    def test_quota_lock_waits_for_another_worker(self):
        with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(max_workers=1) as pool:
            path=Path(tmp)/'shared.lock';started=threading.Event()
            def contender():
                started.set()
                with file_lock(path,wait_for_contention=True):return True
            with file_lock(path):
                future=pool.submit(contender)
                self.assertTrue(started.wait(1))
            self.assertTrue(future.result(timeout=3))

    def pilot(self):
        jobs=[j for j in make_jobs() if j['split']=='pilot']
        records=[dict(prompt=j['prompt'],input_tokens=j['prompt'].split(),
                      salient_logits=[dict(token=' '+j['expected_label'],probability=.9,token_id=1)]) for j in jobs]
        # Actual server-token multiset is the gate; punctuation can bind to words in split(),
        # so use the audited identical word bags for this synthetic gate fixture.
        for r in records:r['input_tokens']=list(word_bag(jobs[0]['prompt']).elements())
        return jobs,records

    def test_pilot_pass_requires_all_eight_and_token_balance(self):
        jobs,records=self.pilot()
        self.assertTrue(pilot_gate(records,jobs)['passed'])
        records[0]['salient_logits'][0]['token']='wrong'
        self.assertFalse(pilot_gate(records,jobs)['passed'])
        jobs,records=self.pilot();records[0]['input_tokens'].append('extra')
        self.assertFalse(pilot_gate(records,jobs)['passed'])
        self.assertFalse(pilot_gate(records[:-1],jobs)['passed'])

    def test_identical_graphs_are_a_zero_effect_null(self):
        result=contrasts(np.ones((4,4)))
        self.assertEqual(result['fact_effect'],0)
        self.assertEqual(result['label_effect'],0)

    def test_label_only_graphs_cannot_fake_a_fact_effect(self):
        matrix=np.array([[float(label==other_label) for _,other_label in KEYS] for _,label in KEYS])
        result=contrasts(matrix)
        self.assertEqual(result['fact_effect'],0)
        self.assertEqual(result['label_effect'],1)
        self.assertEqual(fact_assignment_null(matrix),[0,0,0,0])

    def test_fact_only_positive_control_and_exact_null(self):
        matrix=np.array([[float(fact==other_fact) for other_fact,_ in KEYS] for fact,_ in KEYS])
        result=contrasts(matrix)
        self.assertEqual(result['fact_effect'],1)
        self.assertEqual(result['label_effect'],0)
        self.assertEqual(fact_assignment_null(matrix),[1,0,0,-1])
        pooled=[np.mean(x) for x in itertools.product(fact_assignment_null(matrix),repeat=6)]
        self.assertEqual(len(pooled),4096)
        self.assertEqual(sum(v>=1 for v in pooled),1)


if __name__=='__main__':unittest.main()
