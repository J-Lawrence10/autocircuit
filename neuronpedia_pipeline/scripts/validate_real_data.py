"""
Validate Real Data Usage
Ensures no mock data is being used in the pipeline
"""

from pathlib import Path
import json
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def validate_data_is_real(graph_path):
    """
    Check if a graph file is real Neuronpedia data (not mock)

    Real data characteristics:
    - Large size (>1MB typically)
    - Has 'metadata' with 'slug' from Neuronpedia
    - Has Circuit Tracer generator info
    - node_id format matches Neuronpedia structure
    """

    graph_path = Path(graph_path)

    # Check 1: Filename must have 'real_' prefix
    if not graph_path.name.startswith('real_'):
        return False, "Filename does not start with 'real_'"

    # Check 2: File must be reasonably large
    size_mb = graph_path.stat().st_size / (1024 * 1024)
    if size_mb < 0.5:
        return False, f"File too small ({size_mb:.2f}MB) - likely mock data"

    # Check 3: Check internal structure
    with open(graph_path) as f:
        data = json.load(f)

    # Check for Neuronpedia metadata
    if 'metadata' in data:
        metadata = data['metadata']

        # Real data has slug from Neuronpedia
        if 'slug' in metadata and 'original_nodes' in metadata:
            # This is converted real data
            if metadata['original_nodes'] < 100:
                return False, "Too few nodes for real data"
            return True, f"Converted real data: {metadata['original_nodes']} nodes"

        # Check for Circuit Tracer generator
        if 'generator' in metadata.get('info', {}):
            gen = metadata['info']['generator']
            if 'circuit-tracer' in gen.get('name', ''):
                return True, f"Raw Circuit Tracer data"

    return False, "Missing Neuronpedia metadata"

def check_pipeline_files():
    """Check all graph files in pipeline"""

    print("="*60)
    print("VALIDATING PIPELINE DATA SOURCES")
    print("="*60)

    data_dir = Path("../data/graphs")
    if not data_dir.exists():
        data_dir = Path("data/graphs")

    files_to_check = list(data_dir.glob("*.json"))

    real_data_count = 0
    mock_data_count = 0

    for file_path in files_to_check:
        print(f"\nChecking: {file_path.name}")
        is_real, reason = validate_data_is_real(file_path)

        if is_real:
            print(f"  ✓ REAL DATA - {reason}")
            real_data_count += 1
        else:
            print(f"  ✗ NOT REAL - {reason}")
            mock_data_count += 1

            # Warn if mock data found
            if file_path.stat().st_size < 10000:  # <10KB is definitely mock
                print(f"  ⚠️  WARNING: This appears to be mock data!")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Real data files: {real_data_count}")
    print(f"Mock/invalid files: {mock_data_count}")

    if mock_data_count > 0:
        print("\n⚠️  WARNING: Mock data detected in pipeline!")
        print("Consider removing mock files or ensuring scripts use 'real_' prefix")
    else:
        print("\n✓ All data files are real Neuronpedia data!")

    return real_data_count, mock_data_count

if __name__ == "__main__":
    check_pipeline_files()
