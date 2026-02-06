"""Login and logout callbacks."""
from dash import Input, Output, State, html, callback_context
from flask_login import login_user, logout_user

from src.auth.providers import get_auth_provider


def register_login_callbacks(app):
    """Register login and logout callbacks.
    
    Args:
        app: Dash app instance
    """
    @app.callback(
        [
            Output("login-error", "children"),
            Output("login-location", "pathname"),
        ],
        [
            Input("login-submit", "n_clicks"),
            Input("login-username", "n_submit"),
            Input("login-password", "n_submit"),
        ],
        [
            State("login-username", "value"),
            State("login-password", "value"),
            State("login-redirect-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def handle_login(n_clicks, username_submit, password_submit, username, password, redirect_url):
        """Handle login form submission.
        
        Args:
            n_clicks: Number of button clicks
            username_submit: Username input submit events
            password_submit: Password input submit events
            username: Username value
            password: Password value
            redirect_url: URL to redirect to after login
            
        Returns:
            Tuple of (error message, redirect pathname)
        """
        # Check if login was triggered
        ctx = callback_context
        if not ctx.triggered:
            return "", None

        # Get auth provider
        auth_provider = get_auth_provider()

        # Validate inputs
        if not username or not password:
            return html.Span("Username and password are required."), None

        # Authenticate user
        user = auth_provider.authenticate(username, password)
        if user is None:
            return html.Span("Invalid username or password."), None

        # Login user (store in Flask session)
        login_user(user, remember=True)

        # Redirect to dashboard or stored redirect URL
        redirect_path = redirect_url if redirect_url and redirect_url != "/login" else "/"
        return "", redirect_path
