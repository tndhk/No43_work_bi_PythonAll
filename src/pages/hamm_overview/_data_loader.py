"""Data loading and transformation for HAMM Overview dashboard.

Auto-generated from page_spec.yaml by tools.page_generator,
then manually extended with helper functions and aggregation builders.
"""
import pandas as pd

from src.data.parquet_reader import ParquetReader
from src.data.data_source_registry import resolve_dataset_id
from src.core.cache import get_cached_dataset
from src.utils.data_helpers import extract_unique_values
from src.utils.filter_helpers import build_filter_set_from_map
from src.data.filter_engine import apply_filters

from ._constants import (
    DASHBOARD_ID,
    COLUMN_MAP,
    DERIVED_YEAR,
    DERIVED_MONTH,
    DERIVED_FISCAL_YEAR,
    DERIVED_FISCAL_QUARTER,
    DERIVED_ISO_WEEK,
    DERIVED_START_DATE,
    DERIVED_END_DATE,
    DERIVED_VIDEO_DURATION_SECONDS,
    KPI_ID_KPI_TOTAL_SCREENS,
    KPI_ID_KPI_TOTAL_ERV,
    KPI_ID_KPI_TOTAL_PRELIM,
    TABLE_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    TABLE_ID_TASK_TABLE,
    TABLE_ID_LANGUAGE_TABLE,
    CHART_ID_ERROR_RATIO,
    CHART_ID_ERROR_BY_SCREENER,
    CHART_ID_USER_BREAKDOWN,
    CHART_ID_BREAKDOWN,
    CHART_ID_METADATA_ORIGINAL_LANGUAGE,
    CHART_ID_METADATA_DIALOGUE,
    CHART_ID_METADATA_GENRE,
)

# Re-export custom logic functions so tests can import from _data_loader
from ._custom_logic import (
    add_cadence_columns,
    prepare_task_display_df,
    prepare_language_display_df,
    _format_start_date_monthly,
    _format_start_date_monthly_vec,
    _format_start_date_quarterly,
    _format_start_date_quarterly_vec,
    _format_end_date_quarterly,
    _format_end_date_quarterly_vec,
    _format_start_date_yearly,
    _format_start_date_yearly_vec,
    _format_end_date_yearly,
    _format_end_date_yearly_vec,
    _compute_total_duration_vec,
)

__all__ = [
    "FILTER_COLUMN_MAP",
    "add_cadence_columns",
    "prepare_task_display_df",
    "prepare_language_display_df",
    "_format_start_date_monthly",
    "_format_start_date_monthly_vec",
    "_format_start_date_quarterly",
    "_format_start_date_quarterly_vec",
    "_format_end_date_quarterly",
    "_format_end_date_quarterly_vec",
    "_format_start_date_yearly",
    "_format_start_date_yearly_vec",
    "_format_end_date_yearly",
    "_format_end_date_yearly_vec",
    "_compute_total_duration_vec",
    "load_filter_options",
    "load_and_filter_data",
    "build_volume_summary",
    "build_issues_ratio",
    "build_intervention_by_screener",
    "build_user_intervention_breakdown",
    "build_hamm_intervention_breakdown",
    "build_original_language_distribution",
    "build_genre_distribution",
    "build_dialogue_by_content_type",
    "resolve_dataset_id_for_dashboard",
]


# ---------------------------------------------------------------------------
# Filter column mapping (extends COLUMN_MAP with derived columns)
# ---------------------------------------------------------------------------
FILTER_COLUMN_MAP: dict[str, str] = {
    **COLUMN_MAP,
    "year": DERIVED_YEAR,
    "month": DERIVED_MONTH,
    "fiscal_year": DERIVED_FISCAL_YEAR,
    "fiscal_quarter": DERIVED_FISCAL_QUARTER,
    "iso_week": DERIVED_ISO_WEEK,
    "start_date": DERIVED_START_DATE,
    "end_date": DERIVED_END_DATE,
    "video_duration_seconds": DERIVED_VIDEO_DURATION_SECONDS,
}


# ---------------------------------------------------------------------------
# Base DataFrame preparation
# ---------------------------------------------------------------------------

def _prepare_base_df(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare base DataFrame with derived columns.

    - Strip timezone from created_at and completed_at
    - Add _year, _month (string) from created_at
    - Add _fiscal_year: (created_at + 3 months).year as string
    - Add _video_duration_seconds from video_duration HH:MM:SS
    - Preserve original video_duration column

    Args:
        df: Raw DataFrame from Parquet

    Returns:
        DataFrame with derived columns added
    """
    df = df.copy()

    # Strip timezone from datetime columns
    for col in [COLUMN_MAP["created_at"], COLUMN_MAP["completed_at"]]:
        if col in df.columns:
            dt_series = pd.to_datetime(df[col], utc=True)
            df[col] = dt_series.dt.tz_convert(None)

    created = df[COLUMN_MAP["created_at"]]

    # Derived year / month
    df[DERIVED_YEAR] = created.dt.strftime("%Y")
    df[DERIVED_MONTH] = created.dt.strftime("%b")

    # Fiscal year: April start => created + 3 months => extract year
    shifted = created + pd.DateOffset(months=3)
    df[DERIVED_FISCAL_YEAR] = shifted.dt.strftime("%Y")

    # Video duration in seconds
    df[DERIVED_VIDEO_DURATION_SECONDS] = pd.to_timedelta(
        df[COLUMN_MAP["video_duration"]], errors="coerce"
    ).dt.total_seconds()

    return df


# ---------------------------------------------------------------------------
# Filter options loading
# ---------------------------------------------------------------------------

def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:
    """Load unique values for all filters.

    Args:
        reader: ParquetReader instance
        dataset_id: Dataset ID to load

    Returns:
        Dictionary mapping filter names to option lists
    """
    df = get_cached_dataset(reader, dataset_id)
    df = _prepare_base_df(df)

    return {
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


# ---------------------------------------------------------------------------
# Data loading with filter pairs
# ---------------------------------------------------------------------------

def load_and_filter_data(
    reader: ParquetReader,
    dataset_id: str,
    column_map: dict[str, str],
    filter_pairs: list[tuple[str, list | None]],
) -> pd.DataFrame:
    """Load dataset and apply filter pairs.

    Args:
        reader: ParquetReader instance
        dataset_id: Dataset ID to load
        column_map: Mapping from logical filter key to DataFrame column name
        filter_pairs: List of (key, values) tuples

    Returns:
        Filtered DataFrame with derived columns
    """
    df = get_cached_dataset(reader, dataset_id)
    df = _prepare_base_df(df)

    filters = build_filter_set_from_map(column_map, filter_pairs)
    return apply_filters(df, filters)


# ---------------------------------------------------------------------------
# Volume Summary aggregation
# ---------------------------------------------------------------------------

def build_volume_summary(df: pd.DataFrame, cadence: str) -> pd.DataFrame:
    """Build volume summary table from prepared DataFrame.

    Excludes 'Cancelled' status. Groups by cadence period and counts
    Completed vs Invalid (all non-Completed, non-Cancelled).

    Args:
        df: Prepared DataFrame (post _prepare_base_df)
        cadence: One of "weekly", "monthly", "quarterly", "yearly"

    Returns:
        DataFrame with columns: Fiscal Year, Fiscal Quarter, ISO Week,
        Start Date, End Date, Completed, Invalid, VOLUME TOTAL
    """
    expected_cols = [
        "Fiscal Year", "Fiscal Quarter", "ISO Week",
        "Start Date", "End Date", "Completed", "Invalid", "VOLUME TOTAL",
    ]

    # Exclude cancelled
    df = df[df[COLUMN_MAP["status"]] != "Cancelled"].copy()

    if df.empty:
        return pd.DataFrame(columns=expected_cols)

    # Add cadence columns
    df = add_cadence_columns(df, cadence)

    # Classify status
    df["_status_class"] = df[COLUMN_MAP["status"]].apply(
        lambda s: "Completed" if s == "Completed" else "Invalid"
    )

    group_cols = ["_fiscal_year", "_fiscal_quarter", "_start_date", "_end_date"]
    if cadence == "weekly":
        group_cols.append("_iso_week")

    pivot = df.pivot_table(
        index=group_cols,
        columns="_status_class",
        values=COLUMN_MAP["id"],
        aggfunc="count",
        fill_value=0,
    ).reset_index()

    # Ensure both Completed and Invalid columns exist
    for col in ["Completed", "Invalid"]:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot["VOLUME TOTAL"] = pivot["Completed"] + pivot["Invalid"]

    # Rename columns to display names
    rename_map = {
        "_fiscal_year": "Fiscal Year",
        "_fiscal_quarter": "Fiscal Quarter",
        "_start_date": "Start Date",
        "_end_date": "End Date",
    }
    if "_iso_week" in pivot.columns:
        rename_map["_iso_week"] = "ISO Week"
    pivot = pivot.rename(columns=rename_map)

    if "ISO Week" not in pivot.columns:
        pivot["ISO Week"] = pd.NA

    # Sort by start date for display
    # Parse start dates for sorting
    pivot["_sort_start_dt"] = pd.to_datetime(
        pivot["Start Date"], format="%d-%b-%y", errors="coerce"
    )
    if pivot["_sort_start_dt"].isna().all():
        # Try alternate format
        pivot["_sort_start_dt"] = pd.to_datetime(
            pivot["Start Date"], format="%-d-%b-%y", errors="coerce"
        )

    pivot = pivot.sort_values("_sort_start_dt", ascending=False).reset_index(drop=True)

    # Drop sort helper column
    pivot = pivot.drop(columns=["_sort_start_dt"], errors="ignore")

    # Reorder columns
    out_cols = [c for c in expected_cols if c in pivot.columns]
    return pivot[out_cols]


# ---------------------------------------------------------------------------
# Error/Intervention aggregation functions
# ---------------------------------------------------------------------------

def build_issues_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """Count User vs HAMM error records.

    Filters to only 'User' and 'HAMM' error types, then groups and counts.

    Returns:
        DataFrame with columns: error_type, count
    """
    error_col = COLUMN_MAP["error_type"]
    filtered = df[df[error_col].isin(["User", "HAMM"])].copy()

    if filtered.empty:
        return pd.DataFrame(columns=["error_type", "count"])

    result = (
        filtered.groupby(error_col)
        .size()
        .reset_index(name="count")
        .rename(columns={error_col: "error_type"})
    )
    return result


def build_intervention_by_screener(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate intervention counts by screener type (content type) and error type.

    Filters to User/HAMM, pivots to get User and HAMM as columns.

    Returns:
        DataFrame with columns: video_type_description, User, HAMM
    """
    error_col = COLUMN_MAP["error_type"]
    content_col = COLUMN_MAP["content_type"]

    filtered = df[df[error_col].isin(["User", "HAMM"])].copy()

    if filtered.empty:
        return pd.DataFrame(columns=["video_type_description", "User", "HAMM"])

    pivot = filtered.pivot_table(
        index=content_col,
        columns=error_col,
        values=COLUMN_MAP["id"],
        aggfunc="count",
        fill_value=0,
    ).reset_index()

    pivot.columns.name = None

    # Ensure both columns exist
    for col in ["User", "HAMM"]:
        if col not in pivot.columns:
            pivot[col] = 0

    return pivot[["video_type_description", "User", "HAMM"]]


def _build_intervention_breakdown(
    df: pd.DataFrame, error_type: str
) -> pd.DataFrame:
    """Shared logic for User/HAMM intervention breakdown.

    Filters to the specified error_type, groups by error description,
    counts, and sorts descending.

    Args:
        df: Prepared DataFrame
        error_type: 'User' or 'HAMM'

    Returns:
        DataFrame with columns: error_description, count
    """
    error_col = COLUMN_MAP["error_type"]
    desc_col = COLUMN_MAP["error_description"]

    filtered = df[df[error_col] == error_type].copy()

    if filtered.empty:
        return pd.DataFrame(columns=["error_description", "count"])

    result = (
        filtered.groupby(desc_col)
        .size()
        .reset_index(name="count")
        .rename(columns={desc_col: "error_description"})
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )
    return result


def build_user_intervention_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Build User intervention breakdown by error description."""
    return _build_intervention_breakdown(df, "User")


def build_hamm_intervention_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Build HAMM intervention breakdown by error description."""
    return _build_intervention_breakdown(df, "HAMM")


# ---------------------------------------------------------------------------
# Content Metadata aggregation functions
# ---------------------------------------------------------------------------

def _build_distribution(
    df: pd.DataFrame, logical_key: str, output_col: str
) -> pd.DataFrame:
    """Shared logic for distribution aggregations (language, genre, etc.).

    Groups by the specified column, counts unique ids, excludes NaN,
    sorts descending.

    Args:
        df: Prepared DataFrame
        logical_key: Key into COLUMN_MAP for the grouping column
        output_col: Name for the output column

    Returns:
        DataFrame with columns: [output_col, 'count']
    """
    col = COLUMN_MAP[logical_key]
    valid = df.dropna(subset=[col]).copy()

    if valid.empty:
        return pd.DataFrame(columns=[output_col, "count"])

    result = (
        valid.groupby(col)
        .size()
        .reset_index(name="count")
        .rename(columns={col: output_col})
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )
    return result


def build_original_language_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Build original language distribution."""
    return _build_distribution(df, "original_language", "original_language")


def build_genre_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Build genre distribution."""
    return _build_distribution(df, "genre", "genre")


def build_dialogue_by_content_type(df: pd.DataFrame) -> pd.DataFrame:
    """Build dialogue (Yes/No) by content type pivot.

    Filters to Yes/No only (excludes Unknown), pivots to get Yes and No as columns.

    Returns:
        DataFrame with columns: content_type, Yes, No
    """
    dialogue_col = COLUMN_MAP["dialogue"]
    content_col = COLUMN_MAP["content_type"]

    # Filter to only Yes/No
    filtered = df[df[dialogue_col].isin(["Yes", "No"])].copy()

    if filtered.empty:
        return pd.DataFrame(columns=["content_type", "Yes", "No"])

    pivot = filtered.pivot_table(
        index=content_col,
        columns=dialogue_col,
        values=COLUMN_MAP["id"],
        aggfunc="count",
        fill_value=0,
    ).reset_index()

    pivot.columns.name = None

    # Ensure both columns exist
    for col in ["Yes", "No"]:
        if col not in pivot.columns:
            pivot[col] = 0

    # Rename content type column
    pivot = pivot.rename(columns={content_col: "content_type"})

    return pivot[["content_type", "Yes", "No"]]


# ---------------------------------------------------------------------------
# Dataset ID resolution
# ---------------------------------------------------------------------------

def resolve_dataset_id_for_dashboard() -> str:
    """Resolve the dataset ID for all HAMM Overview charts.

    Returns:
        Dataset ID string

    Raises:
        ValueError: If multiple dataset IDs are found
    """
    component_ids = [
        KPI_ID_KPI_TOTAL_SCREENS,
        KPI_ID_KPI_TOTAL_ERV,
        KPI_ID_KPI_TOTAL_PRELIM,
        TABLE_ID_VOLUME_TABLE,
        CHART_ID_VOLUME_CHART,
        TABLE_ID_TASK_TABLE,
        TABLE_ID_LANGUAGE_TABLE,
        CHART_ID_ERROR_RATIO,
        CHART_ID_ERROR_BY_SCREENER,
        CHART_ID_USER_BREAKDOWN,
        CHART_ID_BREAKDOWN,
        CHART_ID_METADATA_ORIGINAL_LANGUAGE,
        CHART_ID_METADATA_DIALOGUE,
        CHART_ID_METADATA_GENRE,
    ]
    dataset_ids = {
        resolve_dataset_id(DASHBOARD_ID, comp_id) for comp_id in component_ids
    }
    if len(dataset_ids) != 1:
        raise ValueError(
            f"Multiple dataset IDs found for HAMM Overview dashboard: "
            f"{sorted(dataset_ids)}"
        )
    return next(iter(dataset_ids))
