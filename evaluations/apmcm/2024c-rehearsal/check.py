"""Independent arithmetic and isolated clean execution of the bounded rehearsal."""
from pathlib import Path
from decimal import Decimal
import json,math,subprocess,sys,tempfile,shutil,hashlib
from reference import calculate
P=Path(__file__).resolve().parent
A=P/'accepted'
def close(a,b):
    assert math.isclose(float(a),float(b),rel_tol=2e-12,abs_tol=1e-9),(a,b)
def main():
    provenance=json.loads((P/'provenance.json').read_text())
    r=json.loads((A/'results.json').read_text())
    ref=calculate()
    frozen_ref=json.loads((P/'root-reference.json').read_text())['series']
    strip_reason=lambda series:{k:{a:b for a,b in v.items() if a!='selection_reason'} for k,v in series.items()}
    canonical=json.dumps(strip_reason(r['series']),sort_keys=True,separators=(',',':')).encode()
    assert hashlib.sha256(canonical).hexdigest()==provenance['raw_forecast_series_canonical_sha256_ignoring_selection_reason']
    assert all(v['selection_reason']=='min two-origin MAE; no tie' for v in r['series'].values())
    maxgap=0;origin_count=0
    for name,s in r['series'].items():
        e=ref[name];assert s['selected_model']==e['selected']
        for model,value in s['origin_mae'].items():
            close(value,e['MAE'][model]);close(value,frozen_ref[name]['MAE'][model])
            for yr,v in s['all_model_final_forecasts'][model].items():
                close(v,e['all_candidate_forecasts'][model][int(yr)-2024])
        for i,yr in enumerate((2024,2025,2026)):
            gap=abs(s['final_forecasts'][str(yr)]-e['forecast_2024_2026'][i]);maxgap=max(maxgap,gap)
            close(s['final_forecasts'][str(yr)],e['forecast_2024_2026'][i])
        for row in s['validation_origins']:
            assert max(row['train_years'])<row['target_year']
            assert len(row['train_years']) in (3,4);origin_count+=1
            for model,pred in row['predictions'].items():
                target=next(x for x in e['validation'][model] if x['target']==row['target_year'])
                close(pred,target['forecast']);close(row['actual'],target['actual'])
    costs=0
    for row in r['q4_tariff']['rows']:
        t0=.1;t1=row['t1'];k=row['kappa'];eta=row['eta'];share=row['share']
        # Independently construct currency prices and actual volumes, then
        # normalize their revenues/profits, rather than compare formula strings.
        p0=7.;q0=13.;unitcost=5.6
        p1=p0*(1-k*(1-(1+t0)/(1+t1)))
        buyer0=p0*(1+t0);buyer1=p1*(1+t1)
        q1=q0*(buyer1/buyer0)**(-eta)
        affected_revenue=p1*q1/(p0*q0)
        profit=((1-share)*(p0-unitcost)*q0+share*(p1-unitcost)*q1)/(p0*q0)
        close(row['producer_price_mult'],p1/p0);close(row['buyer_price_mult'],buyer1/buyer0)
        close(row['quantity_mult'],q1/q0);close(row['total_revenue_mult'],1-share+share*affected_revenue)
        close(row['profit_per_R0'],profit)
        for restored,cost in row['max_mitigation_cost_100m_USD'].items():
            benefit=max(0,float(restored)*39.6*((p0-unitcost)/p0-profit))
            close(cost,benefit);costs+=1
        if k==1:close(q1/q0,1);close(buyer1/buyer0,1)
        if eta==1:close(affected_revenue,(1+t0)/(1+t1))
    assert len(r['q4_tariff']['rows'])==81
    boundref=json.loads((P/'decision-check-results.json').read_text())['three_market_food_ratio_bounds']
    for actual,expected in zip(r['q2_three_market']['fixed_intensity_food_bounds']['rows'],boundref):
        close(actual['minimum_ratio'],expected['minimum_ratio']);close(actual['maximum_ratio'],expected['maximum_ratio'])
        assert actual['minimum_ratio']<1<actual['maximum_ratio']
    for row in r['post_review_global_scenarios']['rows']:
        h=row['year']-2023;g=Decimal(str(row['annual_growth_scenario']))
        production=Decimal('34.96')*(1+g)**h
        close(row['production_million_tonnes'],production)
        close(row['consumption_million_tonnes'],production*Decimal('.98'))
    # The original pass-through counterexample remains an error after repair.
    failure=json.loads((P/'raw-failure.json').read_text())
    old=failure['raw_absorption_example']
    implied=(old['producer_price_mult']*(1+old['t1'])/1.1)**(-old['eta'])
    assert abs(old['quantity_mult']-implied)>.1
    with tempfile.TemporaryDirectory(prefix='apmcm2024c-clean-') as td:
        case=Path(td);(case/'input').mkdir();out=case/'output/v2';out.mkdir(parents=True)
        for name in ['data.json','source-facts.json']:shutil.copy2(P/'input'/name,case/'input'/name)
        for name in ['solve.py','add_global_anchor.py','global-source.json']:shutil.copy2(A/name,out/name)
        runs=[]
        for script in ['solve.py','add_global_anchor.py']:
            cp=subprocess.run([sys.executable,str(out/script)],check=True,capture_output=True,text=True,timeout=15)
            runs.append({'script':script,'exit_code':cp.returncode})
        actual=json.loads((out/'results.json').read_text());assert actual==r
        assert (out/'forecast-origin-ledger.json').read_bytes()==(A/'forecast-origin-ledger.json').read_bytes()
    report={'status':'pass-with-stated-limitations','series':10,'chronological_origin_rows':origin_count,'max_forecast_difference':maxgap,'policy_rows_independently_recomputed':81,'restoration_cost_values':costs,'demand_bound_years':3,'global_conditional_rows':6,'clean_execution':runs,'clean_results_equal':True,'raw_policy_failure_retained':True,'holdout_predictions_independently_recomputed':60,'candidate_forecasts_independently_recomputed':90,'scope':'Arithmetic, temporal index and declared economic-model checks only. Pet data release times, global demand dynamics, tariff elasticities, mitigation feasibility and award quality remain unverified.'}
    (P/'check-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
