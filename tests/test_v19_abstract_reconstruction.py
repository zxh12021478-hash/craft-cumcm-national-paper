from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "abstract_guard.py"


class AbstractReconstructionTests(unittest.TestCase):
    def test_protocol_is_routed_and_evidence_anchored(self):
        manifest = (ROOT / "manifest.yaml").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "references" / "abstract-reconstruction-protocol.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("version: 25", manifest)
        self.assertIn("rebuild_abstract_from_full_markdown", manifest)
        self.assertIn("abstract_reconstruction", manifest)
        self.assertIn("abstract_guard", manifest)
        self.assertIn("Complete-Markdown abstract-only reconstruction", skill)
        for required in (
            "only source from which the revised abstract may acquire facts",
            "S/A/B/C value ordering",
            "Original-abstract loss audit",
            "local 134-paper collection",
            "every byte outside",
        ):
            with self.subTest(required=required):
                self.assertIn(required, protocol)

    def test_ledger_has_candidate_pool_and_loss_audit(self):
        ledger = (ROOT / "assets" / "templates" / "论文论证台账模板.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("摘要事实候选池", ledger)
        self.assertIn("原摘要信息损失与失真审计", ledger)
        self.assertIn("正文证据定位", ledger)
        self.assertIn("S / A / B / C", ledger)

    def test_replace_preserves_heading_keywords_and_remainder(self):
        source_text = (
            "# 题目\n\n## 摘要\n\n旧摘要第一段。\n\n"
            "**关键词：** 原词一；原词二\n\n## 一、问题分析\n正文数字 12.3。\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "paper.md"
            abstract = root / "abstract.txt"
            revised = root / "revised.md"
            replace_report = root / "replace.json"
            verify_report = root / "verify.json"
            source.write_text(source_text, encoding="utf-8")
            abstract.write_text("新摘要给出直接答案 12.3，并报告验证证据。", encoding="utf-8")

            replaced = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "replace",
                    "--source",
                    str(source),
                    "--abstract",
                    str(abstract),
                    "--output",
                    str(revised),
                    "--report",
                    str(replace_report),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(replaced.returncode, 0, replaced.stderr)
            verified = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "verify",
                    "--original",
                    str(source),
                    "--revised",
                    str(revised),
                    "--report",
                    str(verify_report),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(verified.returncode, 0, verified.stderr)
            report = json.loads(verify_report.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "pass")
            self.assertTrue(report["abstract_changed"])
            self.assertTrue(report["abstract_heading_unchanged"])
            self.assertTrue(report["keywords_and_remainder_unchanged"])
            self.assertIn("**关键词：** 原词一；原词二", revised.read_text(encoding="utf-8"))

    def test_verify_blocks_non_abstract_change(self):
        original = "## 摘要\n\n旧摘要。\n\n关键词：甲；乙\n\n## 正文\n原正文。\n"
        revised = "## 摘要\n\n新摘要。\n\n关键词：甲；乙\n\n## 正文\n被修改的正文。\n"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original_path = root / "original.md"
            revised_path = root / "revised.md"
            original_path.write_text(original, encoding="utf-8")
            revised_path.write_text(revised, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "verify",
                    "--original",
                    str(original_path),
                    "--revised",
                    str(revised_path),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "blocked")

    def test_replace_fails_closed_on_ambiguous_abstract_heading(self):
        source_text = (
            "## 摘要\n\n旧摘要。\n\n关键词：甲\n\n"
            "## 附录\n\n## 摘要\n\n说明。\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "paper.md"
            abstract = root / "abstract.txt"
            output = root / "output.md"
            source.write_text(source_text, encoding="utf-8")
            abstract.write_text("新摘要。", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "replace",
                    "--source",
                    str(source),
                    "--abstract",
                    str(abstract),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())
            self.assertIn("exactly one abstract heading", result.stderr)


if __name__ == "__main__":
    unittest.main()
