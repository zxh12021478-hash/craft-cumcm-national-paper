#!/usr/bin/env python3
"""Check a frozen source conflict; never replace the original question data."""
import hashlib
import json
from decimal import Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    source = json.loads((ROOT / 'source.json').read_text())
    api_path = ROOT / source['uncomtrade']['snapshot']
    question_path = ROOT / source['question']['input_json']
    before = question_path.read_bytes()
    assert hashlib.sha256(before).hexdigest() == source['question']['input_sha256']
    assert hashlib.sha256(api_path.read_bytes()).hexdigest() == source['uncomtrade']['sha256']
    response = json.loads(api_path.read_text())
    assert response['count'] == 1 and len(response['data']) == 1 and not response['error']
    row = response['data'][0]
    for field, expected in source['uncomtrade']['expected_row'].items():
        assert row[field] == expected, (field, row[field], expected)
    assert row['primaryValue'] == row['fobvalue']
    assert row['qtyUnitCode'] == 8  # kg, official supplementary-unit reference
    assert row['isNetWgtEstimated'] is True
    question = json.loads(before)
    years = question['years']
    exports = {year: D(str(value)) for year, value in
               zip(years, question['exports_value_original'])}
    currencies = dict(zip(years, question['exports_currency']))
    assert all(currencies[y] == 'USD' for y in [2021, 2022, 2023])
    ministry = {int(year): D(str(value)) for year, value in
                source['mofcom']['export_value_100m_USD'].items()}
    scale = D(str(question['value_scale']))
    value, mass = D(str(row['primaryValue'])), D(str(row['netWgt']))
    assert value > 0 and mass > 0
    matched_unit_value = value / mass
    hybrid_unit_value = exports[2023] * scale / mass
    # A common currency/unit cannot establish a common commodity scope.
    # This negative example is constructed here; it is not a received draft.
    ratio = exports[2023] * scale / value
    assert ratio > 3 and exports[2022] != ministry[2022]
    assert question_path.read_bytes() == before
    result = {
        'check_status': 'pass',
        'meaning': 'Frozen primary API row and question data reproduce; cross-source scope remains unresolved',
        '2022_comparison_100m_USD': {
            'question': float(exports[2022]), 'ministry_article': float(ministry[2022]),
            'question_2021_to_2022_growth_percent': float(100 * (exports[2022] / exports[2021] - 1)),
            'article_2021_to_2022_growth_percent': float(100 * (ministry[2022] / ministry[2021] - 1)),
            'status': 'Different labeled-source sequences; no automatic correction or splice'},
        '2023_comparison': {
            'question_export_100m_USD': float(exports[2023]),
            'UN_HS230910_export_USD': float(value),
            'UN_net_weight_kg': float(mass),
            'UN_net_weight_is_estimated': row['isNetWgtEstimated'],
            'UN_isReported': row['isReported'], 'UN_isAggregate': row['isAggregate'],
            'matched_UN_unit_value_USD_per_kg': float(matched_unit_value),
            'unit_value_interpretation': 'Aggregate descriptive unit value with estimated net weight, not a homogeneous transaction price or identified price elasticity'},
        'constructed_negative_probe': {
            'hybrid_question_value_div_UN_weight_USD_per_kg': float(hybrid_unit_value),
            'ratio_to_matched_UN_unit_value': float(ratio),
            'units': 'USD/kg in both; dimensional agreement does not resolve scope',
            'status': 'unsupported_scope',
            'judgment': 'Root semantic assessment; not an automated scope discovery or actual receiver failure'},
        'original_question_bytes_unchanged': True,
        'old_case_results_and_PDF_changed': False,
        'boundary': 'Current retrieved snapshot; not archived2024 information, a fitted forecast or empirical validation of the question-wide bridge',
    }
    (ROOT / 'check-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
