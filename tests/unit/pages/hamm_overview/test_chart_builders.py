"""Tests for Hamm Overview chart builders module.

Tests for _chart_builders.py which extracts chart/table rendering logic
from _callbacks.py. Functions tested:
- build_volume_table: renders volume summary as DataTable
- build_volume_chart: renders volume summary as stacked bar chart
- build_task_table: renders task detail as DataTable
"""
import pandas as pd
import pytest
from dash import dash_table, html
import plotly.graph_objects as go

from src.pages.hamm_overview._constants import COLUMN_MAP


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def volume_df() -> pd.DataFrame:
    """Minimal DataFrame satisfying build_volume_table's display_columns."""
    return pd.DataFrame(
        {
            "Fiscal Year": ["FY2025", "FY2025"],
            "Fiscal Quarter": ["Q1", "Q1"],
            "ISO Week": ["W01", "W02"],
            "Start Date": ["01-Jan-25", "08-Jan-25"],
            "End Date": ["07-Jan-25", "14-Jan-25"],
            "Prelim": [10, 20],
            "ERV": [5, 8],
            "VOLUME TOTAL": [15, 28],
        }
    )


@pytest.fixture()
def empty_volume_df() -> pd.DataFrame:
    """Empty DataFrame for empty-state tests."""
    return pd.DataFrame(
        columns=[
            "Fiscal Year",
            "Fiscal Quarter",
            "ISO Week",
            "Start Date",
            "End Date",
            "Prelim",
            "ERV",
            "VOLUME TOTAL",
        ]
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


@pytest.fixture()
def task_df_multiple() -> pd.DataFrame:
    """Multi-row task DataFrame with varied IDs for sort testing."""
    base = pd.Timestamp("2025-06-01 10:00:00")
    end = pd.Timestamp("2025-06-01 12:30:00")
    return pd.DataFrame(
        {
            COLUMN_MAP["id"]: ["300", "100", "200"],
            COLUMN_MAP["title"]: ["Task C", "Task A", "Task B"],
            COLUMN_MAP["content_type"]: ["Prelim", "ERV", "Prelim"],
            COLUMN_MAP["status"]: ["Complete", "Complete", "Error"],
            COLUMN_MAP["video_duration"]: ["00:10:00", "00:20:00", "00:30:00"],
            COLUMN_MAP["audio_details"]: ["Stereo", "Mono", "Stereo"],
            COLUMN_MAP["created_at"]: [base, base, base],
            COLUMN_MAP["completed_at"]: [end, end, end],
        }
    )


@pytest.fixture()
def empty_task_df() -> pd.DataFrame:
    """Empty DataFrame for task table empty-state tests."""
    return pd.DataFrame(
        columns=[
            COLUMN_MAP["id"],
            COLUMN_MAP["title"],
            COLUMN_MAP["content_type"],
            COLUMN_MAP["status"],
            COLUMN_MAP["video_duration"],
            COLUMN_MAP["audio_details"],
            COLUMN_MAP["created_at"],
            COLUMN_MAP["completed_at"],
        ]
    )


@pytest.fixture()
def task_df_missing_completed() -> pd.DataFrame:
    """Task DataFrame with missing completed_at for edge case testing."""
    now = pd.Timestamp("2025-06-01 10:00:00")
    return pd.DataFrame(
        {
            COLUMN_MAP["id"]: ["1001"],
            COLUMN_MAP["title"]: ["Sample Task"],
            COLUMN_MAP["content_type"]: ["Prelim"],
            COLUMN_MAP["status"]: ["In Progress"],
            COLUMN_MAP["video_duration"]: ["00:45:00"],
            COLUMN_MAP["audio_details"]: ["Stereo"],
            COLUMN_MAP["created_at"]: [now],
            COLUMN_MAP["completed_at"]: [pd.NaT],
        }
    )


# ---------------------------------------------------------------------------
# build_volume_table tests
# ---------------------------------------------------------------------------

class TestBuildVolumeTable:
    """build_volume_table should render a DataTable with compact styling."""

    def test_returns_datatable(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        result = build_volume_table(volume_df)
        assert isinstance(result, dash_table.DataTable), (
            f"Expected DataTable, got {type(result).__name__}"
        )

    def test_style_cell_font_size(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        table = build_volume_table(volume_df)
        assert table.style_cell.get("fontSize") == "0.75rem"

    def test_style_cell_padding(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        table = build_volume_table(volume_df)
        assert table.style_cell.get("padding") == "4px 6px"

    def test_style_header_font_size(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        table = build_volume_table(volume_df)
        assert table.style_header.get("fontSize") == "0.75rem"

    def test_style_header_font_weight(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        table = build_volume_table(volume_df)
        assert table.style_header.get("fontWeight") == "bold"

    def test_has_native_sort(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        table = build_volume_table(volume_df)
        assert table.sort_action == "native"

    def test_page_size_is_20(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        table = build_volume_table(volume_df)
        assert table.page_size == 20

    def test_has_all_display_columns(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        table = build_volume_table(volume_df)
        column_names = [c["name"] for c in table.columns]
        expected = [
            "Fiscal Year",
            "Fiscal Quarter",
            "ISO Week",
            "Start Date",
            "End Date",
            "Prelim",
            "ERV",
            "VOLUME TOTAL",
        ]
        assert column_names == expected

    def test_data_row_count_matches(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        table = build_volume_table(volume_df)
        assert len(table.data) == 2

    def test_empty_df_returns_empty_state(self, empty_volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        result = build_volume_table(empty_volume_df)
        assert isinstance(result, html.P), (
            f"Expected html.P for empty state, got {type(result).__name__}"
        )

    def test_empty_state_has_text_muted_class(self, empty_volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        result = build_volume_table(empty_volume_df)
        assert result.className == "text-muted"


# ---------------------------------------------------------------------------
# build_volume_chart tests
# ---------------------------------------------------------------------------

class TestBuildVolumeChart:
    """build_volume_chart should render a stacked bar chart."""

    def test_returns_figure(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        result = build_volume_chart(volume_df)
        assert isinstance(result, go.Figure)

    def test_has_two_bar_traces(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        assert len(bar_traces) == 2

    def test_trace_names(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        trace_names = [t.name for t in fig.data]
        assert "ERV" in trace_names
        assert "Prelim" in trace_names

    def test_barmode_is_stack(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        assert fig.layout.barmode == "stack"

    def test_height_is_400(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        assert fig.layout.height == 400

    def test_erv_marker_color(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        erv_trace = [t for t in fig.data if t.name == "ERV"][0]
        assert erv_trace.marker.color == "#f6b3b3"

    def test_prelim_marker_color(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        prelim_trace = [t for t in fig.data if t.name == "Prelim"][0]
        assert prelim_trace.marker.color == "#e57f7f"

    def test_empty_df_returns_figure_with_annotation(self, empty_volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(empty_volume_df)
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) >= 1
        assert fig.layout.annotations[0].text == "No data available"

    def test_empty_df_has_no_traces(self, empty_volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(empty_volume_df)
        assert len(fig.data) == 0


# ---------------------------------------------------------------------------
# build_task_table tests
# ---------------------------------------------------------------------------

class TestBuildTaskTable:
    """build_task_table should render task detail as DataTable."""

    def test_returns_datatable(self, task_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        result = build_task_table(task_df)
        assert isinstance(result, dash_table.DataTable), (
            f"Expected DataTable, got {type(result).__name__}"
        )

    def test_style_cell_font_size(self, task_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        table = build_task_table(task_df)
        assert table.style_cell.get("fontSize") == "0.75rem"

    def test_style_cell_padding(self, task_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        table = build_task_table(task_df)
        assert table.style_cell.get("padding") == "4px 6px"

    def test_style_header_font_size(self, task_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        table = build_task_table(task_df)
        assert table.style_header.get("fontSize") == "0.75rem"

    def test_style_header_font_weight(self, task_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        table = build_task_table(task_df)
        assert table.style_header.get("fontWeight") == "bold"

    def test_has_all_ordered_columns(self, task_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        table = build_task_table(task_df)
        column_names = [c["name"] for c in table.columns]
        expected = [
            "Task ID",
            "Task Name",
            "Content Type",
            "Task Status",
            "Source File Duration",
            "Audio Details",
            "Job Created",
            "Completed / Err",
            "Total Duration",
        ]
        assert column_names == expected

    def test_total_duration_format(self, task_df):
        """Total Duration should be in HH:MM:SS format."""
        from src.pages.hamm_overview._chart_builders import build_task_table

        table = build_task_table(task_df)
        record = table.data[0]
        duration = record["Total Duration"]
        # 2.5 hours = 02:30:00
        assert duration == "02:30:00"

    def test_missing_completed_at_shows_empty_duration(self, task_df_missing_completed):
        """When completed_at is NaT, Total Duration should be empty string."""
        from src.pages.hamm_overview._chart_builders import build_task_table

        table = build_task_table(task_df_missing_completed)
        record = table.data[0]
        assert record["Total Duration"] == ""

    def test_sorts_by_task_id_numerically(self, task_df_multiple):
        """Rows should be sorted by Task ID as numeric values."""
        from src.pages.hamm_overview._chart_builders import build_task_table

        table = build_task_table(task_df_multiple)
        task_ids = [row["Task ID"] for row in table.data]
        assert task_ids == ["100", "200", "300"]

    def test_empty_df_returns_empty_state(self, empty_task_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        result = build_task_table(empty_task_df)
        assert isinstance(result, html.P), (
            f"Expected html.P for empty state, got {type(result).__name__}"
        )

    def test_has_native_sort(self, task_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        table = build_task_table(task_df)
        assert table.sort_action == "native"

    def test_page_size_is_20(self, task_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        table = build_task_table(task_df)
        assert table.page_size == 20
