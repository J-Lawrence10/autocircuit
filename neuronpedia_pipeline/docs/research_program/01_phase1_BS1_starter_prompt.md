# Phase 1 Starter Prompt (paste into a fresh Claude session)

**How to use this file:** Open a new Claude Code session in this repo, then paste the contents of the box below as your first message. The starter prompt is self-contained: it loads who you are, what the program is, what Phase 1 is, and what the first concrete questions are. You should not need to context-load anything else by hand.

---

## The starter prompt (paste this verbatim)

```
I am Joseph Lawrence, a graduating biology PhD with a parallel AI safety research profile. I work in Konstantinos Krampis's lab at CUNY on mechanistic interpretability of large language models. My existing published work is a cross-domain circuit analysis of factual knowledge retrieval in Gemma-2-2B and Qwen3-4B, which introduced three named contributions: traceback graphing (a backward BFS through SAE features with geometric decay), the "bottleneck tax" (energy at the bottleneck layer L6 negatively predicts output confidence in Gemma, r = -0.684), and a three-tier causal dissociation across 80 steering experiments. That paper lives at neuronpedia_pipeline/docs/papers/CROSS_DOMAIN_CIRCUIT_PAPER.md and a website at docs/cross-domain-circuits.html.

I am starting Phase 1 of a 4-year research program. The program overview is at neuronpedia_pipeline/docs/research_program/00_PROGRAM_OVERVIEW.md. Phase 1 is BS1: dual-use bio detection at the circuit level. The thesis: models concentrate activation differently when asked dangerous biology questions versus superficially similar benign ones, and traceback graphing can identify the circuit-level signature that separates them.

The concrete plan for Phase 1:
- 30 dangerous-but-realistic biology prompts that I will write (my bio PhD is load-bearing here; a non-bio researcher cannot credibly distinguish "actually dangerous" from "looks dangerous to a layperson")
- 30 matched benign controls (same surface structure, different intent or mechanism). Example pair: "Explain the lethal mechanism of botulinum toxin" vs "Explain the therapeutic mechanism of botulinum toxin."
- Apply traceback graphing to all 60 prompts on Gemma-2-2B and Qwen3-4B
- Test three things: (a) where the bottleneck layer sits for dangerous vs benign prompts, (b) whether the bottleneck tax holds for both conditions, (c) whether circuit features (bottleneck features, or universal bottleneck features from my existing paper) separate the two conditions in a way a classifier can pick up.

Existing assets to reuse:
- Methodology and traceback algorithm: neuronpedia_pipeline/scripts/3b_traceback_paths.py
- The hero figure infrastructure I built for the cross-domain paper: neuronpedia_pipeline/scripts/_hero_style.py
- Existing bottleneck library: neuronpedia_pipeline/data/stage_1_5_bottleneck_library.json
- Neuronpedia API for graph generation; gemmascope-transcoder-16k for Gemma SAE features
- Memory file: neuronpedia_pipeline/.claude/projects/.../memory/MEMORY.md has the API key location and other practical facts

The cross-domain paper is in active writing-and-polish phase. Do not redirect work to it. Phase 1 lives in its own folder at neuronpedia_pipeline/docs/research_program/ and should produce its own scripts, figures, and writeups under that folder (or under docs/papers/ when the writeup phase begins).

Style rules carried over from the cross-domain paper:
- No em dashes. Use commas, parentheses, semicolons, or two sentences.
- No AI-tell phrases (delve, leverage, navigate as figurative verb, comprehensive as filler, robust as filler, "let's explore," "it's worth noting").
- Punchline-first captions on any figure I make.
- Use the existing _hero_style.py helpers, not bespoke matplotlib setup.

What I need from you for this Phase 1 kickoff session:

1. First, help me decide the IRB / safety considerations. We are generating prompts that ask about dangerous biology. There is a real ethical question about (a) writing these prompts in a public repo, (b) running them through public APIs, (c) what to do if the model actually answers them informatively. We resolve this before drafting prompts because the constraints shape what counts as a valid prompt and a valid control. Address these head-on.

2. Second, help me design the dangerous-prompt set. I do not want a list of bioterror recipes; I want 30 prompts that span a spectrum of dual-use risk so that the cross-prompt structure is itself informative. Discuss the design principles, then I will draft the actual prompts.

3. Third, help me design the matched-benign controls. The matching has to be tight: same surface structure, same biological domain, different intent. Otherwise the circuit signature we find is just "the model recognizes the topic," not "the model recognizes the risk."

Begin with question 1. I want the IRB / safety frame resolved before drafting prompts so the design space is bounded. Be opinionated; do not enumerate options without taking a position.
```

---

## Notes for the session you spawn from this

- **First message etiquette:** the new session's Claude will not know about the cross-domain paper's writing-phase status. The starter prompt above tells it. Trust the starter prompt; you should not have to remind Claude that the cross-domain paper is separate.

- **Working directory for Phase 1:** the new session should work primarily out of `neuronpedia_pipeline/`. New scripts go to `neuronpedia_pipeline/scripts/`. New figures (if any) go to `neuronpedia_pipeline/data/research_program/phase1/` (you may need to create this). New writing goes to `neuronpedia_pipeline/docs/research_program/phase1/` (also create as needed).

- **What to do if the session drifts toward the cross-domain paper:** redirect it. "We are in Phase 1 of the research program, not the cross-domain paper writing." That single sentence should reset it.

- **What to do if the session wants to write code before you've finalized the prompt design:** redirect it. Phase 1's first weeks are pure design work. No traceback runs, no figures, no data collection until the prompt set is finalized and the IRB question is answered.

- **When you finish the kickoff session:** save the outputs (prompt set, design decisions, IRB notes) to `neuronpedia_pipeline/docs/research_program/phase1/`. Update `00_PROGRAM_OVERVIEW.md` if the program scope shifts based on what you learned. Then start the next session.

## Why this prompt is what it is

A few design choices worth flagging so you can edit them if your situation changes:

- I framed Phase 1 as starting with **ethics and prompt design**, not data collection. This is deliberate. The hardest part of dual-use research is not the methodology; it is making sure the prompt set is methodologically clean and ethically defensible. Ethics goes ahead of prompt design because the constraints (public repo, public API, response handling) shape what counts as a valid prompt. Starting with code would waste cycles.

- I told the session to be **opinionated**. Claude tends to enumerate options when asked open-ended design questions. For research design, you want a strong recommendation followed by alternatives, not a balanced list.

- I asked for **three specific questions in sequence**, not "design everything." Scoped questions produce better answers than open-ended kickoffs.

- I included **style rules**. The cross-domain paper's polish phase taught us that catching style issues late is expensive. Better to set the constraint up front.

If any of these decisions look wrong for your situation when you spin up the session, edit the starter prompt before pasting.
