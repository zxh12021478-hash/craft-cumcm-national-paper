"""Independent comparisons for the new bridge and decision formulas only."""
from pathlib import Path
import json
import math
import random
from itertools import product

P=Path(__file__).resolve().parent


def main():
    r=json.loads((P/'linked-results.json').read_text())
    base=json.loads((P/'base-results.json').read_text())
    price_gap=0
    for row in r['analytic_price_decisions']:
        p0,q0=7,13
        g=(1+row['t1'])/(1+row['t0'])
        c=row['unit_cost_fraction']*p0
        best=-math.inf
        for i in range(10001):
            p1=p0*(1-(i/10000)*(1-1/g))
            volume=q0*(p1*(1+row['t1'])/(p0*(1+row['t0'])))**(-row['eta'])
            best=max(best,(p1-c)*volume/(p0*q0))
        actual=row['profit_per_exposed_baseline_revenue']
        assert actual>=best-1e-12
        price_gap=max(price_gap,actual-best)
    # Check the same before-uncertainty action across uncertain cost/elasticity;
    # negative-margin prices are outside this robust model's feasible domain.
    robust=r['robust_price_decision'];g=1.5/1.1
    def worst(mp):return min((mp-a)*(mp*g)**(-eta) for a in (.2,.8) for eta in (.5,6))
    expected=worst(robust['producer_price_multiplier'])
    grid=max(worst(.8+.2*i/10000) for i in range(10001))
    assert expected>=grid-1e-12
    max_d_gap=0
    for row in r['capacity_cost_decisions']:
        def gain(d):return row['exposed_share']*(row['replacement_margin']-row['old_margin'])*d-row['quadratic_cost']*d*d-(row['fixed_cost'] if d>0 else 0)
        best=max(gain(row['capacity_assumed']*i/10000) for i in range(10001))
        actual=row['incremental_profit_per_baseline_revenue']
        assert actual>=best-1e-12;max_d_gap=max(max_d_gap,actual-best)
        assert 0<=row['move_fraction']<=row['capacity_assumed']
    # Actual money reconstruction, not reusing the normalized output formula.
    rng=random.Random(20261031);inside=0;annual_cases=0;corner_cases=0
    for b in r['bridge_bounds']:
        yr=b['year'];h=yr-2023
        cat=base['series']['China_cat']['final_forecasts'][str(yr)]
        dog=base['series']['China_dog']['final_forecasts'][str(yr)]
        corner=list(product([0,.05],[-.02,.02],[-.02,.02],[.25,2],[-.02,.02],[.95,1.05],[.5,1]))
        interior=[tuple(rng.uniform(lo,hi) for lo,hi in [(0,.05),(-.02,.02),(-.02,.02),(.25,2),(-.02,.02),(.95,1.05),(.5,1)]) for _ in range(80)]
        endpoint_values={}
        for index,(growth,share,price,intensity,domprice,fx,valuation) in enumerate(corner+interior):
            global_tonnes_0=34.96e6*.98
            global_tonnes_h=global_tonnes_0*(1+growth)**h
            # Arbitrary baseline price only constructs an equivalent accounting
            # example; not an empirical export price estimate.
            export_price0=3000
            export_qty0=39.6e8/export_price0
            market_share0=export_qty0/global_tonnes_0
            export_qtyh=global_tonnes_h*market_share0*(1+share)**h
            exports=export_qtyh*export_price0*(1+price)**h
            exports_factory0=valuation*39.6e8*7.0467
            domestic_factory0=2793e8-exports_factory0
            domgrowth=(intensity*cat+dog)/(intensity*6980+5175)
            production=domestic_factory0*domgrowth*(1+domprice)**h+valuation*exports*7.0467*fx
            for metric,v in [('exports_100m_USD',exports/1e8),('production_100m_CNY',production/1e8)]:
                assert b[metric]['minimum'][metric]-1e-9<=v<=b[metric]['maximum'][metric]+1e-9
            # Actual exposed quantities and costs, then conversion to factory
            # value; neither the normalized annual result nor its formula used.
            exposed_baseline_revenue=exports*.5
            exposed_after_revenue=exposed_baseline_revenue*(1.1/1.5)
            annual_exports=exports*.5+exposed_after_revenue
            annual_profit=.2*exports*.5+.2*exposed_after_revenue
            inventory_factory=(exports-annual_exports)*7.0467*fx*valuation
            gain=exports*(.5*(.2-.2*(1.1/1.5))*.25-.02*.25**2-.005)
            annual={
                'exports_after_tariff_100m_USD':annual_exports/1e8,
                'sales_adjusted_factory_value_100m_CNY':(production-inventory_factory)/1e8,
                'fixed_factory_value_100m_CNY':production/1e8,
                'fixed_output_extra_inventory_value_100m_CNY':inventory_factory/1e8,
                'operating_profit_after_tariff_100m_USD':annual_profit/1e8,
                'operating_profit_after_move_100m_USD':(annual_profit+gain)/1e8}
            annual_row=next(v for v in r['annual_policy']['rows'] if v['year']==yr)
            for metric,v in annual.items():
                envelope=annual_row['componentwise_envelopes'][metric]
                assert envelope['minimum']-1e-9<=v<=envelope['maximum']+1e-9
                if index<len(corner):endpoint_values.setdefault(metric,[]).append(v)
            if index<len(corner):corner_cases+=1
            else:inside+=1
            annual_cases+=1
        for metric,values in endpoint_values.items():
            envelope=annual_row['componentwise_envelopes'][metric]
            assert math.isclose(min(values),envelope['minimum'],rel_tol=1e-12,abs_tol=1e-8)
            assert math.isclose(max(values),envelope['maximum'],rel_tol=1e-12,abs_tol=1e-8)
    out={'status':'pass within declared conditional models','analytic_price_cases':27,'independent_price_grid_points_per_case':10001,'maximum_analytic_advantage_over_grid':price_gap,'robust_before_uncertainty_price':robust['producer_price_multiplier'],'robust_worst_profit':expected,'capacity_fixed_cost_cases':len(r['capacity_cost_decisions']),'maximum_diversification_advantage_over_grid':max_d_gap,'independent_continuous_interior_bridge_cases':inside,'independent_endpoint_bridge_cases':corner_cases,'annual_policy_fields_per_year':6,'annual_policy_years':3,'independent_annual_accounting_cases':annual_cases,'annual_envelope_extrema_independently_recomputed':True,'limits':'Grid comparisons support analytic derivation; scenario domain/valuation/realism not empirically validated. Prices and tax rates illustrative, not law.'}
    (P/'check-linked-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))


if __name__=='__main__':main()
