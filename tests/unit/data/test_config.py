"""Tests for configuration."""
import pytest
import os
from src.data.config import Settings


def test_settings_load_from_env(monkeypatch):
    """Test: Settings load from environment variables."""
    # Given: Environment variables set
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("S3_REGION", "us-east-1")
    monkeypatch.setenv("BASIC_AUTH_USERNAME", "testuser")
    monkeypatch.setenv("BASIC_AUTH_PASSWORD", "testpass")

    # When: Creating settings
    settings = Settings()

    # Then: Settings are loaded from environment
    assert settings.s3_bucket == "test-bucket"
    assert settings.s3_region == "us-east-1"
    assert settings.basic_auth_username == "testuser"
    assert settings.basic_auth_password == "testpass"


def test_settings_defaults():
    """Test: Settings use default values when env vars not set."""
    # Given: No environment variables set (using fresh Settings instance)
    # Note: This test assumes defaults from config.py
    settings = Settings()

    # Then: Default values are used
    assert settings.s3_bucket == "bi-datasets"
    assert settings.s3_region == "ap-northeast-1"
