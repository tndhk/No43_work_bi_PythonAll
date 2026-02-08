"""Shared chart builder: DataFrame + ChartSpec -> themed go.Figure.

Supports ``bar``, ``line``, ``pie``, and ``stacked_bar`` chart types.
``apply_theme()`` from ``plotly_theme`` is applied automatically.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.charts.empty_states import create_empty_figure
from src.charts.plotly_theme import apply_theme
from src.charts.specs import ChartSpec

_SUPPORTED_TYPES = {"bar", "line", "pie", "stacked_bar"}


def build_chart(df: pd.DataFrame, spec: ChartSpec) -> go.Figure:
    """Build a themed Plotly figure from a DataFrame and a ChartSpec.

    Args:
        df: Source data.  An empty DataFrame triggers the empty-state figure.
        spec: Declarative chart configuration.

    Returns:
        A ``go.Figure`` with the requested traces, layout, and theme.

    Raises:
        ValueError: If ``spec.chart_type`` is not one of the supported types.
    """
    if spec.chart_type not in _SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported chart_type '{spec.chart_type}'. "
            f"Supported: {sorted(_SUPPORTED_TYPES)}"
        )

    if len(df) == 0:
        fig = create_empty_figure(message="No data available", height=spec.height)
        fig.update_layout(title=dict(text=spec.title))
        return apply_theme(fig)

    fig = go.Figure()

    labels = spec.labels or {}
    color_map = spec.color_map or {}

    if spec.chart_type == "pie":
        _add_pie_trace(fig, df, spec, labels)
    elif spec.chart_type in ("bar", "stacked_bar"):
        _add_bar_traces(fig, df, spec, labels, color_map)
    elif spec.chart_type == "line":
        _add_line_traces(fig, df, spec, labels, color_map)

    # --- layout ------------------------------------------------------------
    barmode = spec.barmode
    if spec.chart_type == "stacked_bar":
        barmode = "stack"

    fig.update_layout(
        title=dict(text=spec.title),
        height=spec.height,
        showlegend=spec.show_legend,
        barmode=barmode,
    )

    return apply_theme(fig)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _add_bar_traces(
    fig: go.Figure,
    df: pd.DataFrame,
    spec: ChartSpec,
    labels: dict[str, str],
    color_map: dict[str, str],
) -> None:
    for y_col in spec.y_columns:
        trace_name = labels.get(y_col, y_col)
        marker_color = color_map.get(y_col)
        fig.add_trace(
            go.Bar(
                x=df[spec.x_column],
                y=df[y_col],
                name=trace_name,
                marker_color=marker_color,
            )
        )


def _add_line_traces(
    fig: go.Figure,
    df: pd.DataFrame,
    spec: ChartSpec,
    labels: dict[str, str],
    color_map: dict[str, str],
) -> None:
    for y_col in spec.y_columns:
        trace_name = labels.get(y_col, y_col)
        line_color = color_map.get(y_col)
        line_kwargs: dict = {}
        if line_color:
            line_kwargs["line"] = dict(color=line_color)
        fig.add_trace(
            go.Scatter(
                x=df[spec.x_column],
                y=df[y_col],
                mode="lines",
                name=trace_name,
                **line_kwargs,
            )
        )


def _add_pie_trace(
    fig: go.Figure,
    df: pd.DataFrame,
    spec: ChartSpec,
    labels: dict[str, str],
) -> None:
    y_col = spec.y_columns[0]
    fig.add_trace(
        go.Pie(
            labels=df[spec.x_column],
            values=df[y_col],
            name=labels.get(y_col, y_col),
        )
    )
