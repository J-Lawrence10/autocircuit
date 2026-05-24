# Research Program Overview

**Author:** Joseph Lawrence
**PI:** Konstantinos Krampis (CUNY)
**Date drafted:** 2026-05-24
**Status:** Design phase, awaiting Phase 1 kickoff

---

## 1. Research identity

Not "Joseph the interpretability researcher." Not "Joseph the bio guy." The identity this program builds is:

**Joseph, who studies the cross-model phylogeny of capabilities, with particular attention to the high-stakes ones (biosafety, in-context learning, model self-representation).**

This identity has a real moat. Most mechanistic interpretability researchers work on a single model at a time. Most cross-model researchers are not safety-focused. Almost none have a biology PhD that lets them write credible dual-use bio prompts without a reviewer questioning the design. The intersection is mostly empty, and the bio framing genuinely changes which research questions are askable.

## 2. The five-phase arc

Each phase is a distinct paper. Phases are ordered so each one supports the next.

### Phase 1 (months 0-6): BS1, Dual-use bio detection at the circuit level

**Question:** Do models concentrate activation differently when asked dangerous biology questions versus superficially similar benign ones?

**Concrete design:**
- 30 dangerous-but-realistic biology prompts (Joseph designs the prompt set; the bio PhD is load-bearing here)
- 30 superficially similar benign prompts as matched controls (e.g., "explain the lethal mechanism of botulinum toxin" vs "explain the therapeutic mechanism of botulinum toxin")
- Apply traceback graphing (the cross-domain paper's methodology) to all 60 prompts on Gemma-2-2B and Qwen3-4B
- Test whether the bottleneck tax holds, where the bottleneck sits, and whether circuit signatures separate dangerous from benign

**Why first:** Highest readiness. Reuses existing methodology directly. Bio differentiation establishes credibility. AISIs are actively funding this exact area in 2026, so the grant application is almost as important as the paper. Ships in 6 months.

**Target venues:** NeurIPS or ICLR mechanistic interpretability track. AISI workshop. Grant outcome: AISI bridge grant or Anthropic responsible scaling collaboration.

**Risks:** (1) Both prompt sets might use the same circuits, in which case the result is "no circuit-level signal for dual-use detection." That is still publishable, just less splashy. (2) Gemma-2-2B may be too small to distinguish; might need to escalate to Gemma-2-9B if so.

### Phase 2 (months 6-18): T4-A, Circuit phylogeny across model family trees

**Question:** Treat each model in a family as a species. Build a phylogenetic tree of circuit similarity across the open-weights model family tree. Where do new capabilities introduce genuinely new circuits versus adapt existing ones? Which circuits are conserved across all lineages (the "highly conserved genes" of LLMs) and which are species-specific?

**Concrete design:**
- Three lineages: Llama (1, 2, 3, Code Llama, 3.1), Qwen (1, 2, 3), Gemma (1, 2)
- Apply cross-model comparison methodology to identify conserved versus divergent circuits
- Build a literal phylogenetic tree using circuit-similarity as the distance metric
- Identify which capabilities have "convergent" circuit structures (same solution arose independently) versus "homologous" ones (inherited from a shared ancestor)

**Why this becomes the spine:** Once you have cross-model phylogeny infrastructure, every subsequent project just asks "what about THIS capability across the tree?" Phase 3 and Phase 4 reuse the infrastructure directly.

**Target venues:** Nature Machine Intelligence or Distill perspective. NeurIPS / ICML methods spinoff for the cross-model comparison technique itself.

**Risks:** This is the riskiest project on the list. Logistically heavy: 10+ models, SAE feature space harmonization, compute budget. Needs a collaborator by month 9. Mitigation: Phase 1's success establishes credibility that helps recruit a Phase 2 collaborator.

**Bio framing role:** Load-bearing. The phylogenetic framing is the contribution. Most mech interp researchers do not naturally arrive at this lens.

### Phase 3 (months 18-30): WC1, In-context learning at the circuit level, using Phase 2's phylogeny framework

**Question:** When did the in-context learning (ICL) circuit emerge in each lineage? Is ICL convergent (same circuit appears independently in Llama and Qwen) or contingent (different circuits doing similar functional work)?

**Concrete design:**
- Apply the phylogeny framework to ICL specifically
- Use Pythia's published intermediate training checkpoints (154 per model size, 8 sizes) to also trace ICL emergence within a single lineage's training trajectory
- Compare emergence patterns across model families

**Why this slot:** ICL is the biggest unsolved capability mystery in LLMs, and almost no one has approached it cross-architecturally. Phase 2 gives you the infrastructure. This is the Anthropic-class result.

**Target venues:** NeurIPS main track. Anthropic interpretability team would actively want this work.

### Phase 4 (months 30-42): WC2, Mechanistic self-model and introspection across model families

**Question:** When the model is asked "are you certain," "what's your name," "what kind of system are you," which circuits fire? Does a "self-model" exist across all architectures, or only in instruction-tuned variants? Does it correlate with capability or with training stage?

**Concrete design:**
- Curated set of introspection prompts (capabilities, identity, uncertainty, self-reflection)
- Apply Phase 2's phylogeny lens
- Connect to the bottleneck tax: does the model's expressed uncertainty correlate with circuit-level "bottleneck energy"?

**Why this slot:** By this point the program has cross-model methodology, a bio-safety paper, a phylogeny paper, and an ICL paper. Adding the self-model paper closes a philosophy-adjacent loop that gets press attention without compromising research credibility.

**Target venues:** Nature Machine Intelligence. Also good fit for cognitive-science venues if the analysis aligns to specific cog-sci frameworks.

### Phase 5 (months 42+, optional): BS3, Bio taxonomy alignment with model representations

**Question:** How does the model organize biological knowledge internally? Use SAE features to build the model's implicit biological taxonomy. Compare to gene ontology, Linnaean classification, MeSH terms.

**Concrete design:**
- Catalog SAE features that activate on biology-domain prompts
- Cluster features by activation co-occurrence
- Compare cluster structure to formal biological taxonomies
- Identify where the model carves nature at biological joints versus non-biological ones

**Why this slot:** Comes back to bio for the capstone. By month 42+, Joseph has the credibility to publish "how does the model organize biology" at Nature Machine Intelligence without a reviewer asking "who is this person." It is the project that uses bio depth most heavily and lands best after the research identity is established.

**Optional because:** A program does not need a fifth paper if the first four define the identity. Phase 5 is "if the program is going well and you want a capstone."

## 3. What this program deliberately excludes

Three things that are tempting but should not be in the program:

1. **The original safety arc (B1 → A1, refusal bottleneck tax → sandbagging detection).** Tempting because it ships fast and reuses existing methodology. Excluded because it does not use Joseph's unique advantages. Other mech interp researchers can do this work. If a collaborator wants to pick it up as a parallel paper, great. But it is not Joseph's most differentiated move.

2. **CircuitBench (T1, the interpretability evaluation benchmark).** Tempting because tools have the highest citation leverage. Excluded because it pulls Joseph away from research toward tool-building, and the program above already builds methodology (Phase 2's phylogeny framework) that other labs can adopt without Joseph needing to ship a pip-installable package.

3. **Mechanistic deception detection on intentionally trained sleeper agents.** Tempting because it is Anthropic-coded. Excluded because (a) Gemma-2-2B is probably too small for spontaneous deception, (b) training sleeper agents requires capabilities Joseph's lab does not have today, (c) the WC2 self-model paper covers adjacent territory with less risk.

These exclusions are not "bad ideas." They are "good ideas that do not fit this program."

## 4. Collaborators to identify

- **By month 6 (Phase 1 ship):** None strictly required. Joseph can run BS1 solo on existing infrastructure.
- **By month 9 (Phase 2 ramp-up):** One collaborator with model-access infrastructure and SAE training experience. Likely candidates: Anthropic's open-source SAE team (Cunningham, Bricken), EleutherAI's interpretability group, or a CUNY lab-mate (Olalekan, Anish) who wants to co-author Phase 2.
- **By month 18 (Phase 3 kickoff):** One collaborator with Pythia checkpoint analysis experience, ideally someone who has previously published on emergence dynamics.
- **By Phase 4:** A cognitive science or philosophy collaborator if the self-model paper benefits from interdisciplinary framing.

## 5. Required resources and risks

| Phase | Compute | Model access | Other | Risk |
|-------|---------|--------------|-------|------|
| 1 (BS1) | Lab hardware fine | Gemma-2-2B + Qwen3-4B (already have) | Bio prompt design (Joseph) | Low: methodology is proven |
| 2 (T4-A) | Significant: 10+ models | Open-weights models, full SAE access | Collaborator with SAE infrastructure | High: logistically the hardest project |
| 3 (WC1) | Significant: many Pythia checkpoints | Pythia 8 sizes × 154 checkpoints (public) | Phase 2 infrastructure | Medium: depends on Phase 2 finishing |
| 4 (WC2) | Moderate | Same as Phase 2 + 3 | Philosophy of mind background reading | Medium: framing is harder than data |
| 5 (BS3, optional) | Moderate | Same | Bio taxonomy databases (free, public) | Low: capstone, low pressure |

## 6. What this program does NOT solve

Two limitations to be honest about up front:

1. **It does not address Anthropic's frontier models.** The whole program runs on open weights. If "interpretability of GPT-4-class models" is the prize, this program does not get there directly. The bet is that cross-model phylogeny on smaller models produces methodology that transfers, and Anthropic will care because the methodology transfers, not because Phase 1 itself touched their models.

2. **It does not include any agentic AI safety work.** As models go agentic (tool use, web browsing, code execution), interpretability of agent failures becomes a major gap. This program does not address it. If agentic safety becomes the dominant 2027 research direction, a Phase 6 or a parallel track might be warranted.

## 7. What success looks like at each milestone

- **End of Phase 1 (month 6):** One paper at NeurIPS interpretability track. AISI grant application submitted. Bio-safety credibility established. Anthropic responsible scaling team has heard your name.

- **End of Phase 2 (month 18):** Nature Machine Intelligence paper on circuit phylogeny. Methodology being adopted by 1-2 other labs. Joseph is "the cross-model phylogeny person" in mech interp Twitter / Discord conversations.

- **End of Phase 3 (month 30):** NeurIPS main track paper on ICL phylogeny. Anthropic / DeepMind safety teams citing the work. Joseph is on the shortlist for senior research scientist roles.

- **End of Phase 4 (month 42):** Press coverage of the self-model paper. Joseph has spoken at one of the major AI conferences. Permanent research position offer in hand.

- **End of Phase 5 (capstone):** Nature Machine Intelligence paper closes the program with the deepest use of Joseph's bio expertise.

## 8. Next concrete step

Start Phase 1 (BS1, dual-use bio detection) in a fresh session using `01_phase1_BS1_starter_prompt.md` as the kickoff. The cross-domain paper continues on its own track in parallel; do not stop work on it.
