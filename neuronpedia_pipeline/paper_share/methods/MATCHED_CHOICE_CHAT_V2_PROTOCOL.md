# Matched-choice chat-frame revision v2

5 September 2026, after inspecting partial behavior-only v1 pilot outcomes and before requesting any v2 outcome. This is an explicitly outcome-informed protocol revision, not an unchanged continuation of v1. All v1 predictions, failures, and rules remain archived. No held-out graph similarity has been inspected for this revision.

## Reason

The raw-completion Qwen3-4B pilot chose A for both France/Paris mappings in the first four prompts, including the two where Paris was B. This fails the intended mapping control. Qwen3-4B's official tokenizer configuration supplies a chat template with an `enable_thinking=False` option. V2 tests whether the appropriate instruction framing improves behavior; improvement is not assumed.

## Sole prompt change

Render every v1 prompt as one user message through the archived official Qwen3-4B chat template, with `add_generation_prompt=True`, `enable_thinking=False`, and no tools. Do not hand-edit the rendered string or supply factual demonstrations. All countries, capitals, query wordings, mappings, expected A/B decisions, pilot/held-out blocks, and graph settings remain unchanged. Pin and hash the tokenizer configuration, tokenizer, template renderer version, base design, and v2 design script before any v2 request.

Run Qwen3-4B only. Gemma-2-2B is a different, base-model pipeline and is not given Qwen's chat template. Its v1 pilot remains a separate experiment. Qwen3-1.7B remains unsupported by the hosted token cap. V2 is a new chat-conditioned choice experiment, not a repair to the original free-completion manuscript estimates.

## Gates and analysis

All eight v2 pilot previews must match the expected top label and have identical server input-token multisets. Only then generate the six fixed eight-cell held-out blocks. Confirm offline that each rendered block still has identical word and tokenizer-ID multisets and fits the 64-token hosted cap. No extra capitalization, whitespace, answer cue, prompt replacement, or template variation may be chosen after observing v2 outcomes.

Use the v1 integrity, complete-block retrieval, feature definitions, four fact/label pair categories, exact conditional fact-assignment null, bootstrap, and sensitivity rules unchanged. Full primary inference requires all six blocks eligible. For this revised analysis, apply conservative Bonferroni correction across three planned model/version primary opportunities (v1 Qwen, v1 Gemma, v2 Qwen), regardless of any pilot failures. Report the raw p and `min(1,3p)`. Original v1 rules are not retroactively rewritten.

V1 and v2 share a single durable quota ledger, counting all preview/generation/retry POSTs, at least 125 seconds between starts and no more than 30 requests in any rolling hour. Each version has separate deterministic slugs and output paths. Ambiguous submissions are reconciled or reported blocked, never blindly resubmitted. Failure of v2 is retained as a behavior/design limitation rather than hidden behind another unrecorded prompt change.

Outputs: `data/model_extension/matched_choice_chat_v2`. This document and manifest are frozen before v2 starts. See [official tokenizer configuration](https://huggingface.co/Qwen/Qwen3-4B/blob/main/tokenizer_config.json); the artifact records the actual pinned revision and SHA-256 used, not merely this moving link.
