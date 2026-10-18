#!/usr/bin/env python3
"""Bind a compact brief to local evidence hashes; no LLM or network calls."""
import argparse
import json
from pathlib import Path
from audit_bundle import digest, resolve


def impact_map(data, bound=None):
    """Validate explicit dependencies; do not infer semantic correctness."""
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('items'), list) or not data['items']:
        raise ValueError('Invalid impact map')
    items, ids = [], set()
    for item in data['items']:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id'].strip() or item['id'] in ids:
            raise ValueError('Invalid or duplicate review item')
        ids.add(item['id'])
        files, deps = item.get('files', []), item.get('depends_on', [])
        for values in (files, deps):
            if not isinstance(values, list) or any(not isinstance(x, str) or not x for x in values) or len(values) != len(set(values)):
                raise ValueError('Invalid review dependencies')
        if not files and not deps: raise ValueError('Review item needs evidence or an upstream item')
        for name in files:
            if Path(name).is_absolute() or '..' in Path(name).parts:
                raise ValueError('Unsafe impact path')
            if bound is not None and name not in bound: raise ValueError('Unbound impact dependency: ' + name)
        items.append({'id': item['id'], 'files': files, 'depends_on': deps})
    for item in items:
        if any(x not in ids for x in item['depends_on']): raise ValueError('Unknown upstream review item')
    pending = {x['id']: set(x['depends_on']) for x in items}
    while pending:
        ready = {key for key, deps in pending.items() if not deps}
        if not ready: raise ValueError('Cyclic review dependencies')
        pending = {key: deps - ready for key, deps in pending.items() if key not in ready}
    opened = data.get('open_items', [])
    if not isinstance(opened, list) or any(not isinstance(x, str) or x not in ids for x in opened) or len(opened) != len(set(opened)):
        raise ValueError('Invalid unresolved review items')
    return {'version': 1, 'items': items, 'open_items': opened}


def snapshot(root, names, facts, max_chars=6000, impact=None):
    if not names: raise ValueError('At least one evidence file is required')
    text = resolve(root, facts).read_text(encoding='utf-8')
    if len(text) > max_chars: raise ValueError('Brief exceeds max_chars; shorten or explicitly raise the limit')
    mapping = None
    if impact is not None:
        mapping = impact_map(json.loads(resolve(root, impact).read_text(encoding='utf-8')))
        names = [*names, impact, *(name for item in mapping['items'] for name in item['files'])]
    files = []
    for name in dict.fromkeys([*names, facts]):
        files.append({'path': name, 'sha256': digest(resolve(root, name).read_bytes())})
    record = {'version': 1, 'facts': facts, 'files': files,
              'scope': 'Freshness of listed dependencies only. Contents and completeness require review.'}
    if mapping is not None: record.update({'impact_path': impact, 'impact_map': mapping})
    return record


def check(root, record, show_facts=False, context_changed=False):
    if not isinstance(record, dict) or record.get('version') != 1 or not isinstance(record.get('files'), list) or not record['files']:
        raise ValueError('Invalid cache record')
    dirty, seen = [], set()
    for f in record['files']:
        if not isinstance(f, dict) or not isinstance(f.get('path'), str) or f['path'] in seen:
            raise ValueError('Malformed or duplicate dependency')
        name = f['path']; seen.add(name)
        try:
            if digest(resolve(root, name).read_bytes()) != f.get('sha256'): dirty.append({'path': name, 'reason': 'changed'})
        except (ValueError, OSError) as e: dirty.append({'path': name, 'reason': str(e)})
    if record.get('facts') not in seen: raise ValueError('Brief itself must be hash-bound')
    result = {'status': 'stale' if dirty or context_changed else 'fresh', 'changed_files': dirty,
              'checked_files': len(seen), 'scope': record.get('scope')}
    if context_changed: result['context_changed'] = True
    if 'impact_map' in record:
        if record.get('impact_path') not in seen: raise ValueError('Impact map itself must be hash-bound')
        mapping = impact_map(record['impact_map'], seen)
        changed = {x['path'] for x in dirty}
        mapped = {name for item in mapping['items'] for name in item['files']}
        global_change = context_changed or bool(changed & {record['facts'], record['impact_path']}) or bool(changed - mapped)
        affected = {item['id'] for item in mapping['items'] if global_change or changed.intersection(item['files'])}
        while True:
            more = {item['id'] for item in mapping['items'] if affected.intersection(item['depends_on'])}
            if more.issubset(affected): break
            affected |= more
        opened = set(mapping['open_items'])
        result['review_plan'] = {
            'requires_full_review': global_change,
            'affected_items': [x['id'] for x in mapping['items'] if x['id'] in affected],
            'unresolved_items': mapping['open_items'],
            'review_items': [x['id'] for x in mapping['items'] if x['id'] in affected | opened],
            'unaffected_items': [x['id'] for x in mapping['items'] if x['id'] not in affected | opened],
            'scope': 'Explicit file/item dependencies only; unaffected does not mean verified. Rebaseline changed maps and review omitted dependencies.'}
    if not dirty and not context_changed and show_facts: result['facts'] = resolve(root, record['facts']).read_text(encoding='utf-8')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('snapshot'); a.add_argument('--root', type=Path, required=True)
    a.add_argument('--file', action='append', required=True); a.add_argument('--facts', required=True)
    a.add_argument('--output', type=Path, required=True); a.add_argument('--max-chars', type=int, default=6000)
    a.add_argument('--impact-map', help='Optional explicit review dependencies JSON, relative to root')
    b = sub.add_parser('check'); b.add_argument('--root', type=Path, required=True)
    b.add_argument('--manifest', type=Path, required=True); b.add_argument('--show-facts', action='store_true')
    b.add_argument('--context-changed', action='store_true', help='Interpretation or user instructions changed even if files did not')
    args = p.parse_args()
    try:
        if args.command == 'snapshot':
            r = snapshot(args.root, args.file, args.facts, args.max_chars, args.impact_map)
            if args.output.resolve() in {resolve(args.root, f['path']) for f in r['files']}:
                raise ValueError('Cache output cannot overwrite evidence or brief')
            args.output.write_text(json.dumps(r, indent=2, ensure_ascii=False)+'\n')
            print(json.dumps({'status': 'created', 'files': len(r['files']), 'output': str(args.output)})); return 0
        r = check(args.root, json.loads(args.manifest.read_text()), args.show_facts, args.context_changed)
        print(json.dumps(r, indent=2, ensure_ascii=False)); return 0 if r['status']=='fresh' else 1
    except (ValueError, TypeError, OSError) as e:
        print(json.dumps({'status': 'fail', 'error': str(e)})); return 2

if __name__=='__main__': raise SystemExit(main())
