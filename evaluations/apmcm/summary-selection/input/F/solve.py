import json
from pathlib import Path

def solve():
    data=json.loads(Path(__file__).with_name('data.json').read_text())
    out={}
    for scenario,rows in data.items():
        valid=[r for r in rows if r['served']/100>=0.9 and r['max_hours']<=6]
        chosen=min(valid,key=lambda r:r['cost_cny'])
        out[scenario]={'rows':rows,'feasible':[r['policy'] for r in valid],'chosen':chosen}
    out['base']['saving_vs_A']=(240-out['base']['chosen']['cost_cny'])/240
    out['scope']='Supplied synthetic tables, not controller or field validation'
    return out

if __name__=='__main__':print(json.dumps(solve(),indent=2))
