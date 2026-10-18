import json, math
from fractions import Fraction
from pathlib import Path
root = Path(__file__).resolve().parent
pts = [(0,0),(120,0),(120,80),(0,80)]
edges = list(zip(pts,pts[1:]+pts[:1]))
perimeter_px = sum(math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in edges)
area_px2 = abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in edges))/2
s = Fraction(10,200)
width_interval_calibration_only = [Fraction(120*10,202),Fraction(120*10,198)]
r = json.loads((root/'forward-input/results.json').read_text())
a = sum(r['Q1']['model'],[]); b = sum(r['Q1']['CFD'],[])
err = [x-y for x,y in zip(a,b)]
checks = {'A':{'perimeter_mm':perimeter_px*float(s),'area_mm2':area_px2*float(s*s), 'width_mm_interval_calibration_only':[float(x) for x in width_interval_calibration_only], 'nominal_width_mm':6,'max_width_deviation_from_calibration_alone':float(max(abs(x-6) for x in width_interval_calibration_only)), 'all_endpoint_errors_zero_is_allowed':True, 'supports_uniform_0_02_mm_bound':False}, 'B':{'range_overlap':max(0,min(max(a),max(b))-max(min(a),min(b)))/(max(max(a),max(b))-min(min(a),min(b))),'matched_point_MAE_degC':sum(abs(x) for x in err)/len(err),'matched_point_RMSE_degC':math.sqrt(sum(x*x for x in err)/len(err)),'max_abs_error_degC':max(abs(x) for x in err),'base_best':min(('H','J'),key=lambda x:r['Q2'][x]),'upper_endpoint_best':min(r['Q3']['upper_endpoint_scores'],key=r['Q3']['upper_endpoint_scores'].get),'confidence_interval_supported':False,'empirical_validation_supported':False}}
(root/'root-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
