"""
Archive Manager - Script Backup Utility

This module provides utilities for creating timestamped backups of scripts
before making edits. All backups are stored in scripts/archive/ with timestamps.

Usage:
    from archive_manager import ArchiveManager

    am = ArchiveManager()
    am.archive_script('1_generate_graph.py')  # Creates backup before editing

    # Or archive multiple scripts
    am.archive_scripts(['1_generate_graph.py', '2_convert_graph.py'])
"""

import shutil
from pathlib import Path
from datetime import datetime
import json


class ArchiveManager:
    """Manages script backups and versioning"""

    def __init__(self, scripts_dir=None):
        """
        Args:
            scripts_dir: Directory containing scripts (defaults to current directory)
        """
        if scripts_dir is None:
            self.scripts_dir = Path(__file__).parent
        else:
            self.scripts_dir = Path(scripts_dir)

        self.archive_dir = self.scripts_dir / 'archive'
        self.archive_dir.mkdir(exist_ok=True)

        # Archive index file
        self.index_file = self.archive_dir / 'archive_index.json'
        self.index = self._load_index()

    def _load_index(self) -> dict:
        """Load archive index or create new one"""
        if self.index_file.exists():
            with open(self.index_file) as f:
                return json.load(f)
        return {}

    def _save_index(self):
        """Save archive index"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def archive_script(self, script_name: str, reason: str = ""):
        """
        Archive a single script before editing

        Args:
            script_name: Name of script to archive (e.g., '1_generate_graph.py')
            reason: Optional reason for archiving (e.g., 'Adding PathManager integration')

        Returns:
            Path to archived file
        """
        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            print(f"[ERROR] Script not found: {script_name}")
            return None

        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create archive filename
        base_name = script_path.stem  # e.g., '1_generate_graph'
        archive_name = f"{base_name}_{timestamp}.py"
        archive_path = self.archive_dir / archive_name

        # Copy file
        shutil.copy2(script_path, archive_path)

        # Update index
        if script_name not in self.index:
            self.index[script_name] = []

        self.index[script_name].append({
            'timestamp': timestamp,
            'archive_file': archive_name,
            'reason': reason,
            'original_size': script_path.stat().st_size
        })

        self._save_index()

        print(f"[OK] Archived {script_name} -> {archive_name}")
        if reason:
            print(f"     Reason: {reason}")

        return archive_path

    def archive_scripts(self, script_names: list, reason: str = ""):
        """
        Archive multiple scripts at once

        Args:
            script_names: List of script names to archive
            reason: Optional reason for archiving

        Returns:
            List of archive paths
        """
        archived = []
        for script_name in script_names:
            archive_path = self.archive_script(script_name, reason)
            if archive_path:
                archived.append(archive_path)

        print(f"\n[OK] Archived {len(archived)}/{len(script_names)} scripts")
        return archived

    def get_archive_history(self, script_name: str) -> list:
        """
        Get archive history for a script

        Args:
            script_name: Name of script

        Returns:
            List of archive entries (newest first)
        """
        if script_name not in self.index:
            return []

        return sorted(
            self.index[script_name],
            key=lambda x: x['timestamp'],
            reverse=True
        )

    def restore_script(self, script_name: str, timestamp: str = None):
        """
        Restore a script from archive

        Args:
            script_name: Name of script to restore
            timestamp: Specific timestamp to restore (defaults to most recent)

        Returns:
            True if restored successfully
        """
        history = self.get_archive_history(script_name)

        if not history:
            print(f"[ERROR] No archive history for {script_name}")
            return False

        # Find archive entry
        if timestamp is None:
            # Use most recent
            entry = history[0]
        else:
            entry = next((e for e in history if e['timestamp'] == timestamp), None)
            if entry is None:
                print(f"[ERROR] No archive found for timestamp {timestamp}")
                return False

        # Restore file
        archive_path = self.archive_dir / entry['archive_file']
        script_path = self.scripts_dir / script_name

        # Backup current version first
        self.archive_script(script_name, reason=f"Before restoring {entry['timestamp']}")

        # Restore
        shutil.copy2(archive_path, script_path)

        print(f"[OK] Restored {script_name} from {entry['timestamp']}")
        if entry['reason']:
            print(f"     Original reason: {entry['reason']}")

        return True

    def list_all_archives(self):
        """Print summary of all archived scripts"""
        if not self.index:
            print("[INFO] No scripts have been archived yet")
            return

        print("=" * 70)
        print("ARCHIVE SUMMARY")
        print("=" * 70)

        for script_name in sorted(self.index.keys()):
            history = self.get_archive_history(script_name)
            print(f"\n{script_name}: {len(history)} versions")

            # Show last 3 versions
            for entry in history[:3]:
                print(f"  {entry['timestamp']} - {entry['archive_file']}")
                if entry['reason']:
                    print(f"    Reason: {entry['reason']}")

        print(f"\nTotal scripts archived: {len(self.index)}")
        print(f"Total versions: {sum(len(h) for h in self.index.values())}")

    def clean_old_archives(self, keep_last_n: int = 5):
        """
        Remove old archive versions, keeping only the most recent N

        Args:
            keep_last_n: Number of recent versions to keep per script

        Returns:
            Number of files deleted
        """
        deleted_count = 0

        for script_name in self.index.keys():
            history = self.get_archive_history(script_name)

            # Keep only last N
            to_delete = history[keep_last_n:]

            for entry in to_delete:
                archive_path = self.archive_dir / entry['archive_file']
                if archive_path.exists():
                    archive_path.unlink()
                    deleted_count += 1

            # Update index
            self.index[script_name] = history[:keep_last_n]

        self._save_index()

        print(f"[OK] Cleaned {deleted_count} old archive files (keeping last {keep_last_n} per script)")
        return deleted_count


def archive_before_edit(script_names: list, reason: str = ""):
    """
    Convenience function to archive scripts before editing

    Args:
        script_names: List of script names or single script name
        reason: Reason for archiving
    """
    if isinstance(script_names, str):
        script_names = [script_names]

    am = ArchiveManager()
    am.archive_scripts(script_names, reason)


if __name__ == "__main__":
    # Test the archive manager
    import sys

    am = ArchiveManager()

    if len(sys.argv) > 1:
        # Command-line usage
        command = sys.argv[1]

        if command == "list":
            am.list_all_archives()

        elif command == "archive" and len(sys.argv) > 2:
            script_name = sys.argv[2]
            reason = sys.argv[3] if len(sys.argv) > 3 else ""
            am.archive_script(script_name, reason)

        elif command == "history" and len(sys.argv) > 2:
            script_name = sys.argv[2]
            history = am.get_archive_history(script_name)
            print(f"\nArchive history for {script_name}:")
            for entry in history:
                print(f"  {entry['timestamp']}: {entry['archive_file']}")
                if entry['reason']:
                    print(f"    Reason: {entry['reason']}")

        elif command == "restore" and len(sys.argv) > 2:
            script_name = sys.argv[2]
            timestamp = sys.argv[3] if len(sys.argv) > 3 else None
            am.restore_script(script_name, timestamp)

        elif command == "clean":
            keep_n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            am.clean_old_archives(keep_n)

        else:
            print("Usage:")
            print("  python archive_manager.py list")
            print("  python archive_manager.py archive <script_name> [reason]")
            print("  python archive_manager.py history <script_name>")
            print("  python archive_manager.py restore <script_name> [timestamp]")
            print("  python archive_manager.py clean [keep_n]")

    else:
        # Demo mode
        print("Archive Manager - Demo Mode")
        print("=" * 70)
        print("\nTo use from command line:")
        print("  python archive_manager.py list")
        print("  python archive_manager.py archive 1_generate_graph.py 'Adding PathManager'")
        print("\nTo use in Python:")
        print("  from archive_manager import ArchiveManager")
        print("  am = ArchiveManager()")
        print("  am.archive_script('1_generate_graph.py', 'Adding PathManager integration')")
        print("\nOr use the convenience function:")
        print("  from archive_manager import archive_before_edit")
        print("  archive_before_edit(['1_generate_graph.py', '2_convert_graph.py'], 'PathManager integration')")
