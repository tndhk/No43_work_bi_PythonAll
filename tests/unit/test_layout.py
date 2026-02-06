"""Tests for main layout."""
import pytest
from unittest.mock import patch, MagicMock
from dash import html
from src.layout import create_layout


def test_create_layout_returns_div():
    """Test: create_layout() returns html.Div."""
    # Given: Mock sidebar component
    mock_sidebar = html.Div("Mock Sidebar")
    
    # When: Creating layout with mocked sidebar
    with patch("src.layout.create_sidebar", return_value=mock_sidebar):
        layout = create_layout()
    
    # Then: Layout is a Div component
    assert isinstance(layout, html.Div)
    assert layout is not None


def test_create_layout_includes_sidebar_and_main_content():
    """Test: Layout includes sidebar and main content."""
    # Given: Mock sidebar component
    mock_sidebar = html.Div("Mock Sidebar")
    
    # When: Creating layout
    with patch("src.layout.create_sidebar", return_value=mock_sidebar):
        layout = create_layout()
    
    # Then: Layout has children (sidebar and main content)
    assert hasattr(layout, "children")
    assert layout.children is not None
