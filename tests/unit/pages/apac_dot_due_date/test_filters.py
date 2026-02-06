"""Tests for APAC DOT Due Date filter layout module.

TDD Step 1 (RED): These tests define the expected behavior of
build_filter_layout() before implementation.
"""
import pytest
from dash import html, dcc
import dash_bootstrap_components as dbc


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


def _make_empty_filter_options() -> dict:
    """Create filter_options with empty lists (error fallback state)."""
    return {
        "months": [],
        "areas": [],
        "workstreams": [],
        "vendors": [],
        "amp_vs_av": [],
        "order_types": [],
        "total_count": 0,
        "prc_count": 0,
        "non_prc_count": 0,
    }


# ===========================================================================
# build_filter_layout return type tests
# ===========================================================================

class TestBuildFilterLayoutReturnType:
    """build_filter_layout must return a list of dbc.Row components."""

    def test_returns_list(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        result = build_filter_layout(_make_filter_options())
        assert isinstance(result, list)

    def test_returns_non_empty_list(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        result = build_filter_layout(_make_filter_options())
        assert len(result) > 0

    def test_all_elements_are_dbc_row(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        result = build_filter_layout(_make_filter_options())
        for row in result:
            assert isinstance(row, dbc.Row), (
                f"Expected dbc.Row, got {type(row).__name__}"
            )

    def test_returns_five_rows(self):
        """Should produce 5 rows: control, month, prc, category, additional."""
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        result = build_filter_layout(_make_filter_options())
        assert len(result) == 5


# ===========================================================================
# Num/% toggle (control row) tests
# ===========================================================================

class TestNumPercentToggle:
    """First row must contain the Num/% RadioItems toggle."""

    def test_control_row_contains_num_percent_toggle(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        control_row = rows[0]

        # Recursively find the RadioItems component with id="apac-dot-ctrl-num-percent"
        found = _find_component_by_id(control_row, "apac-dot-ctrl-num-percent")
        assert found is not None, "apac-dot-ctrl-num-percent RadioItems not found in control row"

    def test_num_percent_toggle_default_value(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        toggle = _find_component_by_id(rows[0], "apac-dot-ctrl-num-percent")
        assert toggle.value == "num"

    def test_num_percent_toggle_has_two_options(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        toggle = _find_component_by_id(rows[0], "apac-dot-ctrl-num-percent")
        assert len(toggle.options) == 2

    def test_num_percent_toggle_option_values(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        toggle = _find_component_by_id(rows[0], "apac-dot-ctrl-num-percent")
        values = [opt["value"] for opt in toggle.options]
        assert "num" in values
        assert "percent" in values


# ===========================================================================
# Break Down tabs tests
# ===========================================================================

class TestBreakdownTabs:
    """First row must also contain the Break Down tabs."""

    def test_control_row_contains_breakdown_tabs(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = _find_component_by_id(rows[0], "apac-dot-ctrl-breakdown")
        assert found is not None, "apac-dot-ctrl-breakdown not found in control row"

    def test_breakdown_tabs_default_active_tab(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        tabs = _find_component_by_id(rows[0], "apac-dot-ctrl-breakdown")
        assert tabs.active_tab == "area"

    def test_breakdown_tabs_has_three_tabs(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        tabs = _find_component_by_id(rows[0], "apac-dot-ctrl-breakdown")
        assert len(tabs.children) == 3

    def test_breakdown_tabs_tab_ids(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        tabs = _find_component_by_id(rows[0], "apac-dot-ctrl-breakdown")
        tab_ids = [tab.tab_id for tab in tabs.children]
        assert tab_ids == ["area", "category", "vendor"]


# ===========================================================================
# Month filter tests
# ===========================================================================

class TestMonthFilter:
    """Second row must contain the Filter Month dropdown."""

    def test_month_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = _find_component_by_id(rows[1], "apac-dot-filter-month")
        assert found is not None, "apac-dot-filter-month dropdown not found"

    def test_month_filter_is_multi_select(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        dropdown = _find_component_by_id(rows[1], "apac-dot-filter-month")
        assert dropdown.multi is True

    def test_month_filter_default_value_all_months(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        opts = _make_filter_options()
        rows = build_filter_layout(opts)
        dropdown = _find_component_by_id(rows[1], "apac-dot-filter-month")
        assert dropdown.value == opts["months"]

    def test_month_filter_options_count(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        opts = _make_filter_options()
        rows = build_filter_layout(opts)
        dropdown = _find_component_by_id(rows[1], "apac-dot-filter-month")
        assert len(dropdown.options) == len(opts["months"])


# ===========================================================================
# PRC filter tests
# ===========================================================================

class TestPrcFilter:
    """Third row must contain the PRC RadioItems filter."""

    def test_prc_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = _find_component_by_id(rows[2], "apac-dot-filter-prc")
        assert found is not None, "apac-dot-filter-prc not found"

    def test_prc_filter_default_value(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        prc = _find_component_by_id(rows[2], "apac-dot-filter-prc")
        assert prc.value == "all"

    def test_prc_filter_has_three_options(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        prc = _find_component_by_id(rows[2], "apac-dot-filter-prc")
        assert len(prc.options) == 3

    def test_prc_filter_option_values(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        prc = _find_component_by_id(rows[2], "apac-dot-filter-prc")
        values = [opt["value"] for opt in prc.options]
        assert values == ["all", "prc_only", "prc_not_included"]

    def test_prc_filter_select_all_label_contains_total_count(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        opts = _make_filter_options()
        rows = build_filter_layout(opts)
        prc = _find_component_by_id(rows[2], "apac-dot-filter-prc")
        all_opt = [o for o in prc.options if o["value"] == "all"][0]
        assert str(opts["total_count"]) in all_opt["label"]


# ===========================================================================
# Category filters (row 4) tests
# ===========================================================================

class TestCategoryFilters:
    """Fourth row: Area, Category, Vendor dropdowns."""

    def test_area_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = _find_component_by_id(rows[3], "apac-dot-filter-area")
        assert found is not None, "apac-dot-filter-area not found in category row"

    def test_category_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = _find_component_by_id(rows[3], "apac-dot-filter-category")
        assert found is not None, "apac-dot-filter-category not found in category row"

    def test_vendor_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = _find_component_by_id(rows[3], "apac-dot-filter-vendor")
        assert found is not None, "apac-dot-filter-vendor not found in category row"


# ===========================================================================
# Additional filters (row 5) tests
# ===========================================================================

class TestAdditionalFilters:
    """Fifth row: AMP VS AV and Order Type dropdowns."""

    def test_amp_av_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = _find_component_by_id(rows[4], "apac-dot-filter-amp-av")
        assert found is not None, "apac-dot-filter-amp-av not found in additional row"

    def test_order_type_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = _find_component_by_id(rows[4], "apac-dot-filter-order-type")
        assert found is not None, "apac-dot-filter-order-type not found in additional row"


# ===========================================================================
# Edge cases
# ===========================================================================

class TestBuildFilterLayoutEdgeCases:
    """Edge cases: empty options, zero counts."""

    def test_empty_filter_options_still_returns_five_rows(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        result = build_filter_layout(_make_empty_filter_options())
        assert len(result) == 5

    def test_empty_months_produces_empty_dropdown_options(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_empty_filter_options())
        dropdown = _find_component_by_id(rows[1], "apac-dot-filter-month")
        assert dropdown.options == []

    def test_empty_months_default_value_is_empty_list(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_empty_filter_options())
        dropdown = _find_component_by_id(rows[1], "apac-dot-filter-month")
        assert dropdown.value == []

    def test_zero_total_count_in_prc_label(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_empty_filter_options())
        prc = _find_component_by_id(rows[2], "apac-dot-filter-prc")
        all_opt = [o for o in prc.options if o["value"] == "all"][0]
        assert "0" in all_opt["label"]


# ===========================================================================
# Helpers
# ===========================================================================

def _find_component_by_id(component, component_id: str):
    """Recursively search a Dash component tree for a component with given id.

    Returns the component if found, or None.
    """
    # Check current component
    if hasattr(component, "id") and component.id == component_id:
        return component

    # Search children
    children = getattr(component, "children", None)
    if children is None:
        return None

    if isinstance(children, (list, tuple)):
        for child in children:
            result = _find_component_by_id(child, component_id)
            if result is not None:
                return result
    else:
        return _find_component_by_id(children, component_id)

    return None
