"""Tests for Flask-Login session authentication."""
import pytest
from flask import Flask
from flask_login import LoginManager

from src.auth.flask_login_setup import init_login_manager, User
from src.auth.providers import FormAuthProvider


@pytest.fixture
def flask_app():
    """Flask app for testing."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["TESTING"] = True
    return app


@pytest.fixture
def auth_provider(monkeypatch):
    """FormAuthProvider with test credentials."""
    monkeypatch.setenv("BASIC_AUTH_USERNAME", "testuser")
    monkeypatch.setenv("BASIC_AUTH_PASSWORD", "testpass")
    return FormAuthProvider()


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
            user = flask_app.login_manager._user_callback("testuser")

        # Then: User object returned
        assert user is not None
        assert user.id == "testuser"
        assert isinstance(user.groups, list)
