"""Data loading and filtering logic for Cursor Usage Dashboard.

Extracts data access concerns from the page module so that layout()
and update_dashboard() remain thin UI-only functions.
"""
import pandas as pd

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.data_source_registry import resolve_dataset_id
from src.data.filter_engine import apply_filters, extract_unique_values
from src.utils.filter_helpers import build_filter_set_from_map
from ._constants import (
    COLUMN_MAP,
    DASHBOARD_ID,
    CHART_ID_KPI_TOTAL_COST,
    CHART_ID_KPI_TOTAL_TOKENS,
    CHART_ID_KPI_REQUEST_COUNT,
    CHART_ID_COST_TREND,
    CHART_ID_TOKEN_EFFICIENCY,
    CHART_ID_MODEL_DISTRIBUTION,
    CHART_ID_DATA_TABLE,
)


def resolve_dataset_id_for_dashboard() -> str:
    """Resolve the dataset ID for all Cursor Usage charts.

    Ensures every chart ID maps to exactly one dataset ID.
    """
    chart_ids = [
        CHART_ID_KPI_TOTAL_COST,
        CHART_ID_KPI_TOTAL_TOKENS,
        CHART_ID_KPI_REQUEST_COUNT,
        CHART_ID_COST_TREND,
        CHART_ID_TOKEN_EFFICIENCY,
        CHART_ID_MODEL_DISTRIBUTION,
        CHART_ID_DATA_TABLE,
    ]
    dataset_ids = {resolve_dataset_id(DASHBOARD_ID, chart_id) for chart_id in chart_ids}
    if len(dataset_ids) != 1:
        raise ValueError(
            "Multiple dataset IDs found for Cursor Usage dashboard: "
            f"{sorted(dataset_ids)}"
        )
    return next(iter(dataset_ids))


def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:
    """Load filter option values from cached dataset.

    Returns a dict with keys:
        models, users, min_date, max_date

    On any exception the function returns safe defaults (empty lists / None)
    so that the layout can still render.
    """
    try:
        df = get_cached_dataset(reader, dataset_id)

        date_col = COLUMN_MAP["date"]
        model_col = COLUMN_MAP["model"]
        user_col = COLUMN_MAP["user"]
        kind_col = COLUMN_MAP["kind"]

        # Strip timezone for filter compatibility
        df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.tz_convert(None)
        df["DateOnly"] = df[date_col].dt.date

        # Extract unique model values (exclude NaN)
        models = extract_unique_values(df, model_col)

        # Extract unique user values (exclude NaN)
        users = extract_unique_values(df, user_col)

        # Extract unique kind values (exclude NaN)
        kinds = extract_unique_values(df, kind_col)

        # Extract date range
        if len(df) > 0:
            min_date = df["DateOnly"].min().isoformat()
            max_date = df["DateOnly"].max().isoformat()
        else:
            min_date = None
            max_date = None

        return {
            "models": models,
            "users": users,
            "kinds": kinds,
            "min_date": min_date,
            "max_date": max_date,
        }

    except Exception:
        return {
            "models": [],
            "users": [],
            "kinds": [],
            "min_date": None,
            "max_date": None,
        }


def load_and_filter_data(
    reader: ParquetReader,
    dataset_id: str,
    start_date,
    end_date,
    model_values,
    user_values,
    kind_values,
) -> pd.DataFrame:
    """Load dataset and apply all filter criteria.

    Args:
        reader: ParquetReader instance.
        dataset_id: S3 dataset identifier.
        start_date: ISO date string (YYYY-MM-DD) or None.
        end_date: ISO date string (YYYY-MM-DD) or None.
        model_values: List of model name strings or None/[].
        user_values: List of user name strings or None/[].
        kind_values: List of kind strings or None/[].

    Returns:
        Filtered DataFrame with timezone-naive Date column and DateOnly column.
    """
    df = get_cached_dataset(reader, dataset_id)

    date_col = COLUMN_MAP["date"]
    # Strip timezone for filter compatibility (Parquet returns UTC-aware)
    df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.tz_convert(None)
    df["DateOnly"] = df[date_col].dt.date

    # Build FilterSet using shared helper
    filters = build_filter_set_from_map(
        column_map=COLUMN_MAP,
        filter_pairs=[
            ("model", model_values),
            ("user", user_values),
            ("kind", kind_values),
        ],
        date_range=("date", start_date, end_date) if start_date and end_date else None,
    )

    return apply_filters(df, filters)
