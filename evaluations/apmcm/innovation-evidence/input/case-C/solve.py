#!/usr/bin/env python3
import itertools
import json


def solve():
    capacity = {'A':4, 'B':3, 'C':5}
    costs = {'A':7, 'B':5, 'C':10}
    rows=[]
    for flags in itertools.product([0,1], repeat=3):
        installed=[name for name,yes in zip(capacity,flags) if yes]
        total=sum(capacity[n] for n in installed)
        residual={n:total-capacity[n] for n in installed}
        valid=total>=7 and all(v>=3 for v in residual.values())
        rows.append({'installed':installed,'normal_supply':total,'single_failure_supply':residual,'cost_cny':sum(costs[n] for n in installed),'feasible':valid})
    feasible=[r for r in rows if r['feasible']]
    minimum=min(r['cost_cny'] for r in feasible)
    return {'candidates':rows,'optimal_designs':[r for r in feasible if r['cost_cny']==minimum], 'reference':['B','C'],'reference_cost_cny':15,'cost_reduction':(15-minimum)/15,'scope':'Complete finite specified model only'}


if __name__=='__main__':
    print(json.dumps(solve(),indent=2))
