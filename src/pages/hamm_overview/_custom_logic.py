"""Custom data transformation logic for HAMM Overview dashboard.

This module contains complex transformation functions that cannot be expressed
in page_spec.yaml's declarative data_transform operations.
"""
import calendar

import pandas as pd

from ._constants import COLUMN_MAP, ERV_LABEL, LANGUAGE_TABLE_SPEC, PRELIM_LABEL


# ---------------------------------------------------------------------------
# Scalar date formatters (used by .apply() and as reference for vec versions)
# ---------------------------------------------------------------------------

def _format_start_date_monthly(ts: pd.Timestamp) -> str:
    """Return '1-Mon-YY' for a timestamp, 'Null' for NaT."""
    if pd.isna(ts):
        return "Null"
    return ts.replace(day=1).strftime("%-d-%b-%y")


def _format_start_date_quarterly(ts: pd.Timestamp) -> str:
    """Return '1-Mon-YY' for the first day of the quarter, 'Null' for NaT."""
    if pd.isna(ts):
        return "Null"
    q_month = ((ts.month - 1) // 3) * 3 + 1
    return ts.replace(month=q_month, day=1).strftime("%-d-%b-%y")


def _format_end_date_quarterly(ts: pd.Timestamp) -> str:
    """Return 'dd-Mon-YY' for the last day of the quarter, 'Null' for NaT."""
    if pd.isna(ts):
        return "Null"
    q_end_month = ((ts.month - 1) // 3) * 3 + 3
    last_day = calendar.monthrange(ts.year, q_end_month)[1]
    return ts.replace(month=q_end_month, day=last_day).strftime("%-d-%b-%y")


def _format_start_date_yearly(ts: pd.Timestamp) -> str:
    """Return '1-Jan-YY' for the start of the year, 'Null' for NaT."""
    if pd.isna(ts):
        return "Null"
    return ts.replace(month=1, day=1).strftime("%-d-%b-%y")


def _format_end_date_yearly(ts: pd.Timestamp) -> str:
    """Return '31-Dec-YY' for the end of the year, 'Null' for NaT."""
    if pd.isna(ts):
        return "Null"
    return ts.replace(month=12, day=31).strftime("%-d-%b-%y")


# ---------------------------------------------------------------------------
# Vectorized date formatters
# ---------------------------------------------------------------------------

def _format_start_date_monthly_vec(series: pd.Series) -> pd.Series:
    """Vectorized: return '1-Mon-YY' for each timestamp, 'Null' for NaT."""
    if series.empty:
        return pd.Series([], dtype=str)
    mask = series.isna()
    # Month start: replace day with 1
    valid = series.dropna()
    starts = valid.dt.to_period("M").dt.to_timestamp()
    formatted = starts.dt.strftime("%-d-%b-%y")
    result = pd.Series("Null", index=series.index)
    result.loc[~mask] = formatted.values
    return result


def _format_start_date_quarterly_vec(series: pd.Series) -> pd.Series:
    """Vectorized: return '1-Mon-YY' for the first day of each quarter."""
    if series.empty:
        return pd.Series([], dtype=str)
    mask = series.isna()
    valid = series.dropna()
    starts = valid.dt.to_period("Q").dt.to_timestamp()
    formatted = starts.dt.strftime("%-d-%b-%y")
    result = pd.Series("Null", index=series.index)
    result.loc[~mask] = formatted.values
    return result


def _format_end_date_quarterly_vec(series: pd.Series) -> pd.Series:
    """Vectorized: return 'dd-Mon-YY' for the last day of each quarter."""
    if series.empty:
        return pd.Series([], dtype=str)
    mask = series.isna()
    valid = series.dropna()
    # End of quarter = start of next quarter - 1 day
    ends = (valid.dt.to_period("Q") + 1).dt.to_timestamp() - pd.Timedelta(days=1)
    formatted = ends.dt.strftime("%-d-%b-%y")
    result = pd.Series("Null", index=series.index)
    result.loc[~mask] = formatted.values
    return result


def _format_start_date_yearly_vec(series: pd.Series) -> pd.Series:
    """Vectorized: return '1-Jan-YY' for the start of each year."""
    if series.empty:
        return pd.Series([], dtype=str)
    mask = series.isna()
    valid = series.dropna()
    starts = valid.dt.to_period("Y").dt.to_timestamp()
    formatted = starts.dt.strftime("%-d-%b-%y")
    result = pd.Series("Null", index=series.index)
    result.loc[~mask] = formatted.values
    return result


def _format_end_date_yearly_vec(series: pd.Series) -> pd.Series:
    """Vectorized: return '31-Dec-YY' for the end of each year."""
    if series.empty:
        return pd.Series([], dtype=str)
    mask = series.isna()
    valid = series.dropna()
    ends = (valid.dt.to_period("Y") + 1).dt.to_timestamp() - pd.Timedelta(days=1)
    formatted = ends.dt.strftime("%-d-%b-%y")
    result = pd.Series("Null", index=series.index)
    result.loc[~mask] = formatted.values
    return result


# ---------------------------------------------------------------------------
# Vectorized Total Duration computation
# ---------------------------------------------------------------------------

def _compute_total_duration_vec(
    created: pd.Series, completed: pd.Series
) -> pd.Series:
    """Vectorized: compute 'HH:MM:SS' duration, '' for NaT completed.

    Args:
        created: Series of creation timestamps
        completed: Series of completion timestamps

    Returns:
        Series of formatted duration strings
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


# ---------------------------------------------------------------------------
# Cadence column generation
# ---------------------------------------------------------------------------

def add_cadence_columns(df: pd.DataFrame, cadence: str) -> pd.DataFrame:
    """Add cadence-specific derived columns (_fiscal_year, _fiscal_quarter,
    _iso_week, _start_date, _end_date).

    Args:
        df: DataFrame with created_at column (may be timezone-aware)
        cadence: One of "weekly", "monthly", "quarterly", "yearly"

    Returns:
        DataFrame with additional derived columns
    """
    df = df.copy()
    # Ensure timezone-naive for calculations
    created = pd.to_datetime(df[COLUMN_MAP["created_at"]], utc=True).dt.tz_convert(None)

    # Fiscal year: April start => created + 3 months gives fiscal year
    mask = created.isna()
    shifted = created + pd.DateOffset(months=3)
    df["_fiscal_year"] = shifted.dt.strftime("%Y")
    df.loc[mask, "_fiscal_year"] = "Null"

    # Fiscal quarter: standard calendar quarter Q1=Jan-Mar, Q2=Apr-Jun, etc.
    df["_fiscal_quarter"] = created.dt.quarter.astype("Int64").astype(str)
    df.loc[mask, "_fiscal_quarter"] = "Null"

    if cadence == "weekly":
        # Monday-start week: weekday() gives Mon=0..Sun=6
        # Start of week = date - weekday
        weekday = created.dt.weekday
        week_start = created - pd.to_timedelta(weekday, unit="D")
        week_end = week_start + pd.Timedelta(days=6)

        df["_start_date"] = week_start.dt.strftime("%d-%b-%y")
        df["_end_date"] = week_end.dt.strftime("%d-%b-%y")
        df["_iso_week"] = created.dt.isocalendar().week.astype(str).str.zfill(2).values

        df.loc[mask, "_start_date"] = "Null"
        df.loc[mask, "_end_date"] = "Null"
        df.loc[mask, "_iso_week"] = "Null"

    elif cadence == "monthly":
        df["_start_date"] = _format_start_date_monthly_vec(created)
        # End date = last day of month
        valid = created.dropna()
        end_dates = valid.dt.to_period("M").dt.to_timestamp(how="end")
        formatted_end = pd.Series(end_dates, index=valid.index).dt.strftime("%-d-%b-%y")
        df["_end_date"] = "Null"
        df.loc[~mask, "_end_date"] = formatted_end.values
        df["_iso_week"] = pd.NA

    elif cadence == "quarterly":
        df["_start_date"] = _format_start_date_quarterly_vec(created)
        df["_end_date"] = _format_end_date_quarterly_vec(created)
        df["_iso_week"] = pd.NA

    elif cadence == "yearly":
        df["_start_date"] = _format_start_date_yearly_vec(created)
        df["_end_date"] = _format_end_date_yearly_vec(created)
        df["_iso_week"] = pd.NA

    return df


# ---------------------------------------------------------------------------
# Task display table preparation
# ---------------------------------------------------------------------------

def prepare_task_display_df(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare task details for display in a DataTable.

    Columns: Task ID, Task Name, Content Type, Task Status,
             Source File Duration, Audio Details, Job Created,
             Completed / Err, Total Duration

    Sorts by Task ID (numeric ascending).
    """
    expected_cols = [
        "Task ID", "Task Name", "Content Type", "Task Status",
        "Source File Duration", "Audio Details",
        "Job Created", "Completed / Err", "Total Duration",
    ]

    if df.empty:
        return pd.DataFrame(columns=expected_cols)

    out = pd.DataFrame()
    out["Task ID"] = df[COLUMN_MAP["id"]].values
    out["Task Name"] = df[COLUMN_MAP["title"]].values
    out["Content Type"] = df[COLUMN_MAP["content_type"]].values
    out["Task Status"] = df[COLUMN_MAP["status"]].values
    out["Source File Duration"] = df[COLUMN_MAP["video_duration"]].values
    out["Audio Details"] = df[COLUMN_MAP["audio_details"]].values

    # Format datetime columns
    created_s = pd.to_datetime(df[COLUMN_MAP["created_at"]])
    completed_s = pd.to_datetime(df[COLUMN_MAP["completed_at"]])

    out["Job Created"] = created_s.dt.strftime("%Y-%m-%d %H:%M").values
    out["Completed / Err"] = completed_s.dt.strftime("%Y-%m-%d %H:%M").values

    # Total Duration: HH:MM:SS (supports >24h), '' for NaT completed
    out["Total Duration"] = _compute_total_duration_vec(
        created_s.reset_index(drop=True),
        completed_s.reset_index(drop=True),
    ).values

    # Sort by Task ID numerically
    out["_sort_key"] = pd.to_numeric(out["Task ID"], errors="coerce")
    out = out.sort_values("_sort_key").drop(columns=["_sort_key"]).reset_index(drop=True)

    return out


# ---------------------------------------------------------------------------
# Language display table preparation
# ---------------------------------------------------------------------------

def prepare_language_display_df(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare language details for display in a DataTable.

    Columns match LANGUAGE_TABLE_SPEC.column_order:
        Task ID, Task Name, Content Type, Status, Language Count, Additional Languages

    NaN Additional Languages are replaced with 'N/A'.
    Sorts by Task ID (numeric ascending).
    """
    column_order = LANGUAGE_TABLE_SPEC.column_order

    if df.empty:
        return pd.DataFrame(columns=column_order)

    out = pd.DataFrame()
    out["Task ID"] = df[COLUMN_MAP["id"]].values
    out["Task Name"] = df[COLUMN_MAP["title"]].values
    out["Content Type"] = df[COLUMN_MAP["content_type"]].values
    out["Status"] = df[COLUMN_MAP["status"]].values
    out["Language Count"] = df[COLUMN_MAP["language_count"]].values
    out["Additional Languages"] = df[COLUMN_MAP["additional_languages"]].fillna("N/A").values

    # Sort by Task ID numerically
    out["_sort_key"] = pd.to_numeric(out["Task ID"], errors="coerce")
    out = out.sort_values("_sort_key").drop(columns=["_sort_key"]).reset_index(drop=True)

    return out[column_order]


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
