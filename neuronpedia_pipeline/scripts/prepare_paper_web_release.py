"""Prepare a scoped paper/site commit without switching or staging the user's checkout.

No push, API calls, model calls, raw-data copying, or changes to the real Git index.
The website and review folder use the same manifest-verified bytes.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import zipfile

PIPELINE = Path(__file__).resolve().parents[1]
REPO = PIPELINE.parent
PACKAGE = PIPELINE / 'paper_share'
PREFIX = 'neuronpedia_pipeline/paper_share/'


def git(*args, data=None, env=None):
    return subprocess.run(['git', *args], cwd=REPO, input=data, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=True).stdout


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='origin/main')
    parser.add_argument('--branch', default='codex/paper-reviewed-20261111')
    parser.add_argument('--message', default='Publish reviewed manuscript, abstract, and print-ready figures')
    parser.add_argument('--report', default='data/model_extension/paper_review_20261111/main_release_preparation.json')
    args = parser.parse_args()
    assert args.branch.startswith('codex/'), 'Use a dedicated release branch'
    git('check-ref-format', '--branch', args.branch)
    exists = subprocess.run(['git', 'show-ref', '--verify', '--quiet',
                             f'refs/heads/{args.branch}'], cwd=REPO).returncode == 0
    assert not exists, 'Release branch already exists; inspect it rather than overwriting'
    subprocess.run([sys.executable, str(PACKAGE/'code/verify_package.py')], check=True)
    base = git('rev-parse', args.base).decode().strip()
    head = git('rev-parse', 'HEAD').decode().strip()
    index = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
    index_before = index.read_bytes()
    manifest = json.loads((PACKAGE/'provenance/package_manifest.json').read_text(encoding='utf-8'))
    payload = {}
    for record in manifest['files']:
        rel = PurePosixPath(record['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        raw = (PACKAGE/rel).read_bytes()
        assert digest(raw) == record['sha256'], str(rel)
        payload[rel.as_posix()] = raw
    payload['provenance/package_manifest.json'] = (PACKAGE/'provenance/package_manifest.json').read_bytes()
    originals = git('show', f'{base}:README.md')
    # Update the existing paper notice without nesting another archived overview.
    archive_marker = b'<details>\n<summary>Archived project overview</summary>\n\n'
    if originals.startswith(b'# AutoCircuit: current attribution-graph paper\n'):
        assert originals.count(archive_marker) == 1, 'Ambiguous existing README wrapper'
        assert originals.rstrip().endswith(b'</details>'), 'Unexpected README footer'
        originals = originals.split(archive_marker, 1)[1].rstrip()
        originals = originals[:-len(b'</details>')].rstrip() + b'\n'
    notice = (
        '# AutoCircuit: current attribution-graph paper\n\n'
        '## Working paper, 11 November 2026\n\n'
        '[Read the paper online](https://j-lawrence10.github.io/autocircuit/manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.html) '
        '| [Website and figures](https://j-lawrence10.github.io/autocircuit/) '
        '| [Review package](neuronpedia_pipeline/paper_share/)\n\n'
        '**Feature sharing in attribution graphs tracks predicted responses.** '
        'The paper asks whether graph feature sharing reflects the fact being asked about or the answer the model produces. '
        'This reviewed edition includes the approved manuscript and abstract, six main figures, ten supplements, derived tables, analysis code snapshots, and audit records. '
        'It is a working manuscript, not a peer-reviewed publication. Raw Neuronpedia exports, credentials, model files, and third-party reference PDFs are not included.\n\n'
        '**Historical correction:** Earlier traceback, bottleneck, redundancy, and causal claims are withdrawn. '
        'The archived research overview below is not the current paper or its conclusions.\n\n'
        '<details>\n<summary>Archived project overview</summary>\n\n'
    ).encode('utf-8')
    changes = {'README.md': notice + originals + b'\n</details>\n', 'docs/.nojekyll': b''}
    for rel, raw in payload.items():
        changes[PREFIX+rel] = raw
        changes['docs/'+rel] = raw
    script_rel = 'neuronpedia_pipeline/scripts/prepare_paper_web_release.py'
    changes[script_rel] = Path(__file__).read_bytes()
    # Remove only files owned by the prior verified package and superseded now.
    prior = json.loads(git('show', f'{base}:{PREFIX}provenance/package_manifest.json'))
    retired = []
    for record in prior['files']:
        rel = PurePosixPath(record['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        if rel.as_posix() not in payload:
            for prefix in [PREFIX, 'docs/']:
                path = prefix + rel.as_posix()
                assert digest(git('show', f'{base}:{path}')) == record['sha256'], path
                retired.append(path)

    with tempfile.TemporaryDirectory(prefix='paper-release-index-') as temporary:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary)/'index'))
        git('read-tree', base, env=env)
        if retired:
            git('update-index', '--force-remove', '-z', '--stdin',
                data=('\0'.join(retired)+'\0').encode('utf-8'), env=env)
        entries = []
        for rel, raw in sorted(changes.items()):
            blob = git('hash-object', '-w', '--no-filters', '--stdin', data=raw).decode().strip()
            entries.append(f'100644 {blob}\t{rel}\0')
        git('update-index', '-z', '--index-info', data=''.join(entries).encode('utf-8'), env=env)
        tree = git('write-tree', env=env).decode().strip()
        changed = git('diff-tree', '--no-commit-id', '--name-only', '-r', base, tree).decode().splitlines()
        assert set(changed) <= set(changes) | set(retired), 'Unexpected files in release'
        # Read the actual staged blobs back, not just the source files.
        for rel, raw in changes.items():
            assert git('show', f'{tree}:{rel}') == raw, rel
        remaining = set(git('ls-tree', '-r', '--name-only', tree).decode().splitlines())
        assert not set(retired).intersection(remaining), 'Superseded files remain'
        # Test a fresh export of the exact Git tree, including package checksums.
        archive = git('archive', '--format=zip', tree, PREFIX.rstrip('/'))
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            for name in z.namelist():
                p = PurePosixPath(name)
                assert not p.is_absolute() and '..' not in p.parts
            z.extractall(Path(temporary)/'export')
        exported = Path(temporary)/'export'/PREFIX
        subprocess.run([sys.executable, str(exported/'code/verify_package.py')], check=True)
        commit = git('commit-tree', tree, '-p', base, '-m', args.message).decode().strip()
        git('update-ref', f'refs/heads/{args.branch}', commit, '0'*40)
    assert git('rev-parse', 'HEAD').decode().strip() == head
    assert index.read_bytes() == index_before, 'Original index changed'
    report = {'base': base, 'branch': args.branch, 'commit': commit,
              'package_files': len(payload), 'release_paths': len(changed),
              'retired_package_paths': retired,
              'website_matches_package': True, 'fresh_git_export_verified': True,
              'original_head_and_index_unchanged': True, 'pushed': False,
              'site_source': {'branch': 'main', 'path': '/docs'}}
    destination = (PIPELINE/args.report).resolve()
    assert destination.is_relative_to((PIPELINE/'data/model_extension').resolve()), 'Keep release reports in the local archive'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
