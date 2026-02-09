"""Chart and table builders for Hamm Overview dashboard.

Delegates rendering to shared infrastructure:
- build_volume_table: build_table(df, VOLUME_TABLE_SPEC) -> (title, DataTable)
- build_volume_chart: build_chart(df, VOLUME_CHART_SPEC) -> go.Figure (+ custom layout)
- build_task_table: build_table(df, TASK_TABLE_SPEC) -> (title, DataTable)
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go
from dash import dash_table, html

from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from ._constants import (
    VOLUME_TABLE_SPEC,
    VOLUME_CHART_SPEC,
    TASK_TABLE_SPEC,
    ERROR_RATIO_SPEC,
    ERROR_BY_SCREENER_SPEC,
    USER_BREAKDOWN_SPEC,
    HAMM_BREAKDOWN_SPEC,
)


def build_volume_table(df: pd.DataFrame) -> tuple[str, Any]:
    """Render volume summary DataFrame via shared build_table.

    Args:
        df: Volume summary DataFrame with columns: Fiscal Year,
            Fiscal Quarter, ISO Week, Start Date, End Date,
            Prelim, ERV, VOLUME TOTAL.

    Returns:
        A ``(title, component)`` tuple where component is either a
        ``dash_table.DataTable`` or an ``html.P`` empty-state placeholder.
    """
    return build_table(df, VOLUME_TABLE_SPEC)


def build_volume_chart(df: pd.DataFrame) -> go.Figure:
    """Render volume summary DataFrame via shared build_chart + custom layout.

    Delegates trace creation and theme application to the shared
    ``build_chart`` infrastructure, then applies page-specific layout
    overrides (margin, legend orientation, axis titles).

    Args:
        df: Volume summary DataFrame with Start Date, Prelim, ERV columns.

    Returns:
        A themed go.Figure with stacked bar traces, or empty-state figure.
    """
    fig = build_chart(df, VOLUME_CHART_SPEC)

    # Page-specific layout overrides (applied after theme)
    fig.update_layout(
        margin={"l": 30, "r": 10, "t": 20, "b": 60},
        legend={"orientation": "h", "y": -0.2},
        xaxis_title="",
        yaxis_title="",
    )

    return fig


def build_task_table(df: pd.DataFrame) -> tuple[str, Any]:
    """Render pre-transformed task display DataFrame via shared build_table.

    Expects a DataFrame already processed by prepare_task_display_df()
    with display column names (Task ID, Task Name, etc.).

    Args:
        df: Display-ready DataFrame with columns matching
            TASK_TABLE_SPEC.column_order.

    Returns:
        A ``(title, component)`` tuple where component is either a
        ``dash_table.DataTable`` or an ``html.P`` empty-state placeholder.
    """
    return build_table(df, TASK_TABLE_SPEC)


# ---------------------------------------------------------------------------
# Error Details chart builders
# ---------------------------------------------------------------------------

def build_error_ratio_chart(df: pd.DataFrame) -> go.Figure:
    """Render User vs HAMM ratio via shared build_chart.
    
    Args:
        df: DataFrame with columns: error_type, count
    
    Returns:
        A themed go.Figure with pie chart, or empty-state figure.
    """
    return build_chart(df, ERROR_RATIO_SPEC)


def build_error_by_screener_chart(df: pd.DataFrame) -> go.Figure:
    """Render Screener Type vs User/HAMM intervention via shared build_chart.
    
    Args:
        df: DataFrame with columns: video_type_description, User, HAMM
    
    Returns:
        A themed go.Figure with stacked bar chart, or empty-state figure.
    """
    return build_chart(df, ERROR_BY_SCREENER_SPEC)


def build_user_breakdown_chart(df: pd.DataFrame) -> go.Figure:
    """Render User intervention breakdown via shared build_chart.
    
    Args:
        df: DataFrame with columns: error_description, count
    
    Returns:
        A themed go.Figure with bar chart, or empty-state figure.
    """
    return build_chart(df, USER_BREAKDOWN_SPEC)


def build_hamm_breakdown_chart(df: pd.DataFrame) -> go.Figure:
    """Render HAMM intervention breakdown via shared build_chart.
    
    Args:
        df: DataFrame with columns: error_description, count
    
    Returns:
        A themed go.Figure with bar chart, or empty-state figure.
    """
    return build_chart(df, HAMM_BREAKDOWN_SPEC)
