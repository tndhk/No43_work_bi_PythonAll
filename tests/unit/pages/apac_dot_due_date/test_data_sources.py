"""Tests for APAC DOT Due Date data_sources.yml mapping."""
from __future__ import annotations

from src.data.data_source_registry import load_dashboard_config
from src.pages.apac_dot_due_date import _constants as const


def test_data_sources_contains_expected_chart_ids():
    """data_sources.yml must include the reference table chart ID."""
    load_dashboard_config.cache_clear()
    config = load_dashboard_config(const.DASHBOARD_ID)
    chart_ids = set(config["charts"].keys())
    assert chart_ids == {const.CHART_ID_REFERENCE_TABLE}
