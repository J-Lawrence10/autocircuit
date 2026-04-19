# Semantic Taxonomy Methodology

## How We Determine Feature Categories

### Overview

The semantic taxonomy categorizes features based on **what they represent** rather than where they occur. This enables us to track information flow and understand thought progression in human-interpretable terms.

---

## Core Question

**"Given a feature's activation examples, what TYPE of information does it encode?"**

Not: "What layer is it in?" (that's architecture)
Not: "How strongly does it activate?" (that's magnitude)
But: "What SEMANTIC or SYNTACTIC pattern does it detect?"

---

## Primary Categories (3 Main Types)

### 1. **SYNTAX Features**

**Definition**: Features that fire on structural or formatting patterns, NOT semantic meaning

**Indicators**:
- Punctuation: `(`, `)`, `,`, `.`, `;`, `:`
- Code syntax: `class`, `def`, `import`, `return`, `{`, `}`
- Special tokens: `▁`, `<bos>`, `<eos>`, `\n`, `\t`
- Formatting: Indentation, spacing, line breaks
- Pattern repetition: `...`, `"""`, `'''`

**Examples**:
- L0_F5150441: Activates on `(`, `)`, `[`, `]` → SYNTAX (bracket matching)
- L4_F80651345: Activates on `;`, `{`, `}` → SYNTAX (code delimiters)

**Key Test**: Would this feature activate identically on semantically opposite sentences if they have same structure?
- "Paris is the capital" vs "Paris is not the capital" → If yes, it's SYNTAX

---

### 2. **SEMANTICS Features**

**Definition**: Features that fire on MEANING - concepts, entities, facts

**Sub-categories**:

**A. Geographic/Spatial**
- Countries: "France", "Japan", "Mexico"
- Cities: "Paris", "Tokyo", "Austin"
- Regions: "Europe", "Asia", "South"
- Spatial relations: "north", "south", "capital", "border"

**B. Temporal**
- Time: "yesterday", "tomorrow", "2024"
- Sequence: "before", "after", "next"
- Duration: "hour", "day", "year"

**C. Entities**
- People: "John", "Smith", "president"
- Organizations: "Microsoft", "UN", "Congress"
- Objects: "car", "building", "airplane"

**D. Abstract Concepts**
- Ideas: "freedom", "justice", "beauty"
- Relations: "cause", "effect", "similar"
- Properties: "large", "fast", "important"

**Examples**:
- L10_F100614194: Activates on "France", "Paris", "London" → SEMANTICS (geographic)
- L15_F376262: Activates on "president", "governor", "leader" → SEMANTICS (entity/role)

**Key Test**: Would changing the structure but keeping the meaning activate this feature?
- "Paris is the capital" vs "The capital city is Paris" → If yes, it's SEMANTICS

---

### 3. **POLYSEMANTIC Features**

**Definition**: Features that fire on MULTIPLE unrelated patterns (syntax AND semantics, or multiple semantic domains)

**Why this happens**:
- Feature scarcity: Not enough features to represent all patterns distinctly
- Emergent behavior: Model learned to compress multiple patterns into one feature
- Superposition: Features represent linear combinations of concepts

**Indicators**:
- Activates on both code syntax AND natural language concepts
- Activates on geographically AND temporally related terms
- Mixes entity types (people + places + objects)

**Examples**:
- L5_F7993995: Activates on "capital", "}", "president", ";" → POLYSEMANTIC (mixed)
- L8_F39331: Activates on "France", "(", "city", ")" → POLYSEMANTIC (geo + syntax)

**Key Test**: Can you explain activation pattern with a single coherent semantic concept?
- If NO (requires 2+ unrelated concepts) → POLYSEMANTIC

---

## Decision Tree for Classification

```
START: Look at top 5-10 activation examples

Q1: Are >70% of examples punctuation/code/formatting?
    YES → SYNTAX
    NO → Continue to Q2

Q2: Are >70% of examples meaningful words with coherent semantic theme?
    YES → SEMANTICS (+ identify sub-category)
    NO → Continue to Q3

Q3: Is there a mix of syntax patterns AND semantic concepts?
    YES → POLYSEMANTIC
    NO → Continue to Q4

Q4: Is there a mix of MULTIPLE unrelated semantic domains?
    YES → POLYSEMANTIC
    NO → Default to SEMANTICS (if mostly meaningful) or SYNTAX (if mostly structural)
```

---

## Validation Criteria

### How do we know our categorization is correct?

**1. Inter-Rater Reliability**
- Have 2-3 people independently categorize the same 50 features
- Calculate Cohen's Kappa or Fleiss' Kappa
- Target: κ > 0.7 (substantial agreement)

**2. Consistency Check**
- Re-categorize the same features 1 week later
- Measure self-consistency
- Target: >90% same category on re-review

**3. Predictive Validity**
- Hypothesis: SEMANTICS features in early layers should correlate with factual accuracy
- Test: Do prompts that preserve SEMANTICS features through bottleneck get correct answers?
- Measure: Correlation between semantic preservation and accuracy

**4. Ground Truth Validation** (if available)
- Compare to known interpretable features from prior research
- Check against SAE (Sparse Autoencoder) literature
- Verify against Neuronpedia community annotations

---

## Practical Annotation Process

### Step 1: Initial Automated Pass
```python
# Use query_feature_semantics.py with preliminary categorization
python query_feature_semantics.py --feature L5_F7993995

# Output includes:
# - Activation examples
# - Preliminary category (automated)
# - Needs manual review: YES/NO
```

### Step 2: Manual Review Spreadsheet

Create annotation file: `semantic_taxonomy_annotations.csv`

| Feature | Layer | Examples | Auto_Category | Manual_Category | Confidence | Notes |
|---------|-------|----------|---------------|-----------------|------------|-------|
| L5_F7993995 | 5 | "capital", "}", "president" | POLYSEMANTIC | POLYSEMANTIC | HIGH | Mixes geo + syntax |
| L10_F100614194 | 10 | "France", "Paris", "London" | SEMANTICS | SEMANTICS:GEO | HIGH | Clear geographic |

**Columns**:
- **Feature**: Feature ID
- **Layer**: Layer number
- **Examples**: Top 3-5 activation examples (from API)
- **Auto_Category**: Automated preliminary categorization
- **Manual_Category**: Human-verified category (with sub-category if applicable)
- **Confidence**: LOW/MEDIUM/HIGH (how certain are you?)
- **Notes**: Why you categorized this way, edge cases, ambiguities

### Step 3: Review Session
- Annotate 20-30 features per session (15-30 minutes)
- Start with high-confidence obvious cases
- Flag ambiguous cases for group discussion
- Document decision rules for edge cases

### Step 4: Consensus Resolution
- For features with disagreement, discuss as group
- Document reasoning for final category choice
- Update decision tree if needed
- Build "edge case" reference guide

---

## Edge Cases & How to Handle Them

### Edge Case 1: Feature activates on one word with multiple meanings
**Example**: "bank" (financial institution vs river edge)

**Solution**: Look at OTHER activation examples
- If activates on "loan", "money", "account" → SEMANTICS:FINANCIAL
- If activates on "river", "shore", "water" → SEMANTICS:GEOGRAPHIC
- If activates on BOTH contexts → POLYSEMANTIC

### Edge Case 2: Semantic concept that's also grammatical
**Example**: "the", "a", "is" (semantically empty but grammatically essential)

**Solution**: Categorize as **SYNTAX** because primary function is structural, not semantic

### Edge Case 3: Named entities vs common nouns
**Example**: "Paris" (city name) vs "paris" (lowercase, different meaning?)

**Solution**: Look at context in activation examples
- If consistently capitalized + other city names → SEMANTICS:ENTITY (proper noun)
- If mixed case + generic usage → SEMANTICS:CONCEPT (common noun)

### Edge Case 4: Numbers
**Example**: "100", "25", "2024"

**Solution**: Depends on context
- If activates on any numbers (1, 2, 3, 100, 999) → SYNTAX (digit detection)
- If activates on specific values (100, 212, 373) → SEMANTICS:NUMERIC (meaningful quantities like boiling point)
- If activates on year-like patterns (1980, 2024, 2030) → SEMANTICS:TEMPORAL

### Edge Case 5: Code identifiers with semantic meaning
**Example**: "calculate_area", "user_name", "max_speed"

**Solution**: Check if it fires on structure or meaning
- Fires on "calculate_*", "user_*", "*_name" (pattern) → SYNTAX
- Fires specifically on "calculate_area" + other area-related terms → SEMANTICS

---

## Quality Assurance Metrics

### Target Metrics for Phase 1 Taxonomy

**Coverage**:
- ✅ Annotate top 100 features (by activation strength)
- ✅ Include features from all layers (L0-L25)
- ✅ Ensure bottleneck features (L5_F7993995) are included

**Distribution** (Expected):
- SYNTAX: 30-40% (early layers over-represented)
- SEMANTICS: 40-50% (middle-late layers)
- POLYSEMANTIC: 10-20% (sign of superposition)

**Inter-Rater Reliability**:
- κ > 0.7 (substantial agreement)
- >85% exact category match
- >95% agreement on broad category (syntax vs semantics)

**Time Investment**:
- Initial 100 features: 4-6 hours total
- Re-validation: 2 hours
- Consensus resolution: 1-2 hours
- **Total: ~8-10 hours for robust taxonomy**

---

## Using the Taxonomy

### Once taxonomy is built, we can:

**1. Track Semantic Flow**
```python
# Count semantic vs syntax features per layer
L0: SYNTAX=80%, SEMANTICS=15%, POLY=5%  # Input: mostly structure
L5: SYNTAX=60%, SEMANTICS=30%, POLY=10% # Bottleneck: filtering semantics
L10: SYNTAX=30%, SEMANTICS=60%, POLY=10% # Post-bottleneck: syntax dominated
L25: SYNTAX=20%, SEMANTICS=70%, POLY=10% # Output: semantic concepts
```

**2. Identify Bottleneck Behavior**
```python
# What types of features survive vs get blocked?
Pre-bottleneck (L0-L4): 50 SEMANTICS:GEO features active
Bottleneck (L5): 5 SEMANTICS:GEO features survive (90% blocked!)
Post-bottleneck (L6-L25): Only syntax features amplified
```

**3. Predict Failure Modes**
```python
# If prompt requires SEMANTICS:GEO but L5 blocks 90% of geo features:
# → Prediction: Model will fail on geographic questions
```

**4. Design Interventions**
```python
# To fix geographic failures:
# → Amplify SEMANTICS:GEO features at L4 (before bottleneck)
# → Ablate SYNTAX features at L5 (reduce competition)
# → Modify L5_F7993995 if it's blocking geographic info
```

---

## Deliverables

### Phase 1 Output (Week 1-2):

1. **`semantic_taxonomy_annotations.csv`** - Master annotation file with 100+ features
2. **`SEMANTIC_TAXONOMY.md`** - Human-readable summary with examples
3. **`semantic_distribution_by_layer.png`** - Visualization showing category % per layer
4. **`bottleneck_semantic_analysis.md`** - Specific analysis of L5_F7993995 and why it blocks geography

### Example Output Format:

**SEMANTIC_TAXONOMY.md**:
```markdown
# Semantic Taxonomy - GEMMA-2-2B "Water Boils" Circuit

## Summary Statistics
- Total Features Annotated: 127
- SYNTAX: 42 (33%)
- SEMANTICS: 68 (54%)
  - Geographic: 23 (18%)
  - Temporal: 12 (9%)
  - Entity: 19 (15%)
  - Concept: 14 (11%)
- POLYSEMANTIC: 17 (13%)

## Key Findings

### Bottleneck Feature: L5_F7993995
- **Category**: POLYSEMANTIC
- **Activation Examples**: "capital" (geo), "}" (syntax), "president" (entity), ";" (syntax)
- **Behavior**: Acts as universal filter, blocks specific semantic types
- **Geographic Features Blocked**: 18 of 23 (78%) geographic features blocked at L5

### Pre-Bottleneck (L0-L4)
- Geographic features: 23 active
- Semantic richness: HIGH

### Post-Bottleneck (L6-L25)
- Geographic features: 5 surviving (22%)
- Semantic richness: LOW (syntax-dominated)

## Conclusion
L5_F7993995 polysemantic bottleneck causes 78% geographic information loss, explaining
why GEMMA predicts " home" (syntactically plausible) instead of " Florida" (semantically correct).
```

---

## Summary: Why This Methodology Works

1. **Grounded in Data**: Categories based on actual activation patterns, not theory
2. **Reproducible**: Clear decision rules anyone can follow
3. **Validated**: Inter-rater reliability ensures objectivity
4. **Actionable**: Directly informs intervention design
5. **Interpretable**: Results understandable to non-experts

**Next Step**: Run `query_feature_semantics.py` on L5_F7993995 to get activation examples, then begin manual annotation following this methodology.
