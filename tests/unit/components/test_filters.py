"""Tests for filter UI components."""
import pytest
import pandas as pd
from dash import html
from src.components.filters import create_category_filter, create_date_range_filter


def test_create_category_filter():
    """Test: Category filter component is created."""
    # Given: Filter parameters
    filter_id = "category-filter"
    column_name = "category"
    options = ["A", "B", "C"]

    # When: Creating category filter
    component = create_category_filter(filter_id, column_name, options)

    # Then: Component is created (Card wrapper)
    assert component is not None
    # Component structure verification would require Dash component inspection


def test_create_date_range_filter():
    """Test: Date range filter component is created."""
    # Given: Filter parameters
    filter_id = "date-filter"
    column_name = "date"
    min_date = "2024-01-01"
    max_date = "2024-12-31"

    # When: Creating date range filter
    component = create_date_range_filter(
        filter_id, column_name, min_date, max_date
    )

    # Then: Component is created
    assert component is not None
