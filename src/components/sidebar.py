"""Sidebar navigation component."""
from dash import html, page_registry, dcc
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
            html.Div("BI Dashboard", className="sidebar-brand"),
            dbc.Nav(nav_links, vertical=True, pills=True, className="sidebar-nav"),
            html.Div([
                dbc.Button(
                    "Logout",
                    id="logout-button",
                    n_clicks=0,
                    className="sidebar-logout-button",
                    color="link",
                ),
            ], className="sidebar-footer"),
        ], className="sidebar-content"),
    ], className="sidebar")
