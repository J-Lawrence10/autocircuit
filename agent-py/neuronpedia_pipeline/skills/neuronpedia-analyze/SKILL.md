# Neuronpedia Analyze

Detect supernodes and analyze circuit structure using Louvain community detection.

## Instructions

When the user wants to analyze circuit structure:

1. **Navigate to the pipeline directory**:
   ```bash
   cd neuronpedia_pipeline
   ```

2. **Identify the converted graph**:
   - Auto-detects the latest `*_converted.json` file
   - Or use a specific file if the user specifies

3. **Run the analysis script**:
   ```bash
   python scripts/3_analyze_circuit.py
   ```
   - Takes 5-10 seconds typically
   - Runs Louvain community detection algorithm
   - Calculates betweenness centrality for bottlenecks
   - Ranks features by importance

4. **Report the analysis results**:
   - Number of supernodes detected
   - Description of each supernode:
     - Size (number of nodes)
     - Role (main processing, bottleneck, input/output)
     - Layers covered
     - Average activation
     - Betweenness centrality if high (>0.5 indicates bottleneck)
   - Top 5 features by activation (with layer and activation value)
   - Circuit statistics:
     - Graph density
     - Modularity score
     - Average path length
     - Clustering coefficient

## Output

- **File created**: `data/graphs/real_{name}_supernodes.json`
- **File size**: 50-100 KB
- **Console output**: Detailed statistics about circuit structure

## Example interaction

**User**: "Analyze the circuit structure"

**You should**:
1. Navigate to neuronpedia_pipeline
2. Run analysis script
3. Report: "✓ Analysis complete:

   **Supernodes detected**: 3

   - **SN3** (92 nodes): Main processing pathway
     - Layers: 0, 1, 2, 3, 5, 7, 9, 11
     - Average activation: 12.3

   - **SN7** (37 nodes): Critical bottleneck
     - Layers: 13, 15, 17
     - Average activation: 45.2
     - Betweenness: 0.82 (HIGH - information bottleneck)

   - **SN11** (41 nodes): Input processing
     - Layers: 0, 1, 2
     - Average activation: 8.7

   **Top 5 features**:
   1. L15_F376262: 150.290
   2. L24_F88478228: 124.506
   3. L15_F294512: 105.398
   4. L13_F33150139: 101.254
   5. L21_F98371329: 80.364

   **Circuit stats**:
   - Density: 0.0309 (sparse, hierarchical)
   - Modularity: 0.567 (strong community structure)

   Next step: Run `/neuronpedia-visualize` to create circuit diagrams"

## Common issues

- **"No supernodes detected"**: Try lowering minimum supernode size parameter
- **"One huge supernode"**: May need to adjust resolution parameter
- **"Low modularity (<0.3)"**: Graph may have weak community structure (can be normal)

## When to use this skill

- User asks to "analyze the circuit"
- User wants to find supernodes or bottlenecks
- After running `/neuronpedia-convert`
- User asks "what are the important features?"
- User wants to understand circuit structure

## Next steps after this skill

After analyzing:
1. Run `/neuronpedia-visualize` - Create visual circuit diagrams
2. Run `/neuronpedia-compare` - Compare with other prompts (if multiple graphs available)

## Key insight

This skill uses **Louvain community detection** (data-driven) rather than hard-coded layer grouping, making it 60-120x faster than manual approaches.
