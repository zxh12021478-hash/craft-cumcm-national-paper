#!/usr/bin/env python3
"""Recompute the supplied fixtures; no claim of implementation validation."""
import csv
import json
from fractions import Fraction
from pathlib import Path


def rows(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def number(value):
    return Fraction(value)


def encoded(value):
    if isinstance(value, Fraction):
        return {'exact': str(value), 'decimal': float(value)}
    raise TypeError(type(value).__name__)


def main():
    root = Path(__file__).resolve().parent
    a = rows(root / 'input/case-A/runs.csv')
    by_key = {(r['scenario'], r['policy']): r for r in a}
    assert len(a) == len(by_key) == 60
    scenarios = sorted({r['scenario'] for r in a})
    assert len(scenarios) == 20
    policies = {}
    for policy in ['B', 'T', 'TM']:
        selected = [by_key[s, policy] for s in scenarios]
        valid = [r for r in selected if all(r[k] == '1' for k in ['complete', 'hard_feasible', 'cost_complete'])]
        policies[policy] = {
            'scenarios': len(selected), 'valid': len(valid),
            'valid_fraction': Fraction(len(valid), len(selected)),
            'complete_valid_cost_sum_cny': sum(number(r['cost_cny']) for r in valid),
            'all_scenario_cost_available': len(valid) == len(selected),
        }
    common = [s for s in scenarios if all(by_key[s,p][k] == '1' for p in ['B','T','TM'] for k in ['complete','hard_feasible','cost_complete'])]
    common_cost = {p: sum(number(by_key[s,p]['cost_cny']) for s in common) for p in ['B','T','TM']}
    quiet = [s for s in scenarios if by_key[s,'B']['group'] == 'quiet']
    quiet_cost = {p: sum(number(by_key[s,p]['cost_cny']) for s in quiet) for p in ['B','TM']}
    result_a = {
        'policy_metrics': policies,
        'common_complete_scenarios': common,
        'common_complete_costs_cny': common_cost,
        'TM_cost_increase_vs_B_on_common_complete': (common_cost['TM']-common_cost['B'])/common_cost['B'],
        'TM_cost_increase_vs_T_on_common_complete': (common_cost['TM']-common_cost['T'])/common_cost['T'],
        'quiet_only_saving_vs_B': (quiet_cost['B']-quiet_cost['TM'])/quiet_cost['B'],
        'T_all_scenario_saving_vs_B': (policies['B']['complete_valid_cost_sum_cny']-policies['T']['complete_valid_cost_sum_cny'])/policies['B']['complete_valid_cost_sum_cny'],
        'retained_candidate': 'T on the supplied 20 scenarios, subject to absent implementation verification',
        'limits': ['no independent evaluation set', 'unequal tuning budgets', 'missing M-only variant and tuning scores', 'failed-run partial costs cannot establish total policy cost', 'scenario fractions are not deployment probabilities'],
    }
    assert common_cost == {'B':1600,'T':1520,'TM':1680}
    assert result_a['TM_cost_increase_vs_B_on_common_complete'] == Fraction(1,20)
    assert result_a['TM_cost_increase_vs_T_on_common_complete'] == Fraction(2,19)
    assert policies['TM']['valid_fraction'] == Fraction(4,5)
    assert not policies['TM']['all_scenario_cost_available']
    assert result_a['quiet_only_saving_vs_B'] == Fraction(1,5)
    b = rows(root / 'input/case-B/runs.csv')
    pairs = {(r['day'],r['policy']):r for r in b}
    days = sorted({r['day'] for r in b})
    assert len(b) == len(pairs) == 24 and len(days) == 12
    totals = {}
    for p in ['P','R']:
        selected = [pairs[d,p] for d in days]
        assert all(r[k] == '1' for r in selected for k in ['complete','hard_feasible','cost_complete'])
        assert all(number(r['served'])/number(r['requests']) >= Fraction(9,10) for r in selected)
        totals[p] = {'cost_cny':sum(number(r['cost_cny']) for r in selected),
                     'service':sum(number(r['served']) for r in selected)/sum(number(r['requests']) for r in selected)}
    result_b = {'units': '12 paired synthetic days, not 12000 independent requests',
                'totals':totals,
                'relative_cost_reduction':(totals['P']['cost_cny']-totals['R']['cost_cny'])/totals['P']['cost_cny'],
                'service_gain_percentage_points':100*(totals['R']['service']-totals['P']['service']),
                'lower_cost_days':sum(number(pairs[d,'R']['cost_cny']) < number(pairs[d,'P']['cost_cny']) for d in days),
                'retained_candidate':'R for these held-out synthetic days',
                'limits':['source code unavailable', 'no field validation', 'no universal or probabilistic claim']}
    assert result_b['relative_cost_reduction'] == Fraction(1,20)
    assert result_b['service_gain_percentage_points'] == 2
    report = {'A':result_a,'B':result_b,'scope':'Exact arithmetic from supplied synthetic tables. Does not verify absent controllers, provenance of claimed execution logs, future performance or prizes.'}
    print(json.dumps(report,ensure_ascii=False,indent=2,default=encoded))


if __name__ == '__main__':
    main()
