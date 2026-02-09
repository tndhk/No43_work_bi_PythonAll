"""Tests for Hamm Overview chart builders module.

Tests for _chart_builders.py which delegates to shared builders:
- build_volume_table: delegates to build_table(df, VOLUME_TABLE_SPEC)
- build_volume_chart: delegates to build_chart(df, VOLUME_CHART_SPEC) + custom layout
- build_task_table: delegates to build_table(df, TASK_TABLE_SPEC)

After migration to shared builders:
- build_volume_table returns (title, component) tuple
- build_volume_chart returns go.Figure (with theme applied)
- build_task_table returns (title, component) tuple
"""
import pandas as pd
import pytest
from dash import dash_table, html
import plotly.graph_objects as go


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
            "Completed": [10, 20],
            "Invalid": [5, 8],
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
            "Completed",
            "Invalid",
            "VOLUME TOTAL",
        ]
    )


@pytest.fixture()
def task_display_df() -> pd.DataFrame:
    """Pre-transformed display DataFrame for build_task_table (single row).

    This simulates the output of prepare_task_display_df(), which is now
    responsible for all data transformations. build_task_table only renders.
    """
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


@pytest.fixture()
def task_display_df_multiple() -> pd.DataFrame:
    """Multi-row pre-transformed display DataFrame (already sorted by Task ID)."""
    return pd.DataFrame(
        {
            "Task ID": ["100", "200", "300"],
            "Task Name": ["Task A", "Task B", "Task C"],
            "Content Type": ["ERV", "Prelim", "Prelim"],
            "Task Status": ["Complete", "Error", "Complete"],
            "Source File Duration": ["00:20:00", "00:30:00", "00:10:00"],
            "Audio Details": ["Mono", "Stereo", "Stereo"],
            "Job Created": ["2025-06-01 10:00"] * 3,
            "Completed / Err": ["2025-06-01 12:30"] * 3,
            "Total Duration": ["02:30:00"] * 3,
        }
    )


@pytest.fixture()
def empty_task_display_df() -> pd.DataFrame:
    """Empty pre-transformed display DataFrame for empty-state tests."""
    return pd.DataFrame(
        columns=[
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
    )


# ---------------------------------------------------------------------------
# build_volume_table tests
# ---------------------------------------------------------------------------

class TestBuildVolumeTable:
    """build_volume_table delegates to shared build_table and returns (title, component)."""

    def test_returns_tuple(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        result = build_volume_table(volume_df)
        assert isinstance(result, tuple), (
            f"Expected tuple, got {type(result).__name__}"
        )
        assert len(result) == 2

    def test_tuple_title_is_volume_summary(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        title, _ = build_volume_table(volume_df)
        assert title == "Volume Summary"

    def test_tuple_component_is_datatable(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, component = build_volume_table(volume_df)
        assert isinstance(component, dash_table.DataTable), (
            f"Expected DataTable, got {type(component).__name__}"
        )

    def test_style_cell_font_size(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, table = build_volume_table(volume_df)
        assert table.style_cell.get("fontSize") == "0.75rem"

    def test_style_cell_padding(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, table = build_volume_table(volume_df)
        assert table.style_cell.get("padding") == "4px 6px"

    def test_style_header_font_size(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, table = build_volume_table(volume_df)
        assert table.style_header.get("fontSize") == "0.75rem"

    def test_style_header_font_weight(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, table = build_volume_table(volume_df)
        assert table.style_header.get("fontWeight") == "bold"

    def test_has_native_sort(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, table = build_volume_table(volume_df)
        assert table.sort_action == "native"

    def test_page_size_is_20(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, table = build_volume_table(volume_df)
        assert table.page_size == 20

    def test_has_all_display_columns(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, table = build_volume_table(volume_df)
        column_names = [c["name"] for c in table.columns]
        expected = [
            "Fiscal Year",
            "Fiscal Quarter",
            "ISO Week",
            "Start Date",
            "End Date",
            "Completed",
            "Invalid",
            "VOLUME TOTAL",
        ]
        assert column_names == expected

    def test_data_row_count_matches(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, table = build_volume_table(volume_df)
        assert len(table.data) == 2

    def test_empty_df_returns_tuple(self, empty_volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        result = build_volume_table(empty_volume_df)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_df_title_is_volume_summary(self, empty_volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        title, _ = build_volume_table(empty_volume_df)
        assert title == "Volume Summary"

    def test_empty_df_component_is_html_p(self, empty_volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, component = build_volume_table(empty_volume_df)
        assert isinstance(component, html.P), (
            f"Expected html.P for empty state, got {type(component).__name__}"
        )

    def test_empty_state_has_text_muted_class(self, empty_volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_table

        _, component = build_volume_table(empty_volume_df)
        assert component.className == "text-muted"

    def test_delegates_to_shared_build_table(self, volume_df):
        """Verify build_volume_table delegates to the shared build_table."""
        from unittest.mock import patch
        from src.pages.hamm_overview._chart_builders import build_volume_table
        from src.pages.hamm_overview._constants import VOLUME_TABLE_SPEC

        with patch("src.pages.hamm_overview._chart_builders.build_table") as mock_bt:
            mock_bt.return_value = ("Volume Summary", "mock_component")
            result = build_volume_table(volume_df)
            mock_bt.assert_called_once()
            # Verify spec argument
            call_args = mock_bt.call_args
            assert call_args[0][1] is VOLUME_TABLE_SPEC


# ---------------------------------------------------------------------------
# build_volume_chart tests
# ---------------------------------------------------------------------------

class TestBuildVolumeChart:
    """build_volume_chart delegates to shared build_chart + custom layout."""

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
        assert "Completed" in trace_names
        assert "Invalid" in trace_names

    def test_barmode_is_stack(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        assert fig.layout.barmode == "stack"

    def test_height_is_400(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        assert fig.layout.height == 400

    def test_completed_marker_color(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        completed_trace = [t for t in fig.data if t.name == "Completed"][0]
        assert completed_trace.marker.color == "#2d6a2e"

    def test_invalid_marker_color(self, volume_df):
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        invalid_trace = [t for t in fig.data if t.name == "Invalid"][0]
        assert invalid_trace.marker.color == "#9ca3af"

    def test_custom_margin(self, volume_df):
        """Custom margin should be applied after build_chart."""
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        assert fig.layout.margin.l == 30
        assert fig.layout.margin.r == 10
        assert fig.layout.margin.t == 20
        assert fig.layout.margin.b == 60

    def test_custom_legend_orientation(self, volume_df):
        """Custom legend orientation should be applied after build_chart."""
        from src.pages.hamm_overview._chart_builders import build_volume_chart

        fig = build_volume_chart(volume_df)
        assert fig.layout.legend.orientation == "h"
        assert fig.layout.legend.y == -0.2

    def test_theme_is_applied(self, volume_df):
        """Theme template should be applied by shared build_chart."""
        from src.pages.hamm_overview._chart_builders import build_volume_chart
        from src.charts.plotly_theme import PLOTLY_TEMPLATE

        fig = build_volume_chart(volume_df)
        assert fig.layout.template == PLOTLY_TEMPLATE

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

    def test_delegates_to_shared_build_chart(self, volume_df):
        """Verify build_volume_chart delegates to the shared build_chart."""
        from unittest.mock import patch
        from src.pages.hamm_overview._chart_builders import build_volume_chart
        from src.pages.hamm_overview._constants import VOLUME_CHART_SPEC

        mock_fig = go.Figure()
        with patch("src.pages.hamm_overview._chart_builders.build_chart") as mock_bc:
            mock_bc.return_value = mock_fig
            build_volume_chart(volume_df)
            mock_bc.assert_called_once()
            call_args = mock_bc.call_args
            assert call_args[0][1] is VOLUME_CHART_SPEC


# ---------------------------------------------------------------------------
# build_task_table tests
# ---------------------------------------------------------------------------

class TestBuildTaskTable:
    """build_task_table delegates to shared build_table and returns (title, component).

    Data transformations (datetime formatting, duration calculation, column
    renaming, sorting) are now handled by prepare_task_display_df() in
    _data_loader.py. build_task_table only receives display-ready data and
    renders it as a DataTable.
    """

    def test_returns_tuple(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        result = build_task_table(task_display_df)
        assert isinstance(result, tuple), (
            f"Expected tuple, got {type(result).__name__}"
        )
        assert len(result) == 2

    def test_tuple_title_is_task_details(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        title, _ = build_task_table(task_display_df)
        assert title == "Task Details"

    def test_tuple_component_is_datatable(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, component = build_task_table(task_display_df)
        assert isinstance(component, dash_table.DataTable), (
            f"Expected DataTable, got {type(component).__name__}"
        )

    def test_style_cell_font_size(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, table = build_task_table(task_display_df)
        assert table.style_cell.get("fontSize") == "0.75rem"

    def test_style_cell_padding(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, table = build_task_table(task_display_df)
        assert table.style_cell.get("padding") == "4px 6px"

    def test_style_header_font_size(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, table = build_task_table(task_display_df)
        assert table.style_header.get("fontSize") == "0.75rem"

    def test_style_header_font_weight(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, table = build_task_table(task_display_df)
        assert table.style_header.get("fontWeight") == "bold"

    def test_has_all_ordered_columns(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, table = build_task_table(task_display_df)
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

    def test_data_row_count_matches(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, table = build_task_table(task_display_df)
        assert len(table.data) == 1

    def test_data_preserves_values(self, task_display_df):
        """build_task_table should pass through display values unchanged."""
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, table = build_task_table(task_display_df)
        record = table.data[0]
        assert record["Task ID"] == "1001"
        assert record["Total Duration"] == "02:30:00"
        assert record["Job Created"] == "2025-06-01 10:00"

    def test_multiple_rows_preserved(self, task_display_df_multiple):
        """Multiple rows should all be present in the rendered table."""
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, table = build_task_table(task_display_df_multiple)
        assert len(table.data) == 3
        task_ids = [row["Task ID"] for row in table.data]
        assert task_ids == ["100", "200", "300"]

    def test_empty_df_returns_tuple(self, empty_task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        result = build_task_table(empty_task_display_df)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_df_title_is_task_details(self, empty_task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        title, _ = build_task_table(empty_task_display_df)
        assert title == "Task Details"

    def test_empty_df_component_is_html_p(self, empty_task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, component = build_task_table(empty_task_display_df)
        assert isinstance(component, html.P), (
            f"Expected html.P for empty state, got {type(component).__name__}"
        )

    def test_has_native_sort(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, table = build_task_table(task_display_df)
        assert table.sort_action == "native"

    def test_page_size_is_20(self, task_display_df):
        from src.pages.hamm_overview._chart_builders import build_task_table

        _, table = build_task_table(task_display_df)
        assert table.page_size == 20

    def test_delegates_to_shared_build_table(self, task_display_df):
        """Verify build_task_table delegates to the shared build_table."""
        from unittest.mock import patch
        from src.pages.hamm_overview._chart_builders import build_task_table
        from src.pages.hamm_overview._constants import TASK_TABLE_SPEC

        with patch("src.pages.hamm_overview._chart_builders.build_table") as mock_bt:
            mock_bt.return_value = ("Task Details", "mock_component")
            result = build_task_table(task_display_df)
            mock_bt.assert_called_once()
            call_args = mock_bt.call_args
            assert call_args[0][1] is TASK_TABLE_SPEC


class TestContentMetadataChartBuilders:
    def test_build_original_language_chart(self):
        from src.pages.hamm_overview._chart_builders import build_original_language_chart

        df = pd.DataFrame({
            "original_language": ["Japanese", "Korean"],
            "count": [12, 9],
        })
        fig = build_original_language_chart(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Pie)
        assert set(fig.data[0].labels) == {"Japanese", "Korean"}

    def test_build_dialogue_chart(self):
        from src.pages.hamm_overview._chart_builders import build_dialogue_chart

        df = pd.DataFrame({
            "content_type": ["ERV", "Prelim"],
            "Yes": [9, 5],
            "No": [4, 3],
        })
        fig = build_dialogue_chart(df)

        assert isinstance(fig, go.Figure)
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        assert len(bar_traces) == 2
        assert set([t.name for t in bar_traces]) == {"Yes", "No"}
        assert fig.layout.barmode == "stack"

    def test_build_genre_chart(self):
        from src.pages.hamm_overview._chart_builders import build_genre_chart

        df = pd.DataFrame({
            "genre": ["Documentary", "Crime/Mystery/Thriller", "Drama"],
            "count": [12, 5, 4],
        })
        fig = build_genre_chart(df)

        assert isinstance(fig, go.Figure)
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        assert len(bar_traces) == 1
        assert bar_traces[0].name == "count"
