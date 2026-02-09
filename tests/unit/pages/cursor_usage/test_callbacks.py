"""Tests for Cursor Usage callbacks module.

TDD Step 5b (RED->GREEN): Validates that update_dashboard uses
build_chart, build_table, and empty_states (shared infrastructure)
instead of the legacy render_* templates and inline go.Figure construction.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import plotly.graph_objects as go
from dash import html, dash_table


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

def _make_sample_df() -> pd.DataFrame:
    """Create a sample DataFrame mimicking the Cursor Usage dataset."""
    return pd.DataFrame({
        "Date": pd.to_datetime([
            "2024-01-10 09:00:00",
            "2024-01-15 10:30:00",
            "2024-02-05 14:00:00",
        ]),
        "Model": ["gpt-4", "claude-3", "gpt-4"],
        "Cost": [0.50, 1.20, 0.80],
        "Total Tokens": [1000, 2500, 1500],
        "User": ["alice", "bob", "alice"],
        "Kind": ["chat", "completion", "chat"],
    })


def _make_empty_df() -> pd.DataFrame:
    return pd.DataFrame()


# ===========================================================================
# Registry dataset ID test (preserved from original)
# ===========================================================================

@patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
@patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
@patch("src.pages.cursor_usage._callbacks.ParquetReader")
def test_update_dashboard_uses_registry_dataset_id(
    mock_reader_cls, mock_resolve, mock_load
):
    from src.pages.cursor_usage._callbacks import update_dashboard

    mock_reader_cls.return_value = MagicMock()
    mock_resolve.return_value = "cursor-usage"
    mock_load.return_value = _make_empty_df()

    update_dashboard("2024-01-01", "2024-01-31", ["gpt-4"], None, None)

    mock_resolve.assert_called_once_with()
    args, _ = mock_load.call_args
    assert args[1] == "cursor-usage"


# ===========================================================================
# Return structure tests
# ===========================================================================

class TestUpdateDashboardReturnStructure:
    """update_dashboard must return a 7-tuple."""

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_returns_seven_elements(self, mock_reader_cls, mock_resolve, mock_load):
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        assert len(result) == 7

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_charts_are_go_figure(self, mock_reader_cls, mock_resolve, mock_load):
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        # indices 3, 4, 5 are chart figures
        for idx in (3, 4, 5):
            assert isinstance(result[idx], go.Figure), f"result[{idx}] is not go.Figure"


# ===========================================================================
# Empty state tests (must use shared empty_states functions)
# ===========================================================================

class TestEmptyState:
    """When filtered data is empty, dashboard must use shared empty state functions."""

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_empty_data_returns_seven_elements(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_empty_df()

        result = update_dashboard(None, None, None, None, None)
        assert len(result) == 7

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_empty_data_chart_figures_have_annotation(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        """Empty state figures must contain a 'no data' annotation (from create_empty_figure)."""
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_empty_df()

        result = update_dashboard(None, None, None, None, None)
        # Chart figures are indices 3, 4, 5
        for idx in (3, 4, 5):
            fig = result[idx]
            assert isinstance(fig, go.Figure)
            assert len(fig.layout.annotations) >= 1
            has_no_data_text = any(
                "no data" in ann.text.lower() or "No data" in ann.text
                for ann in fig.layout.annotations
            )
            assert has_no_data_text, (
                f"result[{idx}] annotation missing 'no data' text"
            )


# ===========================================================================
# Error state tests
# ===========================================================================

class TestErrorState:
    """When an exception occurs, dashboard must use shared error_states functions."""

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_exception_returns_seven_elements(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.side_effect = Exception("S3 connection failed")

        result = update_dashboard(None, None, None, None, None)
        assert len(result) == 7

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_exception_chart_figures_have_error_annotation(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        """Error figures must contain the error message annotation (from create_error_figure)."""
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.side_effect = Exception("S3 connection failed")

        result = update_dashboard(None, None, None, None, None)
        for idx in (3, 4, 5):
            fig = result[idx]
            assert isinstance(fig, go.Figure)
            assert len(fig.layout.annotations) >= 1


# ===========================================================================
# build_chart integration: verify charts use shared builder
# ===========================================================================

class TestBuildChartIntegration:
    """Callbacks must use build_chart from src.charts.chart_builder."""

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_cost_trend_chart_has_title(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        """Title is now suppressed (shown via CardHeader); title.text must be None."""
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        cost_trend_fig = result[3]
        assert cost_trend_fig.layout.title.text is None

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_token_efficiency_chart_has_title(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        """Title is now suppressed (shown via CardHeader); title.text must be None."""
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        efficiency_fig = result[4]
        assert efficiency_fig.layout.title.text is None

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_model_distribution_chart_has_title(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        """Title is now suppressed (shown via CardHeader); title.text must be None."""
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        distribution_fig = result[5]
        assert distribution_fig.layout.title.text is None

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_cost_trend_chart_has_line_trace(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        cost_trend_fig = result[3]
        assert len(cost_trend_fig.data) >= 1
        assert cost_trend_fig.data[0].type == "scatter"

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_token_efficiency_chart_has_bar_trace(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        efficiency_fig = result[4]
        assert len(efficiency_fig.data) >= 1
        assert efficiency_fig.data[0].type == "bar"

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_model_distribution_chart_has_pie_trace(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        distribution_fig = result[5]
        assert len(distribution_fig.data) >= 1
        assert distribution_fig.data[0].type == "pie"


# ===========================================================================
# build_table integration: verify table uses shared builder
# ===========================================================================

class TestBuildTableIntegration:
    """Table component must be built via shared build_table + TableSpec."""

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_table_is_dash_data_table(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        table_component = result[6]
        assert isinstance(table_component, dash_table.DataTable)

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_table_page_size_matches_spec(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        table_component = result[6]
        assert table_component.page_size == 20

    @patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
    @patch("src.pages.cursor_usage._callbacks.resolve_dataset_id_for_dashboard")
    @patch("src.pages.cursor_usage._callbacks.ParquetReader")
    def test_table_style_table_has_overflow(
        self, mock_reader_cls, mock_resolve, mock_load
    ):
        from src.pages.cursor_usage._callbacks import update_dashboard

        mock_reader_cls.return_value = MagicMock()
        mock_resolve.return_value = "cursor-usage"
        mock_load.return_value = _make_sample_df()

        result = update_dashboard("2024-01-01", "2024-12-31", None, None, None)
        table_component = result[6]
        assert table_component.style_table["overflowX"] == "auto"


# ===========================================================================
# Imports must NOT use legacy render_* functions
# ===========================================================================

class TestNoLegacyImports:
    """_callbacks.py must not import render_bar_chart, render_line_chart, render_pie_chart."""

    def test_no_render_bar_chart_import(self):
        import inspect
        from src.pages.cursor_usage import _callbacks

        source = inspect.getsource(_callbacks)
        assert "render_bar_chart" not in source

    def test_no_render_line_chart_import(self):
        import inspect
        from src.pages.cursor_usage import _callbacks

        source = inspect.getsource(_callbacks)
        assert "render_line_chart" not in source

    def test_no_render_pie_chart_import(self):
        import inspect
        from src.pages.cursor_usage import _callbacks

        source = inspect.getsource(_callbacks)
        assert "render_pie_chart" not in source

    def test_uses_build_chart_import(self):
        import inspect
        from src.pages.cursor_usage import _callbacks

        source = inspect.getsource(_callbacks)
        assert "build_chart" in source

    def test_uses_build_table_import(self):
        import inspect
        from src.pages.cursor_usage import _callbacks

        source = inspect.getsource(_callbacks)
        assert "build_table" in source

    def test_uses_empty_states_import(self):
        import inspect
        from src.pages.cursor_usage import _callbacks

        source = inspect.getsource(_callbacks)
        assert "create_empty_figure" in source or "create_error_figure" in source
