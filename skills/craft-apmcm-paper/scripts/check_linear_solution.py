#!/usr/bin/env python3
"""Independently recompute declared linear constraints and objective; no solver.

Original implementation. Method reference: yushui2022/MathModel-Skill,
modeling-tools.md (pinned source and selection notes in docs/github-learning-20261018.md).
A pass never establishes optimality, source-model fidelity or nonlinear feasibility.
"""
import argparse
import json
import math
from pathlib import Path


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected a finite numeric value (not a boolean)')
    return value


def vector(value, size=None):
    if not isinstance(value, list): raise ValueError('Expected a numeric array')
    if size is not None and len(value) != size: raise ValueError('Vector dimensions disagree')
    return [number(v) for v in value]


def audit(record):
    rows, errors = [], []
    result = {'status': 'fail', 'linear_feasible': False, 'optimality_verified': False,
        'scope': 'Declared linear constraints, explicit bounds, integrality and objective only; '
                 'not optimality, model fidelity, units, nonlinear or undeclared constraints.'}
    try:
        if not isinstance(record, dict): raise ValueError('Input must be an object')
        model, candidate = record.get('model'), record.get('candidate')
        if not isinstance(model, dict) or not isinstance(candidate, dict):
            raise ValueError('Declare model and candidate objects')
        if model.get('sense') not in ('min', 'max'): raise ValueError('Declare original objective sense')
        c = vector(model.get('c'))
        if not c: raise ValueError('At least one variable is required')
        x, n = vector(candidate.get('x'), len(c)), len(c)
        tol = record.get('tolerances', {})
        if not isinstance(tol, dict): raise ValueError('Tolerances must be an object')
        absolute = number(tol.get('absolute', 1e-7))
        relative = number(tol.get('relative', 1e-9))
        integer_tol = number(tol.get('integer', 1e-7))
        if min(absolute, relative, integer_tol) < 0: raise ValueError('Tolerances must be nonnegative')
        bounds = model.get('bounds')
        if not isinstance(bounds, list) or len(bounds) != n:
            raise ValueError('Every variable requires an explicit [lower, upper] bound pair')

        def check(label, lhs, rhs, equality=False, integer=False):
            number(lhs); number(rhs)
            limit = integer_tol if integer else absolute + relative * max(abs(lhs), abs(rhs))
            violation = abs(lhs-rhs) if equality else max(0.0, lhs-rhs)
            number(limit); number(violation)
            rows.append({'id': label, 'lhs': lhs, 'rhs': rhs, 'violation': violation,
                         'tolerance': limit, 'passed': violation <= limit})

        for matrix_key, rhs_key, equality in (('A_ub','b_ub',False),('A_eq','b_eq',True)):
            if matrix_key not in model and rhs_key not in model: continue
            matrix, rhs = model.get(matrix_key), model.get(rhs_key)
            if not isinstance(matrix, list): raise ValueError('Declare matrix with matching RHS: '+matrix_key)
            rhs = vector(rhs, len(matrix))
            for i, (row, target) in enumerate(zip(matrix, rhs)):
                coeff = vector(row, n)
                lhs = math.fsum(a*b for a,b in zip(coeff, x))
                check(f'{matrix_key}[{i}]', lhs, target, equality)
        for i, pair in enumerate(bounds):
            if not isinstance(pair, list) or len(pair) != 2: raise ValueError('Invalid bound pair')
            lower, upper = pair
            if lower is not None: number(lower)
            if upper is not None: number(upper)
            if lower is not None and upper is not None and lower > upper:
                raise ValueError('Lower bound exceeds upper bound')
            if lower is not None: check(f'lower[{i}]', lower, x[i])
            if upper is not None: check(f'upper[{i}]', x[i], upper)
        indices = model.get('integer_indices', [])
        if not isinstance(indices, list) or any(type(i) is not int or not 0 <= i < n for i in indices):
            raise ValueError('Invalid integer variable indices')
        if len(set(indices)) != len(indices): raise ValueError('Duplicate integer variable index')
        if indices and integer_tol >= 0.5:
            raise ValueError('Integer tolerance must be less than half an integer step')
        for i in indices: check(f'integer[{i}]', x[i], round(x[i]), True, True)
        feasible = all(r['passed'] for r in rows)
        offset = number(model.get('offset', 0))
        objective = number(math.fsum([offset, *(a*b for a,b in zip(c,x))]))
        if 'reported_objective' in candidate:
            check('objective', objective, number(candidate['reported_objective']), True)
        else:
            errors.append({'code': 'OBJECTIVE_UNREPORTED', 'detail': 'Cannot compare the reported objective'})
        failed = [r['id'] for r in rows if not r['passed']]
        if failed: errors.append({'code': 'CHECK_FAILED', 'detail': failed})
        result.update(linear_feasible=feasible, objective=objective, sense=model['sense'],
                      status='fail' if errors else 'pass')
    except (ValueError, TypeError, OverflowError) as exc:
        errors.append({'code': 'INVALID_INPUT', 'detail': str(exc)})
    result.update(checks=rows, errors=errors)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        report=audit(json.loads(args.input.read_text()))
    except (ValueError,OSError) as exc:
        report={'status':'fail','errors':[{'code':'INVALID_INPUT','detail':str(exc)}]}
    text=json.dumps(report,ensure_ascii=False,indent=2)
    if args.output: args.output.write_text(text+'\n')
    print(text)
    return 0 if report['status']=='pass' else 1

if __name__=='__main__':raise SystemExit(main())
