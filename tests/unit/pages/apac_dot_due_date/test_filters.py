"""Tests for APAC DOT Due Date filter layout module.

TDD Step 1 (RED): These tests define the expected behavior of
build_filter_layout() before implementation.
"""
import pytest
from dash import html
import dash_bootstrap_components as dbc

from tests.helpers.dash_test_utils import find_component_by_id


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

    def test_returns_two_rows(self):
        """Should produce 2 rows: top controls and bottom category filters."""
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        result = build_filter_layout(_make_filter_options())
        assert len(result) == 2


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
        found = find_component_by_id(control_row, "apac-dot-ctrl-num-percent")
        assert found is not None, "apac-dot-ctrl-num-percent RadioItems not found in control row"

    def test_num_percent_toggle_default_value(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        toggle = find_component_by_id(rows[0], "apac-dot-ctrl-num-percent")
        assert toggle.value == "num"

    def test_num_percent_toggle_has_two_options(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        toggle = find_component_by_id(rows[0], "apac-dot-ctrl-num-percent")
        assert len(toggle.options) == 2

    def test_num_percent_toggle_option_values(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        toggle = find_component_by_id(rows[0], "apac-dot-ctrl-num-percent")
        values = [opt["value"] for opt in toggle.options]
        assert "num" in values
        assert "percent" in values


# ===========================================================================
# Break Down RadioItems tests
# ===========================================================================

class TestBreakdownRadioItems:
    """First row must also contain the Break Down RadioItems."""

    def test_control_row_contains_breakdown(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = find_component_by_id(rows[0], "apac-dot-ctrl-breakdown")
        assert found is not None, "apac-dot-ctrl-breakdown not found in control row"

    def test_breakdown_default_value(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        radio = find_component_by_id(rows[0], "apac-dot-ctrl-breakdown")
        assert radio.value == "area"

    def test_breakdown_has_three_options(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        radio = find_component_by_id(rows[0], "apac-dot-ctrl-breakdown")
        assert len(radio.options) == 3

    def test_breakdown_option_values(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        radio = find_component_by_id(rows[0], "apac-dot-ctrl-breakdown")
        values = [opt["value"] for opt in radio.options]
        assert values == ["area", "category", "vendor"]


# ===========================================================================
# Month filter tests
# ===========================================================================

class TestMonthFilter:
    """Top row must contain the Filter Month slicer."""

    def test_month_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = find_component_by_id(rows[0], "apac-dot-filter-month")
        assert found is not None, "apac-dot-filter-month slicer not found"

    def test_month_filter_is_multi_select_slicer(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        slicer = find_component_by_id(rows[0], "apac-dot-filter-month")
        assert slicer.multiple is True

    def test_month_filter_default_value_empty(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        opts = _make_filter_options()
        rows = build_filter_layout(opts)
        slicer = find_component_by_id(rows[0], "apac-dot-filter-month")
        assert slicer.value == []

    def test_month_filter_options_count(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        opts = _make_filter_options()
        rows = build_filter_layout(opts)
        slicer = find_component_by_id(rows[0], "apac-dot-filter-month")
        assert len(slicer.children) == len(opts["months"])


# ===========================================================================
# PRC filter tests
# ===========================================================================

class TestPrcFilter:
    """Top row must contain the PRC single-select slicer."""

    def test_prc_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = find_component_by_id(rows[0], "apac-dot-filter-prc")
        assert found is not None, "apac-dot-filter-prc not found"

    def test_prc_filter_default_value(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        prc = find_component_by_id(rows[0], "apac-dot-filter-prc")
        assert prc.value == "prc_not_included"

    def test_prc_filter_is_single_select(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        prc = find_component_by_id(rows[0], "apac-dot-filter-prc")
        assert prc.multiple is False

    def test_prc_filter_has_two_options(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        prc = find_component_by_id(rows[0], "apac-dot-filter-prc")
        assert len(prc.children) == 2

    def test_prc_filter_option_values(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        prc = find_component_by_id(rows[0], "apac-dot-filter-prc")
        values = [chip.value for chip in prc.children]
        assert values == ["prc_only", "prc_not_included"]



# ===========================================================================
# Category filters (row 4) tests
# ===========================================================================

class TestCategoryFilters:
    """Bottom row: Area, Category, Vendor slicers."""

    def test_area_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = find_component_by_id(rows[1], "apac-dot-filter-area")
        assert found is not None, "apac-dot-filter-area not found in category row"

    def test_category_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = find_component_by_id(rows[1], "apac-dot-filter-category")
        assert found is not None, "apac-dot-filter-category not found in category row"

    def test_vendor_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = find_component_by_id(rows[1], "apac-dot-filter-vendor")
        assert found is not None, "apac-dot-filter-vendor not found in category row"


# ===========================================================================
# Additional filters (row 5) tests
# ===========================================================================

class TestAdditionalFilters:
    """Bottom row: AMP VS AV and Order Type slicers."""

    def test_amp_av_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = find_component_by_id(rows[1], "apac-dot-filter-amp-av")
        assert found is not None, "apac-dot-filter-amp-av not found in additional row"

    def test_order_type_filter_exists(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        found = find_component_by_id(rows[1], "apac-dot-filter-order-type")
        assert found is not None, "apac-dot-filter-order-type not found in additional row"


# ===========================================================================
# Per-slicer clear button tests
# ===========================================================================

class TestPerSlicerClearButtons:
    """Each slicer should expose its own clear button."""

    def test_all_clear_buttons_exist(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_filter_options())
        expected_ids = [
            "apac-dot-ctrl-clear-month",
            "apac-dot-ctrl-clear-prc",
            "apac-dot-ctrl-clear-area",
            "apac-dot-ctrl-clear-category",
            "apac-dot-ctrl-clear-vendor",
            "apac-dot-ctrl-clear-amp-av",
            "apac-dot-ctrl-clear-order-type",
        ]
        for clear_id in expected_ids:
            found = find_component_by_id(html.Div(rows), clear_id)
            assert found is not None, f"{clear_id} clear button not found"


# ===========================================================================
# Edge cases
# ===========================================================================

class TestBuildFilterLayoutEdgeCases:
    """Edge cases: empty options, zero counts."""

    def test_empty_filter_options_still_returns_two_rows(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        result = build_filter_layout(_make_empty_filter_options())
        assert len(result) == 2

    def test_empty_months_produces_empty_slicer_options(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_empty_filter_options())
        slicer = find_component_by_id(rows[0], "apac-dot-filter-month")
        assert slicer.children == []

    def test_empty_months_default_value_is_empty_list(self):
        from src.pages.apac_dot_due_date._filters import build_filter_layout

        rows = build_filter_layout(_make_empty_filter_options())
        slicer = find_component_by_id(rows[0], "apac-dot-filter-month")
        assert slicer.value == []

