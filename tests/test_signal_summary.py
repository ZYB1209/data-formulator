import unittest

import pandas as pd

from data_formulator.signal_summary import summarize_signals


class TestSignalSummary(unittest.TestCase):
    def test_known_values(self):
        """用已知答案检查统计结果，并确认原始数据未修改。"""
        df = pd.DataFrame({
            "时间": [0, 1, 2, 3],
            "通道0": [1, 3, None, None],
            "通道1": [0, 4, 0, 4],
        })
        original = df.copy(deep=True)

        result = summarize_signals(df, ["通道0", "通道1"])
        first, second = result["channels"]

        self.assertEqual(result["row_count"], 4)
        self.assertEqual(result["channel_count"], 2)
        self.assertEqual(first, {
            "channel": "通道0",
            "valid_count": 2,
            "missing_count": 2,
            "mean": 2.0,
            "std": 1.0,
            "min": 1.0,
            "max": 3.0,
            "peak_to_peak": 2.0,
        })
        self.assertEqual(second["mean"], 2.0)
        self.assertEqual(second["std"], 2.0)
        self.assertEqual(second["peak_to_peak"], 4.0)
        self.assertEqual(result["most_variable_channels"], ["通道1"])
        pd.testing.assert_frame_equal(df, original)

    def test_all_missing_channel(self):
        """全空通道返回空统计值，不参与波动比较。"""
        df = pd.DataFrame({"通道0": [None, None]})

        result = summarize_signals(df, ["通道0"])
        channel = result["channels"][0]

        self.assertEqual(channel["valid_count"], 0)
        self.assertEqual(channel["missing_count"], 2)
        self.assertIsNone(channel["mean"])
        self.assertIsNone(channel["std"])
        self.assertIsNone(channel["peak_to_peak"])
        self.assertEqual(result["most_variable_channels"], [])

    def test_invalid_values(self):
        """无法识别的文字和无穷大应明确报错。"""
        for values in ([1, "错误文本"], [1, float("inf")]):
            with self.subTest(values=values):
                df = pd.DataFrame({"通道0": values})
                with self.assertRaises(ValueError):
                    summarize_signals(df, ["通道0"])

    def test_unknown_channel(self):
        """不存在的通道应明确报错。"""
        df = pd.DataFrame({"通道0": [1, 2]})

        with self.assertRaises(ValueError):
            summarize_signals(df, ["通道99"])


if __name__ == "__main__":
    unittest.main()