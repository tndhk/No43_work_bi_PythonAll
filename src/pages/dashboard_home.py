"""Dashboard home page."""
import dash
from dash import html, dcc, page_registry
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Home", order=0)


def layout():
    """Home page layout."""
    # Get all registered pages except home
    pages = [
        p for p in sorted(page_registry.values(), key=lambda p: p.get("order", 999))
        if p["path"] != "/"
    ]

    if not pages:
        # Empty state
        content = html.Div(
            html.P("ダッシュボードはまだありません", className="empty-state"),
            className="empty-state-container",
        )
    else:
        # Dashboard cards grid
        cards = []
        for page in pages:
            page_name = page.get("name", page["path"])
            page_description = page.get("description", "")
            page_path = page["path"]

            card = dbc.Card(
                [
                    dbc.CardBody([
                        html.H3(page_name, className="dashboard-card-title"),
                        html.P(page_description, className="dashboard-card-description") if page_description else None,
                        dcc.Link(
                            "開く →",
                            href=page_path,
                            className="dashboard-card-link",
                        ),
                    ]),
                ],
                className="dashboard-card",
            )
            cards.append(card)

        content = html.Div(cards, className="dashboard-grid")

    return html.Div([
        html.H1("BI Dashboard", className="mb-4 animate-fade-in-up"),
        content,
    ], className="page-container page-load")
