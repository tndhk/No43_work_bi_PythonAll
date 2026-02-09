"""Callbacks for Hamm Overview dashboard.

This module is the slim orchestration layer.  All chart/table rendering
lives in ``_chart_builders``, data aggregation in ``_data_loader``, and
clear-filter callbacks are registered via ``register_clear_callbacks``.
"""
import pandas as pd
from dash import callback, Input, Output, html

from src.data.parquet_reader import ParquetReader
from src.charts.empty_states import create_empty_figure
from src.utils.callback_helpers import ensure_list, register_clear_callbacks
from src.components.cards import create_kpi_card
from ._constants import (
    CHART_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    CHART_ID_TASK_TABLE,
    CHART_ID_LANGUAGE_TABLE,
    CHART_ID_ERROR_RATIO,
    CHART_ID_ERROR_BY_SCREENER,
    CHART_ID_USER_BREAKDOWN,
    CHART_ID_HAMM_BREAKDOWN,
    CHART_ID_METADATA_ORIGINAL_LANGUAGE,
    CHART_ID_METADATA_DIALOGUE,
    CHART_ID_METADATA_GENRE,
    CHART_ID_KPI_TOTAL_SCREENS,
    CHART_ID_KPI_TOTAL_ERV,
    CHART_ID_KPI_TOTAL_PRELIM,
    FILTER_ID_REGION,
    FILTER_ID_YEAR,
    FILTER_ID_MONTH,
    FILTER_ID_TASK_ID,
    FILTER_ID_CONTENT_TYPE,
    FILTER_ID_ORIGINAL_LANGUAGE,
    FILTER_ID_DIALOGUE,
    FILTER_ID_GENRE,
    FILTER_ID_ERROR_CODE,
    FILTER_ID_ERROR_TYPE,
    FILTER_ID_CADENCE,
    CLEAR_PAIRS,
    SORT_START_COL,
    KPI_COLOR_SCREENS,
    KPI_COLOR_ERV,
    KPI_COLOR_PRELIM,
    PRELIM_LABEL,
    ERV_LABEL,
)
from ._data_loader import (
    resolve_dataset_id_for_dashboard,
    load_and_filter_data,
    build_volume_summary,
    prepare_task_display_df,
    prepare_language_display_df,
    build_issues_ratio,
    build_intervention_by_screener,
    build_user_intervention_breakdown,
    build_hamm_intervention_breakdown,
    build_original_language_distribution,
    build_dialogue_by_content_type,
    build_genre_distribution,
    FILTER_COLUMN_MAP,
)
from ._chart_builders import (
    build_volume_table,
    build_volume_chart,
    build_task_table,
    build_language_table,
    build_error_ratio_chart,
    build_error_by_screener_chart,
    build_user_breakdown_chart,
    build_hamm_breakdown_chart,
    build_original_language_chart,
    build_dialogue_chart,
    build_genre_chart,
)


def _strip_sort_column(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[SORT_START_COL], errors="ignore")


def compute_volume_kpis(filtered_df: pd.DataFrame) -> dict:
    """Volume KPI値を算出（content_type別）

    Args:
        filtered_df: フィルタ適用後のデータフレーム

    Returns:
        total_screens, total_erv, total_prelimを含む辞書
    """
    if len(filtered_df) == 0:
        return {"total_screens": 0, "total_erv": 0, "total_prelim": 0}

    # Import COLUMN_MAP for content_type and status columns
    from ._constants import COLUMN_MAP

    content_type_col = COLUMN_MAP["content_type"]
    status_col = COLUMN_MAP["status"]

    # Exclude Cancelled status (same logic as build_volume_summary)
    df = filtered_df[~filtered_df[status_col].isin(["Cancelled"])]

    # Total screens (all non-cancelled records)
    total_screens = len(df)

    # ERV and Prelim counts by content_type
    erv_count = len(df[df[content_type_col] == ERV_LABEL])
    prelim_count = len(df[df[content_type_col] == PRELIM_LABEL])

    return {
        "total_screens": total_screens,
        "total_erv": erv_count,
        "total_prelim": prelim_count,
    }


@callback(
    Output(CHART_ID_KPI_TOTAL_SCREENS, "children"),
    Output(CHART_ID_KPI_TOTAL_ERV, "children"),
    Output(CHART_ID_KPI_TOTAL_PRELIM, "children"),
    Output(CHART_ID_VOLUME_TABLE, "children"),
    Output(CHART_ID_VOLUME_CHART, "figure"),
    Output(CHART_ID_TASK_TABLE, "children"),
    Output(CHART_ID_ERROR_RATIO, "figure"),
    Output(CHART_ID_ERROR_BY_SCREENER, "figure"),
    Output(CHART_ID_USER_BREAKDOWN, "figure"),
    Output(CHART_ID_HAMM_BREAKDOWN, "figure"),
    Output(CHART_ID_METADATA_ORIGINAL_LANGUAGE, "figure"),
    Output(CHART_ID_METADATA_DIALOGUE, "figure"),
    Output(CHART_ID_METADATA_GENRE, "figure"),
    Output(CHART_ID_LANGUAGE_TABLE, "children"),
    Input(FILTER_ID_REGION, "value"),
    Input(FILTER_ID_YEAR, "value"),
    Input(FILTER_ID_MONTH, "value"),
    Input(FILTER_ID_TASK_ID, "value"),
    Input(FILTER_ID_CONTENT_TYPE, "value"),
    Input(FILTER_ID_ORIGINAL_LANGUAGE, "value"),
    Input(FILTER_ID_DIALOGUE, "value"),
    Input(FILTER_ID_GENRE, "value"),
    Input(FILTER_ID_ERROR_CODE, "value"),
    Input(FILTER_ID_ERROR_TYPE, "value"),
    Input(FILTER_ID_CADENCE, "value"),
)
def update_dashboard(
    region_values,
    year_values,
    month_values,
    task_id_value,
    content_type_values,
    original_language_values,
    dialogue_values,
    genre_values,
    error_code_values,
    error_type_values,
    cadence_value,
):
    reader = ParquetReader()
    dataset_id = resolve_dataset_id_for_dashboard()

    filter_pairs = [
        ("region", ensure_list(region_values)),
        ("year", ensure_list(year_values)),
        ("month", ensure_list(month_values)),
        ("id", ensure_list(task_id_value)),
        ("content_type", ensure_list(content_type_values)),
        ("original_language", ensure_list(original_language_values)),
        ("dialogue", ensure_list(dialogue_values)),
        ("genre", ensure_list(genre_values)),
        ("error_code", ensure_list(error_code_values)),
        ("error_type", ensure_list(error_type_values)),
    ]

    cadence = cadence_value or "weekly"

    try:
        df = load_and_filter_data(
            reader,
            dataset_id,
            FILTER_COLUMN_MAP,
            filter_pairs,
        )

        volume_summary = build_volume_summary(df, cadence)

        # Compute KPI values from filtered data (not volume_summary)
        kpi_values = compute_volume_kpis(df)

        volume_chart_df = _strip_sort_column(volume_summary)
        volume_table_df = _strip_sort_column(
            volume_summary.sort_values(
                by=[SORT_START_COL],
                ascending=False,
                kind="mergesort",
            )
        )

        _, volume_table = build_volume_table(volume_table_df)
        volume_chart = build_volume_chart(volume_chart_df)
        task_display_df = prepare_task_display_df(df)
        _, task_table = build_task_table(task_display_df)

        language_display_df = prepare_language_display_df(df)
        _, language_table = build_language_table(language_display_df)

        # Error analysis
        issues_ratio_df = build_issues_ratio(df)
        intervention_by_screener_df = build_intervention_by_screener(df)
        user_breakdown_df = build_user_intervention_breakdown(df)
        hamm_breakdown_df = build_hamm_intervention_breakdown(df)

        # Build error charts
        error_ratio_fig = build_error_ratio_chart(issues_ratio_df)
        error_by_screener_fig = build_error_by_screener_chart(intervention_by_screener_df)
        user_breakdown_fig = build_user_breakdown_chart(user_breakdown_df)
        hamm_breakdown_fig = build_hamm_breakdown_chart(hamm_breakdown_df)

        # Content metadata analysis
        original_language_df = build_original_language_distribution(df)
        dialogue_df = build_dialogue_by_content_type(df)
        genre_df = build_genre_distribution(df)

        original_language_fig = build_original_language_chart(original_language_df)
        dialogue_fig = build_dialogue_chart(dialogue_df)
        genre_fig = build_genre_chart(genre_df)

        # Create KPI cards
        kpi_screens = create_kpi_card(
            "Total Screens Processed",
            f"{kpi_values['total_screens']:,}",
            bg_color=KPI_COLOR_SCREENS["bg"],
            accent_color=KPI_COLOR_SCREENS["accent"],
        )
        kpi_erv = create_kpi_card(
            "Total ERV Processed",
            f"{kpi_values['total_erv']:,}",
            bg_color=KPI_COLOR_ERV["bg"],
            accent_color=KPI_COLOR_ERV["accent"],
        )
        kpi_prelim = create_kpi_card(
            "Total Prelim Processed",
            f"{kpi_values['total_prelim']:,}",
            bg_color=KPI_COLOR_PRELIM["bg"],
            accent_color=KPI_COLOR_PRELIM["accent"],
        )

        return (
            kpi_screens,
            kpi_erv,
            kpi_prelim,
            volume_table,
            volume_chart,
            task_table,
            error_ratio_fig,
            error_by_screener_fig,
            user_breakdown_fig,
            hamm_breakdown_fig,
            original_language_fig,
            dialogue_fig,
            genre_fig,
            language_table,
        )

    except Exception as exc:
        error_msg = html.P(f"Error loading data: {exc}", className="text-danger")
        empty_fig = create_empty_figure(message="Error loading data")
        return (
            error_msg,
            error_msg,
            error_msg,
            error_msg,
            empty_fig,
            error_msg,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            error_msg,
        )


# ---------------------------------------------------------------------------
# Clear-filter callbacks (registered via shared helper)
# ---------------------------------------------------------------------------
register_clear_callbacks(CLEAR_PAIRS)
