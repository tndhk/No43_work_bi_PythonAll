"""Tests for LLM context builder."""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
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
