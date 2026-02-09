"""Chart and table builders for Hamm Overview dashboard.

Delegates rendering to shared infrastructure:
- build_volume_table: build_table(df, VOLUME_TABLE_SPEC) -> (title, DataTable)
- build_volume_chart: build_chart(df, VOLUME_CHART_SPEC) -> go.Figure (+ custom layout)
- build_task_table: build_table(df, TASK_TABLE_SPEC) -> (title, DataTable)
- build_language_table: build_table(df, LANGUAGE_TABLE_SPEC) -> (title, DataTable)
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go

from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.layout_helpers import apply_compact_chart_layout
from ._constants import (
    VOLUME_TABLE_SPEC,
    VOLUME_CHART_SPEC,
    TASK_TABLE_SPEC,
    LANGUAGE_TABLE_SPEC,
    ERROR_RATIO_SPEC,
    ERROR_BY_SCREENER_SPEC,
    USER_BREAKDOWN_SPEC,
    HAMM_BREAKDOWN_SPEC,
    ORIGINAL_LANGUAGE_SPEC,
    DIALOGUE_SPEC,
    GENRE_SPEC,
)


def build_volume_table(df: pd.DataFrame) -> tuple[str, Any]:
    """Render volume summary DataFrame via shared build_table.

    Args:
        df: Volume summary DataFrame with columns: Fiscal Year,
            Fiscal Quarter, ISO Week, Start Date, End Date,
            Completed, Invalid, VOLUME TOTAL.

    Returns:
        A ``(title, component)`` tuple where component is either a
        ``dash_table.DataTable`` or an ``html.P`` empty-state placeholder.
    """
    return build_table(df, VOLUME_TABLE_SPEC)


def build_volume_chart(df: pd.DataFrame) -> go.Figure:
    """Render volume summary DataFrame via shared build_chart + compact layout.

    Delegates trace creation and theme application to the shared
    ``build_chart`` infrastructure, then applies ``apply_compact_chart_layout``
    for page-specific layout overrides (margin, legend orientation, axis titles).

    Args:
        df: Volume summary DataFrame with Start Date, Completed, Invalid columns.

    Returns:
        A themed go.Figure with stacked bar traces, or empty-state figure.
    """
    fig = build_chart(df, VOLUME_CHART_SPEC)

    if len(fig.data) > 0:
        fig.update_traces(textposition="inside")

    return apply_compact_chart_layout(
        fig,
        margin={"l": 30, "r": 10, "t": 8, "b": 60},
        legend={"orientation": "h", "y": -0.25},
    )


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


def build_language_table(df: pd.DataFrame) -> tuple[str, Any]:
    """Render pre-transformed language display DataFrame via shared build_table.

    Expects a DataFrame already processed with display column names
    (Task ID, Task Name, Content Type, Status, Language Count,
    Additional Languages).

    Args:
        df: Display-ready DataFrame with columns matching
            LANGUAGE_TABLE_SPEC.column_order.

    Returns:
        A ``(title, component)`` tuple where component is either a
        ``dash_table.DataTable`` or an ``html.P`` empty-state placeholder.
    """
    return build_table(df, LANGUAGE_TABLE_SPEC)


# ---------------------------------------------------------------------------
# Error Details chart builders
# ---------------------------------------------------------------------------

def build_error_ratio_chart(df: pd.DataFrame) -> go.Figure:
    """Render User vs HAMM ratio via shared build_chart + compact layout.

    Args:
        df: DataFrame with columns: error_type, count

    Returns:
        A themed go.Figure with pie chart, or empty-state figure.
    """
    fig = build_chart(df, ERROR_RATIO_SPEC)

    if len(fig.data) > 0:
        fig.update_traces(
            textinfo="label+value+percent",
            textposition="inside",
        )

    return apply_compact_chart_layout(
        fig,
        margin={"l": 8, "r": 8, "t": 8, "b": 34},
        legend={"orientation": "h", "x": 0.0, "y": -0.06},
    )


def build_error_by_screener_chart(df: pd.DataFrame) -> go.Figure:
    """Render Screener Type vs User/HAMM intervention via shared build_chart + compact layout.

    Args:
        df: DataFrame with columns: video_type_description, User, HAMM

    Returns:
        A themed go.Figure with stacked bar chart, or empty-state figure.
    """
    fig = build_chart(df, ERROR_BY_SCREENER_SPEC)

    if len(fig.data) > 0:
        fig.update_traces(textposition="inside")

    return apply_compact_chart_layout(
        fig,
        margin={"l": 16, "r": 70, "t": 8, "b": 30},
        legend={
            "orientation": "v",
            "x": 1.02,
            "xanchor": "left",
            "y": 0.5,
            "yanchor": "middle",
        },
    )


def build_user_breakdown_chart(df: pd.DataFrame) -> go.Figure:
    """Render User intervention breakdown via shared build_chart + compact layout.

    Args:
        df: DataFrame with columns: error_description, count

    Returns:
        A themed go.Figure with bar chart, or empty-state figure.
    """
    fig = build_chart(df, USER_BREAKDOWN_SPEC)

    return apply_compact_chart_layout(
        fig,
        margin={"l": 24, "r": 8, "t": 8, "b": 44},
    )


def build_hamm_breakdown_chart(df: pd.DataFrame) -> go.Figure:
    """Render HAMM intervention breakdown via shared build_chart + compact layout.

    Args:
        df: DataFrame with columns: error_description, count

    Returns:
        A themed go.Figure with bar chart, or empty-state figure.
    """
    fig = build_chart(df, HAMM_BREAKDOWN_SPEC)

    return apply_compact_chart_layout(
        fig,
        margin={"l": 24, "r": 8, "t": 8, "b": 44},
    )




def build_original_language_chart(df: pd.DataFrame) -> go.Figure:
    """Render original language distribution via shared build_chart."""
    fig = build_chart(df, ORIGINAL_LANGUAGE_SPEC)
    if len(df) > 0 and len(fig.data) > 0:
        # Pie uses category-based colors; ensure image-aligned colours.
        color_map = ORIGINAL_LANGUAGE_SPEC.color_map or {}
        colors = [color_map.get(label) for label in df["original_language"]]
        fig.update_traces(
            marker={"colors": colors},
            textinfo="label+value+percent",
            textposition="inside",
        )
    return apply_compact_chart_layout(
        fig,
        margin={"l": 8, "r": 8, "t": 8, "b": 34},
        legend={"orientation": "h", "x": 0.0, "y": -0.06},
    )


def build_dialogue_chart(df: pd.DataFrame) -> go.Figure:
    """Render dialogue Yes/No by content type via shared build_chart."""
    fig = build_chart(df, DIALOGUE_SPEC)
    if len(fig.data) > 0:
        fig.update_traces(textposition="inside")
    return apply_compact_chart_layout(
        fig,
        margin={"l": 16, "r": 70, "t": 8, "b": 30},
        legend={"orientation": "v", "x": 1.02, "xanchor": "left", "y": 0.5, "yanchor": "middle"},
    )


def build_genre_chart(df: pd.DataFrame) -> go.Figure:
    """Render genre distribution via shared build_chart."""
    fig = build_chart(df, GENRE_SPEC)
    return apply_compact_chart_layout(
        fig,
        margin={"l": 24, "r": 8, "t": 8, "b": 44},
    )
