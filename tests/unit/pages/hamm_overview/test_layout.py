"""Tests for Hamm Overview layout structure.

These tests verify the expected layout grid configuration:
- Row 1: CSS Grid with title (4 cols) + 3 filters (1 col each) -- className="filter-row-title-3filters"
- Row 2: CSS Grid with 7 equal columns (html.Div className="filter-row-7col")
- Title fontSize: 32px

Helper utilities:
- find_components: generic tree walker with a user-supplied predicate
"""
from unittest.mock import patch, MagicMock
from dash import html, dcc
import dash_bootstrap_components as dbc

import pytest

from tests.helpers.dash_test_utils import find_components

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
        _layout_mod, "resolve_dataset_id_for_dashboard", return_value="hamm-dashboard"
    ):
        return _layout_mod.build_layout()




class TestRow1FilterRow:
    """Row 1: CSS Grid with title (4 cols) + 3 filters (1 col each)."""

    def _find_filter_row_title_3filters(self, layout) -> list:
        return find_components(
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
        return find_components(
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
        divs = find_components(
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
        card_bodies = find_components(
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
        candidates = find_components(
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
        h3_list = find_components(
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
        p_list = find_components(
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
        rows = find_components(
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
        rows = find_components(
            layout,
            lambda c: isinstance(c, dbc.Row),
        )

        # Find the row that contains the Volume section (backgroundColor=#2f5f8f)
        volume_row = None
        for row in rows:
            volume_divs = find_components(
                row,
                lambda c: isinstance(c, html.Div)
                and isinstance(getattr(c, "style", None), dict)
                and getattr(c, "style", {}).get("backgroundColor") == "#2f5f8f",
            )
            if volume_divs:
                volume_row = row
                break

        assert volume_row is not None, "Could not find dbc.Row containing Volume section"

        cols = find_components(
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
            for c in find_components(layout, lambda c: getattr(c, "id", None) is not None)
        }
        for clear_id in clear_ids:
            assert clear_id in found_ids, f"{clear_id} not found in layout"


class TestContentMetadataSection:
    def test_content_metadata_header_exists(self, layout):
        header_divs = find_components(
            layout,
            lambda c: isinstance(c, html.H3) and getattr(c, "children", "") == "Content Metadata",
        )
        assert len(header_divs) >= 1, "Content Metadata header not found"

    def test_content_metadata_graph_ids_exist(self, layout):
        expected_ids = {
            "hamm-metadata-original-language",
            "hamm-metadata-dialogue",
            "hamm-metadata-genre",
        }
        graphs = find_components(layout, lambda c: isinstance(c, dcc.Graph))
        graph_ids = {getattr(g, "id", None) for g in graphs}

        for expected_id in expected_ids:
            assert expected_id in graph_ids, f"{expected_id} not found in layout"

    def test_content_metadata_row_has_scope_class(self, layout):
        rows = find_components(
            layout,
            lambda c: isinstance(c, dbc.Row)
            and "chart-density-row" in (getattr(c, "className", None) or ""),
        )
        assert len(rows) >= 1, "chart-density-row class not found"

    def test_content_metadata_cards_have_class(self, layout):
        cards = find_components(
            layout,
            lambda c: isinstance(c, dbc.Card)
            and "chart-density-card" in (getattr(c, "className", None) or ""),
        )
        assert len(cards) == 8, f"Expected 8 density cards (3 metadata + 1 volume + 4 error), got {len(cards)}"

    def test_content_metadata_graphs_have_class_and_config(self, layout):
        expected_ids = {
            "hamm-metadata-original-language",
            "hamm-metadata-dialogue",
            "hamm-metadata-genre",
        }
        graphs = find_components(
            layout,
            lambda c: isinstance(c, dcc.Graph) and getattr(c, "id", None) in expected_ids,
        )
        assert len(graphs) == 3, f"Expected 3 metadata graphs, got {len(graphs)}"

        for graph in graphs:
            class_name = getattr(graph, "className", "") or ""
            assert "chart-density-graph" in class_name
            config = getattr(graph, "config", None) or {}
            assert config.get("displayModeBar") is False
            assert config.get("responsive") is True


# ---------------------------------------------------------------------------
# Language Table layout presence (RED -- not yet implemented)
# ---------------------------------------------------------------------------

class TestVolumeSectionDensity:
    """Volume Chart card must have chart-density classes and config."""

    def test_volume_chart_has_density_graph_class(self, layout):
        """The Volume Chart dcc.Graph must have className='chart-density-graph'."""
        from src.pages.hamm_overview._constants import CHART_ID_VOLUME_CHART

        graphs = find_components(
            layout,
            lambda c: isinstance(c, dcc.Graph)
            and getattr(c, "id", None) == CHART_ID_VOLUME_CHART,
        )
        assert len(graphs) == 1, f"Expected 1 Volume Chart graph, got {len(graphs)}"
        class_name = getattr(graphs[0], "className", "") or ""
        assert "chart-density-graph" in class_name, (
            f"Volume Chart graph should have 'chart-density-graph' class, got '{class_name}'"
        )

    def test_volume_chart_has_config(self, layout):
        """The Volume Chart dcc.Graph must have config with displayModeBar=False and responsive=True."""
        from src.pages.hamm_overview._constants import CHART_ID_VOLUME_CHART

        graphs = find_components(
            layout,
            lambda c: isinstance(c, dcc.Graph)
            and getattr(c, "id", None) == CHART_ID_VOLUME_CHART,
        )
        assert len(graphs) == 1, f"Expected 1 Volume Chart graph, got {len(graphs)}"
        config = getattr(graphs[0], "config", None) or {}
        assert config.get("displayModeBar") is False, (
            f"Volume Chart config.displayModeBar should be False, got {config.get('displayModeBar')}"
        )
        assert config.get("responsive") is True, (
            f"Volume Chart config.responsive should be True, got {config.get('responsive')}"
        )


class TestErrorDetailsDensity:
    """Error Details charts must have chart-density classes and config."""

    _ERROR_CHART_IDS = [
        "hamm-error-ratio",
        "hamm-error-by-screener",
        "hamm-user-breakdown",
        "hamm-hamm-breakdown",
    ]

    def test_error_charts_have_density_graph_class(self, layout):
        """All 4 Error Detail dcc.Graph components must have className='chart-density-graph'."""
        for chart_id in self._ERROR_CHART_IDS:
            graphs = find_components(
                layout,
                lambda c, cid=chart_id: isinstance(c, dcc.Graph)
                and getattr(c, "id", None) == cid,
            )
            assert len(graphs) == 1, f"Expected 1 graph with id='{chart_id}', got {len(graphs)}"
            class_name = getattr(graphs[0], "className", "") or ""
            assert "chart-density-graph" in class_name, (
                f"Graph '{chart_id}' should have 'chart-density-graph' class, got '{class_name}'"
            )

    def test_error_charts_have_config(self, layout):
        """All 4 Error Detail dcc.Graph components must have config with displayModeBar=False and responsive=True."""
        for chart_id in self._ERROR_CHART_IDS:
            graphs = find_components(
                layout,
                lambda c, cid=chart_id: isinstance(c, dcc.Graph)
                and getattr(c, "id", None) == cid,
            )
            assert len(graphs) == 1, f"Expected 1 graph with id='{chart_id}', got {len(graphs)}"
            config = getattr(graphs[0], "config", None) or {}
            assert config.get("displayModeBar") is False, (
                f"Graph '{chart_id}' config.displayModeBar should be False, got {config.get('displayModeBar')}"
            )
            assert config.get("responsive") is True, (
                f"Graph '{chart_id}' config.responsive should be True, got {config.get('responsive')}"
            )

    def test_error_details_rows_have_density_row_class(self, layout):
        """The 2 Error Details dbc.Row containers must have 'chart-density-row' in className."""
        rows = find_components(
            layout,
            lambda c: isinstance(c, dbc.Row)
            and "chart-density-row" in (getattr(c, "className", None) or ""),
        )
        # Content Metadata has 1 density row, Error Details should add 2 more = 3 total
        assert len(rows) >= 3, (
            f"Expected at least 3 chart-density-row rows (1 metadata + 2 error), got {len(rows)}"
        )

    def test_error_details_cards_have_density_card_class(self, layout):
        """The 4 Error Details dbc.Card containers must have 'chart-density-card' in className."""
        # We find all density cards and verify the error ones specifically
        error_chart_ids = set(self._ERROR_CHART_IDS)
        error_density_cards = []

        all_density_cards = find_components(
            layout,
            lambda c: isinstance(c, dbc.Card)
            and "chart-density-card" in (getattr(c, "className", None) or ""),
        )
        for card in all_density_cards:
            graphs_in_card = find_components(
                card,
                lambda c: isinstance(c, dcc.Graph)
                and getattr(c, "id", None) in error_chart_ids,
            )
            if graphs_in_card:
                error_density_cards.append(card)

        assert len(error_density_cards) == 4, (
            f"Expected 4 Error Details cards with 'chart-density-card' class, got {len(error_density_cards)}"
        )


class TestLanguageTableInLayout:
    """Layout must contain a placeholder for CHART_ID_LANGUAGE_TABLE."""

    def test_language_table_id_exists_in_layout(self, layout):
        """A component with id=CHART_ID_LANGUAGE_TABLE must exist in the layout tree."""
        from src.pages.hamm_overview._constants import CHART_ID_LANGUAGE_TABLE

        all_components = find_components(
            layout,
            lambda c: getattr(c, "id", None) == CHART_ID_LANGUAGE_TABLE,
        )
        assert len(all_components) >= 1, (
            f"Component with id='{CHART_ID_LANGUAGE_TABLE}' not found in layout"
        )


class TestRow1HeaderBarStyle:
    """Row 1 title must have DOMO-style blue background."""

    def _get_title(self, layout):
        divs = find_components(
            layout,
            lambda c: isinstance(c, html.Div)
            and "filter-row-title-3filters" in (getattr(c, "className", None) or ""),
        )
        assert len(divs) >= 1, "filter-row-title-3filters div not found"
        children = divs[0].children if isinstance(divs[0].children, list) else [divs[0].children]
        return children[0]

    def test_title_has_blue_background(self, layout):
        """The title element must have backgroundColor='#4a7fb5'."""
        title_div = self._get_title(layout)
        style = getattr(title_div, "style", {})
        assert style.get("backgroundColor") == "#4a7fb5", (
            f"Title should have backgroundColor='#4a7fb5', got '{style.get('backgroundColor')}'"
        )

    def test_title_has_white_color(self, layout):
        """The title element must have style color='white'."""
        title_div = self._get_title(layout)
        style = getattr(title_div, "style", {})
        assert style.get("color") == "white", (
            f"Title should have color='white', got '{style.get('color')}'"
        )


class TestFilterPlacement:
    """Filters must be placed in correct rows matching DOMO layout."""

    def _get_row1(self, layout):
        divs = find_components(
            layout,
            lambda c: isinstance(c, html.Div)
            and "filter-row-title-3filters" in (getattr(c, "className", None) or ""),
        )
        assert len(divs) >= 1
        return divs[0]

    def _get_row2(self, layout):
        divs = find_components(
            layout,
            lambda c: isinstance(c, html.Div)
            and "filter-row-7col" in (getattr(c, "className", None) or ""),
        )
        assert len(divs) >= 1
        return divs[0]

    def _find_filter_ids_in(self, component) -> list[str]:
        """Extract all filter IDs (from Dropdown and ChipGroup) within a component."""
        all_ids = find_components(
            component,
            lambda c: getattr(c, "id", None) is not None,
        )
        return [getattr(c, "id", None) for c in all_ids]

    def test_month_in_row1(self, layout):
        """Month filter (hamm-filter-month) must be in Row 1."""
        row1 = self._get_row1(layout)
        ids = self._find_filter_ids_in(row1)
        assert "hamm-filter-month" in ids, (
            f"'hamm-filter-month' should be in Row 1, found IDs: {ids}"
        )

    def test_content_type_in_row2(self, layout):
        """Content Type filter (hamm-filter-content-type) must be in Row 2."""
        row2 = self._get_row2(layout)
        ids = self._find_filter_ids_in(row2)
        assert "hamm-filter-content-type" in ids, (
            f"'hamm-filter-content-type' should be in Row 2, found IDs: {ids}"
        )

    def test_content_type_not_in_row1(self, layout):
        """Content Type filter must NOT be in Row 1."""
        row1 = self._get_row1(layout)
        ids = self._find_filter_ids_in(row1)
        assert "hamm-filter-content-type" not in ids, (
            "Content Type should not be in Row 1"
        )

    def test_month_not_in_row2(self, layout):
        """Month filter must NOT be in Row 2."""
        row2 = self._get_row2(layout)
        ids = self._find_filter_ids_in(row2)
        assert "hamm-filter-month" not in ids, (
            "Month should not be in Row 2"
        )

    def test_row2_filter_order(self, layout):
        """Row 2 filters must follow DOMO order: Task ID, Content Type, Original Language, Dialogue, Genre, Error Code, Error Type."""
        row2 = self._get_row2(layout)
        children = row2.children if isinstance(row2.children, list) else [row2.children]

        # Each child is a dbc.Card; extract the filter ID from each card
        card_filter_ids = []
        for child in children:
            ids = self._find_filter_ids_in(child)
            # Filter out clear button IDs (they contain "ctrl-clear")
            filter_ids = [fid for fid in ids if "ctrl-clear" not in fid]
            if filter_ids:
                card_filter_ids.append(filter_ids[0])

        expected_order = [
            "hamm-filter-task-id",
            "hamm-filter-content-type",
            "hamm-filter-original-language",
            "hamm-filter-dialogue",
            "hamm-filter-genre",
            "hamm-filter-error-code",
            "hamm-filter-error-type",
        ]
        assert card_filter_ids == expected_order, (
            f"Row 2 filter order mismatch.\nExpected: {expected_order}\nGot: {card_filter_ids}"
        )
