# PathManager Integration - Progress Tracker

## Overview

Updating all pipeline scripts (1-10) to use PathManager instead of hardcoded paths for the new file organization structure.

---

## Status Summary

### ✅ Completed Scripts

#### **Script 1: Generate Graph** (`1_generate_graph.py`)
- **Status**: ✅ Updated
- **Archived**: `20260120_235040`
- **Changes**:
  - Added PathManager import
  - Updated to save raw graph using `pm.raw_graph_path(prompt)`
  - Saves metadata using `pm.save_metadata(prompt, metadata)`
  - Outputs to `data/prompts/{slug}/1_generation/`

#### **Script 2: Convert Graph** (`2_convert_graph.py`)
- **Status**: ✅ Updated
- **Archived**: `20260120_235133`
- **Changes**:
  - Added PathManager import
  - Updated `find_available_raw_graphs()` to search new structure
  - Uses `pm.converted_graph_path(prompt)` for output
  - Saves conversion stats using `pm.conversion_stats_path(prompt)`
  - Outputs to `data/prompts/{slug}/2_conversion/`
  - **Backward compatible**: Still checks old `data/graphs/` location

---

### ⏳ In Progress

#### **Script 3: Analyze Circuit** (`3_analyze_circuit.py`)
- **Status**: ⏳ Archived, ready to update
- **Archived**: `20260120_235133`
- **Needed Changes**:
  - Add PathManager import
  - Update input path finding to use `pm.converted_graph_path(prompt)`
  - Update output to use `pm.circuit_analysis_path(prompt)`
  - Save supernodes using `pm.supernodes_path(prompt)`
  - Save layer groups using `pm.layer_groups_path(prompt)`

#### **Script 4: Visualize** (`4_visualize.py`)
- **Status**: ⏳ Archived, ready to update
- **Archived**: `20260120_235133`
- **Needed Changes**:
  - Add PathManager import
  - Update input to use `pm.circuit_analysis_path(prompt)`
  - Update visualization output to use `pm.visualization_path(prompt, viz_name)`
  - Save all 8 visualizations to `data/prompts/{slug}/4_visualizations/`

#### **Script 5: Cross-Prompt Analysis** (`5_cross_prompt_analysis.py`)
- **Status**: ⏳ Archived, ready to update
- **Archived**: `20260120_235133`
- **Needed Changes**:
  - Add PathManager import
  - Update to find analysis files using `pm.find_analysis_for_prompts(prompts)`
  - Update output to use `pm.get_cross_analysis_dir(analysis_name)`
  - Save outputs using cross-analysis path methods

---

### 📋 Not Yet Started

#### **Script 7: Minimal Pathways** (`7_extract_minimal_pathways.py`)
- **Status**: 📋 Not started
- **Priority**: High (Tier 1)
- **Needed Changes**:
  - Add PathManager import
  - Update to use `pm.circuit_analysis_path(prompt)` for input
  - Update to use `pm.minimal_pathways_dir(prompt)` for output

#### **Script 8: Supernode Evolution** (`8_supernode_evolution.py`)
- **Status**: 📋 Not started
- **Priority**: Medium (Tier 2)
- **Needed Changes**:
  - Add PathManager import
  - Update to use `pm.circuit_analysis_path(prompt)` for input
  - Update to use `pm.evolution_dir(prompt)` for output

#### **Script 9: Steering Analysis** (`9_steering_analysis.py`)
- **Status**: 📋 Not started
- **Priority**: High (Tier 1)
- **Needed Changes**:
  - Add PathManager import
  - Update to use `pm.circuit_analysis_path(prompt)` for input
  - Update to use `pm.steering_dir(prompt)` for output

#### **Script 10: Polysemanticity** (`10_polysemanticity_analysis.py`)
- **Status**: 📋 Not started
- **Priority**: Medium (Tier 2)
- **Needed Changes**:
  - Add PathManager import
  - Update to use `pm.circuit_analysis_path(prompt)` for input
  - Update to use `pm.polysemanticity_dir(prompt)` for output

---

## Testing Plan

### Phase 1: Core Pipeline (Scripts 1-4)
Once Scripts 1-4 are updated, test the core pipeline:

```bash
# Test full pipeline on new prompt
python scripts/1_generate_graph.py --prompt "Test prompt for PathManager"

# Verify structure created
ls data/prompts/test-prompt-for-pathmanager/
# Expected: 1_generation/ with raw_graph.json and metadata.json

# Convert
python scripts/2_convert_graph.py

# Verify conversion
ls data/prompts/test-prompt-for-pathmanager/
# Expected: 1_generation/, 2_conversion/ with converted_graph.json

# Analyze
python scripts/3_analyze_circuit.py

# Verify analysis
ls data/prompts/test-prompt-for-pathmanager/
# Expected: 1_generation/, 2_conversion/, 3_analysis/ with circuit_analysis.json

# Visualize
python scripts/4_visualize.py

# Verify visualizations
ls data/prompts/test-prompt-for-pathmanager/4_visualizations/
# Expected: 8 PNG files
```

### Phase 2: Cross-Prompt (Script 5)
After Scripts 1-4 work:

```bash
# Run cross-prompt analysis on 2+ prompts
python scripts/5_cross_prompt_analysis.py

# Verify output
ls data/cross_analysis/
# Expected: analysis folder with consensus_supernodes.json, etc.
```

### Phase 3: Optional Analyses (Scripts 7-10)
After core pipeline validated:

```bash
# Test each optional analysis
python scripts/7_extract_minimal_pathways.py
python scripts/8_supernode_evolution.py
python scripts/9_steering_analysis.py
python scripts/10_polysemanticity_analysis.py

# Verify outputs in respective directories
ls data/prompts/*/7_minimal_pathways/
ls data/prompts/*/8_evolution/
ls data/prompts/*/9_steering/
ls data/prompts/*/10_polysemanticity/
```

---

## Integration Checklist

### For Each Script:

- [ ] Archive current version using archive_manager
- [ ] Add PathManager import
- [ ] Update input path finding
- [ ] Update output path generation
- [ ] Test script with existing data
- [ ] Test script with new data
- [ ] Verify correct directory structure created
- [ ] Verify outputs have standard filenames

---

## Archive History

All scripts archived before editing:

| Script | Archive Timestamp | Reason |
|--------|------------------|--------|
| 1_generate_graph.py | 20260120_235040 | PathManager integration - updating to new directory structure |
| 2_convert_graph.py | 20260120_235133 | PathManager integration - core pipeline scripts |
| 3_analyze_circuit.py | 20260120_235133 | PathManager integration - core pipeline scripts |
| 4_visualize.py | 20260120_235133 | PathManager integration - core pipeline scripts |
| 5_cross_prompt_analysis.py | 20260120_235133 | PathManager integration - core pipeline scripts |

---

## Key Files Modified

### Completed:
1. ✅ `scripts/1_generate_graph.py` (lines 6-16, 226-262)
2. ✅ `scripts/2_convert_graph.py` (lines 7-15, 17-33, 155-181, 214-240, 302-321, 357-358)

### In Progress:
3. ⏳ `scripts/3_analyze_circuit.py`
4. ⏳ `scripts/4_visualize.py`
5. ⏳ `scripts/5_cross_prompt_analysis.py`

### Pending:
6. 📋 `scripts/7_extract_minimal_pathways.py`
7. 📋 `scripts/8_supernode_evolution.py`
8. 📋 `scripts/9_steering_analysis.py`
9. 📋 `scripts/10_polysemanticity_analysis.py`

---

## Next Steps

1. **Update Scripts 3-5** (core pipeline completion)
   - Script 3: Analyze Circuit
   - Script 4: Visualize
   - Script 5: Cross-Prompt Analysis

2. **Test Core Pipeline** (Scripts 1-5)
   - Generate new prompt
   - Verify directory structure
   - Verify all outputs in correct locations

3. **Update Scripts 7-10** (optional analyses)
   - Script 7: Minimal Pathways
   - Script 8: Evolution
   - Script 9: Steering
   - Script 10: Polysemanticity

4. **Full Integration Test**
   - Run all 10 scripts on new prompt
   - Verify complete directory structure
   - Compare outputs with migration results

---

## Known Issues

### Script 2 Compatibility:
- ✅ Updated `find_available_raw_graphs()` to check both:
  - New location: `data/prompts/*/1_generation/raw_graph.json`
  - Old location: `data/graphs/real_*.json`
- This ensures backward compatibility with pre-migration data

### Metadata Extraction:
- ⚠️ Some old files may not have prompt in metadata
- Fallback: Extract from slug or filename
- Scripts handle missing metadata gracefully

---

**Last Updated**: 2026-01-20 23:51:33
**Progress**: 2/10 scripts updated (20%)
**Next Priority**: Update Scripts 3, 4, 5
