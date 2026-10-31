"""Independent case checks: accounting, target-derived feature, game and demand bounds."""
from pathlib import Path
from decimal import Decimal, getcontext
import json, math
P=Path(__file__).resolve().parent
getcontext().prec=40

def main():
    fx=Decimal('6.8985');exports2019=Decimal('154.1')/fx
    corrected_drop=(Decimal('9.8')/exports2019-1)*100
    raw_drop=(Decimal('9.8')/Decimal('154.1')-1)*100
    # Analytic toy: an input defined from the contemporaneous target can give a
    # perfect fit and still cannot be computed at an unknown future target.
    toyY=[100,150,210,280];N=10
    E=[y/N for y in toyY];reconstructed=[N*e for e in E]
    assert reconstructed==toyY
    future_E={str(y):y/N for y in (300,600)}
    assert future_E['300']!=future_E['600']
    # Visible handbook eq31 vs an alternative that matches displayed payoffs.
    rows=[]
    for price in (50,45):
        share=1/(1+math.exp(1.5*(price-55)))
        for tariff in (.25,.30):
            rows.append({'price':price,'tariff':tariff,'share':share,
                         'literal_eq31_profit':(price-30-tariff)*share,
                         'alternative_advalorem_profit':(price*(1-tariff)-30)*share,
                         'US_visible_profit':(55-35)*(1-share)})
    assert all(rows[i]['US_visible_profit']==rows[i+1]['US_visible_profit'] for i in (0,2))
    nash={}
    for form in ['literal_eq31_profit','alternative_advalorem_profit']:
        eq=[]
        for row in rows:
            c_best=max(x[form] for x in rows if x['tariff']==row['tariff'])
            a_best=max(x['US_visible_profit'] for x in rows if x['price']==row['price'])
            if row[form]>=c_best-1e-12 and row['US_visible_profit']>=a_best-1e-12: eq.append([row['price'],row['tariff']])
        assert eq==[[50,.25],[50,.30]]
        nash[form]=eq
    ref=json.loads((P/'root-reference.json').read_text())['series']
    names=[n for n in ref if n.startswith(('America_','France_','Germany_'))]
    bounds=[]
    for h in range(3):
        ratios={n:ref[n]['forecast_2024_2026'][h]/ref[n]['observed'][-1] for n in names}
        lo,hi=min(ratios.values()),max(ratios.values())
        # Vertex weights attain bounds; one arbitrary positive interior point
        # independently verifies the ratio-of-weighted-quantities identity.
        a={n:i+1 for i,n in enumerate(names)}
        den=sum(a[n]*ref[n]['observed'][-1] for n in names)
        actual=sum(a[n]*ref[n]['forecast_2024_2026'][h] for n in names)/den
        assert lo<=actual<=hi
        assert all(lo<=v<=hi for v in ratios.values())
        bounds.append({'year':2024+h,'minimum_ratio':lo,'maximum_ratio':hi,'growth_sign_identified':lo>1 or hi<1,'ratios':ratios})
    out={'FX2019_exports_100mUSD':str(exports2019),'2019_to_2020_corrected_change_pct':str(corrected_drop),'mixed_currency_change_pct':str(raw_drop),
         'target_feature_toy':{'P':N,'Y':toyY,'E_equals_Y_over_P':E,'reconstructed_Y':reconstructed,'future_feature_depends_on_unknown_target':future_E,'scope':'Analytic counterexample, not reproduction of paper regression.'},
         'visible_case_game':{'rows':rows,'pure_equilibria':nash,'interpretation':'US payoff independent oftariff in visible formula, so no stricttariff preference is established. Alternativeformula is a reconstruction, not authorcode.'},
         'three_market_food_ratio_bounds':bounds,'bound_assumptions':'Fixed nonnegative per-pet coefficients within six observed market/species groups; pointstockforecasts treated as given. Ratio is convexcombination of groupstockratios. Not global or confidencebounds; rest-of-world and changingintensity unbounded here.',
         'source':'Official2024Cquestion and userhandbookcase physical262-263,265,270-272; case fullimplementation notavailable.'}
    (P/'decision-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
