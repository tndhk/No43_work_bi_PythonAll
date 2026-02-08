"""Tests for Hamm Overview layout structure.

These tests verify the expected layout grid configuration:
- Row 1: CSS Grid with title (4 cols) + 3 filters (1 col each) -- className="filter-row-title-3filters"
- Row 2: CSS Grid with 7 equal columns (html.Div className="filter-row-7col")
- Title fontSize: 32px

Helper utilities:
- _find_components: generic tree walker with a user-supplied predicate
"""
from unittest.mock import patch, MagicMock
from dash import html
import dash_bootstrap_components as dbc

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


def _find_components(component, predicate) -> list:
    """Recursively find all components in the tree that satisfy *predicate*."""
    results = []
    if predicate(component):
        results.append(component)
    children = getattr(component, "children", None)
    if children is None:
        return results
    if not isinstance(children, list):
        children = [children]
    for child in children:
        if child is not None:
            results.extend(_find_components(child, predicate))
    return results


class TestRow1FilterRow:
    """Row 1: CSS Grid with title (4 cols) + 3 filters (1 col each)."""

    def _find_filter_row_title_3filters(self, layout) -> list:
        return _find_components(
            layout,
            lambda c: isinstance(c, html.Div)
            and "filter-row-title-3filters" in (getattr(c, "className", None) or ""),
        )

    def test_filter_row_title_3filters_exists(self, layout):
        """A html.Div with className 'filter-row-title-3filters' must exist."""
        divs = self._find_filter_row_title_3filters(layout)
        assert len(divs) >= 1, (
            "Expected at least one html.Div with className='filter-row-title-3filters'"
        )

    def test_filter_row_title_3filters_has_4_children(self, layout):
        """The filter-row-title-3filters div must contain exactly 4 child elements (title + 3 filters)."""
        divs = self._find_filter_row_title_3filters(layout)
        grid_div = divs[0]
        children = grid_div.children
        if not isinstance(children, list):
            children = [children]
        assert len(children) == 4, (
            f"filter-row-title-3filters should have 4 children (title + 3 filters), got {len(children)}"
        )


class TestRow2CssGrid:
    """Row 2: CSS Grid layout with 7 equal-width filter columns."""

    def _find_filter_row_7col(self, layout) -> list:
        return _find_components(
            layout,
            lambda c: isinstance(c, html.Div)
            and "filter-row-7col" in (getattr(c, "className", None) or ""),
        )

    def test_filter_row_7col_exists(self, layout):
        """A html.Div with className 'filter-row-7col' must exist."""
        divs = self._find_filter_row_7col(layout)
        assert len(divs) >= 1, (
            "Expected at least one html.Div with className='filter-row-7col'"
        )

    def test_filter_row_7col_has_7_children(self, layout):
        """The filter-row-7col div must contain exactly 7 child elements."""
        divs = self._find_filter_row_7col(layout)
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
        # Find the filter-row-title-3filters div
        divs = _find_components(
            layout,
            lambda c: isinstance(c, html.Div)
            and "filter-row-title-3filters" in (getattr(c, "className", None) or ""),
        )
        assert len(divs) >= 1, "filter-row-title-3filters div not found"

        grid_div = divs[0]
        children = grid_div.children if isinstance(grid_div.children, list) else [grid_div.children]

        # Title is the first child
        title_div = children[0]
        style = getattr(title_div, "style", {})
        assert style.get("fontSize") == "32px", (
            f"Title fontSize should be '32px', got '{style.get('fontSize')}'"
        )


class TestCadenceFilter:
    """Cadence filter CardBody must have className='cadence-chip-body'."""

    def test_cadence_card_body_has_classname(self, layout):
        """A dbc.CardBody with className containing 'cadence-chip-body' must exist."""
        card_bodies = _find_components(
            layout,
            lambda c: isinstance(c, dbc.CardBody),
        )
        assert len(card_bodies) >= 1, "No dbc.CardBody found in layout"

        matching = [
            cb for cb in card_bodies
            if "cadence-chip-body" in (getattr(cb, "className", None) or "")
        ]
        assert len(matching) >= 1, (
            "Expected at least one dbc.CardBody with className containing "
            f"'cadence-chip-body', but none found. "
            f"CardBody classNames: {[getattr(cb, 'className', None) for cb in card_bodies]}"
        )


class TestVolumeSectionWhiteText:
    """Volume section H3 and P must have white text color."""

    def _find_volume_section(self, layout):
        """Find the Volume section div (backgroundColor=#2f5f8f with list children containing H3)."""
        candidates = _find_components(
            layout,
            lambda c: isinstance(c, html.Div)
            and isinstance(getattr(c, "style", None), dict)
            and getattr(c, "style", {}).get("backgroundColor") == "#2f5f8f"
            and isinstance(getattr(c, "children", None), list),
        )
        return candidates

    def test_volume_h3_has_white_color(self, layout):
        """The H3 inside the Volume section must have style color='white'."""
        sections = self._find_volume_section(layout)
        assert len(sections) >= 1, "Volume section div (backgroundColor=#2f5f8f) not found"

        section = sections[0]
        h3_list = _find_components(
            section,
            lambda c: isinstance(c, html.H3),
        )
        assert len(h3_list) >= 1, "No H3 found inside Volume section"

        h3 = h3_list[0]
        style = getattr(h3, "style", None) or {}
        color = style.get("color", "")
        assert color == "white", (
            f"Volume H3 should have style color='white', got '{color}'"
        )

    def test_volume_p_has_white_color(self, layout):
        """The P inside the Volume section must have a white-ish text color."""
        sections = self._find_volume_section(layout)
        assert len(sections) >= 1, "Volume section div (backgroundColor=#2f5f8f) not found"

        section = sections[0]
        p_list = _find_components(
            section,
            lambda c: isinstance(c, html.P),
        )
        assert len(p_list) >= 1, "No P found inside Volume section"

        p = p_list[0]
        style = getattr(p, "style", None) or {}
        color = str(style.get("color", ""))
        assert "white" in color or "rgba(255" in color, (
            f"Volume P should have a white-ish text color, got '{color}'"
        )


class TestVolumeCadenceRowAlignment:
    """The dbc.Row containing Volume section and Cadence filter must use align-items-stretch."""

    def test_row_has_align_items_stretch(self, layout):
        """The dbc.Row wrapping Volume + Cadence must have 'align-items-stretch' in className."""
        rows = _find_components(
            layout,
            lambda c: isinstance(c, dbc.Row),
        )
        assert len(rows) >= 1, "No dbc.Row found in layout"

        matching_rows = [
            r for r in rows
            if "align-items-stretch" in (getattr(r, "className", None) or "")
        ]
        assert len(matching_rows) >= 1, (
            "Expected at least one dbc.Row with 'align-items-stretch' in className, "
            f"but none found. Row classNames: {[getattr(r, 'className', None) for r in rows]}"
        )

    def test_child_cols_have_d_flex(self, layout):
        """The dbc.Col children of the Volume/Cadence row must have 'd-flex' in className."""
        rows = _find_components(
            layout,
            lambda c: isinstance(c, dbc.Row),
        )

        # Find the row that contains the Volume section (backgroundColor=#2f5f8f)
        volume_row = None
        for row in rows:
            volume_divs = _find_components(
                row,
                lambda c: isinstance(c, html.Div)
                and isinstance(getattr(c, "style", None), dict)
                and getattr(c, "style", {}).get("backgroundColor") == "#2f5f8f",
            )
            if volume_divs:
                volume_row = row
                break

        assert volume_row is not None, "Could not find dbc.Row containing Volume section"

        cols = _find_components(
            volume_row,
            lambda c: isinstance(c, dbc.Col),
        )
        assert len(cols) >= 2, f"Expected at least 2 dbc.Col in Volume row, got {len(cols)}"

        for i, col in enumerate(cols):
            col_class = getattr(col, "className", None) or ""
            assert "d-flex" in col_class, (
                f"dbc.Col[{i}] in Volume/Cadence row should have 'd-flex' in className, "
                f"got '{col_class}'"
            )


class TestPerSlicerClearButtons:
    """Slicer filters should expose per-filter clear buttons."""

    def test_clear_buttons_exist_for_hamm_slicers(self, layout):
        clear_ids = {
            "hamm-ctrl-clear-region",
            "hamm-ctrl-clear-year",
            "hamm-ctrl-clear-content-type",
            "hamm-ctrl-clear-original-language",
            "hamm-ctrl-clear-dialogue",
            "hamm-ctrl-clear-genre",
            "hamm-ctrl-clear-error-type",
        }

        found_ids = {
            getattr(c, "id", None)
            for c in _find_components(layout, lambda c: getattr(c, "id", None) is not None)
        }
        for clear_id in clear_ids:
            assert clear_id in found_ids, f"{clear_id} not found in layout"
