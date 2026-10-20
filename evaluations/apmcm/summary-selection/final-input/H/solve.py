import json
from fractions import Fraction

if __name__=='__main__':
    w=Fraction(2,5)
    rows={'X':(9,3),'Y':(6,8),'Z':(5,2)}
    scores={n:w*a+(1-w)*b for n,(a,b) in rows.items()}
    assert max(scores,key=scores.get)=='Y'
    assert sorted({x-y for x in [8,10] for y in [5,7]})==[1,3,5]
    # Score difference is w(d+5)-5. Robust conditions use its two endpoints.
    print(json.dumps({'fixed_weight':str(w),'scores':{n:str(v) for n,v in scores.items()},'winner':'Y','nominal_tie_weight':str(Fraction(5,8)),'robust_Y_no_worse_max_weight':str(Fraction(5,10)),'robust_X_no_worse_min_weight':str(Fraction(5,6)),'middle_region':'depends on actual criterion values','boundary_ties_possible':True,'Z_dominated':True,'scope':'Exact interval inequalities, not probabilities'},indent=2))
