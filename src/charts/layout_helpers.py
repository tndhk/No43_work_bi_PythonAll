"""Shared layout helpers for Plotly figure customization.

This module provides reusable layout functions for common chart styling patterns
across dashboard pages, eliminating duplication and ensuring consistent appearance.
"""
from __future__ import annotations

import plotly.graph_objects as go


def apply_compact_chart_layout(
    fig: go.Figure,
    *,
    margin: dict[str, int],
    legend: dict | None = None,
) -> go.Figure:
    """Apply compact layout tweaks for charts displayed in cards.

    This function is designed for charts that are rendered inside dbc.Card components
    where the card header already displays the title. It removes the figure's built-in
    title, suppresses axis titles, and applies uniform text settings for a clean,
    space-efficient appearance.

    Args:
        fig: The Plotly Figure to modify.
        margin: Dictionary of margin values (e.g., {"l": 40, "r": 40, "t": 20, "b": 40}).
        legend: Optional legend configuration dict to override defaults.

    Returns:
        The modified Figure with updated layout.

    Example:
        >>> fig = go.Figure(data=[...])
        >>> fig = apply_compact_chart_layout(
        ...     fig,
        ...     margin={"l": 40, "r": 40, "t": 20, "b": 40},
        ...     legend={"orientation": "h", "y": -0.2}
        ... )
    """
    layout_kwargs: dict = {
        "title": {"text": None},
        "margin": margin,
        "xaxis_title": "",
        "yaxis_title": "",
        "uniformtext_minsize": 11,
        "uniformtext_mode": "hide",
    }
    if legend is not None:
        layout_kwargs["legend"] = legend
    fig.update_layout(**layout_kwargs)
    return fig
