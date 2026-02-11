"""Layout callbacks for authentication-based routing."""
from dash import Input, Output, html, page_container, dcc
from flask_login import current_user
from src.components.chat_panel import create_chat_panel, create_chat_toggle_button
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
            ], id="page-content", className="main-content"),
            # Chat components
            create_chat_panel(),
            create_chat_toggle_button(),
            # Chat state stores
            dcc.Store(id="chat-session-store", storage_type="memory", data=[]),
            dcc.Store(id="chat-context-store", storage_type="memory", data={}),
            dcc.Store(id="chat-panel-state", storage_type="memory", data=False),
            dcc.Store(id="chat-filter-state-cursor", storage_type="memory", data={}),
            dcc.Store(id="chat-filter-state-hamm", storage_type="memory", data={}),
            dcc.Store(id="chat-filter-state-apac", storage_type="memory", data={}),
        ])
