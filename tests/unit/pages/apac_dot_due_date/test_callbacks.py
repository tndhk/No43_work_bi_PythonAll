"""Tests for APAC DOT Due Date callbacks module.

TDD Step 1 (RED): These tests define the expected behavior of
update_dashboard() after refactoring.

Refactored architecture:
- build_pivot_data() (from _chart_builders) produces a DataFrame
- build_table() (from src.charts.table_builder) renders it
- register_clear_callbacks() replaces 7 individual clear functions
- TABLE_SPECS is imported from _constants (not charts._table_specs)
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
# Common mock patch paths (updated for refactored architecture)
# ---------------------------------------------------------------------------
_PATCH_READER = "src.pages.apac_dot_due_date._callbacks.ParquetReader"
_PATCH_LOAD = "src.pages.apac_dot_due_date._callbacks.load_and_filter_data"
_PATCH_BUILD_PIVOT = "src.pages.apac_dot_due_date._callbacks.build_pivot_table"
_PATCH_RESOLVE = "src.pages.apac_dot_due_date._callbacks.resolve_dataset_id"


def _setup_happy_path(mock_reader_cls, mock_load, mock_build_pivot):
    """Configure mocks for a successful (non-error) callback invocation."""
    mock_reader_cls.return_value = MagicMock()
    # load_and_filter_data will be called twice (once per dataset)
    mock_load.side_effect = [_make_sample_df(), _make_sample_df_2()]
    # build_pivot_table will be called twice (once per dataset)
    mock_build_pivot.side_effect = [
        ("Title 0", html.Div("table-0")),
        ("Title 1", html.Div("table-1")),
    ]


def _invoke_update(
    months=None, prc="all", areas=None, cats=None,
    vendors=None, amp_av=None, order_types=None,
    num_percent="number", breakdown="area",
):
    """Import and call update_dashboard with sensible defaults."""
    from src.pages.apac_dot_due_date._callbacks import update_dashboard

    return update_dashboard(
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
    """_callbacks module must exist and expose update_dashboard."""

    def test_module_imports(self):
        """_callbacks module should be importable."""
        from src.pages.apac_dot_due_date import _callbacks  # noqa: F401

    def test_update_dashboard_is_callable(self):
        """update_dashboard must be a callable function."""
        from src.pages.apac_dot_due_date._callbacks import update_dashboard
        assert callable(update_dashboard)


class TestImportSources:
    """_callbacks must import from the correct (refactored) locations."""

    def test_imports_build_pivot_data_from_chart_builders(self):
        """build_pivot_data must be importable from _chart_builders."""
        from src.pages.apac_dot_due_date._chart_builders import build_pivot_data
        assert callable(build_pivot_data)

    def test_imports_build_table_from_shared_module(self):
        """build_table must be importable from src.charts.table_builder."""
        from src.charts.table_builder import build_table
        assert callable(build_table)

    def test_imports_table_specs_from_constants(self):
        """TABLE_SPECS must be importable from _constants."""
        from src.pages.apac_dot_due_date._constants import TABLE_SPECS
        assert isinstance(TABLE_SPECS, dict)

    def test_no_charts_subpackage_imports(self):
        """_callbacks must NOT import from the old .charts subpackage."""
        import src.pages.apac_dot_due_date._callbacks as cb_module
        import inspect
        source = inspect.getsource(cb_module)
        assert ".charts._pivot_table_builder" not in source
        assert ".charts._table_specs" not in source


# ===========================================================================
# update_dashboard return value tests
# ===========================================================================

class TestUpdateDashboardReturnValue:
    """update_dashboard must return a 5-tuple of (kpi, title0, comp0, title1, comp1)."""

    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_returns_tuple_of_length_5(
        self, mock_reader_cls, mock_load, mock_build_pivot
    ):
        _setup_happy_path(mock_reader_cls, mock_load, mock_build_pivot)
        result = _invoke_update()
        assert isinstance(result, tuple)
        assert len(result) == 5

    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_returns_kpi_and_chart_build_outputs(
        self, mock_reader_cls, mock_load, mock_build_pivot
    ):
        """Return value: position 0 is KPI, positions 1-2 from first build, 3-4 from second."""
        _setup_happy_path(mock_reader_cls, mock_load, mock_build_pivot)
        expected_title_0 = "0) Reference : Number of Work Order"
        expected_comp_0 = html.Div("ref table")
        expected_title_1 = "1) DDD Change + Issue : Number of Work Order"
        expected_comp_1 = html.Div("change table")
        mock_build_pivot.side_effect = [
            (expected_title_0, expected_comp_0),
            (expected_title_1, expected_comp_1),
        ]

        result = _invoke_update()
        assert isinstance(result[0], str)  # KPI value
        assert result[1] == expected_title_0
        assert result[2] == expected_comp_0
        assert result[3] == expected_title_1
        assert result[4] == expected_comp_1


# ===========================================================================
# load_and_filter_data delegation tests
# ===========================================================================

class TestLoadAndFilterDataDelegation:
    """update_dashboard must call load_and_filter_data correctly for each dataset."""

    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_calls_load_function_twice(
        self, mock_reader_cls, mock_load, mock_build_pivot
    ):
        """load_and_filter_data called twice (once per dataset configuration)."""
        _setup_happy_path(mock_reader_cls, mock_load, mock_build_pivot)
        _invoke_update()
        assert mock_load.call_count == 2

    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_dataset1_not_passed_order_type(
        self, mock_reader_cls, mock_load, mock_build_pivot
    ):
        """First load_and_filter_data call (reference dataset) must receive order_type_values=None."""
        _setup_happy_path(mock_reader_cls, mock_load, mock_build_pivot)
        _invoke_update(order_types=["TypeA", "TypeB"])

        # First call (reference dataset)
        call_args_list = mock_load.call_args_list
        assert len(call_args_list) >= 1
        _, kwargs = call_args_list[0]
        assert kwargs["order_type_values"] is None

    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_dataset2_passed_order_type(
        self, mock_reader_cls, mock_load, mock_build_pivot
    ):
        """Second load_and_filter_data call (change_issue dataset) must receive the UI order_type values."""
        _setup_happy_path(mock_reader_cls, mock_load, mock_build_pivot)
        order_types = ["TypeA", "TypeB"]
        _invoke_update(order_types=order_types)

        # Second call (change_issue dataset)
        call_args_list = mock_load.call_args_list
        assert len(call_args_list) >= 2
        _, kwargs = call_args_list[1]
        assert kwargs["order_type_values"] == order_types

    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_passes_filter_args_correctly(
        self, mock_reader_cls, mock_load, mock_build_pivot
    ):
        """Filter arguments must be forwarded correctly to load_and_filter_data."""
        _setup_happy_path(mock_reader_cls, mock_load, mock_build_pivot)

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

        # Check first call (reference dataset)
        call_args_list = mock_load.call_args_list
        assert len(call_args_list) >= 1
        _, kwargs = call_args_list[0]
        assert kwargs["selected_months"] == months
        assert kwargs["prc_filter_value"] == prc
        assert kwargs["area_values"] == areas
        assert kwargs["category_values"] == cats
        assert kwargs["vendor_values"] == vendors
        assert kwargs["amp_av_values"] == amp_av
        assert kwargs["order_type_values"] is None  # reference dataset skips order_type

    @patch(_PATCH_RESOLVE)
    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_passes_reader_and_dataset_id(
        self, mock_reader_cls, mock_load, mock_build_pivot, mock_resolve
    ):
        """A ParquetReader instance and resolved dataset IDs must be passed."""
        from src.pages.apac_dot_due_date._constants import (
            DASHBOARD_ID, DATASETS,
        )

        mock_reader_instance = MagicMock()
        mock_reader_cls.return_value = mock_reader_instance
        mock_resolve.side_effect = lambda dash_id, chart_id: f"resolved-{chart_id}"
        mock_load.side_effect = [_make_sample_df(), _make_sample_df_2()]
        mock_build_pivot.side_effect = [
            ("Title 0", html.Div()),
            ("Title 1", html.Div()),
        ]

        _invoke_update()

        # resolve_dataset_id should be called twice: once for each dataset
        assert mock_resolve.call_count == 2
        mock_resolve.assert_any_call(DASHBOARD_ID, DATASETS["reference"].chart_id)
        mock_resolve.assert_any_call(DASHBOARD_ID, DATASETS["change_issue"].chart_id)

        # load_and_filter_data gets reader + resolved dataset IDs
        call_args_list = mock_load.call_args_list
        assert len(call_args_list) == 2
        args1, _ = call_args_list[0]
        assert args1[0] == mock_reader_instance
        assert args1[1] == f"resolved-{DATASETS['reference'].chart_id}"
        args2, _ = call_args_list[1]
        assert args2[0] == mock_reader_instance
        assert args2[1] == f"resolved-{DATASETS['change_issue'].chart_id}"


# ===========================================================================
# build_pivot_table delegation tests
# ===========================================================================

class TestChartBuildDelegation:
    """update_dashboard must pass filtered data and UI params to build_pivot_table."""

    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_passes_filtered_df_to_build(
        self, mock_reader_cls, mock_load, mock_build_pivot
    ):
        sample_df = _make_sample_df()
        sample_df_2 = _make_sample_df_2()
        mock_load.side_effect = [sample_df, sample_df_2]
        mock_build_pivot.side_effect = [
            ("Title 0", html.Div()),
            ("Title 1", html.Div()),
        ]

        _invoke_update()

        # Check first call (reference dataset)
        call_args_list = mock_build_pivot.call_args_list
        assert len(call_args_list) >= 1
        kwargs_0 = call_args_list[0].kwargs
        pd.testing.assert_frame_equal(kwargs_0["filtered_df"], sample_df)

        # Check second call (change_issue dataset)
        assert len(call_args_list) >= 2
        kwargs_1 = call_args_list[1].kwargs
        pd.testing.assert_frame_equal(kwargs_1["filtered_df"], sample_df_2)

    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_passes_breakdown_tab_to_build(
        self, mock_reader_cls, mock_load, mock_build_pivot
    ):
        _setup_happy_path(mock_reader_cls, mock_load, mock_build_pivot)
        _invoke_update(breakdown="vendor")

        call_args_list = mock_build_pivot.call_args_list
        assert len(call_args_list) >= 2
        kwargs_0 = call_args_list[0].kwargs
        assert kwargs_0["breakdown_tab"] == "vendor"

        kwargs_1 = call_args_list[1].kwargs
        assert kwargs_1["breakdown_tab"] == "vendor"

    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_passes_num_percent_mode_to_build(
        self, mock_reader_cls, mock_load, mock_build_pivot
    ):
        _setup_happy_path(mock_reader_cls, mock_load, mock_build_pivot)
        _invoke_update(num_percent="percent")

        call_args_list = mock_build_pivot.call_args_list
        assert len(call_args_list) >= 2
        kwargs_0 = call_args_list[0].kwargs
        assert kwargs_0["num_percent_mode"] == "percent"

        kwargs_1 = call_args_list[1].kwargs
        assert kwargs_1["num_percent_mode"] == "percent"


# ===========================================================================
# Error handling tests
# ===========================================================================

class TestErrorHandling:
    """update_dashboard must handle exceptions gracefully with 5-tuple."""

    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_returns_error_tuple_of_length_5(self, mock_reader_cls, mock_load):
        mock_load.side_effect = Exception("S3 connection failed")

        result = _invoke_update()
        assert isinstance(result, tuple)
        assert len(result) == 5

    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_error_kpi_is_zero(self, mock_reader_cls, mock_load):
        """On error, KPI should be "0"."""
        mock_load.side_effect = Exception("S3 connection failed")

        result = _invoke_update()
        assert result[0] == "0"

    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_error_titles_are_defaults(self, mock_reader_cls, mock_load):
        """On error, both titles should be their default values."""
        mock_load.side_effect = Exception("S3 connection failed")

        result = _invoke_update()
        assert result[1] == "0) Reference : Number of Work Order"
        assert result[3] == "1) DDD Change + Issue : Number of Work Order"

    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_error_components_contain_message(self, mock_reader_cls, mock_load):
        """On error, both error components should contain the error message."""
        mock_load.side_effect = Exception("S3 connection failed")

        result = _invoke_update()
        # Check component at position 2 (reference table error)
        assert isinstance(result[2], html.Div)
        error_text_0 = extract_text_recursive(result[2])
        assert "S3 connection failed" in error_text_0
        # Check component at position 4 (change_issue table error)
        assert isinstance(result[4], html.Div)
        error_text_1 = extract_text_recursive(result[4])
        assert "S3 connection failed" in error_text_1

    @patch(_PATCH_BUILD_PIVOT)
    @patch(_PATCH_LOAD)
    @patch(_PATCH_READER)
    def test_error_in_chart_build_handled(
        self, mock_reader_cls, mock_load, mock_build_pivot
    ):
        """If build_pivot_table raises, error should be handled."""
        mock_load.side_effect = [_make_sample_df(), _make_sample_df_2()]
        mock_build_pivot.side_effect = KeyError("missing column")

        result = _invoke_update()
        assert isinstance(result, tuple)
        assert len(result) == 5
        assert result[0] == "0"
        assert result[1] == "0) Reference : Number of Work Order"
        assert result[3] == "1) DDD Change + Issue : Number of Work Order"


# ===========================================================================
# Callback registration tests
# ===========================================================================

class TestCallbackRegistration:
    """Importing _callbacks should register the Dash callback."""

    def test_update_dashboard_has_callback_attributes(self):
        """update_dashboard should have Dash callback metadata if registered."""
        from src.pages.apac_dot_due_date._callbacks import update_dashboard
        assert callable(update_dashboard)


# ===========================================================================
# Integration: __init__.py imports _callbacks
# ===========================================================================

class TestInitImportsCallbacks:
    """__init__.py must import _callbacks to register callbacks via side effect."""

    def test_init_module_has_callbacks_import(self):
        """The __init__.py should trigger _callbacks import."""
        from src.pages.apac_dot_due_date import _callbacks  # noqa: F401


# ===========================================================================
# Clear callbacks: now using register_clear_callbacks
# ===========================================================================

class TestClearCallbacksUseRegisterHelper:
    """Clear callbacks must be registered via register_clear_callbacks utility."""

    def test_callbacks_module_uses_register_clear_callbacks(self):
        """_callbacks.py source must call register_clear_callbacks."""
        import inspect
        import src.pages.apac_dot_due_date._callbacks as cb_module
        source = inspect.getsource(cb_module)
        assert "register_clear_callbacks" in source

    def test_no_individual_clear_functions_defined(self):
        """_callbacks.py should NOT define individual clear_month, clear_area, etc. functions."""
        import inspect
        import src.pages.apac_dot_due_date._callbacks as cb_module
        source = inspect.getsource(cb_module)
        # Should not have `def clear_month` etc. defined individually
        assert "def clear_month" not in source
        assert "def clear_area" not in source
        assert "def clear_category" not in source
        assert "def clear_vendor" not in source
        assert "def clear_amp_av" not in source
        assert "def clear_order_type" not in source

    def test_prc_clear_returns_none_as_default(self):
        """PRC clear callback must return None (not []) since it is a single-select filter."""
        # register_clear_callbacks for PRC must use default_value=None
        import inspect
        import src.pages.apac_dot_due_date._callbacks as cb_module
        source = inspect.getsource(cb_module)
        # There should be a register_clear_callbacks call with default_value=None for PRC
        assert "default_value=None" in source
