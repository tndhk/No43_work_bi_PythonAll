"""Sidebar callbacks."""
from dash import Input, Output
from flask_login import logout_user


def register_sidebar_callbacks(app):
    """Register sidebar callbacks.
    
    Args:
        app: Dash app instance
    """
    @app.callback(
        Output("logout-location", "pathname"),
        Input("logout-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def handle_logout(n_clicks):
        """Handle logout button click.
        
        Args:
            n_clicks: Number of button clicks
            
        Returns:
            Redirect pathname to login page
        """
        if n_clicks:
            logout_user()
            return "/login"
        return None
