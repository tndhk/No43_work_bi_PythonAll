"""Tests for Cursor Usage data loader module.

TDD Step 1 (RED): These tests define the expected behavior of
load_filter_options() and load_and_filter_data() before implementation.
The module does not exist yet, so all tests MUST fail with ImportError.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

def _make_sample_df() -> pd.DataFrame:
    """Create a sample DataFrame mimicking the Cursor Usage dataset.

    Includes timezone-aware Date column (as Parquet would return)
    to verify that timezone stripping is handled correctly.
    """
    return pd.DataFrame({
        "Date": pd.to_datetime([
            "2024-01-10 09:00:00",
            "2024-01-15 10:30:00",
            "2024-02-05 14:00:00",
            "2024-02-20 08:15:00",
            "2024-03-01 16:45:00",
        ], utc=True),
        "Model": ["gpt-4", "claude-3", "gpt-4", "claude-3", "gpt-4"],
        "Cost": [0.50, 1.20, 0.80, 0.60, 1.00],
        "Total Tokens": [1000, 2500, 1500, 1200, 2000],
        "User": ["alice", "bob", "alice", "charlie", "bob"],
        "Kind": ["chat", "completion", "chat", "chat", "completion"],
    })


def _make_empty_df() -> pd.DataFrame:
    """Create an empty DataFrame with the expected columns."""
    return pd.DataFrame({
        "Date": pd.Series(dtype="datetime64[ns, UTC]"),
        "Model": pd.Series(dtype="str"),
        "Cost": pd.Series(dtype="float64"),
        "Total Tokens": pd.Series(dtype="int64"),
        "User": pd.Series(dtype="str"),
        "Kind": pd.Series(dtype="str"),
    })


# ===========================================================================
# load_filter_options tests
# ===========================================================================

class TestLoadFilterOptionsReturnStructure:
    """load_filter_options must return a dict with all required keys."""

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_returns_dict(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        assert isinstance(result, dict)

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_has_all_required_keys(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        expected_keys = {"models", "min_date", "max_date"}
        assert set(result.keys()) == expected_keys


class TestLoadFilterOptionsValues:
    """load_filter_options must extract correct values from the dataset."""

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_models_sorted_unique(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        assert result["models"] == ["claude-3", "gpt-4"]

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_models_is_list(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        assert isinstance(result["models"], list)

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_min_date_is_string(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        assert isinstance(result["min_date"], str)

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_max_date_is_string(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        assert isinstance(result["max_date"], str)

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_min_date_value(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        # Earliest date in sample: 2024-01-10
        assert result["min_date"] == "2024-01-10"

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_max_date_value(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        # Latest date in sample: 2024-03-01
        assert result["max_date"] == "2024-03-01"


class TestLoadFilterOptionsException:
    """load_filter_options must return defaults on exception."""

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_returns_defaults_on_exception(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.side_effect = Exception("S3 connection failed")
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        assert result["models"] == []
        assert result["min_date"] is None
        assert result["max_date"] is None


class TestLoadFilterOptionsEdgeCases:
    """load_filter_options edge cases: NaN values, empty data, missing columns."""

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_nan_models_excluded_from_options(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        df = _make_sample_df()
        df.loc[0, "Model"] = None
        mock_cache.return_value = df
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        # None/NaN should be excluded from models list
        assert None not in result["models"]
        # claude-3 still present (rows 1,3), gpt-4 still present (rows 2,4)
        assert "claude-3" in result["models"]
        assert "gpt-4" in result["models"]

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_empty_dataframe_returns_empty_models(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.return_value = _make_empty_df()
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        assert result["models"] == []

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_empty_dataframe_returns_none_dates(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        mock_cache.return_value = _make_empty_df()
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        assert result["min_date"] is None
        assert result["max_date"] is None

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_missing_model_column_returns_empty_list(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_filter_options

        df = _make_sample_df().drop(columns=["Model"])
        mock_cache.return_value = df
        reader = MagicMock()

        result = load_filter_options(reader, "cursor-usage")
        assert result["models"] == []


# ===========================================================================
# load_and_filter_data tests
# ===========================================================================

class TestLoadAndFilterDataBasic:
    """load_and_filter_data must return a DataFrame."""

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_returns_dataframe(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date=None,
            model_values=None,
        )
        assert isinstance(result, pd.DataFrame)

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_no_filters_returns_all_rows(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date=None,
            model_values=None,
        )
        assert len(result) == 5


class TestLoadAndFilterDataTimezone:
    """load_and_filter_data must strip timezone from Date column."""

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_date_column_is_timezone_naive(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date=None,
            model_values=None,
        )
        # Date column must be timezone-naive after processing
        assert result["Date"].dt.tz is None

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_timezone_aware_input_is_converted(self, mock_cache):
        """Verify that UTC-aware input from Parquet is properly handled."""
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        df = _make_sample_df()
        # Confirm input IS timezone-aware
        assert df["Date"].dt.tz is not None

        mock_cache.return_value = df
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date=None,
            model_values=None,
        )
        # Output MUST be timezone-naive
        assert result["Date"].dt.tz is None


class TestLoadAndFilterDataDateFilter:
    """load_and_filter_data date range filter logic."""

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_start_and_end_date_filter(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date="2024-01-01",
            end_date="2024-01-31",
            model_values=None,
        )
        # Only January rows: 2024-01-10 and 2024-01-15
        assert len(result) == 2

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_start_date_boundary_inclusive(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date="2024-01-10",
            end_date="2024-03-01",
            model_values=None,
        )
        # start_date is inclusive, so row with 2024-01-10 should be included
        assert len(result) == 5

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_end_date_boundary_inclusive(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date="2024-03-01",
            end_date="2024-03-01",
            model_values=None,
        )
        # end_date is inclusive, row at 2024-03-01 16:45:00 should be included
        assert len(result) == 1

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_narrow_date_range_excludes_out_of_range(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date="2024-02-01",
            end_date="2024-02-28",
            model_values=None,
        )
        # February rows: 2024-02-05 and 2024-02-20
        assert len(result) == 2


class TestLoadAndFilterDataModelFilter:
    """load_and_filter_data model filter logic."""

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_single_model_filter(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date=None,
            model_values=["gpt-4"],
        )
        assert len(result) == 3
        assert all(result["Model"] == "gpt-4")

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_multiple_model_filter(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date=None,
            model_values=["gpt-4", "claude-3"],
        )
        # All rows match either model
        assert len(result) == 5

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_nonexistent_model_returns_empty(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date=None,
            model_values=["nonexistent-model"],
        )
        assert len(result) == 0


class TestLoadAndFilterDataCombinedFilters:
    """load_and_filter_data with multiple filters combined."""

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_date_plus_model_combined(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date="2024-01-01",
            end_date="2024-01-31",
            model_values=["gpt-4"],
        )
        # January + gpt-4: only row 0 (2024-01-10, gpt-4)
        assert len(result) == 1
        assert result.iloc[0]["Model"] == "gpt-4"

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_combined_filters_no_match_returns_empty(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date="2024-03-01",
            end_date="2024-03-31",
            model_values=["claude-3"],
        )
        # March has only gpt-4 (row 4), no claude-3 in March
        assert len(result) == 0


class TestLoadAndFilterDataEdgeCases:
    """load_and_filter_data edge cases."""

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_empty_list_model_treated_as_no_filter(self, mock_cache):
        """Empty list [] should not filter (same as None)."""
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date=None,
            model_values=[],
        )
        # Empty list should be treated same as None -> no filtering
        assert len(result) == 5

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_only_start_date_without_end_date_no_date_filter(self, mock_cache):
        """If only start_date is provided (end_date is None), no date filter applied."""
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date="2024-02-01",
            end_date=None,
            model_values=None,
        )
        # Both start_date AND end_date are required for date filter
        assert len(result) == 5

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_only_end_date_without_start_date_no_date_filter(self, mock_cache):
        """If only end_date is provided (start_date is None), no date filter applied."""
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date="2024-02-28",
            model_values=None,
        )
        # Both start_date AND end_date are required for date filter
        assert len(result) == 5

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_date_only_column_created(self, mock_cache):
        """DateOnly column should be created for date-based grouping."""
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_sample_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date=None,
            model_values=None,
        )
        assert "DateOnly" in result.columns

    @patch("src.pages.cursor_usage._data_loader.get_cached_dataset")
    def test_empty_dataframe_returns_empty(self, mock_cache):
        from src.pages.cursor_usage._data_loader import load_and_filter_data

        mock_cache.return_value = _make_empty_df()
        reader = MagicMock()

        result = load_and_filter_data(
            reader, "cursor-usage",
            start_date=None,
            end_date=None,
            model_values=None,
        )
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)
