"""Check a historical Summary's mapped values/configurations, not its prose quality."""
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parent


def pointer(data, path):
    for key in path.strip('/').split('/'):
        data = data[int(key)] if isinstance(data, list) else data[key]
    return data


def main():
    source = (P / 'frozen-results.json').read_bytes()
    results = json.loads(source)
    ledger = json.loads((P / 'claim-ledger.json').read_text())
    summary = (P / 'summary.md').read_text()
    assert hashlib.sha256(source).hexdigest() == ledger['source_sha256']
    mapped = []
    for c in ledger['claims']:
        actual = pointer(results, c['result_pointer']) * c['multiplier']
        error = abs(actual - c['displayed_value'])
        assert c['quote'] in summary, c['id']
        assert error <= c['absolute_tolerance'], (c['id'], actual)
        mapped.append({'id': c['id'], 'actual': actual,
                       'displayed': c['displayed_value'], 'error': error})
    wins = results['winners']
    common = ['location', 'z', 'q', 'zin', 'nin', 'angle']
    assert all(wins[q]['design'][k] == wins['Q4']['design'][k]
               for q in wins for k in common)
    assert wins['Q1']['design']['shape'] == 'cylinder'
    assert wins['Q1']['design']['nout'] == 1
    assert wins['Q2']['design']['shape'] == 'tower'
    assert wins['Q2']['design']['nout'] == 2
    assert wins['Q3']['design'] == wins['Q4']['design']
    assert wins['Q4']['design']['shape'] == 'tower'
    assert wins['Q4']['design']['nout'] == 1
    assert wins['Q3']['winter']['RH_final_mean_pct'] < 50
    # The integrated objective alone averages the four normalized components.
    assert abs(sum(wins['Q4']['metrics']) / 4 - wins['Q4']['score']) < 1e-12
    for name, key in [('baseline', 'score_improvement_pct'),
                      ('same_flow_baseline', 'same_flow_improvement_pct')]:
        gain = 100 * (results[name]['score'] - wins['Q4']['score']) / results[name]['score']
        assert abs(gain - results[key]) < 1e-12
    same = results['same_flow_baseline']['design']
    changed = sorted(k for k in same if same[k] != wins['Q4']['design'][k])
    assert changed == ['angle', 'location']
    mix_tests = [x for x in results['sensitivity'] if x['parameter'] == 'mix']
    assert sorted(x['factor'] for x in mix_tests) == [0.7, 1.3]
    assert all(x['reranked_design'] == wins['Q4']['design'] for x in mix_tests)
    return {'status': 'pass', 'mapped_numeric_claims': mapped,
            'shared_settings_consistent': True, 'same_flow_changed_fields': changed,
            'RH_target_not_reached': True, 'mixing_rerank_scope_checked': True,
            'scope': 'Arithmetic, provenance and configuration checks only. '
                     'No new solver run, physical validation, English semantic '
                     'grading, independent receiver or actual Modex test.'}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
