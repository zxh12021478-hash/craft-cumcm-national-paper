#!/usr/bin/env python3
"""Recheck one answer-changing source conflict; no model fitting or PDF needed."""
import importlib.util
import json
from decimal import Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def evaluate(table, level_half_width):
    values = {row['printed_year']: D(row['value']) for row in table['columns']}
    old, new = values[2022], values[2023]
    change = new - old
    return {
        'implied_change_million_tonnes': float(change),
        'level_ratio_growth_percent': float(100 * change / old),
        'agrees_with_printed_change_with_rounding':
            abs(change - D(table['printed_change'])) <= 2 * level_half_width,
        'growth_rounding_range_percent': [
            float(100 * ((new - level_half_width) / (old + level_half_width) - 1)),
            float(100 * ((new + level_half_width) / (old - level_half_width) - 1)),
        ],
    }


def main():
    facts = json.loads((ROOT / 'source.json').read_text())
    half = D(facts['level_rounding_half_width'])
    raw = evaluate(facts['raw_sector_table'], half)
    accepted = evaluate(facts['detailed_pet_table'], half)
    assert not raw['agrees_with_printed_change_with_rounding']
    assert accepted['agrees_with_printed_change_with_rounding']
    assert raw['growth_rounding_range_percent'][1] < 0
    assert accepted['growth_rounding_range_percent'][0] > 0
    # The printed levels are rounded. Their implied rate need not equal the
    # separately rounded reported rate to its last displayed digit.
    reported = D(facts['detailed_pet_table']['printed_growth_percent'])
    rate_half = D(facts['growth_rounding_half_width_percent'])
    low, high = map(D, map(str, accepted['growth_rounding_range_percent']))
    assert low <= reported + rate_half and high >= reported - rate_half

    script = REPO / 'skills/craft-apmcm-paper/scripts/check_information.py'
    spec = importlib.util.spec_from_file_location('availability', script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Illustrative YEAR indices, not an archived real-time backtest. A2024
    # vintage for period2022 cannot be observed at a2023 forecast origin.
    trace = {'availability_lags': {'tonnage_2022_v2024': 1},
             'forecasts': [{'id': 'origin2023', 'origin': 2023, 'target': 2024,
                            'features': [{'name': 'tonnage_2022_v2024',
                                          'source_time': 2022, 'kind': 'observed'}]}]}
    falsely_labeled = module.audit(trace)
    trace['availability_lags']['tonnage_2022_v2024'] = 2
    corrected = module.audit(trace)
    assert falsely_labeled['status'] == 'pass'
    assert corrected['status'] == 'fail'
    assert corrected['errors'][0]['code'] == 'FUTURE_INFORMATION'
    result = {
        'check_status': 'pass',
        'meaning': 'Source arithmetic conflict identified and reconciled with detailed table; metadata guard scope demonstrated',
        'literal_sector_headers': raw,
        'detailed_pet_headers': accepted,
        'printed_growth_percent': float(reported),
        'reported_rate_consistent_with_rounded_levels': True,
        'illustrative_vintage_guard': {
            'false_first_release_lag_status': falsely_labeled['status'],
            'correct_revision_lag_status': corrected['status'],
            'correct_revision_error': corrected['errors'],
            'boundary': 'Declared metadata demonstration only; no real-time forecast score or inferred publication date'},
        'readiness': 'One historical production-growth interval; not a fitted consumption-growth model, empirical policy validation or contest clearance',
        'unchanged_prior_2024C_anchor': 34.96,
        'prior_results_or_PDF_changed': False,
        'behavior_test': 'No model receiver or independent AI pass in this narrow source check',
    }
    (ROOT / 'check-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
