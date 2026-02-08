"""Tests for the shared chart builder.

build_chart() converts a DataFrame + ChartSpec into a themed go.Figure.
It supports bar, line, pie, and stacked_bar chart types.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.charts.specs import ChartSpec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_spec(**overrides) -> ChartSpec:
    """Create a minimal ChartSpec with sensible defaults, merging overrides."""
    defaults = dict(
        title="Test Chart",
        chart_type="bar",
        x_column="category",
        y_columns=["value"],
    )
    defaults.update(overrides)
    return ChartSpec(**defaults)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "category": ["A", "B", "C"],
        "value": [10, 20, 30],
        "value2": [5, 15, 25],
    })


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

class TestImport:
    """build_chart can be imported."""

    def test_import(self):
        from src.charts.chart_builder import build_chart  # noqa: F401


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

class TestReturnType:
    """build_chart returns a go.Figure."""

    def test_returns_figure(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec()
        result = build_chart(_sample_df(), spec)
        assert isinstance(result, go.Figure)


# ---------------------------------------------------------------------------
# Chart types
# ---------------------------------------------------------------------------

class TestBarChart:
    """Bar chart creation."""

    def test_bar_chart_has_bar_traces(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(chart_type="bar")
        fig = build_chart(_sample_df(), spec)
        assert len(fig.data) >= 1
        assert fig.data[0].type == "bar"

    def test_bar_chart_with_multiple_y(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(chart_type="bar", y_columns=["value", "value2"])
        fig = build_chart(_sample_df(), spec)
        assert len(fig.data) == 2
        for trace in fig.data:
            assert trace.type == "bar"


class TestLineChart:
    """Line chart creation."""

    def test_line_chart_has_scatter_traces(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(chart_type="line")
        fig = build_chart(_sample_df(), spec)
        assert len(fig.data) >= 1
        assert fig.data[0].type == "scatter"

    def test_line_chart_with_multiple_y(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(chart_type="line", y_columns=["value", "value2"])
        fig = build_chart(_sample_df(), spec)
        assert len(fig.data) == 2


class TestPieChart:
    """Pie chart creation."""

    def test_pie_chart_has_pie_trace(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(chart_type="pie")
        fig = build_chart(_sample_df(), spec)
        assert len(fig.data) == 1
        assert fig.data[0].type == "pie"

    def test_pie_chart_uses_first_y_column(self):
        """Pie chart uses the first y_column as values."""
        from src.charts.chart_builder import build_chart

        spec = _make_spec(chart_type="pie", x_column="category", y_columns=["value"])
        fig = build_chart(_sample_df(), spec)
        # pie trace should have labels from x_column and values from first y_column
        assert list(fig.data[0].labels) == ["A", "B", "C"]
        assert list(fig.data[0].values) == [10, 20, 30]


class TestStackedBarChart:
    """Stacked bar chart creation."""

    def test_stacked_bar_sets_barmode_stack(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(chart_type="stacked_bar", y_columns=["value", "value2"])
        fig = build_chart(_sample_df(), spec)
        assert fig.layout.barmode == "stack"

    def test_stacked_bar_has_bar_traces(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(chart_type="stacked_bar", y_columns=["value", "value2"])
        fig = build_chart(_sample_df(), spec)
        for trace in fig.data:
            assert trace.type == "bar"


# ---------------------------------------------------------------------------
# Unsupported chart type
# ---------------------------------------------------------------------------

class TestUnsupportedChartType:
    """Unknown chart_type raises ValueError."""

    def test_raises_on_unknown_type(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(chart_type="radar")
        with pytest.raises(ValueError, match="radar"):
            build_chart(_sample_df(), spec)


# ---------------------------------------------------------------------------
# Theme application
# ---------------------------------------------------------------------------

class TestTheme:
    """apply_theme() is applied to every figure."""

    def test_template_is_applied(self):
        from src.charts.chart_builder import build_chart
        from src.charts.plotly_theme import PLOTLY_TEMPLATE

        spec = _make_spec()
        fig = build_chart(_sample_df(), spec)
        assert fig.layout.template == PLOTLY_TEMPLATE


# ---------------------------------------------------------------------------
# Layout configuration
# ---------------------------------------------------------------------------

class TestLayoutConfig:
    """Spec options are forwarded to the figure layout."""

    def test_title_set(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(title="Revenue Chart")
        fig = build_chart(_sample_df(), spec)
        assert fig.layout.title.text == "Revenue Chart"

    def test_height_set(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(height=600)
        fig = build_chart(_sample_df(), spec)
        assert fig.layout.height == 600

    def test_default_height_400(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec()
        fig = build_chart(_sample_df(), spec)
        assert fig.layout.height == 400

    def test_show_legend_true(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(show_legend=True)
        fig = build_chart(_sample_df(), spec)
        assert fig.layout.showlegend is True

    def test_show_legend_false(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(show_legend=False)
        fig = build_chart(_sample_df(), spec)
        assert fig.layout.showlegend is False

    def test_barmode_forwarded(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(barmode="group")
        fig = build_chart(_sample_df(), spec)
        assert fig.layout.barmode == "group"


# ---------------------------------------------------------------------------
# Color map
# ---------------------------------------------------------------------------

class TestColorMap:
    """color_map assigns colors to named traces."""

    def test_color_map_applied_to_bar(self):
        from src.charts.chart_builder import build_chart

        color_map = {"value": "#ff0000", "value2": "#00ff00"}
        spec = _make_spec(
            chart_type="bar",
            y_columns=["value", "value2"],
            color_map=color_map,
        )
        fig = build_chart(_sample_df(), spec)
        assert fig.data[0].marker.color == "#ff0000"
        assert fig.data[1].marker.color == "#00ff00"

    def test_color_map_applied_to_line(self):
        from src.charts.chart_builder import build_chart

        color_map = {"value": "#ff0000"}
        spec = _make_spec(
            chart_type="line",
            y_columns=["value"],
            color_map=color_map,
        )
        fig = build_chart(_sample_df(), spec)
        assert fig.data[0].line.color == "#ff0000"


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

class TestLabels:
    """labels dict is used for axis/trace display names."""

    def test_labels_applied_to_bar_trace_names(self):
        from src.charts.chart_builder import build_chart

        labels = {"value": "Revenue", "value2": "Cost"}
        spec = _make_spec(
            chart_type="bar",
            y_columns=["value", "value2"],
            labels=labels,
        )
        fig = build_chart(_sample_df(), spec)
        assert fig.data[0].name == "Revenue"
        assert fig.data[1].name == "Cost"

    def test_labels_not_provided_uses_column_name(self):
        from src.charts.chart_builder import build_chart

        spec = _make_spec(chart_type="bar", y_columns=["value"])
        fig = build_chart(_sample_df(), spec)
        assert fig.data[0].name == "value"


# ---------------------------------------------------------------------------
# Empty DataFrame
# ---------------------------------------------------------------------------

class TestEmptyDataFrame:
    """build_chart with an empty DataFrame returns an empty-state figure."""

    def test_empty_df_returns_figure(self):
        from src.charts.chart_builder import build_chart

        df = pd.DataFrame(columns=["category", "value"])
        spec = _make_spec()
        fig = build_chart(df, spec)
        assert isinstance(fig, go.Figure)

    def test_empty_df_has_annotation(self):
        from src.charts.chart_builder import build_chart

        df = pd.DataFrame(columns=["category", "value"])
        spec = _make_spec()
        fig = build_chart(df, spec)
        assert len(fig.layout.annotations) == 1
        assert "No data" in fig.layout.annotations[0].text
