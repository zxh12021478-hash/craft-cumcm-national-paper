import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CurrentRuleTests(unittest.TestCase):
    def test_manifest_tracks_2026_ai_rule(self):
        payload = json.loads((ROOT / "assets" / "rules" / "cumcm-current-rules.json").read_text(encoding="utf-8"))
        ai_rule = next(item for item in payload["documents"] if item["id"] == "ai-use-policy")
        self.assertIn("fef94648f2836ab6cc81586f4c38512b", ai_rule["url"])
        self.assertIn("参考文献之前设置", ai_rule["required_phrases"])
        self.assertIn("逐项人工审查与核实", ai_rule["required_phrases"])

    def test_used_ai_declaration_replaces_2025_marking_checks(self):
        validator = load_module("validate_submission")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paper = root / "paper.txt"
            disclosure = root / "AI工具使用详情.pdf"
            paper.write_text(
                "正文\nAI工具使用声明\n"
                "本参赛队在竞赛过程中使用了AI工具，主要用于代码调试和语言润色，详细使用情况见支撑材料。\n"
                "参考文献\n[1] 示例\n",
                encoding="utf-8",
            )
            disclosure.write_bytes(b"placeholder")
            report = validator.ai_cross_check(paper, disclosure, "yes", True)
            self.assertEqual([], report["findings"])

    def test_declaration_after_references_is_blocked(self):
        validator = load_module("validate_submission")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paper = root / "paper.txt"
            disclosure = root / "AI工具使用详情.pdf"
            paper.write_text(
                "参考文献\n[1] 示例\nAI工具使用声明\n"
                "本参赛队在竞赛过程中使用了AI工具，主要用于代码调试，详细使用情况见支撑材料。\n",
                encoding="utf-8",
            )
            disclosure.write_bytes(b"placeholder")
            report = validator.ai_cross_check(paper, disclosure, "yes", True)
            self.assertIn("AI_DECLARATION_POSITION", {item["code"] for item in report["findings"]})

    def test_disclosure_separates_official_and_team_fields(self):
        validator = load_module("validate_ai_disclosure")
        with tempfile.TemporaryDirectory() as temp:
            disclosure = Path(temp) / "detail.txt"
            disclosure.write_text(
                "工具名称：Codex\n版本：GPT-5\n开发机构：OpenAI\n使用日期：2026-09-10\n"
                "使用目的和环节：代码调试\n主要提示方式与使用过程：对报错进行定位。\n"
                "采纳情况：部分采纳\n人工修改情况：重写边界检查。\n人工核验：独立运行。\n"
                "影响的论文位置：3.2节。团队逐项核对输入、输出、单位、边界条件与异常路径，"
                "并从干净环境复现程序结果；未采纳无法由独立计算或原始数据支持的建议。"
                "采用前由队员重新推导关键公式，对照原始数据回算主要数值，并核查代码实现与论文叙述。"
                "对于语言润色，仅保留不改变事实、数值、因果关系和结论边界的修改；其余输出均记录接受或拒绝理由。\n",
                encoding="utf-8",
            )
            report = validator.inspect(disclosure)
            self.assertEqual([], report["missing_fields"])
            self.assertEqual([], report["missing_traceability_fields"])
            self.assertEqual([], report["findings"])


if __name__ == "__main__":
    unittest.main()
