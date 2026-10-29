#!/usr/bin/env python3
"""Local records and handoffs for Codex-assisted prop image generation.

This CLI never invokes an image provider or acquires a GPU. Run --help for commands.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import warnings

from PIL import Image, UnidentifiedImageError


FORMAT = 'prop-to-image/0.1'
Image.MAX_IMAGE_PIXELS = 40_000_000
EXTENSIONS = {'PNG': '.png', 'JPEG': '.jpg', 'MPO': '.jpg', 'WEBP': '.webp'}


class WorkflowError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise WorkflowError(f'{label} must be a nonempty string')
    return value.strip()


def read_object(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise WorkflowError(f'Expected a JSON object in {path}')
    return value


def atomic_json(path, value):
    fd, name = tempfile.mkstemp(prefix='.writing-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def inside(root, relative):
    p = Path(relative)
    resolved = (root / p).resolve()
    if p.is_absolute() or not resolved.is_relative_to(root):
        raise WorkflowError('Artifact path must stay inside the project')
    return resolved


def image_info(path):
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        try:
            with Image.open(path) as im:
                fmt, size = im.format, im.size
                frames = getattr(im, 'n_frames', 1)
                if fmt not in EXTENSIONS or (frames != 1 and fmt != 'MPO'):
                    raise WorkflowError('Use a still PNG, JPEG/MPO, or WebP image')
                im.verify()
            with Image.open(path) as im:
                for frame in range(frames):
                    im.seek(frame)
                    im.load()
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError,
                Image.DecompressionBombWarning, SyntaxError) as exc:
            raise WorkflowError(f'Invalid image: {path.name}: {exc}') from exc
    return {'format': fmt, 'width': size[0], 'height': size[1],
            'frame_count': frames, 'primary_frame': 0}


def artifact(root, path, **metadata):
    return {'path': path.relative_to(root).as_posix(), 'sha256': digest(path),
            'bytes': path.stat().st_size, **metadata}


def copy_image(root, source, stem):
    info = image_info(source)
    dest = inside(root, str(stem) + EXTENSIONS[info['format']])
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise WorkflowError(f'Artifact already exists: {dest.name}')
    shutil.copyfile(source, dest)
    try:
        image_info(dest)
        return artifact(root, dest, **info)
    except BaseException:
        dest.unlink(missing_ok=True)
        raise


def verify(root, item):
    path = inside(root, item['path'])
    if not path.is_file() or digest(path) != item['sha256']:
        raise WorkflowError(f'Artifact checksum mismatch: {item["path"]}')
    return path


def verify_inputs(root, record):
    verify(root, record['brief'])
    verify(root, record['source'])
    for item in record['style_references']:
        verify(root, item)


@contextmanager
def project_lock(root):
    if not root.is_dir():
        raise WorkflowError('Project does not exist; use init first')
    lock = root / '.write.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise WorkflowError('Project is locked by another writer. If stale, verify the owner has stopped before removing .write.lock.') from exc
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(json.dumps({'pid': os.getpid(), 'created_at': now()}))
        yield
    finally:
        lock.unlink(missing_ok=True)


def find(items, identity, kind):
    match = next((x for x in items if x['id'] == identity), None)
    if match is None:
        raise WorkflowError(f'Unknown {kind}: {identity}')
    return match


def next_id(items, prefix):
    return f'{prefix}-{len(items) + 1:04d}'


def init(args, root):
    if root.exists():
        raise WorkflowError('Project already exists; refusing to overwrite it')
    source = Path(args.source).resolve()
    brief = read_object(args.brief)
    for key in ('fixed_features', 'allowed_changes', 'unknowns'):
        values = brief.get(key, [])
        if not isinstance(values, list) or any(not isinstance(x, str) or not x.strip() for x in values):
            raise WorkflowError(f'Brief {key} must be a list of nonempty strings')
    image_info(source)
    styles = [Path(p).resolve() for p in args.style]
    for path in styles:
        image_info(path)
    asset_id, title = text(args.asset_id, 'Asset ID'), text(args.title, 'Title')
    root.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.prop-init-', dir=root.parent))
    try:
        original = copy_image(staging, source, 'source/original')
        refs = [copy_image(staging, path, f'source/style-{i:02d}') for i, path in enumerate(styles, 1)]
        atomic_json(staging / 'brief.json', brief)
        record = {'format': FORMAT, 'asset_id': asset_id, 'title': title,
                  'mode': args.mode, 'created_at': now(), 'source': original,
                  'source_role': args.source_role, 'style_references': refs,
                  'brief': artifact(staging, staging / 'brief.json'),
                  'canonical_record': {'uri': args.canonical_record_uri,
                                       'revision': args.canonical_record_revision,
                                       'source_revision_id': args.source_revision_id},
                  'jobs': [], 'candidates': [], 'selection': None, 'selection_history': []}
        atomic_json(staging / 'project.json', record)
        if root.exists():
            raise WorkflowError('Project appeared during initialization; refusing to overwrite')
        staging.rename(root)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {'project_path': str(root), 'asset_id': asset_id, 'status': 'initialized'}


def prepare(args, root, record):
    verify_inputs(root, record)
    title, direction = text(args.title, 'Title'), text(args.direction, 'Direction')
    brief = read_object(verify(root, record['brief']))
    mode = ('Keep the outer contour, proportions, openings, grip position, and attachments unchanged. Change finish only.'
            if record['mode'] == 'finish-only' else
            'Retain the fixed features below; change only the explicitly allowed exterior details.')
    prompt = (f'Create one film-prop appearance study. Image 1 is the edit target '
              f'({record["source_role"]}); any additional images are style references only.\n'
              f'Mode: {record["mode"]}. {mode}\nAppearance direction: {direction}\n'
              f'Brief: {json.dumps(brief, ensure_ascii=False)}\n'
              'Keep the entire object visible. Preserve its identity and do not add labels or watermarks. '
              'Treat this as cinematic exterior styling; do not invent functional internal mechanisms.')
    job_id = next_id(record['jobs'], 'job')
    request = {'tool': 'image_gen.imagegen', 'arguments': {
        'prompt': prompt, 'referenced_image_paths': [str(verify(root, record['source']))] +
            [str(verify(root, x)) for x in record['style_references']],
        'transparent_background': bool(args.transparent)},
        'execution': 'Codex calls the built-in tool; this CLI does not execute generation',
        'input_sha256': [record['source']['sha256']] + [x['sha256'] for x in record['style_references']]}
    path = root / 'jobs' / f'{job_id}.json'
    path.parent.mkdir(exist_ok=True)
    if path.exists():
        raise WorkflowError('Request file already exists; inspect an interrupted prior write')
    atomic_json(path, request)
    record['jobs'].append({'id': job_id, 'title': title, 'direction': direction,
                           'status': 'prepared', 'created_at': now(), 'request': artifact(root, path)})
    return {'job_id': job_id, 'request_path': str(path), 'status': 'prepared'}


def add_candidate(root, record, image_path, title, provenance, job_id=None, canonical_revision_id=None):
    title = text(title, 'Title')
    candidate_id = next_id(record['candidates'], 'candidate')
    image = copy_image(root, Path(image_path).resolve(), f'candidates/{candidate_id}')
    candidate = {'id': candidate_id, 'title': title, 'image': image,
                 'created_at': now(), 'job_id': job_id, 'provenance': provenance,
                 'canonical_revision_id': canonical_revision_id}
    record['candidates'].append(candidate)
    return {'candidate_id': candidate_id, 'image_path': str(root / image['path']), 'status': 'candidate'}


def complete(args, root, record):
    verify_inputs(root, record)
    job = find(record['jobs'], args.job, 'job')
    if job['status'] != 'prepared':
        raise WorkflowError('Job is terminal; prepare a new job for another attempt')
    request = read_object(verify(root, job['request']))
    provider = text(args.provider, 'Provider')
    result = add_candidate(root, record, args.image, job['title'], {
        'origin': 'generated-from-prepared-job', 'provider': provider, 'model': args.model,
        'prompt': request['arguments']['prompt'], 'request_sha256': job['request']['sha256'],
        'notes': args.notes}, job_id=job['id'])
    job.update(status='completed', completed_at=now(), candidate_id=result['candidate_id'])
    return result


def fail(args, root, record):
    job = find(record['jobs'], args.job, 'job')
    if job['status'] != 'prepared':
        raise WorkflowError('Job is terminal; prepare a new job for another attempt')
    job.update(status=args.status, completed_at=now(), reason=text(args.reason, 'Reason'))
    return {'job_id': job['id'], 'status': job['status']}


def import_candidate(args, root, record):
    verify_inputs(root, record)
    provenance = read_object(args.provenance)
    text(provenance.get('origin'), 'Provenance origin')
    provenance.setdefault('model', None)
    provenance.setdefault('prompt', None)
    return add_candidate(root, record, args.image, args.title, provenance,
                         canonical_revision_id=args.canonical_revision_id)


def select(args, root, record):
    verify_inputs(root, record)
    c = find(record['candidates'], args.candidate, 'candidate')
    verify(root, c['image'])
    selection = {'id': next_id(record['selection_history'], 'selection'), 'candidate_id': c['id'],
                 'sha256': c['image']['sha256'], 'actor': text(args.by, 'Selected by'),
                 'selected_at': now(), 'notes': args.notes,
                 'scope': 'Local handoff selection; canonical approval unchanged'}
    record['selection'] = selection
    record['selection_history'].append(selection)
    return {'selection': selection}


def gallery(args, root, record):
    verify_inputs(root, record)
    esc = lambda value: html.escape(str(value), quote=True)
    selected = record['selection']['candidate_id'] if record['selection'] else None
    cards = []
    for c in record['candidates']:
        verify(root, c['image'])
        path = esc(c['image']['path'])
        label = 'Selected for handoff' if c['id'] == selected else 'Candidate'
        note = c['provenance'].get('notes') or ''
        cards.append(f'<article><a href="{path}"><img loading="lazy" src="{path}" alt="{esc(c["title"])}"></a>'
                     f'<div class="caption"><small>{esc(c["id"])} · {label}</small><h2>{esc(c["title"])}</h2>'
                     f'<p>{esc(note)}</p></div></article>')
    jobs = ''.join(f'<li><strong>{esc(j["title"])}</strong> — {esc(j["status"])}'
                   f'{": " + esc(j["reason"]) if j.get("reason") else ""}</li>' for j in record['jobs'])
    source = esc(record['source']['path'])
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(record['title'])} · Prop to Image</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#151819;color:#e9e8e3;font:16px/1.5 system-ui,sans-serif}}
main{{max-width:1440px;margin:auto;padding:40px 28px}}header{{margin:0 0 32px}}small{{color:#a6b2b0;font-size:12px;letter-spacing:.06em}}
h1{{font-size:clamp(32px,5vw,62px);font-weight:500;letter-spacing:-.045em;margin:8px 0 12px;line-height:1.05}}h2{{font-size:22px;font-weight:500;margin:8px 0}}
p{{color:#b9c3c0;max-width:850px}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}}article{{background:#202526;border:1px solid #37413f;border-radius:10px;overflow:hidden}}
img{{width:100%;aspect-ratio:2/1;object-fit:contain;display:block;background:#101313}}.caption{{padding:18px 20px}}.source{{max-width:1000px;margin-bottom:36px}}
a{{color:#e2b98b}}footer{{margin-top:36px;border-top:1px solid #37413f;padding-top:20px}}ul{{padding-left:20px}}@media(max-width:760px){{.grid{{grid-template-columns:1fr}}main{{padding:26px 16px}}}}</style>
<main><header><small>IDEA TO PROP / {esc(record['asset_id'])}</small><h1>{esc(record['title'])}</h1>
<p>{esc(record['mode'])} · {len(record['candidates'])} candidates · {'Selection recorded' if selected else 'No selection yet'}</p></header>
<h2>Preserved source</h2><article class="source"><a href="{source}"><img src="{source}" alt="Preserved source reference"></a><div class="caption"><small>{esc(record['source_role'])}</small></div></article>
<h2>Appearance candidates</h2><div class="grid">{''.join(cards) or '<p>No completed images yet.</p>'}</div>
<footer><h2>Generation jobs</h2><ul>{jobs or '<li>No generation jobs; existing images may have been imported.</li>'}</ul>
<p>This gallery displays preserved files. Selection is recorded through Codex or the CLI. A chosen appearance does not establish physical fit or approve inferred 3D surfaces.</p>
<a href="project.json">Project record</a> · <a href="brief.json">Appearance brief</a></footer></main></html>'''
    (root / 'index.html').write_text(page, encoding='utf-8')
    return {'gallery_path': str(root / 'index.html'), 'candidates': len(cards)}


def handoff(args, root, record):
    verify_inputs(root, record)
    selected = record['selection']
    if args.provisional_reason and not args.candidate:
        raise WorkflowError('A provisional handoff requires --candidate')
    if args.candidate:
        identity = args.candidate
        is_selected = selected is not None and selected['candidate_id'] == identity
        if not is_selected and not args.provisional_reason:
            raise WorkflowError('Candidate is not selected; use select or supply --provisional-reason')
    elif selected:
        identity = selected['candidate_id']
    else:
        raise WorkflowError('No selected candidate; use select first or explicitly export a provisional candidate')
    c = find(record['candidates'], identity, 'candidate')
    source = verify(root, c['image'])
    provisional = bool(args.provisional_reason)
    if not provisional and selected['sha256'] != c['image']['sha256']:
        raise WorkflowError('Selection checksum mismatch')
    link = record['canonical_record']
    linked = all((link['uri'], link['revision'], c['canonical_revision_id']))
    parent = root / 'handoffs'
    parent.mkdir(exist_ok=True)
    dest = Path(tempfile.mkdtemp(prefix=f'{identity}-', dir=parent))
    try:
        image_path = dest / ('input' + source.suffix)
        shutil.copyfile(source, image_path)
        result = {'format': 'prop-to-image-handoff/0.1', 'asset_id': record['asset_id'], 'created_at': now(),
                  'linkage_status': 'linked-record-snapshot' if linked else 'unlinked-tool-handoff',
                  'canonical_record': link, 'source_candidate_id': identity,
                  'source_revision_id': c['canonical_revision_id'],
                  'parent_revision_ids': [c['canonical_revision_id']] if c['canonical_revision_id'] else [],
                  'selection_status': 'provisional' if provisional else 'selected',
                  'selection': None if provisional else selected,
                  'provisional_reason': text(args.provisional_reason, 'Provisional reason') if provisional else None,
                  'image': artifact(dest, image_path), 'provenance': c['provenance'],
                  'source_image_sha256': record['source']['sha256'], 'brief_sha256': record['brief']['sha256'],
                  'geometry': {'units': None, 'dimensions': None, 'up_axis': None}, 'model_created': False,
                  'limitations': ['Image-to-3D generation has not been executed by this tool.',
                                  'A single view does not determine reverse-side geometry, thickness, or physical fit.',
                                  'Local selection does not modify canonical approval.']}
        atomic_json(dest / 'handoff.json', result)
    except BaseException:
        shutil.rmtree(dest)
        raise
    return {'handoff_path': str(dest / 'handoff.json'), 'selection_status': result['selection_status']}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    commands = {name: sub.add_parser(name) for name in ('init', 'prepare', 'complete', 'fail', 'import', 'select', 'gallery', 'handoff')}
    for cmd in commands.values():
        cmd.add_argument('project', help='Local asset project directory')
    c = commands['init']
    for flag in ('source', 'brief', 'asset-id', 'title'):
        c.add_argument('--' + flag, required=True)
    c.add_argument('--mode', choices=['finish-only', 'exterior-redesign'], required=True)
    c.add_argument('--source-role', choices=['physical-photo', 'generated-concept', 'unknown-reference'], default='physical-photo')
    c.add_argument('--style', action='append', default=[])
    for flag in ('canonical-record-uri', 'canonical-record-revision', 'source-revision-id'):
        c.add_argument('--' + flag)
    c = commands['prepare']
    c.add_argument('--title', required=True)
    c.add_argument('--direction', required=True)
    c.add_argument('--transparent', action='store_true')
    c = commands['complete']
    for flag in ('job', 'image', 'provider'):
        c.add_argument('--' + flag, required=True)
    c.add_argument('--model')
    c.add_argument('--notes')
    c = commands['fail']
    c.add_argument('--job', required=True)
    c.add_argument('--status', choices=['failed', 'blocked'], required=True)
    c.add_argument('--reason', required=True)
    c = commands['import']
    for flag in ('image', 'title', 'provenance'):
        c.add_argument('--' + flag, required=True)
    c.add_argument('--canonical-revision-id')
    c = commands['select']
    c.add_argument('--candidate', required=True)
    c.add_argument('--by', required=True)
    c.add_argument('--notes')
    c = commands['handoff']
    c.add_argument('--candidate')
    c.add_argument('--provisional-reason')
    return p


def main():
    args = parser().parse_args()
    root = Path(args.project).expanduser().resolve()
    try:
        if args.command == 'init':
            result = init(args, root)
        else:
            with project_lock(root):
                record = read_object(root / 'project.json')
                if record.get('format') != FORMAT:
                    raise WorkflowError('Unsupported project record format')
                fn = import_candidate if args.command == 'import' else globals()[args.command]
                result = fn(args, root, record)
                if args.command not in ('gallery', 'handoff'):
                    atomic_json(root / 'project.json', record)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0
    except (WorkflowError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f'prop-to-image: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
