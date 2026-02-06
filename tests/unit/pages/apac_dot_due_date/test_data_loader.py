"""Tests for APAC DOT Due Date data loader module.

TDD Step 1 (RED): These tests define the expected behavior of
load_filter_options() and load_and_filter_data() before implementation.
"""
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
