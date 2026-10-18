#!/usr/bin/env python3
"""Check a declared forecast feature-use trace against release-time lags.

Time is a numeric index in a single declared unit (e.g. week). This validates
records, not their fidelity to code or source metadata. Scenarios are explicitly
assumed inputs, never observed future values.
"""
import argparse
import json
import math
from pathlib import Path


def _time(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Time indices and release lags must be finite numbers')
    return value


def audit(record):
    errors, assumptions, checked = [], [], 0
    try:
        if not isinstance(record, dict): raise ValueError('Trace must be an object')
        lags, forecasts = record.get('availability_lags'), record.get('forecasts')
        if not isinstance(lags, dict) or not lags: raise ValueError('Declare release lags')
        for name, lag in lags.items():
            if not isinstance(name, str) or not name.strip(): raise ValueError('Invalid feature name')
            _time(lag)
        if not isinstance(forecasts, list) or not forecasts: raise ValueError('Declare forecasts')
        seen = set()
        for row in forecasts:
            if not isinstance(row, dict): raise ValueError('Forecast row must be an object')
            ident = row.get('id')
            if not isinstance(ident, str) or not ident.strip() or ident in seen:
                raise ValueError('Forecast IDs must be nonempty and unique')
            seen.add(ident)
            origin, target = _time(row.get('origin')), _time(row.get('target'))
            if target <= origin: raise ValueError('Target must follow forecast origin')
            uses = row.get('features')
            if not isinstance(uses, list): raise ValueError('Declare actual feature uses, even if empty')
            for feature in uses:
                if not isinstance(feature, dict): raise ValueError('Feature use must be an object')
                name, kind = feature.get('name'), feature.get('kind')
                if name not in lags: raise ValueError('Missing release lag for feature: ' + str(name))
                source = _time(feature.get('source_time'))
                if kind == 'observed':
                    released = source + lags[name]
                    if released > origin:
                        errors.append({'code': 'FUTURE_INFORMATION', 'forecast': ident,
                            'feature': name, 'source_time': source,
                            'available_at': released, 'origin': origin})
                elif kind in ('scenario', 'forecast'):
                    if not isinstance(feature.get('note'), str) or not feature['note'].strip():
                        raise ValueError('Non-observed inputs require an explicit assumption/method')
                    formed = _time(feature.get('formed_at'))
                    if formed > origin:
                        errors.append({'code': 'POST_ORIGIN_INPUT', 'forecast': ident, 'feature': name})
                    assumptions.append({'forecast': ident, 'feature': name, 'kind': kind,
                                        'note': feature['note']})
                else:
                    raise ValueError('Unknown feature kind: ' + str(kind))
                checked += 1
    except (ValueError, TypeError) as exc:
        errors.append({'code': 'INVALID_INPUT', 'detail': str(exc)})
    return {'status': 'fail' if errors else 'pass', 'checked_feature_uses': checked,
            'errors': errors, 'non_observed_inputs': assumptions,
            'scope': 'Declared feature availability only; compare trace to actual code and source metadata. '
                     'A pass does not establish forecast accuracy or prove scenarios are true.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        report = audit(json.loads(args.trace.read_text()))
    except (ValueError, OSError) as exc:
        report = {'status': 'fail', 'errors': [{'code': 'INVALID_INPUT', 'detail': str(exc)}]}
    result = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output: args.output.write_text(result+'\n')
    print(result)
    return 0 if report['status']=='pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
