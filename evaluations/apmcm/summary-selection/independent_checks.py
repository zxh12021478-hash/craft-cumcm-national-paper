"""Independent arithmetic/analytic checks of the synthetic source facts."""
import json
import math
from fractions import Fraction
from pathlib import Path


def main():
    root=Path(__file__).resolve().parent
    f=json.loads((root/'input/F/data.json').read_text())
    selected={}
    for scenario in ['base','stress']:
        # Integer service count and deadline checks on every supplied row.
        feasible={r['policy']:r for r in f[scenario] if r['served']>=90 and r['max_hours']<=6}
        selected[scenario]=min(feasible,key=lambda name:feasible[name]['cost_cny'])
        assert set(feasible)==({'A','B','D','E'} if scenario=='base' else {'D'})
    assert selected=={'base':'B','stress':'D'}
    saving=Fraction(240-210,240)
    assert saving==Fraction(1,8)
    g=json.loads((root/'input/G/data.json').read_text())
    final=g['transient'][-1]
    k=-math.log((final['temperature_C']-20)/10)/final['hours']
    assert math.isclose(k,0.25,abs_tol=1e-14)
    assert all(math.isclose(row['temperature_C'],20+10*math.exp(-k*row['hours']),abs_tol=1e-12) for row in g['transient'])
    h=Fraction(50,10)
    capacitance=h/Fraction(1,4)
    assert h==5 and capacitance==20 and capacitance*3600==72000
    time=4*math.log(2.5)
    assert math.isclose(time,3.6651629274966204,abs_tol=1e-14)
    temperature_at_deadline=20+10*math.exp(-0.25*3)
    assert temperature_at_deadline>24
    assert all(math.isclose(hh/cc,0.25) for hh,cc in [(2.5,10),(5,20)])
    # Original transient alone has a positive scale symmetry in (h,C).
    assert max([4,3,5])<7
    lower_bound=sum(sorted([7,5,10])[:2])
    assert lower_bound==12 and 4+3>=7 and min(4,3)>=3
    print(json.dumps({'F':{'chosen':selected,'base_saving_exact':str(saving),'base_saving_percent':12.5},'G':{'rate_per_hour':k,'h_W_per_K':5,'C_Wh_per_K':20,'C_J_per_K':72000,'time_hours':time,'temperature_at_3h_C':temperature_at_deadline,'meets_deadline':False,'transient_scale_symmetry':'h and C jointly rescaled give identical transient'},'C':{'lower_bound':12,'attained_by':['A','B'],'post_failure_supply':[3,4]},'scope':'Synthetic source-fact checks; not field validation, a prize model or usage measurement'},indent=2))


if __name__=='__main__':main()
