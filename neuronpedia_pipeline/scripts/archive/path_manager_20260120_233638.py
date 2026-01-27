"""
Path Manager - Centralized file organization for Neuronpedia Pipeline

This module provides a single source of truth for all file paths and folder structure.
All scripts should import and use PathManager instead of hardcoding paths.

Standard Structure:
    data/prompts/{prompt-slug}/
        1_generation/raw_graph.json, metadata.json
        2_conversion/converted_graph.json, conversion_stats.json
        3_analysis/circuit_analysis.json, supernodes.json, layer_groups.json
        4_visualizations/*.png
        7_minimal_pathways/minimal_circuit.json, pathway_comparison.png
        8_evolution/evolution_data.json, evolution_heatmap.png
        9_steering/steering_targets.json, targets_viz.png
        10_polysemanticity/purity_scores.json, purity_viz.png

    data/cross_analysis/{analysis-name}/
        metadata.json
        feature_overlap.json
        supernode_matches.json
        consensus_supernodes.json
        *.png
"""

from pathlib import Path
import re
import json
from datetime import datetime


class PathManager:
    """Centralized path management for the pipeline"""

    def __init__(self, base_dir=None):
        """
        Args:
            base_dir: Base directory for data (defaults to neuronpedia_pipeline/data)
        """
        if base_dir is None:
            # Auto-detect: assume we're in scripts/ folder
            script_dir = Path(__file__).parent
            self.base_dir = script_dir.parent / 'data'
        else:
            self.base_dir = Path(base_dir)

        self.prompts_dir = self.base_dir / 'prompts'
        self.cross_analysis_dir = self.base_dir / 'cross_analysis'

        # Ensure base directories exist
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.cross_analysis_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def slugify(text: str) -> str:
        """
        Convert prompt text to a clean slug

        Examples:
            "The capitol of Texas is" -> "the-capitol-of-texas-is"
            "Dallas is located in the state of" -> "dallas-is-located-in-the-state-of"
            "<bos>The capitol..." -> "the-capitol..."
        """
        # Remove <bos> tag
        text = text.replace('<bos>', '').strip()

        # Convert to lowercase
        text = text.lower()

        # Replace spaces and special chars with hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_]+', '-', text)

        # Remove leading/trailing hyphens
        text = text.strip('-')

        # Limit length (max 50 chars)
        if len(text) > 50:
            text = text[:50].rstrip('-')

        return text

    def get_prompt_dir(self, prompt: str) -> Path:
        """Get main directory for a prompt"""
        slug = self.slugify(prompt)
        prompt_dir = self.prompts_dir / slug
        prompt_dir.mkdir(parents=True, exist_ok=True)
        return prompt_dir

    def get_step_dir(self, prompt: str, step: int, step_name: str) -> Path:
        """
        Get directory for a pipeline step

        Args:
            prompt: The prompt text
            step: Step number (1-10)
            step_name: Step name (e.g., 'generation', 'conversion')

        Returns:
            Path to step directory
        """
        prompt_dir = self.get_prompt_dir(prompt)
        step_dir = prompt_dir / f"{step}_{step_name}"
        step_dir.mkdir(parents=True, exist_ok=True)
        return step_dir

    # ========== Step 1: Generation ==========
    def generation_dir(self, prompt: str) -> Path:
        return self.get_step_dir(prompt, 1, 'generation')

    def raw_graph_path(self, prompt: str) -> Path:
        return self.generation_dir(prompt) / 'raw_graph.json'

    def metadata_path(self, prompt: str) -> Path:
        return self.generation_dir(prompt) / 'metadata.json'

    # ========== Step 2: Conversion ==========
    def conversion_dir(self, prompt: str) -> Path:
        return self.get_step_dir(prompt, 2, 'conversion')

    def converted_graph_path(self, prompt: str) -> Path:
        return self.conversion_dir(prompt) / 'converted_graph.json'

    def conversion_stats_path(self, prompt: str) -> Path:
        return self.conversion_dir(prompt) / 'conversion_stats.json'

    # ========== Step 3: Analysis ==========
    def analysis_dir(self, prompt: str) -> Path:
        return self.get_step_dir(prompt, 3, 'analysis')

    def circuit_analysis_path(self, prompt: str) -> Path:
        return self.analysis_dir(prompt) / 'circuit_analysis.json'

    def supernodes_path(self, prompt: str) -> Path:
        return self.analysis_dir(prompt) / 'supernodes.json'

    def layer_groups_path(self, prompt: str) -> Path:
        return self.analysis_dir(prompt) / 'layer_groups.json'

    # ========== Step 4: Visualizations ==========
    def visualizations_dir(self, prompt: str) -> Path:
        return self.get_step_dir(prompt, 4, 'visualizations')

    def visualization_path(self, prompt: str, viz_name: str) -> Path:
        """
        Get path for a specific visualization

        Args:
            prompt: The prompt text
            viz_name: Name like 'supernode_overview', 'layer_distribution', etc.
        """
        return self.visualizations_dir(prompt) / f"{viz_name}.png"

    # ========== Step 7: Minimal Pathways ==========
    def minimal_pathways_dir(self, prompt: str) -> Path:
        return self.get_step_dir(prompt, 7, 'minimal_pathways')

    def minimal_circuit_path(self, prompt: str) -> Path:
        return self.minimal_pathways_dir(prompt) / 'minimal_circuit.json'

    def pathway_comparison_path(self, prompt: str) -> Path:
        return self.minimal_pathways_dir(prompt) / 'pathway_comparison.png'

    # ========== Step 8: Evolution ==========
    def evolution_dir(self, prompt: str) -> Path:
        return self.get_step_dir(prompt, 8, 'evolution')

    def evolution_data_path(self, prompt: str) -> Path:
        return self.evolution_dir(prompt) / 'evolution_data.json'

    def evolution_report_path(self, prompt: str) -> Path:
        return self.evolution_dir(prompt) / 'evolution_report.txt'

    def evolution_viz_path(self, prompt: str) -> Path:
        return self.evolution_dir(prompt) / 'evolution_heatmap.png'

    # ========== Step 9: Steering ==========
    def steering_dir(self, prompt: str) -> Path:
        return self.get_step_dir(prompt, 9, 'steering')

    def steering_targets_path(self, prompt: str) -> Path:
        return self.steering_dir(prompt) / 'steering_targets.json'

    def steering_viz_path(self, prompt: str) -> Path:
        return self.steering_dir(prompt) / 'targets_viz.png'

    # ========== Step 10: Polysemanticity ==========
    def polysemanticity_dir(self, prompt: str) -> Path:
        return self.get_step_dir(prompt, 10, 'polysemanticity')

    def polysemanticity_data_path(self, prompt: str) -> Path:
        return self.polysemanticity_dir(prompt) / 'purity_scores.json'

    def polysemanticity_report_path(self, prompt: str) -> Path:
        return self.polysemanticity_dir(prompt) / 'purity_report.txt'

    def polysemanticity_viz_path(self, prompt: str) -> Path:
        return self.polysemanticity_dir(prompt) / 'purity_viz.png'

    # ========== Cross-Analysis ==========
    def get_cross_analysis_dir(self, analysis_name: str) -> Path:
        """
        Get directory for cross-analysis

        Args:
            analysis_name: e.g., 'geography-domain-5prompts', 'politics-vs-geography'
        """
        cross_dir = self.cross_analysis_dir / analysis_name
        cross_dir.mkdir(parents=True, exist_ok=True)
        return cross_dir

    def cross_analysis_metadata_path(self, analysis_name: str) -> Path:
        return self.get_cross_analysis_dir(analysis_name) / 'metadata.json'

    def cross_analysis_overlap_path(self, analysis_name: str) -> Path:
        return self.get_cross_analysis_dir(analysis_name) / 'feature_overlap.json'

    def cross_analysis_matches_path(self, analysis_name: str) -> Path:
        return self.get_cross_analysis_dir(analysis_name) / 'supernode_matches.json'

    def cross_analysis_consensus_path(self, analysis_name: str) -> Path:
        return self.get_cross_analysis_dir(analysis_name) / 'consensus_supernodes.json'

    def cross_analysis_report_path(self, analysis_name: str) -> Path:
        return self.get_cross_analysis_dir(analysis_name) / 'analysis_report.txt'

    def cross_analysis_heatmap_path(self, analysis_name: str) -> Path:
        return self.get_cross_analysis_dir(analysis_name) / 'overlap_heatmap.png'

    def cross_analysis_network_path(self, analysis_name: str) -> Path:
        return self.get_cross_analysis_dir(analysis_name) / 'reuse_network.png'

    # ========== Utility Methods ==========
    def save_metadata(self, prompt: str, metadata: dict):
        """Save metadata for a prompt"""
        metadata['generated_at'] = datetime.now().isoformat()
        metadata['prompt'] = prompt
        metadata['slug'] = self.slugify(prompt)

        with open(self.metadata_path(prompt), 'w') as f:
            json.dump(metadata, f, indent=2)

    def load_metadata(self, prompt: str) -> dict:
        """Load metadata for a prompt"""
        path = self.metadata_path(prompt)
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}

    def get_all_analyzed_prompts(self) -> list:
        """Get list of all prompts that have been analyzed"""
        analyzed = []
        for prompt_dir in self.prompts_dir.iterdir():
            if prompt_dir.is_dir():
                analysis_file = prompt_dir / '3_analysis' / 'circuit_analysis.json'
                if analysis_file.exists():
                    metadata = self.load_metadata_from_dir(prompt_dir)
                    if metadata:
                        analyzed.append(metadata['prompt'])
        return analyzed

    def load_metadata_from_dir(self, prompt_dir: Path) -> dict:
        """Load metadata from a specific directory"""
        metadata_file = prompt_dir / '1_generation' / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)
        return {}

    def find_analysis_for_prompts(self, prompts: list) -> list:
        """
        Find circuit_analysis.json files for given prompts

        Args:
            prompts: List of prompt strings

        Returns:
            List of Path objects to circuit_analysis.json files
        """
        paths = []
        for prompt in prompts:
            analysis_path = self.circuit_analysis_path(prompt)
            if analysis_path.exists():
                paths.append(analysis_path)
        return paths


# Global instance for easy importing
path_manager = PathManager()


if __name__ == "__main__":
    # Test the path manager
    pm = PathManager()

    test_prompts = [
        "The capitol of Texas is",
        "Dallas is located in the state of",
        "<bos>Houston is a city in"
    ]

    print("=== Testing Path Manager ===\n")

    for prompt in test_prompts:
        print(f"Prompt: {prompt}")
        print(f"  Slug: {pm.slugify(prompt)}")
        print(f"  Prompt dir: {pm.get_prompt_dir(prompt)}")
        print(f"  Raw graph: {pm.raw_graph_path(prompt)}")
        print(f"  Analysis: {pm.circuit_analysis_path(prompt)}")
        print()

    print("=== Cross-Analysis Paths ===")
    analysis_name = "geography-domain-5prompts"
    print(f"Analysis: {analysis_name}")
    print(f"  Dir: {pm.get_cross_analysis_dir(analysis_name)}")
    print(f"  Report: {pm.cross_analysis_report_path(analysis_name)}")
    print(f"  Consensus: {pm.cross_analysis_consensus_path(analysis_name)}")
