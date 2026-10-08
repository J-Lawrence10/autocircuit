# Audit of the failed position pilot

1 October 2026. The purpose is to determine whether the failed country-position pilot reflects incorrect scoring or transport, a prompt-induced task shortcut, or an unresolved hosted-model issue. This is an outcome-informed diagnostic, not a new confirmatory experiment. The failed pilot and all earlier estimates remain unchanged.

## Local audit

Reconstruct the correct answer by parsing the actual prompt text and using a country-capital lookup independent of the factorial metadata. Check all 112 saved prompts. For the 16 observed pilot responses, verify the submitted and returned prompt, every token piece against the pinned tokenizer, top-token ID decoding, and archived request/response provenance. Compare frozen code and protocol hashes. These checks cannot independently certify the hosted model weights or its numerical implementation.

## Fixed remote diagnostic

Use hosted Qwen3-4B and the same source set and no-thinking chat frame. No local inference and no graph generation. Freeze every diagnostic prompt and expected answer before requesting any new outcome. Preserve all cases regardless of success.

Twenty next-token previews are planned:

- Two literal instruction checks asking only for A or B.
- Two exact replays of previously successful named-country pilot prompts, one with each correct label.
- Four cases selected from the failed pilot where the expected label is opposite to the ordinal shortcut: first country requiring B, or second country requiring A, balanced over France and Germany.
- For those four cases, a complete two-by-two diagnostic: select the country by ordinal versus explicit name, and request an A/B label versus the capital name. The original ordinal-plus-label arm is an exact replay. The other twelve prompts change only the query reference or response instruction, retaining the country list and options.

This is deliberately a diagnostic, not a token-matched graph experiment. Capital-name responses must be assessed as next-token format compliance; unexpected whitespace or partial tokens are not automatically factual errors. Expected capital continuations are checked offline for single-token compatibility. Request order is fixed before outcomes, with positive controls first and the sixteen factorial cases in seeded shuffled order. Shared quota remains at least 125 seconds between POST starts and at most 30 per rolling hour, including retries. Stop on unresolved transport errors. Do not issue graph-generation requests or adaptive extra prompts.

## Interpretation before outcomes

If independently parsed expected labels disagree with the manifest, fix and test scoring in a new implementation without erasing the originals. If exact tokens or payloads disagree, investigate transport before interpreting behavior.

If exact archived failures reproduce while named-country versions succeed, the wording or ordinal task is implicated. If ordinal capital-name responses succeed but ordinal A/B responses fail, the difficulty is more specifically in combining selection with the label mapping. If all new variants fail, this does not establish loss of factual knowledge; the hosted runtime and response format remain alternatives. If literal or formerly successful controls fail, do not attribute the problem solely to the position manipulation.

A newly successful formulation would be a candidate repair to validate across all balanced cells and a fresh held-out graph protocol, not proof that the old results are now rescued. Model probabilities close to one are reported API values, not an independent check on numerical accuracy. No new graph claim, p-value, or manuscript conclusion is authorized by these diagnostic previews alone.
