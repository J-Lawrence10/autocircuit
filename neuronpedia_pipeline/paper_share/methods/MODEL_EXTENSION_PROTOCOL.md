# Prospective Model-Extension Protocol

**Frozen:** 30 August 2026, before any Qwen3-4B or Llama-3.2-1B extension outcome was generated or inspected.  
**Status:** Prospective replication extension to `WHOLE_GRAPH_ANALYSIS_PROTOCOL.md`.  
**Purpose:** Test whether the paper's fact- and prompt-form findings reproduce in a larger Qwen model and a different model family without changing the completed Gemma-2-2B/Qwen3-1.7B confirmatory analysis.

## 1. Frozen cohorts

Two model pipelines are registered:

| Extension ID | Model | Graph backend | Decomposition | Status rule |
|---|---|---|---|---|
| `qwen3-4b` | Qwen3-4B | Neuronpedia `/api/graph/generate` | Neuronpedia default `transcoder-hp` | Generate remotely under the public rate limit. |
| `llama-3.2-1b` | Meta Llama-3.2-1B | local `safety-research/circuit-tracer` | `mntss/transcoder-Llama-3.2-1B` PLTs | Run only with the registered model/decomposition; if local resources are insufficient, record the cohort as blocked rather than substitute a model or decomposition. |

Each model receives the same two frozen designs:

1. **Controlled cohort:** the 120 prompts in `config/paper_control_manifest.csv` (30 facts x target, positive paraphrase, same-template nonce, and paraphrased nonce). The source file SHA-256 at freeze time is `C2C36A46E09A4C7943FF38E537F78CF3E7D4AA27E031B011BE3B6035C6106196`.
2. **Crossed fact-by-format cohort:** the 27 prompts in `VARIED_PROMPTS` in `scripts/stage_2_format_variation_experiment.py` (3 domains x 3 facts x 3 formats). The source file SHA-256 at freeze time is `ABD0FDC0F541AB2E0D2451425D7715E4678DD4D9AC9AFA43D6D5A7ED67C87C58`.

No prompt, expected answer, domain, split, or role may be changed in response to extension outcomes. Technical corrections must be recorded in a dated deviation log.

## 2. Generation and integrity rules

- Archive raw graph JSON and generation metadata before conversion.
- Use `desiredLogitProb=0.99` for Neuronpedia generation.
- Stay below Neuronpedia's 30 requests per 60 minutes limit; resume only missing jobs.
- Preserve model, decomposition/source set, prompt, retrieval URL or local checkpoint revision, generation time, and file SHA-256.
- Fail closed on missing files, ambiguous manifest mappings, orphan endpoints, non-finite weights, or unresolved duplicate node IDs.
- Ambiguous duplicate IDs are excluded with their incident edges for the registered primary representation and reported separately.
- Reconstruction-error nodes are excluded from the primary sparse-feature representation and restored as separate error-family classes in sensitivity analyses.
- Feature identities are never compared directly across models.

## 3. Eligibility

A fact enters the controlled fact-identity analysis only when:

1. all four registered roles are present;
2. both target and positive paraphrase produce the expected top token after whitespace trimming;
3. at least one other eligible factual paraphrase exists in the same domain and split; and
4. the graph passes the registered integrity checks.

Incorrect and ineligible graphs remain in the audit. They are not replaced with new prompts.

## 4. Outcomes and inferential unit

The fact is the inferential unit. For fact `i`, the primary outcome is:

`M_i = Jaccard(target_i, paraphrase_i) - mean Jaccard(target_i, other eligible paraphrases in the same domain and split)`.

The crossed experiment retains the three registered categories: same fact/different format, different fact/same format, and different fact/different format. Fact and format effects are computed relative to the different-fact/different-format baseline without treating pairwise similarities as independent samples.

## 5. Registered tests and gates

For each model separately:

- fact-bootstrap 95% confidence interval with 10,000 resamples;
- exact one-sided sign-flip test on fact-level margins;
- exact within-domain fact-label permutation;
- binary Jaccard and influence-weighted cosine representations;
- graph-size-adjusted HC1 estimate;
- leave-one-fact-out sensitivity;
- error-inclusive binary and weighted sensitivities;
- collision-free subset sensitivity; and
- output-type-matched nonce controls where eligible.

**Controlled replication Gate R1:** held-out pooled mean is positive, the bootstrap interval excludes zero, and the exact one-sided p-value is at most 0.05 after Holm correction across extension models that complete the cohort.

**Domain Gate R2:** at least two domains each contain at least two eligible held-out facts and have positive domain means. A three-domain claim additionally requires positive means in chemistry, geography, and history.

**Specificity Gate R3:** the exact within-domain fact-label permutation is significant at 0.05 after Holm correction across completed extension models.

**Crossed Gate R4:** both the fact effect and format effect are positive with their registered permutation p-values at most 0.05 after Holm correction across the two effects and all completed extension models. The relative magnitude of fact and format effects is descriptive; this protocol does not register a universal claim that one dominates the other.

A model that fails an eligibility, integrity, compute, or completion gate is reported as incomplete or failed. It is not omitted from the extension report.

## 6. Claim boundary

The extension may support broader pipeline or model-family replication only if its corresponding gates pass. It cannot establish causal circuits, prompt invariance, architecture-level mechanisms, or cross-model feature identity. The original confirmatory estimates remain unchanged and are reported separately from this extension.

## 7. Deviations

- **30 August 2026, before extension outcome inspection:** the user directed that models requiring local generation not be run because the available workstation is not suitably provisioned. Llama-3.2-1B is therefore retained as a registered but resource-deferred future cohort. No Llama graph was generated, and no substitute model or decomposition was introduced. The active extension is Qwen3-4B only. Because this decision occurred before any extension outcome was inspected, it does not alter the Qwen3-4B hypotheses, prompts, gates, or analysis rules.
- **30 August 2026, during the first schema smoke check:** Qwen3-4B exports were found to prefix stored prompts with the tokenizer marker `<|endoftext|>`. The existing normalizer already removed Gemma's `<bos>` and earlier Qwen's `<|im_end|>` markers. `<|endoftext|>` was added to the same normalization-only list before inferential analysis. This correction changes neither prompt content nor any numerical graph representation.
