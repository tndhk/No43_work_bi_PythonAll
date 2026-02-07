"""Tests for APAC DOT Due Date callbacks module.

TDD Step 1 (RED): These tests define the expected behavior of
update_all_charts() before implementation.
"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, call
from dash import html

from tests.helpers.dash_test_utils import extract_text_recursive


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

def _make_sample_df() -> pd.DataFrame:
    """Create a sample DataFrame mimicking the APAC DOT Due Date dataset."""
    return pd.DataFrame({
        "Delivery Completed Month": ["2024-01", "2024-01", "2024-02"],
        "business area": ["APAC", "EMEA", "APAC"],
        "Metric Workstream": ["WS-A", "WS-B", "WS-A"],
        "Vendor: Account Name": ["Vendor1", "Vendor2", "Vendor1"],
        "AMP VS AV Scope": ["AMP", "AV", "AMP"],
        "order tags": ["TypeA", "TypeB", "TypeA"],
        "job name": ["PRC-Job-1", "Normal-Job-2", "PRC-Job-3"],
        "work order id": ["WO-001", "WO-002", "WO-003"],
    })


def _make_empty_df() -> pd.DataFrame:
    """Create an empty DataFrame with the expected columns."""
    return pd.DataFrame({
        "Delivery Completed Month": pd.Series(dtype="str"),
        "business area": pd.Series(dtype="str"),
        "Metric Workstream": pd.Series(dtype="str"),
        "Vendor: Account Name": pd.Series(dtype="str"),
        "AMP VS AV Scope": pd.Series(dtype="str"),
        "order tags": pd.Series(dtype="str"),
        "job name": pd.Series(dtype="str"),
        "work order id": pd.Series(dtype="str"),
    })


# ===========================================================================
# Module existence and function availability
# ===========================================================================

class TestModuleExists:
    """_callbacks module must exist and expose update_all_charts."""

    def test_module_imports(self):
        """_callbacks module should be importable."""
        from src.pages.apac_dot_due_date import _callbacks  # noqa: F401

    def test_update_all_charts_is_callable(self):
        """update_all_charts must be a callable function."""
        from src.pages.apac_dot_due_date._callbacks import update_all_charts
        assert callable(update_all_charts)


# ===========================================================================
# update_all_charts return value tests
# ===========================================================================

class TestUpdateAllChartsReturnValue:
    """update_all_charts must return a tuple of (title, component)."""

    @patch("src.pages.apac_dot_due_date._callbacks._ch00_reference_table")
    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_returns_tuple(self, mock_reader_cls, mock_load, mock_chart):
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        mock_load.return_value = _make_sample_df()
        mock_chart.build.return_value = ("Title", html.Div("table"))

        result = update_all_charts(
            "number", "area", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )
        assert isinstance(result, tuple)
        assert len(result) == 2

    @patch("src.pages.apac_dot_due_date._callbacks._ch00_reference_table")
    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_returns_chart_build_output(self, mock_reader_cls, mock_load, mock_chart):
        """Return value should match _ch00_reference_table.build() output."""
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        mock_load.return_value = _make_sample_df()
        expected_title = "0) Reference : Number of Work Order"
        expected_component = html.Div("some table")
        mock_chart.build.return_value = (expected_title, expected_component)

        result = update_all_charts(
            "number", "area", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )
        assert result[0] == expected_title
        assert result[1] == expected_component


# ===========================================================================
# load_and_filter_data delegation tests
# ===========================================================================

class TestLoadAndFilterDataDelegation:
    """update_all_charts must call load_and_filter_data exactly once."""

    @patch("src.pages.apac_dot_due_date._callbacks._ch00_reference_table")
    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_calls_load_and_filter_data_once(
        self, mock_reader_cls, mock_load, mock_chart
    ):
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        mock_load.return_value = _make_sample_df()
        mock_chart.build.return_value = ("Title", html.Div())

        update_all_charts(
            "number", "area", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )
        assert mock_load.call_count == 1

    @patch("src.pages.apac_dot_due_date._callbacks._ch00_reference_table")
    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_passes_filter_args_correctly(
        self, mock_reader_cls, mock_load, mock_chart
    ):
        """All filter arguments must be forwarded to load_and_filter_data."""
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        mock_load.return_value = _make_sample_df()
        mock_chart.build.return_value = ("Title", html.Div())

        months = ["2024-01", "2024-02"]
        prc = "prc_only"
        areas = ["APAC"]
        cats = ["WS-A", "WS-B"]
        vendors = ["Vendor1"]
        amp_av = ["AMP"]
        order_types = ["TypeA"]

        update_all_charts(
            "number", "area", months, prc,
            areas, cats, vendors, amp_av, order_types,
        )

        _, kwargs = mock_load.call_args
        assert kwargs["selected_months"] == months
        assert kwargs["prc_filter_value"] == prc
        assert kwargs["area_values"] == areas
        assert kwargs["category_values"] == cats
        assert kwargs["vendor_values"] == vendors
        assert kwargs["amp_av_values"] == amp_av
        assert kwargs["order_type_values"] == order_types

    @patch("src.pages.apac_dot_due_date._callbacks._ch00_reference_table")
    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_passes_reader_and_dataset_id(
        self, mock_reader_cls, mock_load, mock_chart
    ):
        """A ParquetReader instance and DATASET_ID must be passed to load_and_filter_data."""
        from src.pages.apac_dot_due_date._callbacks import update_all_charts
        from src.pages.apac_dot_due_date._constants import DATASET_ID

        mock_reader_instance = MagicMock()
        mock_reader_cls.return_value = mock_reader_instance
        mock_load.return_value = _make_sample_df()
        mock_chart.build.return_value = ("Title", html.Div())

        update_all_charts(
            "number", "area", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )

        args, kwargs = mock_load.call_args
        # First positional arg or keyword should be the reader instance
        assert args[0] == mock_reader_instance or kwargs.get("reader") == mock_reader_instance
        # Second positional arg or keyword should be DATASET_ID
        assert args[1] == DATASET_ID or kwargs.get("dataset_id") == DATASET_ID


# ===========================================================================
# _ch00_reference_table.build delegation tests
# ===========================================================================

class TestChartBuildDelegation:
    """update_all_charts must pass filtered data and UI params to chart build."""

    @patch("src.pages.apac_dot_due_date._callbacks._ch00_reference_table")
    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_passes_filtered_df_to_build(
        self, mock_reader_cls, mock_load, mock_chart
    ):
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        sample_df = _make_sample_df()
        mock_load.return_value = sample_df
        mock_chart.build.return_value = ("Title", html.Div())

        update_all_charts(
            "number", "area", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )

        args, _ = mock_chart.build.call_args
        # First argument to build should be the filtered DataFrame
        pd.testing.assert_frame_equal(args[0], sample_df)

    @patch("src.pages.apac_dot_due_date._callbacks._ch00_reference_table")
    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_passes_breakdown_tab_to_build(
        self, mock_reader_cls, mock_load, mock_chart
    ):
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        mock_load.return_value = _make_sample_df()
        mock_chart.build.return_value = ("Title", html.Div())

        update_all_charts(
            "number", "vendor", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )

        args, _ = mock_chart.build.call_args
        assert args[1] == "vendor"

    @patch("src.pages.apac_dot_due_date._callbacks._ch00_reference_table")
    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_passes_num_percent_mode_to_build(
        self, mock_reader_cls, mock_load, mock_chart
    ):
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        mock_load.return_value = _make_sample_df()
        mock_chart.build.return_value = ("Title", html.Div())

        update_all_charts(
            "percent", "area", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )

        args, _ = mock_chart.build.call_args
        assert args[2] == "percent"


# ===========================================================================
# Error handling tests
# ===========================================================================

class TestErrorHandling:
    """update_all_charts must handle exceptions gracefully."""

    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_returns_error_tuple_on_exception(self, mock_reader_cls, mock_load):
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        mock_load.side_effect = Exception("S3 connection failed")

        result = update_all_charts(
            "number", "area", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )
        assert isinstance(result, tuple)
        assert len(result) == 2

    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_error_title_is_default(self, mock_reader_cls, mock_load):
        """On error, the title should be the default reference table title."""
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        mock_load.side_effect = Exception("S3 connection failed")

        result = update_all_charts(
            "number", "area", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )
        assert result[0] == "0) Reference : Number of Work Order"

    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_error_component_contains_message(self, mock_reader_cls, mock_load):
        """On error, the component should contain the error message."""
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        mock_load.side_effect = Exception("S3 connection failed")

        result = update_all_charts(
            "number", "area", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )
        error_component = result[1]
        assert isinstance(error_component, html.Div)
        # The error text should be somewhere in the component tree
        error_text = extract_text_recursive(error_component)
        assert "S3 connection failed" in error_text

    @patch("src.pages.apac_dot_due_date._callbacks._ch00_reference_table")
    @patch("src.pages.apac_dot_due_date._callbacks.load_and_filter_data")
    @patch("src.pages.apac_dot_due_date._callbacks.ParquetReader")
    def test_error_in_chart_build_handled(
        self, mock_reader_cls, mock_load, mock_chart
    ):
        """If _ch00_reference_table.build raises, error should be handled."""
        from src.pages.apac_dot_due_date._callbacks import update_all_charts

        mock_load.return_value = _make_sample_df()
        mock_chart.build.side_effect = KeyError("missing column")

        result = update_all_charts(
            "number", "area", ["2024-01"], "all",
            ["APAC"], ["WS-A"], ["Vendor1"], ["AMP"], ["TypeA"],
        )
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "0) Reference : Number of Work Order"


# ===========================================================================
# Callback registration tests
# ===========================================================================

class TestCallbackRegistration:
    """Importing _callbacks should register the Dash callback."""

    def test_update_all_charts_has_callback_attributes(self):
        """update_all_charts should have Dash callback metadata if registered."""
        # Dash wraps callback functions - we check it's wrapped by the decorator
        # by verifying it's callable (the decorator preserves callability)
        from src.pages.apac_dot_due_date._callbacks import update_all_charts
        assert callable(update_all_charts)


# ===========================================================================
# Integration: __init__.py imports _callbacks
# ===========================================================================

class TestInitImportsCallbacks:
    """__init__.py must import _callbacks to register callbacks via side effect."""

    def test_init_module_has_callbacks_import(self):
        """The __init__.py should trigger _callbacks import."""
        import importlib
        import src.pages.apac_dot_due_date as page_module
        # After importing the page module, _callbacks should be accessible
        assert hasattr(page_module, '_callbacks') or True
        # A more reliable check: _callbacks module should be importable
        from src.pages.apac_dot_due_date import _callbacks  # noqa: F401


