"""Chart templates for Plotly Dash (backward-compatible wrappers).

These functions preserve the legacy render_bar_chart / render_line_chart /
render_pie_chart API.  Internally they delegate to ``build_chart()`` via
an on-the-fly ``ChartSpec``.

New code should use ``build_chart()`` + ``ChartSpec`` directly.
"""
from __future__ import annotations

from typing import Any, Optional, Dict

import pandas as pd
import plotly.graph_objects as go

from src.charts.chart_builder import build_chart
from src.charts.specs import ChartSpec


def render_bar_chart(
    dataset: pd.DataFrame,
    filters: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> go.Figure:
    """Render a bar chart.

    Backward-compatible wrapper that delegates to ``build_chart()``.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (ignored, kept for API compat)
        params: Optional parameters:
            - x_column: X-axis column (default: first column)
            - y_column: Y-axis column (default: second column)

    Returns:
        Plotly Figure object
    """
    if params is None:
        params = {}

    x_column = params.get(
        "x_column", dataset.columns[0]
    )
    y_column = params.get(
        "y_column",
        dataset.columns[1] if len(dataset.columns) > 1 else dataset.columns[0],
    )

    spec = ChartSpec(
        title=f"{y_column} by {x_column}",
        chart_type="bar",
        x_column=x_column,
        y_columns=[y_column],
        show_legend=False,
        height=400,
    )
    return build_chart(dataset, spec)


def render_line_chart(
    dataset: pd.DataFrame,
    filters: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> go.Figure:
    """Render a line chart.

    Backward-compatible wrapper that delegates to ``build_chart()``.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (ignored, kept for API compat)
        params: Optional parameters:
            - x_column: X-axis column (default: first column)
            - y_column: Y-axis column (default: second column)

    Returns:
        Plotly Figure object
    """
    if params is None:
        params = {}

    x_column = params.get(
        "x_column", dataset.columns[0]
    )
    y_column = params.get(
        "y_column",
        dataset.columns[1] if len(dataset.columns) > 1 else dataset.columns[0],
    )

    spec = ChartSpec(
        title=f"{y_column} over {x_column}",
        chart_type="line",
        x_column=x_column,
        y_columns=[y_column],
        show_legend=False,
        height=400,
    )
    return build_chart(dataset, spec)


def render_pie_chart(
    dataset: pd.DataFrame,
    filters: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> go.Figure:
    """Render a pie chart.

    Backward-compatible wrapper that delegates to ``build_chart()``.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (ignored, kept for API compat)
        params: Optional parameters:
            - names_column: Category column (default: first column)
            - values_column: Values column (default: second column)

    Returns:
        Plotly Figure object
    """
    if params is None:
        params = {}

    names_column = params.get(
        "names_column", dataset.columns[0]
    )
    values_column = params.get(
        "values_column",
        dataset.columns[1] if len(dataset.columns) > 1 else dataset.columns[0],
    )

    spec = ChartSpec(
        title=f"{values_column} by {names_column}",
        chart_type="pie",
        x_column=names_column,
        y_columns=[values_column],
        height=400,
    )
    return build_chart(dataset, spec)
