"""Tests for filter engine."""
import pytest
import pandas as pd
from datetime import datetime
from src.data.filter_engine import (
    CategoryFilter,
    DateRangeFilter,
    FilterSet,
    apply_filters,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample DataFrame for filter testing."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "category": ["A", "B", "A", "C", None],
        "amount": [100.0, 200.0, 300.0, 400.0, 500.0],
        "date": pd.to_datetime([
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
        ]),
    })


def test_apply_filters_empty(sample_df):
    """Test: Empty filter set returns original DataFrame."""
    # Given: Empty filter set
    filter_set = FilterSet()

    # When: Applying filters
    result = apply_filters(sample_df, filter_set)

    # Then: Original DataFrame is returned
    assert len(result) == len(sample_df)
    pd.testing.assert_frame_equal(result, sample_df)


def test_category_filter_single_value(sample_df):
    """Test: Category filter with single value."""
    # Given: Filter for category "A"
    filter_set = FilterSet(
        category_filters=[
            CategoryFilter(column="category", values=["A"]),
        ],
    )

    # When: Applying filters
    result = apply_filters(sample_df, filter_set)

    # Then: Only rows with category "A" are returned
    assert len(result) == 2
    assert all(result["category"] == "A")


def test_category_filter_multiple_values(sample_df):
    """Test: Category filter with multiple values."""
    # Given: Filter for category "A" or "B"
    filter_set = FilterSet(
        category_filters=[
            CategoryFilter(column="category", values=["A", "B"]),
        ],
    )

    # When: Applying filters
    result = apply_filters(sample_df, filter_set)

    # Then: Rows with category "A" or "B" are returned
    assert len(result) == 2
    assert set(result["category"].dropna()) == {"A", "B"}


def test_category_filter_with_null(sample_df):
    """Test: Category filter with include_null=True."""
    # Given: Filter for category "A" including NULL
    filter_set = FilterSet(
        category_filters=[
            CategoryFilter(column="category", values=["A"], include_null=True),
        ],
    )

    # When: Applying filters
    result = apply_filters(sample_df, filter_set)

    # Then: Rows with category "A" or NULL are returned
    assert len(result) == 3
    assert result["category"].isna().sum() == 1
    assert (result["category"] == "A").sum() == 2


def test_date_range_filter(sample_df):
    """Test: Date range filter."""
    # Given: Filter for date range 2024-01-02 to 2024-01-04
    filter_set = FilterSet(
        date_filters=[
            DateRangeFilter(
                column="date",
                start_date="2024-01-02",
                end_date="2024-01-04",
            ),
        ],
    )

    # When: Applying filters
    result = apply_filters(sample_df, filter_set)

    # Then: Only rows in date range are returned
    assert len(result) == 3
    assert result["date"].min().date().isoformat() == "2024-01-02"
    assert result["date"].max().date().isoformat() == "2024-01-04"


def test_date_range_filter_boundary_inclusive(sample_df):
    """Test: Date range filter includes boundaries."""
    # Given: Filter for exact date range
    filter_set = FilterSet(
        date_filters=[
            DateRangeFilter(
                column="date",
                start_date="2024-01-02",
                end_date="2024-01-02",
            ),
        ],
    )

    # When: Applying filters
    result = apply_filters(sample_df, filter_set)

    # Then: Boundary date is included
    assert len(result) == 1
    assert result["date"].iloc[0].date().isoformat() == "2024-01-02"


def test_combined_filters(sample_df):
    """Test: Combined category and date filters (AND condition)."""
    # Given: Category filter + date filter
    filter_set = FilterSet(
        category_filters=[
            CategoryFilter(column="category", values=["A"]),
        ],
        date_filters=[
            DateRangeFilter(
                column="date",
                start_date="2024-01-02",
                end_date="2024-01-03",
            ),
        ],
    )

    # When: Applying filters
    result = apply_filters(sample_df, filter_set)

    # Then: Rows matching both conditions are returned
    assert len(result) == 1
    assert result["category"].iloc[0] == "A"
    assert result["date"].iloc[0].date().isoformat() == "2024-01-03"


def test_multiple_category_filters(sample_df):
    """Test: Multiple category filters on different columns."""
    # Given: Multiple category filters
    df = sample_df.copy()
    df["status"] = ["active", "inactive", "active", "inactive", "active"]

    filter_set = FilterSet(
        category_filters=[
            CategoryFilter(column="category", values=["A"]),
            CategoryFilter(column="status", values=["active"]),
        ],
    )

    # When: Applying filters
    result = apply_filters(df, filter_set)

    # Then: Rows matching all filters are returned
    assert len(result) == 1
    assert result["category"].iloc[0] == "A"
    assert result["status"].iloc[0] == "active"


def test_empty_dataframe():
    """Test: Filtering empty DataFrame returns empty DataFrame."""
    # Given: Empty DataFrame
    df = pd.DataFrame({"category": [], "date": []})

    # When: Applying filters
    filter_set = FilterSet(
        category_filters=[
            CategoryFilter(column="category", values=["A"]),
        ],
    )
    result = apply_filters(df, filter_set)

    # Then: Empty DataFrame is returned
    assert len(result) == 0
