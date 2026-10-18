"""Independent elementary checks, not a solver or performance evaluator."""
import json
from pathlib import Path
r=Path(__file__).resolve().parent
eta=.9
max_first_charge=min(2,5-4)
max_stored=eta*max_first_charge
max_hour2_discharge=eta*max_stored
shortfall=7-(5+max_hour2_discharge)
assert abs(shortfall-1.19)<1e-12
A,B,C,D=(8,70,6),(10,80,7),(12,85,5),(11,75,8)
def dominates(a,b):
 return a[0]<=b[0] and a[1]>=b[1] and a[2]<=b[2] and a!=b
assert dominates(B,D)
assert not dominates((B[0]*1.05,B[1]*.95,B[2]*1.05),
                     (D[0]*.95,D[1]*1.05,D[2]*.95))
correct_energy=[.9,.9-2/.9,.9-2/.9]
reported_energy=[.9,.9-2*.9,.9-2*.9]
report={'O':{'solar_worst':0,'max_charge_hour1':max_first_charge,
 'max_storage_after_hour1':max_stored,'max_discharge_hour2':max_hour2_discharge,
 'max_supply_hour2':5+max_hour2_discharge,'infeasibility_shortfall_kWh':shortfall},
 'R':{'nominal_B_dominates_D':True,'nominal_dominance_not_guaranteed_under_joint_5pct':True},
 'audit':{'energy_improvement_fraction':(100-95)/100,'cost_improvement_fraction':(100-80)/100,
 'comfort_proxy_improvement_fraction':(.5-.4)/.5,'correct_battery_energy_states':correct_energy,
 'draft_battery_states':reported_energy},
 'alert':{'probability_threshold_if_binary_false_alarm_loss_model':1/(1+5)},
 'scope':'Elementary arithmetic and specified counterexamples; not an empirical forecast benchmark or contest evaluation'}
(r/'oracle-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
