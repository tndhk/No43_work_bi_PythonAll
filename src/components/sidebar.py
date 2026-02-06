"""Sidebar navigation component."""
from dash import html, page_registry
import dash_bootstrap_components as dbc


def create_sidebar() -> html.Div:
    """
    Create sidebar navigation from dash.page_registry.

    Returns:
        Sidebar Dash component
    """
    # Get all registered pages and sort by order
    pages = sorted(
        page_registry.values(),
        key=lambda p: p.get("order", 999),
    )

    # Create navigation links
    nav_links = []
    for page in pages:
        nav_links.append(
            dbc.NavLink(
                page.get("name", page["path"]),
                href=page["path"],
                active="exact",
            )
        )

    return html.Div([
        html.Div([
            html.H4("BI Dashboard", className="mb-4"),
            dbc.Nav(nav_links, vertical=True, pills=True),
        ], style={
            "padding": "20px",
        }),
    ], style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "width": "250px",
        "height": "100vh",
        "backgroundColor": "#f8f9fa",
        "borderRight": "1px solid #dee2e6",
        "overflowY": "auto",
    })
