"""Tests for Cursor Usage chart builders module.

TDD RED phase: These tests define the expected chart layout properties
(margins, title suppression, trace attributes) for the chart design
improvement. The implementation has not been updated yet, so these tests
MUST fail.
"""
import pandas as pd
import pytest
import plotly.graph_objects as go


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def cost_trend_df() -> pd.DataFrame:
    """Minimal DataFrame for build_daily_cost_trend (already aggregated)."""
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-06-01", "2024-06-02", "2024-06-03"]),
            "Cost": [12.50, 8.30, 15.00],
        }
    )


@pytest.fixture()
def token_efficiency_df() -> pd.DataFrame:
    """Minimal DataFrame for build_token_efficiency_chart."""
    return pd.DataFrame(
        {
            "Model": ["gpt-4", "claude-3"],
            "Total Tokens": [50000, 80000],
            "Cost": [10.0, 5.0],
        }
    )


@pytest.fixture()
def model_distribution_df() -> pd.DataFrame:
    """Minimal DataFrame for build_model_distribution_chart."""
    return pd.DataFrame(
        {
            "Model": ["gpt-4", "claude-3", "gemini-pro"],
            "Cost": [20.0, 15.0, 10.0],
        }
    )


# ---------------------------------------------------------------------------
# build_daily_cost_trend tests
# ---------------------------------------------------------------------------

class TestBuildDailyCostTrend:
    """build_daily_cost_trend must produce a figure with compact layout."""

    def test_returns_figure(self, cost_trend_df):
        from src.pages.cursor_usage._chart_builders import build_daily_cost_trend

        fig = build_daily_cost_trend(cost_trend_df)
        assert isinstance(fig, go.Figure)

    def test_title_is_none(self, cost_trend_df):
        """Chart title should be suppressed (displayed via CardHeader instead)."""
        from src.pages.cursor_usage._chart_builders import build_daily_cost_trend

        fig = build_daily_cost_trend(cost_trend_df)
        assert fig.layout.title.text is None

    def test_margin_top(self, cost_trend_df):
        from src.pages.cursor_usage._chart_builders import build_daily_cost_trend

        fig = build_daily_cost_trend(cost_trend_df)
        assert fig.layout.margin.t == 8

    def test_margin_left(self, cost_trend_df):
        from src.pages.cursor_usage._chart_builders import build_daily_cost_trend

        fig = build_daily_cost_trend(cost_trend_df)
        assert fig.layout.margin.l == 48

    def test_margin_right(self, cost_trend_df):
        from src.pages.cursor_usage._chart_builders import build_daily_cost_trend

        fig = build_daily_cost_trend(cost_trend_df)
        assert fig.layout.margin.r == 16

    def test_margin_bottom(self, cost_trend_df):
        from src.pages.cursor_usage._chart_builders import build_daily_cost_trend

        fig = build_daily_cost_trend(cost_trend_df)
        assert fig.layout.margin.b == 40


# ---------------------------------------------------------------------------
# build_token_efficiency_chart tests
# ---------------------------------------------------------------------------

class TestBuildTokenEfficiencyChart:
    """build_token_efficiency_chart must produce a figure with compact layout."""

    def test_returns_figure(self, token_efficiency_df):
        from src.pages.cursor_usage._chart_builders import build_token_efficiency_chart

        fig = build_token_efficiency_chart(token_efficiency_df)
        assert isinstance(fig, go.Figure)

    def test_title_is_none(self, token_efficiency_df):
        """Chart title should be suppressed (displayed via CardHeader instead)."""
        from src.pages.cursor_usage._chart_builders import build_token_efficiency_chart

        fig = build_token_efficiency_chart(token_efficiency_df)
        assert fig.layout.title.text is None

    def test_margin_top(self, token_efficiency_df):
        from src.pages.cursor_usage._chart_builders import build_token_efficiency_chart

        fig = build_token_efficiency_chart(token_efficiency_df)
        assert fig.layout.margin.t == 8

    def test_margin_left(self, token_efficiency_df):
        from src.pages.cursor_usage._chart_builders import build_token_efficiency_chart

        fig = build_token_efficiency_chart(token_efficiency_df)
        assert fig.layout.margin.l == 24

    def test_margin_right(self, token_efficiency_df):
        from src.pages.cursor_usage._chart_builders import build_token_efficiency_chart

        fig = build_token_efficiency_chart(token_efficiency_df)
        assert fig.layout.margin.r == 8

    def test_margin_bottom(self, token_efficiency_df):
        from src.pages.cursor_usage._chart_builders import build_token_efficiency_chart

        fig = build_token_efficiency_chart(token_efficiency_df)
        assert fig.layout.margin.b == 44

    def test_bar_trace_textposition_inside(self, token_efficiency_df):
        """Bar traces should have textposition='inside' for compact data labels."""
        from src.pages.cursor_usage._chart_builders import build_token_efficiency_chart

        fig = build_token_efficiency_chart(token_efficiency_df)
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        assert len(bar_traces) >= 1, "Expected at least one Bar trace"
        for trace in bar_traces:
            assert trace.textposition == "inside"


# ---------------------------------------------------------------------------
# build_model_distribution_chart tests
# ---------------------------------------------------------------------------

class TestBuildModelDistributionChart:
    """build_model_distribution_chart must produce a figure with compact layout."""

    def test_returns_figure(self, model_distribution_df):
        from src.pages.cursor_usage._chart_builders import build_model_distribution_chart

        fig = build_model_distribution_chart(model_distribution_df)
        assert isinstance(fig, go.Figure)

    def test_title_is_none(self, model_distribution_df):
        """Chart title should be suppressed (displayed via CardHeader instead)."""
        from src.pages.cursor_usage._chart_builders import build_model_distribution_chart

        fig = build_model_distribution_chart(model_distribution_df)
        assert fig.layout.title.text is None

    def test_margin_top(self, model_distribution_df):
        from src.pages.cursor_usage._chart_builders import build_model_distribution_chart

        fig = build_model_distribution_chart(model_distribution_df)
        assert fig.layout.margin.t == 8

    def test_margin_left(self, model_distribution_df):
        from src.pages.cursor_usage._chart_builders import build_model_distribution_chart

        fig = build_model_distribution_chart(model_distribution_df)
        assert fig.layout.margin.l == 8

    def test_margin_right(self, model_distribution_df):
        from src.pages.cursor_usage._chart_builders import build_model_distribution_chart

        fig = build_model_distribution_chart(model_distribution_df)
        assert fig.layout.margin.r == 8

    def test_margin_bottom(self, model_distribution_df):
        from src.pages.cursor_usage._chart_builders import build_model_distribution_chart

        fig = build_model_distribution_chart(model_distribution_df)
        assert fig.layout.margin.b == 34

    def test_legend_orientation_horizontal(self, model_distribution_df):
        """Pie chart legend should be horizontal for space efficiency."""
        from src.pages.cursor_usage._chart_builders import build_model_distribution_chart

        fig = build_model_distribution_chart(model_distribution_df)
        assert fig.layout.legend.orientation == "h"

    def test_pie_trace_textinfo(self, model_distribution_df):
        """Pie trace should show label, value, and percent."""
        from src.pages.cursor_usage._chart_builders import build_model_distribution_chart

        fig = build_model_distribution_chart(model_distribution_df)
        pie_traces = [t for t in fig.data if isinstance(t, go.Pie)]
        assert len(pie_traces) >= 1, "Expected at least one Pie trace"
        for trace in pie_traces:
            assert trace.textinfo == "label+value+percent"

    def test_pie_trace_textposition_inside(self, model_distribution_df):
        """Pie trace should have textposition='inside'."""
        from src.pages.cursor_usage._chart_builders import build_model_distribution_chart

        fig = build_model_distribution_chart(model_distribution_df)
        pie_traces = [t for t in fig.data if isinstance(t, go.Pie)]
        assert len(pie_traces) >= 1, "Expected at least one Pie trace"
        for trace in pie_traces:
            assert trace.textposition == "inside"
