"""RED-phase tests for Hamm Overview callback helpers.

These tests verify compact table styling for _build_volume_table and
_build_task_table.  They are expected to FAIL against the current
production code which uses padding="8px" and no fontSize.

Expected (target) styling:
    style_cell  -> {"fontSize": "0.75rem", "padding": "4px 6px", ...}
    style_header -> {"fontSize": "0.75rem", ...}
"""

import pandas as pd
import pytest
from dash import dash_table

from src.pages.hamm_overview._callbacks import _build_volume_table, _build_task_table
from src.pages.hamm_overview._constants import COLUMN_MAP


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def volume_df() -> pd.DataFrame:
    """Minimal DataFrame satisfying _build_volume_table's display_columns."""
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
    """Minimal DataFrame satisfying _build_task_table's column requirements."""
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
# _build_volume_table -- style_cell
# ---------------------------------------------------------------------------

class TestBuildVolumeTableStyleCell:
    """style_cell must use compact font and padding."""

    def test_returns_datatable(self, volume_df):
        result = _build_volume_table(volume_df)
        assert isinstance(result, dash_table.DataTable), (
            f"Expected DataTable, got {type(result).__name__}"
        )

    def test_style_cell_font_size(self, volume_df):
        table = _build_volume_table(volume_df)
        style_cell = table.style_cell
        assert style_cell.get("fontSize") == "0.75rem", (
            f"style_cell fontSize should be '0.75rem', got {style_cell.get('fontSize')!r}"
        )

    def test_style_cell_padding(self, volume_df):
        table = _build_volume_table(volume_df)
        style_cell = table.style_cell
        assert style_cell.get("padding") == "4px 6px", (
            f"style_cell padding should be '4px 6px', got {style_cell.get('padding')!r}"
        )


# ---------------------------------------------------------------------------
# _build_volume_table -- style_header
# ---------------------------------------------------------------------------

class TestBuildVolumeTableStyleHeader:
    """style_header must include compact font size."""

    def test_style_header_font_size(self, volume_df):
        table = _build_volume_table(volume_df)
        style_header = table.style_header
        assert style_header.get("fontSize") == "0.75rem", (
            f"style_header fontSize should be '0.75rem', got {style_header.get('fontSize')!r}"
        )


# ---------------------------------------------------------------------------
# _build_task_table -- style_cell
# ---------------------------------------------------------------------------

class TestBuildTaskTableStyleCell:
    """style_cell must use compact font and padding."""

    def test_returns_datatable(self, task_df):
        result = _build_task_table(task_df)
        assert isinstance(result, dash_table.DataTable), (
            f"Expected DataTable, got {type(result).__name__}"
        )

    def test_style_cell_font_size(self, task_df):
        table = _build_task_table(task_df)
        style_cell = table.style_cell
        assert style_cell.get("fontSize") == "0.75rem", (
            f"style_cell fontSize should be '0.75rem', got {style_cell.get('fontSize')!r}"
        )

    def test_style_cell_padding(self, task_df):
        table = _build_task_table(task_df)
        style_cell = table.style_cell
        assert style_cell.get("padding") == "4px 6px", (
            f"style_cell padding should be '4px 6px', got {style_cell.get('padding')!r}"
        )


# ---------------------------------------------------------------------------
# _build_task_table -- style_header
# ---------------------------------------------------------------------------

class TestBuildTaskTableStyleHeader:
    """style_header must include compact font size."""

    def test_style_header_font_size(self, task_df):
        table = _build_task_table(task_df)
        style_header = table.style_header
        assert style_header.get("fontSize") == "0.75rem", (
            f"style_header fontSize should be '0.75rem', got {style_header.get('fontSize')!r}"
        )


class TestPerSlicerClearCallbacks:
    """Per-slicer clear callbacks should return cleared values."""

    def test_clear_region(self):
        from src.pages.hamm_overview._callbacks import clear_region
        assert clear_region(1) == []

    def test_clear_year(self):
        from src.pages.hamm_overview._callbacks import clear_year
        assert clear_year(1) == []

    def test_clear_content_type(self):
        from src.pages.hamm_overview._callbacks import clear_content_type
        assert clear_content_type(1) == []

    def test_clear_original_language(self):
        from src.pages.hamm_overview._callbacks import clear_original_language
        assert clear_original_language(1) == []

    def test_clear_dialogue(self):
        from src.pages.hamm_overview._callbacks import clear_dialogue
        assert clear_dialogue(1) == []

    def test_clear_genre(self):
        from src.pages.hamm_overview._callbacks import clear_genre
        assert clear_genre(1) == []

    def test_clear_error_type(self):
        from src.pages.hamm_overview._callbacks import clear_error_type
        assert clear_error_type(1) == []
