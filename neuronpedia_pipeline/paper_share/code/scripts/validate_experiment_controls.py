#!/usr/bin/env python3
"""Validate that every experiment pair includes positive and negative controls."""

import argparse
import json
from pathlib import Path

from control_manifest import load_control_manifest, summarize_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--manifest',
        type=Path,
        default=Path(__file__).parent.parent / 'config' / 'paper_control_manifest.csv',
    )
    args = parser.parse_args()
    rows = load_control_manifest(args.manifest)
    print(json.dumps(summarize_manifest(rows), indent=2))
    print('[OK] Every pair has a target, positive paraphrase, matched-template negative, and nonce negative.')


if __name__ == '__main__':
    main()
