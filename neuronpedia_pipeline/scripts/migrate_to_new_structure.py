"""
Migration Script - Reorganize existing data to new structure

This script:
1. Finds all existing circuit data in data/graphs/
2. Reorganizes into data/prompts/{slug}/ structure
3. Moves cross-analysis data to data/cross_analysis/
4. Creates backup before migration
5. Validates migration succeeded

Usage:
    python scripts/migrate_to_new_structure.py [--dry-run] [--backup]
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))
from path_manager import PathManager


class DataMigrator:
    """Migrate existing data to new structure"""

    def __init__(self, dry_run=False, create_backup=True):
        self.pm = PathManager()
        self.dry_run = dry_run
        self.create_backup = create_backup

        # Old structure paths
        self.old_graphs_dir = self.pm.base_dir / 'graphs'
        self.old_cross_prompt_dir = self.pm.base_dir / 'cross_prompt_analysis'
        self.old_minimal_dir = self.pm.base_dir / 'minimal_pathways'
        self.old_evolution_dir = self.pm.base_dir / 'evolution_analysis'
        self.old_steering_dir = self.pm.base_dir / 'steering_analysis'
        self.old_polysemanticity_dir = self.pm.base_dir / 'polysemanticity_analysis'

        self.migrated_count = 0
        self.errors = []

    def create_backup_if_needed(self):
        """Create backup of data directory"""
        if not self.create_backup:
            return

        backup_dir = self.pm.base_dir.parent / f'data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

        print(f"[BACKUP] Creating backup at: {backup_dir}")
        if not self.dry_run:
            shutil.copytree(self.pm.base_dir, backup_dir)
            print(f"[OK] Backup created successfully")

    def extract_prompt_from_metadata(self, graph_file: Path) -> str:
        """Extract prompt from raw graph JSON"""
        try:
            with open(graph_file) as f:
                data = json.load(f)
                return data.get('prompt', '')
        except:
            return ''

    def extract_prompt_from_analysis(self, analysis_file: Path) -> str:
        """Extract prompt from analysis JSON"""
        try:
            with open(analysis_file) as f:
                data = json.load(f)
                return data.get('metadata', {}).get('prompt', '')
        except:
            return ''

    def migrate_prompt_data(self, old_prompt_dir: Path):
        """
        Migrate data for a single prompt from old structure to new

        Old structure:
            data/graphs/{slug}/
                real_*_analysis.json
                real_*_converted.json
                graph_*.json
                visualizations/*

        New structure:
            data/prompts/{slug}/
                1_generation/raw_graph.json, metadata.json
                2_conversion/converted_graph.json
                3_analysis/circuit_analysis.json
                4_visualizations/*.png
        """
        # Find files
        raw_graphs = list(old_prompt_dir.glob('graph_*.json'))
        converted_graphs = list(old_prompt_dir.glob('*_converted.json'))
        analyses = list(old_prompt_dir.glob('*_analysis.json'))
        viz_dir = old_prompt_dir / 'visualizations'

        if not analyses:
            print(f"[SKIP] No analysis found in {old_prompt_dir.name}")
            return

        # Extract prompt from analysis
        prompt = self.extract_prompt_from_analysis(analyses[0])
        if not prompt:
            print(f"[ERROR] Could not extract prompt from {analyses[0]}")
            self.errors.append(f"No prompt in {old_prompt_dir}")
            return

        print(f"\n[MIGRATE] Prompt: {prompt}")
        print(f"  From: {old_prompt_dir}")
        print(f"  To: {self.pm.get_prompt_dir(prompt)}")

        # Step 1: Generation
        if raw_graphs:
            src = raw_graphs[0]
            dst = self.pm.raw_graph_path(prompt)
            print(f"  [1_generation] {src.name} -> {dst.name}")
            if not self.dry_run:
                shutil.copy2(src, dst)

                # Create metadata
                with open(src) as f:
                    raw_data = json.load(f)
                metadata = {
                    'prompt': prompt,
                    'model': raw_data.get('modelId', 'gemma-2-2b'),
                    'slug': raw_data.get('slug', ''),
                    'num_nodes': raw_data.get('numNodes', 0),
                    'num_links': raw_data.get('numLinks', 0),
                    'migrated_from': str(src)
                }
                self.pm.save_metadata(prompt, metadata)

        # Step 2: Conversion
        if converted_graphs:
            src = converted_graphs[0]
            dst = self.pm.converted_graph_path(prompt)
            print(f"  [2_conversion] {src.name} -> {dst.name}")
            if not self.dry_run:
                shutil.copy2(src, dst)

        # Step 3: Analysis
        if analyses:
            src = analyses[0]
            dst = self.pm.circuit_analysis_path(prompt)
            print(f"  [3_analysis] {src.name} -> {dst.name}")
            if not self.dry_run:
                shutil.copy2(src, dst)

        # Step 4: Visualizations
        if viz_dir.exists():
            for viz_file in viz_dir.glob('*.png'):
                dst = self.pm.visualizations_dir(prompt) / viz_file.name
                print(f"  [4_visualizations] {viz_file.name}")
                if not self.dry_run:
                    shutil.copy2(viz_file, dst)

        self.migrated_count += 1

    def migrate_optional_analyses(self):
        """Migrate minimal pathways, evolution, steering, polysemanticity"""

        # Minimal Pathways
        if self.old_minimal_dir.exists():
            for prompt_dir in self.old_minimal_dir.iterdir():
                if prompt_dir.is_dir():
                    # Find corresponding prompt
                    json_files = list(prompt_dir.glob('minimal_pathway.json'))
                    if json_files:
                        # Try to match by slug
                        slug = prompt_dir.name
                        # Find prompt with matching slug
                        for analysis_dir in (self.pm.base_dir / 'graphs').glob('*/'):
                            if slug in analysis_dir.name:
                                analysis_file = list(analysis_dir.glob('*_analysis.json'))
                                if analysis_file:
                                    prompt = self.extract_prompt_from_analysis(analysis_file[0])
                                    if prompt:
                                        print(f"\n[MIGRATE] Minimal pathways for: {prompt}")
                                        for file in prompt_dir.glob('*'):
                                            if file.is_file():
                                                dst = self.pm.minimal_pathways_dir(prompt) / file.name
                                                print(f"  [7_minimal_pathways] {file.name}")
                                                if not self.dry_run:
                                                    shutil.copy2(file, dst)
                                        break

        # Evolution
        if self.old_evolution_dir.exists():
            self._migrate_optional_dir(self.old_evolution_dir, '8_evolution', self.pm.evolution_dir)

        # Steering
        if self.old_steering_dir.exists():
            self._migrate_optional_dir(self.old_steering_dir, '9_steering', self.pm.steering_dir)

        # Polysemanticity
        if self.old_polysemanticity_dir.exists():
            self._migrate_optional_dir(self.old_polysemanticity_dir, '10_polysemanticity', self.pm.polysemanticity_dir)

    def _migrate_optional_dir(self, old_dir: Path, step_name: str, dir_func):
        """Helper to migrate optional analysis directories"""
        for prompt_dir in old_dir.iterdir():
            if prompt_dir.is_dir():
                # Try to find matching prompt
                slug = prompt_dir.name
                for analysis_dir in (self.pm.base_dir / 'graphs').glob('*/'):
                    if slug in analysis_dir.name:
                        analysis_file = list(analysis_dir.glob('*_analysis.json'))
                        if analysis_file:
                            prompt = self.extract_prompt_from_analysis(analysis_file[0])
                            if prompt:
                                print(f"\n[MIGRATE] {step_name} for: {prompt}")
                                for file in prompt_dir.glob('*'):
                                    if file.is_file():
                                        dst = dir_func(prompt) / file.name
                                        print(f"  [{step_name}] {file.name}")
                                        if not self.dry_run:
                                            shutil.copy2(file, dst)
                                break

    def migrate_cross_analysis(self):
        """Migrate cross-analysis data"""
        if not self.old_cross_prompt_dir.exists():
            return

        for analysis_dir in self.old_cross_prompt_dir.iterdir():
            if analysis_dir.is_dir():
                analysis_name = analysis_dir.name
                print(f"\n[MIGRATE] Cross-analysis: {analysis_name}")

                new_dir = self.pm.get_cross_analysis_dir(analysis_name)

                # Map old filenames to new
                file_mapping = {
                    'cross_prompt_analysis.txt': 'analysis_report.txt',
                    'feature_overlap_heatmap.png': 'overlap_heatmap.png',
                    'supernode_reuse_network.png': 'reuse_network.png',
                    'consensus_supernodes.json': 'consensus_supernodes.json'
                }

                for old_name, new_name in file_mapping.items():
                    old_file = analysis_dir / old_name
                    if old_file.exists():
                        new_file = new_dir / new_name
                        print(f"  {old_name} -> {new_name}")
                        if not self.dry_run:
                            shutil.copy2(old_file, new_file)

    def run_migration(self):
        """Run full migration"""
        print("=" * 70)
        print("DATA MIGRATION TO NEW STRUCTURE")
        print("=" * 70)

        if self.dry_run:
            print("[DRY RUN] No files will be modified\n")

        # Backup
        self.create_backup_if_needed()

        # Migrate prompt data
        if self.old_graphs_dir.exists():
            print(f"\n[STEP 1] Migrating prompt data from {self.old_graphs_dir}")
            for prompt_dir in self.old_graphs_dir.iterdir():
                if prompt_dir.is_dir():
                    self.migrate_prompt_data(prompt_dir)

        # Migrate optional analyses
        print(f"\n[STEP 2] Migrating optional analyses")
        self.migrate_optional_analyses()

        # Migrate cross-analysis
        print(f"\n[STEP 3] Migrating cross-analysis data")
        self.migrate_cross_analysis()

        # Summary
        print("\n" + "=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        print(f"Prompts migrated: {self.migrated_count}")
        print(f"Errors: {len(self.errors)}")

        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  - {error}")

        if not self.dry_run:
            print(f"\n[SUCCESS] Migration complete!")
            print(f"New structure: {self.pm.prompts_dir}")
            print(f"Cross-analysis: {self.pm.cross_analysis_dir}")
        else:
            print(f"\n[DRY RUN] No changes made. Run without --dry-run to migrate.")


def main():
    parser = argparse.ArgumentParser(description='Migrate data to new file structure')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup (not recommended)')

    args = parser.parse_args()

    migrator = DataMigrator(
        dry_run=args.dry_run,
        create_backup=not args.no_backup
    )

    migrator.run_migration()


if __name__ == "__main__":
    main()
