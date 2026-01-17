#!/usr/bin/env python3
"""
Example: Run Full Pipeline
Complete example of running the pipeline on a custom prompt
"""

import subprocess
import sys

def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"{description}")
    print('='*60)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"ERROR: {description} failed!")
        sys.exit(1)

if __name__ == "__main__":
    print("Running Complete Neuronpedia Pipeline")
    print("="*60)

    # Note: Edit scripts/1_generate_graph.py to change the prompt

    run_command(
        "python scripts/1_generate_graph.py",
        "Step 1: Generate attribution graph from Neuronpedia"
    )

    run_command(
        "python scripts/2_convert_graph.py",
        "Step 2: Convert graph to pipeline format"
    )

    run_command(
        "python scripts/3_analyze_circuit.py",
        "Step 3: Analyze circuit and detect supernodes"
    )

    run_command(
        "python scripts/4_visualize.py",
        "Step 4: Generate visualizations"
    )

    print("\n" + "="*60)
    print("PIPELINE COMPLETE!")
    print("="*60)
    print("\nCheck these directories:")
    print("  - data/graphs/ for graph JSON files")
    print("  - data/visualizations/ for PNG images")
