"""Build DashboardContext for HAMM Overview page."""
from __future__ import annotations

import pandas as pd

from src.llm.page_context import DashboardContext, KPIValue
from src.pages.hamm_overview._custom_logic import compute_volume_kpis

# Filter state key -> display name mapping
_FILTER_DISPLAY_NAMES: dict[str, str] = {
    "filter_region_values": "Region",
    "filter_year_values": "Year",
    "filter_content_type_values": "Content Type",
    "filter_original_language_values": "Original Language",
    "filter_dialogue_values": "Dialogue",
    "filter_genre_values": "Genre",
    "filter_error_type_values": "Error Type",
    "filter_month_values": "Month",
    "filter_task_id_values": "Task ID",
    "filter_error_code_values": "Error Code",
    "filter_cadence_values": "Cadence",
}

PAGE_DESCRIPTION = (
    "HAMM Overview - "
    "スクリーン処理のボリューム、エラー分析、コンテンツメタデータを表示するダッシュボード"
)


def build_hamm_dashboard_context(
    df: pd.DataFrame,
    filter_state: dict | None,
) -> DashboardContext:
    """Build DashboardContext for the HAMM Overview page.

    Args:
        df: Filtered DataFrame currently displayed.
        filter_state: Current filter selections from chat-filter-state-hamm store.

    Returns:
        DashboardContext with KPI values and active filter info.
    """
    # Compute KPIs
    kpis_dict = compute_volume_kpis(df)

    kpis = [
        KPIValue(
            name="Total Screens Processed",
            value=f"{kpis_dict['total_screens']:,}",
            logic="Cancelledステータスを除外した全レコード数",
        ),
        KPIValue(
            name="Total ERV Processed",
            value=f"{kpis_dict['total_erv']:,}",
            logic='Cancelled除外、content_type="ERV"のレコード数',
        ),
        KPIValue(
            name="Total Prelim Processed",
            value=f"{kpis_dict['total_prelim']:,}",
            logic='Cancelled除外、content_type="Prelim"のレコード数',
        ),
    ]

    # Build active filters
    active_filters: dict[str, list[str] | str | None] = {}
    if filter_state:
        for key, display_name in _FILTER_DISPLAY_NAMES.items():
            values = filter_state.get(key)
            if isinstance(values, list) and len(values) > 0:
                active_filters[display_name] = [str(v) for v in values]
            elif isinstance(values, str):
                active_filters[display_name] = values
            else:
                active_filters[display_name] = None

    return DashboardContext(
        page_description=PAGE_DESCRIPTION,
        kpis=kpis,
        active_filters=active_filters,
    )
