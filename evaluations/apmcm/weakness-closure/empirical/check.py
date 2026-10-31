"""Independent derivative-root fit and empirical holdout evaluation."""
from pathlib import Path
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent


def profile(k, rows):
    f = [-math.expm1(-k * r['pressure']) for r in rows]
    a = math.fsum(v * r['volume'] for v, r in zip(f, rows)) / math.fsum(v*v for v in f)
    residual = [r['volume']-a*v for v, r in zip(f, rows)]
    derivative = -2*a*math.fsum(r['pressure']*math.exp(-k*r['pressure'])*e
                               for r, e in zip(rows, residual))
    return a, math.fsum(e*e for e in residual), derivative


def independent_fit(rows):
    grid = [10**(-7+6*i/600) for i in range(601)]
    candidates = [grid[0], grid[-1]]
    for lo, hi in zip(grid, grid[1:]):
        dlo = profile(lo, rows)[2]
        if dlo * profile(hi, rows)[2] > 0:
            continue
        for _ in range(70):
            mid = (lo+hi)/2
            if profile(mid, rows)[2] * dlo <= 0:
                hi = mid
            else:
                lo = mid
                dlo = profile(lo, rows)[2]
        candidates.append((lo+hi)/2)
    k = min(candidates, key=lambda z: profile(z, rows)[1])
    a, rss, derivative = profile(k, rows)
    return {'A': a, 'k': k, 'RSS': rss, 'profile_derivative': derivative,
            'bounded_stationary_candidates_including_endpoints': len(candidates)}


def main():
    inp = json.loads((P/'train.json').read_text())
    rows = inp['calibration_rows']
    held = json.loads((P/'holdout.json').read_text())['rows']
    raw = json.loads((P/'raw/results.json').read_text())
    fitted = independent_fit(rows)
    assert abs(fitted['RSS']-raw['saturating']['RSS']) < 1e-12
    maxgap = max(abs(fitted['A']*(-math.expm1(-fitted['k']*r['pressure']))-
                     r['saturating_volume']) for r in raw['frozen_predictions'])
    assert maxgap < 1e-6
    details = []
    metrics = {}
    for h, pred in zip(held, raw['frozen_predictions']):
        assert h['pressure'] == pred['pressure']
        details.append({**h, **pred,
                        'affine_error_prediction_minus_observation': pred['affine_volume']-h['volume'],
                        'saturating_error_prediction_minus_observation': pred['saturating_volume']-h['volume']})
    for model in ['affine', 'saturating']:
        errors = [r[model+'_error_prediction_minus_observation'] for r in details]
        metrics[model] = {'MAE': sum(map(abs, errors))/len(errors),
                          'RMSE': math.sqrt(sum(e*e for e in errors)/len(errors)),
                          'bias': sum(errors)/len(errors), 'max_abs_error': max(map(abs, errors))}
    # Local Jacobian conditioning is a diagnostic, not a measurement uncertainty
    # or proof that the asymptotic capacity is physically identified.
    a, k = fitted['A'], fitted['k']
    j1 = [-math.expm1(-k*r['pressure']) for r in rows]
    j2 = [a*r['pressure']*math.exp(-k*r['pressure']) for r in rows]
    corr = -math.fsum(u*v for u,v in zip(j1,j2))/math.sqrt(math.fsum(u*u for u in j1)*math.fsum(v*v for v in j2))
    with tempfile.TemporaryDirectory(prefix='apmcm-empirical-') as td:
        case = Path(td); (case/'output').mkdir()
        shutil.copy2(P/'train.json', case/'train.json')
        shutil.copy2(P/'raw/fit.py', case/'output/fit.py')
        subprocess.run([sys.executable,str(case/'output/fit.py')],check=True,capture_output=True,timeout=15)
        rerun=json.loads((case/'output/results.json').read_text())
        byte_equal=(case/'output/results.json').read_bytes()==(P/'raw/results.json').read_bytes()
        for actual,frozen in zip(rerun['frozen_predictions'],raw['frozen_predictions']):
            for key in ['affine_volume','saturating_volume']:assert math.isclose(actual[key],frozen[key],rel_tol=1e-9,abs_tol=1e-6)
        accepted=json.loads((P/'accepted/results.json').read_text())
        assert accepted['affine']==raw['affine'] and accepted['frozen_predictions']==raw['frozen_predictions']
        shutil.copy2(P/'accepted/fit.py',case/'output/fit.py')
        subprocess.run([sys.executable,str(case/'output/fit.py')],check=True,capture_output=True,timeout=15)
        repaired_run=json.loads((case/'output/results.json').read_text())
        for actual,frozen in zip(repaired_run['frozen_predictions'],accepted['frozen_predictions']):
            for key in ['affine_volume','saturating_volume']:assert math.isclose(actual[key],frozen[key],rel_tol=1e-9,abs_tol=1e-6)
        assert repaired_run['saturating']['optimization']['interior_solution']
        assert repaired_run['saturating']['optimization']['log_window_stopping_met']
    result = {'status':'reproduced and evaluated, physical generalization limited',
              'source':'NIST Misra1a observed adsorption data; source units unspecified',
              'calibration_rows':10,'withheld_response_rows':4,'holdout_type':'higher-pressure extrapolation, not chronological or new experiment',
              'producer_source_sha256':hashlib.sha256((P/'raw/fit.py').read_bytes()).hexdigest(),
              'independent_fit':fitted,'max_prediction_gap':maxgap,'clean_rerun_numerically_reproduced':True,'clean_rerun_byte_equal_in_this_interpreter':byte_equal,
              'holdout_metrics':metrics,'matched_observations':details,
              'local_parameter_correlation_under_unweighted_LS':corr,
              'retrospective_exposure':'Root saw complete benchmark/certificates while sourcing; receiver had 10 responses only by task scope. Known benchmark/same conversation, not blind.',
              'confirmed_issues':['Handoff invents a predeclared model-selection rule based on final holdout RSS; the frozen plan did not authorize post-test route selection.',
                                  'converged_interior flag tests only location, not convergence; independent derivative calculation supplies a separate check for this actual fit.',
                                  'Small training residuals and successful point extrapolation do not establish saturation capacity accuracy; parameter correlation and systematic heldout residuals remain.'],
              'effect_on_claims':'Retain frozen saturation predictions as evaluated descriptive candidate, not select/refit on final test; report both models and all signed errors. No measured device/HVAC or universal physical validity claim.'}
    (P/'check-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['matched_observations','confirmed_issues']},indent=2))


if __name__=='__main__':
    main()
