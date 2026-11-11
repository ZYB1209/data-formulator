import numpy as np
import pandas as pd


def summarize_signals(
    df: pd.DataFrame,
    channel_columns: list[str],
) -> dict:
    """统计指定信号列，不修改原始数据。"""

    if not channel_columns:
        raise ValueError("请至少选择一个信号通道。")

    if len(channel_columns) != len(set(channel_columns)):
        raise ValueError("通道名称不能重复。")

    if not df.columns.is_unique:
        raise ValueError("表格存在重名列，请先确认列名。")

    missing_columns = [
        column for column in channel_columns
        if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(f"表格中找不到这些列：{missing_columns}")

    summaries = []

    for column in channel_columns:
        source = df[column]

        # 允许数字文本，但拒绝把其他文字静默当成缺失值。
        numeric = pd.to_numeric(source, errors="coerce")
        invalid_count = int((source.notna() & numeric.isna()).sum())
        if invalid_count:
            raise ValueError(
                f"通道 {column} 有 {invalid_count} 个无法转换为数字的值。"
            )

        values = numeric.dropna().to_numpy(dtype=float)

        if not np.isfinite(values).all():
            raise ValueError(f"通道 {column} 包含无穷大等非有限数值。")

        valid_count = int(len(values))
        summary = {
            "channel": column,
            "valid_count": valid_count,
            "missing_count": int(source.isna().sum()),
            "mean": None,
            "std": None,
            "min": None,
            "max": None,
            "peak_to_peak": None,
        }

        if valid_count > 0:
            summary.update({
                "mean": float(np.mean(values)),
                "std": float(np.std(values, ddof=0)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "peak_to_peak": float(np.max(values) - np.min(values)),
            })

        summaries.append(summary)

    # 至少有两个有效点，才参与波动大小比较。
    comparable = [
        item for item in summaries
        if item["valid_count"] >= 2
    ]
    most_variable_channels = []

    if comparable:
        largest_std = max(item["std"] for item in comparable)
        most_variable_channels = [
            item["channel"]
            for item in comparable
            if item["std"] == largest_std
        ]

    return {
        "row_count": int(len(df)),
        "channel_count": len(channel_columns),
        "std_ddof": 0,
        "variability_metric": "std",
        "channels": summaries,
        "most_variable_channels": most_variable_channels,
    }