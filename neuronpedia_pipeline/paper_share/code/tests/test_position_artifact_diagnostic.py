import unittest
from collections import Counter
import json

from scripts.audit_position_pilot import score_prompt_text, SOURCE
from scripts.diagnose_position_artifact import make_jobs, record


class PositionArtifactTests(unittest.TestCase):
    def test_independent_oracle_follows_country_and_capital_not_position(self):
        prefix='Reply with only A or B. A: Berlin. B: Paris. Countries: France, Germany. '
        first=score_prompt_text(prefix+'Question: what is the capital for the first country, not the second? Answer:')
        second=score_prompt_text(prefix+'Question: for the second country not the first, what is the capital? Answer:')
        self.assertEqual(first['expected_label'],'B')
        self.assertEqual(first['capital'],'Paris')
        self.assertEqual(second['expected_label'],'A')
        self.assertEqual(second['capital'],'Berlin')

    def test_all_saved_expectations_match_text_oracle(self):
        jobs=json.loads((SOURCE/'jobs.json').read_text())
        for job in jobs:
            oracle=score_prompt_text(job['plain_prompt'])
            self.assertEqual(oracle['expected_label'],job['expected_label'])
            self.assertEqual(oracle['country'],job['queried_country'])

    def test_fixed_complete_diagnostic(self):
        jobs=make_jobs();frozen=record(jobs)
        self.assertEqual(frozen['n'],20)
        self.assertEqual(Counter(j['arm'] for j in jobs),dict(literal=2,previous_success_replay=2,
                         ordinal_label=4,ordinal_capital=4,named_label=4,named_capital=4))
        self.assertEqual(jobs,make_jobs())

    def test_exact_replay_not_silently_reworded(self):
        originals={j['job_id']:j for j in json.loads((SOURCE/'jobs.json').read_text())}
        for job in make_jobs():
            if job['arm']=='ordinal_label':
                original=originals['pilot_france_germany__'+job['case']]
                self.assertEqual(job['prompt'],original['prompt'])
                self.assertEqual(job['expected'],original['expected_label'])


if __name__=='__main__':unittest.main()
