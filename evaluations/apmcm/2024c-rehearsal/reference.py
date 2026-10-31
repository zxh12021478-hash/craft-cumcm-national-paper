"""Independent reference: exact level fits and log-fit normal equations.

Does not import or execute the receiver implementation. The level-line fit
uses Fraction arithmetic; the log-line fit solves uncentered normal equations.
"""
from fractions import Fraction
from pathlib import Path
import json
import math

P = Path(__file__).resolve().parent
MODELS = ("last_value", "level_linear", "log_linear")


def predict(values, model, targets):
    if model == "last_value":
        return [float(values[-1])] * len(targets)
    n = len(values)
    sx, sxx = sum(range(n)), sum(i * i for i in range(n))
    if model == "level_linear":
        y = [Fraction(str(v)) for v in values]
    else:
        y = [math.log(float(v)) for v in values]
    sy = sum(y)
    sxy = sum(i * v for i, v in enumerate(y))
    determinant = n * sxx - sx * sx
    intercept = (sxx * sy - sx * sxy) / determinant
    slope = (n * sxy - sx * sy) / determinant
    fitted = [intercept + slope * t for t in targets]
    return ([float(v) for v in fitted] if model == "level_linear"
            else [math.exp(v) for v in fitted])


def calculate():
    data = json.loads((P / "input/data.json").read_text())
    fx = Fraction("6.8985")
    series = dict(data["pets"])
    series["production_100m_CNY"] = data["production_value_100m_CNY"]
    series["exports_100m_USD"] = [
        Fraction(str(v)) / fx if currency == "CNY" else Fraction(str(v))
        for v, currency in zip(data["exports_value_original"], data["exports_currency"])
    ]
    out = {}
    for name, values in series.items():
        validation, errors, candidates = {}, {}, {}
        for model in MODELS:
            rows = []
            for cut in (3, 4):
                forecast = predict(values[:cut], model, [cut])[0]
                rows.append({"origin": 2018 + cut, "target": 2019 + cut,
                             "forecast": forecast, "actual": float(values[cut])})
            validation[model] = rows
            errors[model] = sum(abs(r["forecast"] - r["actual"]) for r in rows) / 2
            candidates[model] = predict(values, model, [5, 6, 7])
        best = min(errors.values())
        selected = next(m for m in MODELS if abs(errors[m] - best) < 1e-12)
        out[name] = {"observed": [float(v) for v in values], "validation": validation,
                     "MAE": errors, "selected": selected,
                     "forecast_2024_2026": candidates[selected],
                     "all_candidate_forecasts": candidates}
    return out


if __name__ == "__main__":
    print(json.dumps({"series": calculate()}, indent=2))
