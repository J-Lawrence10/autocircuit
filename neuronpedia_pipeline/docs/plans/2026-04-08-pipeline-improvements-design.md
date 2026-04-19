# Pipeline Improvements Design

**Date:** 2026-04-08
**Scope:** 3 features — programmatic upload, batch mode, random forest classifier
**Primary interface:** Claude Code (CLIs minimal)

## Feature 1: `--upload` flag (supernode_pipeline.py)

Adds direct upload to Neuronpedia after `export_annotated_graph()` writes the JSON.

**API flow (3 steps):**
1. `POST https://www.neuronpedia.org/api/graph/signed-put` with `{filename, contentLength, contentType: "application/json"}` → `{url, putRequestId}`
2. `PUT` JSON bytes to pre-signed S3 URL (no auth)
3. `POST https://www.neuronpedia.org/api/graph/save-to-db` with `{putRequestId}` → `{url}` (viewable graph URL)

Auth: `x-api-key` header from `config/neuronpedia_config.yaml`.

**CLI additions:**
- `--upload` — upload after pipeline completes
- `--upload-only PATH` — skip pipeline, upload an existing `annotated_graph.json`

**Output:** Save URL to `upload_result.json`, print to stdout. On failure, keep local file and print manual upload instructions.

## Feature 2: Batch mode (supernode_pipeline.py)

**CLI additions:**
- Multiple positional prompts: `supernode_pipeline.py "prompt 1" "prompt 2"`
- `--batch-file PATH` — one prompt per line, `#` comments, blank lines skipped

**Behavior:**
- Sequential processing; one failure doesn't stop others
- Combined with `--upload` to batch-upload all
- Final summary: prompt → status → output dir → URL
- Save `batch_results.json` in the parent output directory

## Feature 3: Random Forest Semantic Classifier

**New file:** `neuronpedia_pipeline/scripts/semantic_classifier_rf.py`

**Features (per SAE feature):**
- TF-IDF of NP explanation text (max_features=500)
- Layer number
- Activation count
- Cross-circuit frequency
- Unicode script flag (non-latin presence)

**Training data:** `semantic_taxonomy_annotations.csv` `manual_category` column (~80 features)

**Model:** `sklearn.ensemble.RandomForestClassifier(n_estimators=100, max_depth=8)`, leave-one-out CV given small dataset.

**Persistence:** `data/classifier/rf_classifier.joblib` (model + vectorizer bundle)

**CLI:**
- `--train` — train from annotations CSV
- `--evaluate` — LOO cross-validation metrics
- `--predict "explanation text" --layer N` — classify a single feature

**Integration:** Exports `classify_feature(explanation, layer, activation_count, frequency)` function. `annotate_features_v2.py` can call this as drop-in replacement, falling back to keyword classifier if joblib missing.

**Dependencies added:** `scikit-learn`, `joblib` (added to `config/requirements.txt`)

## Out of scope
- No retries on upload failure (fail fast)
- No QWEN support (blocked on upstream API)
- No embedding-based classifier (future upgrade path)
