from __future__ import annotations

import hashlib
import io
import importlib.util
import json
import tempfile
import unittest
import zipfile
from argparse import Namespace
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class V25RoutingTests(unittest.TestCase):
    def test_manifest_routes_operational_readiness(self):
        manifest = (ROOT / "manifest.yaml").read_text(encoding="utf-8")
        self.assertIn("version: 25", manifest)
        for needle in (
            "stage-contest-readiness.md",
            "contest_doctor.py",
            "recovery_card.py",
            "build_submission_package.py",
            "validator-runtime.json",
        ):
            self.assertIn(needle, manifest)

    def test_validator_dependencies_are_fully_pinned(self):
        requirements = (ROOT / "scripts" / "requirements-validator.txt").read_text(encoding="utf-8")
        for distribution in ("jsonschema", "pypdf", "python-docx", "Pillow", "PyYAML"):
            self.assertRegex(requirements, rf"(?im)^{distribution}==[^\s]+$")
        config = json.loads((ROOT / "assets" / "workflows" / "validator-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual("validator-v25", config["runtime_id"])
        self.assertGreaterEqual(config["minimum_free_bytes"], 2 * 1024 * 1024 * 1024)
        wheelhouse = ROOT / config["skill_relative_wheelhouse"]
        self.assertTrue(wheelhouse.is_dir())
        self.assertGreaterEqual(len(list(wheelhouse.glob("*.whl"))), 5)


class RecoveryCardTests(unittest.TestCase):
    def setUp(self):
        self.recovery = load_module("recovery_card")

    def test_card_is_hash_bound_and_detects_changed_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / ".cumcm"
            state.mkdir()
            problem = root / "A题.pdf"
            paper = root / "论文.md"
            ledger = root / "结果.json"
            problem.write_bytes(b"official problem")
            paper.write_text("draft", encoding="utf-8")
            ledger.write_text(
                json.dumps(
                    {
                        "frozen_at": "2026-09-07T12:00:00+08:00",
                        "approved_by_team": True,
                        "results": [
                            {
                                "id": "Q1-R1",
                                "question": "Q1",
                                "label": "minimum",
                                "value": 12.5,
                                "unit": "m",
                                "decision_critical": True,
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            workflow = {
                "version": 1,
                "problem": "2026-A",
                "profile": "final-strict",
                "deadline": "2099-09-10T18:00:00+08:00",
                "gates": {"result_acceptance": {"status": "approved"}},
                "declarations": {"ai_used": "yes"},
                "artifacts": {
                    "problem_bundle": {"path": "A题.pdf", "sha256": hashlib.sha256(problem.read_bytes()).hexdigest()},
                    "paper": {"path": "论文.md", "sha256": hashlib.sha256(paper.read_bytes()).hexdigest()},
                    "result_ledger": {"path": "结果.json", "sha256": hashlib.sha256(ledger.read_bytes()).hexdigest()},
                },
            }
            workflow_path = state / "workflow.json"
            workflow_path.write_text(json.dumps(workflow, ensure_ascii=False), encoding="utf-8")
            card = self.recovery.build_card(root, workflow_path, None)
            card_path = state / "赛时恢复卡.json"
            markdown_path = state / "赛时恢复卡.md"
            card_path.write_text(json.dumps(card, ensure_ascii=False), encoding="utf-8")
            markdown_path.write_text(self.recovery.render_markdown(card), encoding="utf-8")
            self.assertEqual("pass", self.recovery.verify_card(root, card_path, markdown_path)["status"])
            self.assertEqual("Q1-R1", card["headline_results"]["results"][0]["id"])
            paper.write_text("changed", encoding="utf-8")
            report = self.recovery.verify_card(root, card_path, markdown_path)
            self.assertEqual("fail", report["status"])
            self.assertIn("ARTIFACT_CHANGED", {row["code"] for row in report["findings"]})


class DeterministicPackageTests(unittest.TestCase):
    def setUp(self):
        self.packager = load_module("build_submission_package")

    def test_approved_inputs_build_identical_sorted_support_archives(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paper = root / "论文.pdf"
            support_dir = root / "support"
            support_dir.mkdir()
            code = support_dir / "run.py"
            result = support_dir / "result.json"
            paper.write_bytes(b"%PDF-1.4\n% test\n")
            code.write_text("print(1)\n", encoding="utf-8")
            result.write_text('{"value": 1}\n', encoding="utf-8")
            manifest = root / ".cumcm" / "submission-manifest.json"
            prepare_args = Namespace(
                root=root,
                paper=paper,
                support=[support_dir],
                manifest=manifest,
                paper_upload_name=None,
                support_upload_name="支撑材料.zip",
                ai_used="no",
                paper_max_bytes=20 * 1024 * 1024,
                support_max_bytes=20 * 1024 * 1024,
                replace_unapproved=False,
            )
            with redirect_stdout(io.StringIO()):
                self.assertEqual(0, self.packager.prepare(prepare_args))
                self.assertEqual(0, self.packager.approve(Namespace(manifest=manifest, approved_by="队员甲")))
            first = root / "package-1"
            second = root / "package-2"
            for output in (first, second):
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(0, self.packager.build(Namespace(manifest=manifest, root=None, output_dir=output, strict=True)))
            first_zip = first / "upload" / "支撑材料.zip"
            second_zip = second / "upload" / "支撑材料.zip"
            self.assertEqual(self.packager.sha256(first_zip), self.packager.sha256(second_zip))
            with zipfile.ZipFile(first_zip) as archive:
                self.assertEqual(sorted(archive.namelist()), archive.namelist())
                self.assertTrue(all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist()))
            self.assertEqual({"论文.pdf", "支撑材料.zip"}, {path.name for path in (first / "upload").iterdir()})
            code.write_text("print(2)\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                blocked = self.packager.build(Namespace(manifest=manifest, root=None, output_dir=root / "package-3", strict=True))
            self.assertEqual(2, blocked)

    def test_strict_build_rejects_unknown_ai_state_and_unsafe_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paper = root / "paper.pdf"
            code = root / "run.py"
            paper.write_bytes(b"pdf")
            code.write_text("pass\n", encoding="utf-8")
            payload = {
                "version": 1,
                "project_root": str(root),
                "paper": {"path": "paper.pdf", "sha256": self.packager.sha256(paper)},
                "support_archive": {"files": [{"path": "../escape.py", "sha256": "x"}]},
                "ai_used": "unknown",
                "approved_by_team": False,
            }
            _, _, _, findings = self.packager.validate_manifest(payload, None, True)
            codes = {row["code"] for row in findings}
            self.assertIn("UNSAFE_ARCHIVE_PATH", codes)
            self.assertIn("AI_USE_UNKNOWN", codes)
            self.assertIn("TEAM_APPROVAL_MISSING", codes)


if __name__ == "__main__":
    unittest.main()
