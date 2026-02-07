"""Tests for applying DataTable styles from chart definitions."""

from src.pages.apac_dot_due_date.charts._chart_defs import get_chart_def
from src.pages.apac_dot_due_date.charts._table_style import build_table_style


def test_build_table_style_replaces_breakdown_column():
    chart_def = get_chart_def("ch00_reference_table")
    style = build_table_style(chart_def, "business area")
    conditional = style["style_data_conditional"][0]
    filter_query = conditional["if"]["filter_query"]
    assert "{breakdown_col}" not in filter_query
    assert "{business area}" in filter_query
