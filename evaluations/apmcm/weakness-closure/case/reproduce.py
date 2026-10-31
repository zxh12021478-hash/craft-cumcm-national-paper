"""Clean stdlib-only reproduction; PDF building is a separate presentation step."""
from pathlib import Path
import json
import math
import shutil
import subprocess
import sys
import tempfile

P=Path(__file__).resolve().parent


def combine(base,linked,data):
    return {'base':base,'linked':linked,'input_data':data,
            'derived':{'cat_growth_pct':100*(6980/4412-1),
                       'dog_decline_pct':100*(1-5175/5503),
                       'cat_share_2019_pct':100*4412/(4412+5503),
                       'cat_share_2023_pct':100*6980/(6980+5175),
                       'overseas_growth_pct':{k:100*(v[-1]/v[0]-1) for k,v in data['pets'].items() if not k.startswith('China')}}}


def equal_numeric(a,b,path=''):
    if isinstance(a,bool) or isinstance(b,bool):assert a is b,path
    elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
        assert math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-8),(path,a,b)
    elif isinstance(a,dict):
        assert isinstance(b,dict) and a.keys()==b.keys(),path
        for key in a:equal_numeric(a[key],b[key],path+'/'+key)
    elif isinstance(a,list):
        assert isinstance(b,list) and len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):equal_numeric(x,y,path+'/'+str(i))
    else:assert a==b,(path,a,b)


def main():
    expected=json.loads((P/'results.json').read_text())
    runs=[]
    with tempfile.TemporaryDirectory(prefix='apmcm2024c-linked-') as td:
        work=Path(td)
        shutil.copytree(P/'input',work/'input');shutil.copytree(P/'baseline',work/'baseline')
        (work/'linked').mkdir();shutil.copy2(P/'linked/linked.py',work/'linked/linked.py')
        for script in ['baseline/solve.py','baseline/add_global_anchor.py']:
            cp=subprocess.run([sys.executable,str(work/script)],check=True,capture_output=True,timeout=20)
            runs.append({'script':script,'exit_code':cp.returncode})
        shutil.copy2(work/'baseline/results.json',work/'linked/base-results.json')
        cp=subprocess.run([sys.executable,str(work/'linked/linked.py')],check=True,capture_output=True,timeout=20)
        runs.append({'script':'linked/linked.py','exit_code':cp.returncode})
        actual=combine(json.loads((work/'baseline/results.json').read_text()),
                       json.loads((work/'linked/linked-results.json').read_text()),
                       json.loads((work/'input/data.json').read_text()))
        equal_numeric(actual,expected)
        ledger_equal=(work/'baseline/forecast-origin-ledger.json').read_bytes()==(P/'baseline/forecast-origin-ledger.json').read_bytes()
    report={'status':'pass','runs':runs,'all_result_fields_match_with_numeric_tolerance':True,
            'numeric_tolerance':{'relative':1e-11,'absolute':1e-8},
            'origin_ledger_byte_equal_in_this_interpreter':ledger_equal,
            'interpretation':'Computational reproduction only, not economic calibration, source authenticity or current-rule clearance',
            'python':sys.version.split()[0]}
    (P/'reviews/reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
