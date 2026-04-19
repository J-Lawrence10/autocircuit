# Supplementary Materials

**Companion to:** Cross-Domain Circuit Analysis of Factual Knowledge Retrieval in LLMs

---

## Table of Contents

- [S1. Extended Results](#s1-extended-results)
  - [S1.1 Category-Specific Features](#s11-category-specific-features)
  - [S1.2 Cross-Category Overlap](#s12-cross-category-overlap)
  - [S1.3 Statistical Significance](#s13-statistical-significance)
  - [S1.4 Path Topology](#s14-path-topology)
  - [S1.5 Community Structure](#s15-community-structure)
  - [S1.6 Activation Profiles](#s16-activation-profiles)
  - [S1.7 Confidence vs Bottleneck Position](#s17-confidence-vs-bottleneck-position)
  - [S1.8 Expanded Correlation Analysis](#s18-expanded-correlation-analysis)
  - [S1.9 ANOVA: Domain Effects on Circuit Metrics](#s19-anova-domain-effects-on-circuit-metrics)
  - [S1.10 Effect Sizes (Cohen's d)](#s110-effect-sizes-cohens-d)
  - [S1.11 Statistical Power](#s111-statistical-power)
  - [S1.12 Domain Overlap Signal-to-Noise Analysis](#s112-domain-overlap-signal-to-noise-analysis)
  - [S1.13 Bottleneck Energy Decomposition](#s113-bottleneck-energy-decomposition)
  - [S1.14 Edge Flow Analysis](#s114-edge-flow-analysis)
  - [S1.15 Feature Co-Activation Patterns](#s115-feature-co-activation-patterns)
  - [S1.16 Output Logit Decomposition](#s116-output-logit-decomposition)
  - [S1.17 Outlier Analysis](#s117-outlier-analysis)
  - [S1.18 Hidden Predictor Discovery](#s118-hidden-predictor-discovery)
  - [S1.19 Multi-Algorithm Validation](#s119-multi-algorithm-validation)
  - [S1.20 Batch Feature Annotation](#s120-batch-feature-annotation)
  - [S1.21 Polysemanticity Analysis](#s121-polysemanticity-analysis)
- [S2. Extended Discussion](#s2-extended-discussion)
  - [S2.1 Pervasive Cross-Model Differences](#s21-pervasive-cross-model-differences)
  - [S2.2 Domain-Specific Circuit Conservation](#s22-domain-specific-circuit-conservation)
  - [S2.3 Algorithm Sensitivity of Community Structure](#s23-algorithm-sensitivity-of-community-structure)
  - [S2.4 Polysemanticity and the Infrastructure Hypothesis](#s24-polysemanticity-and-the-infrastructure-hypothesis)

---

## S1. Extended Results

### S1.1 Category-Specific Features

We also identified features exclusive to one knowledge domain:

| Model | Chemistry-Only | Geography-Only | History-Only |
|-------|---------------|----------------|--------------|
| GEMMA | 107 | 28 | 138 |
| QWEN | 78 | 110 | 167 |

History circuits have the most domain-specific features in both models, consistent with the low within-category Jaccard similarity observed in Section 5.1. Geography has the fewest domain-specific features in GEMMA (28), reflecting the high circuit conservation within the geography domain.

### S1.2 Cross-Category Overlap

Pairwise overlap between categories (features shared as bottlenecks in both domains):

**GEMMA**:
| Pair | Shared Features | Jaccard |
|------|----------------|---------|
| Chemistry vs Geography | 7 | 0.044 |
| Chemistry vs History | 14 | 0.052 |
| Geography vs History | 15 | 0.079 |

**QWEN**:
| Pair | Shared Features | Jaccard |
|------|----------------|---------|
| Chemistry vs Geography | 18 | 0.081 |
| Chemistry vs History | 20 | 0.072 |
| Geography vs History | 25 | 0.081 |

Cross-category overlap is consistently low (Jaccard < 0.1), indicating that despite the existence of universal bottleneck features, the majority of each domain's circuit architecture is domain-specific.

### S1.3 Statistical Significance

We validated the significance of within-domain circuit convergence using permutation tests, bootstrap confidence intervals, and chi-square tests for layer distribution independence.

**Permutation tests** (N=10,000, shuffled category labels): Within-category Jaccard is significantly higher than cross-category Jaccard for both models:

| Model | Within Mean | Cross Mean | Observed Diff | p-value |
|-------|------------|-----------|---------------|---------|
| GEMMA | 0.264 | 0.065 | 0.199 | <0.0001 |
| QWEN | 0.280 | 0.142 | 0.138 | <0.0001 |

Both models achieve p < 0.0001, confirming that domain structure is genuine and not an artifact of random feature overlap. The effect size is larger in GEMMA (0.199 vs 0.138), suggesting GEMMA's circuits are more domain-differentiated despite its smaller architecture.

**Bootstrap 95% confidence intervals** for within-category Jaccard:

| Model | Chemistry | Geography | History |
|-------|-----------|-----------|---------|
| GEMMA | [0.268, 0.311] | [0.373, 0.419] | [0.091, 0.125] |
| QWEN | [0.331, 0.377] | [0.315, 0.354] | [0.138, 0.169] |

The non-overlapping CIs between geography and history in both models confirm that within-domain similarity differences are statistically robust.

**Chi-square tests** for layer distribution independence (contingency table: category x layer group):

| Model | chi-squared | dof | p-value |
|-------|-----|-----|---------|
| GEMMA | 31.51 | 8 | 0.0001 |
| QWEN | 23.94 | 8 | 0.0023 |

Layer distributions are significantly non-independent of category (p < 0.01 for both models), meaning the distribution of bottleneck features across processing stages does differ by knowledge domain, even though the average bottleneck depth does not.

### S1.4 Path Topology

We analyzed the structural properties of traceback paths across domains:

**GEMMA Path Topology**:
| Category | Compression | Score Decay Rate | Branching Factor |
|----------|-------------|-----------------|-----------------|
| Chemistry | 0.593+/-0.072 | 0.91+/-0.19 | 2.93+/-0.42 |
| Geography | 0.569+/-0.042 | 0.90+/-0.12 | 3.10+/-0.18 |
| History | 0.618+/-0.090 | 1.15+/-0.14 | 2.95+/-0.26 |

**QWEN Path Topology**:
| Category | Compression | Score Decay Rate | Branching Factor |
|----------|-------------|-----------------|-----------------|
| Chemistry | 0.537+/-0.066 | 0.59+/-0.11 | 3.03+/-0.44 |
| Geography | 0.525+/-0.053 | 0.87+/-0.12 | 3.10+/-0.21 |
| History | 0.497+/-0.046 | 0.83+/-0.22 | 3.34+/-0.42 |

History circuits exhibit higher score decay rates in GEMMA (1.15 vs ~0.90), indicating faster information concentration along paths. QWEN history paths have the highest branching factor (3.34), suggesting more parallel processing streams. Geography paths show the lowest variance across all metrics, consistent with the high circuit conservation observed in Jaccard analysis.

### S1.5 Community Structure

Louvain community detection reveals that community partitions are more similar within domains than across domains, mirroring the Jaccard results:

| Model | Category | Mean ARI (within) | Mean # Supernodes |
|-------|----------|-------------------|-------------------|
| GEMMA | Chemistry | 0.400 | 12.2 |
| GEMMA | Geography | 0.627 | 11.2 |
| GEMMA | History | 0.285 | 12.1 |
| QWEN | Chemistry | 0.691 | 13.0 |
| QWEN | Geography | 0.752 | 12.9 |
| QWEN | History | 0.366 | 15.4 |

Geography circuits have the highest community structure similarity in both models (ARI = 0.627 GEMMA, 0.752 QWEN). QWEN history circuits have notably more supernodes (15.4 vs ~13 for other categories), suggesting more complex community organization for temporal knowledge.

### S1.6 Activation Profiles

Layer-by-layer activation fingerprints show extremely high within-category cosine similarity (>0.98) across all categories and models:

| Model | Chemistry | Geography | History |
|-------|-----------|-----------|---------|
| GEMMA | 0.988 | 0.989 | 0.980 |
| QWEN | 0.983 | 0.990 | 0.987 |

Cross-category cosine similarity is also high (>0.96), indicating that the overall activation "shape" across layers is largely model-determined. However, peak activation layers differ: GEMMA peaks at L13-15 (mid-network), while QWEN peaks at L35 (near-output). This complements the bottleneck depth finding -- QWEN concentrates both activation energy and bottleneck features near the output.

### S1.7 Confidence vs Bottleneck Position

We correlated model output probability with five bottleneck position metrics per model:

| Model | Metric | Spearman r | p-value |
|-------|--------|-----------|---------|
| GEMMA | Median bottleneck layer | 0.481 | **0.007** |
| GEMMA | Average bottleneck layer | 0.295 | 0.114 |
| GEMMA | Min/Max/Std bottleneck layer | -0.058 to 0.099 | >0.60 |
| QWEN | All bottleneck position metrics | -0.242 to 0.178 | >0.19 |

In GEMMA, **median** (but not mean) bottleneck layer significantly predicts confidence: higher-confidence predictions have bottlenecks positioned deeper in the network. The mean-median discrepancy suggests that the relationship is driven by the typical bottleneck position rather than outliers. QWEN shows no bottleneck-confidence relationship, consistent with its different architectural strategy.

### S1.8 Expanded Correlation Analysis

We correlated output probability against 16 circuit metrics with Bonferroni correction (alpha = 0.003):

**GEMMA** (5/16 significant uncorrected, 1 surviving Bonferroni):
- **Total activation energy**: r = 0.527, p = 0.003 -- **sole Bonferroni survivor**
- Weight kurtosis: r = 0.518, p = 0.003 (marginal)
- Total nodes: r = 0.478, p = 0.008
- Total edges: r = 0.434, p = 0.016
- Num bottlenecks: r = 0.386, p = 0.035

**QWEN** (1/16 significant uncorrected, 0 surviving Bonferroni):
- Top-10% weight share: r = -0.434, p = 0.017 (only uncorrected signal)

Total activation energy is the single strongest predictor of GEMMA prediction confidence, surviving stringent multiple testing correction. This suggests a model where the amount of neural "effort" (total activation across all features) scales with prediction certainty.

### S1.9 ANOVA: Domain Effects on Circuit Metrics

We tested whether 9 circuit metrics differ by knowledge domain using ANOVA (normal data via Shapiro-Wilk) or Kruskal-Wallis (non-normal), with Bonferroni correction (alpha = 0.003):

**Bonferroni-surviving effects (6/18)**:

| Model | Metric | Test | p-value | Effect Size | Category Means |
|-------|--------|------|---------|-------------|----------------|
| GEMMA | Score decay rate | ANOVA | 0.003 | eta-squared = 0.354 | Chem 0.91, Geo 0.90, **Hist 1.15** |
| GEMMA | Total energy | KW | 0.0001 | epsilon-squared = 0.615 | Chem 11654, **Geo 9422**, Hist 11382 |
| GEMMA | Output probability | KW | 0.0001 | epsilon-squared = 0.654 | Chem 0.60, **Geo 0.21**, Hist 0.65 |
| QWEN | Total energy | KW | 0.0001 | epsilon-squared = 0.630 | Chem 4900, Geo 4827, **Hist 6455** |
| QWEN | Output probability | KW | 0.002 | epsilon-squared = 0.406 | **Chem 0.95**, Geo 0.73, Hist 0.83 |
| QWEN | Weight kurtosis | ANOVA | 0.003 | eta-squared = 0.355 | Chem 508, Geo 435, **Hist 658** |

Key patterns: Total energy and output probability consistently differ by domain in both models. GEMMA geography has notably lower confidence (mean 0.21 vs 0.60-0.65 for other domains), while QWEN chemistry has the highest (0.95). History circuits show elevated total energy in QWEN and elevated score decay in GEMMA.

### S1.10 Effect Sizes (Cohen's d)

Cohen's d for pairwise category comparisons reveals the magnitude of domain effects:

**Largest effects (|d| > 2.0)**:
- GEMMA total energy: Chemistry vs Geography d = 4.88, Geography vs History d = -2.78
- GEMMA output probability: Chemistry vs Geography d = 3.90, Geography vs History d = -4.35
- QWEN total energy: Chemistry vs History d = -2.87, Geography vs History d = -2.95
- QWEN score decay rate: Chemistry vs Geography d = -2.35
- QWEN output probability: Chemistry vs Geography d = 2.15

Geography stands out as the most distinctive domain in GEMMA (extreme d-values for energy and probability), while History is most distinctive in QWEN (elevated energy and kurtosis).

### S1.11 Statistical Power

At n = 30 per model (10 per category), our analyses have the following power characteristics:
- **Correlation**: ~80% power for |r| >= 0.45 at alpha = 0.05; after Bonferroni (alpha = 0.003), only |r| >= 0.60 is reliably detectable
- **ANOVA** (n = 10/group): ~80% power for large effects (f >= 0.40)
- **Regression** (9 predictors, n = 30): Only 21 residual df; reduced models with 3 predictors (26 df) are preferred
- **Mann-Whitney** (n1 = n2 = 30): ~80% power for medium-to-large effects

These constraints mean that medium-sized effects (|r| = 0.3-0.45, Cohen's d = 0.5-0.8) may exist but remain undetectable. Larger datasets would be needed to confirm or reject these.

### S1.12 Domain Overlap Signal-to-Noise Analysis

We computed a per-layer signal-to-noise ratio (SNR) comparing cross-domain energy differences to within-domain variability. At each layer: SNR = max(category_means) - min(category_means) / mean(category_stds).

- **GEMMA**: Only 2/26 layers (8%) have SNR < 1, meaning at 92% of layers, cross-domain differences exceed within-domain variability.
- **QWEN**: 11/36 layers (31%) have SNR < 1, showing QWEN domains are less distinguishable.

However, a permutation test (N = 5000, shuffled category labels) shows that the observed cross-domain differences are significantly larger than chance (p < 0.001 for both models). This creates a nuanced picture: **domains produce statistically real but architecturally small energy profile differences**. The permutation test confirms the domain signal is genuine, but the cosine similarity analysis (Section 5.13.1) shows it accounts for only ~2% of profile variance.

### S1.13 Bottleneck Energy Decomposition

We decomposed total circuit energy into energy at bottleneck layers (L5-7 for GEMMA, L22-25 for QWEN) vs non-bottleneck layers, testing whether concentrated bottleneck energy predicts confidence.

- **GEMMA**: Bottleneck energy fraction vs confidence: r = 0.256, p = 0.173 (not significant)
- **QWEN**: Bottleneck energy fraction vs confidence: r = -0.293, p = 0.117 (not significant)

This confirms and extends the null result from Section 5.12.7: it is not energy at the bottleneck specifically, nor the overall convergence quality, that predicts confidence -- it is total distributed energy across all layers.

### S1.14 Edge Flow Analysis

Beyond energy profiles, we analyzed the *wiring topology* of all 60 circuits -- specifically, the layer-to-layer edge weight patterns (Fig 30).

**Skip connections dominate.** In GEMMA, 80.1% of edges are skip connections (spanning 2+ layers), carrying 77.2% of total edge weight. QWEN shows even higher skip rates: 84.8% of edges, 78.3% of weight. The average skip span is 8.6 layers (GEMMA) and 9.1 layers (QWEN) -- information routinely bypasses 8-9 intermediate layers.

**Wiring topology is architecture-invariant.** We compared forward-flow-ratio profiles across domains within each model using cosine similarity. Cross-category similarity was 0.995 (GEMMA) and 0.995 (QWEN), with the within-category split-half gap below 0.005 for both models. This means edge flow patterns are as architecture-determined as energy profiles, confirming that wiring topology reflects model structure rather than knowledge domain (Fig 31).

### S1.15 Feature Co-Activation Patterns

We examined which bottleneck features co-occur across circuits, testing whether universal features form functional modules (Fig 32).

Of 244 cross-circuit features in the bottleneck library, 235 appeared in 2+ of our 60 circuits. Computing pairwise Jaccard similarity across all 27,495 feature pairs revealed:

- **Same-layer co-activation (J=0.292) is 1.9x stronger than cross-layer (J=0.153).** Features within the same layer co-activate more frequently, suggesting within-layer functional modules rather than cross-layer chains.
- **Perfect co-activation pairs exist** (Jaccard=1.000), indicating features that always fire together across circuits.
- **Hierarchical clustering** identified 5 distinct feature clusters with characteristic layer distributions (Fig 33), suggesting that bottleneck features organize into specialized processing groups.

### S1.16 Output Logit Decomposition

We decomposed each circuit's edge weights into bottleneck-passing (edges touching GEMMA L5-7 or QWEN L22-25) versus non-bottleneck contributions, testing whether bottleneck contribution predicts confidence (Fig 34-35).

**GEMMA reveals a dual signal:**
- Path-level bottleneck ratio positively correlates with confidence (r=0.415, p=0.016) -- critical paths that route more through bottleneck layers yield higher confidence.
- All-edges bottleneck ratio negatively correlates with confidence (r=-0.694, p<0.0001) -- circuits where a larger *overall* fraction of weight passes through bottleneck layers have lower confidence.

This reconciles the "bottleneck tax" (Section 5.12.7) with evidence accumulation: bottleneck layers are critical routing hubs on the most important paths, but over-reliance on bottleneck processing across the full circuit imposes an information compression cost. The finding that critical paths and bulk flow show opposite correlations is a novel structural insight.

**QWEN** shows no significant path-level correlation (r=-0.261, p=0.152), but total energy negatively predicts confidence (r=-0.438, p=0.010), consistent with simpler circuits yielding higher confidence.

### S1.17 Outlier Analysis

We fit the GEMMA 3-predictor regression model (total_energy, weight_kurtosis, total_nodes -> output_probability) and computed Cook's distance to identify influential outliers (Fig 36).

The model replicates with R-squared=0.489, confirming the robust explanatory power of circuit energetics. Only 2 of 30 GEMMA circuits exceed the Cook's distance threshold (4/n=0.133), indicating good model fit with few exceptions. Residual analysis by category reveals geography circuits are slightly over-predicted (mean residual -0.096) while history circuits are under-predicted (+0.074), suggesting domain-specific confidence patterns not fully captured by structural predictors alone.

The QWEN regression (same predictors) yields R-squared=0.024, confirming that GEMMA's predictive structure does not transfer to QWEN -- different architectures require different predictive models, reinforcing the architecture-over-domain thesis.

### S1.18 Hidden Predictor Discovery

We systematically analyzed 9 data table columns excluded from prior analyses, uncovering several significant relationships (Fig 37-38).

**Weight variance predicts confidence in opposite directions by model.** GEMMA's weight coefficient of variation (CV) positively correlates with confidence (r=0.423, p<0.05) while QWEN's CV shows a strong negative correlation (r=-0.460, p<0.05). High weight variance in GEMMA indicates concentrated processing through dominant pathways (beneficial), while in QWEN it indicates chaotic, unconverged flow (harmful). QWEN's weight standard deviation also negatively predicts confidence (r=-0.372, p<0.05).

**Pareto edge efficiency reveals model-specific bottleneck signatures.** The fraction of edges carrying 50% of total weight shows distinct patterns: GEMMA averages 12.2% efficiency (top edges highly concentrated) while QWEN averages 9.2% (more distributed). QWEN's edge efficiency ratio significantly predicts confidence (r=0.448, p<0.05), suggesting that efficient circuits with fewer dominant edges produce better outputs.

**Weight median is the strongest unused predictor.** Previously overlooked, weight median shows the strongest single correlation: r=-0.630 (p<0.001) for GEMMA and r=+0.449 (p<0.01) for QWEN. The sign reversal mirrors the CV finding -- GEMMA benefits from skewed weight distributions (high activation through few pathways) while QWEN benefits from elevated baseline weights (broad activation).

**Category interactions dramatically improve prediction.** Adding category dummy variables increases R-squared by +0.376 in GEMMA (0.489 to 0.865) and +0.505 in QWEN (0.024 to 0.529). Full interaction terms push GEMMA to R-squared=0.891 and QWEN to R-squared=0.734. This reveals that the domain effect on confidence operates differently within each category -- the same structural predictor has different meaning depending on the knowledge domain.

### S1.19 Multi-Algorithm Validation

We tested the robustness of circuit community structure by running 4 independent algorithms (Louvain, Leiden, Greedy Modularity, Label Propagation) on all 60 circuits and measuring pairwise Jaccard agreement (Fig 39-40).

**Community structure is algorithm-dependent.** The mean Jaccard agreement across all circuits is 0.363, with 93% classified as WEAK (<0.5) and 0% as VALID (>0.7). This indicates that the community partitions reported in earlier analyses are not robust to algorithm choice.

**Two algorithm families emerge.** Louvain and Greedy Modularity agree strongly (mean Jaccard=0.770), consistent with their shared modularity-optimization framework. Leiden disagrees with all other methods (Jaccard<0.05 with Greedy and Label Propagation), likely because its CPM resolution parameter (0.01) is poorly tuned for sparse attribution graphs. Label Propagation produces intermediate agreement (0.42-0.45 with Louvain/Greedy).

**Model and domain effects persist.** GEMMA circuits show slightly higher agreement (0.400) than QWEN (0.327), and chemistry shows the highest agreement (0.414) compared to history (0.304). The top-5 highest-agreement circuits are all chemistry prompts, suggesting that simpler factual lookups (element symbols) produce more structurally robust communities.

**Modularity is high regardless.** Despite poor cross-algorithm agreement, average modularity scores are substantial: GEMMA Louvain=0.511, Greedy=0.507; QWEN Louvain=0.422, Greedy=0.409. The community structure is real (high modularity) but its specific partition boundaries are degenerate -- multiple equally valid community assignments exist.

### S1.20 Batch Feature Annotation

We queried the Neuronpedia feature explanation API for all unannotated GEMMA bottleneck features, successfully retrieving explanations for 84 features (100% API success rate). This brought annotation coverage from 46/244 (18.9%) to 130/244 (53.3%). The remaining 114 unannotated features are exclusively QWEN, for which the Neuronpedia feature API is not yet available.

### S1.21 Polysemanticity Analysis

Using the 130 annotated features, we classified each feature into semantic categories using pattern-based analysis of Neuronpedia explanations (Fig 47-48).

**Most bottleneck features are monosemantic.** Of 130 annotated features, 114 (87.7%) mapped to a single semantic category and 16 (12.3%) were polysemantic (2+ categories). This is lower than typical SAE polysemanticity rates reported in the literature, consistent with bottleneck features serving more specialized routing functions.

**Semantic distribution reveals infrastructure dominance.** The most common categories are OTHER (26%), CODE (20%), and LANGUAGE (20%), followed by DOMAIN_SPECIFIC (13%), SCIENCE (11%), MATH (8%), ENTITIES (8%), CONCEPTS (7%), and MULTILINGUAL (2%). The preponderance of CODE and LANGUAGE features -- formatting, syntax, and linguistic structure -- supports the hypothesis that bottleneck features serve as routing infrastructure rather than knowledge stores (Section 6.2).

**Polysemanticity increases with layer depth.** Early layers (L0-L3) show 0-14% polysemanticity, while late layers (L11-L12, L21, L24) show 50-100%. Layers L11 (50%), L12 (75%), and L24 (50%) are outliers. This aligns with the superposition hypothesis: deeper layers compress more diverse information into shared representations. The transition occurs around L10-L12, coinciding with GEMMA's post-bottleneck processing region.

**Cross-domain features are pervasive.** 70 features (53.8%) appear in circuits from 2+ knowledge domains, and 23 (17.7%) appear in all 3 domains. The 23 all-domain features include both annotated features (L3_F5150441: "HTML formatting tags"; L0_F1813559: "code/file keywords") and 15 unannotated QWEN features. Cross-domain features classified as CODE (8) and LANGUAGE (6) dominate, reinforcing the infrastructure interpretation.

---

## S2. Extended Discussion

### S2.1 Pervasive Cross-Model Differences

The Mann-Whitney analysis reveals that 13/16 circuit metrics differ significantly between GEMMA and QWEN, with peak activation layer and bottleneck layer showing perfect rank separation (r = 1.0). Only branching factor, total edges, and community entropy are architecture-invariant. The three shared properties may represent computational constants of factual retrieval: regardless of where bottlenecks are placed or how much activation is recruited, the branching structure of information flow and the total volume of edges appear fixed by the task rather than the architecture.

### S2.2 Domain-Specific Circuit Conservation

The varying degree of within-domain circuit similarity (geography > chemistry > history) reflects the structural similarity of the prompts within each domain:
- Geography prompts are nearly identical in structure ("The capital of X is"), producing highly conserved circuits with the highest Adjusted Rand Index for community structure (ARI = 0.627 GEMMA, 0.752 QWEN).
- Chemistry prompts share structure but vary in the element name, producing moderate conservation.
- History prompts vary more in structure and subject matter, producing the most diverse circuits. QWEN history circuits also have more supernodes (15.4 vs ~13), suggesting temporal knowledge requires more complex community organization.

The permutation tests (p < 0.0001 for both models) confirm that this within-domain convergence is statistically genuine and not an artifact of random feature overlap. The chi-square tests further show that the layer distribution of bottleneck features is significantly non-independent of category, even though the average bottleneck depth is consistent within each architecture.

ANOVA/Kruskal-Wallis tests with Bonferroni correction reveal that the most robust domain effects are in total energy and output probability (both surviving correction in both models), with large effect sizes (epsilon-squared = 0.62-0.65). Cohen's d analysis shows extreme pairwise effects: GEMMA geography is an energetic outlier (d = 4.88 vs chemistry), while QWEN history is an outlier in total energy (d = -2.95 vs geography) and weight kurtosis (d = -1.61). These domain-specific signatures are superimposed on the architecture-determined baseline.

### S2.3 Algorithm Sensitivity of Community Structure

The multi-algorithm validation (Section 5.19) demonstrates that community partitions in attribution graphs are not robust -- different algorithms produce substantially different assignments (mean Jaccard=0.363). However, the high modularity scores (>0.4 for Louvain and Greedy Modularity) indicate that the community *structure* is real, even if its specific *boundaries* are degenerate.

This has methodological implications: any analysis that depends on specific community assignments (e.g., supernode construction, community-level statistics) should be interpreted with caution. Future work should report results across multiple algorithms or focus on algorithm-invariant properties.

### S2.4 Polysemanticity and the Infrastructure Hypothesis

The polysemanticity analysis (Section 5.24) provides the strongest evidence yet for the "infrastructure hypothesis" -- that bottleneck features serve as general-purpose routing mechanisms rather than domain-specific knowledge stores. Three converging lines of evidence support this:

1. **Semantic categories are infrastructure-dominated**: CODE (20%) and LANGUAGE (20%) features -- encoding formatting, syntax, and linguistic patterns -- outnumber domain-specific features (13%).
2. **Cross-domain features are pervasive**: 54% of features appear in 2+ domains and 18% appear in all 3 domains, inconsistent with domain-specific knowledge encoding.
3. **Polysemanticity increases with depth**: The sharp increase in polysemanticity at L10-L12 (50-75%) coincides with the transition from GEMMA's bottleneck region (L5-7) to post-bottleneck processing, suggesting that deeper layers compress increasingly diverse functions into shared feature representations.

The low overall polysemanticity rate (12.3%) compared to typical SAE features suggests that bottleneck features are more specialized than the average SAE feature -- they are selected by the circuit architecture for specific routing functions, even if those functions span multiple knowledge domains.
