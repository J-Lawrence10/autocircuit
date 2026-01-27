# File Organization - Neuronpedia Pipeline

## Overview

This document defines the **canonical file structure** for the Neuronpedia interpretability pipeline. All scripts use `PathManager` to ensure consistent organization.

---

## 🗂️ Directory Structure

```
neuronpedia_pipeline/
├── data/
│   ├── prompts/                    # Per-prompt analyses
│   │   ├── the-capitol-of-texas-is/
│   │   ├── dallas-is-located-in-the-state-of/
│   │   └── ... (one folder per prompt)
│   │
│   └── cross_analysis/             # Cross-prompt comparisons
│       ├── geography-domain-5prompts/
│       ├── politics-vs-geography/
│       └── ... (one folder per analysis)
│
├── scripts/                        # All pipeline scripts
│   ├── path_manager.py            # Centralized path management
│   ├── 1_generate_graph.py
│   ├── 2_convert_graph.py
│   └── ...
│
└── ... (other dirs)
```

---

## 📋 Per-Prompt Structure

Each prompt gets its own folder with consistent internal organization:

```
data/prompts/{prompt-slug}/
├── 1_generation/
│   ├── raw_graph.json              # Original from Neuronpedia API
│   └── metadata.json               # Prompt, model, slug, timestamps
│
├── 2_conversion/
│   ├── converted_graph.json        # NetworkX-compatible format
│   └── conversion_stats.json       # Node/edge counts, layers
│
├── 3_analysis/
│   ├── circuit_analysis.json       # Full analysis output
│   ├── supernodes.json             # Louvain communities
│   └── layer_groups.json           # Theory-driven groups
│
├── 4_visualizations/
│   ├── supernode_overview.png
│   ├── layer_distribution.png
│   ├── thought_progression.png
│   ├── feature_importance.png
│   ├── information_flow.png
│   ├── activation_heatmap.png
│   ├── supernode_connections.png
│   └── summary_dashboard.png       # (8 total visualizations)
│
├── 7_minimal_pathways/             # Optional: Script 7
│   ├── minimal_circuit.json
│   └── pathway_comparison.png
│
├── 8_evolution/                    # Optional: Script 8
│   ├── evolution_data.json
│   ├── evolution_report.txt
│   └── evolution_heatmap.png
│
├── 9_steering/                     # Optional: Script 9
│   ├── steering_targets.json
│   └── targets_viz.png
│
└── 10_polysemanticity/             # Optional: Script 10
    ├── purity_scores.json
    ├── purity_report.txt
    └── purity_viz.png
```

---

## 📝 Naming Conventions

### 1. Prompt Slugs (Folder Names)

**Format**: lowercase, hyphens, max 50 chars

**Rules**:
- Remove `<bos>` tag
- Convert to lowercase
- Replace spaces/punctuation with `-`
- Remove leading/trailing `-`
- Truncate to 50 characters

**Examples**:
```python
"The capitol of Texas is"                    → "the-capitol-of-texas-is"
"Dallas is located in the state of"          → "dallas-is-located-in-the-state-of"
"<bos>The political party of Joe Biden is"   → "the-political-party-of-joe-biden-is"
```

**Implementation**:
```python
from path_manager import PathManager
pm = PathManager()
slug = pm.slugify("The capitol of Texas is")  # Returns: "the-capitol-of-texas-is"
```

---

### 2. Step Directories

**Format**: `{number}_{name}/`

**Standard Steps**:
```
1_generation/       # Raw data from Neuronpedia
2_conversion/       # NetworkX conversion
3_analysis/         # Supernode detection + analysis
4_visualizations/   # All PNG outputs
7_minimal_pathways/ # Optional: Minimal circuit
8_evolution/        # Optional: Layer evolution
9_steering/         # Optional: Intervention targets
10_polysemanticity/ # Optional: Semantic purity
```

**Why numbered?**
- Enforces execution order
- Easy to see pipeline progress (which steps completed)
- Allows gaps for optional analyses

---

### 3. File Names

**Principle**: Same filename across all prompts for same content type

#### Generation (Step 1):
```
raw_graph.json      # Original Neuronpedia response
metadata.json       # Prompt info, timestamps, model
```

#### Conversion (Step 2):
```
converted_graph.json    # NetworkX DiGraph JSON
conversion_stats.json   # Summary stats
```

#### Analysis (Step 3):
```
circuit_analysis.json   # Full analysis (supernodes + layers + flow)
supernodes.json         # Legacy format (for compatibility)
layer_groups.json       # Theory-driven groups
```

#### Visualizations (Step 4):
```
supernode_overview.png      # Louvain communities
layer_distribution.png      # Theory-driven groups
thought_progression.png     # Reasoning stages
feature_importance.png      # Top features per layer
information_flow.png        # Edge flow between layers
activation_heatmap.png      # Layer activation patterns
supernode_connections.png   # Supernode network
summary_dashboard.png       # All-in-one overview
```

#### Minimal Pathways (Step 7):
```
minimal_circuit.json        # Pruned circuit
pathway_comparison.png      # Before/after viz
```

#### Evolution (Step 8):
```
evolution_data.json         # Feature counts per layer
evolution_report.txt        # Human-readable analysis
evolution_heatmap.png       # Heatmap visualization
```

#### Steering (Step 9):
```
steering_targets.json       # Ranked intervention targets
targets_viz.png             # Top targets bar chart
```

#### Polysemanticity (Step 10):
```
purity_scores.json          # Purity per supernode
purity_report.txt           # Human-readable analysis
purity_viz.png              # Purity distribution
```

---

## 🔄 Cross-Analysis Structure

```
data/cross_analysis/{analysis-name}/
├── metadata.json                   # Which prompts, when analyzed
├── feature_overlap.json            # Jaccard similarity matrix
├── supernode_matches.json          # Matched supernodes with scores
├── consensus_supernodes.json       # Clusters appearing in majority
├── analysis_report.txt             # Human-readable summary
├── overlap_heatmap.png             # Feature overlap visualization
└── reuse_network.png               # Supernode reuse network
```

### Cross-Analysis Naming

**Format**: Descriptive + prompt count (when applicable)

**Examples**:
```
geography-domain-5prompts/          # 5 geography prompts
politics-domain-10prompts/          # 10 political prompts
politics-vs-geography/              # Cross-domain comparison
texas-capitol-variations/           # Prompt variations
```

**Why descriptive?**
- Easy to understand what's being compared
- Helps find related analyses
- Self-documenting

---

## 🔧 Using PathManager

### Import and Initialize

```python
from path_manager import PathManager

pm = PathManager()  # Auto-detects data directory
```

### Get Paths for a Prompt

```python
prompt = "The capitol of Texas is"

# Main directory
prompt_dir = pm.get_prompt_dir(prompt)
# Returns: data/prompts/the-capitol-of-texas-is/

# Specific files
raw_graph = pm.raw_graph_path(prompt)
# Returns: data/prompts/the-capitol-of-texas-is/1_generation/raw_graph.json

circuit_analysis = pm.circuit_analysis_path(prompt)
# Returns: data/prompts/the-capitol-of-texas-is/3_analysis/circuit_analysis.json

viz_file = pm.visualization_path(prompt, 'supernode_overview')
# Returns: data/prompts/the-capitol-of-texas-is/4_visualizations/supernode_overview.png
```

### Get Cross-Analysis Paths

```python
analysis_name = "geography-domain-5prompts"

cross_dir = pm.get_cross_analysis_dir(analysis_name)
# Returns: data/cross_analysis/geography-domain-5prompts/

consensus_file = pm.cross_analysis_consensus_path(analysis_name)
# Returns: data/cross_analysis/geography-domain-5prompts/consensus_supernodes.json
```

### Save/Load Metadata

```python
# Save
metadata = {
    'model': 'gemma-2-2b',
    'num_nodes': 1025,
    'num_links': 31077
}
pm.save_metadata(prompt, metadata)

# Load
metadata = pm.load_metadata(prompt)
print(metadata['model'])  # 'gemma-2-2b'
```

---

## 🚀 Script Integration

### Before (Hardcoded Paths):
```python
# ❌ BAD - Different scripts use different path logic
output_file = f"data/graphs/{slug}/real_{slug}_analysis.json"
viz_dir = f"data/graphs/{slug}/visualizations"
```

### After (PathManager):
```python
# ✅ GOOD - Consistent across all scripts
from path_manager import PathManager
pm = PathManager()

output_file = pm.circuit_analysis_path(prompt)
viz_dir = pm.visualizations_dir(prompt)
```

---

## 📊 Migration from Old Structure

### Old Structure (Messy):
```
data/
├── graphs/
│   ├── thecapitolofthes-1768927787684/
│   │   ├── real_the_capitol_of_the_state_analysis.json
│   │   ├── real_the_capitol_of_the_state_converted.json
│   │   ├── graph_thecapitolofthes-1768927787684.json
│   │   └── visualizations/*.png
│   └── ... (slug-based, inconsistent)
│
├── cross_prompt_analysis/
│   └── politics_vs_geography/
│       └── cross_prompt_analysis.txt
│
├── minimal_pathways/
│   └── thecapitolofthes-1768927787684/
│       └── minimal_pathway.json
│
└── ... (scattered)
```

### New Structure (Organized):
```
data/
├── prompts/
│   └── the-capitol-of-the-state-containing-dallas/
│       ├── 1_generation/raw_graph.json
│       ├── 2_conversion/converted_graph.json
│       ├── 3_analysis/circuit_analysis.json
│       ├── 4_visualizations/*.png
│       └── 7_minimal_pathways/minimal_circuit.json
│
└── cross_analysis/
    └── politics-vs-geography/
        ├── analysis_report.txt
        └── consensus_supernodes.json
```

### Run Migration:

```bash
# Dry run (preview changes)
python scripts/migrate_to_new_structure.py --dry-run

# Actual migration (creates backup first)
python scripts/migrate_to_new_structure.py

# Skip backup (not recommended)
python scripts/migrate_to_new_structure.py --no-backup
```

---

## ✅ Benefits

### 1. **Predictable Structure**
Every prompt has the same internal organization. If you know one, you know all.

### 2. **Easy Navigation**
```bash
cd data/prompts/the-capitol-of-texas-is/
ls  # See all analysis steps at a glance
cd 3_analysis/
cat circuit_analysis.json  # Consistent filename
```

### 3. **Script Simplification**
All scripts use `PathManager` → no path logic duplication

### 4. **Cross-Prompt Discovery**
```python
pm = PathManager()
prompts = pm.get_all_analyzed_prompts()  # Find all available data
```

### 5. **Clear Progress Tracking**
```bash
ls data/prompts/my-prompt/
# See which steps completed:
# 1_generation/ ✓
# 2_conversion/ ✓
# 3_analysis/ ✓
# 4_visualizations/ ✓
# 7_minimal_pathways/ ✗ (not run yet)
```

---

## 📦 Deliverables Per Prompt

### Minimum (Core Pipeline):
- ✅ `1_generation/` - Raw data
- ✅ `2_conversion/` - NetworkX graph
- ✅ `3_analysis/` - Supernodes + layers
- ✅ `4_visualizations/` - 8 PNG files

### Optional (Advanced):
- ⭐ `7_minimal_pathways/` - Circuit reduction
- ⭐ `8_evolution/` - Layer transformations
- ⭐ `9_steering/` - Intervention targets
- ⭐ `10_polysemanticity/` - Semantic purity

---

## 🔍 Finding Data

### List All Analyzed Prompts:
```python
from path_manager import PathManager
pm = PathManager()

for prompt in pm.get_all_analyzed_prompts():
    print(prompt)
```

### Find Analysis Files for Multiple Prompts:
```python
prompts = [
    "The capitol of Texas is",
    "Dallas is located in the state of"
]

analysis_files = pm.find_analysis_for_prompts(prompts)
for file in analysis_files:
    print(file)
# data/prompts/the-capitol-of-texas-is/3_analysis/circuit_analysis.json
# data/prompts/dallas-is-located-in-the-state-of/3_analysis/circuit_analysis.json
```

---

## 🎯 Next Steps

1. **Run Migration**: `python scripts/migrate_to_new_structure.py`
2. **Update Scripts**: Integrate `PathManager` into Scripts 1-10
3. **Test Pipeline**: Run full pipeline on new prompt
4. **Validate**: Ensure all files in correct locations

---

## 📚 Reference

### PathManager API

**Prompt Directories**:
- `get_prompt_dir(prompt)` - Main directory
- `generation_dir(prompt)` - Step 1
- `conversion_dir(prompt)` - Step 2
- `analysis_dir(prompt)` - Step 3
- `visualizations_dir(prompt)` - Step 4
- `minimal_pathways_dir(prompt)` - Step 7
- `evolution_dir(prompt)` - Step 8
- `steering_dir(prompt)` - Step 9
- `polysemanticity_dir(prompt)` - Step 10

**File Paths**:
- `raw_graph_path(prompt)`
- `metadata_path(prompt)`
- `converted_graph_path(prompt)`
- `circuit_analysis_path(prompt)`
- `visualization_path(prompt, viz_name)`
- `minimal_circuit_path(prompt)`
- `evolution_data_path(prompt)`
- `steering_targets_path(prompt)`
- `polysemanticity_data_path(prompt)`

**Cross-Analysis**:
- `get_cross_analysis_dir(name)`
- `cross_analysis_metadata_path(name)`
- `cross_analysis_consensus_path(name)`
- `cross_analysis_report_path(name)`

**Utilities**:
- `slugify(text)` - Convert prompt to slug
- `save_metadata(prompt, metadata)`
- `load_metadata(prompt)`
- `get_all_analyzed_prompts()`
- `find_analysis_for_prompts(prompts)`

---

**Last Updated**: 2026-01-20
**Version**: 1.0
**Maintainer**: Neuronpedia Pipeline Team
