"""Tests for Hamm Overview callback helpers.

Tests verify:
- Chart builder functions (now in _chart_builders.py) return (title, component)
  tuples for tables and go.Figure for charts.
- Clear callbacks are registered via register_clear_callbacks.
"""

import pandas as pd
import pytest
from dash import dash_table

from src.pages.hamm_overview._chart_builders import build_volume_table, build_task_table


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def volume_df() -> pd.DataFrame:
    """Minimal DataFrame satisfying build_volume_table's display_columns."""
    return pd.DataFrame(
        {
            "Fiscal Year": ["FY2025"],
            "Fiscal Quarter": ["Q1"],
            "ISO Week": ["W01"],
            "Start Date": ["01-Jan-25"],
            "End Date": ["07-Jan-25"],
            "Prelim": [10],
            "ERV": [5],
            "VOLUME TOTAL": [15],
        }
    )


@pytest.fixture()
def task_df() -> pd.DataFrame:
    """Pre-transformed display DataFrame for build_task_table."""
    return pd.DataFrame(
        {
            "Task ID": ["1001"],
            "Task Name": ["Sample Task"],
            "Content Type": ["Prelim"],
            "Task Status": ["Complete"],
            "Source File Duration": ["00:45:00"],
            "Audio Details": ["Stereo"],
            "Job Created": ["2025-06-01 10:00"],
            "Completed / Err": ["2025-06-01 12:30"],
            "Total Duration": ["02:30:00"],
        }
    )


# ---------------------------------------------------------------------------
# build_volume_table -- style_cell
# ---------------------------------------------------------------------------

class TestBuildVolumeTableStyleCell:
    """style_cell must use compact font and padding."""

    def test_returns_tuple_with_datatable(self, volume_df):
        result = build_volume_table(volume_df)
        assert isinstance(result, tuple), (
            f"Expected tuple, got {type(result).__name__}"
        )
        _, component = result
        assert isinstance(component, dash_table.DataTable), (
            f"Expected DataTable, got {type(component).__name__}"
        )

    def test_style_cell_font_size(self, volume_df):
        _, table = build_volume_table(volume_df)
        style_cell = table.style_cell
        assert style_cell.get("fontSize") == "0.75rem", (
            f"style_cell fontSize should be '0.75rem', got {style_cell.get('fontSize')!r}"
        )

    def test_style_cell_padding(self, volume_df):
        _, table = build_volume_table(volume_df)
        style_cell = table.style_cell
        assert style_cell.get("padding") == "2px 4px", (
            f"style_cell padding should be '2px 4px', got {style_cell.get('padding')!r}"
        )


# ---------------------------------------------------------------------------
# build_volume_table -- style_header
# ---------------------------------------------------------------------------

class TestBuildVolumeTableStyleHeader:
    """style_header must include compact font size."""

    def test_style_header_font_size(self, volume_df):
        _, table = build_volume_table(volume_df)
        style_header = table.style_header
        assert style_header.get("fontSize") == "0.75rem", (
            f"style_header fontSize should be '0.75rem', got {style_header.get('fontSize')!r}"
        )


# ---------------------------------------------------------------------------
# build_task_table -- style_cell
# ---------------------------------------------------------------------------

class TestBuildTaskTableStyleCell:
    """style_cell must use compact font and padding."""

    def test_returns_tuple_with_datatable(self, task_df):
        result = build_task_table(task_df)
        assert isinstance(result, tuple), (
            f"Expected tuple, got {type(result).__name__}"
        )
        _, component = result
        assert isinstance(component, dash_table.DataTable), (
            f"Expected DataTable, got {type(component).__name__}"
        )

    def test_style_cell_font_size(self, task_df):
        _, table = build_task_table(task_df)
        style_cell = table.style_cell
        assert style_cell.get("fontSize") == "0.75rem", (
            f"style_cell fontSize should be '0.75rem', got {style_cell.get('fontSize')!r}"
        )

    def test_style_cell_padding(self, task_df):
        _, table = build_task_table(task_df)
        style_cell = table.style_cell
        assert style_cell.get("padding") == "2px 4px", (
            f"style_cell padding should be '2px 4px', got {style_cell.get('padding')!r}"
        )


# ---------------------------------------------------------------------------
# build_task_table -- style_header
# ---------------------------------------------------------------------------

class TestBuildTaskTableStyleHeader:
    """style_header must include compact font size."""

    def test_style_header_font_size(self, task_df):
        _, table = build_task_table(task_df)
        style_header = table.style_header
        assert style_header.get("fontSize") == "0.75rem", (
            f"style_header fontSize should be '0.75rem', got {style_header.get('fontSize')!r}"
        )


class TestUpdateDashboardCallback:
    """Tests for update_dashboard: happy path, error path, and Output registration."""

    def test_update_dashboard_returns_14_outputs(self, mock_dashboard_deps):
        cb_mod = mock_dashboard_deps
        result = cb_mod.update_dashboard(
            None, None, None, None, None, None, None, None, None, None, "weekly"
        )
        assert isinstance(result, tuple)
        assert len(result) == 14

    def test_update_dashboard_error_path_returns_14_outputs(self, monkeypatch):
        import src.pages.hamm_overview._callbacks as cb_mod

        monkeypatch.setattr(cb_mod, "ParquetReader", lambda: object())
        monkeypatch.setattr(cb_mod, "resolve_dataset_id_for_dashboard", lambda: "hamm-dashboard")
        monkeypatch.setattr(cb_mod, "load_and_filter_data", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("x")))

        result = cb_mod.update_dashboard(
            None, None, None, None, None, None, None, None, None, None, "weekly"
        )
        assert isinstance(result, tuple)
        assert len(result) == 14

    def test_output_includes_language_table_id(self):
        """The callback Outputs should contain CHART_ID_LANGUAGE_TABLE."""
        from src.pages.hamm_overview._constants import CHART_ID_LANGUAGE_TABLE
        import src.pages.hamm_overview._callbacks as cb_mod

        import inspect
        source = inspect.getsource(cb_mod)
        assert f'Output({repr(CHART_ID_LANGUAGE_TABLE)}' in source or \
               f"Output(CHART_ID_LANGUAGE_TABLE" in source, \
            f"CHART_ID_LANGUAGE_TABLE not found in callback Outputs"
