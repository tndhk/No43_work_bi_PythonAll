"""Callbacks for Hamm Overview dashboard.

This module is the slim orchestration layer.  All chart/table rendering
lives in ``_chart_builders``, data aggregation in ``_data_loader``, and
clear-filter callbacks are registered via ``register_clear_callbacks``.
"""
from typing import Iterable

import pandas as pd
from dash import callback, Input, Output, html

from src.data.parquet_reader import ParquetReader
from src.charts.empty_states import create_empty_figure
from src.utils.callback_helpers import register_clear_callbacks
from ._constants import (
    CHART_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    CHART_ID_TASK_TABLE,
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
    FILTER_COLUMN_MAP,
)
from ._chart_builders import (
    build_volume_table,
    build_volume_chart,
    build_task_table,
)


def _ensure_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_filter_values(*values: Iterable) -> list[list]:
    return [_ensure_list(v) for v in values]


def _strip_sort_column(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[SORT_START_COL], errors="ignore")


@callback(
    Output(CHART_ID_VOLUME_TABLE, "children"),
    Output(CHART_ID_VOLUME_CHART, "figure"),
    Output(CHART_ID_TASK_TABLE, "children"),
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

    normalized = _normalize_filter_values(
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
    )

    (
        region_values,
        year_values,
        month_values,
        task_ids,
        content_type_values,
        original_language_values,
        dialogue_values,
        genre_values,
        error_code_values,
        error_type_values,
    ) = normalized

    cadence = cadence_value or "weekly"

    try:
        df = load_and_filter_data(
            reader,
            dataset_id,
            FILTER_COLUMN_MAP,
            regions=region_values,
            years=year_values,
            months=month_values,
            task_ids=task_ids,
            content_types=content_type_values,
            original_languages=original_language_values,
            dialogue_values=dialogue_values,
            genres=genre_values,
            error_codes=error_code_values,
            error_types=error_type_values,
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

        volume_table = build_volume_table(volume_table_df)
        volume_chart = build_volume_chart(volume_chart_df)
        task_table = build_task_table(df)

        return volume_table, volume_chart, task_table

    except Exception as exc:
        error_msg = html.P(f"Error loading data: {exc}", className="text-danger")
        empty_fig = create_empty_figure(message="Error loading data")
        return error_msg, empty_fig, error_msg


# ---------------------------------------------------------------------------
# Clear-filter callbacks (registered via shared helper)
# ---------------------------------------------------------------------------
register_clear_callbacks(CLEAR_PAIRS)
