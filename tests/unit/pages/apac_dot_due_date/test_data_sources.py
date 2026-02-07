"""Tests for APAC DOT Due Date data_sources.yml mapping."""
from __future__ import annotations

from src.data.data_source_registry import load_dashboard_config, get_dataset_id
from src.pages.apac_dot_due_date import _constants as const


def test_data_sources_contains_expected_chart_ids():
    """data_sources.yml must include both chart-00 and chart-01 chart IDs."""
    load_dashboard_config.cache_clear()
    config = load_dashboard_config(const.DASHBOARD_ID)
    chart_ids = set(config["charts"].keys())
    assert chart_ids == {const.CHART_ID_REFERENCE_TABLE, const.CHART_ID_CHANGE_ISSUE_TABLE}


def test_chart_01_maps_to_dataset_id_2():
    """chart-01 (change-issue table) must resolve to DATASET_ID_2."""
    load_dashboard_config.cache_clear()
    dataset_id = get_dataset_id(const.DASHBOARD_ID, const.CHART_ID_CHANGE_ISSUE_TABLE)
    assert dataset_id == const.DATASET_ID_2
