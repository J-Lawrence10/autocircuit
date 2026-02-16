# Feature Annotation Tools

Two AI-powered tools to assist with semantic taxonomy annotation using decision tree logic.

## Tool 1: Interactive Assisted Annotation (`annotate_features_assisted.py`)

**Best for**: Careful, supervised annotation where you want to review each feature.

### Features
- AI suggests category, confidence, and notes for each feature
- Shows decision tree reasoning
- You can accept, modify, or skip each suggestion
- Progress saved every 5 features
- Resume from where you left off

### Usage

```bash
cd neuronpedia_pipeline/scripts

python annotate_features_assisted.py \
    --input ../semantic_taxonomy_annotations.csv \
    --output ../semantic_taxonomy_annotations_completed.csv
```

### Interactive Commands

```
[Enter]  - Accept AI suggestion
m <cat>  - Modify category (e.g., "m SEMANTICS:TEMPORAL")
c <conf> - Modify confidence (e.g., "c LOW")
n <text> - Modify notes (e.g., "n Different reasoning")
s        - Skip this feature
q        - Quit and save progress
```

### Example Session

```
[3/80] L0_F1000 (Layer 0)
────────────────────────────────────────────────────────────────────────
Examples: <bos>; The; the
Count: 3
Auto Category: SYNTAX

AI SUGGESTION:
  Category:   SYNTAX
  Confidence: HIGH
  Notes:      100% syntax indicators (special tokens, punctuation, code syntax)

Reasoning:
  - Q1: 100% syntax indicators (special tokens, punctuation, code syntax)
  - Examples: <bos>, The, the
────────────────────────────────────────────────────────────────────────

Action ([Enter]=accept, m/c/n=modify, s=skip, q=quit): [Enter]
✓ Accepted suggestion for L0_F1000
```

### Resume from Specific Row

```bash
python annotate_features_assisted.py \
    --input ../semantic_taxonomy_annotations.csv \
    --output ../semantic_taxonomy_annotations_completed.csv \
    --start-row 25  # Resume from row 25
```

---

## Tool 2: Automatic Batch Annotation (`annotate_features_auto.py`)

**Best for**: Quick first-pass annotation, then review afterward in spreadsheet.

### Features
- Automatically annotates all 80 features
- Uses same decision tree logic as interactive tool
- Shows progress with confidence indicators
- Generates summary statistics
- Fast (~30 seconds for 80 features)

### Usage

```bash
cd neuronpedia_pipeline/scripts

python annotate_features_auto.py \
    --input ../semantic_taxonomy_annotations.csv \
    --output ../semantic_taxonomy_annotations_auto.csv \
    --summary  # Optional: show statistics after annotation
```

### Output Example

```
[1/80] ✓ L0_F100: SEMANTICS:CODE (HIGH) [Auto:✓]
[2/80] ✓ L0_F500: SEMANTICS:CODE (HIGH) [Auto:✓]
[3/80] ✓ L0_F1000: SYNTAX (HIGH) [Auto:✓]
[4/80] ✓ L0_F3000: SYNTAX (HIGH) [Auto:✓]
[5/80] ~ L0_F5000: SEMANTICS:CODE (MEDIUM) [Auto:✓]
...

════════════════════════════════════════════════════════════════════════
ANNOTATION COMPLETE!
════════════════════════════════════════════════════════════════════════

Annotated: 80/80

Category Distribution:
  POLYSEMANTIC              :   3 (  3.8%)
  SEMANTICS:CODE            :  55 ( 68.8%)
  SEMANTICS:CONCEPT         :  12 ( 15.0%)
  SEMANTICS:ENTITY          :   3 (  3.8%)
  SEMANTICS:GEOGRAPHIC      :   1 (  1.2%)
  SYNTAX                    :   5 (  6.2%)
  UNKNOWN                   :   1 (  1.2%)

Output saved to: ../semantic_taxonomy_annotations_auto.csv
```

### Review Workflow

After automatic annotation:
1. Open `semantic_taxonomy_annotations_auto.csv` in Excel/Google Sheets
2. Filter by confidence = "LOW" → verify these first
3. Filter by notes containing "Disagree with auto" → check these
4. Spot-check random HIGH confidence annotations
5. Make manual corrections as needed

---

## Decision Tree Logic (Both Tools)

The AI applies the same decision tree from the annotation workflow:

### Q1: Is >70% syntax?
- **Checks**: Special tokens (`<bos>`, `<eos>`), punctuation, brackets, operators
- **If YES** → `SYNTAX` (confidence HIGH if >90%, MEDIUM if 70-90%)

### Q2: Is >70% semantic with coherent theme?
- **Checks**: Semantic indicators by type (geographic, temporal, entity, concept, code)
- **If YES** → `SEMANTICS:{TYPE}` (confidence based on consistency)
- **Sub-types**:
  - `SEMANTICS:GEOGRAPHIC` - Location, countries, cities, spatial
  - `SEMANTICS:TEMPORAL` - Time, dates, sequences
  - `SEMANTICS:ENTITY` - People, organizations, objects
  - `SEMANTICS:CONCEPT` - Abstract ideas, relations, properties
  - `SEMANTICS:CODE` - Programming identifiers (camelCase, PascalCase, API names)

### Q3: Mix of syntax AND semantics?
- **Checks**: Both syntax (>20%) and semantics (>20%) present
- **If YES** → `POLYSEMANTIC` (confidence MEDIUM)

### Q4: Multiple unrelated semantic domains?
- **Checks**: Examples span 2+ different semantic types
- **If YES** → `POLYSEMANTIC` (confidence MEDIUM)

### Default
- If mostly word-like → `SEMANTICS:CONCEPT` (confidence LOW)
- Otherwise → `POLYSEMANTIC` (confidence LOW)

---

## Pattern Detection

The AI recognizes these patterns:

### Code Identifiers
```
camelCase       → createSlice, onAttach, webdriver
PascalCase      → SqlCommand, MigrationBuilder, DeleteBehavior
UPPER_SNAKE     → EDEFAULT, SBATCH
lower_snake     → principalColumn, rawDesc
```

### Multilingual Content
```
Chinese:  來的, 截至
Arabic:   جغرافيا, استنادى
Hebrew:   חיצוניים
Cyrillic: архивлан
```

### Historical Spelling
```
Long s (ſ):  itſelf → itself
            myſelf → myself
            ſtate  → state
```

---

## Comparison: Which Tool to Use?

| Feature | Interactive | Automatic |
|---------|-------------|-----------|
| Speed | ~4 hours | ~30 seconds |
| Supervision | Feature-by-feature | Batch review afterward |
| Flexibility | Modify on-the-fly | Edit in spreadsheet |
| Best for | High-stakes annotation | Quick first pass |
| Resume capability | Yes (--start-row) | No (but skips annotated) |

**Recommended workflow**:
1. Run **automatic** tool first for quick first pass
2. Review output, make corrections to LOW confidence features
3. Use **interactive** tool for remaining uncertain features
4. Final manual review in spreadsheet

---

## Validation

After annotation, validate your results:

### Agreement Rate
```python
import pandas as pd

df = pd.read_csv('../semantic_taxonomy_annotations_completed.csv')

# Calculate agreement
agreement = (df['auto_category'] == df['manual_category']).sum() / len(df) * 100
print(f"Agreement rate: {agreement:.1f}%")

# Target: >85%
assert agreement > 85, "Low agreement - review annotations"
```

### Category Distribution
```python
# Check distribution
dist = df['manual_category'].value_counts(normalize=True) * 100
print("Manual category distribution:")
print(dist)

# Expected ranges:
# SEMANTICS:*  70-90%
# SYNTAX       5-15%
# POLYSEMANTIC 5-15%
```

### Confidence Distribution
```python
# Check confidence
conf = df['confidence'].value_counts(normalize=True) * 100
print("Confidence distribution:")
print(conf)

# Expected:
# HIGH    50-70%
# MEDIUM  25-40%
# LOW     5-15%
```

---

## Troubleshooting

### ImportError: Can't find annotate_features_assisted.py
**Solution**: Ensure both scripts are in the same directory (`neuronpedia_pipeline/scripts/`)

### UnicodeEncodeError on Windows
**Solution**: Use `chcp 65001` before running to enable UTF-8 in terminal

### "Already annotated (skipping)" for all features
**Solution**: Clear manual_category, confidence, notes columns if you want to re-annotate

### Agreement rate < 85%
**Solution**: This is expected for automatic annotation. The tool is conservative. Review LOW confidence annotations and fix systematic errors.

---

## Tips for High-Quality Annotation

1. **Trust HIGH confidence suggestions** - The AI is usually right when confident
2. **Review LOW confidence carefully** - These need human judgment
3. **Check disagreements** - When AI disagrees with auto_category, it found a pattern
4. **Batch similar features** - Use spreadsheet sorting to annotate similar features together
5. **Take breaks** - Annotation fatigue affects quality after ~20 features

---

## Next Steps After Annotation

Once all 80 features are annotated:

1. **Calculate statistics** (see Validation section above)
2. **Proceed to Task 1.3**: Bottleneck deep dive analysis
3. **Generate visualizations** (Task 1.4) using annotated taxonomy
4. **Use annotations** for semantic-aware circuit visualizations (Stage 2)

---

**Created**: 2025-02-09
**Tools**: `annotate_features_assisted.py`, `annotate_features_auto.py`
**Documentation**: Part of Stage 1.2 (Manual Annotation with Decision Tree)
