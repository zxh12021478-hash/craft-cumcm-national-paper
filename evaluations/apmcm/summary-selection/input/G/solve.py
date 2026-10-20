import json
import math
from pathlib import Path

def solve():
    data=json.loads(Path(__file__).with_name('data.json').read_text())
    initial=data['initial_C'];ambient=data['ambient_C']
    positive=[r for r in data['transient'] if r['hours']>0]
    k=-sum(r['hours']*math.log((r['temperature_C']-ambient)/(initial-ambient)) for r in positive)/sum(r['hours']**2 for r in positive)
    h=data['steady_power_W']/data['steady_rise_K']
    capacitance=h/k
    time=math.log((initial-ambient)/(data['target_C']-ambient))/k
    return {'rate_per_hour':k,'transient_separately_identifies_h_C':False,'conductance_W_per_K':h,'capacitance_Wh_per_K':capacitance,'capacitance_J_per_K':capacitance*3600,'time_hours':time,'meets_3_hour_deadline':time<=3,'tangent_hours':(initial-data['target_C'])/(k*(initial-ambient)),'scope':'Exact synthetic model; no physical validation or measured uncertainty'}

if __name__=='__main__':print(json.dumps(solve(),indent=2))
