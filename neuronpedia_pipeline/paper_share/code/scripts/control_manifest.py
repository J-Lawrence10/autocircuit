"""Validation helpers for preregistered positive and negative controls."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

REQUIRED_COLUMNS = {'pair_id', 'domain', 'split', 'role', 'prompt', 'expected_token'}
REQUIRED_ROLES = {
    'target',
    'positive_paraphrase',
    'negative_same_template',
    'negative_nonce',
}


def load_control_manifest(path: Path) -> List[dict]:
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    validate_control_manifest(rows)
    return rows


def validate_control_manifest(rows: List[dict]) -> None:
    if not rows:
        raise ValueError('Control manifest is empty')
    missing_columns = REQUIRED_COLUMNS - set(rows[0])
    if missing_columns:
        raise ValueError(f'Missing manifest columns: {sorted(missing_columns)}')
    groups: Dict[str, List[dict]] = defaultdict(list)
    prompts = Counter()
    for index, row in enumerate(rows, 2):
        pair_id = row.get('pair_id', '').strip()
        role = row.get('role', '').strip()
        split = row.get('split', '').strip()
        prompt = row.get('prompt', '').strip()
        if not pair_id or not prompt:
            raise ValueError(f'Row {index}: pair_id and prompt are required')
        if role not in REQUIRED_ROLES:
            raise ValueError(f'Row {index}: unknown role {role!r}')
        if split not in {'development', 'held_out'}:
            raise ValueError(f'Row {index}: unknown split {split!r}')
        if role in {'target', 'positive_paraphrase'} and not row.get('expected_token', '').strip():
            raise ValueError(f'Row {index}: {role} requires expected_token')
        groups[pair_id].append(row)
        prompts[prompt] += 1
    duplicates = [prompt for prompt, count in prompts.items() if count > 1]
    if duplicates:
        raise ValueError(f'Prompts must be unique: {duplicates}')
    for pair_id, group in groups.items():
        role_counts = Counter(row['role'].strip() for row in group)
        missing_roles = REQUIRED_ROLES - set(role_counts)
        if missing_roles:
            raise ValueError(f'{pair_id}: missing controls {sorted(missing_roles)}')
        if role_counts['target'] != 1:
            raise ValueError(f'{pair_id}: exactly one target is required')
        expected = {
            row['expected_token'].strip()
            for row in group
            if row['role'].strip() in {'target', 'positive_paraphrase'}
        }
        if len(expected) != 1:
            raise ValueError(f'{pair_id}: target and positive control must share expected_token')


def summarize_manifest(rows: List[dict]) -> dict:
    return {
        'pairs': len({row['pair_id'] for row in rows}),
        'prompts': len(rows),
        'roles': dict(Counter(row['role'] for row in rows)),
        'domains': dict(Counter(row['domain'] for row in rows)),
        'splits': dict(Counter(row['split'] for row in rows)),
    }
