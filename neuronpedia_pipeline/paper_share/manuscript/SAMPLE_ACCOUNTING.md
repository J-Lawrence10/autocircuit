# Questions and graphs available for the original comparison

This table separates data collection from analysis inclusion. Each subject has five evaluation questions, with four required prompt/control graphs per question. Questions used plus questions not used always equals five. These are not accuracy scores. Development questions and the later follow-up studies are not included in this table.

| Model | Subject | Graphs available | Graphs planned | Questions used | Questions not used | Reasons questions were not used |
|---|---|---:|---:|---:|---:|---|
| Gemma-2-2B | Chemistry | 20 | 20 | 5 | 0 | None |
| Gemma-2-2B | Geography | 20 | 20 | 0 | 5 | Expected next-token check failed: 4; No qualifying comparison question: 1 |
| Gemma-2-2B | History | 20 | 20 | 3 | 2 | Expected next-token check failed: 2 |
| Qwen3-1.7B | Chemistry | 20 | 20 | 5 | 0 | None |
| Qwen3-1.7B | Geography | 5 | 20 | 0 | 5 | Incomplete prompt/control set: 5 |
| Qwen3-1.7B | History | 0 | 20 | 0 | 5 | No graphs collected: 5 |
| Qwen3-4B* | Chemistry | 20 | 20 | 5 | 0 | None |
| Qwen3-4B* | Geography | 20 | 20 | 5 | 0 | None |
| Qwen3-4B* | History | 18 | 20 | 0 | 5 | Incomplete prompt/control set: 1; Expected next-token check failed: 3; No qualifying comparison question: 1 |

A failed next-token check does not necessarily mean a wrong completed answer: partial words and alternative continuations can fail this rule. A complete question can still be unused if no second qualifying question remains in its subject and evaluation split.

The original Qwen3-4B extension remains incomplete at 145 of 147 total graphs. The asterisk marks this status. Existing results and inclusion rules are unchanged.

[Per-question audit](../tables/test_fact_inclusion_audit.csv)
