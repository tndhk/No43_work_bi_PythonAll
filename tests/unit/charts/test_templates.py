"""Tests for chart templates."""
import pytest
import pandas as pd
from dash import html
import plotly.graph_objects as go
from src.charts.templates import (
    get_chart_template,
    get_all_chart_types,
    CHART_TEMPLATES,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample DataFrame for chart testing."""
    return pd.DataFrame({
        "category": ["A", "B", "C", "A", "B"],
        "amount": [100.0, 200.0, 300.0, 150.0, 250.0],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]),
    })


def test_get_all_chart_types():
    """Test: get_all_chart_types returns all chart type identifiers."""
    chart_types = get_all_chart_types()
    assert len(chart_types) == 6
    assert "summary-number" in chart_types
    assert "bar" in chart_types
    assert "line" in chart_types
    assert "pie" in chart_types
    assert "table" in chart_types
    assert "pivot" in chart_types


def test_get_chart_template_existing():
    """Test: get_chart_template returns template for existing type."""
    template = get_chart_template("bar")
    assert "name" in template
    assert "description" in template
    assert "render" in template
    assert callable(template["render"])


def test_get_chart_template_default():
    """Test: get_chart_template returns table template for unknown type."""
    template = get_chart_template("unknown-type")
    assert template == CHART_TEMPLATES["table"]


def test_render_summary_number(sample_df):
    """Test: Summary number template renders correctly."""
    template = get_chart_template("summary-number")
    result = template["render"](
        dataset=sample_df,
        filters=None,
        params={"value_column": "amount", "agg_func": "sum"},
    )

    assert isinstance(result, html.Div)


def test_render_summary_number_default_params(sample_df):
    """Test: Summary number template uses default parameters."""
    template = get_chart_template("summary-number")
    result = template["render"](
        dataset=sample_df,
        filters=None,
        params=None,
    )

    assert isinstance(result, html.Div)


def test_render_bar_chart(sample_df):
    """Test: Bar chart template renders correctly."""
    template = get_chart_template("bar")
    result = template["render"](
        dataset=sample_df,
        filters=None,
        params={"x_column": "category", "y_column": "amount"},
    )

    assert isinstance(result, go.Figure)


def test_render_line_chart(sample_df):
    """Test: Line chart template renders correctly."""
    template = get_chart_template("line")
    result = template["render"](
        dataset=sample_df,
        filters=None,
        params={"x_column": "date", "y_column": "amount"},
    )

    assert isinstance(result, go.Figure)


def test_render_pie_chart(sample_df):
    """Test: Pie chart template renders correctly."""
    template = get_chart_template("pie")
    result = template["render"](
        dataset=sample_df,
        filters=None,
        params={"names_column": "category", "values_column": "amount"},
    )

    assert isinstance(result, go.Figure)


def test_render_table(sample_df):
    """Test: Table template renders correctly."""
    template = get_chart_template("table")
    result = template["render"](
        dataset=sample_df,
        filters=None,
        params=None,
    )

    assert isinstance(result, html.Div)


def test_render_pivot_table(sample_df):
    """Test: Pivot table template renders correctly."""
    template = get_chart_template("pivot")
    result = template["render"](
        dataset=sample_df,
        filters=None,
        params={
            "index_column": "category",
            "values_column": "amount",
            "agg_func": "sum",
        },
    )

    assert isinstance(result, html.Div)


def test_render_empty_dataframe():
    """Test: Templates handle empty DataFrame."""
    empty_df = pd.DataFrame()

    template = get_chart_template("table")
    result = template["render"](
        dataset=empty_df,
        filters=None,
        params=None,
    )

    assert isinstance(result, html.Div)
