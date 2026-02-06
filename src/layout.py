from dash import html, dcc


def create_layout() -> html.Div:
    """Create main layout container.
    
    Actual content is determined by layout_callbacks based on authentication.
    """
    return html.Div([
        dcc.Location(id="main-location", refresh=True),
        html.Div(id="main-content"),
    ])
