#!/usr/bin/env python3
"""Make a verified local APMCM evidence archive, not an official-platform submission."""
import argparse
import copy
import datetime
import json
import zipfile
from pathlib import Path
from audit_bundle import audit, resolve, digest, approval_hash


def package(root, manifest, output, rules=None, final=False):
    # Freeze caller-owned metadata so audit, approval and archive use one version.
    manifest, rules = copy.deepcopy(manifest), copy.deepcopy(rules)
    result = audit(root, manifest, rules, final)
    if result['status'] != 'pass':
        raise ValueError('Audit failed: ' + json.dumps(result['errors'], ensure_ascii=False))
    if final:
        approval = manifest.get('team_approval', {})
        if approval.get('approved') is not True or not approval.get('name') or approval.get('manifest_sha256') != approval_hash(manifest):
            raise ValueError('Missing real, hash-bound team approval')
        timestamp = approval.get('timestamp')
        if not isinstance(timestamp, str): raise ValueError('Approval timestamp must be an ISO string')
        datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    if output.exists(): raise ValueError('Refusing to overwrite existing package')
    reserved = {'BUNDLE-MANIFEST.json', 'AUDIT.json', 'ARCHIVE-NOTICE.txt', 'RULES.json'}
    if reserved.intersection(result['checked_files']): raise ValueError('Reserved archive entry collision')
    # Read and re-hash before any output is created, so an intervening edit cannot silently pass.
    data = {}
    for name, sha in result['checked_files'].items():
        b = resolve(root, name).read_bytes()
        if digest(b) != sha: raise ValueError('Artifact changed during packaging: ' + name)
        data[name] = b
    data['BUNDLE-MANIFEST.json'] = json.dumps(manifest, ensure_ascii=False, indent=2).encode()
    if final:
        data['RULES.json'] = json.dumps(rules, ensure_ascii=False, indent=2).encode()
    data['AUDIT.json'] = json.dumps(result, ensure_ascii=False, indent=2).encode()
    data['ARCHIVE-NOTICE.txt'] = b'LOCAL EVIDENCE ARCHIVE. Not the official platform upload contract. No signatures are generated.\n'
    created = False
    try:
        stream = output.open('xb')
        created = True
        with stream, zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, b in sorted(data.items()):
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, b)
    except Exception:
        if created and output.exists(): output.unlink()
        raise
    return {'output': str(output), 'sha256': digest(output.read_bytes()), 'entries': len(data), 'kind': 'local-evidence-archive'}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--rules', type=Path)
    p.add_argument('--final', action='store_true')
    a = p.parse_args()
    try:
        r = package(a.root, json.loads(a.manifest.read_text()), a.output,
                    json.loads(a.rules.read_text()) if a.rules else None, a.final)
        print(json.dumps(r, indent=2))
    except (ValueError, OSError, TypeError) as e:
        print(json.dumps({'status': 'fail', 'error': str(e)})); raise SystemExit(1)
