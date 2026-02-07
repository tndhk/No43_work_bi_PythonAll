"""Tests for filter engine."""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime
from src.data.filter_engine import (
    CategoryFilter,
    DateRangeFilter,
    FilterSet,
    apply_filters,
    extract_unique_values,
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
    assert len(result) == 3
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
    assert len(result) == 2
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


# --- FilterSet mutability tests ---


def test_filterset_is_mutable():
    """Test: FilterSet allows field reassignment (not frozen)."""
    # Given: A FilterSet with one category filter
    filter_set = FilterSet(
        category_filters=[
            CategoryFilter(column="category", values=["A"]),
        ],
    )

    # When: Reassigning category_filters field
    new_filters = [CategoryFilter(column="category", values=["B"])]
    filter_set.category_filters = new_filters

    # Then: Field is updated without raising an error
    assert len(filter_set.category_filters) == 1
    assert filter_set.category_filters[0].values == ["B"]


def test_filterset_list_append_after_creation():
    """Test: FilterSet allows appending to its list fields after creation."""
    # Given: An empty FilterSet
    filter_set = FilterSet()

    # When: Appending a filter to the list
    filter_set.category_filters.append(
        CategoryFilter(column="status", values=["active"])
    )

    # Then: The appended filter is present
    assert len(filter_set.category_filters) == 1
    assert filter_set.category_filters[0].column == "status"


# --- extract_unique_values tests ---


class TestExtractUniqueValues:
    """Tests for extract_unique_values helper."""

    def test_returns_sorted_unique_values(self):
        """Test: Returns sorted unique values when column exists."""
        # Given: DataFrame with duplicate values in a column
        df = pd.DataFrame({"color": ["red", "blue", "red", "green", "blue"]})

        # When: Extracting unique values
        result = extract_unique_values(df, "color")

        # Then: Sorted unique values are returned
        assert result == ["blue", "green", "red"]

    def test_returns_empty_list_when_column_missing(self):
        """Test: Returns empty list when column does not exist."""
        # Given: DataFrame without the target column
        df = pd.DataFrame({"name": ["Alice", "Bob"]})

        # When: Extracting unique values from a non-existent column
        result = extract_unique_values(df, "missing_column")

        # Then: Empty list is returned
        assert result == []

    def test_excludes_nan_values(self):
        """Test: NaN values are excluded from the result."""
        # Given: DataFrame with NaN values
        df = pd.DataFrame({"status": ["active", None, "inactive", np.nan, "active"]})

        # When: Extracting unique values
        result = extract_unique_values(df, "status")

        # Then: NaN/None are excluded, remaining values are sorted and unique
        assert result == ["active", "inactive"]

    def test_returns_empty_list_for_empty_dataframe(self):
        """Test: Returns empty list when DataFrame is empty."""
        # Given: Empty DataFrame with the target column
        df = pd.DataFrame({"category": pd.Series([], dtype="object")})

        # When: Extracting unique values
        result = extract_unique_values(df, "category")

        # Then: Empty list is returned
        assert result == []

    def test_numeric_values_sorted(self):
        """Test: Numeric values are also sorted correctly."""
        # Given: DataFrame with numeric column
        df = pd.DataFrame({"score": [30, 10, 20, 10, 30]})

        # When: Extracting unique values
        result = extract_unique_values(df, "score")

        # Then: Sorted unique numeric values are returned
        assert result == [10, 20, 30]

    def test_all_nan_column(self):
        """Test: Column with only NaN values returns empty list."""
        # Given: DataFrame where column has only NaN
        df = pd.DataFrame({"data": [None, np.nan, None]})

        # When: Extracting unique values
        result = extract_unique_values(df, "data")

        # Then: Empty list is returned
        assert result == []
