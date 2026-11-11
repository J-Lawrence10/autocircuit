# Writing references for the attribution graph paper

These three papers are reference models for structure, explanation, and claim discipline. Use their writing principles, not their wording or the strength of their causal claims. Local copies were downloaded on 4 October 2026; the original PDFs are unmodified.

## Main structural reference

**Fred Zhang and Neel Nanda. Towards Best Practices of Activation Patching in Language Models: Metrics and Methods. ICLR 2024.**


Source: [ICLR proceedings PDF](https://proceedings.iclr.cc/paper_files/paper/2024/file/06a52a54c8ee03cd86771136bc91eb1f-Paper-Conference.pdf).

Use as our main template: introduce a precise measurement problem, organize experiments around methodological alternatives, and connect each result to its practical interpretation. Particularly useful for our abstract, control experiments, and discussion. Start with the introduction and Section 6, Discussion and Recommendations.

## Concrete examples and progressive explanation

**Jiahai Feng and Jacob Steinhardt. How do Language Models Bind Entities in Context? 2024 revision.**


Source: [arXiv version 2 PDF](https://arxiv.org/pdf/2310.17191v2).

Use its example-first explanation for our country-capital task and answer-mapping controls. Introduce an intuitive case before notation, then build through progressively stronger tests. Read the introduction, preliminaries, and generality/limitations section. Their causal interventions support stronger mechanism claims than our observational overlap study; do not transfer those claims to our paper.

## Validation and failure cases within the main argument

**Kevin Wang, Alexandre Variengien, Arthur Conmy, Buck Shlegeris, and Jacob Steinhardt. Interpretability in the Wild: A Circuit for Indirect Object Identification in GPT-2 Small. ICLR 2023.**


Downloaded source: [arXiv version 1 PDF](https://arxiv.org/pdf/2211.00593v1), the November 2022 preprint of the work subsequently published at ICLR 2023. The [OpenReview conference PDF](https://openreview.net/pdf?id=NpsVSN6o4ul) returned HTTP 403 during download, so the local copy is the explicitly versioned preprint, not the conference PDF.

Use its separation of explanation from validation and its treatment of adversarial/failure examples as supporting tests of the main investigation. Particularly useful for our failure-case section and limitations. Their causal circuit analysis is not a method we have performed merely by comparing graph features.

## How to apply these references

Combine Zhang and Nanda's methodological structure, Feng and Steinhardt's concrete explanations, and Wang and colleagues' validation discipline. For each results subsection, state the question, the comparison, the observation, and the interpretation limit. Keep three-model findings distinct from Qwen3-4B-only follow-ups, and distinguish locally frozen analyses from outcome-informed diagnostics.

These copies are for our reference library. Downloading them does not establish permission to redistribute them with a public data release; check each source's license before doing so. The manuscript and its scientific results are unchanged by adding this folder.
