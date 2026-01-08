#!/usr/bin/env python3
"""Script to generate attribution graph from Neuronpedia API"""

import requests
import json
import sys

API_KEY = "sk-np-xM8SydJfvJjlyFg7hZPEPpqWB3Bcqpx8O0mIM4P5BmQ0"
BASE_URL = "https://neuronpedia.org/api"

def generate_graph(prompt, model_id="gemma-2-2b", output_file="graph_output.json"):
    """Generate attribution graph for a given prompt"""

    url = f"{BASE_URL}/graph/generate"
    headers = {
        "Content-Type": "application/json",
        "x-secret-key": API_KEY
    }

    payload = {
        "prompt": prompt,
        "model_id": model_id,
        "node_threshold": 0.1,
        "edge_threshold": 0.05,
        "max_feature_nodes": 100
    }

    print(f"Generating attribution graph for prompt: '{prompt}'")
    print(f"Using model: {model_id}")
    print(f"Calling API endpoint: {url}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)

        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            graph_data = response.json()

            # Save to file
            with open(output_file, 'w') as f:
                json.dump(graph_data, f, indent=2)

            print(f"✓ Graph generated successfully!")
            print(f"✓ Saved to: {output_file}")

            # Print summary
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            print(f"\nGraph Summary:")
            print(f"  - Nodes: {len(nodes)}")
            print(f"  - Edges: {len(edges)}")

            return graph_data
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return None
    except requests.exceptions.Timeout:
        print("Request timed out after 120 seconds")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    prompt = "The powerhouse of the cell is the"
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])

    generate_graph(prompt, output_file="powerhouse_graph.json")
