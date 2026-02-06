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
            html.H6(title, className="card-subtitle mb-2 text-muted"),
            html.H2(
                str(value),
                className="card-title mb-1",
                style={"fontSize": "2.5rem", "fontWeight": "700"},
            ),
            html.P(subtitle, className="card-text text-muted") if subtitle else None,
        ]),
    ], className="mb-3", style={"height": "100%"})

