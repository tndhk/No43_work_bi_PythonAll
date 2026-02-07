"""Tests for Plotly theme."""
import pytest
import plotly.graph_objects as go
from src.charts.plotly_theme import apply_theme, PLOTLY_COLOR_PALETTE, PLOTLY_TEMPLATE


def test_plotly_color_palette():
    """Test: Color palette is defined correctly."""
    assert len(PLOTLY_COLOR_PALETTE) == 6
    assert "#2563eb" in PLOTLY_COLOR_PALETTE  # Blue (primary)
    assert "#059669" in PLOTLY_COLOR_PALETTE  # Emerald


def test_plotly_template_exists():
    """Test: Plotly template is defined."""
    assert PLOTLY_TEMPLATE is not None
    assert isinstance(PLOTLY_TEMPLATE, go.layout.Template)


def test_plotly_template_colors():
    """Test: Template uses correct color palette."""
    assert list(PLOTLY_TEMPLATE.layout.colorway) == PLOTLY_COLOR_PALETTE


def test_plotly_template_backgrounds():
    """Test: Template has transparent backgrounds."""
    assert PLOTLY_TEMPLATE.layout.paper_bgcolor == "rgba(0,0,0,0)"
    assert PLOTLY_TEMPLATE.layout.plot_bgcolor == "rgba(0,0,0,0)"


def test_plotly_template_fonts():
    """Test: Template uses correct fonts."""
    assert "Noto Sans JP" in PLOTLY_TEMPLATE.layout.font.family
    assert "Noto Sans JP" in PLOTLY_TEMPLATE.layout.title.font.family


def test_apply_theme():
    """Test: apply_theme function works correctly."""
    # Given: A Plotly figure
    fig = go.Figure(
        data=[go.Bar(x=["A", "B", "C"], y=[1, 2, 3])]
    )

    # When: Applying theme
    styled_fig = apply_theme(fig)

    # Then: Figure has template applied
    assert styled_fig.layout.template == PLOTLY_TEMPLATE


def test_apply_theme_preserves_data():
    """Test: apply_theme preserves figure data."""
    # Given: A Plotly figure with data
    original_data = [go.Bar(x=["A", "B"], y=[10, 20])]
    fig = go.Figure(data=original_data)

    # When: Applying theme
    styled_fig = apply_theme(fig)

    # Then: Data is preserved
    assert len(styled_fig.data) == 1
    assert styled_fig.data[0].x == ("A", "B")
    assert styled_fig.data[0].y == (10, 20)
