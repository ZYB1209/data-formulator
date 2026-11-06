import pandas as pd


def check_data_quality(df: pd.DataFrame) -> dict:
    """检查表格质量，只报告问题，不修改原始数据。"""

    # 统计每列缺失值数量
    missing_counts = df.isna().sum()

    # 找出只有一种非空取值的列；全空列由缺失值检查报告
    constant_columns = [
        column
        for column in df.columns
        if df[column].nunique(dropna=True) == 1
    ]

    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_values": {
            str(column): int(count)
            for column, count in missing_counts.items()
        },
        # 相同记录保留第一条，其余计为重复行
        "duplicate_row_count": int(df.duplicated().sum()),
        "constant_columns": [str(column) for column in constant_columns],
    }