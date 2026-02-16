# Deployment Checklist

**Use this checklist when deploying to Pi**

---

## Pre-Deployment Verification

### Local Testing (Before Pushing)

- [ ] **Validate all data is real**
  ```bash
  cd neuronpedia_pipeline
  python scripts/validate_real_data.py
  ```
  Expected: "✓ All data files are real Neuronpedia data!"

- [ ] **Check all scripts exist**
  ```bash
  ls scripts/*.py
  ```
  Expected: 7 Python files listed

- [ ] **Check all documentation exists**
  ```bash
  ls *.md
  ```
  Expected: 8 markdown files listed

- [ ] **Verify requirements.txt is complete**
  ```bash
  cat config/requirements.txt
  ```
  Expected: networkx, matplotlib, requests, pyyaml, numpy, python-louvain

---

## Deployment Steps

### Step 1: Copy to Pi

- [ ] **Option A: Via Git**
  ```bash
  git add neuronpedia_pipeline/
  git commit -m "Add production-ready pipeline"
  git push

  # On Pi:
  git pull
  ```

- [ ] **Option B: Direct SCP**
  ```bash
  scp -r neuronpedia_pipeline/ pi@YOUR_PI_IP:/home/pi/
  ```

- [ ] **Option C: USB/Network Share**
  - Copy neuronpedia_pipeline folder
  - Transfer to Pi

### Step 2: Pi Setup

- [ ] **Navigate to folder**
  ```bash
  ssh pi@YOUR_PI_IP
  cd neuronpedia_pipeline
  ```

- [ ] **Install dependencies**
  ```bash
  pip install -r config/requirements.txt
  ```

- [ ] **Add API key**
  ```bash
  nano config/neuronpedia_config.yaml
  # Add your Neuronpedia API key
  # Save: Ctrl+O, Enter, Ctrl+X
  ```

### Step 3: Test Installation

- [ ] **Test script 1 (Generate)**
  ```bash
  python scripts/1_generate_graph.py
  ```
  Expected: Graph generated in ~10 seconds

- [ ] **Test script 2 (Convert)**
  ```bash
  python scripts/2_convert_graph.py
  ```
  Expected: Converted file created

- [ ] **Test script 3 (Analyze)**
  ```bash
  python scripts/3_analyze_circuit.py
  ```
  Expected: Supernodes detected

- [ ] **Test script 4 (Visualize)**
  ```bash
  python scripts/4_visualize.py
  ```
  Expected: 5 PNG files created

- [ ] **Test script 5 (Compare)** (if you have 2+ graphs)
  ```bash
  python scripts/5_compare_prompts.py graph1.json graph2.json
  ```
  Expected: Comparison output

- [ ] **Test validation**
  ```bash
  python scripts/validate_real_data.py
  ```
  Expected: Real data confirmed

---

## Post-Deployment Verification

### Check Outputs

- [ ] **Verify graph files exist**
  ```bash
  ls data/graphs/
  ```
  Expected: .json files

- [ ] **Verify visualizations exist**
  ```bash
  ls data/visualizations/
  ```
  Expected: .png files

- [ ] **Check file sizes**
  ```bash
  du -h data/graphs/*.json
  ```
  Expected: MB-sized files (not KB)

### Run Full Pipeline Test

- [ ] **Complete end-to-end test**
  ```bash
  # Generate test prompt
  python scripts/1_generate_graph.py
  python scripts/2_convert_graph.py
  python scripts/3_analyze_circuit.py
  python scripts/4_visualize.py
  ```
  Expected: Completes in ~30 seconds

---

## Troubleshooting Common Issues

### "No module named 'networkx'"
→ Run: `pip install -r config/requirements.txt`

### "API key not found"
→ Edit: `config/neuronpedia_config.yaml`
→ Add: `api_key: "sk-np-YOUR-KEY"`

### "Graph generation failed"
→ Check internet connection
→ Verify API key is correct
→ Try shorter prompt

### "Permission denied"
→ Run: `chmod +x scripts/*.py`

### "No visualizations created"
→ Check matplotlib backend: `python -c "import matplotlib; print(matplotlib.get_backend())"`
→ If issues, install: `pip install matplotlib --upgrade`

---

## Performance Benchmarks

Expected execution times on Pi:

- Graph generation: 10-15 seconds
- Conversion: <1 second
- Analysis: 5-10 seconds
- Visualization: 10-20 seconds
- Comparison: 5-10 seconds

**Total pipeline**: 30-45 seconds on Pi (vs ~30 sec on desktop)

---

## Success Criteria

### ✅ Deployment Successful If:

- [ ] All dependencies installed without errors
- [ ] API key configured correctly
- [ ] Test graph generates successfully
- [ ] Conversion completes
- [ ] Supernodes detected
- [ ] 5 visualizations created
- [ ] Validation passes (real data confirmed)
- [ ] No errors in any script

### 📊 Quality Checks:

- [ ] Graph has 500+ nodes
- [ ] Supernodes detected (typically 3-5)
- [ ] Top features have activation >50
- [ ] Visualizations are readable
- [ ] File sizes are MB-scale (not KB)

---

## What to Do After Successful Deployment

### 1. Document Your Setup
- [ ] Note Pi model and specs
- [ ] Record typical execution times
- [ ] Save any custom configurations

### 2. Generate Test Dataset
- [ ] Create 3-5 different prompt graphs
- [ ] Run comparisons between them
- [ ] Look for patterns (Layer 15, L15_F376262)

### 3. Validate Discoveries
- [ ] Check if L15_F376262 appears in your graphs
- [ ] Calculate feature overlap percentages
- [ ] Compare with documented findings

### 4. Plan Phase 2
- [ ] Review NODE_STEERING_GUIDE.md
- [ ] Research Neuronpedia steering API
- [ ] Design first causal experiment

---

## Rollback Plan (If Issues)

### If Deployment Fails:

1. **Save error messages**
   ```bash
   python scripts/1_generate_graph.py 2> error.log
   cat error.log
   ```

2. **Check Python version**
   ```bash
   python --version
   ```
   Required: Python 3.8+

3. **Verify internet connectivity**
   ```bash
   ping neuronpedia.org
   ```

4. **Try minimal test**
   ```bash
   python -c "import networkx; print('OK')"
   python -c "import matplotlib; print('OK')"
   ```

5. **If all fails, fresh install**
   ```bash
   rm -rf neuronpedia_pipeline
   # Re-copy folder
   # Reinstall dependencies
   ```

---

## Support Resources

### Documentation Files
- `README.md` - Main guide
- `QUICK_REFERENCE.md` - Command reference
- `PIPELINE_STATUS.md` - Feature overview
- `READY_FOR_DEPLOYMENT.md` - Detailed deployment guide

### External Resources
- Neuronpedia: https://neuronpedia.org
- AutoCircuit: https://github.com/KKrampis/autocircuit
- Circuit Tracer: https://github.com/safety-research/circuit-tracer

---

## Version Information

- **Pipeline Version**: 1.0
- **Last Updated**: 2026-01-16
- **Tested On**: Windows 10, Python 3.11
- **Requires**: Python 3.8+, Internet connection
- **Phase**: Phase 1 complete, Phase 2 planned

---

## Final Checklist Summary

### Before Push
- [x] Code tested locally
- [x] Data validated (real, not mock)
- [x] Documentation complete
- [x] Requirements.txt updated

### During Deployment
- [ ] Folder copied to Pi
- [ ] Dependencies installed
- [ ] API key configured
- [ ] Test successful

### After Deployment
- [ ] Full pipeline runs
- [ ] Outputs validated
- [ ] Performance acceptable
- [ ] Ready for experiments

---

**When all checkboxes are complete, deployment is successful! ✅**

**Next step**: Generate your first custom prompt graph on Pi
