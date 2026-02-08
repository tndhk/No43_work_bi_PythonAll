"""Tests for filter UI components."""
import pytest
import pandas as pd
from dash import html
from src.components.filters import create_category_filter, create_date_range_filter, create_slicer_filter


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


class TestSlicerFilterChipLayout:
    """Slicer filter chips should be wrapped in flex container."""

    def test_chipgroup_wrapped_in_flex_div(self):
        """ChipGroup must be wrapped in html.Div with flex-wrap style."""
        card = create_slicer_filter(
            filter_id="test-filter",
            column_name="Test",
            options=["A", "B", "C"],
        )
        # card -> CardBody -> children[0] should be html.Div wrapper
        card_body = card.children[1]  # CardBody (index 1, after CardHeader)
        wrapper = card_body.children[0]
        assert isinstance(wrapper, html.Div)
        style = getattr(wrapper, "style", {})
        assert style.get("display") == "flex"
        assert style.get("flexWrap") == "wrap"

    def test_single_select_default_value_is_scalar(self):
        """Single-select slicer should set scalar ChipGroup value."""
        card = create_slicer_filter(
            filter_id="single-filter",
            column_name="Single",
            options=[
                {"label": "All", "value": "all"},
                {"label": "Only", "value": "only"},
            ],
            multi=False,
            default_value="all",
        )
        card_body = card.children[1]
        wrapper = card_body.children[0]
        chip_group = wrapper.children
        assert chip_group.multiple is False
        assert chip_group.value == "all"

    def test_slicer_with_clear_button_renders_button(self):
        """Slicer header should include clear button when clear_button_id is set."""
        card = create_slicer_filter(
            filter_id="clearable-filter",
            column_name="Clearable",
            options=["A", "B"],
            clear_button_id="clearable-btn",
        )
        card_header = card.children[0]
        header_div = card_header.children
        button = header_div.children[1]
        assert button.id == "clearable-btn"
