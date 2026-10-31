"""Conditional physical-to-value bridge and exact tariff decisions.

Development evidence only. Uses frozen 2024C forecasts without refitting.
Missing economic quantities remain declared scenario assumptions.
"""
from itertools import product
from pathlib import Path
import json

P = Path(__file__).resolve().parent


def price_optimum(t0, t1, eta, cost):
    if not (0 <= t0 <= t1 and eta >= 0 and 0 < cost < 1):
        raise ValueError('This example assumes a nonnegative tariff increase, eta>=0, and 0<cost<1')
    g = (1+t1)/(1+t0)
    lower = 1/g
    target = eta*cost/(eta-1) if eta > 1 else 1
    mp = min(1, max(lower, target))
    profit = (mp-cost)*(mp*g)**(-eta)
    return {'producer_price_multiplier':mp, 'absorption_fraction':
            (1-mp)/(1-lower) if g != 1 else 0,
            'buyer_price_multiplier':mp*g, 'profit_per_exposed_baseline_revenue':profit}


def diversification(exposed_share, old_margin, replacement_margin, capacity, quadratic_cost, fixed_cost):
    if not (0 <= exposed_share <= 1 and 0 <= capacity <= 1 and quadratic_cost > 0 and fixed_cost >= 0):
        raise ValueError('Require share/capacity in[0,1], positive quadratic cost and nonnegative fixed cost')
    # Capacity is the attainable fraction of baseline exposed business that can
    # move, at a replacement margin already including destination unit costs.
    advantage = exposed_share*(replacement_margin-old_margin)
    d = min(capacity,max(0,advantage/(2*quadratic_cost)))
    gain_before_fixed = advantage*d-quadratic_cost*d*d
    if d == 0 or gain_before_fixed <= fixed_cost:
        d = 0
    return {'move_fraction':d,'incremental_profit_per_baseline_revenue':
            advantage*d-quadratic_cost*d*d-(fixed_cost if d>0 else 0),
            'maximum_acceptable_fixed_cost':gain_before_fixed,
            'capacity_assumed':capacity}


def main():
    prior=json.loads((P/'base-results.json').read_text())
    base_cats,base_dogs=6980,5175
    baseline_production,baseline_exports,fx0=2793,39.6,7.0467
    bounds=[]
    annual_policy=[]
    for year in (2024,2025,2026):
        h=year-2023
        cat=prior['series']['China_cat']['final_forecasts'][str(year)]
        dog=prior['series']['China_dog']['final_forecasts'][str(year)]
        candidates=[]
        for growth,share_growth,export_price_growth,cat_intensity,dom_price_growth,fx_ratio,valuation in product(
                [0,.05],[-.02,.02],[-.02,.02],[.25,2],[-.02,.02],[.95,1.05],[.5,1]):
            # Under fixed loss/inventory fractions, consumption grows like
            # production; that assumption, not pet stocks, supplies world growth.
            global_ratio=(1+growth)**h
            export_ratio=global_ratio*(1+share_growth)**h*(1+export_price_growth)**h
            domestic_ratio=(cat_intensity*cat+dog)/(cat_intensity*base_cats+base_dogs)
            # valuation converts export-border USD to comparable factory value.
            # It is assumed, not an estimated export share or a known accounting identity.
            export_factory_share=valuation*fx0*baseline_exports/baseline_production
            production_ratio=((1-export_factory_share)*domestic_ratio*(1+dom_price_growth)**h
                              +export_factory_share*export_ratio*fx_ratio)
            candidates.append({'exports_100m_USD':baseline_exports*export_ratio,
                               'production_100m_CNY':baseline_production*production_ratio,
                               'global_consumption_ratio':global_ratio,
                               'assumptions':{'global_growth':growth,'share_growth':share_growth,
                                              'export_price_growth':export_price_growth,
                                              'cat_dog_food_intensity_ratio':cat_intensity,
                                              'domestic_price_growth':dom_price_growth,
                                              'FX_h_over_FX_2023':fx_ratio,'border_to_factory_valuation':valuation}})
        row={'year':year,'endpoint_scenarios':len(candidates)}
        for metric in ['exports_100m_USD','production_100m_CNY']:
            row[metric]={'minimum':min(candidates,key=lambda x:x[metric]),
                         'maximum':max(candidates,key=lambda x:x[metric])}
        bounds.append(row)
        # Partial-equilibrium annual policy illustration, not estimated law:
        # eta=1, a=.8, s=.5, t0=.1 -> t1=.5, optimal mp=1.
        # Separate sales-adjusted output from fixed output/inventory response.
        revenue_ratio=.5+.5*(1.1/1.5)
        profit_ratio=.5*.2+.5*.2*(1.1/1.5)
        move=diversification(.5,.2*(1.1/1.5),.2,.25,.02,.005)
        annual=[]
        for candidate in candidates:
            x=candidate['exports_100m_USD'];v=candidate['production_100m_CNY']
            assumptions=candidate['assumptions']
            unsold=(x*(1-revenue_ratio)*fx0*assumptions['FX_h_over_FX_2023']
                    *assumptions['border_to_factory_valuation'])
            annual.append({'exports_after_tariff_100m_USD':x*revenue_ratio,
                           'sales_adjusted_factory_value_100m_CNY':v-unsold,
                           'fixed_factory_value_100m_CNY':v,
                           'fixed_output_extra_inventory_value_100m_CNY':unsold,
                           'operating_profit_after_tariff_100m_USD':x*profit_ratio,
                           'operating_profit_after_move_100m_USD':x*(profit_ratio+move['incremental_profit_per_baseline_revenue'])})
        annual_policy.append({'year':year,'componentwise_envelopes':{
            metric:{'minimum':min(v[metric] for v in annual),'maximum':max(v[metric] for v in annual)}
            for metric in annual[0]}})
    pricing=[]
    for t1,eta,cost in product([.1,.25,.5],[.5,1,6],[.2,.5,.8]):
        pricing.append({'t0':.1,'t1':t1,'eta':eta,'unit_cost_fraction':cost,
                        **price_optimum(.1,t1,eta,cost)})
    # One before-uncertainty price decision with a non-loss-making-price
    # feasibility constraint. Margins are nonnegative; worst eta/cost at maxima.
    robust=price_optimum(.1,.5,6,.8)
    robust['tariff_assumed']={'t0':.1,'t1':.5}
    robust['assumed_domain']={'eta':[.5,6],'cost':[.2,.8],
                              'producer_price_minimum':max(1/(1.5/1.1),.8)}
    policy=[]
    old=price_optimum(.1,.5,1,.8)['profit_per_exposed_baseline_revenue']
    for margin,cap,fixed in product([.10,.20],[0,.25,.75],[0,.005]):
        policy.append({'exposed_share':.5,'old_margin':old,'replacement_margin':margin,
                       'quadratic_cost':.02,'fixed_cost':fixed,
                       **diversification(.5,old,margin,cap,.02,fixed)})
    result={'scope':'Conditional accounting/decision extension, not calibrated forecasts or actual tariff facts',
            'source_FX_2023':{'CNY_per_USD':fx0,'url':'https://www.stats.gov.cn/sj/zxfb/202402/t20240228_1947915.html'},
            'valuation_warning':'Factory production and border exports are not automatically comparable. Border-to-factory factor and fixed factor over horizon are assumed; no empirical export share inferred.',
            'growth_warning':'Global0/5%, market share/prices+-2%, intensity.25/2, FX.95/1.05, valuation.5/1 are declared scenario endpoints, not measured bounds or probabilities.',
            'bridge_bounds':bounds,'analytic_price_decisions':pricing,
            'annual_policy':{'assumptions':{'t0':.1,'t1':.5,'eta':1,'cost_fraction':.8,'exposed_share':.5,
                                            'producer_price_ratio':1,'replacement_margin':.2,
                                            'move_capacity':.25,'quadratic_cost':.02,'fixed_cost':.005},
                             'revenue_ratio':revenue_ratio,'profit_per_prepolicy_export_revenue':profit_ratio,
                             'move_incremental_profit_per_prepolicy_export_revenue':move['incremental_profit_per_baseline_revenue'],
                             'scope':'Componentwise scenario envelopes, not jointly attainable endpoint tuples, probabilities or forecasts. All costs scale with that year pre-policy export revenue; world demand is exogenous. Sales-adjusted output assumes no inventory buildup or domestic rerouting. Fixed-output mode records unsold factory-value inventory, not tonnes or a verified inventory policy. No post-relocation export receipts inferred from a profit margin alone.',
                             'rows':annual_policy},
            'robust_price_decision':robust,'capacity_cost_decisions':policy,
            'limits':['No observed global consumption growth, market shares or matched valuation factor calibration',
                      'No causal policy estimate; actual tariff coverage, destination replacement margin/capacity/cost unverified',
                      'Scenario ranges do not provide confidence intervals or known physical possibility bounds',
                      'Policy optima apply to stated constant-elasticity, constant-unit-cost model only']}
    (P/'linked-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'bridge_years':3,'scenario_endpoints_per_year':len(candidates),
                      'analytic_price_decisions':len(pricing),'capacity_cost_decisions':len(policy),
                      'robust_example':robust},indent=2))


if __name__=='__main__':main()
