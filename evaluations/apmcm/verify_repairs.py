#!/usr/bin/env python3
"""Independent development checks; requires numpy, runtime skill does not."""
import ast
import csv
from fractions import Fraction as F
import json
from pathlib import Path
import re
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'skills/craft-apmcm-paper/scripts'))
import check_information

# Read raw input; use numpy least squares rather than the executor's hand-built
# normal-equation elimination. Preserve the same declared fitting problem.
with (ROOT/'inputs/demand.csv').open() as stream:
    rows=list(csv.DictReader(stream))
y=np.array([float(r['demand_units']) for r in rows])
promo=np.array([float(r['planned_promotion']) for r in rows])
t=np.arange(1,len(y)+1,dtype=float)
errs={model:{h:[] for h in range(1,5)} for model in ('single','piecewise')}
for origin in range(60,77):
    for h in range(1,5):
        known=(origin+h-2<=origin)
        for model in errs:
            possible=range(35,origin-4) if model=='piecewise' else [None]
            best=None
            for k in possible:
                cols=[np.ones(origin),t[:origin]]
                if k is not None:cols.append(np.maximum(0,t[:origin]-k))
                if known:cols.append(promo[:origin])
                X=np.column_stack(cols)
                b=np.linalg.lstsq(X,y[:origin],rcond=None)[0]
                loss=float(np.sum((X@b-y[:origin])**2))
                if best is None or loss<best[0]:best=(loss,k,b)
            _,k,b=best
            xx=[1,origin+h]
            if k is not None:xx.append(max(0,origin+h-k))
            if known:xx.append(promo[origin+h-1])
            errs[model][h].append(float(np.dot(b,xx)-y[origin+h-1]))
printed=(ROOT/'with-skill/repaired/probes/outputs/probe_F_v2.out').read_text()
current=None; comparisons=[]
for line in printed.splitlines():
    if line in ('-- single --','-- piecewise --'):current=line[3:-3]
    m=re.fullmatch(r'h=(\d) point: (\{.*\})',line)
    if m:
        h=int(m[1]);reported=ast.literal_eval(m[2]);e=np.array(errs[current][h])
        expected={'n':len(e),'MAE':round(float(np.mean(np.abs(e))),3),
                  'RMSE':round(float(np.sqrt(np.mean(e*e))),3),'bias':round(float(np.mean(e)),3)}
        assert reported==expected,(current,h,reported,expected)
        comparisons.append({'model':current,'horizon':h,**expected})
assert len(comparisons)==8
trace=json.loads((ROOT/'with-skill/repaired/information/information-trace.json').read_text())
information=check_information.audit(trace)
assert information['status']=='pass'

# Exact independent score/region crosscheck and a negative control to reject the
# false assertion that C>=D everywhere on the weight simplex.
Z={'A':(F(1),F(0),F(2,3)),'B':(F(1,2),F(2,3),F(1,3)),
   'C':(F(0),F(1),F(1)),'D':(F(1,4),F(1,3),F(0))}
checked=0
for i in range(101):
    for j in range(101-i):
        wc,we=F(i,100),F(j,100);wb=1-wc-we
        scores={k:wc*z[0]+wb*z[1]+we*z[2] for k,z in Z.items()}
        actual={k for k,v in scores.items() if v==max(scores.values())}
        region=set()
        if 7*wc+6*we>=4 and 6*wc+2*we>=3:region.add('A')
        if 7*wc+6*we<=4 and 5*wc-2*we>=2:region.add('B')
        if 6*wc+2*we<=3 and 5*wc-2*we<=2:region.add('C')
        assert region==actual,(wc,we,region,actual)
        checked+=1
assert Z['C'][0]<Z['D'][0]  # pure cost preference is a counterexample

# Exact independently computed power balance under the explicitly changed
# assumption solar>=1.19; check endpoints and interior without solver state.
eta=F(9,10)
assert sum((4,7,5))>3*5 and eta**2<1  # s=0; empty initial/final storage
assert F(5)+eta**2*(5-4)<7  # independent hourly infeasibility bound
def feasible(g,c,d,u,solar,cap):
    E=F(0)
    for n,L in enumerate((4,7,5)):
        assert g[n]+u[n]+d[n]==L+c[n]
        assert 0<=g[n]<=cap and 0<=u[n]<=solar[n]
        assert 0<=c[n]<=2 and 0<=d[n]<=2 and c[n]*d[n]==0
        E+=eta*c[n]-d[n]/eta
        assert 0<=E<=3
    assert E==0
for sv in (F(119,100),F(2),F(4)):
    feasible([5,5,5],[1,0,0],[0,F(81,100),0],[0,F(119,100),0],[0,sv,0],5)
c1=F(100,81)
feasible([4+c1,6,5],[c1,0,0],[0,1,0],[0,0,0],[0,0,0],6)
# Exact boundary from the revised audit, distinct from rounded display.
feasible([F(1024,181),F(1024,181),5],[F(300,181),0,0],
         [0,F(243,181),0],[0,0,0],[0,0,0],F(1024,181))
report={'status':'pass-targeted-repair-checks','forecast_numpy_crosscheck':comparisons,
 'information_audit':{'status':information['status'],'checked_feature_uses':information['checked_feature_uses'],
                      'errors':len(information['errors'])},
 'ranking_exact_grid_points':checked,'ranking_false_global_dominance_rejected':True,
 'dispatch_exact_relaxed_examples_checked':5,'original_dispatch_still_infeasible':True,
 'scope':'Independent numerical checks of feedback-informed repairs, not blinded performance, future forecast accuracy, actual Modex output, quota savings or prize certification.'}
(ROOT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
