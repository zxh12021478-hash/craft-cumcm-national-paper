#!/usr/bin/env python3
"""Independent lower-bound argument, not the supplied enumeration code."""
import json
from pathlib import Path

root=Path(__file__).resolve().parent
capacity={'A':4,'B':3,'C':5}
cost={'A':7,'B':5,'C':10}
normal_required=7
post_failure_required=3
assert max(capacity.values()) < normal_required
# At least two positive-cost modules are necessary. The cheapest two give a
# valid lower bound regardless of the contingency constraints.
lower_bound=sum(sorted(cost.values())[:2])
chosen=['A','B']
chosen_cost=sum(cost[n] for n in chosen)
total=sum(capacity[n] for n in chosen)
residual={n:total-capacity[n] for n in chosen}
assert total>=normal_required
assert all(v>=post_failure_required for v in residual.values())
assert chosen_cost==lower_bound==12
given=json.loads((root/'input/case-C/results.json').read_text())
assert len(given['candidates'])==8
assert len(given['optimal_designs'])==1
assert given['optimal_designs'][0]['installed']==chosen
assert given['optimal_designs'][0]['single_failure_supply']==residual
print(json.dumps({'lower_bound_cny':lower_bound,'attaining_design':chosen,'cost_cny':chosen_cost,'normal_supply':total,'single_failure_supply':residual,'proof':'One module supplies at most 5 < 7, so at least two are necessary; their cost is at least 5+7=12. A+B attains this bound and passes both specified outages. All other pairs have greater cost and costs are positive, so the optimum is unique.','scope':'Exact specified mathematical model, not physical capacity validation or future reliability.'},indent=2))
