"""Shared chart builder: DataFrame + ChartSpec -> themed go.Figure.

Supports ``bar``, ``line``, ``pie``, ``stacked_bar``, ``scatter``, and ``area`` chart types.
``apply_theme()`` from ``plotly_theme`` is applied automatically.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.charts.empty_states import create_empty_figure
from src.charts.plotly_theme import apply_theme
from src.charts.specs import ChartSpec

_SUPPORTED_TYPES = {"bar", "line", "pie", "stacked_bar", "scatter", "area", "horizontal_bar"}


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
    elif spec.chart_type in ("bar", "stacked_bar", "horizontal_bar"):
        _add_bar_traces(fig, df, spec, labels, color_map)
    elif spec.chart_type == "line":
        _add_line_traces(fig, df, spec, labels, color_map)
    elif spec.chart_type == "scatter":
        _add_scatter_traces(fig, df, spec, labels, color_map)
    elif spec.chart_type == "area":
        _add_area_traces(fig, df, spec, labels, color_map)

    # --- layout ------------------------------------------------------------
    barmode = spec.barmode
    if spec.chart_type == "stacked_bar":
        barmode = "stack"
    elif spec.chart_type == "horizontal_bar":
        # horizontal_bar is an alias for bar with orientation="h"
        barmode = barmode or "group"

    layout_kwargs: dict = {
        "title": dict(text=spec.title),
        "height": spec.height,
        "showlegend": spec.show_legend,
    }
    
    # Only set barmode for bar charts
    if spec.chart_type in ("bar", "stacked_bar", "horizontal_bar"):
        layout_kwargs["barmode"] = barmode

    fig.update_layout(**layout_kwargs)

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
        
        # Handle orientation: "h" swaps x and y
        # Also handle horizontal_bar chart type (alias for orientation="h")
        if spec.orientation == "h" or spec.chart_type == "horizontal_bar":
            x_data = df[y_col]
            y_data = df[spec.x_column]
        else:
            x_data = df[spec.x_column]
            y_data = df[y_col]
        
        trace_kwargs: dict = {
            "x": x_data,
            "y": y_data,
            "name": trace_name,
            "marker_color": marker_color,
        }
        
        # Add text template for data labels
        if spec.text_template:
            trace_kwargs["texttemplate"] = spec.text_template
            trace_kwargs["textposition"] = "outside"
        
        # Add hover template
        if spec.hover_template:
            trace_kwargs["hovertemplate"] = spec.hover_template
        
        fig.add_trace(go.Bar(**trace_kwargs))


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
        
        trace_kwargs: dict = {
            "x": df[spec.x_column],
            "y": df[y_col],
            "mode": "lines",
            "name": trace_name,
            **line_kwargs,
        }
        
        # Add text template for data labels
        if spec.text_template:
            trace_kwargs["texttemplate"] = spec.text_template
            trace_kwargs["mode"] = "lines+markers+text"
        
        # Add hover template
        if spec.hover_template:
            trace_kwargs["hovertemplate"] = spec.hover_template
        
        fig.add_trace(go.Scatter(**trace_kwargs))


def _add_pie_trace(
    fig: go.Figure,
    df: pd.DataFrame,
    spec: ChartSpec,
    labels: dict[str, str],
) -> None:
    y_col = spec.y_columns[0]
    
    trace_kwargs: dict = {
        "labels": df[spec.x_column],
        "values": df[y_col],
        "name": labels.get(y_col, y_col),
    }
    
    # Add text template for data labels (pie charts use textinfo)
    if spec.text_template:
        trace_kwargs["textinfo"] = "label+percent"
        trace_kwargs["texttemplate"] = spec.text_template
    
    # Add hover template
    if spec.hover_template:
        trace_kwargs["hovertemplate"] = spec.hover_template
    
    fig.add_trace(go.Pie(**trace_kwargs))


def _add_scatter_traces(
    fig: go.Figure,
    df: pd.DataFrame,
    spec: ChartSpec,
    labels: dict[str, str],
    color_map: dict[str, str],
) -> None:
    """Add scatter plot traces (markers only, no lines)."""
    for y_col in spec.y_columns:
        trace_name = labels.get(y_col, y_col)
        marker_color = color_map.get(y_col)
        
        trace_kwargs: dict = {
            "x": df[spec.x_column],
            "y": df[y_col],
            "mode": "markers",
            "name": trace_name,
        }
        
        if marker_color:
            trace_kwargs["marker"] = dict(color=marker_color)
        
        # Add text template for data labels
        if spec.text_template:
            trace_kwargs["texttemplate"] = spec.text_template
            trace_kwargs["mode"] = "markers+text"
        
        # Add hover template
        if spec.hover_template:
            trace_kwargs["hovertemplate"] = spec.hover_template
        
        fig.add_trace(go.Scatter(**trace_kwargs))


def _add_area_traces(
    fig: go.Figure,
    df: pd.DataFrame,
    spec: ChartSpec,
    labels: dict[str, str],
    color_map: dict[str, str],
) -> None:
    """Add area chart traces (filled line charts)."""
    for y_col in spec.y_columns:
        trace_name = labels.get(y_col, y_col)
        fill_color = color_map.get(y_col)
        
        trace_kwargs: dict = {
            "x": df[spec.x_column],
            "y": df[y_col],
            "mode": "lines",
            "name": trace_name,
            "fill": "tozeroy",  # Fill to zero
        }
        
        if fill_color:
            trace_kwargs["fillcolor"] = fill_color
            trace_kwargs["line"] = dict(color=fill_color)
        
        # Add text template for data labels
        if spec.text_template:
            trace_kwargs["texttemplate"] = spec.text_template
            trace_kwargs["mode"] = "lines+markers+text"
        
        # Add hover template
        if spec.hover_template:
            trace_kwargs["hovertemplate"] = spec.hover_template
        
        fig.add_trace(go.Scatter(**trace_kwargs))
