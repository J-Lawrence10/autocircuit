"""Durable JSON promotion with bounded retries for transient Windows sharing errors.

Kept outside the frozen design modules: transport repair must not alter their hashes.
"""
import json
import os
from pathlib import Path
import tempfile
import time


def replace_with_retry(source, destination, attempts=24, delay=.25):
    for attempt in range(attempts):
        try:
            os.replace(source, destination)
            return
        except PermissionError:
            if attempt + 1 == attempts:
                raise
            time.sleep(delay)


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=True, allow_nan=False)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        replace_with_retry(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
