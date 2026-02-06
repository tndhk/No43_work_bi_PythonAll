"""Login page layout."""
from dash import html, dcc
import dash_bootstrap_components as dbc
from src.data.config import settings


def create_login_layout() -> html.Div:
    """Create login page layout.
    
    Returns:
        Login page Dash component
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H1(
                                        "BI Dashboard",
                                        className="login-brand",
                                    ),
                                    html.P(
                                        "Sign in to access your dashboards",
                                        className="login-subtitle",
                                    ),
                                ],
                                className="login-header",
                            ),
                            html.Div(
                                [
                                    dbc.Input(
                                        id="login-username",
                                        type="text",
                                        placeholder="Username",
                                        className="login-input",
                                        autoComplete="username",
                                        value=settings.basic_auth_username,
                                    ),
                                    dbc.Input(
                                        id="login-password",
                                        type="password",
                                        placeholder="Password",
                                        className="login-input",
                                        autoComplete="current-password",
                                        value=settings.basic_auth_password,
                                    ),
                                    html.Div(
                                        id="login-error",
                                        className="login-error",
                                    ),
                                    dbc.Button(
                                        "Sign In",
                                        id="login-submit",
                                        n_clicks=0,
                                        className="login-button",
                                        type="submit",
                                    ),
                                ],
                                className="login-form",
                            ),
                        ],
                        className="login-card",
                    ),
                ],
                className="login-container",
            ),
            # Store for redirect URL after login
            dcc.Location(id="login-location", refresh=True),
            dcc.Store(id="login-redirect-store", data="/"),
        ],
        className="login-page",
    )
