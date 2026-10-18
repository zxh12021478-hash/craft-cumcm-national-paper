#!/usr/bin/env python3
"""Validate an APMCM evidence ledger; never claim scientific or prize certification."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_RULES = ('schedule', 'language', 'ai_policy', 'page_limit', 'page_structure',
                  'anonymity', 'english_template', 'file_naming', 'support_materials', 'control_sheet', 'submission_channel')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def resolve(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError('Unsafe relative path: ' + repr(name))
    target = (root / name).resolve()
    target.relative_to(root.resolve())
    if not target.is_file():
        raise ValueError('Missing file: ' + name)
    return target


def pointer(obj, path):
    if not isinstance(path, str) or not path.startswith('/'):
        raise ValueError('JSON pointer must start with /')
    for key in path[1:].split('/'):
        key = key.replace('~1', '/').replace('~0', '~')
        obj = obj[int(key)] if isinstance(obj, list) else obj[key]
    if isinstance(obj, bool) or not isinstance(obj, (int, float)) or not math.isfinite(obj):
        raise ValueError('Claim source must be a finite numeric value')
    return obj


def rules_hash(rules):
    return digest(json.dumps(rules, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())


def approval_hash(manifest):
    m = dict(manifest)
    m.pop('team_approval', None)
    return digest(json.dumps(m, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())


def audit(root, manifest, rules=None, final=False):
    # Reject malformed JSON shapes before indexing or iterating their records.
    shape_errors = []
    if not isinstance(manifest, dict):
        shape_errors.append('Manifest must be an object')
    else:
        for field in ('files', 'claims', 'required_outputs'):
            records = manifest.get(field, [])
            if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
                shape_errors.append(field + ' must be an array of objects')
        for field in ('reviews', 'rule_checks'):
            records = manifest.get(field, {})
            if not isinstance(records, dict) or any(not isinstance(r, dict) for r in records.values()):
                shape_errors.append(field + ' must be an object of review objects')
        if 'team_approval' in manifest and not isinstance(manifest['team_approval'], dict):
            shape_errors.append('team_approval must be an object')
    if rules is not None:
        if not isinstance(rules, dict) or not isinstance(rules.get('rules', {}), dict):
            shape_errors.append('Rules profile and rules must be objects')
        elif any(not isinstance(r, dict) for r in rules.get('rules', {}).values()):
            shape_errors.append('Rule entries must be objects')
    if shape_errors:
        return {'status': 'fail', 'final': final, 'scope': 'invalid input; no audit completed',
                'errors': [{'code': 'INVALID_INPUT', 'detail': e} for e in shape_errors],
                'warnings': [], 'checked_files': {}, 'claim_count': 0, 'requirement_count': 0}
    errors, warnings, checked = [], [], {}
    def fail(code, detail): errors.append({'code': code, 'detail': str(detail)})
    if manifest.get('event') != 'APMCM': fail('EVENT', 'Expected APMCM')
    if manifest.get('mode') not in ('training', 'historical-rehearsal', 'live-contest'):
        fail('MODE', 'Unknown mode')
    files = manifest.get('files', [])
    if not files: fail('FILES_EMPTY', 'No bound artifacts')
    for item in files:
        try:
            name, expected = item['path'], item['sha256']
            if name in checked: raise ValueError('Duplicate path: ' + name)
            actual = digest(resolve(root, name).read_bytes())
            checked[name] = actual
            if not re.fullmatch('[0-9a-f]{64}', expected) or actual != expected:
                fail('HASH_MISMATCH', name)
        except (KeyError, ValueError, TypeError, OSError) as e: fail('FILE', e)
    def bound(name):
        if name not in checked: raise ValueError('Unbound artifact: ' + str(name))
        return resolve(root, name)
    try:
        paper = bound(manifest['paper']).read_text(encoding='utf-8')
        results = json.loads(bound(manifest['results']).read_text(encoding='utf-8'))
    except (KeyError, ValueError, OSError, UnicodeError) as e:
        fail('INPUT', e); paper, results = '', {}
    claims = manifest.get('claims', [])
    if not claims: fail('CLAIMS_EMPTY', 'No numerical claims mapped')
    claim_ids = set()
    for c in claims:
        try:
            if not c['id'] or c['id'] in claim_ids: raise ValueError('Missing/duplicate claim ID')
            claim_ids.add(c['id'])
            quote, token = c['quote'], c['token']
            if not quote or paper.count(quote) != 1: raise ValueError('Quote must occur exactly once')
            number = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
            if not isinstance(token, str) or not re.fullmatch(number, token):
                raise ValueError('Token is not a numeric string')
            if not re.search(r'(?<![\w.−-])' + re.escape(token) + r'(?!\w|\.\d)', quote):
                raise ValueError('Numeric token not present as a whole token in quote')
            value = float(token)
            scale, tol = float(c.get('scale', 1)), float(c.get('absolute_tolerance', 0))
            if not all(math.isfinite(x) for x in (value, scale, tol)) or tol < 0:
                raise ValueError('Invalid number, scale or tolerance')
            if not c.get('unit'): raise ValueError('Unit must be explicit, including dimensionless')
            expected = pointer(results, c['pointer']) * scale
            if not math.isfinite(expected) or abs(value - expected) > tol + 1e-12:
                raise ValueError(f'Number differs: manuscript={value}, result={expected}, tolerance={tol}')
        except (KeyError, ValueError, TypeError, IndexError, OSError) as e:
            fail('CLAIM', f"{c.get('id', '?')}: {e}")
    outputs = manifest.get('required_outputs', [])
    if not outputs: fail('COVERAGE_EMPTY', 'No original-problem requirement matrix')
    ids = set()
    for o in outputs:
        try:
            if not o['id'] or o['id'] in ids: raise ValueError('Missing/duplicate output ID')
            ids.add(o['id'])
            if o.get('status') != 'verified' or not o.get('review_note') or not o.get('evidence'):
                raise ValueError('Unverified output or missing content-level review')
            for name in o['evidence']: bound(name)
        except (KeyError, ValueError, TypeError) as e: fail('OUTPUT', f"{o.get('id', '?')}: {e}")
    # Compare against the pre-draft original-question inventory, not only the
    # author's returned list (which could silently omit an entire question).
    requirement_matrix = manifest.get('requirement_matrix')
    if requirement_matrix is not None:
        try:
            matrix = json.loads(bound(requirement_matrix).read_text(encoding='utf-8'))
            records = matrix.get('requirements') if isinstance(matrix, dict) else None
            if not isinstance(records, list) or not records:
                raise ValueError('Original requirement matrix must contain requirements')
            expected_ids = set()
            for row in records:
                if not isinstance(row, dict): raise ValueError('Requirement must be an object')
                for key in ('id', 'request', 'deliverable', 'acceptance'):
                    if not isinstance(row.get(key), str) or not row[key].strip():
                        raise ValueError('Missing requirement field: ' + key)
                if row['id'] in expected_ids: raise ValueError('Duplicate original requirement ID')
                expected_ids.add(row['id'])
            missing, unexpected = expected_ids - ids, ids - expected_ids
            if missing: fail('REQUIREMENT_MISSING', ', '.join(sorted(missing)))
            if unexpected: fail('REQUIREMENT_UNEXPECTED', ', '.join(sorted(unexpected)))
        except (KeyError, ValueError, TypeError, OSError, UnicodeError) as e:
            fail('REQUIREMENT_MATRIX', e)
    elif final:
        fail('REQUIREMENT_MATRIX', 'Final audit requires a bound original-question matrix')
    else:
        warnings.append('No original-question matrix bound; returned output list completeness is unverified.')
    def review(rec, label):
        if not isinstance(rec, dict) or rec.get('status') != 'pass' or not rec.get('reviewer'):
            fail('REVIEW', label + ' is incomplete'); return
        try: bound(rec['evidence'])
        except (KeyError, ValueError, TypeError) as e: fail('REVIEW_EVIDENCE', label + ': ' + str(e))
    for name in ('semantic', 'figures', 'coverage', 'reproduction'):
        review(manifest.get('reviews', {}).get(name), name)
    if final:
        if manifest.get('mode') != 'live-contest': fail('FINAL_MODE', 'Final requires live-contest')
        if not rules or rules.get('event') != 'APMCM' or rules.get('event_year') != manifest.get('event_year'):
            fail('RULE_EVENT', 'Missing/mismatched current-year APMCM rules')
        if manifest.get('rules_sha256') != rules_hash(rules):
            fail('RULE_HASH', 'Rules profile is not bound to this manifest')
        for name in REQUIRED_RULES:
            r = (rules or {}).get('rules', {}).get(name, {})
            source_url = r.get('source_url')
            try:
                host = (urlparse(source_url).hostname or '') if isinstance(source_url, str) else ''
            except ValueError:
                host = ''
            official = any(host == d or host.endswith('.' + d) for d in ('apmcm.org', 'saikr.com', 'bsig.org.cn'))
            if r.get('status') != 'verified' or r.get('value') is None or r.get('event_year') != manifest.get('event_year') or not official:
                fail('RULE_UNRESOLVED', name)
            review(manifest.get('rule_checks', {}).get(name), 'rule:' + name)
    else:
        if manifest.get('mode') == 'live-contest': fail('FINAL_REQUIRED', 'Live work must use --final')
        warnings.append('Local rehearsal evidence only; no current submission clearance.')
    return {'status': 'pass' if not errors else 'fail', 'final': final,
            'scope': 'file/ledger checks; semantic and review records are declared evidence, not automated proof',
            'errors': errors, 'warnings': warnings, 'checked_files': checked,
            'claim_count': len(claims), 'requirement_count': len(outputs)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--rules', type=Path)
    p.add_argument('--final', action='store_true')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    try:
        result = audit(a.root, json.loads(a.manifest.read_text()), json.loads(a.rules.read_text()) if a.rules else None, a.final)
    except (ValueError, OSError, TypeError) as e:
        result = {'status': 'fail', 'errors': [{'code': 'INVALID_INPUT', 'detail': str(e)}]}
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if a.output: a.output.write_text(text + '\n')
    print(text)
    return 0 if result['status'] == 'pass' else 1

if __name__ == '__main__':
    raise SystemExit(main())
