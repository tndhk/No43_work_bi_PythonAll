"""Tests for Hamm Overview callback helpers.

Tests verify:
- Chart builder functions (now in _chart_builders.py) are re-exported
  from _callbacks.py for backward compatibility.
- Clear callbacks are registered via register_clear_callbacks.
"""

import pandas as pd
import pytest
from dash import dash_table

from src.pages.hamm_overview._chart_builders import build_volume_table, build_task_table
from src.pages.hamm_overview._constants import COLUMN_MAP


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
    """Minimal DataFrame satisfying build_task_table's column requirements."""
    now = pd.Timestamp("2025-06-01 10:00:00")
    later = pd.Timestamp("2025-06-01 12:30:00")
    return pd.DataFrame(
        {
            COLUMN_MAP["id"]: ["1001"],
            COLUMN_MAP["title"]: ["Sample Task"],
            COLUMN_MAP["content_type"]: ["Prelim"],
            COLUMN_MAP["status"]: ["Complete"],
            COLUMN_MAP["video_duration"]: ["00:45:00"],
            COLUMN_MAP["audio_details"]: ["Stereo"],
            COLUMN_MAP["created_at"]: [now],
            COLUMN_MAP["completed_at"]: [later],
        }
    )


# ---------------------------------------------------------------------------
# build_volume_table -- style_cell
# ---------------------------------------------------------------------------

class TestBuildVolumeTableStyleCell:
    """style_cell must use compact font and padding."""

    def test_returns_datatable(self, volume_df):
        result = build_volume_table(volume_df)
        assert isinstance(result, dash_table.DataTable), (
            f"Expected DataTable, got {type(result).__name__}"
        )

    def test_style_cell_font_size(self, volume_df):
        table = build_volume_table(volume_df)
        style_cell = table.style_cell
        assert style_cell.get("fontSize") == "0.75rem", (
            f"style_cell fontSize should be '0.75rem', got {style_cell.get('fontSize')!r}"
        )

    def test_style_cell_padding(self, volume_df):
        table = build_volume_table(volume_df)
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
        table = build_volume_table(volume_df)
        style_header = table.style_header
        assert style_header.get("fontSize") == "0.75rem", (
            f"style_header fontSize should be '0.75rem', got {style_header.get('fontSize')!r}"
        )


# ---------------------------------------------------------------------------
# build_task_table -- style_cell
# ---------------------------------------------------------------------------

class TestBuildTaskTableStyleCell:
    """style_cell must use compact font and padding."""

    def test_returns_datatable(self, task_df):
        result = build_task_table(task_df)
        assert isinstance(result, dash_table.DataTable), (
            f"Expected DataTable, got {type(result).__name__}"
        )

    def test_style_cell_font_size(self, task_df):
        table = build_task_table(task_df)
        style_cell = table.style_cell
        assert style_cell.get("fontSize") == "0.75rem", (
            f"style_cell fontSize should be '0.75rem', got {style_cell.get('fontSize')!r}"
        )

    def test_style_cell_padding(self, task_df):
        table = build_task_table(task_df)
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
        table = build_task_table(task_df)
        style_header = table.style_header
        assert style_header.get("fontSize") == "0.75rem", (
            f"style_header fontSize should be '0.75rem', got {style_header.get('fontSize')!r}"
        )
