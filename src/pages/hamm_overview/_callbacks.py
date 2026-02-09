"""Callbacks for Hamm Overview dashboard.

This module is the slim orchestration layer.  All chart/table rendering
lives in ``_chart_builders``, data aggregation in ``_data_loader``, and
clear-filter callbacks are registered via ``register_clear_callbacks``.
"""
import pandas as pd
from dash import callback, Input, Output, html

from src.data.parquet_reader import ParquetReader
from src.charts.empty_states import create_empty_figure
from src.utils.callback_helpers import register_clear_callbacks
from ._constants import (
    CHART_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    CHART_ID_TASK_TABLE,
    CHART_ID_ERROR_RATIO,
    CHART_ID_ERROR_BY_SCREENER,
    CHART_ID_USER_BREAKDOWN,
    CHART_ID_HAMM_BREAKDOWN,
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
)
from ._data_loader import (
    resolve_dataset_id_for_dashboard,
    load_and_filter_data,
    build_volume_summary,
    prepare_task_display_df,
    build_issues_ratio,
    build_intervention_by_screener,
    build_user_intervention_breakdown,
    build_hamm_intervention_breakdown,
    FILTER_COLUMN_MAP,
)
from ._chart_builders import (
    build_volume_table,
    build_volume_chart,
    build_task_table,
    build_error_ratio_chart,
    build_error_by_screener_chart,
    build_user_breakdown_chart,
    build_hamm_breakdown_chart,
)


def _ensure_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _strip_sort_column(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[SORT_START_COL], errors="ignore")


@callback(
    Output(CHART_ID_VOLUME_TABLE, "children"),
    Output(CHART_ID_VOLUME_CHART, "figure"),
    Output(CHART_ID_TASK_TABLE, "children"),
    Output(CHART_ID_ERROR_RATIO, "figure"),
    Output(CHART_ID_ERROR_BY_SCREENER, "figure"),
    Output(CHART_ID_USER_BREAKDOWN, "figure"),
    Output(CHART_ID_HAMM_BREAKDOWN, "figure"),
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
        ("region", _ensure_list(region_values)),
        ("year", _ensure_list(year_values)),
        ("month", _ensure_list(month_values)),
        ("id", _ensure_list(task_id_value)),
        ("content_type", _ensure_list(content_type_values)),
        ("original_language", _ensure_list(original_language_values)),
        ("dialogue", _ensure_list(dialogue_values)),
        ("genre", _ensure_list(genre_values)),
        ("error_code", _ensure_list(error_code_values)),
        ("error_type", _ensure_list(error_type_values)),
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

        return (
            volume_table,
            volume_chart,
            task_table,
            error_ratio_fig,
            error_by_screener_fig,
            user_breakdown_fig,
            hamm_breakdown_fig,
        )

    except Exception as exc:
        error_msg = html.P(f"Error loading data: {exc}", className="text-danger")
        empty_fig = create_empty_figure(message="Error loading data")
        return (
            error_msg,
            empty_fig,
            error_msg,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
        )


# ---------------------------------------------------------------------------
# Clear-filter callbacks (registered via shared helper)
# ---------------------------------------------------------------------------
register_clear_callbacks(CLEAR_PAIRS)
