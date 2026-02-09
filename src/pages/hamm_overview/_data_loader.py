"""Data loading and filtering logic for Hamm Overview dashboard."""
from typing import Any, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.data_source_registry import resolve_dataset_id
from src.data.filter_engine import apply_filters, extract_unique_values
from src.utils.filter_helpers import build_filter_set_from_map
from ._constants import (
    COLUMN_MAP,
    DASHBOARD_ID,
    CHART_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    CHART_ID_TASK_TABLE,
    CHART_ID_ERROR_RATIO,
    CHART_ID_ERROR_BY_SCREENER,
    CHART_ID_USER_BREAKDOWN,
    CHART_ID_HAMM_BREAKDOWN,
    TASK_TABLE_SPEC,
    DERIVED_YEAR,
    DERIVED_MONTH,
    DERIVED_FISCAL_YEAR,
    DERIVED_FISCAL_QUARTER,
    DERIVED_ISO_WEEK,
    DERIVED_START_DATE,
    DERIVED_END_DATE,
    PRELIM_LABEL,
    ERV_LABEL,
    SORT_START_COL,
)


# Extend COLUMN_MAP with derived columns for filter_set_from_map compatibility
FILTER_COLUMN_MAP: dict[str, str] = {
    **COLUMN_MAP,
    "year": DERIVED_YEAR,
    "month": DERIVED_MONTH,
}

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
        CHART_ID_ERROR_RATIO,
        CHART_ID_ERROR_BY_SCREENER,
        CHART_ID_USER_BREAKDOWN,
        CHART_ID_HAMM_BREAKDOWN,
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


# ---------------------------------------------------------------------------
# Vectorized equivalents of the scalar date formatters above.
# Each accepts a pd.Series of datetime64 and returns a pd.Series of str.
# NaT values are mapped to "Null" to match the scalar versions.
# ---------------------------------------------------------------------------

def _format_start_date_monthly_vec(series: pd.Series) -> pd.Series:
    """Vectorized: '1-Mon-YY' for each timestamp, 'Null' for NaT."""
    formatted = "1-" + series.dt.strftime("%b-%y")
    return formatted.where(series.notna(), "Null")


def _format_start_date_quarterly_vec(series: pd.Series) -> pd.Series:
    """Vectorized: quarter start date as '1-Mon-YY', 'Null' for NaT."""
    quarter = series.dt.quarter
    year_str = series.dt.strftime("%y")

    result = np.select(
        [quarter == 1, quarter == 2, quarter == 3, quarter == 4],
        [
            "1-Jan-" + year_str,
            "1-Apr-" + year_str,
            "1-Jul-" + year_str,
            "1-Oct-" + year_str,
        ],
        default="Null",
    )
    out = pd.Series(result, index=series.index)
    return out.where(series.notna(), "Null")


def _format_end_date_quarterly_vec(series: pd.Series) -> pd.Series:
    """Vectorized: quarter end date as 'dd-Mon-YY', 'Null' for NaT."""
    quarter = series.dt.quarter
    year_str = series.dt.strftime("%y")

    result = np.select(
        [quarter == 1, quarter == 2, quarter == 3, quarter == 4],
        [
            "31-Mar-" + year_str,
            "30-Jun-" + year_str,
            "30-Sep-" + year_str,
            "31-Dec-" + year_str,
        ],
        default="Null",
    )
    out = pd.Series(result, index=series.index)
    return out.where(series.notna(), "Null")


def _format_start_date_yearly_vec(series: pd.Series) -> pd.Series:
    """Vectorized: '1-Jan-YY' for each timestamp, 'Null' for NaT."""
    formatted = "1-Jan-" + series.dt.strftime("%y")
    return formatted.where(series.notna(), "Null")


def _format_end_date_yearly_vec(series: pd.Series) -> pd.Series:
    """Vectorized: '31-Dec-YY' for each timestamp, 'Null' for NaT."""
    formatted = "31-Dec-" + series.dt.strftime("%y")
    return formatted.where(series.notna(), "Null")


def _compute_total_duration_vec(
    created: pd.Series, completed: pd.Series
) -> pd.Series:
    """Vectorized: compute 'HH:MM:SS' duration, '' for NaT completed.

    Replaces the .dt.components.apply(lambda row: ...) pattern.
    """
    if created.empty:
        return pd.Series([], dtype=str)

    missing = completed.isna()
    delta = (completed - created).fillna(pd.Timedelta(0))
    total_seconds = delta.dt.total_seconds().astype("int64")

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    formatted = (
        hours.astype(str).str.zfill(2)
        + ":"
        + minutes.astype(str).str.zfill(2)
        + ":"
        + seconds.astype(str).str.zfill(2)
    )

    return formatted.where(~missing, "")


def add_cadence_columns(df: pd.DataFrame, cadence: str) -> pd.DataFrame:
    created_col = COLUMN_MAP["created_at"]
    df = df.copy()

    shifted = df[created_col] + pd.DateOffset(months=3)
    df[DERIVED_FISCAL_YEAR] = shifted.dt.strftime("%Y").fillna("Null")
    df[DERIVED_FISCAL_QUARTER] = (
        "Q" + shifted.dt.quarter.astype("Int64").astype(str)
    ).where(~shifted.isna(), "Null")

    if cadence == CADENCE_WEEKLY:
        df[DERIVED_ISO_WEEK] = df[created_col].dt.strftime("%V").fillna("Null")

        # ISO week: Monday(0) to Sunday(6)
        weekday = df[created_col].dt.weekday
        start_offsets = weekday.map({0: 0, 1: -1, 2: -2, 3: -3, 4: -4, 5: -5, 6: -6})
        end_offsets = weekday.map({0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0})

        start_dates = df[created_col] + pd.to_timedelta(start_offsets, unit="D")
        end_dates = df[created_col] + pd.to_timedelta(end_offsets, unit="D")

        df[DERIVED_START_DATE] = start_dates.dt.strftime("%d-%b-%y").fillna("Null")
        df[DERIVED_END_DATE] = end_dates.dt.strftime("%d-%b-%y").fillna("Null")

    elif cadence == CADENCE_MONTHLY:
        df[DERIVED_ISO_WEEK] = ""
        df[DERIVED_START_DATE] = _format_start_date_monthly_vec(df[created_col])
        df[DERIVED_END_DATE] = df[created_col].dt.to_period("M").dt.end_time.dt.strftime(
            "%d-%b-%y"
        ).fillna("Null")

    elif cadence == CADENCE_QUARTERLY:
        df[DERIVED_ISO_WEEK] = ""
        df[DERIVED_START_DATE] = _format_start_date_quarterly_vec(df[created_col])
        df[DERIVED_END_DATE] = _format_end_date_quarterly_vec(df[created_col])

    else:
        df[DERIVED_ISO_WEEK] = ""
        df[DERIVED_START_DATE] = _format_start_date_yearly_vec(df[created_col])
        df[DERIVED_END_DATE] = _format_end_date_yearly_vec(df[created_col])

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
    column_map: dict[str, str],
    filter_pairs: Optional[List[Tuple[str, Any]]] = None,
) -> pd.DataFrame:
    """Load dataset and apply all filter criteria.

    Args:
        reader: ParquetReader instance for data access.
        dataset_id: ID of the dataset to load.
        column_map: Mapping from logical filter keys to DataFrame column names.
        filter_pairs: List of (key, values) tuples where key is a key in
            column_map and values is a list of filter values, None, or [].
            None/[] values are ignored (no filtering for that key).
            Example: [("region", ["AMER"]), ("year", [2024]), ...]
    """
    df = get_cached_dataset(reader, dataset_id)
    df = _prepare_base_df(df)

    if filter_pairs is None:
        filter_pairs = []
    filters = build_filter_set_from_map(column_map, filter_pairs)

    return apply_filters(df, filters)


def _parse_start_date(value: str) -> pd.Timestamp:
    """Parse a start date string (dd-Mon-yy) to a Timestamp for sorting."""
    return pd.to_datetime(value, format="%d-%b-%y", errors="coerce")


def build_volume_summary(df: pd.DataFrame, cadence: str) -> pd.DataFrame:
    """Build a volume summary DataFrame grouped by cadence period.

    Adds cadence columns, excludes Cancelled/Invalid statuses, groups
    by time period and content type, and pivots to show Prelim/ERV counts.

    Args:
        df: Pre-filtered DataFrame (already through _prepare_base_df).
        cadence: One of "weekly", "monthly", "quarterly", "yearly".

    Returns:
        A pivoted DataFrame with columns: Fiscal Year, Fiscal Quarter,
        ISO Week, Start Date, End Date, Prelim, ERV, VOLUME TOTAL,
        plus an internal _sort_start_dt column for ordering.
    """
    df = add_cadence_columns(df, cadence)

    # Exclude Cancelled and Invalid status for volume summary
    status_col = COLUMN_MAP["status"]
    excluded_statuses = ["Cancelled", "Invalid"]
    df = df[~df[status_col].isin(excluded_statuses)]

    group_cols = [
        DERIVED_FISCAL_YEAR,
        DERIVED_FISCAL_QUARTER,
        DERIVED_ISO_WEEK,
        DERIVED_START_DATE,
        DERIVED_END_DATE,
        COLUMN_MAP["content_type"],
    ]

    summary = (
        df.groupby(group_cols)[COLUMN_MAP["id"]]
        .nunique()
        .reset_index(name="count")
    )

    pivot = summary.pivot_table(
        index=[
            DERIVED_FISCAL_YEAR,
            DERIVED_FISCAL_QUARTER,
            DERIVED_ISO_WEEK,
            DERIVED_START_DATE,
            DERIVED_END_DATE,
        ],
        columns=COLUMN_MAP["content_type"],
        values="count",
        fill_value=0,
    ).reset_index()

    for label in (PRELIM_LABEL, ERV_LABEL):
        if label not in pivot.columns:
            pivot[label] = 0

    pivot["VOLUME TOTAL"] = pivot[PRELIM_LABEL] + pivot[ERV_LABEL]

    pivot = pivot.rename(columns={
        DERIVED_FISCAL_YEAR: "Fiscal Year",
        DERIVED_FISCAL_QUARTER: "Fiscal Quarter",
        DERIVED_ISO_WEEK: "ISO Week",
        DERIVED_START_DATE: "Start Date",
        DERIVED_END_DATE: "End Date",
    })

    pivot = pivot[[
        "Fiscal Year",
        "Fiscal Quarter",
        "ISO Week",
        "Start Date",
        "End Date",
        PRELIM_LABEL,
        ERV_LABEL,
        "VOLUME TOTAL",
    ]]

    pivot[SORT_START_COL] = pivot["Start Date"].apply(_parse_start_date)

    pivot = pivot.sort_values(by=[SORT_START_COL, "End Date"], kind="mergesort")

    return pivot


def prepare_task_display_df(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw task data into a display-ready DataFrame.

    Performs the following transformations:
    1. Format created_at as "Job Created" (YYYY-MM-DD HH:MM)
    2. Format completed_at as "Completed / Err" (YYYY-MM-DD HH:MM)
    3. Compute "Total Duration" (completed_at - created_at -> HH:MM:SS)
    4. Rename columns via COLUMN_MAP to display names
    5. Sort by Task ID numerically

    Args:
        df: Pre-filtered DataFrame (already through _prepare_base_df).

    Returns:
        A display-ready DataFrame with columns matching TASK_TABLE_SPEC.column_order.
    """
    if df.empty:
        return pd.DataFrame(columns=TASK_TABLE_SPEC.column_order)

    created_col = COLUMN_MAP["created_at"]
    completed_col = COLUMN_MAP["completed_at"]

    display_df = df.copy()
    display_df["Job Created"] = display_df[created_col].dt.strftime("%Y-%m-%d %H:%M")
    display_df["Completed / Err"] = display_df[completed_col].dt.strftime(
        "%Y-%m-%d %H:%M"
    )

    display_df["Total Duration"] = _compute_total_duration_vec(
        display_df[created_col], display_df[completed_col]
    )

    table_columns = {
        "Task ID": COLUMN_MAP["id"],
        "Task Name": COLUMN_MAP["title"],
        "Content Type": COLUMN_MAP["content_type"],
        "Task Status": COLUMN_MAP["status"],
        "Source File Duration": COLUMN_MAP["video_duration"],
        "Audio Details": COLUMN_MAP["audio_details"],
    }

    output_df = pd.DataFrame(
        {
            display_name: display_df[column_name]
            for display_name, column_name in table_columns.items()
        }
    )

    output_df["Job Created"] = display_df["Job Created"]
    output_df["Completed / Err"] = display_df["Completed / Err"]
    output_df["Total Duration"] = display_df["Total Duration"]

    # Sort by Task ID (as numeric)
    output_df = output_df.sort_values(
        by="Task ID",
        key=lambda x: pd.to_numeric(x, errors="coerce").fillna(0),
    )

    return output_df


# ---------------------------------------------------------------------------
# Error Details aggregation functions
# ---------------------------------------------------------------------------

def build_issues_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """Build User vs HAMM ratio for pie chart.
    
    Args:
        df: Pre-filtered DataFrame (already through _prepare_base_df).
    
    Returns:
        DataFrame with columns: error_type, count
    """
    error_type_col = COLUMN_MAP["error_type"]
    
    # Filter to only User and HAMM
    filtered_df = df[df[error_type_col].isin(["User", "HAMM"])].copy()
    filtered_df = filtered_df[filtered_df[COLUMN_MAP["status"]].isin(["Invalid", "Error"])]
    if len(filtered_df) == 0:
        return pd.DataFrame(columns=["error_type", "count"])
    
    ratio_df = (
        filtered_df.groupby(error_type_col)[COLUMN_MAP["id"]]
        .nunique()
        .reset_index(name="count")
    )
    
    ratio_df = ratio_df.rename(columns={error_type_col: "error_type"})
    
    return ratio_df


def build_intervention_by_screener(df: pd.DataFrame) -> pd.DataFrame:
    """Build Screener Type vs User/HAMM intervention counts for stacked bar chart.
    
    Args:
        df: Pre-filtered DataFrame (already through _prepare_base_df).
    
    Returns:
        DataFrame with columns: video_type_description, User, HAMM
    """
    error_type_col = COLUMN_MAP["error_type"]
    content_type_col = COLUMN_MAP["content_type"]
    
    # Filter to only User and HAMM
    filtered_df = df[df[error_type_col].isin(["User", "HAMM"])].copy()
    filtered_df = filtered_df[filtered_df[COLUMN_MAP["status"]].isin(["Invalid", "Error"])]
    if len(filtered_df) == 0:
        return pd.DataFrame(columns=["video_type_description", "User", "HAMM"])
    
    # Group by content_type and error_type, then pivot
    summary = (
        filtered_df.groupby([content_type_col, error_type_col])[COLUMN_MAP["id"]]
        .nunique()
        .reset_index(name="count")
    )
    
    pivot_df = summary.pivot_table(
        index=content_type_col,
        columns=error_type_col,
        values="count",
        fill_value=0,
    ).reset_index()
    
    pivot_df = pivot_df.rename(columns={content_type_col: "video_type_description"})
    
    # Ensure User and HAMM columns exist
    if "User" not in pivot_df.columns:
        pivot_df["User"] = 0
    if "HAMM" not in pivot_df.columns:
        pivot_df["HAMM"] = 0
    
    return pivot_df[["video_type_description", "User", "HAMM"]]


def build_user_intervention_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Build User error breakdown by error description for bar chart.
    
    重要: 関数内で error_type = "User" で事前フィルタ必須
    
    Args:
        df: Pre-filtered DataFrame (already through _prepare_base_df).
    
    Returns:
        DataFrame with columns: error_description, count
    """
    error_type_col = COLUMN_MAP["error_type"]
    error_desc_col = COLUMN_MAP["error_description"]
    
    # Filter to only User records
    user_df = df[df[error_type_col] == "User"].copy()
    user_df = user_df[user_df[COLUMN_MAP["status"]].isin(["Invalid", "Error"])]
    
    if len(user_df) == 0:
        return pd.DataFrame(columns=["error_description", "count"])
    
    # Group by error description
    breakdown_df = (
        user_df.groupby(error_desc_col)[COLUMN_MAP["id"]]
        .nunique()
        .reset_index(name="count")
    )
    
    breakdown_df = breakdown_df.rename(columns={error_desc_col: "error_description"})
    
    # Sort by count descending
    breakdown_df = breakdown_df.sort_values("count", ascending=False)
    
    return breakdown_df


def build_hamm_intervention_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Build HAMM error breakdown by error description for bar chart.
    
    重要: 関数内で error_type = "HAMM" で事前フィルタ必須
    
    Args:
        df: Pre-filtered DataFrame (already through _prepare_base_df).
    
    Returns:
        DataFrame with columns: error_description, count
    """
    error_type_col = COLUMN_MAP["error_type"]
    error_desc_col = COLUMN_MAP["error_description"]
    
    # Filter to only HAMM records
    hamm_df = df[df[error_type_col] == "HAMM"].copy()
    hamm_df = hamm_df[hamm_df[COLUMN_MAP["status"]].isin(["Invalid", "Error"])]
    
    if len(hamm_df) == 0:
        return pd.DataFrame(columns=["error_description", "count"])
    
    # Group by error description
    breakdown_df = (
        hamm_df.groupby(error_desc_col)[COLUMN_MAP["id"]]
        .nunique()
        .reset_index(name="count")
    )
    
    breakdown_df = breakdown_df.rename(columns={error_desc_col: "error_description"})
    
    # Sort by count descending
    breakdown_df = breakdown_df.sort_values("count", ascending=False)
    
    return breakdown_df
