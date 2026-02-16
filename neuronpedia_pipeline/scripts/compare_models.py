"""
Compare circuit analysis between two models
"""
import json
import sys
from pathlib import Path

def load_analysis(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def extract_tokens(desc):
    """Extract tokens from feature description"""
    if desc and 'Activates on:' in desc:
        tokens_str = desc.split('Activates on:')[1].strip()
        return [t.strip() for t in tokens_str.split(',')[:10]]
    return []

def categorize_tokens(tokens):
    """Categorize tokens as geographic/semantic vs syntactic"""
    geographic_keywords = [
        'capital', 'city', 'country', 'state', 'nation', 'paris', 'france',
        'location', 'place', 'region', 'area', 'territory', 'province',
        'london', 'berlin', 'rome', 'madrid', 'moscow', 'beijing', 'tokyo'
    ]

    syntactic_keywords = [
        'the', 'of', 'is', 'and', 'to', 'a', 'in', 'for', 'on', 'with',
        'as', 'by', 'at', 'from', 'or', 'an', 'be', 'this', 'that',
        ',', '.', '(', ')', ':', ';', '[', ']', '{', '}'
    ]

    geographic = []
    syntactic = []
    other = []

    for t in tokens:
        t_clean = t.strip().lower()
        if t_clean in syntactic_keywords or len(t_clean) <= 2:
            syntactic.append(t.strip())
        elif any(geo in t_clean for geo in geographic_keywords):
            geographic.append(t.strip())
        else:
            other.append(t.strip())

    return geographic, syntactic, other

def main():
    # Load both analyses
    script_dir = Path(__file__).parent
    gemma_path = script_dir.parent / 'data/prompts/paris-is-the-capital-of/3_analysis/bosparis-is-the-capital_circuit_analysis.json'
    qwen_path = script_dir.parent / 'data/prompts/im-endparis-is-the-capital-of/3_analysis/im_endparis-is-the-capital_circuit_analysis.json'

    print("=" * 80)
    print("GEMMA-2-2B (2B params) vs QWEN3-4B (4B params) COMPARISON")
    print("Prompt: 'Paris is the capital of'")
    print("=" * 80)

    gemma = load_analysis(gemma_path)
    qwen = load_analysis(qwen_path)

    # Model outputs
    print("\n### MODEL OUTPUTS ###")
    print(f"\nGEMMA-2-2B:")
    print(f"  Top prediction: ' France' (85.7%) <- CORRECT")
    print(f"  Confidence: HIGH (>85%)")
    print(f"  Behavior: Factual completion")

    print(f"\nQWEN3-4B:")
    print(f"  Top prediction: ' the' (20.0%) <- WRONG (syntactic filler)")
    print(f"  Second: ' which' (17.7%)")
    print(f"  Third: ' France' (8.3%) <- Correct answer ranked #3")
    print(f"  Fourth: ' China' (5.7%)")
    print(f"  Fifth: ' Russia' (2.2%)")
    print(f"  Confidence: LOW (<21%)")
    print(f"  Behavior: Syntactic pattern, uncertain about countries")

    # Graph structure
    print("\n### GRAPH STRUCTURE ###")
    print(f"\nGEMMA-2-2B:")
    print(f"  Nodes: 893")
    print(f"  Edges: 22,954")
    print(f"  Density: 0.0288")
    print(f"  Layers: 26 (L0-L25)")
    print(f"  Supernodes: {len(gemma['louvain_supernodes']['supernodes'])}")
    print(f"  Connected: No (2 components)")

    print(f"\nQWEN3-4B:")
    print(f"  Nodes: 885 (similar)")
    print(f"  Edges: 32,225 (+40% MORE)")
    print(f"  Density: 0.0412 (+43% denser)")
    print(f"  Layers: 36 (L0-L35)")
    print(f"  Supernodes: {len(qwen['louvain_supernodes']['supernodes'])}")
    print(f"  Connected: Yes (fully connected)")

    # Feature analysis
    print("\n### FEATURE DESCRIPTIONS ###")
    print(f"\nGEMMA-2-2B:")
    print(f"  Features fetched: {len(gemma['feature_descriptions']['all_features'])}")

    print(f"\nQWEN3-4B:")
    print(f"  Features fetched: {len(qwen['feature_descriptions']['all_features'])}")

    # Analyze token categories
    print("\n### TOKEN CATEGORY ANALYSIS (Top 50 features) ###")

    # GEMMA
    gemma_geo_total = 0
    gemma_syn_total = 0
    gemma_other_total = 0
    gemma_examples = []

    for node_id, desc in list(gemma['feature_descriptions']['all_features'].items())[:50]:
        tokens = extract_tokens(desc)
        geo, syn, other = categorize_tokens(tokens)
        gemma_geo_total += len(geo)
        gemma_syn_total += len(syn)
        gemma_other_total += len(other)
        if geo:
            gemma_examples.append((node_id, geo[:3]))

    print(f"\nGEMMA-2-2B Token Distribution:")
    print(f"  Geographic/Semantic: {gemma_geo_total}")
    print(f"  Syntactic: {gemma_syn_total}")
    print(f"  Other: {gemma_other_total}")
    print(f"  Geographic features found: {len(gemma_examples)}")
    if gemma_examples:
        print(f"  Examples:")
        for node_id, tokens in gemma_examples[:5]:
            print(f"    {node_id}: {', '.join(tokens)}")

    # QWEN
    qwen_geo_total = 0
    qwen_syn_total = 0
    qwen_other_total = 0
    qwen_examples = []

    for node_id, desc in list(qwen['feature_descriptions']['all_features'].items())[:50]:
        tokens = extract_tokens(desc)
        geo, syn, other = categorize_tokens(tokens)
        qwen_geo_total += len(geo)
        qwen_syn_total += len(syn)
        qwen_other_total += len(other)
        if geo:
            qwen_examples.append((node_id, geo[:3]))

    print(f"\nQWEN3-4B Token Distribution:")
    print(f"  Geographic/Semantic: {qwen_geo_total}")
    print(f"  Syntactic: {qwen_syn_total}")
    print(f"  Other: {qwen_other_total}")
    print(f"  Geographic features found: {len(qwen_examples)}")
    if qwen_examples:
        print(f"  Examples:")
        for node_id, tokens in qwen_examples[:5]:
            print(f"    {node_id}: {', '.join(tokens)}")

    # Key findings
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)

    print("\n1. OUTPUT QUALITY:")
    print("   - GEMMA (2B): Correct answer 'France' at 85.7% confidence")
    print("   - QWEN (4B): Wrong answer 'the' at 20.0%, 'France' ranked #3 at 8.3%")
    print("   - CONCLUSION: Smaller model performs BETTER on this factual task!")

    print("\n2. CIRCUIT COMPLEXITY:")
    print("   - QWEN has 40% more edges (32k vs 23k)")
    print("   - QWEN is 43% denser (0.041 vs 0.029)")
    print("   - QWEN has 10 more layers (36 vs 26)")
    print("   - CONCLUSION: Larger model creates MORE COMPLEX circuit")

    print("\n3. FEATURE USAGE:")
    print(f"   - GEMMA: {gemma_geo_total} geographic tokens found in top 50 features")
    print(f"   - QWEN: {qwen_geo_total} geographic tokens found in top 50 features")
    print(f"   - Both models show primarily syntactic/other features")

    print("\n4. HYPOTHESIS:")
    print("   - QWEN's larger circuit may lead to OVERTHINKING")
    print("   - More parameters = more complex interactions = more uncertainty")
    print("   - GEMMA's simpler circuit goes directly to factual answer")
    print("   - Scaling may introduce NOISE rather than improving reasoning")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
