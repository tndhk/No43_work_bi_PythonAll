"""Tests for data_helpers module."""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

from src.utils.data_helpers import (
    safe_load_filter_options,
    strip_timezone,
    resolve_single_dataset_id,
)


class TestSafeLoadFilterOptions:
    """safe_load_filter_options must extract unique values safely."""

    @patch("src.utils.data_helpers.get_cached_dataset")
    def test_extracts_unique_values(self, mock_cache):
        df = pd.DataFrame({
            "Month": ["2024-01", "2024-01", "2024-02"],
            "Area": ["APAC", "EMEA", "APAC"],
        })
        mock_cache.return_value = df
        reader = MagicMock()

        result = safe_load_filter_options(
            reader,
            "test-dataset",
            {"months": "Month", "areas": "Area"},
        )

        assert result["months"] == ["2024-01", "2024-02"]
        assert result["areas"] == ["APAC", "EMEA"]

    @patch("src.utils.data_helpers.get_cached_dataset")
    def test_returns_empty_lists_on_exception(self, mock_cache):
        mock_cache.side_effect = Exception("Connection failed")
        reader = MagicMock()

        result = safe_load_filter_options(
            reader,
            "test-dataset",
            {"months": "Month", "areas": "Area"},
        )

        assert result["months"] == []
        assert result["areas"] == []

    @patch("src.utils.data_helpers.get_cached_dataset")
    def test_applies_prepare_fn(self, mock_cache):
        df = pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=3, tz="UTC"),
        })
        mock_cache.return_value = df
        reader = MagicMock()

        def prepare_fn(df):
            df["Date"] = df["Date"].dt.tz_convert(None)
            return df

        result = safe_load_filter_options(
            reader,
            "test-dataset",
            {"dates": "Date"},
            prepare_fn=prepare_fn,
        )

        assert len(result["dates"]) == 3
        # Dates should be timezone-naive after prepare_fn
        assert np.issubdtype(df["Date"].dtype, np.datetime64)


class TestStripTimezone:
    """strip_timezone must convert timezone-aware to naive."""

    def test_strips_timezone(self):
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=3, tz="UTC"),
        })
        result = strip_timezone(df, "date")
        assert np.issubdtype(result["date"].dtype, np.datetime64)
        assert result["date"].dt.tz is None

    def test_missing_column_no_error(self):
        df = pd.DataFrame({"other": [1, 2, 3]})
        result = strip_timezone(df, "date")
        assert "date" not in result.columns

    def test_returns_copy(self):
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=3, tz="UTC"),
        })
        result = strip_timezone(df, "date")
        assert result is not df


class TestResolveSingleDatasetId:
    """resolve_single_dataset_id must validate single dataset."""

    @patch("src.utils.data_helpers.resolve_dataset_id")
    def test_single_dataset_id(self, mock_resolve):
        mock_resolve.side_effect = lambda dash_id, chart_id: "same-dataset-id"
        result = resolve_single_dataset_id("dashboard", ["chart1", "chart2"])
        assert result == "same-dataset-id"

    @patch("src.utils.data_helpers.resolve_dataset_id")
    def test_multiple_dataset_ids_raises(self, mock_resolve):
        mock_resolve.side_effect = lambda dash_id, chart_id: (
            "dataset-1" if chart_id == "chart1" else "dataset-2"
        )
        with pytest.raises(ValueError, match="Multiple dataset IDs"):
            resolve_single_dataset_id("dashboard", ["chart1", "chart2"])
