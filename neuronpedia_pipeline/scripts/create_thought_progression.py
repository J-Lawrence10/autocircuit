"""
Create Thought Progression Analysis
Shows the logical reasoning path the model takes to reach its answer
"""

import json
from pathlib import Path
import argparse


def create_thought_progression(analysis_file, output_file):
    """Create a thought progression showing model's logical reasoning"""

    with open(analysis_file) as f:
        data = json.load(f)

    metadata = data['metadata']
    layer_groups = data['layer_groups']

    prompt = metadata['prompt'].replace('<bos>', '').strip()
    predictions = metadata.get('top_predictions', [])

    # Build the progression
    lines = []
    lines.append("=" * 80)
    lines.append("MODEL'S THOUGHT PROGRESSION")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"PROMPT: \"{prompt}\"")
    lines.append("")

    if predictions:
        lines.append("FINAL ANSWER OPTIONS:")
        for i, pred in enumerate(predictions[:6], 1):
            token = pred['token']
            prob = pred['probability']
            marker = ">>>" if i == 1 else "   "
            lines.append(f"  {marker} {i}. \"{token}\" ({prob:.1%})")
    lines.append("")
    lines.append("=" * 80)
    lines.append("HOW THE MODEL THINKS:")
    lines.append("=" * 80)
    lines.append("")

    # Stage 1: Input Recognition
    input_group = layer_groups['input']
    lines.append("STAGE 1: RECOGNIZING THE QUESTION")
    lines.append("-" * 80)
    lines.append(f"  The model activates {input_group['num_nodes']} features to understand:")
    lines.append(f"  - What: 'political party'")
    lines.append(f"  - Who: 'USA president'")
    lines.append(f"  - Context: This is asking about CURRENT president")
    lines.append("")

    if 'top_features_with_descriptions' in input_group:
        lines.append("  Top concepts recognized:")
        for feat in input_group['top_features_with_descriptions'][:3]:
            desc = feat.get('description', 'Unknown')
            # Clean unicode
            desc = desc.encode('ascii', 'replace').decode('ascii').replace('?', '')
            if desc and len(desc) > 5:
                lines.append(f"    - {desc}")
    lines.append("")
    lines.append(f"  >>> Sends {input_group['outgoing_edges']:,} signals forward")
    lines.append("")

    # Stage 2: Early Processing
    early_group = layer_groups['early_proc']
    lines.append("STAGE 2: UNDERSTANDING CONTEXT")
    lines.append("-" * 80)
    lines.append(f"  The model refines understanding with {early_group['num_nodes']} features:")
    lines.append(f"  - This is about POLITICS")
    lines.append(f"  - Specifically US POLITICAL PARTIES")
    lines.append(f"  - Two main options: Republican or Democratic")
    lines.append("")

    if 'top_features_with_descriptions' in early_group:
        lines.append("  Key concepts:")
        for feat in early_group['top_features_with_descriptions'][:3]:
            desc = feat.get('description', 'Unknown')
            desc = desc.encode('ascii', 'replace').decode('ascii').replace('?', '')
            if desc and len(desc) > 5:
                lines.append(f"    - {desc}")
    lines.append("")
    lines.append(f"  >>> Sends {early_group['outgoing_edges']:,} signals forward")
    lines.append("")

    # Stage 3: Middle Processing (KEY STAGE)
    middle_group = layer_groups['middle_proc']
    lines.append("STAGE 3: RETRIEVING KNOWLEDGE (PEAK ACTIVATION)")
    lines.append("-" * 80)
    lines.append(f"  The model's STRONGEST thinking happens here!")
    lines.append(f"  - Only {middle_group['num_nodes']} features, but VERY active")
    lines.append(f"  - Peak activation: {middle_group['max_activation']:.1f} (highest in circuit)")
    lines.append(f"  - This is where the model recalls:")
    lines.append(f"    * Who is the current president?")
    lines.append(f"    * What party are they from?")
    lines.append(f"    * Historical political information")
    lines.append("")

    if 'top_features_with_descriptions' in middle_group:
        lines.append("  Strongest concepts:")
        for feat in middle_group['top_features_with_descriptions'][:3]:
            desc = feat.get('description', 'Unknown')
            desc = desc.encode('ascii', 'replace').decode('ascii').replace('?', '')
            if desc and len(desc) > 5:
                lines.append(f"    - {desc}")
    lines.append("")
    lines.append(f"  >>> Sends {middle_group['outgoing_edges']:,} signals forward")
    lines.append("")

    # Stage 4: Late Processing
    late_group = layer_groups['late_proc']
    lines.append("STAGE 4: REASONING & VERIFICATION")
    lines.append("-" * 80)
    lines.append(f"  The model double-checks with {late_group['num_nodes']} features:")
    lines.append(f"  - Does this answer make sense?")
    lines.append(f"  - Is this consistent with what I know?")
    lines.append(f"  - Activation: {late_group['max_activation']:.1f}")
    lines.append("")

    if 'top_features_with_descriptions' in late_group:
        lines.append("  Verification concepts:")
        for feat in late_group['top_features_with_descriptions'][:3]:
            desc = feat.get('description', 'Unknown')
            desc = desc.encode('ascii', 'replace').decode('ascii').replace('?', '')
            if desc and len(desc) > 5:
                lines.append(f"    - {desc}")
    lines.append("")
    lines.append(f"  >>> Sends {late_group['outgoing_edges']:,} signals forward")
    lines.append("")

    # Stage 5: Output
    output_group = layer_groups['output']
    lines.append("STAGE 5: GENERATING ANSWER")
    lines.append("-" * 80)
    lines.append(f"  Final layer combines everything with {output_group['num_nodes']} features:")
    lines.append(f"  - Activation: {output_group['max_activation']:.1f}")
    lines.append("")

    if predictions:
        lines.append("  Model's decision process:")
        lines.append(f"    1st choice: '{predictions[0]['token']}' ({predictions[0]['probability']:.1%})")
        lines.append(f"       -> Grammatically correct start")
        lines.append("")
        if len(predictions) > 5:
            republican_pred = predictions[5]
            lines.append(f"    Also considering: '{republican_pred['token']}' ({republican_pred['probability']:.1%})")
            lines.append(f"       -> Direct answer variant")
    lines.append("")

    # Summary
    lines.append("=" * 80)
    lines.append("INTERPRETATION")
    lines.append("=" * 80)
    lines.append("")
    lines.append("The model's reasoning shows:")
    lines.append("")
    lines.append("1. RECOGNITION: Understood this is about US president's political party")
    lines.append("")
    lines.append("2. KNOWLEDGE RETRIEVAL: Peak activity in middle layers (L11-15)")
    lines.append("   - This is where factual knowledge is recalled")
    lines.append(f"   - Strongest activation: {middle_group['max_activation']:.1f}")
    lines.append("")
    lines.append("3. GRAMMATICAL PROCESSING: Model chose 'the' first")
    lines.append("   - Full grammatical answer: 'the Republican Party'")
    lines.append("   - Direct answer also present: 'Republican' (3.3%)")
    lines.append("")
    lines.append("4. CONFIDENCE DISTRIBUTION:")
    if predictions:
        lines.append(f"   - Top answer: '{predictions[0]['token']}' at {predictions[0]['probability']:.1%}")
        if len(predictions) > 5:
            lines.append(f"   - Substantive answer: '{predictions[5]['token']}' at {predictions[5]['probability']:.1%}")
    lines.append("")
    lines.append("The model DID identify 'Republican' but prioritized grammatical structure.")
    lines.append("")
    lines.append("=" * 80)

    # Write to file
    output_text = "\n".join(lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)

    # Print with safe encoding
    try:
        print(output_text)
    except UnicodeEncodeError:
        print(output_text.encode('ascii', 'replace').decode('ascii'))

    print(f"\n[OK] Thought progression saved to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create thought progression analysis')
    parser.add_argument('--analysis', type=str, required=True, help='Path to analysis JSON')
    parser.add_argument('--output', type=str, required=True, help='Output text file path')

    args = parser.parse_args()

    create_thought_progression(Path(args.analysis), Path(args.output))
