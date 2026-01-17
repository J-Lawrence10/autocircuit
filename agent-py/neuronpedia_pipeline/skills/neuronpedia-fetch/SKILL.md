# Neuronpedia Fetch

Generate attribution graphs from Neuronpedia Circuit Tracer API for circuit analysis.

## Instructions

When the user wants to fetch or generate an attribution graph:

1. **Extract the prompt** from the user's request
   - Look for quoted text or the actual prompt they want to analyze
   - If not provided, ask the user for the specific prompt

2. **Navigate to the pipeline directory**:
   ```bash
   cd neuronpedia_pipeline
   ```

3. **Check if API key is configured**:
   - Verify `config/neuronpedia_config.yaml` has an API key
   - If missing, inform the user to add their Neuronpedia API key

4. **Run the generation script**:
   ```bash
   python scripts/1_generate_graph.py
   ```
   - Note: The script currently has the prompt hardcoded at line 107
   - If the user's prompt differs, you may need to temporarily edit that line or ask them to edit it

5. **Wait for completion** (typically 10-15 seconds)
   - The script will connect to Neuronpedia API
   - Submit the prompt for Circuit Tracer analysis
   - Download the resulting graph from S3

6. **Report the results to the user**:
   - Graph file location (e.g., `data/graphs/real_japan_currency.json`)
   - Number of nodes (typically 500-1500)
   - Number of edges (typically 10K-60K)
   - Layers covered (usually 26 layers: L0-L25)
   - File size (typically 2-6 MB)

## Output

- **File created**: `data/graphs/real_{prompt_slug}.json`
- **File size**: 4-6 MB
- **Content**: Raw Circuit Tracer attribution graph in JSON format
- **Metadata**: Includes Circuit Tracer version, timestamp, model info

## Example interaction

**User**: "Fetch a graph for 'The currency in Japan is'"

**You should**:
1. Navigate to neuronpedia_pipeline
2. Run the generation script
3. Report: "✓ Graph generated successfully:
   - File: data/graphs/real_japan_currency.json
   - Nodes: 962
   - Edges: 35,561
   - Layers: 26 (L0-L25)
   - Size: 4.3 MB

   Next step: Run `/neuronpedia-convert` to prepare for analysis"

## Common issues

- **"API key not found"**: User needs to add API key to `config/neuronpedia_config.yaml`
- **"Graph generation failed"**: Check internet connection, verify API is accessible
- **"Timeout"**: API may be busy, suggest retry in a few moments
- **Connection errors**: Verify Neuronpedia API status

## When to use this skill

- User asks to "fetch a graph" or "generate a graph"
- User wants to analyze a specific prompt
- User says "get attribution data for [prompt]"
- Starting a new circuit analysis
- User asks "what features activate for [text]"

## Next steps after this skill

After fetching, the user typically wants to:
1. Run `/neuronpedia-convert` - Convert the raw graph to pipeline format
2. Run `/neuronpedia-validate` - Verify the data is genuine
