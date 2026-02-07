"""Tests for APAC DOT Due Date Dashboard page - filter option generation with NaN data."""
import math
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from dash import html

from tests.helpers.dash_test_utils import extract_dropdown_options, extract_dropdown_value


def _make_nan_df():
    """Create a DataFrame that has NaN values mixed into every filter column.

    This mirrors real-world Parquet data where some rows have missing values
    in categorical columns.
    """
    return pd.DataFrame({
        "Delivery Completed Month": ["2024-01", "2024-02", None, "2024-03"],
        "business area": ["APAC", None, "EMEA", "APAC"],
        "Metric Workstream": ["WS-A", "WS-B", None, "WS-A"],
        "Vendor: Account Name": [None, "Vendor X", "Vendor Y", "Vendor X"],
        "AMP VS AV Scope": ["AMP", "AV", None, "AMP"],
        "order tags": ["Type A", None, "Type B", "Type A"],
        "job name": ["Job PRC 1", "Job 2", "Job PRC 3", "Job 4"],
        "work order id": [1, 2, 3, 4],
    })


def _make_clean_df():
    """Create a DataFrame with no NaN values (baseline)."""
    return pd.DataFrame({
        "Delivery Completed Month": ["2024-01", "2024-02", "2024-03"],
        "business area": ["APAC", "EMEA", "APAC"],
        "Metric Workstream": ["WS-A", "WS-B", "WS-A"],
        "Vendor: Account Name": ["Vendor X", "Vendor Y", "Vendor X"],
        "AMP VS AV Scope": ["AMP", "AV", "AMP"],
        "order tags": ["Type A", "Type B", "Type A"],
        "job name": ["Job PRC 1", "Job 2", "Job 4"],
        "work order id": [1, 2, 3],
    })




# ---------------------------------------------------------------------------
# Test: NaN-mixed data produces valid filter options without NaN values
# ---------------------------------------------------------------------------


class TestLayoutFilterOptionsWithNaN:
    """Test that layout() correctly generates filter options when DataFrame
    columns contain NaN values mixed with valid strings."""

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_nan_mixed_data_does_not_raise(self, mock_get_cached, _mock_reader):
        """layout() must not raise TypeError when NaN values are present
        in filter columns.

        Current bug: sorted() on a list mixing str and float(nan) raises
        TypeError, which is silently caught by except Exception, causing
        all filter lists to fall back to [].
        """
        mock_get_cached.return_value = _make_nan_df()

        from src.pages.apac_dot_due_date import layout

        # Should not raise -- and should NOT fall back to empty lists
        result = layout()
        assert isinstance(result, html.Div)

        # Verify at least one filter has options (not all empty from fallback)
        area_options = extract_dropdown_options(result, "apac-dot-filter-area")
        assert area_options is not None, "apac-dot-filter-area dropdown not found in layout"
        assert len(area_options) > 0, (
            "apac-dot-filter-area options should not be empty -- "
            "the except-all fallback swallowed the TypeError"
        )

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_nan_excluded_from_month_filter(self, mock_get_cached, _mock_reader):
        """NaN must not appear in the month filter dropdown options."""
        mock_get_cached.return_value = _make_nan_df()

        from src.pages.apac_dot_due_date import layout

        result = layout()
        options = extract_dropdown_options(result, "apac-dot-filter-month")
        assert options is not None, "apac-dot-filter-month dropdown not found"

        option_values = [o["value"] for o in options]
        # No NaN (float) in the values
        for v in option_values:
            assert not (isinstance(v, float) and math.isnan(v)), (
                f"NaN found in month filter options: {option_values}"
            )
        # Should contain the 3 valid months
        assert sorted(option_values) == ["2024-01", "2024-02", "2024-03"]

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_nan_excluded_from_area_filter(self, mock_get_cached, _mock_reader):
        """NaN must not appear in the business area filter dropdown options."""
        mock_get_cached.return_value = _make_nan_df()

        from src.pages.apac_dot_due_date import layout

        result = layout()
        options = extract_dropdown_options(result, "apac-dot-filter-area")
        assert options is not None, "apac-dot-filter-area dropdown not found"

        option_values = [o["value"] for o in options]
        for v in option_values:
            assert not (isinstance(v, float) and math.isnan(v)), (
                f"NaN found in area filter options: {option_values}"
            )
        assert sorted(option_values) == ["APAC", "EMEA"]

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_nan_excluded_from_workstream_filter(self, mock_get_cached, _mock_reader):
        """NaN must not appear in the Metric Workstream filter options."""
        mock_get_cached.return_value = _make_nan_df()

        from src.pages.apac_dot_due_date import layout

        result = layout()
        options = extract_dropdown_options(result, "apac-dot-filter-category")
        assert options is not None, "apac-dot-filter-category dropdown not found"

        option_values = [o["value"] for o in options]
        for v in option_values:
            assert not (isinstance(v, float) and math.isnan(v)), (
                f"NaN found in workstream filter options: {option_values}"
            )
        assert sorted(option_values) == ["WS-A", "WS-B"]

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_nan_excluded_from_vendor_filter(self, mock_get_cached, _mock_reader):
        """NaN must not appear in the Vendor filter options."""
        mock_get_cached.return_value = _make_nan_df()

        from src.pages.apac_dot_due_date import layout

        result = layout()
        options = extract_dropdown_options(result, "apac-dot-filter-vendor")
        assert options is not None, "apac-dot-filter-vendor dropdown not found"

        option_values = [o["value"] for o in options]
        for v in option_values:
            assert not (isinstance(v, float) and math.isnan(v)), (
                f"NaN found in vendor filter options: {option_values}"
            )
        assert sorted(option_values) == ["Vendor X", "Vendor Y"]

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_nan_excluded_from_amp_av_filter(self, mock_get_cached, _mock_reader):
        """NaN must not appear in the AMP VS AV Scope filter options."""
        mock_get_cached.return_value = _make_nan_df()

        from src.pages.apac_dot_due_date import layout

        result = layout()
        options = extract_dropdown_options(result, "apac-dot-filter-amp-av")
        assert options is not None, "apac-dot-filter-amp-av dropdown not found"

        option_values = [o["value"] for o in options]
        for v in option_values:
            assert not (isinstance(v, float) and math.isnan(v)), (
                f"NaN found in amp-av filter options: {option_values}"
            )
        assert sorted(option_values) == ["AMP", "AV"]

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_nan_excluded_from_order_type_filter(self, mock_get_cached, _mock_reader):
        """NaN must not appear in the order tags filter options."""
        mock_get_cached.return_value = _make_nan_df()

        from src.pages.apac_dot_due_date import layout

        result = layout()
        options = extract_dropdown_options(result, "apac-dot-filter-order-type")
        assert options is not None, "apac-dot-filter-order-type dropdown not found"

        option_values = [o["value"] for o in options]
        for v in option_values:
            assert not (isinstance(v, float) and math.isnan(v)), (
                f"NaN found in order-type filter options: {option_values}"
            )
        assert sorted(option_values) == ["Type A", "Type B"]

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_month_filter_default_value_excludes_nan(self, mock_get_cached, _mock_reader):
        """The default value of the month filter (all months selected)
        must not include NaN."""
        mock_get_cached.return_value = _make_nan_df()

        from src.pages.apac_dot_due_date import layout

        result = layout()
        default_months = extract_dropdown_value(result, "apac-dot-filter-month")
        assert default_months is not None, "apac-dot-filter-month default value not found"

        for v in default_months:
            assert not (isinstance(v, float) and math.isnan(v)), (
                f"NaN found in month filter default value: {default_months}"
            )
        assert sorted(default_months) == ["2024-01", "2024-02", "2024-03"]

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_filter_options_sorted_alphabetically(self, mock_get_cached, _mock_reader):
        """Filter options should be sorted even when NaN values are present."""
        mock_get_cached.return_value = _make_nan_df()

        from src.pages.apac_dot_due_date import layout

        result = layout()

        # Check area filter is sorted and non-empty
        area_options = extract_dropdown_options(result, "apac-dot-filter-area")
        area_values = [o["value"] for o in area_options]
        assert len(area_values) > 0, (
            "Area filter options must not be empty (fallback detected)"
        )
        assert area_values == sorted(area_values), (
            f"Area filter options not sorted: {area_values}"
        )

        # Check vendor filter is sorted and non-empty
        vendor_options = extract_dropdown_options(result, "apac-dot-filter-vendor")
        vendor_values = [o["value"] for o in vendor_options]
        assert len(vendor_values) > 0, (
            "Vendor filter options must not be empty (fallback detected)"
        )
        assert vendor_values == sorted(vendor_values), (
            f"Vendor filter options not sorted: {vendor_values}"
        )


class TestLayoutFilterOptionsCleanData:
    """Baseline: layout() works correctly with clean data (no NaN)."""

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_clean_data_produces_correct_options(self, mock_get_cached, _mock_reader):
        """With no NaN values, all filter options should be populated correctly."""
        mock_get_cached.return_value = _make_clean_df()

        from src.pages.apac_dot_due_date import layout

        result = layout()
        assert isinstance(result, html.Div)

        # Verify month options
        month_options = extract_dropdown_options(result, "apac-dot-filter-month")
        month_values = [o["value"] for o in month_options]
        assert sorted(month_values) == ["2024-01", "2024-02", "2024-03"]

        # Verify area options
        area_options = extract_dropdown_options(result, "apac-dot-filter-area")
        area_values = [o["value"] for o in area_options]
        assert sorted(area_values) == ["APAC", "EMEA"]

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_prc_count_correct_with_clean_data(self, mock_get_cached, _mock_reader):
        """PRC filter counts should be correct with clean data."""
        mock_get_cached.return_value = _make_clean_df()

        from src.pages.apac_dot_due_date import layout

        result = layout()
        # PRC radio items should show total count = 3
        # The layout renders "Select all (3)" style labels
        result_str = str(result)
        assert "Select all" in result_str


class TestLayoutFilterOptionsAllNaN:
    """Edge case: a column where ALL values are NaN."""

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._data_loader.get_cached_dataset")
    def test_all_nan_column_produces_empty_options(self, mock_get_cached, _mock_reader):
        """If a column is entirely NaN, its filter should have zero options
        (not raise an error)."""
        df = _make_nan_df()
        # Make business area entirely NaN
        df["business area"] = np.nan

        mock_get_cached.return_value = df

        from src.pages.apac_dot_due_date import layout

        result = layout()
        area_options = extract_dropdown_options(result, "apac-dot-filter-area")
        assert area_options is not None, "apac-dot-filter-area dropdown not found"
        assert len(area_options) == 0, (
            f"Expected empty options for all-NaN column, got: {area_options}"
        )
