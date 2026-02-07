"""Tests for Cursor Usage callbacks module."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd


def _make_empty_df() -> pd.DataFrame:
    return pd.DataFrame()


@patch("src.pages.cursor_usage._callbacks.load_and_filter_data")
@patch("src.pages.cursor_usage._callbacks.resolve_dataset_id")
@patch("src.pages.cursor_usage._callbacks.ParquetReader")
def test_update_dashboard_uses_registry_dataset_id(
    mock_reader_cls, mock_resolve, mock_load
):
    from src.pages.cursor_usage._callbacks import update_dashboard
    from src.pages.cursor_usage._constants import DASHBOARD_ID, CHART_ID_COST_TREND

    mock_reader_cls.return_value = MagicMock()
    mock_resolve.return_value = "cursor-usage"
    mock_load.return_value = _make_empty_df()

    update_dashboard("2024-01-01", "2024-01-31", ["gpt-4"])

    mock_resolve.assert_called_once_with(DASHBOARD_ID, CHART_ID_COST_TREND)
    args, _ = mock_load.call_args
    assert args[1] == "cursor-usage"
