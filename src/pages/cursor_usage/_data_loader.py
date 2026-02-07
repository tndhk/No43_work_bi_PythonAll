"""Data loading and filtering logic for Cursor Usage Dashboard.

Extracts data access concerns from the page module so that layout()
and update_dashboard() remain thin UI-only functions.
"""
import pandas as pd

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.filter_engine import FilterSet, CategoryFilter, DateRangeFilter, apply_filters, extract_unique_values
from ._constants import COLUMN_MAP


def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:
    """Load filter option values from cached dataset.

    Returns a dict with keys:
        models, min_date, max_date

    On any exception the function returns safe defaults (empty lists / None)
    so that the layout can still render.
    """
    try:
        df = get_cached_dataset(reader, dataset_id)

        # Strip timezone for filter compatibility
        df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_convert(None)
        df["DateOnly"] = df["Date"].dt.date

        # Extract unique model values (exclude NaN)
        models = extract_unique_values(df, COLUMN_MAP["model"])

        # Extract date range
        if len(df) > 0:
            min_date = df["DateOnly"].min().isoformat()
            max_date = df["DateOnly"].max().isoformat()
        else:
            min_date = None
            max_date = None

        return {
            "models": models,
            "min_date": min_date,
            "max_date": max_date,
        }

    except Exception:
        return {
            "models": [],
            "min_date": None,
            "max_date": None,
        }


def load_and_filter_data(
    reader: ParquetReader,
    dataset_id: str,
    start_date,
    end_date,
    model_values,
) -> pd.DataFrame:
    """Load dataset and apply all filter criteria.

    Args:
        reader: ParquetReader instance.
        dataset_id: S3 dataset identifier.
        start_date: ISO date string (YYYY-MM-DD) or None.
        end_date: ISO date string (YYYY-MM-DD) or None.
        model_values: List of model name strings or None/[].

    Returns:
        Filtered DataFrame with timezone-naive Date column and DateOnly column.
    """
    df = get_cached_dataset(reader, dataset_id)

    # Strip timezone for filter compatibility (Parquet returns UTC-aware)
    df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_convert(None)
    df["DateOnly"] = df["Date"].dt.date

    # Build FilterSet
    filters = FilterSet()

    if start_date and end_date:
        filters.date_filters.append(
            DateRangeFilter(
                column=COLUMN_MAP["date"],
                start_date=start_date,
                end_date=end_date,
            )
        )

    if model_values:
        filters.category_filters.append(
            CategoryFilter(
                column=COLUMN_MAP["model"],
                values=model_values,
            )
        )

    return apply_filters(df, filters)
