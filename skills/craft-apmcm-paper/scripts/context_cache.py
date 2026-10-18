#!/usr/bin/env python3
"""Bind a compact brief to local evidence hashes; no LLM or network calls."""
import argparse
import json
from pathlib import Path
from audit_bundle import digest, resolve


def snapshot(root, names, facts, max_chars=6000):
    if not names: raise ValueError('At least one evidence file is required')
    text = resolve(root, facts).read_text(encoding='utf-8')
    if len(text) > max_chars: raise ValueError('Brief exceeds max_chars; shorten or explicitly raise the limit')
    files = []
    for name in dict.fromkeys([*names, facts]):
        files.append({'path': name, 'sha256': digest(resolve(root, name).read_bytes())})
    return {'version': 1, 'facts': facts, 'files': files,
            'scope': 'Freshness of listed dependencies only. Contents and completeness require review.'}


def check(root, record, show_facts=False):
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
    result = {'status': 'stale' if dirty else 'fresh', 'changed_files': dirty,
              'checked_files': len(seen), 'scope': record.get('scope')}
    if not dirty and show_facts: result['facts'] = resolve(root, record['facts']).read_text(encoding='utf-8')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('snapshot'); a.add_argument('--root', type=Path, required=True)
    a.add_argument('--file', action='append', required=True); a.add_argument('--facts', required=True)
    a.add_argument('--output', type=Path, required=True); a.add_argument('--max-chars', type=int, default=6000)
    b = sub.add_parser('check'); b.add_argument('--root', type=Path, required=True)
    b.add_argument('--manifest', type=Path, required=True); b.add_argument('--show-facts', action='store_true')
    args = p.parse_args()
    try:
        if args.command == 'snapshot':
            r = snapshot(args.root, args.file, args.facts, args.max_chars)
            if args.output.resolve() in {resolve(args.root, f['path']) for f in r['files']}:
                raise ValueError('Cache output cannot overwrite evidence or brief')
            args.output.write_text(json.dumps(r, indent=2, ensure_ascii=False)+'\n')
            print(json.dumps({'status': 'created', 'files': len(r['files']), 'output': str(args.output)})); return 0
        r = check(args.root, json.loads(args.manifest.read_text()), args.show_facts)
        print(json.dumps(r, indent=2, ensure_ascii=False)); return 0 if r['status']=='fresh' else 1
    except (ValueError, TypeError, OSError) as e:
        print(json.dumps({'status': 'fail', 'error': str(e)})); return 2

if __name__=='__main__': raise SystemExit(main())
