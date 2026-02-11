"""Tests for HAMM Overview context provider.

Verifies that ``build_hamm_dashboard_context`` correctly builds a
``DashboardContext`` from a filtered DataFrame and filter-state dict.
"""
import pandas as pd
import pytest

from src.llm.page_context import DashboardContext, KPIValue


class TestBuildHammDashboardContext:
    """Core integration: DashboardContext is built correctly from inputs."""

    @pytest.fixture()
    def sample_df(self):
        """Sample DataFrame with HAMM-like columns."""
        return pd.DataFrame(
            {
                "status": ["Completed", "Completed", "Cancelled", "Completed"],
                "video_type_description": ["ERV", "Prelim", "ERV", "ERV"],
            }
        )

    @pytest.fixture()
    def empty_df(self):
        """Empty DataFrame with expected columns."""
        return pd.DataFrame({"status": [], "video_type_description": []})

    def test_returns_dashboard_context_type(self, sample_df):
        """Return type is DashboardContext."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(sample_df, filter_state=None)
        assert isinstance(ctx, DashboardContext)

    def test_kpi_total_screens_value(self, sample_df):
        """Total Screens KPI: 3 non-cancelled out of 4 rows."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(sample_df, filter_state=None)
        assert ctx.kpis[0].value == "3"
        assert ctx.kpis[0].name == "Total Screens Processed"

    def test_kpi_total_erv_value(self, sample_df):
        """Total ERV KPI: 2 ERV records among non-cancelled."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(sample_df, filter_state=None)
        assert ctx.kpis[1].value == "2"
        assert ctx.kpis[1].name == "Total ERV Processed"

    def test_kpi_total_prelim_value(self, sample_df):
        """Total Prelim KPI: 1 Prelim record among non-cancelled."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(sample_df, filter_state=None)
        assert ctx.kpis[2].value == "1"
        assert ctx.kpis[2].name == "Total Prelim Processed"

    def test_kpi_logic_descriptions_non_empty(self, sample_df):
        """Every KPI has a non-empty logic description string."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(sample_df, filter_state=None)
        for kpi in ctx.kpis:
            assert isinstance(kpi.logic, str)
            assert len(kpi.logic) > 0

    def test_kpi_count_is_three(self, sample_df):
        """Exactly 3 KPIs are returned."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(sample_df, filter_state=None)
        assert len(ctx.kpis) == 3


class TestFilterStateHandling:
    """Filter state is correctly translated to active_filters."""

    @pytest.fixture()
    def minimal_df(self):
        return pd.DataFrame(
            {
                "status": ["Completed"],
                "video_type_description": ["ERV"],
            }
        )

    def test_filter_state_none_returns_empty_dict(self, minimal_df):
        """filter_state=None produces empty active_filters."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(minimal_df, filter_state=None)
        assert ctx.active_filters == {}

    def test_filter_state_empty_dict_returns_empty_active(self, minimal_df):
        """filter_state={} produces empty active_filters (no keys match)."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(minimal_df, filter_state={})
        assert ctx.active_filters == {}

    def test_filter_with_values_mapped_to_display_name(self, minimal_df):
        """Selected filter values appear under human-readable display name."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(
            minimal_df,
            filter_state={
                "filter_region_values": ["APAC", "EMEA"],
                "filter_year_values": None,
            },
        )
        assert ctx.active_filters["Region"] == ["APAC", "EMEA"]
        assert ctx.active_filters["Year"] is None

    def test_filter_empty_list_treated_as_none(self, minimal_df):
        """An empty list selection is treated as None (all selected)."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(
            minimal_df,
            filter_state={"filter_region_values": []},
        )
        assert ctx.active_filters["Region"] is None

    def test_filter_values_converted_to_strings(self, minimal_df):
        """Numeric filter values are converted to strings."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(
            minimal_df,
            filter_state={"filter_year_values": [2024, 2025]},
        )
        assert ctx.active_filters["Year"] == ["2024", "2025"]

    def test_cadence_filter_reflected_in_active_filters(self, minimal_df):
        """Cadence single-select filter appears as str in active_filters."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(
            minimal_df,
            filter_state={
                "filter_cadence_values": "monthly",
                "filter_region_values": ["APAC"],
            },
        )
        assert ctx.active_filters["Cadence"] == "monthly"
        assert ctx.active_filters["Region"] == ["APAC"]

    def test_unknown_filter_key_ignored(self, minimal_df):
        """Keys not in _FILTER_DISPLAY_NAMES are silently ignored."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(
            minimal_df,
            filter_state={"unknown_filter_key": ["value"]},
        )
        # No "unknown_filter_key" in active_filters
        assert "unknown_filter_key" not in ctx.active_filters


class TestEmptyDataFrame:
    """Edge case: empty DataFrame."""

    @pytest.fixture()
    def empty_df(self):
        return pd.DataFrame({"status": [], "video_type_description": []})

    def test_all_kpis_zero(self, empty_df):
        """All KPI values are '0' for empty DataFrame."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(empty_df, filter_state=None)
        assert ctx.kpis[0].value == "0"
        assert ctx.kpis[1].value == "0"
        assert ctx.kpis[2].value == "0"

    def test_returns_valid_context(self, empty_df):
        """DashboardContext is still valid even with empty data."""
        from src.pages.hamm_overview._context_provider import (
            build_hamm_dashboard_context,
        )

        ctx = build_hamm_dashboard_context(empty_df, filter_state=None)
        assert isinstance(ctx, DashboardContext)
        assert len(ctx.page_description) > 0


class TestPageDescription:
    """Page description metadata."""

    def test_page_description_non_empty(self):
        """PAGE_DESCRIPTION constant is a non-empty string."""
        from src.pages.hamm_overview._context_provider import PAGE_DESCRIPTION

        assert isinstance(PAGE_DESCRIPTION, str)
        assert len(PAGE_DESCRIPTION) > 0

    def test_page_description_in_context(self):
        """page_description field in context matches the module constant."""
        from src.pages.hamm_overview._context_provider import (
            PAGE_DESCRIPTION,
            build_hamm_dashboard_context,
        )

        df = pd.DataFrame(
            {
                "status": ["Completed"],
                "video_type_description": ["ERV"],
            }
        )
        ctx = build_hamm_dashboard_context(df, filter_state=None)
        assert ctx.page_description == PAGE_DESCRIPTION
