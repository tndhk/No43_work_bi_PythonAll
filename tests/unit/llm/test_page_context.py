"""Tests for LLM page context data models."""
import pytest
from src.llm.page_context import KPIValue, DashboardContext


class TestKPIValue:
    def test_creation(self):
        kpi = KPIValue(name="Total", value="23", logic="全レコード数")
        assert kpi.name == "Total"
        assert kpi.value == "23"
        assert kpi.logic == "全レコード数"

    def test_frozen(self):
        kpi = KPIValue(name="Total", value="23", logic="logic")
        with pytest.raises(AttributeError):
            kpi.name = "Changed"


class TestDashboardContext:
    def test_creation(self):
        kpi = KPIValue(name="Total", value="23", logic="logic")
        ctx = DashboardContext(
            page_description="テストページ",
            kpis=[kpi],
            active_filters={"Region": None, "Year": ["2024"]},
        )
        assert ctx.page_description == "テストページ"
        assert len(ctx.kpis) == 1
        assert ctx.active_filters["Year"] == ["2024"]

    def test_empty_kpis(self):
        ctx = DashboardContext(
            page_description="desc",
            kpis=[],
            active_filters={},
        )
        assert ctx.kpis == []

    def test_active_filters_with_str_value(self):
        ctx = DashboardContext(
            page_description="desc",
            kpis=[],
            active_filters={"Cadence": "weekly", "Region": None},
        )
        assert ctx.active_filters["Cadence"] == "weekly"
        assert ctx.active_filters["Region"] is None

    def test_frozen(self):
        ctx = DashboardContext(
            page_description="desc",
            kpis=[],
            active_filters={},
        )
        with pytest.raises(AttributeError):
            ctx.page_description = "new"
