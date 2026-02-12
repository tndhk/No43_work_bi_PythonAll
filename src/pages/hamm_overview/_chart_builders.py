"""Chart and table builders for HAMM Overview dashboard.

Auto-generated from page_spec.yaml by tools.page_generator.

Delegates rendering to shared infrastructure:
- build_*_table: build_table(df, *_TABLE_SPEC) -> (title, DataTable)
- build_*_chart: build_chart(df, *_CHART_SPEC) -> go.Figure (+ custom layout)
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go

from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.layout_helpers import apply_compact_chart_layout
from ._constants import (
    VOLUME_CHART_SPEC,
    ERROR_RATIO_SPEC,
    ERROR_BY_SCREENER_SPEC,
    USER_BREAKDOWN_SPEC,
    BREAKDOWN_SPEC,
    METADATA_ORIGINAL_LANGUAGE_SPEC,
    METADATA_DIALOGUE_SPEC,
    METADATA_GENRE_SPEC,
    VOLUME_TABLE_SPEC,
    TASK_TABLE_SPEC,
    LANGUAGE_TABLE_SPEC,
)

# ---------------------------------------------------------------------------
# Reusable layout configuration constants
# ---------------------------------------------------------------------------

# Pie chart layout (error_ratio, metadata_original_language)
_PIE_MARGIN = {"l": 8, "r": 8, "t": 8, "b": 34}
_PIE_LEGEND = {"orientation": "h", "x": 0.0, "y": -0.06}

# Right-legend stacked bar layout (error_by_screener, metadata_dialogue)
_RIGHT_LEGEND_MARGIN = {"l": 16, "r": 70, "t": 8, "b": 30}
_RIGHT_LEGEND = {
    "orientation": "v",
    "x": 1.02,
    "xanchor": "left",
    "y": 0.5,
    "yanchor": "middle",
}

# Simple bar layout (user_breakdown, hamm_breakdown, metadata_genre)
_SIMPLE_BAR_MARGIN = {"l": 24, "r": 8, "t": 8, "b": 44}


def build_volume_table(df: pd.DataFrame) -> tuple[str, Any]:
    """Render Volume Summary.

    Args:
        df: Transformed DataFrame

    Returns:
        A ``(title, component)`` tuple where component is either a
        ``dash_table.DataTable`` or an ``html.P`` empty-state placeholder.
    """
    return build_table(df, VOLUME_TABLE_SPEC)


def build_task_table(df: pd.DataFrame) -> tuple[str, Any]:
    """Render Task Details.

    Args:
        df: Transformed DataFrame

    Returns:
        A ``(title, component)`` tuple where component is either a
        ``dash_table.DataTable`` or an ``html.P`` empty-state placeholder.
    """
    return build_table(df, TASK_TABLE_SPEC)


def build_language_table(df: pd.DataFrame) -> tuple[str, Any]:
    """Render Language Details.

    Args:
        df: Transformed DataFrame

    Returns:
        A ``(title, component)`` tuple where component is either a
        ``dash_table.DataTable`` or an ``html.P`` empty-state placeholder.
    """
    return build_table(df, LANGUAGE_TABLE_SPEC)


def _set_bar_textposition_inside(fig: go.Figure) -> None:
    """Set textposition='inside' for all Bar traces."""
    for trace in fig.data:
        if isinstance(trace, go.Bar):
            trace.textposition = "inside"


def _set_pie_text_details(fig: go.Figure) -> None:
    """Set textinfo and textposition for all Pie traces."""
    for trace in fig.data:
        if isinstance(trace, go.Pie):
            trace.textinfo = "label+value+percent"
            trace.textposition = "inside"


def build_volume_chart(df: pd.DataFrame) -> go.Figure:
    """Render Volume Chart.

    Args:
        df: Transformed DataFrame

    Returns:
        A themed go.Figure with stacked_bar traces, or empty-state figure.
    """
    fig = build_chart(df, VOLUME_CHART_SPEC)
    _set_bar_textposition_inside(fig)
    fig = apply_compact_chart_layout(
        fig,
        margin={"l": 30, "r": 10, "t": 8, "b": 60},
        legend={"orientation": "h", "y": -0.25},
    )
    # Sort X-axis by actual date (oldest to newest, left to right)
    if "Start Date" in df.columns and not df.empty:
        sorted_dates = (
            df.assign(
                _dt=pd.to_datetime(df["Start Date"], format="%d-%b-%y", errors="coerce")
            )
            .sort_values("_dt")["Start Date"]
            .tolist()
        )
        fig.update_xaxes(categoryorder="array", categoryarray=sorted_dates)
    return fig


def build_error_ratio(df: pd.DataFrame) -> go.Figure:
    """Render Issues Ratio (HAMM vs Human Intervention).

    Args:
        df: Transformed DataFrame

    Returns:
        A themed go.Figure with pie traces, or empty-state figure.
    """
    fig = build_chart(df, ERROR_RATIO_SPEC)
    _set_pie_text_details(fig)
    fig = apply_compact_chart_layout(
        fig,
        margin=_PIE_MARGIN,
        legend=_PIE_LEGEND,
    )
    return fig


def build_error_by_screener(df: pd.DataFrame) -> go.Figure:
    """Render Intervention per Screener Type.

    Args:
        df: Transformed DataFrame

    Returns:
        A themed go.Figure with stacked_bar traces, or empty-state figure.
    """
    fig = build_chart(df, ERROR_BY_SCREENER_SPEC)
    _set_bar_textposition_inside(fig)
    fig = apply_compact_chart_layout(
        fig,
        margin=_RIGHT_LEGEND_MARGIN,
        legend=_RIGHT_LEGEND,
    )
    return fig


def build_user_breakdown(df: pd.DataFrame) -> go.Figure:
    """Render User Intervention Breakdown.

    Args:
        df: Transformed DataFrame

    Returns:
        A themed go.Figure with bar traces, or empty-state figure.
    """
    fig = build_chart(df, USER_BREAKDOWN_SPEC)
    fig = apply_compact_chart_layout(
        fig,
        margin=_SIMPLE_BAR_MARGIN,
    )
    return fig


def build_hamm_breakdown(df: pd.DataFrame) -> go.Figure:
    """Render HAMM Intervention Breakdown.

    Args:
        df: Transformed DataFrame

    Returns:
        A themed go.Figure with bar traces, or empty-state figure.
    """
    fig = build_chart(df, BREAKDOWN_SPEC)
    fig = apply_compact_chart_layout(
        fig,
        margin=_SIMPLE_BAR_MARGIN,
    )
    return fig


def build_metadata_original_language(df: pd.DataFrame) -> go.Figure:
    """Render Original Language.

    Args:
        df: Transformed DataFrame

    Returns:
        A themed go.Figure with pie traces, or empty-state figure.
    """
    fig = build_chart(df, METADATA_ORIGINAL_LANGUAGE_SPEC)
    _set_pie_text_details(fig)
    fig = apply_compact_chart_layout(
        fig,
        margin=_PIE_MARGIN,
        legend=_PIE_LEGEND,
    )
    return fig


def build_metadata_dialogue(df: pd.DataFrame) -> go.Figure:
    """Render Was dialogue Provided?.

    Args:
        df: Transformed DataFrame

    Returns:
        A themed go.Figure with stacked_bar traces, or empty-state figure.
    """
    fig = build_chart(df, METADATA_DIALOGUE_SPEC)
    _set_bar_textposition_inside(fig)
    fig = apply_compact_chart_layout(
        fig,
        margin=_RIGHT_LEGEND_MARGIN,
        legend=_RIGHT_LEGEND,
    )
    return fig


def build_metadata_genre(df: pd.DataFrame) -> go.Figure:
    """Render Genre.

    Args:
        df: Transformed DataFrame

    Returns:
        A themed go.Figure with bar traces, or empty-state figure.
    """
    fig = build_chart(df, METADATA_GENRE_SPEC)
    fig = apply_compact_chart_layout(
        fig,
        margin=_SIMPLE_BAR_MARGIN,
    )
    # Genre chart has no legend
    fig.update_layout(showlegend=False)
    return fig


# Aliases for import compatibility
build_error_ratio_chart = build_error_ratio
build_error_by_screener_chart = build_error_by_screener
build_user_breakdown_chart = build_user_breakdown
build_hamm_breakdown_chart = build_hamm_breakdown
build_original_language_chart = build_metadata_original_language
build_dialogue_chart = build_metadata_dialogue
build_genre_chart = build_metadata_genre
