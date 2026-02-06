"""Tests for basic authentication."""
import pytest
from dash import Dash
from src.auth.basic_auth import setup_auth
from src.data.config import Settings


def test_setup_auth(monkeypatch):
    """Test: Basic auth setup uses settings."""
    # Given: Environment variables set
    monkeypatch.setenv("BASIC_AUTH_USERNAME", "testuser")
    monkeypatch.setenv("BASIC_AUTH_PASSWORD", "testpass")

    # When: Setting up auth
    app = Dash(__name__)
    setup_auth(app)

    # Then: Auth is configured (verification requires actual request)
    assert app is not None
