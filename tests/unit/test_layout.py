"""Tests for main layout."""
import pytest
from dash import html, dcc
from src.layout import create_layout


def test_create_layout_returns_div():
    """Test: create_layout() returns html.Div."""
    # When: Creating layout
    layout = create_layout()

    # Then: Layout is a Div component
    assert isinstance(layout, html.Div)
    assert layout is not None


def test_create_layout_includes_location_and_main_content():
    """Test: Layout includes location and main content."""
    # When: Creating layout
    layout = create_layout()

    # Then: Layout has children (location and main content)
    assert hasattr(layout, "children")
    assert layout.children is not None
    assert len(layout.children) == 2
    assert isinstance(layout.children[0], dcc.Location)
    assert layout.children[0].id == "main-location"
    assert isinstance(layout.children[1], html.Div)
    assert layout.children[1].id == "main-content"
