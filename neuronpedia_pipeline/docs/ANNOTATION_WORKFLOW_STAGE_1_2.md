# Stage 1.2: Manual Annotation Workflow

## Overview

**Objective**: Manually annotate 80 features using decision tree methodology to build comprehensive semantic taxonomy.

**Input**: `semantic_taxonomy_annotations.csv` (80 rows, auto_category pre-filled)
**Output**: Same CSV with manual_category, confidence, and notes columns filled
**Time**: ~4 hours (~3 minutes per feature)

---

## Decision Tree (Apply to Each Feature)

### Q1: Is >70% punctuation, code syntax, or special tokens?
**Indicators**: `<bos>`, `<eos>`, `()[]{}`, `;;;`, `def`, `class`, `import`, `▁`

- **YES** → Categorize as **SYNTAX**
- **NO** → Continue to Q2

### Q2: Is >70% meaningful words with coherent semantic theme?
**Indicators**: Related words, consistent domain, clear concept

- **YES** → Categorize as **SEMANTICS** (determine sub-category)
- **NO** → Continue to Q3

### Q3: Mix of syntax patterns AND semantic concepts?
**Indicators**: Some special tokens + some meaningful words

- **YES** → Categorize as **POLYSEMANTIC**
- **NO** → Continue to Q4

### Q4: Mix of multiple unrelated semantic domains?
**Indicators**: Geographic + temporal together, person names + code, etc.

- **YES** → Categorize as **POLYSEMANTIC**
- **NO** → Default to closest match (SEMANTICS if mostly meaningful, SYNTAX if mostly structural)

---

## Semantic Sub-Categories (If SEMANTICS)

### SEMANTICS:GEOGRAPHIC
- Countries: France, Japan, USA
- Cities: Paris, Tokyo, Dallas
- Locations: north, south, capital, border
- Spatial: between, near, far, located

### SEMANTICS:TEMPORAL
- Time: yesterday, tomorrow, 2024, noon
- Sequence: before, after, during, while
- Duration: hour, day, week, century
- Events: birthday, election, holiday

### SEMANTICS:ENTITY
- People: John, president, scientist
- Organizations: Microsoft, UN, government
- Objects: car, building, computer
- Proper names: Named entities

### SEMANTICS:CONCEPT
- Abstract ideas: freedom, justice, beauty
- Relations: cause, effect, because, therefore
- Properties: large, fast, important
- Actions: calculate, determine, establish
- States: possible, necessary, certain

### SEMANTICS:CODE (Programming-specific)
- API/Function names: `SqlCommand`, `createSlice`, `onAttach`
- Framework terms: `MigrationBuilder`, `GraphicsUnit`
- Library references: `bootstrapcdn`, `GoogleFonts`

---

## Confidence Ratings

### HIGH (>90% certainty)
- All examples clearly match one category
- Consistent theme across examples
- No ambiguity in interpretation
- Auto_category agrees with manual_category

### MEDIUM (70-90% certainty)
- Most examples match, but some ambiguity
- Theme is present but not perfectly clear
- Some examples could fit multiple categories
- Minor disagreement with auto_category

### LOW (<70% certainty)
- Examples are unclear or contradictory
- No clear theme emerges
- Heavy polysemantic signals
- Significant disagreement with auto_category
- Insufficient examples (n<2)

---

## Notes Column Guidelines

Document the following:

1. **Reasoning**: Why did you choose this category?
2. **Edge Cases**: Any examples that don't fit well?
3. **Ambiguities**: Unclear aspects or multiple interpretations?
4. **Disagreements**: If auto_category differs, explain why
5. **Patterns**: Interesting semantic relationships observed

**Examples**:
- `"Motion/arrival concept - 'incoming' in multiple languages. Semantic bias toward directionality."`
- `"Historical text with archaic spellings (ſ for s). Clearly SEMANTICS despite unusual orthography."`
- `"Mixed: <bos> is syntax but 'quelize' is semantic. Slight POLYSEMANTIC lean but auto says SEMANTICS."`
- `"Programming framework identifiers - all C# GUI code. SEMANTICS:CODE subcategory."`

---

## Annotation Process (Step-by-Step)

### Step 1: Setup
1. Open `semantic_taxonomy_annotations.csv` in spreadsheet editor
2. Create backup copy: `semantic_taxonomy_annotations_backup.csv`
3. Open this workflow document in adjacent window
4. Prepare to annotate row-by-row (rows 2-81)

### Step 2: For Each Feature (Rows 2-81)
1. **Read activation examples** column
2. **Apply decision tree** (Q1 → Q2 → Q3 → Q4)
3. **Determine category**:
   - SYNTAX
   - SEMANTICS:{GEOGRAPHIC|TEMPORAL|ENTITY|CONCEPT|CODE}
   - POLYSEMANTIC
4. **Assign confidence**: HIGH | MEDIUM | LOW
5. **Write notes**: Brief explanation (1-2 sentences)

### Step 3: Validation Pass
After completing all 80 features:
1. **Agreement check**: Compare auto_category vs manual_category
   - Count exact matches: `=COUNTIF(F:F, G:G)`
   - Target: >85% agreement
2. **Distribution check**: Are percentages reasonable?
   - SEMANTICS should be 70-90%
   - SYNTAX should be 5-15%
   - POLYSEMANTIC should be 5-15%
3. **Edge case review**: Review all LOW confidence ratings
   - Can confidence be upgraded with deeper analysis?
   - Document why confidence remains LOW

### Step 4: Documentation
Create summary statistics:
- Total features: 80
- Category breakdown (count and %)
- Agreement rate with auto_category
- Confidence distribution
- Notable findings

---

## Example Annotations

### Example 1: L0_F1000
```csv
feature_label: L0_F1000
activation_examples: <bos>; The; the
auto_category: SYNTAX
manual_category: SYNTAX
confidence: HIGH
notes: "Special token <bos> and articles 'The/the'. Structural function, no semantic content."
```

**Reasoning**: Q1: >70% special tokens/articles → YES → SYNTAX

---

### Example 2: L20_F5000
```csv
feature_label: L20_F5000
activation_examples: IN; IN; into
auto_category: SEMANTICS
manual_category: SEMANTICS:CONCEPT
confidence: HIGH
notes: "Preposition 'into' indicates direction/containment. Abstract spatial relation concept."
```

**Reasoning**: Q1: No → Q2: Meaningful spatial concept → YES → SEMANTICS:CONCEPT

---

### Example 3: L3_F1000
```csv
feature_label: L3_F1000
activation_examples: nahilalakip; defaultstate; surla
auto_category: POLYSEMANTIC
manual_category: POLYSEMANTIC
confidence: MEDIUM
notes: "Mix of code identifier 'defaultstate' and foreign words. No unifying theme across examples."
```

**Reasoning**: Q1: No → Q2: No coherent theme → Q3: Mixed signals → Q4: Unrelated domains → POLYSEMANTIC

---

### Example 4: L15_F10000
```csv
feature_label: L15_F10000
activation_examples: staff; Staff; Signalez
auto_category: SEMANTICS
manual_category: SEMANTICS:ENTITY
confidence: MEDIUM
notes: "Primary meaning is people/workforce (entity). 'Signalez' (French 'report') less clear connection. Entity interpretation preferred."
```

**Reasoning**: Q1: No → Q2: Two examples about people/staff → YES → SEMANTICS:ENTITY (with note about ambiguity)

---

### Example 5: L9_F10000
```csv
feature_label: L9_F10000
activation_examples: استنادى; jsPsych; //};
auto_category: SEMANTICS
manual_category: POLYSEMANTIC
confidence: HIGH
notes: "Mix of Arabic text, JavaScript library, and code syntax. Three unrelated domains. Disagree with auto_category."
```

**Reasoning**: Q1: No (not all syntax) → Q2: No (unrelated examples) → Q4: Multiple domains → POLYSEMANTIC

---

## Common Pitfalls to Avoid

### Pitfall 1: Assuming all code is SYNTAX
**Wrong**: `SqlCommand`, `createSlice` → SYNTAX
**Correct**: These are meaningful semantic concepts (programming APIs) → SEMANTICS:CODE

Code identifiers have semantic meaning even if they appear in syntax-heavy contexts.

### Pitfall 2: Historical spelling = UNKNOWN
**Wrong**: `itſelf` (archaic spelling) → UNKNOWN
**Correct**: It's just "itself" with historical orthography → SEMANTICS

Archaic spellings don't negate semantic content.

### Pitfall 3: Foreign language = POLYSEMANTIC
**Wrong**: `來的; 来的` (Chinese variants) → POLYSEMANTIC
**Correct**: Same concept in different scripts → SEMANTICS

Multilingual examples of same concept are still coherent semantics.

### Pitfall 4: Trusting auto_category blindly
**Wrong**: Auto says SEMANTICS, so it must be SEMANTICS
**Correct**: Apply decision tree independently, document disagreements

Auto-categorization is preliminary and often wrong.

### Pitfall 5: Over-specificity in sub-categories
**Wrong**: `staff; Staff` → SEMANTICS:ENTITY:PERSON:WORKPLACE:GROUP
**Correct**: `staff; Staff` → SEMANTICS:ENTITY

Use only the four sub-categories defined above.

---

## Annotation Quality Checks

### Self-Check Questions (Per Feature)
1. Can I explain this categorization in one sentence?
2. Would another annotator reach the same conclusion?
3. Does my confidence rating match the clarity of examples?
4. Did I document why I disagreed with auto_category (if applicable)?
5. Did I consider all examples, not just the first one?

### Global Checks (After Completing All 80)
1. **Distribution sanity**: Is 90%+ in one category? (Red flag - review)
2. **Confidence balance**: Are most ratings HIGH or MEDIUM? (Expected)
3. **Note quality**: Did I document reasoning for LOW confidence and disagreements?
4. **Consistency**: Similar examples across features categorized similarly?

---

## Timeline & Breaks

**Total time**: ~4 hours for 80 features

**Suggested pacing**:
- **Hour 1**: Features 1-20 (L0-L3)
- **Break**: 10 minutes
- **Hour 2**: Features 21-40 (L6-L9)
- **Break**: 10 minutes
- **Hour 3**: Features 41-60 (L12-L20)
- **Break**: 10 minutes
- **Hour 4**: Features 61-80 (L20-L25) + validation pass

**Maintaining quality**:
- Take breaks to prevent annotation fatigue
- Review 5-10 previous annotations after each break for consistency
- If stuck on a feature for >5 minutes, mark LOW confidence and move on

---

## Post-Annotation Analysis

After completing manual annotation, calculate:

### 1. Agreement Metrics
```python
import pandas as pd

df = pd.read_csv('semantic_taxonomy_annotations.csv')

# Exact agreement rate
exact_matches = (df['auto_category'] == df['manual_category']).sum()
agreement_rate = exact_matches / len(df) * 100
print(f"Agreement rate: {agreement_rate:.1f}%")

# Expected: >85%
assert agreement_rate > 85, "Low agreement - review annotations"
```

### 2. Category Distribution
```python
# Manual category counts
manual_dist = df['manual_category'].value_counts(normalize=True) * 100
print("Manual category distribution:")
print(manual_dist)

# Expected:
# SEMANTICS:*  70-90%
# SYNTAX       5-15%
# POLYSEMANTIC 5-15%
```

### 3. Confidence Distribution
```python
conf_dist = df['confidence'].value_counts(normalize=True) * 100
print("Confidence distribution:")
print(conf_dist)

# Expected:
# HIGH    50-70%
# MEDIUM  25-40%
# LOW     5-15%
```

### 4. Layer-by-Layer Patterns
```python
# Semantic distribution by layer
layer_semantics = df.groupby('layer')['manual_category'].apply(
    lambda x: (x.str.contains('SEMANTICS')).sum() / len(x) * 100
)
print("SEMANTICS % by layer:")
print(layer_semantics)

# Expected pattern: Increases with layer depth (L0 < L25)
```

---

## Next Steps (After Completion)

Once all 80 features are annotated:

1. **Save final CSV** with all three columns filled
2. **Generate summary statistics** using post-annotation analysis code
3. **Proceed to Task 1.3**: Bottleneck deep dive analysis
4. **Use annotations for visualizations** in Task 1.4

The annotated taxonomy becomes the foundation for:
- Semantic-aware visualizations (Stage 2)
- Intervention experiment design (Stage 3)
- Cross-circuit semantic comparison (Stage 4)

---

## Questions During Annotation?

If uncertain about a specific feature:
1. **Check decision tree** - Did you follow all four questions?
2. **Compare to examples** in this document
3. **Mark MEDIUM or LOW confidence** rather than guessing
4. **Document uncertainty in notes** - Future reviews can refine

**Remember**: Thoughtful annotations with honest confidence ratings are more valuable than forced categorizations.

---

## Completion Checklist

- [ ] All 80 rows have manual_category filled
- [ ] All 80 rows have confidence rating (HIGH/MEDIUM/LOW)
- [ ] All 80 rows have notes (at least brief explanation)
- [ ] Backup copy created before editing
- [ ] Agreement rate calculated (target >85%)
- [ ] Category distribution calculated and reasonable
- [ ] Confidence distribution calculated
- [ ] LOW confidence features reviewed for possible upgrade
- [ ] Disagreements with auto_category documented in notes
- [ ] Ready to proceed to Task 1.3 (Bottleneck Analysis)

---

**File**: `ANNOTATION_WORKFLOW_STAGE_1_2.md`
**Created**: 2025-02-09
**Purpose**: Guide manual semantic taxonomy annotation for 80 features
