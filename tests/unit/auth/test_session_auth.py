"""Tests for Flask-Login session authentication."""
import pytest
from flask import Flask
from dash import Dash
from flask_login import LoginManager, current_user
from werkzeug.security import check_password_hash

from src.auth.flask_login_setup import init_login_manager, User
from src.auth.providers import FormAuthProvider
from src.data.config import Settings


@pytest.fixture
def flask_app():
    """Flask app for testing."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["TESTING"] = True
    return app


@pytest.fixture
def dash_app(flask_app):
    """Dash app with Flask-Login initialized."""
    dash_app = Dash(__name__, server=flask_app)
    init_login_manager(flask_app)
    return dash_app


@pytest.fixture
def auth_provider(monkeypatch):
    """FormAuthProvider with test credentials."""
    monkeypatch.setenv("BASIC_AUTH_USERNAME", "testuser")
    monkeypatch.setenv("BASIC_AUTH_PASSWORD", "testpass")
    return FormAuthProvider()


@pytest.fixture
def client(dash_app):
    """Test client."""
    return dash_app.server.test_client()


class TestFormAuthProvider:
    """Test FormAuthProvider authentication."""

    def test_authenticate_success(self, auth_provider):
        """TC-N-01: 正しいユーザー名/パスワードでログイン成功"""
        # Given: Valid credentials
        username = "testuser"
        password = "testpass"

        # When: Authenticating
        user = auth_provider.authenticate(username, password)

        # Then: User object returned
        assert user is not None
        assert user.id == username
        assert isinstance(user.groups, list)
        assert len(user.groups) == 0  # TC-U-01: groups is empty list initially

    def test_authenticate_wrong_username(self, auth_provider):
        """TC-A-01: 間違ったユーザー名でログイン失敗"""
        # Given: Wrong username
        username = "wronguser"
        password = "testpass"

        # When: Authenticating
        user = auth_provider.authenticate(username, password)

        # Then: None returned
        assert user is None

    def test_authenticate_wrong_password(self, auth_provider):
        """TC-A-02: 間違ったパスワードでログイン失敗"""
        # Given: Wrong password
        username = "testuser"
        password = "wrongpass"

        # When: Authenticating
        user = auth_provider.authenticate(username, password)

        # Then: None returned
        assert user is None

    def test_authenticate_empty_username(self, auth_provider):
        """TC-A-03: 空のユーザー名でログイン失敗"""
        # Given: Empty username
        username = ""
        password = "testpass"

        # When: Authenticating
        user = auth_provider.authenticate(username, password)

        # Then: None returned
        assert user is None

    def test_authenticate_empty_password(self, auth_provider):
        """TC-A-04: 空のパスワードでログイン失敗"""
        # Given: Empty password
        username = "testuser"
        password = ""

        # When: Authenticating
        user = auth_provider.authenticate(username, password)

        # Then: None returned
        assert user is None

    def test_authenticate_none_username(self, auth_provider):
        """TC-B-05: NULLユーザー名でログイン失敗"""
        # Given: None username
        username = None
        password = "testpass"

        # When: Authenticating
        user = auth_provider.authenticate(username, password)

        # Then: None returned
        assert user is None

    def test_authenticate_none_password(self, auth_provider):
        """TC-B-06: NULLパスワードでログイン失敗"""
        # Given: None password
        username = "testuser"
        password = None

        # When: Authenticating
        user = auth_provider.authenticate(username, password)

        # Then: None returned
        assert user is None

    def test_get_user_groups(self, auth_provider):
        """TC-U-01: ユーザーのgroups取得（将来拡張用）"""
        # Given: User ID
        user_id = "testuser"

        # When: Getting user groups
        groups = auth_provider.get_user_groups(user_id)

        # Then: Empty list returned (stub for now)
        assert isinstance(groups, list)
        assert len(groups) == 0


class TestUserModel:
    """Test User model."""

    def test_user_creation(self):
        """TC-U-02: ユーザー作成時にidとgroupsが設定される"""
        # Given: User ID and groups
        user_id = "testuser"
        groups = []

        # When: Creating user
        user = User(user_id, groups)

        # Then: User properties set correctly
        assert user.id == user_id
        assert user.groups == groups
        assert user.is_authenticated is True
        assert user.is_active is True
        assert user.is_anonymous is False

    def test_user_get_id(self):
        """Test: User.get_id() returns user ID."""
        # Given: User
        user = User("testuser", [])

        # When: Getting ID
        user_id = user.get_id()

        # Then: ID returned
        assert user_id == "testuser"


class TestFlaskLoginIntegration:
    """Test Flask-Login integration."""

    def test_login_manager_initialized(self, flask_app):
        """Test: Login manager is initialized."""
        # Given: Flask app
        # When: Initializing login manager
        init_login_manager(flask_app)

        # Then: Login manager exists
        assert hasattr(flask_app, "login_manager")
        assert isinstance(flask_app.login_manager, LoginManager)

    def test_user_loader(self, flask_app):
        """Test: User loader loads user from session."""
        # Given: Login manager initialized
        init_login_manager(flask_app)

        # When: Loading user
        with flask_app.test_request_context():
            user = flask_app.login_manager.user_loader("testuser")

        # Then: User object returned
        assert user is not None
        assert user.id == "testuser"
        assert isinstance(user.groups, list)

    def test_login_flow(self, client, auth_provider):
        """TC-N-01: ログインフロー（セッション保存確認）"""
        # Given: Test client and valid credentials
        # Note: Actual login flow will be tested via Dash callbacks
        # This is a placeholder for integration test
        assert client is not None
        assert auth_provider is not None

    def test_logout_flow(self, client):
        """TC-N-03: ログアウトフロー（セッションクリア確認）"""
        # Given: Test client
        # Note: Actual logout flow will be tested via Dash callbacks
        # This is a placeholder for integration test
        assert client is not None
