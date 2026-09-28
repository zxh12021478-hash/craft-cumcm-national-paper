from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_v22_manifest_routes_red_team_protocol():
    manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["version"] >= 22
    assert manifest["references"]["red_team_judge"] == "references/red-team-judge-protocol.md"
    triggers = manifest["stage_routes"]["rigorous-review"]["triggers"]
    assert "red_team_judge" in triggers
    assert "simulate_national_judge" in triggers


def test_red_team_protocol_rejects_false_independence_and_precision():
    protocol = (ROOT / "references/red-team-judge-protocol.md").read_text(encoding="utf-8")
    assert "correlated views from one system" in protocol
    assert "not independent evidence" in protocol
    assert "national percentile: not calibrated" in protocol
    assert "Do not invent Top-X placement or percentage award chances" in protocol
    assert "unable-to-verify" in protocol


def test_rigorous_review_preanchors_and_preserves_role_boundary():
    stage = (ROOT / "static/fragments/stage-rigorous-review.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "Before reading the abstract, conclusion, or claimed route" in stage
    assert "red-team-judge-protocol.md" in stage
    assert "not independent human" in skill
    assert "Do not independently generate a full paper body" in skill
