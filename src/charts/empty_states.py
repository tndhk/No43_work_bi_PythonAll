"""Factory functions for empty-state and error-state UI components.

These replace the duplicated go.Figure() + add_annotation() + update_layout()
pattern found across callback modules (cursor_usage, hamm_overview,
apac_dot_due_date, etc.).
"""
from __future__ import annotations

import plotly.graph_objects as go
from dash import html


def create_empty_figure(
    message: str = "No data available",
    height: int = 400,
) -> go.Figure:
    """Return a blank Plotly figure with a centered text annotation.

    Args:
        message: Text to display in the centre of the figure.
        height: Figure height in pixels.

    Returns:
        A ``go.Figure`` with no data traces and one annotation.
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
    )
    fig.update_layout(height=height)
    return fig


def create_empty_table(message: str = "No data available") -> html.P:
    """Return a Dash ``html.P`` placeholder for an empty table.

    Args:
        message: Text to display.

    Returns:
        A ``html.P`` component with ``className="text-muted"``.
    """
    return html.P(message, className="text-muted")


def create_error_figure(
    error: str,
    height: int = 400,
) -> go.Figure:
    """Return a blank Plotly figure with a red error annotation.

    Args:
        error: Error message to display.
        height: Figure height in pixels.

    Returns:
        A ``go.Figure`` with no data traces and one red annotation.
    """
    fig = go.Figure()
    fig.add_annotation(
        text=error,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(color="red"),
    )
    fig.update_layout(height=height)
    return fig
