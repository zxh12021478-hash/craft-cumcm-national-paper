"""Arithmetic/configuration evidence only; not a language or physical-model grader."""
import json
from pathlib import Path


def check(facts):
    selected = facts["selected"]
    same = facts["same_flow_baseline"]
    baseline = facts["baseline"]
    changed = sorted(k for k in selected["design"]
                     if selected["design"][k] != same["design"][k])
    assert changed == ["angle", "location"]
    assert selected["design"]["q"] == same["design"]["q"] == 600
    assert selected["design"]["shape"] == same["design"]["shape"] == "tower"
    assert [facts["question_objectives"][q]["component_index"]
            for q in ["Q1", "Q2", "Q3"]] == [0, 1, 2]
    assert sum(facts["question_objectives"]["Q4"]["weights"]) == 1
    gain = lambda ref: 100 * (ref["score"] - selected["score"]) / ref["score"]
    return {
        "same_flow_changed_settings": changed,
        "same_shell": True,
        "gain_vs_declared_baseline_pct": gain(baseline),
        "gain_vs_same_flow_baseline_pct": gain(same),
        "interpretation": "Q1-Q3 minimize separate components; Q4 uses the weighted sum. The same-flow comparison changes joint placement/angle settings, not shell shape.",
        "scope": "Checks frozen facts; does not establish successful Summary reconstruction or physical validation.",
    }


if __name__ == "__main__":
    print(json.dumps(check(json.loads(Path(__file__).with_name("facts.json").read_text())), indent=2))
