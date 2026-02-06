from dash import html, page_container
from src.components.sidebar import create_sidebar


def create_layout() -> html.Div:
    """Create main layout with sidebar and page container."""
    return html.Div([
        create_sidebar(),
        html.Div([
            page_container,
        ], className="main-content"),
    ])
