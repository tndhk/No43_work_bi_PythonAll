"""Tests for Hamm Overview constants module."""


class TestDatasetId:
    def test_dataset_id_value(self):
        from src.pages.hamm_overview._constants import DATASET_ID

        assert DATASET_ID == "hamm-dashboard"


class TestDashboardId:
    def test_dashboard_id_value(self):
        from src.pages.hamm_overview._constants import DASHBOARD_ID

        assert DASHBOARD_ID == "hamm_overview"


class TestIdPrefix:
    def test_id_prefix_value(self):
        from src.pages.hamm_overview._constants import ID_PREFIX

        assert ID_PREFIX == "hamm-"


class TestColumnMap:
    def test_column_map_has_expected_keys(self):
        from src.pages.hamm_overview._constants import COLUMN_MAP

        expected = {
            "id",
            "title",
            "status",
            "created_at",
            "completed_at",
            "region",
            "content_type",
            "original_language",
            "dialogue",
            "genre",
            "error_code",
            "error_type",
            "video_duration",
            "audio_details",
        }
        assert set(COLUMN_MAP.keys()) == expected

    def test_column_map_values_are_strings(self):
        from src.pages.hamm_overview._constants import COLUMN_MAP

        for value in COLUMN_MAP.values():
            assert isinstance(value, str)


class TestChartIds:
    def test_chart_ids_values(self):
        from src.pages.hamm_overview import _constants as const

        assert const.CHART_ID_VOLUME_TABLE == "hamm-volume-table"
        assert const.CHART_ID_VOLUME_CHART == "hamm-volume-chart"
        assert const.CHART_ID_TASK_TABLE == "hamm-task-table"


class TestClearControlIds:
    def test_clear_control_ids_values(self):
        from src.pages.hamm_overview import _constants as const

        assert const.CTRL_ID_CLEAR_REGION == "hamm-ctrl-clear-region"
        assert const.CTRL_ID_CLEAR_YEAR == "hamm-ctrl-clear-year"
        assert const.CTRL_ID_CLEAR_CONTENT_TYPE == "hamm-ctrl-clear-content-type"
        assert const.CTRL_ID_CLEAR_ORIGINAL_LANGUAGE == "hamm-ctrl-clear-original-language"
        assert const.CTRL_ID_CLEAR_DIALOGUE == "hamm-ctrl-clear-dialogue"
        assert const.CTRL_ID_CLEAR_GENRE == "hamm-ctrl-clear-genre"
        assert const.CTRL_ID_CLEAR_ERROR_TYPE == "hamm-ctrl-clear-error-type"


class TestClearPairs:
    """CLEAR_PAIRS list should map filter IDs to clear control IDs."""

    def test_clear_pairs_exists(self):
        from src.pages.hamm_overview._constants import CLEAR_PAIRS
        assert isinstance(CLEAR_PAIRS, list)

    def test_clear_pairs_has_7_entries(self):
        from src.pages.hamm_overview._constants import CLEAR_PAIRS
        assert len(CLEAR_PAIRS) == 7

    def test_clear_pairs_are_tuples_of_strings(self):
        from src.pages.hamm_overview._constants import CLEAR_PAIRS
        for pair in CLEAR_PAIRS:
            assert isinstance(pair, tuple)
            assert len(pair) == 2
            assert isinstance(pair[0], str)
            assert isinstance(pair[1], str)

    def test_clear_pairs_filter_ids_match(self):
        from src.pages.hamm_overview._constants import (
            CLEAR_PAIRS,
            FILTER_ID_REGION,
            FILTER_ID_YEAR,
            FILTER_ID_CONTENT_TYPE,
            FILTER_ID_ORIGINAL_LANGUAGE,
            FILTER_ID_DIALOGUE,
            FILTER_ID_GENRE,
            FILTER_ID_ERROR_TYPE,
        )
        filter_ids = {pair[0] for pair in CLEAR_PAIRS}
        expected_filter_ids = {
            FILTER_ID_REGION,
            FILTER_ID_YEAR,
            FILTER_ID_CONTENT_TYPE,
            FILTER_ID_ORIGINAL_LANGUAGE,
            FILTER_ID_DIALOGUE,
            FILTER_ID_GENRE,
            FILTER_ID_ERROR_TYPE,
        }
        assert filter_ids == expected_filter_ids


class TestVolumeTableSpec:
    """VOLUME_TABLE_SPEC should be a TableSpec with compact styling."""

    def test_volume_table_spec_exists(self):
        from src.pages.hamm_overview._constants import VOLUME_TABLE_SPEC
        from src.charts.specs import TableSpec
        assert isinstance(VOLUME_TABLE_SPEC, TableSpec)

    def test_volume_table_spec_style_cell_padding(self):
        from src.pages.hamm_overview._constants import VOLUME_TABLE_SPEC
        assert VOLUME_TABLE_SPEC.style_cell["padding"] == "4px 6px"

    def test_volume_table_spec_style_cell_font_size(self):
        from src.pages.hamm_overview._constants import VOLUME_TABLE_SPEC
        assert VOLUME_TABLE_SPEC.style_cell["fontSize"] == "0.75rem"

    def test_volume_table_spec_style_header_font_size(self):
        from src.pages.hamm_overview._constants import VOLUME_TABLE_SPEC
        assert VOLUME_TABLE_SPEC.style_header["fontSize"] == "0.75rem"

    def test_volume_table_spec_sort_action(self):
        from src.pages.hamm_overview._constants import VOLUME_TABLE_SPEC
        assert VOLUME_TABLE_SPEC.sort_action == "native"

    def test_volume_table_spec_page_size(self):
        from src.pages.hamm_overview._constants import VOLUME_TABLE_SPEC
        assert VOLUME_TABLE_SPEC.page_size == 20

    def test_volume_table_spec_column_order(self):
        from src.pages.hamm_overview._constants import VOLUME_TABLE_SPEC
        expected = [
            "Fiscal Year", "Fiscal Quarter", "ISO Week",
            "Start Date", "End Date", "Prelim", "ERV", "VOLUME TOTAL",
        ]
        assert VOLUME_TABLE_SPEC.column_order == expected


class TestVolumeChartSpec:
    """VOLUME_CHART_SPEC should be a ChartSpec for stacked bar chart."""

    def test_volume_chart_spec_exists(self):
        from src.pages.hamm_overview._constants import VOLUME_CHART_SPEC
        from src.charts.specs import ChartSpec
        assert isinstance(VOLUME_CHART_SPEC, ChartSpec)

    def test_volume_chart_spec_type(self):
        from src.pages.hamm_overview._constants import VOLUME_CHART_SPEC
        assert VOLUME_CHART_SPEC.chart_type == "stacked_bar"

    def test_volume_chart_spec_x_column(self):
        from src.pages.hamm_overview._constants import VOLUME_CHART_SPEC
        assert VOLUME_CHART_SPEC.x_column == "Start Date"

    def test_volume_chart_spec_y_columns(self):
        from src.pages.hamm_overview._constants import VOLUME_CHART_SPEC
        assert VOLUME_CHART_SPEC.y_columns == ["ERV", "Prelim"]

    def test_volume_chart_spec_color_map(self):
        from src.pages.hamm_overview._constants import VOLUME_CHART_SPEC
        assert VOLUME_CHART_SPEC.color_map == {
            "ERV": "#f6b3b3",
            "Prelim": "#e57f7f",
        }

    def test_volume_chart_spec_height(self):
        from src.pages.hamm_overview._constants import VOLUME_CHART_SPEC
        assert VOLUME_CHART_SPEC.height == 400


class TestTaskTableSpec:
    """TASK_TABLE_SPEC should be a TableSpec with compact styling."""

    def test_task_table_spec_exists(self):
        from src.pages.hamm_overview._constants import TASK_TABLE_SPEC
        from src.charts.specs import TableSpec
        assert isinstance(TASK_TABLE_SPEC, TableSpec)

    def test_task_table_spec_style_cell_padding(self):
        from src.pages.hamm_overview._constants import TASK_TABLE_SPEC
        assert TASK_TABLE_SPEC.style_cell["padding"] == "4px 6px"

    def test_task_table_spec_style_cell_font_size(self):
        from src.pages.hamm_overview._constants import TASK_TABLE_SPEC
        assert TASK_TABLE_SPEC.style_cell["fontSize"] == "0.75rem"

    def test_task_table_spec_sort_action(self):
        from src.pages.hamm_overview._constants import TASK_TABLE_SPEC
        assert TASK_TABLE_SPEC.sort_action == "native"

    def test_task_table_spec_page_size(self):
        from src.pages.hamm_overview._constants import TASK_TABLE_SPEC
        assert TASK_TABLE_SPEC.page_size == 20

    def test_task_table_spec_column_order(self):
        from src.pages.hamm_overview._constants import TASK_TABLE_SPEC
        expected = [
            "Task ID", "Task Name", "Content Type", "Task Status",
            "Source File Duration", "Audio Details",
            "Job Created", "Completed / Err", "Total Duration",
        ]
        assert TASK_TABLE_SPEC.column_order == expected
