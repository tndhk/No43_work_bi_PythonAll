"""KPI card components."""
from typing import Optional, Union
import dash_bootstrap_components as dbc
from dash import html


def create_kpi_card(
    title: str,
    value: Union[str, int, float],
    subtitle: Optional[str] = None,
) -> dbc.Card:
    """
    Create a KPI display card.

    Args:
        title: Card title (e.g., "Total Sales")
        value: Value to display
        subtitle: Additional text (e.g., "+5% vs last month")

    Returns:
        dbc.Card component
    """
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="kpi-label mb-2"),
            html.Div(
                str(value),
                className="kpi-value mb-1",
            ),
            html.P(subtitle, className="kpi-subtitle") if subtitle else None,
        ]),
    ], className="kpi-card mb-3 animate-fade-in-up")


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

