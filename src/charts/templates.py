"""Chart templates for Plotly Dash."""
from typing import Any, Optional, Dict
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.charts.plotly_theme import apply_theme


def render_bar_chart(
    dataset: pd.DataFrame,
    filters: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> go.Figure:
    """Render a bar chart.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (not used in this template)
        params: Optional parameters:
            - x_column: X-axis column (default: first column)
            - y_column: Y-axis column (default: second column)

    Returns:
        Plotly Figure object
    """
    if params is None:
        params = {}

    x_column = params.get("x_column", dataset.columns[0])
    y_column = params.get("y_column", dataset.columns[1] if len(dataset.columns) > 1 else dataset.columns[0])

    fig = px.bar(
        dataset,
        x=x_column,
        y=y_column,
        title=f"{y_column} by {x_column}",
    )
    fig.update_layout(
        height=400,
        showlegend=False,
    )
    return apply_theme(fig)


def render_line_chart(
    dataset: pd.DataFrame,
    filters: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> go.Figure:
    """Render a line chart.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (not used in this template)
        params: Optional parameters:
            - x_column: X-axis column (default: first column)
            - y_column: Y-axis column (default: second column)

    Returns:
        Plotly Figure object
    """
    if params is None:
        params = {}

    x_column = params.get("x_column", dataset.columns[0])
    y_column = params.get("y_column", dataset.columns[1] if len(dataset.columns) > 1 else dataset.columns[0])

    fig = px.line(
        dataset,
        x=x_column,
        y=y_column,
        title=f"{y_column} over {x_column}",
    )
    fig.update_layout(
        height=400,
        showlegend=False,
    )
    return apply_theme(fig)


def render_pie_chart(
    dataset: pd.DataFrame,
    filters: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> go.Figure:
    """Render a pie chart.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (not used in this template)
        params: Optional parameters:
            - names_column: Category column (default: first column)
            - values_column: Values column (default: second column)

    Returns:
        Plotly Figure object
    """
    if params is None:
        params = {}

    names_column = params.get("names_column", dataset.columns[0])
    values_column = params.get("values_column", dataset.columns[1] if len(dataset.columns) > 1 else dataset.columns[0])

    fig = px.pie(
        dataset,
        names=names_column,
        values=values_column,
        title=f"{values_column} by {names_column}",
    )
    fig.update_layout(
        height=400,
    )
    return apply_theme(fig)
