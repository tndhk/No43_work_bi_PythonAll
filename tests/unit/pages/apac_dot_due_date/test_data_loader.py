"""Tests for APAC DOT Due Date data loader module.

TDD Step 1 (RED): These tests define the expected behavior of
load_filter_options() and load_and_filter_data() before implementation.
"""
import inspect

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

def _make_sample_df() -> pd.DataFrame:
    """Create a sample DataFrame mimicking the APAC DOT Due Date dataset."""
    return pd.DataFrame({
        "Delivery Completed Month": ["2024-01", "2024-01", "2024-02", "2024-02", "2024-03"],
        "business area": ["APAC", "EMEA", "APAC", "APAC", "EMEA"],
        "Metric Workstream": ["WS-A", "WS-B", "WS-A", "WS-C", "WS-B"],
        "Vendor: Account Name": ["Vendor1", "Vendor2", "Vendor1", "Vendor3", "Vendor2"],
        "AMP VS AV Scope": ["AMP", "AV", "AMP", "AV", "AMP"],
        "order tags": ["TypeA", "TypeB", "TypeA", "TypeC", "TypeB"],
        "job name": ["PRC-Job-1", "Normal-Job-2", "PRC-Job-3", "Normal-Job-4", "Normal-Job-5"],
        "work order id": ["WO-001", "WO-002", "WO-003", "WO-004", "WO-005"],
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
# load_filter_options tests
# ===========================================================================

class TestLoadFilterOptionsReturnStructure:
    """load_filter_options must return a dict with all required keys."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_returns_dict(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert isinstance(result, dict)

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_has_all_required_keys(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        expected_keys = {
            "months", "areas", "workstreams", "vendors",
            "amp_vs_av", "order_types",
            "total_count", "prc_count", "non_prc_count",
        }
        assert set(result.keys()) == expected_keys


class TestLoadFilterOptionsValues:
    """load_filter_options must extract correct unique sorted values."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_months_sorted_unique(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["months"] == ["2024-01", "2024-02", "2024-03"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_areas_sorted_unique(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["areas"] == ["APAC", "EMEA"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_workstreams_sorted_unique(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["workstreams"] == ["WS-A", "WS-B", "WS-C"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_vendors_sorted_unique(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["vendors"] == ["Vendor1", "Vendor2", "Vendor3"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_amp_vs_av_sorted_unique(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["amp_vs_av"] == ["AMP", "AV"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_order_types_sorted_unique(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["order_types"] == ["TypeA", "TypeB", "TypeC"]


class TestLoadFilterOptionsCounts:
    """load_filter_options must compute PRC counts correctly."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_total_count(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["total_count"] == 5

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_count(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        # "PRC-Job-1" and "PRC-Job-3" contain "PRC"
        assert result["prc_count"] == 2

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_non_prc_count(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["non_prc_count"] == 3

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_plus_non_prc_equals_total(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["prc_count"] + result["non_prc_count"] == result["total_count"]


class TestLoadFilterOptionsException:
    """load_filter_options must return defaults on exception."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_returns_defaults_on_exception(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.side_effect = Exception("S3 connection failed")
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["months"] == []
        assert result["areas"] == []
        assert result["workstreams"] == []
        assert result["vendors"] == []
        assert result["amp_vs_av"] == []
        assert result["order_types"] == []
        assert result["total_count"] == 0
        assert result["prc_count"] == 0
        assert result["non_prc_count"] == 0


class TestLoadFilterOptionsEdgeCases:
    """load_filter_options edge cases: NaN values, missing columns."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_nan_values_excluded_from_options(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        df = _make_sample_df()
        df.loc[0, "business area"] = None
        mock_cache.return_value = df
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        # None/NaN should be excluded
        assert None not in result["areas"]
        # APAC still present (rows 2,3), EMEA still present (rows 1,4)
        assert "APAC" in result["areas"]
        assert "EMEA" in result["areas"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_missing_column_returns_empty_list(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        df = _make_sample_df().drop(columns=["business area"])
        mock_cache.return_value = df
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["areas"] == []

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_missing_job_name_column_prc_count_zero(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        df = _make_sample_df().drop(columns=["job name"])
        mock_cache.return_value = df
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["prc_count"] == 0
        assert result["non_prc_count"] == result["total_count"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_empty_dataframe_returns_empty_lists(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_empty_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        assert result["months"] == []
        assert result["areas"] == []
        assert result["total_count"] == 0
        assert result["prc_count"] == 0


# ===========================================================================
# load_and_filter_data tests
# ===========================================================================

class TestLoadAndFilterDataBasic:
    """load_and_filter_data must return a DataFrame."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_returns_dataframe(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        assert isinstance(result, pd.DataFrame)

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_no_filters_returns_all_rows(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        assert len(result) == 5


class TestLoadAndFilterDataPrcFilter:
    """load_and_filter_data PRC filter logic."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_only_filters_to_prc_rows(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="prc_only",
            area_values=None,
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        assert len(result) == 2
        assert all(result["job name"].str.contains("PRC", case=False, na=False))

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_not_included_excludes_prc_rows(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="prc_not_included",
            area_values=None,
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        assert len(result) == 3
        assert not any(result["job name"].str.contains("PRC", case=False, na=False))

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_all_returns_everything(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        assert len(result) == 5

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_filter_missing_job_name_column_noop(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        df = _make_sample_df().drop(columns=["job name"])
        mock_cache.return_value = df
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="prc_only",
            area_values=None,
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        assert len(result) == len(df)


class TestLoadAndFilterDataCategoryFilters:
    """load_and_filter_data category filter logic (months, area, etc.)."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_month_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=["2024-01"],
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        assert len(result) == 2
        assert all(result["Delivery Completed Month"] == "2024-01")

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_area_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="all",
            area_values=["APAC"],
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        assert len(result) == 3
        assert all(result["business area"] == "APAC")

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_category_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=["WS-A"],
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        assert len(result) == 2
        assert all(result["Metric Workstream"] == "WS-A")

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_vendor_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=["Vendor1"],
            amp_av_values=None,
            order_type_values=None,
        )
        assert len(result) == 2
        assert all(result["Vendor: Account Name"] == "Vendor1")

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_amp_av_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=None,
            amp_av_values=["AMP"],
            order_type_values=None,
        )
        assert len(result) == 3
        assert all(result["AMP VS AV Scope"] == "AMP")

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_order_type_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=["TypeA"],
        )
        assert len(result) == 2
        assert all(result["order tags"] == "TypeA")


class TestLoadAndFilterDataCombinedFilters:
    """load_and_filter_data with multiple filters combined."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_plus_area_combined(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="prc_only",
            area_values=["APAC"],
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        # PRC rows: row 0 (APAC), row 2 (APAC) -> both APAC -> 2
        assert len(result) == 2
        assert all(result["business area"] == "APAC")
        assert all(result["job name"].str.contains("PRC", case=False, na=False))

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_month_plus_vendor_combined(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=["2024-01"],
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=["Vendor1"],
            amp_av_values=None,
            order_type_values=None,
        )
        # month=2024-01: rows 0,1; vendor=Vendor1: rows 0,2 -> intersection: row 0
        assert len(result) == 1

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_all_filters_combined_returns_empty_when_no_match(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=["2024-03"],
            prc_filter_value="prc_only",
            area_values=["EMEA"],
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        # month=2024-03: row 4 (EMEA, Normal-Job-5) -> PRC only: none
        assert len(result) == 0


class TestLoadAndFilterDataEdgeCases:
    """load_and_filter_data edge cases."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_empty_list_filters_treated_as_no_filter(self, mock_cache):
        """Empty list [] should not filter (same as None)."""
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=[],
            prc_filter_value="all",
            area_values=[],
            category_values=[],
            vendor_values=[],
            amp_av_values=[],
            order_type_values=[],
        )
        # Empty lists should be treated same as None -> no filtering
        assert len(result) == 5

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_filter_case_insensitive(self, mock_cache):
        """PRC filter should be case insensitive."""
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data

        df = _make_sample_df()
        df.loc[0, "job name"] = "prc-lowercase-job"
        mock_cache.return_value = df
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "apac-dot-due-date",
            selected_months=None,
            prc_filter_value="prc_only",
            area_values=None,
            category_values=None,
            vendor_values=None,
            amp_av_values=None,
            order_type_values=None,
        )
        # row 0: "prc-lowercase-job" (contains prc), row 2: "PRC-Job-3"
        assert len(result) == 2


# ---------------------------------------------------------------------------
# Test data helpers for dataset 2 (change-issue)
# ---------------------------------------------------------------------------

def _make_sample_df2() -> pd.DataFrame:
    """Create a sample DataFrame mimicking the change-issue dataset (COLUMN_MAP_2)."""
    return pd.DataFrame({
        "edit month": ["2024-02", "2024-02", "2024-03", "2024-04"],
        "business area": ["APAC", "EMEA", "APAC", "EMEA"],
        "metric workstream": ["WS-X", "WS-Y", "WS-X", "WS-Z"],
        "vendor: account name": ["VendorA", "VendorB", "VendorA", "VendorC"],
        "order types": ["OrderA", "OrderB", "OrderA", "OrderC"],
        "job name": ["PRC-CI-1", "Normal-CI-2", "Normal-CI-3", "PRC-CI-4"],
        "work order: work order id": ["WO-101", "WO-102", "WO-103", "WO-104"],
    })


# ===========================================================================
# load_and_filter_data_2 tests
# ===========================================================================

class TestLoadAndFilterData2Basic:
    """load_and_filter_data_2 must return a DataFrame."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_returns_dataframe(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        mock_cache.return_value = _make_sample_df2()
        reader = MagicMock()

        result = load_and_filter_data_2(
            reader, "apac-dot-ddd-change-issue-sql",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=None,
            order_type_values=None,
        )
        assert isinstance(result, pd.DataFrame)

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_no_filters_returns_all_rows(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        mock_cache.return_value = _make_sample_df2()
        reader = MagicMock()

        result = load_and_filter_data_2(
            reader, "apac-dot-ddd-change-issue-sql",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=None,
            order_type_values=None,
        )
        assert len(result) == 4


class TestLoadAndFilterData2NoAmpAv:
    """load_and_filter_data_2 must NOT have an amp_av_values parameter."""

    def test_no_amp_av_values_parameter(self):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        sig = inspect.signature(load_and_filter_data_2)
        param_names = list(sig.parameters.keys())
        assert "amp_av_values" not in param_names

    def test_has_expected_parameters(self):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        sig = inspect.signature(load_and_filter_data_2)
        param_names = list(sig.parameters.keys())
        expected = [
            "reader", "dataset_id", "selected_months",
            "prc_filter_value", "area_values", "category_values",
            "vendor_values", "order_type_values",
        ]
        assert param_names == expected


class TestLoadAndFilterData2Filters:
    """load_and_filter_data_2 filter logic using COLUMN_MAP_2 columns."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_edit_month_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        mock_cache.return_value = _make_sample_df2()
        reader = MagicMock()

        result = load_and_filter_data_2(
            reader, "apac-dot-ddd-change-issue-sql",
            selected_months=["2024-02"],
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=None,
            order_type_values=None,
        )
        assert len(result) == 2
        assert all(result["edit month"] == "2024-02")

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_order_types_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        mock_cache.return_value = _make_sample_df2()
        reader = MagicMock()

        result = load_and_filter_data_2(
            reader, "apac-dot-ddd-change-issue-sql",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=None,
            order_type_values=["OrderA"],
        )
        assert len(result) == 2
        assert all(result["order types"] == "OrderA")

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_only_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        mock_cache.return_value = _make_sample_df2()
        reader = MagicMock()

        result = load_and_filter_data_2(
            reader, "apac-dot-ddd-change-issue-sql",
            selected_months=None,
            prc_filter_value="prc_only",
            area_values=None,
            category_values=None,
            vendor_values=None,
            order_type_values=None,
        )
        # PRC-CI-1 and PRC-CI-4
        assert len(result) == 2
        assert all(result["job name"].str.contains("PRC", case=False, na=False))

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_not_included_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        mock_cache.return_value = _make_sample_df2()
        reader = MagicMock()

        result = load_and_filter_data_2(
            reader, "apac-dot-ddd-change-issue-sql",
            selected_months=None,
            prc_filter_value="prc_not_included",
            area_values=None,
            category_values=None,
            vendor_values=None,
            order_type_values=None,
        )
        # Normal-CI-2 and Normal-CI-3
        assert len(result) == 2
        assert not any(result["job name"].str.contains("PRC", case=False, na=False))

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_area_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        mock_cache.return_value = _make_sample_df2()
        reader = MagicMock()

        result = load_and_filter_data_2(
            reader, "apac-dot-ddd-change-issue-sql",
            selected_months=None,
            prc_filter_value="all",
            area_values=["APAC"],
            category_values=None,
            vendor_values=None,
            order_type_values=None,
        )
        assert len(result) == 2
        assert all(result["business area"] == "APAC")

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_category_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        mock_cache.return_value = _make_sample_df2()
        reader = MagicMock()

        result = load_and_filter_data_2(
            reader, "apac-dot-ddd-change-issue-sql",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=["WS-X"],
            vendor_values=None,
            order_type_values=None,
        )
        assert len(result) == 2
        assert all(result["metric workstream"] == "WS-X")

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_vendor_filter(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_and_filter_data_2

        mock_cache.return_value = _make_sample_df2()
        reader = MagicMock()

        result = load_and_filter_data_2(
            reader, "apac-dot-ddd-change-issue-sql",
            selected_months=None,
            prc_filter_value="all",
            area_values=None,
            category_values=None,
            vendor_values=["VendorA"],
            order_type_values=None,
        )
        assert len(result) == 2
        assert all(result["vendor: account name"] == "VendorA")


# ===========================================================================
# load_filter_options extended (dataset_id_2) tests
# ===========================================================================

class TestLoadFilterOptionsExtended:
    """load_filter_options with dataset_id_2 parameter."""

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_months_union_from_both_datasets(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        df1 = _make_sample_df()   # months: 2024-01, 2024-02, 2024-03
        df2 = _make_sample_df2()  # months: 2024-02, 2024-03, 2024-04
        mock_cache.side_effect = [df1, df2]
        reader = MagicMock()

        result = load_filter_options(
            reader, "apac-dot-due-date", dataset_id_2="apac-dot-ddd-change-issue-sql"
        )
        # Union: 2024-01, 2024-02, 2024-03, 2024-04
        assert result["months"] == ["2024-01", "2024-02", "2024-03", "2024-04"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_order_types_from_dataset_2(self, mock_cache):
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        df1 = _make_sample_df()   # order tags: TypeA, TypeB, TypeC
        df2 = _make_sample_df2()  # order types: OrderA, OrderB, OrderC
        mock_cache.side_effect = [df1, df2]
        reader = MagicMock()

        result = load_filter_options(
            reader, "apac-dot-due-date", dataset_id_2="apac-dot-ddd-change-issue-sql"
        )
        # order_types should come from dataset 2 (not dataset 1's "order tags")
        assert result["order_types"] == ["OrderA", "OrderB", "OrderC"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_backward_compatible_without_dataset_id_2(self, mock_cache):
        """When dataset_id_2 is not provided, behavior is unchanged."""
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date")
        # Should work exactly as before
        assert result["months"] == ["2024-01", "2024-02", "2024-03"]
        assert result["order_types"] == ["TypeA", "TypeB", "TypeC"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_dataset_id_2_none_backward_compatible(self, mock_cache):
        """Explicitly passing dataset_id_2=None should be same as not passing it."""
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "apac-dot-due-date", dataset_id_2=None)
        assert result["months"] == ["2024-01", "2024-02", "2024-03"]
        assert result["order_types"] == ["TypeA", "TypeB", "TypeC"]

    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_other_fields_unchanged_with_dataset_id_2(self, mock_cache):
        """Fields other than months and order_types should come from dataset 1."""
        from src.pages.apac_dot_due_date._data_loader import load_filter_options

        df1 = _make_sample_df()
        df2 = _make_sample_df2()
        mock_cache.side_effect = [df1, df2]
        reader = MagicMock()

        result = load_filter_options(
            reader, "apac-dot-due-date", dataset_id_2="apac-dot-ddd-change-issue-sql"
        )
        # areas, workstreams, vendors, amp_vs_av should still come from dataset 1
        assert result["areas"] == ["APAC", "EMEA"]
        assert result["workstreams"] == ["WS-A", "WS-B", "WS-C"]
        assert result["vendors"] == ["Vendor1", "Vendor2", "Vendor3"]
        assert result["amp_vs_av"] == ["AMP", "AV"]
        # counts should still be from dataset 1
        assert result["total_count"] == 5
        assert result["prc_count"] == 2
        assert result["non_prc_count"] == 3
