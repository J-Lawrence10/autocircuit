"""Assemble a portable, allowlisted review package. No model calls or raw export copies."""
from pathlib import Path
import ast
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper_share'
FIG = ROOT / 'data/model_extension/paper_figures_plain_language_20261006'
mapping = {}
source_records = []


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def copy(src, rel):
    src = ROOT / src
    dst = OUT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    mapping[src.resolve()] = dst
    source_records.append({'source': src.relative_to(ROOT).as_posix(), 'destination': rel,
                           'source_sha256': sha(src)})
    return dst


def portable(text, dst):
    def replace(m):
        label, target = m.group(1), m.group(2)
        target = target.replace('\\', '/').removeprefix('file:///')
        if not re.match(r'^[A-Za-z]:/', target):
            return m.group(0)
        p = Path(target).resolve()
        if p in mapping:
            return f'[{label}]({Path(os.path.relpath(mapping[p], dst.parent)).as_posix()})'
        # Unbundled archive references are explicitly non-clickable, not broken links.
        short = p.name
        return f'{label} (author archive: `{short}`; not included)'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace, text)


def main():
    OUT.mkdir(exist_ok=True)
    manifest = json.loads((FIG/'figure_manifest.json').read_text(encoding='utf-8'))
    fs = manifest['figures'] + manifest['supplements']
    for f in fs:
        for ext in ['png', 'svg']:
            src = FIG/f'{f["stem"]}.{ext}'
            copy(src, f'figures/{src.name}')
    for p in sorted((FIG/'tables').glob('*.csv')):
        copy(p, f'tables/{p.name}')
    copy('data/model_extension/paper_figures_draft_20261005/tables/test_fact_inclusion_audit.csv',
         'tables/test_fact_inclusion_audit.csv')
    for ext in ['png', 'svg']:
        copy(f'data/model_extension/paper_claims_map_20261007/paper_claims_map.{ext}', f'claims/paper_claims_map.{ext}')
        copy(f'data/model_extension/figure1_mockups_20261006/option_c_comparison_diagrams.{ext}', f'claims/figure1_option_c.{ext}')
    docs = ['ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT', 'INTEGRATED_PAPER_OUTLINE', 'FINAL_FINDINGS_SUMMARY', 'SAMPLE_ACCOUNTING']
    methods = ['REANALYSIS_PROTOCOL', 'WHOLE_GRAPH_ANALYSIS_PROTOCOL', 'MODEL_EXTENSION_PROTOCOL',
               'EXPLORATORY_CONFOUND_CHECKS_20260905', 'MATCHED_CHOICE_CHAT_V2_PROTOCOL',
               'MATCHED_CHOICE_CONTROL_PROTOCOL', 'MATCHED_CHOICE_POSITION_V3_PROTOCOL',
               'MATCHED_CHOICE_RESULTS_FOR_MANUSCRIPT', 'FAILURE_CASE_GRAPH_ANALYSIS_PLAN',
               'HISTORY_CHOICE_FINAL_PROTOCOL', 'POSITION_PILOT_ARTIFACT_DIAGNOSTIC']
    for folder, names in [('manuscript', docs), ('methods', methods)]:
        for name in names:
            copy(f'docs/papers/{name}.md', f'{folder}/{name}.md')
    copy('docs/writing/references/README.md', 'methods/WRITING_REFERENCES.md')
    copy(FIG/'LEGENDS.md', 'figures/LEGENDS.md')
    copy(FIG/'index.html', 'figures/index.html')
    mapping[(ROOT/'docs/writing/FIGURE_HEADLINES_AND_LEGENDS.md').resolve()] = OUT/'figures/LEGENDS.md'
    mapping[(FIG/'index.html').resolve()] = OUT/'figures/index.html'
    # Map earlier image filenames to their current presentation versions.
    draft = OUT/'manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md'
    body = draft.read_text(encoding='utf-8')
    for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', body):
        current = OUT/'figures'/Path(target).name
        assert current.exists(), target
        mapping[Path(target).resolve()] = current
    by_stem = {f['stem']: f for f in fs}
    # Reconcile all twelve captions to the exact figure package, in the sharing copy only.
    pattern = r'(!\[[^\]]*\]\([^\n]+/(figure[^/]+)\.png\))\n\n\*\*[^\n]+\n'
    def caption(m):
        f = by_stem[m.group(2)]
        prefix = re.match(r'figure(S?\d+)', f['stem']).group(1)
        return f'{m.group(1)}\n\n**Figure {prefix}. {f["title"]}.** {f["legend"]}\n'
    body, count = re.subn(pattern, caption, body)
    assert count == 12, count
    body = body.replace('date: "5 October 2026"', 'date: "8 October 2026"')
    body = body.replace('## Abstract', '> Sharing copy updated 8 October 2026: figures and captions match the current plain-language figure package. Scientific estimates and manuscript body are unchanged.\n\n## Abstract', 1)
    draft.write_text(body, encoding='utf-8')
    for p in [*OUT.glob('manuscript/*.md'), *OUT.glob('methods/*.md'), OUT/'figures/LEGENDS.md']:
        text = portable(p.read_text(encoding='utf-8'), p)
        if p.name == 'WRITING_REFERENCES.md':
            text = re.sub(r'^Local file:.*\n', '', text, flags=re.M)
        p.write_text(text, encoding='utf-8')

    # Explicit task-related seeds plus their static project-local imports.
    seeds = ['build_outline_figures_v2', 'build_paper_claims_map', 'mockup_figure1',
             'analyze_model_extension', 'convert_model_extension', 'analyze_failure_case_graphs',
             'analyze_history_closeout', 'analyze_matched_choice_controls', 'analyze_position_controls',
             'audit_paper_closeout', 'exploratory_confound_checks', 'reproduce_closeout',
             'validate_model_extension', 'validate_failure_case_graphs', 'validate_history_closeout',
             'validate_experiment_controls', 'validate_publication_analysis', 'plot_failure_case_graphs',
             'plot_model_extension', 'plot_publication_analysis', 'generate_model_extension',
             'run_failure_case_graphs', 'run_history_closeout', 'run_matched_choice_controls',
             'run_position_controls', 'diagnose_position_artifact', '2_convert_graph']
    selected = set()
    todo = list(seeds)
    tests = [p for p in (ROOT/'tests').glob('*.py') if 'traceback' not in p.name]
    for p in tests:
        copy(p, f'code/tests/{p.name}')
    def dependencies(p):
        for node in ast.walk(ast.parse(p.read_text(encoding='utf-8-sig'))):
            names = ([node.module] if isinstance(node, ast.ImportFrom) else
                     [n.name for n in node.names] if isinstance(node, ast.Import) else [])
            for name in names:
                if name and (ROOT/'scripts'/f'{name.split(".")[0]}.py').exists():
                    yield name.split('.')[0]
    for p in tests:
        todo.extend(dependencies(p))
    while todo:
        name = todo.pop()
        if name in selected:
            continue
        selected.add(name)
        p = ROOT/'scripts'/f'{name}.py'
        copy(p, f'code/scripts/{p.name}')
        todo.extend(dependencies(p))
    for name in ['requirements-closeout.txt', 'requirements-paper.txt', 'config/paper_control_manifest.csv', 'config/model_extension.json']:
        copy(name, f'code/{name}')
    copy('scripts/build_paper_share_package.py', 'code/scripts/build_paper_share_package.py')
    # Preserve archived evidence; do not misrepresent it as a new test run.
    for name in ['tests.log', 'environment.log', 'verification.json']:
        p = copy(f'data/model_extension/final_closeout_20261005/reproduction/{name}', f'provenance/archived_20261005_{name}')
        value = p.read_text(encoding='utf-8').replace(str(ROOT).replace('\\', '\\\\'), '<AUTHOR_WORKSPACE>').replace(str(ROOT), '<AUTHOR_WORKSPACE>')
        p.write_text(value, encoding='utf-8')
    copy(FIG/'VISUAL_QA.md', 'provenance/figure_wording_review.md')

    css = OUT/'review.css'
    assert css.exists(), 'Review stylesheet must be authored before packaging'
    pandoc = shutil.which('pandoc')
    assert pandoc, 'Pandoc required for the portable HTML review copies'
    for md in [OUT/'README.md', draft]:
        dst = OUT/'index.html' if md.name == 'README.md' else md.with_suffix('.html')
        style = 'review.css' if md.name == 'README.md' else '../review.css'
        subprocess.run([pandoc, str(md), '--standalone', '--toc', '--css', style,
                        '--metadata', 'title=Attribution graph paper review', '-o', str(dst)], check=True)
    # Verify all Markdown and HTML file links resolve after relocation.
    checked = 0
    missing = []
    for p in list(OUT.rglob('*.md')) + list(OUT.rglob('*.html')):
        value = p.read_text(encoding='utf-8')
        refs = re.findall(r'\]\(([^)]+)\)', value) if p.suffix == '.md' else re.findall(r'(?:href|src)="([^"]+)"', value)
        for ref in refs:
            if re.match(r'^(?:https?://|mailto:|#|data:)', ref):
                continue
            ref = html.unescape(ref).split('#')[0]
            checked += 1
            if not (p.parent/ref).exists():
                missing.append([p.relative_to(OUT).as_posix(), ref])
    assert not missing, missing
    (OUT/'provenance/link_audit.json').write_text(json.dumps({'checked': checked, 'missing': missing}, indent=2), encoding='utf-8')
    # Scan contents without printing potential credentials.
    for p in OUT.rglob('*'):
        if p.is_file() and p.suffix not in ['.png']:
            raw = p.read_bytes()
            assert not re.search(rb'\b(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})', raw), f'Possible credential in {p.name}'
    files = [{'path': p.relative_to(OUT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
             for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'package_manifest.json']
    manifest = {'date': '2026-10-08', 'status': 'working_paper_review_package', 'files': files,
                'sources': source_records, 'caption_reconciliations': count,
                'excluded': ['Raw exports', 'Tokenizer/model files', 'Credentials', 'Reference PDFs', 'Local release archive', 'Unrelated edits'],
                'reproduction': 'Source inspection and figure tables only; full analysis requires excluded authorized archive'}
    (OUT/'provenance/package_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    dest = ROOT/'data/model_extension/paper_share_20261008'
    dest.mkdir(exist_ok=True)
    archive = dest/'attribution_graph_paper_review_20261008.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                z.write(p, 'paper_share/'+p.relative_to(OUT).as_posix())
    with zipfile.ZipFile(archive) as z:
        for f in files:
            assert hashlib.sha256(z.read('paper_share/'+f['path'])).hexdigest() == f['sha256']
    print(json.dumps({'folder': str(OUT), 'zip': str(archive), 'files': len(files)+1,
                      'archive_bytes': archive.stat().st_size, 'portable_links_checked': checked,
                      'archive_sha256': sha(archive)}, indent=2))


if __name__ == '__main__':
    main()
