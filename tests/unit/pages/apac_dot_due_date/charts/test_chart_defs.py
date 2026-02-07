"""Tests for chart_defs.yaml loading and validation."""

from src.pages.apac_dot_due_date.charts._chart_defs import get_chart_def, load_chart_defs


def test_load_chart_defs_contains_expected_charts():
    defs = load_chart_defs()
    assert "charts" in defs
    assert "ch00_reference_table" in defs["charts"]
    assert "ch01_change_issue_table" in defs["charts"]


def test_chart_def_has_required_keys():
    chart_def = get_chart_def("ch00_reference_table")
    assert isinstance(chart_def["title"], str)
    assert isinstance(chart_def["column_display"], dict)
    assert isinstance(chart_def["column_order"], list)
    table_style = chart_def["table_style"]
    assert isinstance(table_style["style_table"], dict)
    assert isinstance(table_style["style_cell"], dict)
    assert isinstance(table_style["style_header"], dict)
    assert isinstance(table_style["style_data_conditional"], list)
