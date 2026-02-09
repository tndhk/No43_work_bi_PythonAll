"""Chart builders for Cursor Usage Dashboard.

Contains aggregation logic for charts. Uses shared build_chart/build_table
infrastructure with specs from _constants.py.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.layout_helpers import apply_compact_chart_layout
from ._constants import (
    COLUMN_MAP,
    COST_TREND_SPEC,
    TOKEN_EFFICIENCY_SPEC,
    MODEL_DISTRIBUTION_SPEC,
    DETAIL_TABLE_SPEC,
)




def build_daily_cost_trend(df: pd.DataFrame):
    """Build daily cost trend line chart.

    Args:
        df: Filtered DataFrame with Date and Cost columns.

    Returns:
        Plotly figure for the cost trend chart.
    """
    date_col = COLUMN_MAP["date"]
    cost_col = COLUMN_MAP["cost"]

    daily_cost = df.groupby(df[date_col].dt.date)[cost_col].sum().reset_index()
    daily_cost.columns = [date_col, cost_col]
    daily_cost = daily_cost.sort_values(date_col)

    fig = build_chart(daily_cost, COST_TREND_SPEC)
    return apply_compact_chart_layout(
        fig,
        margin={"l": 48, "r": 16, "t": 8, "b": 40},
    )


def build_token_efficiency_chart(df: pd.DataFrame):
    """Build token efficiency bar chart.

    Args:
        df: Filtered DataFrame with Model, Total Tokens, and Cost columns.

    Returns:
        Plotly figure for the token efficiency chart.
    """
    model_col = COLUMN_MAP["model"]
    total_tokens_col = COLUMN_MAP["total_tokens"]
    cost_col = COLUMN_MAP["cost"]

    model_stats = df.groupby(model_col).agg({
        total_tokens_col: "sum",
        cost_col: "sum",
    }).reset_index()
    model_stats["TokensPerCost"] = model_stats[total_tokens_col] / model_stats[cost_col]
    model_stats = model_stats.sort_values("TokensPerCost", ascending=False)

    fig = build_chart(model_stats, TOKEN_EFFICIENCY_SPEC)
    if len(fig.data) > 0:
        fig.update_traces(textposition="inside")
    return apply_compact_chart_layout(
        fig,
        margin={"l": 24, "r": 8, "t": 8, "b": 44},
    )


def build_model_distribution_chart(df: pd.DataFrame):
    """Build model distribution pie chart.

    Args:
        df: Filtered DataFrame with Model and Cost columns.

    Returns:
        Plotly figure for the model distribution chart.
    """
    model_col = COLUMN_MAP["model"]
    cost_col = COLUMN_MAP["cost"]

    model_dist = df.groupby(model_col)[cost_col].sum().reset_index()
    model_dist.columns = [model_col, cost_col]

    fig = build_chart(model_dist, MODEL_DISTRIBUTION_SPEC)
    if len(fig.data) > 0:
        fig.update_traces(
            textinfo="label+value+percent",
            textposition="inside",
        )
    return apply_compact_chart_layout(
        fig,
        margin={"l": 8, "r": 8, "t": 8, "b": 34},
        legend={"orientation": "h"},
    )


def build_detail_table(df: pd.DataFrame):
    """Build detailed data table.
    
    Args:
        df: Filtered DataFrame.
        
    Returns:
        Tuple of (title, table_component).
    """
    date_col = COLUMN_MAP["date"]
    
    display_df = df.copy()
    display_df[date_col] = display_df[date_col].dt.strftime("%Y-%m-%d %H:%M")

    return build_table(display_df, DETAIL_TABLE_SPEC)
