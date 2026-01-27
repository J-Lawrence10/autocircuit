# Quick Archive Guide

## Before Editing ANY Script - Use This:

```python
from archive_manager import archive_before_edit

archive_before_edit('script_name.py', 'Your reason here')
# Now make your edits
```

---

## Common Commands

### Archive Before Editing
```python
# Single script
archive_before_edit('1_generate_graph.py', 'Adding PathManager')

# Multiple scripts
archive_before_edit(['1_generate_graph.py', '2_convert_graph.py'], 'PathManager integration')
```

### View All Archives
```bash
python archive_manager.py list
```

### View History for One Script
```bash
python archive_manager.py history 1_generate_graph.py
```

### Restore Previous Version
```bash
# Most recent
python archive_manager.py restore 1_generate_graph.py

# Specific version
python archive_manager.py restore 1_generate_graph.py 20260120_233638
```

### Clean Old Versions
```bash
# Keep last 5 versions per script
python archive_manager.py clean 5
```

---

## Rules

1. **Always archive before editing**
2. **Provide meaningful reason**
3. **Never delete archive files manually**

---

## Status

✅ **Active**: 19 scripts archived (baseline: 20260120_233638)
✅ **Location**: `scripts/archive/`

See `ARCHIVE_POLICY.md` for full documentation.
