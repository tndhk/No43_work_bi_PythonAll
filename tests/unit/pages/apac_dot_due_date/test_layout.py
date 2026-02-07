"""Tests for APAC DOT Due Date layout module.

TDD Step 1 (RED): These tests define the expected behavior of
build_layout() before implementation.
"""
import pytest
from unittest.mock import patch, MagicMock
from dash import html, dcc
import dash_bootstrap_components as dbc

from tests.helpers.dash_test_utils import find_component_by_id, find_components_by_type


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

def _make_filter_options() -> dict:
    """Create sample filter_options dict matching load_filter_options output."""
    return {
        "months": ["2024-01", "2024-02", "2024-03"],
        "areas": ["APAC", "EMEA"],
        "workstreams": ["WS-A", "WS-B", "WS-C"],
        "vendors": ["Vendor1", "Vendor2", "Vendor3"],
        "amp_vs_av": ["AMP", "AV"],
        "order_types": ["TypeA", "TypeB", "TypeC"],
        "total_count": 5,
        "prc_count": 2,
        "non_prc_count": 3,
    }


# ===========================================================================
# build_layout return type tests
# ===========================================================================

class TestBuildLayoutReturnType:
    """build_layout must return an html.Div component."""

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_returns_html_div(self, mock_load_opts, mock_reader_cls):
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        assert isinstance(result, html.Div)

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_has_page_container_class(self, mock_load_opts, mock_reader_cls):
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        assert "page-container" in result.className


# ===========================================================================
# Page title tests
# ===========================================================================

class TestPageTitle:
    """build_layout must include an H1 page title."""

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_contains_h1_title(self, mock_load_opts, mock_reader_cls):
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        h1_components = find_components_by_type(result, html.H1)
        assert len(h1_components) >= 1, "No H1 component found in layout"

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_h1_contains_dashboard_text(self, mock_load_opts, mock_reader_cls):
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        h1_components = find_components_by_type(result, html.H1)
        assert any(
            "APAC DOT Due Date Dashboard" in str(getattr(h1, "children", ""))
            for h1 in h1_components
        ), "H1 title text not found"


# ===========================================================================
# Filter section tests
# ===========================================================================

class TestFilterSection:
    """build_layout must include the filter rows from build_filter_layout."""

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_contains_num_percent_toggle(self, mock_load_opts, mock_reader_cls):
        """Filter panel's num-percent-toggle must be present in the layout."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        found = find_component_by_id(result, "apac-dot-ctrl-num-percent")
        assert found is not None, "apac-dot-ctrl-num-percent not found in layout"

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_contains_breakdown_tabs(self, mock_load_opts, mock_reader_cls):
        """Filter panel's breakdown-tabs must be present in the layout."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        found = find_component_by_id(result, "apac-dot-ctrl-breakdown")
        assert found is not None, "apac-dot-ctrl-breakdown not found in layout"

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_contains_filter_month(self, mock_load_opts, mock_reader_cls):
        """Filter panel's filter-month must be present in the layout."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        found = find_component_by_id(result, "apac-dot-filter-month")
        assert found is not None, "apac-dot-filter-month not found in layout"

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_contains_prc_filter(self, mock_load_opts, mock_reader_cls):
        """Filter panel's prc-filter must be present in the layout."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        found = find_component_by_id(result, "apac-dot-filter-prc")
        assert found is not None, "apac-dot-filter-prc not found in layout"


# ===========================================================================
# Chart / Table section tests
# ===========================================================================

class TestChartSection:
    """build_layout must include the chart/table section (apac-dot-chart-00)."""

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_contains_table_title_id(self, mock_load_opts, mock_reader_cls):
        """Table section must have an element with id='apac-dot-chart-00-title'."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        found = find_component_by_id(result, "apac-dot-chart-00-title")
        assert found is not None, "apac-dot-chart-00-title element not found in layout"

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_table_title_is_h3(self, mock_load_opts, mock_reader_cls):
        """apac-dot-chart-00-title should be an H3 element."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        found = find_component_by_id(result, "apac-dot-chart-00-title")
        assert isinstance(found, html.H3), (
            f"Expected html.H3, got {type(found).__name__}"
        )

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_contains_apac_table_id(self, mock_load_opts, mock_reader_cls):
        """Table section must have an element with id='apac-dot-chart-00'."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        found = find_component_by_id(result, "apac-dot-chart-00")
        assert found is not None, "apac-dot-chart-00 element not found in layout"

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_apac_table_is_div(self, mock_load_opts, mock_reader_cls):
        """apac-dot-chart-00 should be an html.Div element."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        found = find_component_by_id(result, "apac-dot-chart-00")
        assert isinstance(found, html.Div), (
            f"Expected html.Div, got {type(found).__name__}"
        )


# ===========================================================================
# Layout structure order tests
# ===========================================================================

class TestLayoutStructureOrder:
    """Verify the overall structure: title -> filters -> chart section."""

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_layout_children_count(self, mock_load_opts, mock_reader_cls):
        """Layout should have at least 7 children: H1 + 5 filter rows + 1 chart row."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        children = result.children
        # H1 + 5 filter rows (spread) + 1 table row = 7
        assert len(children) >= 7, (
            f"Expected at least 7 children, got {len(children)}"
        )

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_first_child_is_h1(self, mock_load_opts, mock_reader_cls):
        """First child of layout should be the H1 title."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        assert isinstance(result.children[0], html.H1)

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    def test_last_child_is_table_section_row(self, mock_load_opts, mock_reader_cls):
        """Last child should be the dbc.Row containing the table section."""
        mock_load_opts.return_value = _make_filter_options()

        from src.pages.apac_dot_due_date._layout import build_layout

        result = build_layout()
        last_child = result.children[-1]
        assert isinstance(last_child, dbc.Row), (
            f"Expected last child to be dbc.Row, got {type(last_child).__name__}"
        )
        # The table-title should be inside the last child
        table_title = find_component_by_id(last_child, "apac-dot-chart-00-title")
        assert table_title is not None, "apac-dot-chart-00-title not in last row"


# ===========================================================================
# Integration: build_filter_layout is called correctly
# ===========================================================================

class TestBuildLayoutCallsFilterLayout:
    """build_layout must delegate filter construction to build_filter_layout."""

    @patch("src.pages.apac_dot_due_date._layout.ParquetReader")
    @patch("src.pages.apac_dot_due_date._layout.load_filter_options")
    @patch("src.pages.apac_dot_due_date._layout.build_filter_layout")
    def test_calls_build_filter_layout_with_options(
        self, mock_build_filter, mock_load_opts, mock_reader_cls
    ):
        opts = _make_filter_options()
        mock_load_opts.return_value = opts
        # Return minimal valid filter rows so layout construction doesn't fail
        mock_build_filter.return_value = [
            dbc.Row() for _ in range(5)
        ]

        from src.pages.apac_dot_due_date._layout import build_layout

        build_layout()
        mock_build_filter.assert_called_once_with(opts)
