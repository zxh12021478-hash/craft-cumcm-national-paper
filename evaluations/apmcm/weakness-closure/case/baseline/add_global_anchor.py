"""Add a versioned production-to-consumption scenario; no empirical growth fit."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent
r=json.loads((P/'results.json').read_text())
source=json.loads((P/'global-source.json').read_text())
rows=[]
for growth in [0.0,0.05]:
    for h in [1,2,3]:
        production=source['value']*(1+growth)**h
        rows.append({'year':2023+h,'annual_growth_scenario':growth,
                     'production_million_tonnes':production,
                     'consumption_million_tonnes':production*.98,
                     'loss_fraction_assumed':.02,'net_inventory_change_assumed':0})
r['post_review_global_scenarios']={'source':source,'rows':rows,
 'status':'Conditional absolute scenarios, not empirically validated global demand forecasts. Growth0/5%, loss2%, inventory0 are assumptions.',
 'phase':'Root source/accounting supplement after receiver v2; no change to existing pet forecasts or policy rows.'}
(P/'results.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
