"""Build LLM context from DataFrame for chat interactions."""
from __future__ import annotations

import pandas as pd

from src.llm.page_context import DashboardContext

MAX_SAMPLE_ROWS = 5
MAX_TOP_VALUES = 5


def _build_dashboard_section(dashboard_context: DashboardContext) -> list[str]:
    """Build the dashboard context sections (description, KPIs, filters).

    Returns a list of string parts to prepend to the main context.
    """
    parts: list[str] = []

    # Dashboard description
    parts.append("## ダッシュボード情報")
    parts.append(dashboard_context.page_description)

    # KPIs (only if non-empty)
    if dashboard_context.kpis:
        parts.append("\n## 現在のKPI値")
        for kpi in dashboard_context.kpis:
            parts.append(f"- {kpi.name}: {kpi.value} ({kpi.logic})")

    # Active filters (only if non-empty)
    if dashboard_context.active_filters:
        parts.append("\n## アクティブフィルタ")
        for name, values in dashboard_context.active_filters.items():
            if values is None:
                parts.append(f"- {name}: 全選択")
            elif isinstance(values, str):
                parts.append(f"- {name}: {values}")
            elif len(values) > 20:
                shown = ", ".join(values[:20])
                parts.append(
                    f"- {name}: {shown} ... (他{len(values) - 20}件)"
                )
            else:
                parts.append(f"- {name}: {', '.join(values)}")

    parts.append("")  # blank line separator before dataset info
    return parts


def build_llm_context(
    df: pd.DataFrame,
    dataset_name: str,
    *,
    dashboard_context: DashboardContext | None = None,
) -> str:
    """Build a context string from a DataFrame for LLM consumption.

    Generates schema information, basic statistics, and sample data
    that the LLM can use to understand and analyze the dataset.

    Args:
        df: The DataFrame to summarize.
        dataset_name: Human-readable name for the dataset.
        dashboard_context: Optional dashboard-level context (KPIs, filters, etc.).

    Returns:
        Context string suitable for injection into a system prompt.
    """
    parts: list[str] = []

    if dashboard_context is not None:
        parts.extend(_build_dashboard_section(dashboard_context))

    parts.append(f"データセット名: {dataset_name}")
    parts.append(f"行数: {len(df)}")
    parts.append(f"列数: {len(df.columns)}")

    if len(df.columns) == 0:
        return "\n".join(parts)

    # Schema
    parts.append("\nスキーマ:")
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = int(df[col].isna().sum())
        parts.append(f"  - {col} ({dtype}, null: {null_count})")

    # Statistics
    parts.append("\n統計情報:")
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            non_null = df[col].dropna()
            if len(non_null) > 0:
                parts.append(
                    f"  - {col}: min={non_null.min()}, max={non_null.max()}, "
                    f"mean={non_null.mean():.2f}"
                )
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            non_null = df[col].dropna()
            if len(non_null) > 0:
                parts.append(
                    f"  - {col}: min={non_null.min()}, max={non_null.max()}"
                )
        else:
            non_null = df[col].dropna()
            unique_count = non_null.nunique()
            top_values = non_null.value_counts().head(MAX_TOP_VALUES).index.tolist()
            top_str = ", ".join(str(v) for v in top_values)
            parts.append(
                f"  - {col}: {unique_count} unique values, top: [{top_str}]"
            )

    # Sample data
    sample = df.head(MAX_SAMPLE_ROWS)
    if len(sample) > 0:
        parts.append(f"\nサンプルデータ（先頭{len(sample)}行）:")
        parts.append(sample.to_string(index=False))

    return "\n".join(parts)
