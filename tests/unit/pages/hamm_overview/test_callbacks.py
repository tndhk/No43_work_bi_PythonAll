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
        assert style_cell.get("padding") == "4px 6px", (
            f"style_cell padding should be '4px 6px', got {style_cell.get('padding')!r}"
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
        assert style_cell.get("padding") == "4px 6px", (
            f"style_cell padding should be '4px 6px', got {style_cell.get('padding')!r}"
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
    def test_update_dashboard_returns_13_outputs(self, monkeypatch):
        import plotly.graph_objects as go
        import src.pages.hamm_overview._callbacks as cb_mod

        volume_summary = pd.DataFrame({
            "Start Date": ["01-Jan-26"],
            "End Date": ["07-Jan-26"],
            "Completed": [2],
            "Invalid": [1],
            "VOLUME TOTAL": [3],
            "Prelim": [1],
            "ERV": [2],
            "_sort_start_dt": pd.to_datetime(["2026-01-01"]),
        })

        monkeypatch.setattr(cb_mod, "ParquetReader", lambda: object())
        monkeypatch.setattr(cb_mod, "resolve_dataset_id_for_dashboard", lambda: "hamm-dashboard")
        monkeypatch.setattr(cb_mod, "load_and_filter_data", lambda *args, **kwargs: pd.DataFrame({"id": ["1"]}))
        monkeypatch.setattr(cb_mod, "build_volume_summary", lambda *args, **kwargs: volume_summary)
        monkeypatch.setattr(cb_mod, "prepare_task_display_df", lambda df: pd.DataFrame({"Task ID": ["1"]}))
        monkeypatch.setattr(cb_mod, "build_issues_ratio", lambda df: pd.DataFrame({"error_type": ["User"], "count": [1]}))
        monkeypatch.setattr(cb_mod, "build_intervention_by_screener", lambda df: pd.DataFrame({"video_type_description": ["ERV"], "User": [1], "HAMM": [0]}))
        monkeypatch.setattr(cb_mod, "build_user_intervention_breakdown", lambda df: pd.DataFrame({"error_description": ["e"], "count": [1]}))
        monkeypatch.setattr(cb_mod, "build_hamm_intervention_breakdown", lambda df: pd.DataFrame({"error_description": ["e"], "count": [1]}))
        monkeypatch.setattr(cb_mod, "build_original_language_distribution", lambda df: pd.DataFrame({"original_language": ["Japanese"], "count": [1]}))
        monkeypatch.setattr(cb_mod, "build_dialogue_by_content_type", lambda df: pd.DataFrame({"content_type": ["ERV"], "Yes": [1], "No": [0]}))
        monkeypatch.setattr(cb_mod, "build_genre_distribution", lambda df: pd.DataFrame({"genre": ["Documentary"], "count": [1]}))

        monkeypatch.setattr(cb_mod, "build_volume_table", lambda df: ("Volume Summary", "table"))
        monkeypatch.setattr(cb_mod, "build_volume_chart", lambda df: go.Figure())
        monkeypatch.setattr(cb_mod, "build_task_table", lambda df: ("Task Details", "task_table"))
        monkeypatch.setattr(cb_mod, "build_error_ratio_chart", lambda df: go.Figure())
        monkeypatch.setattr(cb_mod, "build_error_by_screener_chart", lambda df: go.Figure())
        monkeypatch.setattr(cb_mod, "build_user_breakdown_chart", lambda df: go.Figure())
        monkeypatch.setattr(cb_mod, "build_hamm_breakdown_chart", lambda df: go.Figure())
        monkeypatch.setattr(cb_mod, "build_original_language_chart", lambda df: go.Figure())
        monkeypatch.setattr(cb_mod, "build_dialogue_chart", lambda df: go.Figure())
        monkeypatch.setattr(cb_mod, "build_genre_chart", lambda df: go.Figure())

        monkeypatch.setattr(cb_mod, "create_kpi_card", lambda *args, **kwargs: "kpi")

        result = cb_mod.update_dashboard(
            None, None, None, None, None, None, None, None, None, None, "weekly"
        )
        assert isinstance(result, tuple)
        assert len(result) == 13

    def test_update_dashboard_error_path_returns_13_outputs(self, monkeypatch):
        import src.pages.hamm_overview._callbacks as cb_mod

        monkeypatch.setattr(cb_mod, "ParquetReader", lambda: object())
        monkeypatch.setattr(cb_mod, "resolve_dataset_id_for_dashboard", lambda: "hamm-dashboard")
        monkeypatch.setattr(cb_mod, "load_and_filter_data", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("x")))

        result = cb_mod.update_dashboard(
            None, None, None, None, None, None, None, None, None, None, "weekly"
        )
        assert isinstance(result, tuple)
        assert len(result) == 13
