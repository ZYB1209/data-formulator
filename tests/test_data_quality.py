import unittest

import pandas as pd

from data_formulator.data_quality import check_data_quality


class TestDataQuality(unittest.TestCase):
    def test_data_with_problems(self):
        """含缺失值、重复行和常量列的数据。"""
        df = pd.DataFrame({
            "position": [0, 1, 1, 2],
            "signal": [10, 12, 12, None],
            "channel": ["A", "A", "A", "A"],
        })
        original = df.copy(deep=True)

        result = check_data_quality(df)

        self.assertEqual(result["row_count"], 4)
        self.assertEqual(result["column_count"], 3)
        self.assertEqual(
            result["missing_values"],
            {"position": 0, "signal": 1, "channel": 0},
        )
        self.assertEqual(result["duplicate_row_count"], 1)
        self.assertEqual(result["constant_columns"], ["channel"])
        pd.testing.assert_frame_equal(df, original)

    def test_clean_two_channel_data(self):
        """同一位置有两个通道，不应被误判为重复行。"""
        df = pd.DataFrame([
            {
                "position": position,
                "channel": channel,
                "signal": position * 0.1 + offset,
            }
            for position in range(120)
            for channel, offset in [("A", 10), ("B", 11)]
        ])
        original = df.copy(deep=True)

        result = check_data_quality(df)

        self.assertEqual(result["row_count"], 240)
        self.assertEqual(result["column_count"], 3)
        self.assertEqual(
            result["missing_values"],
            {"position": 0, "channel": 0, "signal": 0},
        )
        self.assertEqual(result["duplicate_row_count"], 0)
        self.assertEqual(result["constant_columns"], [])
        pd.testing.assert_frame_equal(df, original)

class TestDataQualityTool(unittest.TestCase):
    def setUp(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from data_formulator.analyst.skills.core.skill import CoreSkill

        self.df = pd.DataFrame({
            "position": [0, 1, 1, 2],
            "signal": [10, 12, 12, None],
            "channel": ["A", "A", "A", "A"],
        })

        # 模拟工作区读取表格，不需要打开网页。
        self.workspace = Mock()
        self.workspace.read_data_as_df.return_value = self.df

        self.ctx = SimpleNamespace(
            payload={"input_tables": [{"name": "demo"}]},
            workspace=self.workspace,
        )
        self.skill = CoreSkill()

    def test_existing_table(self):
        """表名正确：读取对应表格，返回正确的 JSON。"""
        import json

        result = self.skill.handle_tool(
            "check_data_quality",
            {"table_name": "demo"},
            self.ctx,
        )
        report = json.loads(result.text)

        self.assertEqual(report, {
            "table_name": "demo",
            "row_count": 4,
            "column_count": 3,
            "missing_values": {
                "position": 0,
                "signal": 1,
                "channel": 0,
            },
            "duplicate_row_count": 1,
            "constant_columns": ["channel"],
        })
        self.workspace.read_data_as_df.assert_called_once_with("demo")

    def test_unknown_table(self):
        """表名不存在：拒绝请求，不尝试读取数据。"""
        result = self.skill.handle_tool(
            "check_data_quality",
            {"table_name": "not_existing"},
            self.ctx,
        )

        self.assertIn("Error:", result.text)
        self.assertIn("existing table", result.text)
        self.workspace.read_data_as_df.assert_not_called()
if __name__ == "__main__":
    unittest.main()
