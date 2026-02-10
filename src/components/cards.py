"""KPI card and shared chart/table card components."""
from typing import Any, Optional, Union
import dash_bootstrap_components as dbc
from dash import dcc, html


# Default config for dcc.Graph in chart cards
DEFAULT_GRAPH_CONFIG = {"displayModeBar": False, "responsive": True}


def create_chart_card(
    title: str,
    chart_id: str,
    *,
    card_class: Optional[str] = None,
    body_class: Optional[str] = None,
    graph_class: Optional[str] = None,
    graph_config: Optional[dict[str, Any]] = None,
) -> dbc.Card:
    """Create a card containing a chart with standard header/body/classes.

    Args:
        title: Card header text.
        chart_id: Dash component id for dcc.Graph.
        card_class: Card className (default: chart-density-card).
        body_class: CardBody className (default: p-1).
        graph_class: dcc.Graph className (default: chart-density-graph).
        graph_config: dcc.Graph config (default: displayModeBar=False, responsive=True).

    Returns:
        dbc.Card with CardHeader, CardBody, and dcc.Graph.
    """
    card_class = card_class or "chart-density-card"
    body_class = body_class or "p-1"
    graph_class = graph_class or "chart-density-graph"
    graph_config = graph_config if graph_config is not None else DEFAULT_GRAPH_CONFIG

    return dbc.Card([
        dbc.CardHeader(title, className="card-header"),
        dbc.CardBody([
            dcc.Graph(
                id=chart_id,
                className=graph_class,
                config=graph_config,
            ),
        ], className=body_class),
    ], className=card_class)


def create_table_card(
    title: str,
    table_id: str,
    *,
    card_class: Optional[str] = None,
    body_class: Optional[str] = None,
    header_id: Optional[str] = None,
) -> dbc.Card:
    """Create a card containing a table container with standard header/body/classes.

    Args:
        title: Card header text (or placeholder when header_id is set).
        table_id: Dash component id for the table container (html.Div).
        card_class: Card className (default: standard card styling).
        body_class: CardBody className (default: p-1).
        header_id: Optional id for CardHeader (for dynamic title from callbacks).

    Returns:
        dbc.Card with CardHeader, CardBody, and html.Div table container.
    """
    body_class = body_class or "p-1"
    header = dbc.CardHeader(title, className="card-header", id=header_id) if header_id else dbc.CardHeader(title, className="card-header")

    return dbc.Card([
        header,
        dbc.CardBody([
            html.Div(id=table_id),
        ], className=body_class),
    ], className=card_class or "")


def create_kpi_card(
    title: str,
    value: Union[str, int, float],
    subtitle: Optional[str] = None,
    bg_color: Optional[str] = None,
    accent_color: Optional[str] = None,
) -> dbc.Card:
    """
    Create a KPI display card.

    Args:
        title: Card title (e.g., "Total Sales")
        value: Value to display
        subtitle: Additional text (e.g., "+5% vs last month")
        bg_color: Custom background color (e.g., "#f0f0f0")
        accent_color: Top border accent color (e.g., "#007bff")

    Returns:
        dbc.Card component
    """
    # Build style dict based on provided colors
    style = {}
    if bg_color:
        style["backgroundColor"] = bg_color
    if accent_color:
        style["borderTop"] = f"4px solid {accent_color}"

    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="kpi-label mb-2"),
            html.Div(
                str(value),
                className="kpi-value mb-1",
            ),
            html.P(subtitle, className="kpi-subtitle") if subtitle else None,
        ]),
    ], className="kpi-card mb-3 animate-fade-in-up", style=style if style else None)


def create_kpi_card_with_delta(
    title: str,
    value: Union[str, int, float],
    delta: float,
    delta_suffix: str = "%",
    delta_label: Optional[str] = None,
    positive_is_good: bool = True,
) -> dbc.Card:
    """
    Create a KPI card with delta (change) indicator.

    Args:
        title: Card title (e.g., "Total Sales")
        value: Value to display
        delta: Change value (e.g., 5.2 for +5.2%)
        delta_suffix: Suffix for delta display (default "%")
        delta_label: Optional label for delta (e.g., "vs last month")
        positive_is_good: If True, positive delta is styled as positive (green).
                          If False, positive delta is styled as negative (red).

    Returns:
        dbc.Card component with delta indicator
    """
    # Determine delta color and icon
    if delta > 0:
        delta_class = "text-success" if positive_is_good else "text-danger"
        delta_icon = "↑" if positive_is_good else "↓"
    elif delta < 0:
        delta_class = "text-danger" if positive_is_good else "text-success"
        delta_icon = "↓" if positive_is_good else "↑"
    else:
        delta_class = "text-muted"
        delta_icon = "→"

    delta_sign = "+" if delta > 0 else ""
    delta_text = f"{delta_icon} {delta_sign}{delta:.1f}{delta_suffix}"
    
    if delta_label:
        delta_text = f"{delta_text} {delta_label}"

    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="kpi-label mb-2"),
            html.Div(
                str(value),
                className="kpi-value mb-1",
            ),
            html.P(
                delta_text,
                className=f"kpi-subtitle {delta_class} mb-0",
            ),
        ]),
    ], className="kpi-card mb-3 animate-fade-in-up")

