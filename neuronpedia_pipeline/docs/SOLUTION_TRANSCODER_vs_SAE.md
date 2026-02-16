# SOLUTION: Transcoder vs SAE Feature Mismatch

## 🎯 ROOT CAUSE IDENTIFIED!

Our circuit data uses **GemmaScope Transcoders** but we're querying the **SAE API endpoint**.

### Evidence from Raw Graph Metadata

```json
{
  "info": {
    "source_urls": [
      "https://neuronpedia.org/gemma-2-2b/gemmascope-transcoder-16k",
      "https://huggingface.co/google/gemma-scope-2b-pt-transcoders"
    ],
    "transcoder_set": "gemma",
    "generator": {
      "name": "circuit-tracer by Hanna & Piotrowski"
    }
  }
}
```

**Key Finding:** Circuit Tracer uses `gemmascope-transcoder-16k`, NOT `gemmascope-res-16k`

---

## 🔍 Understanding the Difference

### SAEs (Sparse Autoencoders)
- Traditional interpretability approach
- Learn features from activations
- URL format: `.../gemmascope-res-16k/...`

### Transcoders
- Newer approach by Google DeepMind
- Translate between layers
- URL format: `.../gemmascope-transcoder-16k/...`
- **Our circuit data uses THESE**

---

## ✅ THE FIX

Change the SAE layer format from `res-16k` to `transcoder-16k`

### Current (Wrong):
```python
sae_layer = f"{layer}-gemmascope-res-16k"
# Example: "5-gemmascope-res-16k"
```

### Correct:
```python
sae_layer = f"{layer}-gemmascope-transcoder-16k"
# Example: "5-gemmascope-transcoder-16k"
```

---

## 📝 Implementation Plan

### File to Modify:
**`neuronpedia_pipeline/scripts/feature_description_fetcher.py`**

### Current Code (Lines ~55-70):
```python
def get_sae_layer_name(self, layer: int) -> str:
    """Get SAE layer name in Neuronpedia format"""
    return f"{layer}-gemmascope-res-16k"
```

### New Code:
```python
def get_sae_layer_name(self, layer: int, use_transcoder: bool = True) -> str:
    """
    Get SAE layer name in Neuronpedia format.

    Args:
        layer: Layer number (0-25)
        use_transcoder: If True, use transcoder format (for Circuit Tracer data)
                       If False, use SAE res format (for traditional SAE features)

    Returns:
        Layer name like "5-gemmascope-transcoder-16k" or "5-gemmascope-res-16k"
    """
    layer_type = "transcoder" if use_transcoder else "res"
    return f"{layer}-gemmascope-{layer_type}-16k"
```

### Add Config Option:
**`neuronpedia_pipeline/config/neuronpedia_config.yaml`**

```yaml
model:
  name: "gemma-2-2b"
  layers: 26
  feature_type: "transcoder"  # "transcoder" or "sae"
```

---

## 🧪 Testing Plan

### Test 1: Verify transcoder endpoint works
```bash
# Our circuit feature: L5_F7993995
# Using transcoder endpoint
python query_feature_semantics.py --layer 5 --feature-id 7993995 --use-transcoder
```

**Expected:** 200 response with activation examples

### Test 2: Compare transcoder vs SAE
```bash
# Same layer, low feature ID, try both
python query_feature_semantics.py --layer 0 --feature-id 41  # SAE (current)
python query_feature_semantics.py --layer 0 --feature-id 41 --use-transcoder  # Transcoder (new)
```

**Expected:** Different results (different feature sets)

### Test 3: Bottleneck feature from southern state
```bash
# The famous L5_F7993995 bottleneck
python query_feature_semantics.py --feature L5_F7993995 --use-transcoder
```

**Expected:** Description of what this feature detects

---

## 📊 Why This Matters

### Before Fix:
- ❌ Can't query our circuit features (404 errors)
- ❌ Can't understand bottleneck semantics
- ❌ Stuck on semantic taxonomy Stage 1

### After Fix:
- ✅ Query actual bottleneck features (L5_F7993995)
- ✅ Get activation examples for semantic analysis
- ✅ Build taxonomy from our circuit data
- ✅ Unblocks Phase 2 of research plan

---

## 🚀 Implementation Steps

1. **Modify `feature_description_fetcher.py`** (5 min)
   - Update `get_sae_layer_name()` to support transcoders
   - Add `use_transcoder` parameter (default=True for our use case)

2. **Update config** (2 min)
   - Add `feature_type: "transcoder"` to config
   - Document the difference in comments

3. **Test with L5_F7993995** (5 min)
   - Query the bottleneck feature
   - Verify we get activation examples
   - Document what it detects

4. **Update query tool** (3 min)
   - Add `--use-transcoder` flag to `query_feature_semantics.py`
   - Make it default to True (match our data source)

**Total Time:** ~15 minutes to implement and test

---

## 📚 References

**Neuronpedia Transcoder Page:**
https://neuronpedia.org/gemma-2-2b/gemmascope-transcoder-16k

**HuggingFace Transcoders:**
https://huggingface.co/google/gemma-scope-2b-pt-transcoders

**Circuit Tracer Docs:**
https://github.com/safety-research/circuit-tracer

---

## 🎯 Next Actions

1. Implement the fix (15 min)
2. Test L5_F7993995 (5 min)
3. Document findings (10 min)
4. Proceed with semantic taxonomy (Stage 1 of Phase 2)

**This fix unblocks the entire semantic analysis pipeline!**
