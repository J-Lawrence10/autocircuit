# Feature ID Mapping Status - Current Findings

## ✅ GOOD NEWS: API Query Tool Works!

The fix is successful - `query_feature_semantics.py` correctly queries the Neuronpedia API when given valid SAE feature IDs.

### Test Results

**Working Query:**
```bash
python query_feature_semantics.py --layer 0 --feature-id 41
```

**Output:**
```
Feature: L0_F41
Category: SEMANTICS
Description: Activates on: صوتيه, expandindo, חיצוניים
```

✅ **200 Response** - API connection working
✅ **Unicode handling fixed** - International characters display correctly
✅ **Semantic categorization working** - Auto-classified as SEMANTICS

---

## ❌ PROBLEM: Feature ID Mismatch

The feature IDs from our circuit analysis **don't exist** in Neuronpedia's database.

### Failed Queries

| Our Feature ID | Layer | Status | Note |
|----------------|-------|--------|------|
| 7993995 | 5 | 404 | From southern state bottleneck |
| 100614194 | 10 | 404 | From water boils circuit |
| 88478228 | 24 | 404 | From water boils circuit |

### Working Queries

| Feature ID | Layer | Status | Description |
|------------|-------|--------|-------------|
| 41 | 0 | ✅ 200 | International text tokens |

---

## 🔍 Root Cause Analysis

### Theory 1: Different SAE Releases

**Hypothesis:** Our Circuit Tracer data uses SAE features from a different release than what's in Neuronpedia's current database.

**Evidence:**
- Feature IDs like 7993995, 100614194 are very large numbers (>7M, >100M)
- Neuronpedia feature 41 is a small number
- Suggests different SAE training runs or releases

**Investigation Needed:**
- Check Circuit Tracer API documentation for SAE version
- Check Neuronpedia API for available SAE releases
- Look for version/release metadata in raw graph JSON

### Theory 2: Feature ID Scheme Changed

**Hypothesis:** The feature numbering changed between SAE versions.

**Evidence:**
- Large gaps in feature IDs (41 vs 7M+)
- Different models may have different SAE sizes

**Investigation Needed:**
- What's the max feature ID in each layer?
- Are features sequential or sparse?

### Theory 3: Model/Layer Mismatch

**Hypothesis:** We're querying the wrong model or SAE layer configuration.

**Evidence:**
- We use `gemma-2-2b` as model name
- Layer format: `{layer}-gemmascope-res-16k`
- Maybe there are multiple SAE configs per layer?

**Investigation Needed:**
- Check what SAE configs are available for gemma-2-2b
- Try different layer formats (res-16k vs res-32k vs res-65k?)

---

## 🎯 Next Steps

### Option A: Find Feature ID Mapping (Recommended)

**Goal:** Map our circuit feature IDs to Neuronpedia feature IDs

**Approach:**
1. Check raw Circuit Tracer JSON for SAE version metadata
2. Query Neuronpedia API for available SAE releases
3. Find documentation on feature ID schemes
4. Create mapping table if different versions exist

**Files to Check:**
- `data/prompts/*/1_generation/*_raw_graph.json` - Look for SAE metadata
- Neuronpedia API docs - Check for version/release endpoints

### Option B: Use Available Features (Fallback)

**Goal:** Build semantic taxonomy using features that DO exist in Neuronpedia

**Approach:**
1. Query low feature IDs (0-1000) to find what's available
2. Build taxonomy from working features
3. Accept we can't query our specific bottleneck features

**Trade-off:** Can't directly analyze L5_F7993995, but can still:
- Understand general semantic patterns
- Build taxonomy methodology
- Apply to other prompts/models later

### Option C: Manual Feature Inspection (Alternative)

**Goal:** Understand features without Neuronpedia API

**Approach:**
1. Use circuit activation patterns from our data
2. Manually inspect what tokens activate each feature
3. Categorize based on activation strength patterns

**Trade-off:** More manual work, less concrete activation examples

---

## 🔧 Technical Details

### API URL Format (Confirmed Working)

```
https://neuronpedia.org/api/feature/{model}/{sae_layer}/{feature_id}
```

**Example Working URL:**
```
https://neuronpedia.org/api/feature/gemma-2-2b/0-gemmascope-res-16k/41
```

**Example Failing URL:**
```
https://neuronpedia.org/api/feature/gemma-2-2b/5-gemmascope-res-16k/7993995
→ 404 (feature doesn't exist in this SAE)
```

### Script Status

**`query_feature_semantics.py`** - ✅ WORKING

**Features:**
- ✅ Direct feature ID queries work
- ✅ Label parsing works (L0_F41 → layer=0, feature=41)
- ✅ Unicode handling fixed
- ✅ Semantic categorization preliminary
- ⏳ Bottleneck analysis pending (needs feature mapping)

---

## 📊 Immediate Action Items

1. **Check Circuit Tracer raw graph for SAE metadata** (15 min)
   ```bash
   # Look for version/release info
   cat data/prompts/im-endthe-southern-most-us-state-is/1_generation/*_raw_graph.json | grep -i "sae\|version\|release" | head -20
   ```

2. **Try different SAE layer formats** (15 min)
   ```bash
   # Test if other SAE sizes exist
   python query_feature_semantics.py --layer 5 --feature-id 41  # Try layer 5
   # Try querying small feature IDs across layers
   ```

3. **Document what features ARE available** (30 min)
   - Query features 0-100 in layers 0, 5, 10, 15, 20, 25
   - Build list of working features
   - See if there's a pattern

4. **Decision point:** Continue with Option A (mapping) or pivot to Option B (use available features)

---

## 💡 Key Insight

**The tool works correctly** - this is a **data compatibility issue**, not a code bug. The fix we implemented (passing SAE feature IDs directly) is the right approach. We just need to either:
1. Find the mapping between our features and Neuronpedia's features, OR
2. Use different features that exist in Neuronpedia's database

The semantic taxonomy methodology is still valid - we just need features we can actually query!
