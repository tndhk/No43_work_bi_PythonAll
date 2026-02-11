"""Tests for LLM context builder."""
import pytest
import pandas as pd
from src.llm.context_builder import build_llm_context


class TestBuildLlmContext:
    """Tests for build_llm_context."""

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "amount": [100.0, 200.0, 300.0],
            "region": ["APAC", "EMEA", "APAC"],
        })

    def test_contains_schema_info(self, sample_df):
        """コンテキストにスキーマ情報が含まれること"""
        context = build_llm_context(sample_df, "test-dataset")
        assert "date" in context
        assert "amount" in context
        assert "region" in context

    def test_contains_dataset_name(self, sample_df):
        """コンテキストにデータセット名が含まれること"""
        context = build_llm_context(sample_df, "sales-data")
        assert "sales-data" in context

    def test_contains_row_count(self, sample_df):
        """コンテキストに行数が含まれること"""
        context = build_llm_context(sample_df, "test")
        assert "3" in context

    def test_contains_statistics(self, sample_df):
        """コンテキストに統計情報が含まれること"""
        context = build_llm_context(sample_df, "test")
        # amountの統計情報が含まれるはず
        assert "100" in context or "300" in context

    def test_contains_sample_data(self, sample_df):
        """コンテキストにサンプルデータが含まれること"""
        context = build_llm_context(sample_df, "test")
        assert "APAC" in context

    def test_empty_dataframe(self):
        """空のDataFrameでもエラーにならないこと"""
        df = pd.DataFrame()
        context = build_llm_context(df, "empty")
        assert isinstance(context, str)
        assert "empty" in context

    def test_returns_string(self, sample_df):
        """文字列を返すこと"""
        context = build_llm_context(sample_df, "test")
        assert isinstance(context, str)
        assert len(context) > 0

    def test_large_df_sample_limited(self):
        """大きなDFでもサンプル行が制限されること"""
        df = pd.DataFrame({
            "val": range(1000),
        })
        context = build_llm_context(df, "large")
        # サンプル行は全件表示されないはず（1000行全てが文字列に含まれない）
        assert "1000" in context  # 行数は表示される

    def test_dashboard_context_none_backward_compat(self, sample_df):
        """dashboard_context=Noneで既存動作と同一"""
        ctx_without = build_llm_context(sample_df, "test")
        ctx_with_none = build_llm_context(sample_df, "test", dashboard_context=None)
        assert ctx_without == ctx_with_none

    def test_dashboard_context_with_kpis(self, sample_df):
        """dashboard_contextありでKPI値が出力に含まれる"""
        from src.llm.page_context import KPIValue, DashboardContext
        dashboard_ctx = DashboardContext(
            page_description="テストダッシュボード",
            kpis=[
                KPIValue(name="Total", value="23", logic="全レコード数"),
                KPIValue(name="ERV", value="13", logic="ERVのレコード数"),
            ],
            active_filters={"Region": None, "Year": ["2024"]},
        )
        context = build_llm_context(sample_df, "test", dashboard_context=dashboard_ctx)
        assert "ダッシュボード情報" in context
        assert "テストダッシュボード" in context
        assert "現在のKPI値" in context
        assert "Total: 23" in context
        assert "全レコード数" in context
        assert "ERV: 13" in context
        assert "アクティブフィルタ" in context
        assert "Region: 全選択" in context
        assert "Year: 2024" in context

    def test_dashboard_context_empty_kpis_no_section(self, sample_df):
        """KPIリスト空ならKPIセクション非出力"""
        from src.llm.page_context import DashboardContext
        dashboard_ctx = DashboardContext(
            page_description="desc",
            kpis=[],
            active_filters={"Region": None},
        )
        context = build_llm_context(sample_df, "test", dashboard_context=dashboard_ctx)
        assert "現在のKPI値" not in context
        assert "ダッシュボード情報" in context

    def test_dashboard_context_str_filter_value(self, sample_df):
        """str型フィルタ値が正しく出力されること"""
        from src.llm.page_context import DashboardContext
        dashboard_ctx = DashboardContext(
            page_description="desc",
            kpis=[],
            active_filters={"Cadence": "weekly", "Region": None},
        )
        context = build_llm_context(sample_df, "test", dashboard_context=dashboard_ctx)
        assert "Cadence: weekly" in context
        assert "Region: 全選択" in context

    def test_dashboard_context_empty_filters_no_section(self, sample_df):
        """active_filters空ならフィルタセクション非出力"""
        from src.llm.page_context import KPIValue, DashboardContext
        dashboard_ctx = DashboardContext(
            page_description="desc",
            kpis=[KPIValue(name="Total", value="1", logic="logic")],
            active_filters={},
        )
        context = build_llm_context(sample_df, "test", dashboard_context=dashboard_ctx)
        assert "アクティブフィルタ" not in context

    def test_dashboard_context_many_filter_values_truncated(self, sample_df):
        """20件超のフィルタ値は切り詰めて表示されること"""
        from src.llm.page_context import DashboardContext
        many_values = [f"val_{i}" for i in range(25)]
        dashboard_ctx = DashboardContext(
            page_description="desc",
            kpis=[],
            active_filters={"Region": many_values},
        )
        context = build_llm_context(sample_df, "test", dashboard_context=dashboard_ctx)
        assert "val_0" in context
        assert "val_19" in context
        assert "val_20" not in context
        assert "他5件" in context
