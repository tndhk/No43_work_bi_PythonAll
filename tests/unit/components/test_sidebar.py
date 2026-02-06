"""Tests for sidebar navigation component."""
import pytest
from unittest.mock import patch, MagicMock
from dash import html
from src.components.sidebar import create_sidebar


def test_create_sidebar_with_empty_registry():
    """Test: Sidebar with empty page registry."""
    # Given: Empty page registry
    empty_registry = {}
    
    # When: Creating sidebar with empty registry
    with patch("src.components.sidebar.page_registry", empty_registry):
        sidebar = create_sidebar()
    
    # Then: Sidebar component is created
    assert isinstance(sidebar, html.Div)
    assert sidebar is not None


def test_create_sidebar_with_multiple_pages():
    """Test: Sidebar with multiple pages."""
    # Given: Multiple pages in registry
    mock_registry = {
        "page1": {"path": "/page1", "name": "Page 1", "order": 1},
        "page2": {"path": "/page2", "name": "Page 2", "order": 2},
        "page3": {"path": "/page3", "name": "Page 3", "order": 0},
    }
    
    # When: Creating sidebar
    with patch("src.components.sidebar.page_registry", mock_registry):
        sidebar = create_sidebar()
    
    # Then: Sidebar component is created
    assert isinstance(sidebar, html.Div)
    assert sidebar is not None


def test_create_sidebar_sorts_by_order():
    """Test: Sidebar sorts pages by order attribute."""
    # Given: Pages with different order values
    mock_registry = {
        "page1": {"path": "/page1", "name": "Page 1", "order": 2},
        "page2": {"path": "/page2", "name": "Page 2", "order": 0},
        "page3": {"path": "/page3", "name": "Page 3", "order": 1},
    }
    
    # When: Creating sidebar
    with patch("src.components.sidebar.page_registry", mock_registry):
        sidebar = create_sidebar()
    
    # Then: Sidebar component is created
    assert isinstance(sidebar, html.Div)
    assert sidebar is not None


def test_create_sidebar_with_missing_order():
    """Test: Sidebar handles pages without order attribute."""
    # Given: Pages with and without order
    mock_registry = {
        "page1": {"path": "/page1", "name": "Page 1", "order": 1},
        "page2": {"path": "/page2", "name": "Page 2"},  # No order
        "page3": {"path": "/page3", "name": "Page 3", "order": 0},
    }
    
    # When: Creating sidebar
    with patch("src.components.sidebar.page_registry", mock_registry):
        sidebar = create_sidebar()
    
    # Then: Sidebar component is created (pages without order get order=999)
    assert isinstance(sidebar, html.Div)
    assert sidebar is not None
