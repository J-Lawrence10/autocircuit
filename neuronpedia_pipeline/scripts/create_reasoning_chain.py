"""
Create Chain of Reasoning Summary
Shows step-by-step how the model processes the prompt to reach its output
"""

import json
from pathlib import Path
import argparse


def create_reasoning_chain(analysis_file, output_file):
    """Create a text-based chain of reasoning summary"""

    with open(analysis_file) as f:
        data = json.load(f)

    metadata = data['metadata']
    layer_groups = data['layer_groups']

    prompt = metadata['prompt'].replace('<bos>', '').strip()
    output = metadata.get('model_output', 'Unknown')
    confidence = metadata.get('output_probability', 0)

    # Build the reasoning chain
    chain = []
    chain.append("=" * 80)
    chain.append("CHAIN OF REASONING")
    chain.append("=" * 80)
    chain.append("")
    chain.append(f"PROMPT: \"{prompt}\"")
    chain.append(f"MODEL PREDICTION: \"{output}\" (confidence: {confidence:.1%})")
    chain.append("")
    chain.append("=" * 80)
    chain.append("HOW THE MODEL REASONED:")
    chain.append("=" * 80)
    chain.append("")

    # Stage 1: Input
    input_group = layer_groups['input']
    chain.append("STAGE 1: INPUT PROCESSING (Layers 0-5)")
    chain.append(f"  → {input_group['num_nodes']} features activated")
    chain.append(f"  → Strongest activation: {input_group['max_activation']:.1f}")
    chain.append("")
    chain.append("  Top Features:")
    for feat in input_group.get('top_features_with_descriptions', [])[:3]:
        desc = feat.get('description', 'No description')
        chain.append(f"    • {desc}")
    chain.append("")
    chain.append(f"  ↓ Sending {input_group['outgoing_edges']:,} connections forward")
    chain.append("")

    # Stage 2: Early Processing
    early_group = layer_groups['early_proc']
    chain.append("STAGE 2: EARLY PROCESSING (Layers 6-10)")
    chain.append(f"  → {early_group['num_nodes']} features activated")
    chain.append(f"  → Strongest activation: {early_group['max_activation']:.1f}")
    chain.append("")
    chain.append("  Top Features:")
    for feat in early_group.get('top_features_with_descriptions', [])[:3]:
        desc = feat.get('description', 'No description')
        chain.append(f"    • {desc}")
    chain.append("")
    chain.append(f"  ↓ Sending {early_group['outgoing_edges']:,} connections forward")
    chain.append("")

    # Stage 3: Middle Processing
    middle_group = layer_groups['middle_proc']
    chain.append("STAGE 3: MIDDLE PROCESSING (Layers 11-15) - CONCEPT FORMATION")
    chain.append(f"  → {middle_group['num_nodes']} features activated")
    chain.append(f"  → Strongest activation: {middle_group['max_activation']:.1f} ⭐ PEAK")
    chain.append("")
    chain.append("  Top Features:")
    for feat in middle_group.get('top_features_with_descriptions', [])[:3]:
        desc = feat.get('description', 'No description')
        chain.append(f"    • {desc}")
    chain.append("")
    chain.append(f"  ↓ Sending {middle_group['outgoing_edges']:,} connections forward")
    chain.append("")

    # Stage 4: Late Processing
    late_group = layer_groups['late_proc']
    chain.append("STAGE 4: LATE PROCESSING (Layers 16-20) - KNOWLEDGE RETRIEVAL")
    chain.append(f"  → {late_group['num_nodes']} features activated")
    chain.append(f"  → Strongest activation: {late_group['max_activation']:.1f}")
    chain.append("")
    chain.append("  Top Features:")
    for feat in late_group.get('top_features_with_descriptions', [])[:3]:
        desc = feat.get('description', 'No description')
        chain.append(f"    • {desc}")
    chain.append("")
    chain.append(f"  ↓ Sending {late_group['outgoing_edges']:,} connections forward")
    chain.append("")

    # Stage 5: Output
    output_group = layer_groups['output']
    chain.append("STAGE 5: OUTPUT GENERATION (Layers 21-25)")
    chain.append(f"  → {output_group['num_nodes']} features activated")
    chain.append(f"  → Strongest activation: {output_group['max_activation']:.1f}")
    chain.append("")
    chain.append("  Top Features:")
    for feat in output_group.get('top_features_with_descriptions', [])[:3]:
        desc = feat.get('description', 'No description')
        chain.append(f"    • {desc}")
    chain.append("")
    chain.append(f"  ✓ FINAL PREDICTION: \"{output}\"")
    chain.append("")

    # Summary
    chain.append("=" * 80)
    chain.append("SUMMARY")
    chain.append("=" * 80)
    total_features = sum(lg['num_nodes'] for lg in layer_groups.values())
    total_connections = sum(lg['outgoing_edges'] for lg in list(layer_groups.values())[:-1])

    chain.append(f"  Total Features Active: {total_features:,}")
    chain.append(f"  Total Connections: {total_connections:,}")
    chain.append(f"  Peak Activation Stage: Middle Processing (L11-15)")
    chain.append(f"  Final Output: \"{output}\" ({confidence:.1%} confidence)")
    chain.append("")
    chain.append("=" * 80)

    # Write to file
    output_text = "\n".join(chain)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)

    # Print with safe encoding
    try:
        print(output_text)
    except UnicodeEncodeError:
        print(output_text.encode('ascii', 'replace').decode('ascii'))

    print(f"\n[OK] Reasoning chain saved to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create reasoning chain summary')
    parser.add_argument('--analysis', type=str, required=True, help='Path to analysis JSON')
    parser.add_argument('--output', type=str, required=True, help='Output text file path')

    args = parser.parse_args()

    create_reasoning_chain(Path(args.analysis), Path(args.output))
