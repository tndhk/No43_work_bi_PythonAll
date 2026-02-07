"""Tests for chart templates."""
import pytest
import pandas as pd
import plotly.graph_objects as go
from src.charts.templates import (
    render_bar_chart,
    render_line_chart,
    render_pie_chart,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample DataFrame for chart testing."""
    return pd.DataFrame({
        "category": ["A", "B", "C", "A", "B"],
        "amount": [100.0, 200.0, 300.0, 150.0, 250.0],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]),
    })


def test_render_bar_chart(sample_df):
    """Test: Bar chart template renders correctly."""
    result = render_bar_chart(
        dataset=sample_df,
        filters=None,
        params={"x_column": "category", "y_column": "amount"},
    )

    assert isinstance(result, go.Figure)


def test_render_bar_chart_default_params(sample_df):
    """Test: Bar chart uses default parameters when none provided."""
    result = render_bar_chart(
        dataset=sample_df,
        filters=None,
        params=None,
    )

    assert isinstance(result, go.Figure)


def test_render_line_chart(sample_df):
    """Test: Line chart template renders correctly."""
    result = render_line_chart(
        dataset=sample_df,
        filters=None,
        params={"x_column": "date", "y_column": "amount"},
    )

    assert isinstance(result, go.Figure)


def test_render_line_chart_default_params(sample_df):
    """Test: Line chart uses default parameters when none provided."""
    result = render_line_chart(
        dataset=sample_df,
        filters=None,
        params=None,
    )

    assert isinstance(result, go.Figure)


def test_render_pie_chart(sample_df):
    """Test: Pie chart template renders correctly."""
    result = render_pie_chart(
        dataset=sample_df,
        filters=None,
        params={"names_column": "category", "values_column": "amount"},
    )

    assert isinstance(result, go.Figure)


def test_render_pie_chart_default_params(sample_df):
    """Test: Pie chart uses default parameters when none provided."""
    result = render_pie_chart(
        dataset=sample_df,
        filters=None,
        params=None,
    )

    assert isinstance(result, go.Figure)


def test_deleted_symbols_not_importable():
    """Test: Deleted functions and registry are no longer importable."""
    import importlib
    mod = importlib.import_module("src.charts.templates")

    assert not hasattr(mod, "render_summary_number")
    assert not hasattr(mod, "render_table")
    assert not hasattr(mod, "render_pivot_table")
    assert not hasattr(mod, "CHART_TEMPLATES")
    assert not hasattr(mod, "get_chart_template")
    assert not hasattr(mod, "get_all_chart_types")
