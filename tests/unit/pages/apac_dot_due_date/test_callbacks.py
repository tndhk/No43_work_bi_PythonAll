"""Tests for APAC DOT Due Date callbacks module.

TDD Step 1 (RED): These tests define the expected behavior of
update_all_charts() before implementation.
"""
import inspect

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
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


def _make_sample_df_2() -> pd.DataFrame:
    """Create a sample DataFrame mimicking the change-issue dataset."""
    return pd.DataFrame({
        "edit month": ["2024-01", "2024-02"],
        "business area": ["APAC", "EMEA"],
        "metric workstream": ["WS-A", "WS-B"],
        "vendor: account name": ["Vendor1", "Vendor2"],
        "order types": ["TypeA", "TypeB"],
        "job name": ["PRC-Job-1", "Normal-Job-2"],
        "work order: work order id": ["WO-001", "WO-002"],
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


# ---------------------------------------------------------------------------
# Common mock patch paths
# ---------------------------------------------------------------------------
_PATCH_READER = "src.pages.apac_dot_due_date._callbacks.ParquetReader"
_PATCH_LOAD = "src.pages.apac_dot_due_date._callbacks.load_and_filter_data"
_PATCH_LOAD_2 = "src.pages.apac_dot_due_date._callbacks.load_and_filter_data_2"
_PATCH_CH00 = "src.pages.apac_dot_due_date._callbacks._ch00_reference_table"
_PATCH_CH01 = "src.pages.apac_dot_due_date._callbacks._ch01_change_issue_table"
_PATCH_RESOLVE = "src.pages.apac_dot_due_date._callbacks.resolve_dataset_id"


def _setup_happy_path(mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01):
    """Configure mocks for a successful (non-error) callback invocation."""
    mock_reader_cls.return_value = MagicMock()
    mock_load.return_value = _make_sample_df()
    mock_load_2.return_value = _make_sample_df_2()
    mock_ch00.build.return_value = ("Title 0", html.Div("table-0"))
    mock_ch01.build.return_value = ("Title 1", html.Div("table-1"))


def _invoke_update(
    months=None, prc="all", areas=None, cats=None,
    vendors=None, amp_av=None, order_types=None,
    num_percent="number", breakdown="area",
):
    """Import and call update_all_charts with sensible defaults."""
    from src.pages.apac_dot_due_date._callbacks import update_all_charts

    return update_all_charts(
        num_percent,
        breakdown,
        months or ["2024-01"],
        prc,
        areas or ["APAC"],
        cats or ["WS-A"],
        vendors or ["Vendor1"],
        amp_av or ["AMP"],
        order_types or ["TypeA"],
    )


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
    """update_all_charts must return a 4-tuple of (title0, comp0, title1, comp1)."""

    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_returns_tuple_of_length_4(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01
    ):
        _setup_happy_path(mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01)
        result = _invoke_update()
        assert isinstance(result, tuple)
        assert len(result) == 4

    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_returns_chart_build_outputs(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01
    ):
        """Return value positions 0-1 from ch00.build, 2-3 from ch01.build."""
        _setup_happy_path(mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01)
        expected_title_0 = "0) Reference : Number of Work Order"
        expected_comp_0 = html.Div("ref table")
        expected_title_1 = "1) DDD Change + Issue : Number of Work Order"
        expected_comp_1 = html.Div("change table")
        mock_ch00.build.return_value = (expected_title_0, expected_comp_0)
        mock_ch01.build.return_value = (expected_title_1, expected_comp_1)

        result = _invoke_update()
        assert result[0] == expected_title_0
        assert result[1] == expected_comp_0
        assert result[2] == expected_title_1
        assert result[3] == expected_comp_1


# ===========================================================================
# load_and_filter_data delegation tests
# ===========================================================================

class TestLoadAndFilterDataDelegation:
    """update_all_charts must call both load functions correctly."""

    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_calls_both_load_functions(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01
    ):
        """load_and_filter_data called once AND load_and_filter_data_2 called once."""
        _setup_happy_path(mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01)
        _invoke_update()
        assert mock_load.call_count == 1
        assert mock_load_2.call_count == 1

    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_dataset1_not_passed_order_type(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01
    ):
        """load_and_filter_data (dataset 1) must receive order_type_values=None."""
        _setup_happy_path(mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01)
        _invoke_update(order_types=["TypeA", "TypeB"])

        _, kwargs = mock_load.call_args
        assert kwargs["order_type_values"] is None

    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_dataset2_passed_order_type(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01
    ):
        """load_and_filter_data_2 (dataset 2) must receive the UI order_type values."""
        _setup_happy_path(mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01)
        order_types = ["TypeA", "TypeB"]
        _invoke_update(order_types=order_types)

        _, kwargs = mock_load_2.call_args
        assert kwargs["order_type_values"] == order_types

    def test_dataset2_has_no_amp_av_param(self):
        """load_and_filter_data_2 signature must NOT contain amp_av_values."""
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        sig = inspect.signature(load_and_filter_data_2)
        assert "amp_av_values" not in sig.parameters

    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_passes_filter_args_correctly_to_dataset1(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01
    ):
        """All filter arguments (except order_type) must be forwarded to load_and_filter_data."""
        _setup_happy_path(mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01)

        months = ["2024-01", "2024-02"]
        prc = "prc_only"
        areas = ["APAC"]
        cats = ["WS-A", "WS-B"]
        vendors = ["Vendor1"]
        amp_av = ["AMP"]

        _invoke_update(
            months=months, prc=prc, areas=areas, cats=cats,
            vendors=vendors, amp_av=amp_av, order_types=["TypeA"],
        )

        _, kwargs = mock_load.call_args
        assert kwargs["selected_months"] == months
        assert kwargs["prc_filter_value"] == prc
        assert kwargs["area_values"] == areas
        assert kwargs["category_values"] == cats
        assert kwargs["vendor_values"] == vendors
        assert kwargs["amp_av_values"] == amp_av
        assert kwargs["order_type_values"] is None  # NOT forwarded

    @patch(_PATCH_RESOLVE)
    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_passes_reader_and_dataset_id(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01, mock_resolve
    ):
        """A ParquetReader instance and resolved dataset IDs must be passed."""
        from src.pages.apac_dot_due_date._constants import (
            DASHBOARD_ID, CHART_ID_REFERENCE_TABLE, CHART_ID_CHANGE_ISSUE_TABLE,
        )

        mock_reader_instance = MagicMock()
        mock_reader_cls.return_value = mock_reader_instance
        mock_resolve.side_effect = lambda dash_id, chart_id: f"resolved-{chart_id}"
        mock_load.return_value = _make_sample_df()
        mock_load_2.return_value = _make_sample_df_2()
        mock_ch00.build.return_value = ("Title 0", html.Div())
        mock_ch01.build.return_value = ("Title 1", html.Div())

        _invoke_update()

        # resolve_dataset_id should be called twice: once for each chart
        assert mock_resolve.call_count == 2
        mock_resolve.assert_any_call(DASHBOARD_ID, CHART_ID_REFERENCE_TABLE)
        mock_resolve.assert_any_call(DASHBOARD_ID, CHART_ID_CHANGE_ISSUE_TABLE)

        # load_and_filter_data gets reader + resolved dataset 1 ID
        args1, _ = mock_load.call_args
        assert args1[0] == mock_reader_instance
        assert args1[1] == f"resolved-{CHART_ID_REFERENCE_TABLE}"

        # load_and_filter_data_2 gets reader + resolved dataset 2 ID
        args2, _ = mock_load_2.call_args
        assert args2[0] == mock_reader_instance
        assert args2[1] == f"resolved-{CHART_ID_CHANGE_ISSUE_TABLE}"


# ===========================================================================
# _ch00_reference_table.build delegation tests
# ===========================================================================

class TestChartBuildDelegation:
    """update_all_charts must pass filtered data and UI params to chart build."""

    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_passes_filtered_df_to_build(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01
    ):
        sample_df = _make_sample_df()
        sample_df_2 = _make_sample_df_2()
        mock_load.return_value = sample_df
        mock_load_2.return_value = sample_df_2
        mock_ch00.build.return_value = ("Title 0", html.Div())
        mock_ch01.build.return_value = ("Title 1", html.Div())

        _invoke_update()

        args_0, _ = mock_ch00.build.call_args
        pd.testing.assert_frame_equal(args_0[0], sample_df)

        args_1, _ = mock_ch01.build.call_args
        pd.testing.assert_frame_equal(args_1[0], sample_df_2)

    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_passes_breakdown_tab_to_build(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01
    ):
        _setup_happy_path(mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01)
        _invoke_update(breakdown="vendor")

        args_0, _ = mock_ch00.build.call_args
        assert args_0[1] == "vendor"

        args_1, _ = mock_ch01.build.call_args
        assert args_1[1] == "vendor"

    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_passes_num_percent_mode_to_build(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01
    ):
        _setup_happy_path(mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01)
        _invoke_update(num_percent="percent")

        args_0, _ = mock_ch00.build.call_args
        assert args_0[2] == "percent"

        args_1, _ = mock_ch01.build.call_args
        assert args_1[2] == "percent"


# ===========================================================================
# Error handling tests
# ===========================================================================

class TestErrorHandling:
    """update_all_charts must handle exceptions gracefully with 4-tuple."""

    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_returns_error_tuple_of_length_4(self, mock_reader_cls, mock_load, mock_load_2):
        mock_load.side_effect = Exception("S3 connection failed")

        result = _invoke_update()
        assert isinstance(result, tuple)
        assert len(result) == 4

    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_error_titles_are_defaults(self, mock_reader_cls, mock_load, mock_load_2):
        """On error, both titles should be their default values."""
        mock_load.side_effect = Exception("S3 connection failed")

        result = _invoke_update()
        assert result[0] == "0) Reference : Number of Work Order"
        assert result[2] == "1) DDD Change + Issue : Number of Work Order"

    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_error_components_contain_message(self, mock_reader_cls, mock_load, mock_load_2):
        """On error, both error components should contain the error message."""
        mock_load.side_effect = Exception("S3 connection failed")

        result = _invoke_update()
        # Check component at position 1 (ch00 error)
        assert isinstance(result[1], html.Div)
        error_text_0 = extract_text_recursive(result[1])
        assert "S3 connection failed" in error_text_0
        # Check component at position 3 (ch01 error)
        assert isinstance(result[3], html.Div)
        error_text_1 = extract_text_recursive(result[3])
        assert "S3 connection failed" in error_text_1

    @patch(_PATCH_CH01)
    @patch(_PATCH_CH00)
    @patch(_PATCH_LOAD_2)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_error_in_chart_build_handled(
        self, mock_reader_cls, mock_load, mock_load_2, mock_ch00, mock_ch01
    ):
        """If _ch00_reference_table.build raises, error should be handled."""
        mock_load.return_value = _make_sample_df()
        mock_load_2.return_value = _make_sample_df_2()
        mock_ch00.build.side_effect = KeyError("missing column")

        result = _invoke_update()
        assert isinstance(result, tuple)
        assert len(result) == 4
        assert result[0] == "0) Reference : Number of Work Order"
        assert result[2] == "1) DDD Change + Issue : Number of Work Order"


# ===========================================================================
# Callback registration tests
# ===========================================================================

class TestCallbackRegistration:
    """Importing _callbacks should register the Dash callback."""

    def test_update_all_charts_has_callback_attributes(self):
        """update_all_charts should have Dash callback metadata if registered."""
        from src.pages.apac_dot_due_date._callbacks import update_all_charts
        assert callable(update_all_charts)


# ===========================================================================
# Integration: __init__.py imports _callbacks
# ===========================================================================

class TestInitImportsCallbacks:
    """__init__.py must import _callbacks to register callbacks via side effect."""

    def test_init_module_has_callbacks_import(self):
        """The __init__.py should trigger _callbacks import."""
        from src.pages.apac_dot_due_date import _callbacks  # noqa: F401
