"""Filter engine for applying filters to DataFrames."""
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
from datetime import datetime


@dataclass(frozen=True)
class CategoryFilter:
    """Category filter definition."""

    column: str
    values: list[str]
    include_null: bool = False


@dataclass(frozen=True)
class DateRangeFilter:
    """Date range filter definition."""

    column: str
    start_date: str  # ISO 8601 (YYYY-MM-DD)
    end_date: str    # ISO 8601 (YYYY-MM-DD)


@dataclass
class FilterSet:
    """Set of filters to apply."""

    category_filters: list[CategoryFilter] = field(default_factory=list)
    date_filters: list[DateRangeFilter] = field(default_factory=list)


def apply_filters(df: pd.DataFrame, filter_set: FilterSet) -> pd.DataFrame:
    """
    Apply filters to a DataFrame.

    Filter application rules (per tech-spec 3.3):
    - Category filter: df[column].isin(values)
    - Category filter (with NULL): isin(values) | isna()
    - Date filter: start_date <= column <= end_date (inclusive boundaries)
    - Multiple filters are combined with AND condition

    Date boundary rules:
    - Start date: from 00:00:00 (inclusive)
    - End date: until 23:59:59 (inclusive)
    - Timezone: JST (Asia/Tokyo) fixed

    Args:
        df: Source DataFrame
        filter_set: Set of filters to apply

    Returns:
        Filtered DataFrame (original df is not modified)
    """
    result = df.copy()

    # Apply category filters
    for cat_filter in filter_set.category_filters:
        if cat_filter.column not in result.columns:
            continue

        if cat_filter.include_null:
            # Include NULL values
            mask = (
                result[cat_filter.column].isin(cat_filter.values)
                | result[cat_filter.column].isna()
            )
        else:
            # Exclude NULL values
            mask = result[cat_filter.column].isin(cat_filter.values)

        result = result[mask]

    # Apply date filters
    for date_filter in filter_set.date_filters:
        if date_filter.column not in result.columns:
            continue

        # Convert date strings to datetime for comparison
        start_dt = pd.to_datetime(date_filter.start_date)
        end_dt = pd.to_datetime(date_filter.end_date)

        # Set time to end of day for end_date (23:59:59)
        end_dt = end_dt.replace(hour=23, minute=59, second=59)

        # Apply filter (boundaries inclusive)
        mask = (result[date_filter.column] >= start_dt) & (
            result[date_filter.column] <= end_dt
        )
        result = result[mask]

    return result


def extract_unique_values(df: pd.DataFrame, column: str) -> list:
    """Extract unique values from a column, sorted, excluding NaN/None.

    Args:
        df: DataFrame to extract values from.
        column: Column name.

    Returns:
        Sorted list of unique values. Empty list if column is missing.
    """
    if column not in df.columns:
        return []
    return sorted(df[column].dropna().unique().tolist())
