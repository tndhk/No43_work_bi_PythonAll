"""Data loading and filtering logic for Hamm Overview dashboard."""
from typing import Optional
import pandas as pd

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.data_source_registry import resolve_dataset_id
from src.data.filter_engine import FilterSet, CategoryFilter, apply_filters, extract_unique_values
from ._constants import (
    COLUMN_MAP,
    DASHBOARD_ID,
    CHART_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    CHART_ID_TASK_TABLE,
    DERIVED_YEAR,
    DERIVED_MONTH,
    DERIVED_FISCAL_YEAR,
    DERIVED_FISCAL_QUARTER,
    DERIVED_ISO_WEEK,
    DERIVED_START_DATE,
    DERIVED_END_DATE,
)


CADENCE_WEEKLY = "weekly"
CADENCE_MONTHLY = "monthly"
CADENCE_QUARTERLY = "quarterly"
CADENCE_YEARLY = "yearly"


def resolve_dataset_id_for_dashboard() -> str:
    """Resolve the dataset ID for all Hamm Overview charts."""
    chart_ids = [
        CHART_ID_VOLUME_TABLE,
        CHART_ID_VOLUME_CHART,
        CHART_ID_TASK_TABLE,
    ]
    dataset_ids = {resolve_dataset_id(DASHBOARD_ID, chart_id) for chart_id in chart_ids}
    if len(dataset_ids) != 1:
        raise ValueError(
            "Multiple dataset IDs found for Hamm Overview dashboard: "
            f"{sorted(dataset_ids)}"
        )
    return next(iter(dataset_ids))


def _prepare_base_df(df: pd.DataFrame) -> pd.DataFrame:
    created_col = COLUMN_MAP["created_at"]
    completed_col = COLUMN_MAP["completed_at"]
    id_col = COLUMN_MAP["id"]

    df = df.copy()

    df[id_col] = df[id_col].astype(str)
    df[created_col] = pd.to_datetime(df[created_col], utc=True).dt.tz_convert(None)
    df[completed_col] = pd.to_datetime(df[completed_col], utc=True).dt.tz_convert(None)

    # Convert video_duration from "HH:MM:SS" string to seconds (float)
    dur_col = COLUMN_MAP["video_duration"]
    df["_video_duration_seconds"] = pd.to_timedelta(df[dur_col], errors="coerce").dt.total_seconds()

    df[DERIVED_YEAR] = df[created_col].dt.strftime("%Y")
    df[DERIVED_MONTH] = df[created_col].dt.strftime("%b")

    return df


def _format_start_date_monthly(ts: Optional[pd.Timestamp]) -> str:
    if ts is pd.NaT or pd.isna(ts):
        return "Null"
    return f"1-{ts.strftime('%b-%y')}"


def _format_start_date_quarterly(ts: Optional[pd.Timestamp]) -> str:
    if ts is pd.NaT or pd.isna(ts):
        return "Null"
    month = ts.month
    year = ts.strftime("%y")
    if month in (1, 2, 3):
        return f"1-Jan-{year}"
    if month in (4, 5, 6):
        return f"1-Apr-{year}"
    if month in (7, 8, 9):
        return f"1-Jul-{year}"
    return f"1-Oct-{year}"


def _format_end_date_quarterly(ts: Optional[pd.Timestamp]) -> str:
    if ts is pd.NaT or pd.isna(ts):
        return "Null"
    month = ts.month
    year = ts.strftime("%y")
    if month in (1, 2, 3):
        return f"31-Mar-{year}"
    if month in (4, 5, 6):
        return f"30-Jun-{year}"
    if month in (7, 8, 9):
        return f"30-Sep-{year}"
    return f"31-Dec-{year}"


def _format_start_date_yearly(ts: Optional[pd.Timestamp]) -> str:
    if ts is pd.NaT or pd.isna(ts):
        return "Null"
    return f"1-Jan-{ts.strftime('%y')}"


def _format_end_date_yearly(ts: Optional[pd.Timestamp]) -> str:
    if ts is pd.NaT or pd.isna(ts):
        return "Null"
    return f"31-Dec-{ts.strftime('%y')}"


def _add_cadence_columns(df: pd.DataFrame, cadence: str) -> pd.DataFrame:
    created_col = COLUMN_MAP["created_at"]
    df = df.copy()

    shifted = df[created_col] + pd.DateOffset(months=3)
    df[DERIVED_FISCAL_YEAR] = shifted.dt.strftime("%Y").fillna("Null")
    df[DERIVED_FISCAL_QUARTER] = (
        "Q" + shifted.dt.quarter.astype("Int64").astype(str)
    ).where(~shifted.isna(), "Null")

    if cadence == CADENCE_WEEKLY:
        df[DERIVED_ISO_WEEK] = df[created_col].dt.strftime("%V").fillna("Null")

        weekday = df[created_col].dt.weekday
        start_offsets = weekday.map({0: -6, 1: 0, 2: -1, 3: -2, 4: -3, 5: -4, 6: -5})
        end_offsets = weekday.map({0: 0, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1})

        start_dates = df[created_col] + pd.to_timedelta(start_offsets, unit="D")
        end_dates = df[created_col] + pd.to_timedelta(end_offsets, unit="D")

        df[DERIVED_START_DATE] = start_dates.dt.strftime("%d-%b-%y").fillna("Null")
        df[DERIVED_END_DATE] = end_dates.dt.strftime("%d-%b-%y").fillna("Null")

    elif cadence == CADENCE_MONTHLY:
        df[DERIVED_ISO_WEEK] = ""
        df[DERIVED_START_DATE] = df[created_col].apply(_format_start_date_monthly)
        df[DERIVED_END_DATE] = df[created_col].dt.to_period("M").dt.end_time.dt.strftime(
            "%d-%b-%y"
        ).fillna("Null")

    elif cadence == CADENCE_QUARTERLY:
        df[DERIVED_ISO_WEEK] = ""
        df[DERIVED_START_DATE] = df[created_col].apply(_format_start_date_quarterly)
        df[DERIVED_END_DATE] = df[created_col].apply(_format_end_date_quarterly)

    else:
        df[DERIVED_ISO_WEEK] = ""
        df[DERIVED_START_DATE] = df[created_col].apply(_format_start_date_yearly)
        df[DERIVED_END_DATE] = df[created_col].apply(_format_end_date_yearly)

    return df


def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:
    """Load filter option values from cached dataset."""
    try:
        df = get_cached_dataset(reader, dataset_id)
        df = _prepare_base_df(df)

        options = {
            "regions": extract_unique_values(df, COLUMN_MAP["region"]),
            "years": extract_unique_values(df, DERIVED_YEAR),
            "months": extract_unique_values(df, DERIVED_MONTH),
            "task_ids": extract_unique_values(df, COLUMN_MAP["id"]),
            "content_types": extract_unique_values(df, COLUMN_MAP["content_type"]),
            "original_languages": extract_unique_values(df, COLUMN_MAP["original_language"]),
            "dialogue_options": extract_unique_values(df, COLUMN_MAP["dialogue"]),
            "genres": extract_unique_values(df, COLUMN_MAP["genre"]),
            "error_codes": extract_unique_values(df, COLUMN_MAP["error_code"]),
            "error_types": extract_unique_values(df, COLUMN_MAP["error_type"]),
        }

        return options

    except Exception:
        return {
            "regions": [],
            "years": [],
            "months": [],
            "task_ids": [],
            "content_types": [],
            "original_languages": [],
            "dialogue_options": [],
            "genres": [],
            "error_codes": [],
            "error_types": [],
        }


def load_and_filter_data(
    reader: ParquetReader,
    dataset_id: str,
    regions,
    years,
    months,
    task_ids,
    content_types,
    original_languages,
    dialogue_values,
    genres,
    error_codes,
    error_types,
) -> pd.DataFrame:
    """Load dataset and apply all filter criteria."""
    df = get_cached_dataset(reader, dataset_id)
    df = _prepare_base_df(df)

    filters = FilterSet()

    if regions:
        filters.category_filters.append(CategoryFilter(column=COLUMN_MAP["region"], values=regions))
    if years:
        filters.category_filters.append(CategoryFilter(column=DERIVED_YEAR, values=years))
    if months:
        filters.category_filters.append(CategoryFilter(column=DERIVED_MONTH, values=months))
    if task_ids:
        filters.category_filters.append(CategoryFilter(column=COLUMN_MAP["id"], values=task_ids))
    if content_types:
        filters.category_filters.append(CategoryFilter(column=COLUMN_MAP["content_type"], values=content_types))
    if original_languages:
        filters.category_filters.append(CategoryFilter(column=COLUMN_MAP["original_language"], values=original_languages))
    if dialogue_values:
        filters.category_filters.append(CategoryFilter(column=COLUMN_MAP["dialogue"], values=dialogue_values))
    if genres:
        filters.category_filters.append(CategoryFilter(column=COLUMN_MAP["genre"], values=genres))
    if error_codes:
        filters.category_filters.append(CategoryFilter(column=COLUMN_MAP["error_code"], values=error_codes))
    if error_types:
        filters.category_filters.append(CategoryFilter(column=COLUMN_MAP["error_type"], values=error_types))

    return apply_filters(df, filters)


def add_cadence_columns(df: pd.DataFrame, cadence: str) -> pd.DataFrame:
    """Public wrapper for adding cadence-derived columns."""
    return _add_cadence_columns(df, cadence)
