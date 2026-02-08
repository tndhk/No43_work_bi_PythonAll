"""Tests for the shared table builder.

build_table() converts a DataFrame + TableSpec into a (title, DataTable) tuple.
It handles column reordering, display-name mapping, conditional styling,
sort/filter/pagination options, and empty-state fallback.
"""
from __future__ import annotations

import pandas as pd
import pytest
from dash import dash_table, html

from src.charts.specs import TableSpec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_spec(**overrides) -> TableSpec:
    """Create a minimal TableSpec with sensible defaults, merging overrides."""
    defaults = dict(
        title="Test Table",
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "8px"},
        style_header={"fontWeight": "bold", "backgroundColor": "#2563eb", "color": "white"},
        style_data_conditional=[],
    )
    defaults.update(overrides)
    return TableSpec(**defaults)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "region": ["APAC", "EMEA", "NA"],
        "count": [10, 20, 30],
        "status": ["Open", "Closed", "Open"],
    })


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

class TestImport:
    """build_table can be imported."""

    def test_import(self):
        from src.charts.table_builder import build_table  # noqa: F401


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

class TestReturnType:
    """build_table returns (str, DataTable)."""

    def test_returns_tuple(self):
        from src.charts.table_builder import build_table

        spec = _make_spec()
        title, component = build_table(_sample_df(), spec)
        assert isinstance(title, str)
        assert isinstance(component, dash_table.DataTable)

    def test_title_matches_spec(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(title="My Custom Title")
        title, _ = build_table(_sample_df(), spec)
        assert title == "My Custom Title"


# ---------------------------------------------------------------------------
# Column ordering
# ---------------------------------------------------------------------------

class TestColumnOrdering:
    """column_order controls column presentation order."""

    def test_reorders_columns(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(column_order=["status", "region", "count"])
        _, table = build_table(_sample_df(), spec)
        col_ids = [c["id"] for c in table.columns]
        assert col_ids == ["status", "region", "count"]

    def test_partial_order_puts_remaining_at_end(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(column_order=["count"])
        _, table = build_table(_sample_df(), spec)
        col_ids = [c["id"] for c in table.columns]
        assert col_ids[0] == "count"
        # remaining columns should follow (original order preserved)
        assert set(col_ids[1:]) == {"region", "status"}

    def test_empty_column_order_preserves_original(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(column_order=[])
        _, table = build_table(_sample_df(), spec)
        col_ids = [c["id"] for c in table.columns]
        assert col_ids == ["region", "count", "status"]


# ---------------------------------------------------------------------------
# Column display names
# ---------------------------------------------------------------------------

class TestColumnDisplay:
    """column_display maps internal names to user-facing names."""

    def test_display_name_applied(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(column_display={"region": "Region Name", "count": "Total Count"})
        _, table = build_table(_sample_df(), spec)
        name_map = {c["id"]: c["name"] for c in table.columns}
        assert name_map["region"] == "Region Name"
        assert name_map["count"] == "Total Count"

    def test_unmapped_column_uses_original_name(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(column_display={"region": "Region"})
        _, table = build_table(_sample_df(), spec)
        name_map = {c["id"]: c["name"] for c in table.columns}
        # 'status' is not in column_display, so original name is used
        assert name_map["status"] == "status"


# ---------------------------------------------------------------------------
# Conditional styles
# ---------------------------------------------------------------------------

class TestConditionalStyles:
    """style_data_conditional is forwarded to the DataTable."""

    def test_styles_forwarded(self):
        from src.charts.table_builder import build_table

        cond = [{"if": {"row_index": 0}, "fontWeight": "bold"}]
        spec = _make_spec(style_data_conditional=cond)
        _, table = build_table(_sample_df(), spec)
        assert len(table.style_data_conditional) == 1
        assert table.style_data_conditional[0]["fontWeight"] == "bold"

    def test_styles_are_deepcopied(self):
        """Mutating the original spec's conditional list must not affect the table."""
        from src.charts.table_builder import build_table

        cond = [{"if": {"row_index": 0}, "fontWeight": "bold"}]
        spec = _make_spec(style_data_conditional=cond)
        _, table = build_table(_sample_df(), spec)
        # mutate original list
        cond.append({"if": {"row_index": 1}, "fontWeight": "normal"})
        # DataTable should be unaffected
        assert len(table.style_data_conditional) == 1


# ---------------------------------------------------------------------------
# Data integrity
# ---------------------------------------------------------------------------

class TestDataIntegrity:
    """Data in the table matches the source DataFrame."""

    def test_data_matches_df(self):
        from src.charts.table_builder import build_table

        df = _sample_df()
        spec = _make_spec()
        _, table = build_table(df, spec)
        assert len(table.data) == len(df)
        assert table.data[0]["region"] == "APAC"
        assert table.data[1]["count"] == 20

    def test_data_preserves_all_rows(self):
        from src.charts.table_builder import build_table

        df = pd.DataFrame({"a": list(range(100))})
        spec = _make_spec()
        _, table = build_table(df, spec)
        assert len(table.data) == 100


# ---------------------------------------------------------------------------
# Table configuration (sort, filter, page_size)
# ---------------------------------------------------------------------------

class TestTableConfiguration:
    """sort_action, filter_action, and page_size are forwarded."""

    def test_sort_action_forwarded(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(sort_action="native")
        _, table = build_table(_sample_df(), spec)
        assert table.sort_action == "native"

    def test_filter_action_forwarded(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(filter_action="native")
        _, table = build_table(_sample_df(), spec)
        assert table.filter_action == "native"

    def test_page_size_forwarded(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(page_size=25)
        _, table = build_table(_sample_df(), spec)
        assert table.page_size == 25

    def test_default_page_size_zero(self):
        from src.charts.table_builder import build_table

        spec = _make_spec()
        _, table = build_table(_sample_df(), spec)
        assert table.page_size == 0


# ---------------------------------------------------------------------------
# Styling forwarded
# ---------------------------------------------------------------------------

class TestStylingForwarded:
    """style_table, style_cell, style_header are forwarded to DataTable."""

    def test_style_table(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(style_table={"overflowX": "auto", "maxHeight": "500px"})
        _, table = build_table(_sample_df(), spec)
        assert table.style_table["overflowX"] == "auto"
        assert table.style_table["maxHeight"] == "500px"

    def test_style_cell(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(style_cell={"fontSize": "12px"})
        _, table = build_table(_sample_df(), spec)
        assert table.style_cell["fontSize"] == "12px"

    def test_style_header(self):
        from src.charts.table_builder import build_table

        spec = _make_spec(style_header={"color": "white"})
        _, table = build_table(_sample_df(), spec)
        assert table.style_header["color"] == "white"


# ---------------------------------------------------------------------------
# Empty DataFrame
# ---------------------------------------------------------------------------

class TestEmptyDataFrame:
    """build_table handles an empty DataFrame by returning an empty-state component."""

    def test_empty_df_returns_empty_state(self):
        from src.charts.table_builder import build_table

        df = pd.DataFrame(columns=["a", "b"])
        spec = _make_spec()
        title, component = build_table(df, spec)
        assert isinstance(title, str)
        # For empty DF, should return html.P (empty state) instead of DataTable
        assert isinstance(component, html.P)

    def test_empty_df_title_preserved(self):
        from src.charts.table_builder import build_table

        df = pd.DataFrame(columns=["a", "b"])
        spec = _make_spec(title="Empty Table")
        title, _ = build_table(df, spec)
        assert title == "Empty Table"
