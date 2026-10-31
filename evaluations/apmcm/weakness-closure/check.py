"""Run the development evidence checks; incomplete case must stay rejected."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import sys

P=Path(__file__).resolve().parent
REPO=P.parents[2]


def main():
    runs=[]
    for script in ['empirical/check.py','case/linked/check-linked.py','case/reproduce.py']:
        cp=subprocess.run([sys.executable,str(P/script)],check=True,capture_output=True,text=True,timeout=30)
        runs.append({'script':script,'exit_code':cp.returncode})
    spec=importlib.util.spec_from_file_location('apmcm_audit',REPO/'skills/craft-apmcm-paper/scripts/audit_bundle.py')
    auditor=importlib.util.module_from_spec(spec);spec.loader.exec_module(auditor)
    # The receiver was allowed grouping commas. Normalize manuscript, quote and
    # token together; stripping only the token created four false mismatches.
    normalize=lambda text:re.sub(r'\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b',lambda m:m[0].replace(',',''),text)
    (P/'raw-paper-normalized.md').write_text(normalize((P/'raw-paper-v2.md').read_text()))
    received=json.loads((P/'raw-claim-map-v2.json').read_text())['claims']
    raw_manifest={'event':'APMCM','mode':'historical-rehearsal','paper':'raw-paper-normalized.md',
                  'results':'case/results.json','files':[{'path':f,'sha256':hashlib.sha256((P/f).read_bytes()).hexdigest()}
                  for f in ['raw-paper-normalized.md','case/results.json']],
                  'claims':[{'id':c['id'],'quote':normalize(c['paper_quote']),'token':normalize(c['numeric_token']),
                             'pointer':c['json_pointer'],'scale':c['scale'],'absolute_tolerance':c['absolute_tolerance'],
                             'unit':c['unit']} for c in received]}
    raw_audit=auditor.audit(P,raw_manifest)
    raw_claim_errors=[e for e in raw_audit['errors'] if e['code']=='CLAIM']
    assert len(raw_claim_errors)==12,raw_claim_errors
    case=P/'case'
    files=[f for f in case.rglob('*') if f.is_file() and '__pycache__' not in f.parts
           and f.suffix not in ('.pyc',) and f.name not in ['bundle.json','audit.json']]
    outputs=[{'id':q,'status':'verified' if q=='Q1' else 'unverified',
              'evidence':['results.json','paper.md','reviews/semantic.json'],
              'review_note':('Frozen simple forecasts reproduced; causal drivers not claimed' if q=='Q1'
                             else 'Conditional answer present, but global-consumption/valuation or real policy calibration remains missing; internal evidence readiness not passed')}
             for q in ['Q1','Q2','Q3','Q4']]
    manifest={'event':'APMCM','event_year':2024,'mode':'historical-rehearsal',
              'paper':'paper.md','results':'results.json','requirement_matrix':'requirements.json',
              'files':[{'path':str(f.relative_to(case)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(files)],
              'claims':json.loads((case/'claims.json').read_text()),'required_outputs':outputs,
              'reviews':{k:{'status':'pass','reviewer':'AI review / explicit limited scope',
                            'evidence':v} for k,v in {'semantic':'reviews/semantic.json','coverage':'reviews/semantic.json',
                                                     'figures':'reviews/pdf-check.json','reproduction':'reviews/reproduction.json'}.items()}}
    audit=auditor.audit(case,manifest)
    claim_errors=[e for e in audit['errors'] if e['code']=='CLAIM']
    assert not claim_errors,claim_errors
    assert audit['status']=='fail'
    assert len([e for e in audit['errors'] if e['code']=='OUTPUT'])==3,audit['errors']
    assert all(e['code']=='OUTPUT' for e in audit['errors']),audit['errors']
    (case/'bundle.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (case/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    report={'check_status':'pass','meaning':'Declared computations reproduce and the incomplete case is correctly rejected, not submission readiness',
            'runs':runs,'mapped_scalar_summary_claims':len(manifest['claims']),
            'numeric_claim_errors':0,'full_content_gate':audit['status'],
            'received_map_errors_after_correct_grouping_normalization':len(raw_claim_errors),
            'unverified_original_outputs':['Q2','Q3','Q4'],
            'boundary':'Internal evidence gate, not an organizer disqualification decision; no current2026AI/template clearance or actual Modex test'}
    (P/'check-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
