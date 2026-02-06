"""Tests for dashboard home page."""
import pytest
from unittest.mock import patch
from dash import html
from src.pages.dashboard_home import layout


def test_layout_returns_div():
    """Test: layout() returns html.Div."""
    # Given: Layout function
    
    # When: Calling layout
    result = layout()
    
    # Then: Result is a Div component
    assert isinstance(result, html.Div)
    assert result is not None


def test_layout_shows_empty_state_when_no_pages():
    """Test: layout() shows empty state when no dashboard pages exist."""
    # Given: Only home page registered (no other dashboards)
    mock_registry = {
        "home": {"path": "/", "name": "Home", "order": 0},
    }
    
    # When: Calling layout with only home page
    with patch("src.pages.dashboard_home.page_registry", mock_registry):
        result = layout()
    
    # Then: Empty state message is shown
    assert isinstance(result, html.Div)
    result_str = str(result)
    assert "ダッシュボードはまだありません" in result_str
    assert "empty-state" in result_str


def test_layout_shows_dashboard_cards_when_pages_exist():
    """Test: layout() shows dashboard cards when pages exist."""
    # Given: Multiple pages registered
    mock_registry = {
        "home": {"path": "/", "name": "Home", "order": 0},
        "dashboard1": {"path": "/dashboard1", "name": "Dashboard 1", "order": 1, "description": "First dashboard"},
        "dashboard2": {"path": "/dashboard2", "name": "Dashboard 2", "order": 2, "description": "Second dashboard"},
    }
    
    # When: Calling layout
    with patch("src.pages.dashboard_home.page_registry", mock_registry):
        result = layout()
    
    # Then: Dashboard cards are shown
    assert isinstance(result, html.Div)
    result_str = str(result)
    assert "dashboard-grid" in result_str
    assert "Dashboard 1" in result_str
    assert "Dashboard 2" in result_str
    assert "First dashboard" in result_str
    assert "Second dashboard" in result_str


def test_layout_excludes_home_page_from_list():
    """Test: layout() excludes home page itself from dashboard list."""
    # Given: Home page and other pages registered
    mock_registry = {
        "home": {"path": "/", "name": "Home", "order": 0},
        "dashboard1": {"path": "/dashboard1", "name": "Dashboard 1", "order": 1},
    }
    
    # When: Calling layout
    with patch("src.pages.dashboard_home.page_registry", mock_registry):
        result = layout()
    
    # Then: Home page path "/" is not in dashboard cards
    result_str = str(result)
    # Dashboard1 link should appear
    assert "/dashboard1" in result_str
    # Home page link with path "/" should not appear as a card (only in H1 title)
    assert 'href="/"' not in result_str
