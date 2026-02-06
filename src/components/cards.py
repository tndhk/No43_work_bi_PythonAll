"""KPI card components."""
import dash_bootstrap_components as dbc
from dash import html


def create_kpi_card(
    title: str,
    value: str | int | float,
    subtitle: str | None = None,
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

