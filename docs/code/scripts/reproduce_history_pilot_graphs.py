"""Rebuild and verify the saved-data history follow-up, with no model requests."""
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from importlib import metadata

import run_history_pilot_graphs as design
from run_matched_choice_controls import now
from control_io import atomic_json


def main():
    status = json.loads((design.OUT / 'status.json').read_text())
    if status['state'] not in ('collection_complete', 'collection_incomplete', 'complete', 'complete_with_exclusions'):
        raise RuntimeError('Collection must reach a terminal state before final reproduction')
    folder = design.OUT / 'reproduction'
    folder.mkdir(exist_ok=True)
    env = dict(started_at=now(), python=sys.version, executable=sys.executable, platform=platform.platform(),
               libraries={name: metadata.version(name) for name in ['numpy', 'scipy', 'matplotlib', 'networkx', 'requests', 'PyYAML', 'pytest']})
    atomic_json(folder / 'environment.json', env)
    pinned = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], check=True, capture_output=True, text=True)
    (folder / 'installed_packages.txt').write_text(pinned.stdout, encoding='utf-8')
    commands = [
        ('tests', [sys.executable, '-m', 'pytest', 'tests/test_history_pilot_graphs.py', 'tests/test_history_closeout.py',
                   'tests/test_matched_choice_controls.py', 'tests/test_failure_case_graphs.py', 'tests/test_whole_graph_analysis.py', '-q']),
        ('analysis', [sys.executable, 'scripts/analyze_history_pilot_graphs.py']),
        ('figures', [sys.executable, 'scripts/plot_history_pilot_graphs.py']),
    ]
    records = []
    for stage, command in commands:
        process = subprocess.run(command, cwd=design.ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        (folder / f'{stage}.stdout.log').write_text(process.stdout, encoding='utf-8')
        (folder / f'{stage}.stderr.log').write_text(process.stderr, encoding='utf-8')
        records.append(dict(stage=stage, command=command, exit_code=process.returncode, completed_at=now()))
        atomic_json(folder / 'commands.json', records)
        print(f'{stage}: exit {process.returncode}', flush=True)
        if process.returncode:
            raise RuntimeError(f'{stage} failed; see saved logs')
    pandoc = shutil.which('pandoc')
    if pandoc:
        shutil.copy2(design.ROOT / 'docs/papers/publication-paper.css', design.OUT / 'report.css')
        command = [pandoc, str(design.OUT / 'analysis/RESULTS.md'), '--standalone', '--css', '../report.css',
                   '--metadata', 'title=History graph results including incorrect answers',
                   '-o', str(design.OUT / 'analysis/RESULTS.html')]
        subprocess.run(command, check=True, cwd=design.ROOT)
    env['finished_at'] = now()
    atomic_json(folder / 'environment.json', env)
    from validate_history_pilot_graphs import main as validate
    validate(finalize=True)


if __name__ == '__main__':
    main()
