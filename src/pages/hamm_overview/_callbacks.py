"""Callbacks for HAMM Overview dashboard.

Auto-generated from page_spec.yaml by tools.page_generator.

This module is the slim orchestration layer. All chart/table rendering
lives in ``_chart_builders``, data aggregation in ``_data_loader``, and
clear-filter callbacks are registered via ``register_clear_callbacks``.
"""
import pandas as pd
from dash import callback, Input, Output, html
from src.data.parquet_reader import ParquetReader
from src.charts.empty_states import create_error_figure
from src.utils.callback_helpers import ensure_list, register_clear_callbacks
from src.components.cards import create_kpi_card
from ._constants import (
    COLUMN_MAP,
    ERV_LABEL,
    PRELIM_LABEL,
    KPI_ID_KPI_TOTAL_SCREENS,
    KPI_ID_KPI_TOTAL_ERV,
    KPI_ID_KPI_TOTAL_PRELIM,
    TABLE_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    TABLE_ID_TASK_TABLE,
    TABLE_ID_LANGUAGE_TABLE,
    CHART_ID_LANGUAGE_TABLE,
    CHART_ID_ERROR_RATIO,
    CHART_ID_ERROR_BY_SCREENER,
    CHART_ID_USER_BREAKDOWN,
    CHART_ID_BREAKDOWN,
    CHART_ID_METADATA_ORIGINAL_LANGUAGE,
    CHART_ID_METADATA_DIALOGUE,
    CHART_ID_METADATA_GENRE,
    FILTER_ID_FILTER_REGION,
    FILTER_ID_FILTER_YEAR,
    FILTER_ID_FILTER_CONTENT_TYPE,
    FILTER_ID_FILTER_ORIGINAL_LANGUAGE,
    FILTER_ID_FILTER_DIALOGUE,
    FILTER_ID_FILTER_GENRE,
    FILTER_ID_FILTER_ERROR_TYPE,
    FILTER_ID_FILTER_MONTH,
    FILTER_ID_FILTER_TASK_ID,
    FILTER_ID_FILTER_ERROR_CODE,
    FILTER_ID_FILTER_CADENCE,
    CLEAR_PAIRS,
)
from ._data_loader import (
    resolve_dataset_id_for_dashboard,
    load_and_filter_data,
    FILTER_COLUMN_MAP,
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


@callback(
    Output(KPI_ID_KPI_TOTAL_SCREENS, "children"),
    Output(KPI_ID_KPI_TOTAL_ERV, "children"),
    Output(KPI_ID_KPI_TOTAL_PRELIM, "children"),
    Output(TABLE_ID_VOLUME_TABLE, "children"),
    Output(CHART_ID_VOLUME_CHART, "figure"),
    Output(TABLE_ID_TASK_TABLE, "children"),
    Output(CHART_ID_LANGUAGE_TABLE, "children"),
    Output(CHART_ID_ERROR_RATIO, "figure"),
    Output(CHART_ID_ERROR_BY_SCREENER, "figure"),
    Output(CHART_ID_USER_BREAKDOWN, "figure"),
    Output(CHART_ID_BREAKDOWN, "figure"),
    Output(CHART_ID_METADATA_ORIGINAL_LANGUAGE, "figure"),
    Output(CHART_ID_METADATA_DIALOGUE, "figure"),
    Output(CHART_ID_METADATA_GENRE, "figure"),
    Input(FILTER_ID_FILTER_REGION, "value"),
    Input(FILTER_ID_FILTER_YEAR, "value"),
    Input(FILTER_ID_FILTER_CONTENT_TYPE, "value"),
    Input(FILTER_ID_FILTER_ORIGINAL_LANGUAGE, "value"),
    Input(FILTER_ID_FILTER_DIALOGUE, "value"),
    Input(FILTER_ID_FILTER_GENRE, "value"),
    Input(FILTER_ID_FILTER_ERROR_TYPE, "value"),
    Input(FILTER_ID_FILTER_MONTH, "value"),
    Input(FILTER_ID_FILTER_TASK_ID, "value"),
    Input(FILTER_ID_FILTER_ERROR_CODE, "value"),
    Input(FILTER_ID_FILTER_CADENCE, "value"),
)
def update_dashboard(
    filter_region_values,
    filter_year_values,
    filter_content_type_values,
    filter_original_language_values,
    filter_dialogue_values,
    filter_genre_values,
    filter_error_type_values,
    filter_month_values,
    filter_task_id_values,
    filter_error_code_values,
    filter_cadence_values,
):
    """Update all dashboard components based on filter selections.

    Auto-generated from page_spec.yaml components and filters.
    """
    reader = ParquetReader()
    dataset_id = resolve_dataset_id_for_dashboard()

    filter_pairs = [
        ("region", ensure_list(filter_region_values)),
        ("year", ensure_list(filter_year_values)),
        ("content_type", ensure_list(filter_content_type_values)),
        ("original_language", ensure_list(filter_original_language_values)),
        ("dialogue", ensure_list(filter_dialogue_values)),
        ("genre", ensure_list(filter_genre_values)),
        ("error_type", ensure_list(filter_error_type_values)),
        ("month", ensure_list(filter_month_values)),
        ("id", ensure_list(filter_task_id_values)),
        ("error_code", ensure_list(filter_error_code_values)),
    ]

    cadence = filter_cadence_values or "weekly"

    try:
        df = load_and_filter_data(
            reader,
            dataset_id,
            FILTER_COLUMN_MAP,
            filter_pairs,
        )

        # KPI values via compute_volume_kpis
        kpis = compute_volume_kpis(df)
        kpi_total_screens_card = create_kpi_card(
            "Total Screens Processed",
            f"{kpis['total_screens']:,}",
        )
        kpi_total_erv_card = create_kpi_card(
            "Total ERV Processed",
            f"{kpis['total_erv']:,}",
        )
        kpi_total_prelim_card = create_kpi_card(
            "Total Prelim Processed",
            f"{kpis['total_prelim']:,}",
        )

        # Volume Summary table and chart
        volume_summary_df = build_volume_summary(df, cadence)
        _, volume_table_component = build_volume_table(volume_summary_df)
        volume_chart_fig = build_volume_chart(volume_summary_df)

        # Task Details table
        task_display_df = prepare_task_display_df(df)
        _, task_table_component = build_task_table(task_display_df)

        # Language Details table
        language_display_df = prepare_language_display_df(df)
        _, language_table_component = build_language_table(language_display_df)

        # Error charts
        error_ratio_df = build_issues_ratio(df)
        error_ratio_fig = build_error_ratio_chart(error_ratio_df)

        error_by_screener_df = build_intervention_by_screener(df)
        error_by_screener_fig = build_error_by_screener_chart(error_by_screener_df)

        user_breakdown_df = build_user_intervention_breakdown(df)
        user_breakdown_fig = build_user_breakdown_chart(user_breakdown_df)

        hamm_breakdown_df = build_hamm_intervention_breakdown(df)
        hamm_breakdown_fig = build_hamm_breakdown_chart(hamm_breakdown_df)

        # Content Metadata charts
        original_language_df = build_original_language_distribution(df)
        original_language_fig = build_original_language_chart(original_language_df)

        dialogue_df = build_dialogue_by_content_type(df)
        dialogue_fig = build_dialogue_chart(dialogue_df)

        genre_df = build_genre_distribution(df)
        genre_fig = build_genre_chart(genre_df)

        return (
            kpi_total_screens_card,
            kpi_total_erv_card,
            kpi_total_prelim_card,
            volume_table_component,
            volume_chart_fig,
            task_table_component,
            language_table_component,
            error_ratio_fig,
            error_by_screener_fig,
            user_breakdown_fig,
            hamm_breakdown_fig,
            original_language_fig,
            dialogue_fig,
            genre_fig,
        )

    except Exception as exc:
        error_msg = html.P(f"Error loading data: {exc}", className="text-danger")
        error_fig = create_error_figure(error=str(exc))
        return (
            error_msg,
            error_msg,
            error_msg,
            error_msg,
            error_fig,
            error_msg,
            error_msg,
            error_fig,
            error_fig,
            error_fig,
            error_fig,
            error_fig,
            error_fig,
            error_fig,
        )


# ---------------------------------------------------------------------------
# Volume KPI computation
# ---------------------------------------------------------------------------

def compute_volume_kpis(df: pd.DataFrame) -> dict:
    """Compute volume KPI values from a filtered DataFrame.

    Excludes rows with Cancelled status, then counts total screens,
    ERV-type records, and Prelim-type records.

    Args:
        df: Filtered DataFrame with COLUMN_MAP columns.

    Returns:
        dict with keys "total_screens", "total_erv", "total_prelim" (all int).
    """
    status_col = COLUMN_MAP["status"]
    content_type_col = COLUMN_MAP["content_type"]

    # Exclude Cancelled status
    if df.empty:
        return {"total_screens": 0, "total_erv": 0, "total_prelim": 0}

    non_cancelled = df[df[status_col] != "Cancelled"]

    total_screens = len(non_cancelled)
    total_erv = int((non_cancelled[content_type_col] == ERV_LABEL).sum())
    total_prelim = int((non_cancelled[content_type_col] == PRELIM_LABEL).sum())

    return {
        "total_screens": total_screens,
        "total_erv": total_erv,
        "total_prelim": total_prelim,
    }


# ---------------------------------------------------------------------------
# Clear-filter callbacks (registered via shared helper)
# ---------------------------------------------------------------------------
register_clear_callbacks(CLEAR_PAIRS)
