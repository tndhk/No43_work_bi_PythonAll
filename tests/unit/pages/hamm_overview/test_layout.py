"""Tests for Hamm Overview layout structure.

These tests verify the expected layout grid configuration:
- Row 1: 4 columns (md=6, md=2, md=2, md=2) -- title + 3 filters
- Row 2: CSS Grid with 7 equal columns (html.Div className="filter-row-7col")
- Title fontSize: 32px
"""
from unittest.mock import patch, MagicMock
import dash_bootstrap_components as dbc
from dash import html

import pytest

# Import the module first so patch() can resolve the target
import src.pages.hamm_overview._layout as _layout_mod  # noqa: F401


_MOCK_OPTS = {
    "regions": ["APAC", "EMEA"],
    "years": ["2025", "2026"],
    "months": ["Jan", "Feb"],
    "task_ids": ["1", "2"],
    "content_types": ["Prelim", "ERV"],
    "original_languages": ["Japanese", "Korean"],
    "dialogue_options": ["Yes", "No"],
    "genres": ["Crime", "Drama"],
    "error_codes": ["E1", "E2"],
    "error_types": ["User", "System"],
}


@pytest.fixture()
def layout():
    """Build layout with mocked data dependencies."""
    with patch.object(
        _layout_mod, "load_filter_options", return_value=_MOCK_OPTS
    ), patch.object(
        _layout_mod, "ParquetReader", return_value=MagicMock()
    ), patch.object(
        _layout_mod, "resolve_dataset_id", return_value="hamm-dashboard"
    ):
        return _layout_mod.build_layout()


def _find_rows(component) -> list:
    """Recursively find all dbc.Row instances in the component tree."""
    rows = []
    if isinstance(component, dbc.Row):
        rows.append(component)
    children = getattr(component, "children", None)
    if children is None:
        return rows
    if not isinstance(children, list):
        children = [children]
    for child in children:
        if child is not None:
            rows.extend(_find_rows(child))
    return rows


def _get_col_md_values(row) -> list[int]:
    """Extract md values from all dbc.Col children in a Row."""
    children = row.children if isinstance(row.children, list) else [row.children]
    md_values = []
    for child in children:
        if isinstance(child, dbc.Col):
            md_values.append(child.md)
    return md_values


def _find_divs_with_class(component, class_name: str) -> list:
    """Recursively find all html.Div instances with a specific className."""
    results = []
    if isinstance(component, html.Div):
        cn = getattr(component, "className", None)
        if cn and class_name in cn:
            results.append(component)
    children = getattr(component, "children", None)
    if children is None:
        return results
    if not isinstance(children, list):
        children = [children]
    for child in children:
        if child is not None:
            results.extend(_find_divs_with_class(child, class_name))
    return results


class TestRow1FilterRow:
    """Row 1: title + Region / Year / Month filters -- 4 columns, md=[6,2,2,2]."""

    def test_row1_has_4_columns(self, layout):
        rows = _find_rows(layout)
        row1 = rows[0]
        md_values = _get_col_md_values(row1)
        assert len(md_values) == 4, (
            f"Row 1 should have 4 columns, got {len(md_values)}"
        )

    def test_row1_columns_md_6_2_2_2(self, layout):
        rows = _find_rows(layout)
        row1 = rows[0]
        md_values = _get_col_md_values(row1)
        assert md_values == [6, 2, 2, 2], (
            f"Row 1 columns should be md=[6,2,2,2], got {md_values}"
        )


class TestRow2CssGrid:
    """Row 2: CSS Grid layout with 7 equal-width filter columns."""

    def test_filter_row_7col_exists(self, layout):
        """A html.Div with className 'filter-row-7col' must exist."""
        divs = _find_divs_with_class(layout, "filter-row-7col")
        assert len(divs) >= 1, (
            "Expected at least one html.Div with className='filter-row-7col'"
        )

    def test_filter_row_7col_is_html_div(self, layout):
        """The filter-row-7col element must be an html.Div."""
        divs = _find_divs_with_class(layout, "filter-row-7col")
        assert len(divs) >= 1, "filter-row-7col not found"
        assert isinstance(divs[0], html.Div), (
            f"Expected html.Div, got {type(divs[0]).__name__}"
        )

    def test_filter_row_7col_has_7_children(self, layout):
        """The filter-row-7col div must contain exactly 7 child elements."""
        divs = _find_divs_with_class(layout, "filter-row-7col")
        assert len(divs) >= 1, "filter-row-7col not found"
        grid_div = divs[0]
        children = grid_div.children
        if not isinstance(children, list):
            children = [children]
        assert len(children) == 7, (
            f"filter-row-7col should have 7 children, got {len(children)}"
        )


class TestTitleStyle:
    """Title font size should be 32px."""

    def test_title_font_size_is_32px(self, layout):
        rows = _find_rows(layout)
        row1 = rows[0]
        # Title is inside the first Col of Row 1
        first_col = row1.children[0]
        # The Col contains an html.Div with the title text
        title_div = first_col.children
        if isinstance(title_div, list):
            title_div = title_div[0]
        style = getattr(title_div, "style", {})
        assert style.get("fontSize") == "32px", (
            f"Title fontSize should be '32px', got '{style.get('fontSize')}'"
        )
