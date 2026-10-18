from fractions import Fraction as F
from pathlib import Path
import json
root = Path(__file__).resolve().parent
q1, q2 = F(2), F(3,10)
s1 = F(3)+F(1)+q1-F(3)
s2 = F(9,10)*s1+q2-F(3)
cost = q1+3*q2
assert 0 <= s1 <= 4 and 0 <= s2 <= 4 and 0 <= q1 <= 2 and 0 <= q2 <= 2
# For every feasible point q2 >= 21/10 - 9*q1/10, hence
# cost >= 63/10 - 17*q1/10 >= 29/10 when q1 <= 2.
lower_bound = F(63,10)-F(17,10)*2
assert cost == lower_bound
stress_supply = F(9,10)*(F(1)+F(1,20))+2
assert stress_supply < 3
r = json.loads((root/'input/results-B.json').read_text())
b = r['Q1']['baseline']; l = r['Q1']['L']
relative_cost = (F(b['cost'])-F(l['cost']))/F(b['cost'])
service_pp = (F(str(l['service_rate']))-F(str(b['service_rate'])))*100
assert relative_cost == F(12,100) and service_pp == 6
assert r['Q2']['L']['service_rate'] < r['service_floor'] <= r['Q2']['R']['service_rate']
result = {'A':{'q1_m3':str(q1),'q2_m3':str(q2),'S1_m3':str(s1),'S2_m3':str(s2),'cost_CNY':str(cost),'analytic_lower_bound_CNY':str(lower_bound),'stress_max_day2_supply_m3':str(stress_supply),'stress_shortfall_m3':str(3-stress_supply),'stress_feasible':False},'B':{'cost_reduction_percent':float(relative_cost*100),'service_gain_percentage_points':float(service_pp),'base_policy':'L','stress_feasible_policy':'R'}}
(root/'root-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
