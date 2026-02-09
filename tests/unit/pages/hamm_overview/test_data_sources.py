"""Tests for Hamm Overview data_sources.yml and dataset mapping."""
from unittest.mock import call, patch

from src.data.data_source_registry import load_dashboard_config
from src.pages.hamm_overview import _constants as const


def test_data_sources_contains_all_chart_ids():
    load_dashboard_config.cache_clear()
    config = load_dashboard_config(const.DASHBOARD_ID)
    chart_ids = set(config["charts"].keys())
    expected = {
        const.CHART_ID_VOLUME_TABLE,
        const.CHART_ID_VOLUME_CHART,
        const.CHART_ID_KPI_TOTAL_SCREENS,
        const.CHART_ID_KPI_TOTAL_ERV,
        const.CHART_ID_KPI_TOTAL_PRELIM,
        const.CHART_ID_TASK_TABLE,
        const.CHART_ID_LANGUAGE_TABLE,
        const.CHART_ID_ERROR_RATIO,
        const.CHART_ID_ERROR_BY_SCREENER,
        const.CHART_ID_USER_BREAKDOWN,
        const.CHART_ID_HAMM_BREAKDOWN,
        const.CHART_ID_METADATA_ORIGINAL_LANGUAGE,
        const.CHART_ID_METADATA_DIALOGUE,
        const.CHART_ID_METADATA_GENRE,
    }
    assert chart_ids == expected


@patch("src.pages.hamm_overview._data_loader.resolve_dataset_id")
def test_resolve_dataset_id_for_dashboard_uses_all_chart_ids(mock_resolve):
    from src.pages.hamm_overview._data_loader import resolve_dataset_id_for_dashboard

    mock_resolve.return_value = "hamm-dashboard"

    result = resolve_dataset_id_for_dashboard()

    assert result == "hamm-dashboard"
    expected_calls = [
        call(const.DASHBOARD_ID, const.CHART_ID_VOLUME_TABLE),
        call(const.DASHBOARD_ID, const.CHART_ID_VOLUME_CHART),
        call(const.DASHBOARD_ID, const.CHART_ID_KPI_TOTAL_SCREENS),
        call(const.DASHBOARD_ID, const.CHART_ID_KPI_TOTAL_ERV),
        call(const.DASHBOARD_ID, const.CHART_ID_KPI_TOTAL_PRELIM),
        call(const.DASHBOARD_ID, const.CHART_ID_TASK_TABLE),
        call(const.DASHBOARD_ID, const.CHART_ID_LANGUAGE_TABLE),
        call(const.DASHBOARD_ID, const.CHART_ID_ERROR_RATIO),
        call(const.DASHBOARD_ID, const.CHART_ID_ERROR_BY_SCREENER),
        call(const.DASHBOARD_ID, const.CHART_ID_USER_BREAKDOWN),
        call(const.DASHBOARD_ID, const.CHART_ID_HAMM_BREAKDOWN),
        call(const.DASHBOARD_ID, const.CHART_ID_METADATA_ORIGINAL_LANGUAGE),
        call(const.DASHBOARD_ID, const.CHART_ID_METADATA_DIALOGUE),
        call(const.DASHBOARD_ID, const.CHART_ID_METADATA_GENRE),
    ]
    mock_resolve.assert_has_calls(expected_calls, any_order=True)
    assert mock_resolve.call_count == len(expected_calls)


# ---------------------------------------------------------------------------
# Language Table data source mapping (RED -- not yet implemented)
# ---------------------------------------------------------------------------

def test_data_sources_contains_language_table():
    """hamm-language-table must be mapped to hamm-dashboard in data_sources.yml."""
    load_dashboard_config.cache_clear()
    config = load_dashboard_config(const.DASHBOARD_ID)
    chart_ids = set(config["charts"].keys())
    assert "hamm-language-table" in chart_ids, (
        f"hamm-language-table not found in data_sources.yml charts. "
        f"Found: {sorted(chart_ids)}"
    )


def test_language_table_maps_to_hamm_dashboard():
    """hamm-language-table should map to hamm-dashboard dataset."""
    load_dashboard_config.cache_clear()
    config = load_dashboard_config(const.DASHBOARD_ID)
    assert config["charts"].get("hamm-language-table") == "hamm-dashboard"
