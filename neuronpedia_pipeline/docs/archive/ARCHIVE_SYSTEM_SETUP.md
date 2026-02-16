# Archive System Setup - Complete ✅

## Summary

Successfully implemented a comprehensive script backup system as requested. All 19 scripts now have initial backups stored in `scripts/archive/` with timestamped versions.

---

## What Was Created

### 1. **Archive Manager** (`scripts/archive_manager.py`)
- Full-featured backup utility
- Automatic timestamping
- Archive index tracking
- Restore functionality
- History viewing
- Cleanup tools

**Key Features**:
- ✅ Archive individual or multiple scripts
- ✅ Track archive history with reasons
- ✅ Restore previous versions
- ✅ Clean old archives (keep last N versions)
- ✅ Command-line and Python API
- ✅ Automatic index management

### 2. **Archive Policy** (`scripts/ARCHIVE_POLICY.md`)
- Complete documentation (500+ lines)
- Usage examples (Python + command-line)
- Workflow guidelines
- Best practices
- FAQ section

### 3. **Initial Backups**
Created baseline backups of **19 scripts**:
- All pipeline scripts (1-10)
- Helper scripts (supernode_detector, feature_description_fetcher, etc.)
- Visualization scripts (create_reasoning_chain, etc.)
- Utility scripts (path_manager, validate_real_data)

**Archive Location**: `neuronpedia_pipeline/scripts/archive/`

---

## Archive Structure

```
neuronpedia_pipeline/scripts/
├── archive/
│   ├── archive_index.json                         # Index of all versions
│   ├── 1_generate_graph_20260120_233638.py        # Baseline backup
│   ├── 2_convert_graph_20260120_233638.py
│   ├── 3_analyze_circuit_20260120_233638.py
│   ├── 4_visualize_20260120_233638.py
│   ├── 5_cross_prompt_analysis_20260120_233638.py
│   ├── 7_extract_minimal_pathways_20260120_233638.py
│   ├── 8_supernode_evolution_20260120_233638.py
│   ├── 9_steering_analysis_20260120_233638.py
│   ├── 10_polysemanticity_analysis_20260120_233638.py
│   └── ... (19 total scripts archived)
│
├── archive_manager.py                             # Backup utility
├── ARCHIVE_POLICY.md                              # Documentation
├── path_manager.py                                # PathManager
└── ... (current working versions)
```

---

## How to Use

### Before Editing ANY Script

**Quick Method** (recommended):
```python
from archive_manager import archive_before_edit

archive_before_edit('1_generate_graph.py', 'Adding PathManager integration')
# Now edit the script
```

**Full Control Method**:
```python
from archive_manager import ArchiveManager

am = ArchiveManager()
am.archive_script('1_generate_graph.py', reason='Your edit reason here')
```

**Command-Line Method**:
```bash
cd neuronpedia_pipeline/scripts
python archive_manager.py archive 1_generate_graph.py "Your reason here"
```

---

## Common Operations

### List All Archives
```bash
python archive_manager.py list
```

### View History for Specific Script
```bash
python archive_manager.py history 1_generate_graph.py
```

### Restore Previous Version
```bash
# Restore most recent
python archive_manager.py restore 1_generate_graph.py

# Restore specific version
python archive_manager.py restore 1_generate_graph.py 20260120_233638
```

### Archive Multiple Scripts
```python
from archive_manager import archive_before_edit

scripts = [
    '1_generate_graph.py',
    '2_convert_graph.py',
    '3_analyze_circuit.py'
]

archive_before_edit(scripts, 'PathManager integration')
```

### Clean Old Archives
```bash
# Keep only last 5 versions per script
python archive_manager.py clean 5
```

---

## Archive Policy Rules

### **Rule 1: Always Archive Before Editing**
Before making ANY changes to a script, create an archive with a meaningful reason.

### **Rule 2: Provide Meaningful Reasons**
Always include a descriptive reason:
- ✅ "Adding PathManager integration"
- ✅ "Fix unicode encoding errors"
- ✅ "Optimize path finding algorithm"
- ❌ "Updates" (too vague)

### **Rule 3: Archive Before Bulk Operations**
When updating multiple scripts, archive them all first with a shared reason.

### **Rule 4: Keep Last 5 Versions**
Run cleanup monthly: `python archive_manager.py clean 5`

### **Rule 5: Never Delete Archives Manually**
Always use `clean_old_archives()` to keep the index in sync.

---

## Current Status

### ✅ Archive System Active

**Scripts Archived**: 19
**Total Versions**: 19 (baseline)
**Archive Location**: `scripts/archive/`
**Index File**: `scripts/archive/archive_index.json`

**Baseline Timestamp**: `20260120_233638`
**Baseline Reason**: "Initial backup - baseline before PathManager integration"

---

## Next Steps

Now that the archive system is in place, you can safely proceed with:

### 1. **PathManager Integration** (Next Priority)
Archive scripts before editing:
```python
from archive_manager import archive_before_edit

# Scripts to update
tier1_scripts = [
    '1_generate_graph.py',
    '2_convert_graph.py',
    '3_analyze_circuit.py',
    '4_visualize.py',
    '5_cross_prompt_analysis.py'
]

archive_before_edit(tier1_scripts, 'PathManager integration - Tier 1')

# Then edit each script to use PathManager
```

### 2. **Script Updates**
Update Scripts 1-10 to use PathManager instead of hardcoded paths:

**Template for each script**:
```python
# At top of script
from path_manager import PathManager
pm = PathManager()

# Replace hardcoded paths
# OLD:
output_file = f"data/graphs/{slug}/real_{slug}_analysis.json"

# NEW:
output_file = pm.circuit_analysis_path(prompt)
```

### 3. **Validation**
After updates, test full pipeline:
```bash
# Generate new prompt
python scripts/1_generate_graph.py --prompt "Test prompt"

# Verify new structure
ls data/prompts/test-prompt/
# Should see: 1_generation/, 2_conversion/, etc.
```

---

## Example Workflow

### Scenario: Update Script 1 to Use PathManager

**Step 1: Archive Current Version**
```python
from archive_manager import archive_before_edit
archive_before_edit('1_generate_graph.py', 'Adding PathManager integration')
```

**Step 2: Make Edits**
Edit `1_generate_graph.py` to import and use PathManager.

**Step 3: Test**
```bash
python scripts/1_generate_graph.py --prompt "The capitol of Texas is"
```

**Step 4 (If Needed): Restore**
If something breaks:
```python
from archive_manager import ArchiveManager
am = ArchiveManager()
am.restore_script('1_generate_graph.py')  # Restores previous version
```

---

## Benefits

1. **Safety**: Never lose work due to bad edits
2. **Traceability**: Know exactly when and why scripts changed
3. **Quick Rollback**: Restore previous versions in seconds
4. **Development History**: See evolution of scripts over time
5. **Confidence**: Edit freely knowing you can always go back

---

## Verification

To verify the archive system is working:

```bash
cd neuronpedia_pipeline/scripts

# List all archives
python archive_manager.py list

# Check archive directory
ls archive/

# Verify index exists
cat archive/archive_index.json | head -20
```

Expected output: 19 scripts with 1 version each, all with timestamp `20260120_233638`.

---

## Archive vs Git

The archive system complements Git:

| Feature | Archive System | Git |
|---------|---------------|-----|
| **Purpose** | Local backup before edits | Version control |
| **Scope** | Single file changes | Entire codebase |
| **Granularity** | Every edit | Commits only |
| **Storage** | Local (scripts/archive/) | Local + remote |
| **Best For** | WIP backups | Release management |

**Use Both**: Archive for safety during development, Git for team collaboration.

---

## Files Created

1. **`scripts/archive_manager.py`** (300 lines)
   - ArchiveManager class
   - archive_before_edit() convenience function
   - Command-line interface
   - Index management

2. **`scripts/ARCHIVE_POLICY.md`** (500 lines)
   - Complete usage documentation
   - Workflow examples
   - Best practices
   - FAQ

3. **`ARCHIVE_SYSTEM_SETUP.md`** (this file)
   - Setup summary
   - Quick reference
   - Next steps

4. **`scripts/archive/archive_index.json`**
   - Tracks all archived versions
   - JSON format for easy parsing

5. **19 Baseline Backups** in `scripts/archive/`
   - All scripts archived at timestamp `20260120_233638`
   - Reason: "Initial backup - baseline before PathManager integration"

---

## Success Metrics

✅ **Archive system implemented**: ArchiveManager class with full functionality
✅ **Documentation complete**: ARCHIVE_POLICY.md with comprehensive guide
✅ **Initial backups created**: All 19 scripts archived (baseline)
✅ **Index tracking active**: archive_index.json created and populated
✅ **Command-line tools working**: Tested list, archive commands
✅ **Python API ready**: archive_before_edit() convenience function available

---

## Ready for PathManager Integration

With the archive system in place, you can now safely proceed to update all scripts to use PathManager. The workflow will be:

1. Archive scripts before editing (using archive_manager)
2. Update scripts to use PathManager
3. Test updated scripts
4. If issues arise, restore from archive
5. Repeat for all scripts

**Next Task**: Update Scripts 1-10 to use PathManager (from REORGANIZATION_PLAN.md Phase 2)

---

**Setup Completed**: 2026-01-20 23:36:38
**Scripts Archived**: 19
**System Status**: ✅ Active and Ready
