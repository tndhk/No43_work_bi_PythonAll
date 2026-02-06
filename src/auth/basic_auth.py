import dash_auth
from dash import Dash
from src.data.config import settings


def setup_auth(app: Dash) -> None:
    """DashアプリにBasic認証を設定
    
    Args:
        app: Dashアプリインスタンス
    """
    valid_users = {
        settings.basic_auth_username: settings.basic_auth_password
    }
    dash_auth.BasicAuth(app, valid_users)
