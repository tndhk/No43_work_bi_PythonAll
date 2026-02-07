"""Tests for Cursor Usage data_sources.yml and dataset mapping."""
from __future__ import annotations

from unittest.mock import call, patch

from src.data.data_source_registry import load_dashboard_config
from src.pages.cursor_usage import _constants as const


def test_data_sources_contains_all_chart_ids():
    """data_sources.yml must include every chart ID defined in constants."""
    load_dashboard_config.cache_clear()
    config = load_dashboard_config(const.DASHBOARD_ID)
    chart_ids = set(config["charts"].keys())
    expected = {
        const.CHART_ID_KPI_TOTAL_COST,
        const.CHART_ID_KPI_TOTAL_TOKENS,
        const.CHART_ID_KPI_REQUEST_COUNT,
        const.CHART_ID_COST_TREND,
        const.CHART_ID_TOKEN_EFFICIENCY,
        const.CHART_ID_MODEL_DISTRIBUTION,
        const.CHART_ID_DATA_TABLE,
    }
    assert chart_ids == expected


@patch("src.pages.cursor_usage._data_loader.resolve_dataset_id")
def test_resolve_dataset_id_for_dashboard_uses_all_chart_ids(mock_resolve):
    """resolve_dataset_id_for_dashboard must resolve all chart IDs."""
    from src.pages.cursor_usage._data_loader import resolve_dataset_id_for_dashboard

    mock_resolve.return_value = "cursor-usage"

    result = resolve_dataset_id_for_dashboard()

    assert result == "cursor-usage"
    expected_calls = [
        call(const.DASHBOARD_ID, const.CHART_ID_KPI_TOTAL_COST),
        call(const.DASHBOARD_ID, const.CHART_ID_KPI_TOTAL_TOKENS),
        call(const.DASHBOARD_ID, const.CHART_ID_KPI_REQUEST_COUNT),
        call(const.DASHBOARD_ID, const.CHART_ID_COST_TREND),
        call(const.DASHBOARD_ID, const.CHART_ID_TOKEN_EFFICIENCY),
        call(const.DASHBOARD_ID, const.CHART_ID_MODEL_DISTRIBUTION),
        call(const.DASHBOARD_ID, const.CHART_ID_DATA_TABLE),
    ]
    mock_resolve.assert_has_calls(expected_calls, any_order=True)
    assert mock_resolve.call_count == len(expected_calls)
