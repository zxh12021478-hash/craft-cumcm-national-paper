from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TwoWriterBriefTests(unittest.TestCase):
    def test_outline_template_has_exactly_two_numbered_writer_blocks(self):
        template = (ROOT / "assets" / "templates" / "推荐解题思路大纲模板.md").read_text(
            encoding="utf-8"
        )
        headings = re.findall(r"^###\s+([12])\.\s+(.+)$", template, re.MULTILINE)
        self.assertEqual(
            headings,
            [
                ("1", "题型适配、模型主线与高价值可视化建议"),
                ("2", "求解真实性、验证闭环与成文质量建议"),
            ],
        )
        self.assertIn("不得原样复用模板句", template)
        self.assertIn("具体到本题的小问和变量关系", template)
        self.assertIn("禁止生成数据、虚构", template)

    def test_two_blocks_are_inside_the_single_handoff(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "static" / "core-workflow.md").read_text(encoding="utf-8")
        delivery = (ROOT / "static" / "core-delivery.md").read_text(encoding="utf-8")
        handoff = (ROOT / "references" / "two-system-handoff.md").read_text(encoding="utf-8")
        combined = "\n".join((skill, workflow, delivery, handoff))
        self.assertIn("exactly one user-facing", skill)
        self.assertIn("not two companion files", delivery)
        self.assertIn("not additional deliverables", workflow)
        for heading in (
            "题型适配、模型主线与高价值可视化建议",
            "求解真实性、验证闭环与成文质量建议",
        ):
            self.assertIn(heading, combined)

    def test_blocks_preserve_conceptual_boundary_and_reject_arbitrary_quotas(self):
        template = (ROOT / "assets" / "templates" / "推荐解题思路大纲模板.md").read_text(
            encoding="utf-8"
        )
        handoff = (ROOT / "references" / "two-system-handoff.md").read_text(encoding="utf-8")
        combined = template + "\n" + handoff
        for required in (
            "不写完整公式、计算步骤、参数、伪代码或代码",
            "three-dimensional figure is optional",
            "Do not prescribe a number of 3D figures",
            "若题目确有随时间演化",
            "若没有，就明确不应为满足形式而制造仿真",
            "篇幅服从当年官方规则而非固定页数",
        ):
            self.assertIn(required, combined)
        for banned in (
            r"至少\s*3\s*个伪代码",
            r"3D.{0,12}不少于\s*3",
            r"4\s*[-—~～]\s*5\s*张",
            r"附录.{0,8}3\s*[-—~～]\s*4\s*页",
            r"摘要.{0,8}充满.{0,8}第一页",
        ):
            self.assertIsNone(re.search(banned, combined, re.I))


if __name__ == "__main__":
    unittest.main()
