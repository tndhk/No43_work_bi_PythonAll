"""Layout callbacks for authentication-based routing."""
from dash import Input, Output, html, page_container, dcc
from flask_login import current_user
from src.components.sidebar import create_sidebar
from src.auth.login_layout import create_login_layout


def register_layout_callbacks(app):
    """Register layout callbacks for authentication routing.
    
    Args:
        app: Dash app instance
    """
    @app.callback(
        Output("main-content", "children"),
        Input("main-location", "pathname"),
        prevent_initial_call=False,
    )
    def update_layout(pathname):
        """Update layout based on authentication status.
        
        Args:
            pathname: Current URL pathname
            
        Returns:
            Login page if not authenticated, main layout otherwise
        """
        # Check if user is authenticated
        if not current_user.is_authenticated:
            # Show login page
            return create_login_layout()
        
        # User is authenticated - show main dashboard layout
        return html.Div([
            dcc.Location(id="logout-location", refresh=True),
            create_sidebar(),
            html.Div([
                page_container,
            ], className="main-content"),
        ])
