# Script Archive Policy

## Overview

All scripts in the `neuronpedia_pipeline/scripts/` directory are backed up to `scripts/archive/` before making edits. This ensures we can always restore previous versions if needed.

---

## Archive Structure

```
scripts/
├── archive/
│   ├── archive_index.json          # Index of all archived versions
│   ├── 1_generate_graph_20260120_235959.py
│   ├── 1_generate_graph_20260121_120000.py
│   ├── 2_convert_graph_20260120_235959.py
│   └── ... (timestamped backups)
│
├── archive_manager.py              # Backup utility
├── 1_generate_graph.py             # Current version
├── 2_convert_graph.py
└── ...
```

---

## Usage

### Before Editing Scripts

**Method 1: Python Script**
```python
from archive_manager import ArchiveManager

am = ArchiveManager()

# Archive single script
am.archive_script('1_generate_graph.py', reason='Adding PathManager integration')

# Archive multiple scripts
am.archive_scripts(
    ['1_generate_graph.py', '2_convert_graph.py'],
    reason='PathManager integration'
)
```

**Method 2: Convenience Function**
```python
from archive_manager import archive_before_edit

# Quick one-liner
archive_before_edit('1_generate_graph.py', 'Bug fix for unicode errors')

# Multiple scripts
archive_before_edit(
    ['1_generate_graph.py', '2_convert_graph.py'],
    'PathManager integration'
)
```

**Method 3: Command Line**
```bash
# Archive a script
python archive_manager.py archive 1_generate_graph.py "Adding PathManager"

# List all archives
python archive_manager.py list

# View history for a specific script
python archive_manager.py history 1_generate_graph.py

# Restore from archive
python archive_manager.py restore 1_generate_graph.py 20260120_235959
```

---

## Archive Index

The `archive/archive_index.json` file tracks all archived versions:

```json
{
  "1_generate_graph.py": [
    {
      "timestamp": "20260120_235959",
      "archive_file": "1_generate_graph_20260120_235959.py",
      "reason": "Adding PathManager integration",
      "original_size": 15234
    },
    {
      "timestamp": "20260121_120000",
      "archive_file": "1_generate_graph_20260121_120000.py",
      "reason": "Bug fix for unicode errors",
      "original_size": 15456
    }
  ]
}
```

---

## Viewing Archive History

### List All Archives
```bash
python archive_manager.py list
```

Output:
```
======================================================================
ARCHIVE SUMMARY
======================================================================

1_generate_graph.py: 3 versions
  20260121_120000 - 1_generate_graph_20260121_120000.py
    Reason: Bug fix for unicode errors
  20260120_235959 - 1_generate_graph_20260120_235959.py
    Reason: Adding PathManager integration
  20260120_180000 - 1_generate_graph_20260120_180000.py
    Reason: Initial backup

Total scripts archived: 10
Total versions: 25
```

### View History for Specific Script
```python
from archive_manager import ArchiveManager

am = ArchiveManager()
history = am.get_archive_history('1_generate_graph.py')

for entry in history:
    print(f"{entry['timestamp']}: {entry['reason']}")
```

---

## Restoring Scripts

### Restore Most Recent Version
```python
from archive_manager import ArchiveManager

am = ArchiveManager()
am.restore_script('1_generate_graph.py')
```

### Restore Specific Version
```python
am.restore_script('1_generate_graph.py', timestamp='20260120_235959')
```

**Note**: Restoring automatically creates a backup of the current version before restoring.

---

## Maintenance

### Clean Old Archives

Keep only the last N versions per script:

```python
from archive_manager import ArchiveManager

am = ArchiveManager()
am.clean_old_archives(keep_last_n=5)  # Keep last 5 versions per script
```

Command line:
```bash
python archive_manager.py clean 5
```

---

## Archive Policy Rules

### **Rule 1: Always Archive Before Editing**
Before making ANY changes to a script, create an archive:

```python
from archive_manager import archive_before_edit

archive_before_edit('1_generate_graph.py', 'Your reason here')
# Now make your edits
```

### **Rule 2: Provide Meaningful Reasons**
Always include a reason when archiving:
- ✅ Good: "Adding PathManager integration"
- ✅ Good: "Fix unicode encoding errors"
- ✅ Good: "Optimize path finding algorithm"
- ❌ Bad: "Updates"
- ❌ Bad: "Changes"

### **Rule 3: Archive Before Bulk Operations**
When updating multiple scripts (e.g., PathManager integration), archive them all first:

```python
scripts_to_update = [
    '1_generate_graph.py',
    '2_convert_graph.py',
    '3_analyze_circuit.py'
]

archive_before_edit(scripts_to_update, 'PathManager integration')
# Now edit all scripts
```

### **Rule 4: Keep Last 5 Versions**
Run cleanup monthly to keep only the last 5 versions per script:

```bash
python archive_manager.py clean 5
```

### **Rule 5: Never Delete Archive Manually**
Always use `clean_old_archives()` instead of manually deleting files. This keeps the index in sync.

---

## Workflow Example

### Scenario: Update Script 1 to Use PathManager

**Step 1: Archive Current Version**
```python
from archive_manager import archive_before_edit

archive_before_edit('1_generate_graph.py', 'Adding PathManager integration')
```

Output:
```
[OK] Archived 1_generate_graph.py -> 1_generate_graph_20260120_235959.py
     Reason: Adding PathManager integration
```

**Step 2: Make Your Edits**
Edit `1_generate_graph.py` to use PathManager.

**Step 3: Test Changes**
```bash
python scripts/1_generate_graph.py --prompt "The capitol of Texas is"
```

**Step 4 (If Needed): Restore Previous Version**
If something goes wrong:
```python
from archive_manager import ArchiveManager

am = ArchiveManager()
am.restore_script('1_generate_graph.py')  # Restores most recent backup
```

---

## Integration with Git

The archive system complements Git:

- **Git**: Tracks committed changes, branches, releases
- **Archive**: Tracks uncommitted work-in-progress versions

Archive files should be added to `.gitignore`:

```
# .gitignore
scripts/archive/*.py
scripts/archive/archive_index.json
```

This keeps the Git repository clean while preserving local development history.

---

## Benefits

1. **Safety**: Never lose work due to bad edits
2. **Traceability**: Know exactly when and why scripts were changed
3. **Quick Rollback**: Restore previous versions in seconds
4. **Development History**: See evolution of scripts over time
5. **Conflict Resolution**: Compare versions when debugging

---

## Archive vs Version Control

| Feature | Archive System | Git |
|---------|---------------|-----|
| **Purpose** | Local backup before edits | Version control for team |
| **Scope** | Single file changes | Entire codebase |
| **Granularity** | Every edit | Commits only |
| **History** | Timestamped snapshots | Commit graph |
| **Storage** | Local only | Remote + local |
| **Best For** | WIP backups | Release management |

**Use Both**: Archive for safety during development, Git for team collaboration and releases.

---

## FAQ

**Q: How many versions should I keep?**
A: Keep last 5 versions per script. Clean monthly with `clean_old_archives(5)`.

**Q: What if I forget to archive before editing?**
A: Create an archive immediately after realizing. Mark reason as "After edit - retroactive backup".

**Q: Can I archive non-Python files?**
A: Yes! Archive any file type:
```python
am.archive_script('README.md', 'Documentation update')
```

**Q: How do I bulk archive all scripts?**
A:
```python
from pathlib import Path
from archive_manager import ArchiveManager

am = ArchiveManager()
scripts = [f.name for f in Path('scripts').glob('*.py') if not f.name.startswith('archive')]
am.archive_scripts(scripts, 'Bulk backup before major refactor')
```

**Q: Where is the archive stored?**
A: `scripts/archive/` directory, with index at `scripts/archive/archive_index.json`.

---

## Initial Setup Complete

The archive system has been initialized. To create initial backups of all current scripts:

```bash
cd neuronpedia_pipeline/scripts
python archive_manager.py list  # Verify it works
```

Then in Python:
```python
from pathlib import Path
from archive_manager import ArchiveManager

am = ArchiveManager()

# Get all Python scripts (excluding archive_manager itself)
scripts = [f.name for f in Path('.').glob('*.py') if f.name != 'archive_manager.py']

# Create initial archives
am.archive_scripts(scripts, 'Initial backup - before PathManager integration')
```

---

**Last Updated**: 2026-01-20
**Version**: 1.0
**Maintainer**: Neuronpedia Pipeline Team
