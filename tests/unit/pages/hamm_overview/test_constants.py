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
            "error_description",
            "video_duration",
            "audio_details",
            "language_count",
            "additional_languages",
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
        assert const.CHART_ID_METADATA_ORIGINAL_LANGUAGE == "hamm-metadata-original-language"
        assert const.CHART_ID_METADATA_DIALOGUE == "hamm-metadata-dialogue"
        assert const.CHART_ID_METADATA_GENRE == "hamm-metadata-genre"

    def test_dead_kpi_ids_removed(self):
        """CHART_ID_KPI_TOTAL_TASKS and CHART_ID_KPI_AVG_VIDEO_DURATION
        were dead code (never referenced in layout/callbacks) and must
        not exist in the constants module."""
        from src.pages.hamm_overview import _constants as const

        assert not hasattr(const, "CHART_ID_KPI_TOTAL_TASKS")
        assert not hasattr(const, "CHART_ID_KPI_AVG_VIDEO_DURATION")


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
            "Start Date", "End Date", "Completed", "Invalid", "VOLUME TOTAL",
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
        assert VOLUME_CHART_SPEC.y_columns == ["Completed", "Invalid"]

    def test_volume_chart_spec_color_map(self):
        from src.pages.hamm_overview._constants import VOLUME_CHART_SPEC
        assert VOLUME_CHART_SPEC.color_map == {
            "Completed": "#2d6a2e",
            "Invalid": "#9ca3af",
        }

    def test_volume_chart_spec_text_template(self):
        from src.pages.hamm_overview._constants import VOLUME_CHART_SPEC
        assert VOLUME_CHART_SPEC.text_template == "%{y}"

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


class TestContentMetadataChartSpecs:
    def test_original_language_spec(self):
        from src.pages.hamm_overview._constants import ORIGINAL_LANGUAGE_SPEC
        assert ORIGINAL_LANGUAGE_SPEC.chart_type == "pie"
        assert ORIGINAL_LANGUAGE_SPEC.x_column == "original_language"
        assert ORIGINAL_LANGUAGE_SPEC.y_columns == ["count"]
        assert ORIGINAL_LANGUAGE_SPEC.height == 460
        assert ORIGINAL_LANGUAGE_SPEC.show_legend is True

    def test_dialogue_spec(self):
        from src.pages.hamm_overview._constants import DIALOGUE_SPEC
        assert DIALOGUE_SPEC.chart_type == "stacked_bar"
        assert DIALOGUE_SPEC.x_column == "content_type"
        assert DIALOGUE_SPEC.y_columns == ["Yes", "No"]
        assert DIALOGUE_SPEC.height == 460
        assert DIALOGUE_SPEC.text_template == "%{y}"

    def test_genre_spec(self):
        from src.pages.hamm_overview._constants import GENRE_SPEC
        assert GENRE_SPEC.chart_type == "bar"
        assert GENRE_SPEC.x_column == "genre"
        assert GENRE_SPEC.y_columns == ["count"]
        assert GENRE_SPEC.height == 460
        assert GENRE_SPEC.text_template == "%{y}"
        assert GENRE_SPEC.show_legend is False


# ---------------------------------------------------------------------------
# Language Table constants (RED -- not yet implemented)
# ---------------------------------------------------------------------------

class TestColumnMapLanguageKeys:
    """COLUMN_MAP must include keys for language_count and additional_languages."""

    def test_column_map_has_language_count(self):
        from src.pages.hamm_overview._constants import COLUMN_MAP
        assert "language_count" in COLUMN_MAP

    def test_column_map_has_additional_languages(self):
        from src.pages.hamm_overview._constants import COLUMN_MAP
        assert "additional_languages" in COLUMN_MAP


class TestChartIdLanguageTable:
    """CHART_ID_LANGUAGE_TABLE must exist and follow ID_PREFIX convention."""

    def test_chart_id_language_table_exists(self):
        from src.pages.hamm_overview import _constants as const
        assert hasattr(const, "CHART_ID_LANGUAGE_TABLE")

    def test_chart_id_language_table_has_correct_prefix(self):
        from src.pages.hamm_overview import _constants as const
        assert const.CHART_ID_LANGUAGE_TABLE.startswith("hamm-")

    def test_chart_id_language_table_value(self):
        from src.pages.hamm_overview import _constants as const
        assert const.CHART_ID_LANGUAGE_TABLE == "hamm-language-table"


class TestLanguageTableSpec:
    """LANGUAGE_TABLE_SPEC must be a TableSpec with correct configuration."""

    def test_language_table_spec_exists(self):
        from src.pages.hamm_overview._constants import LANGUAGE_TABLE_SPEC
        from src.charts.specs import TableSpec
        assert isinstance(LANGUAGE_TABLE_SPEC, TableSpec)

    def test_language_table_spec_column_order(self):
        from src.pages.hamm_overview._constants import LANGUAGE_TABLE_SPEC
        expected = [
            "Task ID",
            "Task Name",
            "Content Type",
            "Status",
            "Language Count",
            "Additional Languages",
        ]
        assert LANGUAGE_TABLE_SPEC.column_order == expected

    def test_language_table_spec_style_data_conditional_has_3_rules(self):
        """Should have 3 conditional styling rules:
        1. Status=Completed -> green background
        2. Content Type=ERV -> pink background
        3. Content Type=Prelim -> pink background
        """
        from src.pages.hamm_overview._constants import LANGUAGE_TABLE_SPEC
        assert len(LANGUAGE_TABLE_SPEC.style_data_conditional) == 3

    def test_language_table_spec_completed_green_rule(self):
        """First rule: Status=Completed rows get green background."""
        from src.pages.hamm_overview._constants import LANGUAGE_TABLE_SPEC
        rules = LANGUAGE_TABLE_SPEC.style_data_conditional
        completed_rules = [
            r for r in rules
            if r.get("if", {}).get("filter_query", "") == '{Status} = "Completed"'
        ]
        assert len(completed_rules) == 1
        assert completed_rules[0]["backgroundColor"] == "#d4edda"

    def test_language_table_spec_erv_pink_rule(self):
        """Content Type=ERV rows get pink background."""
        from src.pages.hamm_overview._constants import LANGUAGE_TABLE_SPEC
        rules = LANGUAGE_TABLE_SPEC.style_data_conditional
        erv_rules = [
            r for r in rules
            if r.get("if", {}).get("filter_query", "") == '{Content Type} = "ERV"'
        ]
        assert len(erv_rules) == 1
        assert erv_rules[0]["backgroundColor"] == "#f8d7da"

    def test_language_table_spec_prelim_pink_rule(self):
        """Content Type=Prelim rows get pink background."""
        from src.pages.hamm_overview._constants import LANGUAGE_TABLE_SPEC
        rules = LANGUAGE_TABLE_SPEC.style_data_conditional
        prelim_rules = [
            r for r in rules
            if r.get("if", {}).get("filter_query", "") == '{Content Type} = "Prelim"'
        ]
        assert len(prelim_rules) == 1
        assert prelim_rules[0]["backgroundColor"] == "#f8d7da"

    def test_language_table_spec_sort_action(self):
        from src.pages.hamm_overview._constants import LANGUAGE_TABLE_SPEC
        assert LANGUAGE_TABLE_SPEC.sort_action == "native"

    def test_language_table_spec_page_size(self):
        from src.pages.hamm_overview._constants import LANGUAGE_TABLE_SPEC
        assert LANGUAGE_TABLE_SPEC.page_size == 20
