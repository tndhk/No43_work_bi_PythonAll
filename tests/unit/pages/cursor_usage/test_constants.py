"""Tests for Cursor Usage constants module.

TDD Step 1 (RED): These tests define the expected constants that should
exist in src/pages/cursor_usage/_constants.py.
The module does not exist yet, so all tests MUST fail with ImportError.
"""
import pytest


class TestDatasetId:
    """DATASET_ID must be the correct S3/Parquet dataset identifier."""

    def test_dataset_id_exists(self):
        from src.pages.cursor_usage._constants import DATASET_ID

        assert DATASET_ID is not None

    def test_dataset_id_value(self):
        from src.pages.cursor_usage._constants import DATASET_ID

        assert DATASET_ID == "cursor-usage"

    def test_dataset_id_is_string(self):
        from src.pages.cursor_usage._constants import DATASET_ID

        assert isinstance(DATASET_ID, str)


class TestDashboardId:
    """DASHBOARD_ID must be set for config lookup."""

    def test_dashboard_id_exists(self):
        from src.pages.cursor_usage._constants import DASHBOARD_ID

        assert DASHBOARD_ID is not None

    def test_dashboard_id_value(self):
        from src.pages.cursor_usage._constants import DASHBOARD_ID

        assert DASHBOARD_ID == "cursor_usage"

    def test_dashboard_id_is_string(self):
        from src.pages.cursor_usage._constants import DASHBOARD_ID

        assert isinstance(DASHBOARD_ID, str)


class TestIdPrefix:
    """ID_PREFIX must be set for component ID namespacing to avoid collisions."""

    def test_id_prefix_exists(self):
        from src.pages.cursor_usage._constants import ID_PREFIX

        assert ID_PREFIX is not None

    def test_id_prefix_value(self):
        from src.pages.cursor_usage._constants import ID_PREFIX

        assert ID_PREFIX == "cu-"

    def test_id_prefix_is_string(self):
        from src.pages.cursor_usage._constants import ID_PREFIX

        assert isinstance(ID_PREFIX, str)

    def test_id_prefix_ends_with_separator(self):
        """ID_PREFIX should end with a separator character for easy concatenation."""
        from src.pages.cursor_usage._constants import ID_PREFIX

        assert ID_PREFIX.endswith("-")


class TestColumnMap:
    """COLUMN_MAP maps logical filter keys to DataFrame column names."""

    def test_column_map_exists(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP is not None

    def test_column_map_is_dict(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert isinstance(COLUMN_MAP, dict)

    def test_column_map_has_all_expected_keys(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        expected_keys = {"date", "model", "cost", "total_tokens", "user", "kind"}
        assert set(COLUMN_MAP.keys()) == expected_keys

    def test_column_map_date(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["date"] == "Date"

    def test_column_map_model(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["model"] == "Model"

    def test_column_map_cost(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["cost"] == "Cost"

    def test_column_map_total_tokens(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["total_tokens"] == "Total Tokens"

    def test_column_map_user(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["user"] == "User"

    def test_column_map_kind(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        assert COLUMN_MAP["kind"] == "Kind"

    def test_column_map_values_are_all_strings(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        for key, value in COLUMN_MAP.items():
            assert isinstance(value, str), f"COLUMN_MAP['{key}'] is not a string: {value}"

    def test_column_map_keys_are_all_strings(self):
        from src.pages.cursor_usage._constants import COLUMN_MAP

        for key in COLUMN_MAP.keys():
            assert isinstance(key, str), f"COLUMN_MAP key is not a string: {key}"


class TestChartIds:
    """Chart ID constants must be defined for config mapping."""

    def test_chart_ids_exist(self):
        from src.pages.cursor_usage import _constants as const

        assert const.CHART_ID_KPI_TOTAL_COST is not None
        assert const.CHART_ID_KPI_TOTAL_TOKENS is not None
        assert const.CHART_ID_KPI_REQUEST_COUNT is not None
        assert const.CHART_ID_COST_TREND is not None
        assert const.CHART_ID_TOKEN_EFFICIENCY is not None
        assert const.CHART_ID_MODEL_DISTRIBUTION is not None
        assert const.CHART_ID_DATA_TABLE is not None

    def test_chart_ids_values(self):
        from src.pages.cursor_usage import _constants as const

        assert const.CHART_ID_KPI_TOTAL_COST == "cu-kpi-total-cost"
        assert const.CHART_ID_KPI_TOTAL_TOKENS == "cu-kpi-total-tokens"
        assert const.CHART_ID_KPI_REQUEST_COUNT == "cu-kpi-request-count"
        assert const.CHART_ID_COST_TREND == "cu-chart-cost-trend"
        assert const.CHART_ID_TOKEN_EFFICIENCY == "cu-chart-token-efficiency"
        assert const.CHART_ID_MODEL_DISTRIBUTION == "cu-chart-model-distribution"
        assert const.CHART_ID_DATA_TABLE == "cu-data-table"


# ===========================================================================
# ChartSpec declarations (Step 5b)
# ===========================================================================

class TestCostTrendChartSpec:
    """COST_TREND_SPEC must define a line chart for daily cost trend."""

    def test_cost_trend_spec_exists(self):
        from src.pages.cursor_usage._constants import COST_TREND_SPEC

        assert COST_TREND_SPEC is not None

    def test_cost_trend_spec_is_chart_spec(self):
        from src.pages.cursor_usage._constants import COST_TREND_SPEC
        from src.charts.specs import ChartSpec

        assert isinstance(COST_TREND_SPEC, ChartSpec)

    def test_cost_trend_spec_chart_type_is_line(self):
        from src.pages.cursor_usage._constants import COST_TREND_SPEC

        assert COST_TREND_SPEC.chart_type == "line"

    def test_cost_trend_spec_title(self):
        from src.pages.cursor_usage._constants import COST_TREND_SPEC

        assert COST_TREND_SPEC.title == "Daily Cost Trend"

    def test_cost_trend_spec_x_column(self):
        from src.pages.cursor_usage._constants import COST_TREND_SPEC, COLUMN_MAP

        assert COST_TREND_SPEC.x_column == COLUMN_MAP["date"]

    def test_cost_trend_spec_y_columns(self):
        from src.pages.cursor_usage._constants import COST_TREND_SPEC, COLUMN_MAP

        assert COST_TREND_SPEC.y_columns == [COLUMN_MAP["cost"]]

    def test_cost_trend_spec_show_legend_false(self):
        from src.pages.cursor_usage._constants import COST_TREND_SPEC

        assert COST_TREND_SPEC.show_legend is False


class TestTokenEfficiencyChartSpec:
    """TOKEN_EFFICIENCY_SPEC must define a bar chart for token efficiency."""

    def test_token_efficiency_spec_exists(self):
        from src.pages.cursor_usage._constants import TOKEN_EFFICIENCY_SPEC

        assert TOKEN_EFFICIENCY_SPEC is not None

    def test_token_efficiency_spec_is_chart_spec(self):
        from src.pages.cursor_usage._constants import TOKEN_EFFICIENCY_SPEC
        from src.charts.specs import ChartSpec

        assert isinstance(TOKEN_EFFICIENCY_SPEC, ChartSpec)

    def test_token_efficiency_spec_chart_type_is_bar(self):
        from src.pages.cursor_usage._constants import TOKEN_EFFICIENCY_SPEC

        assert TOKEN_EFFICIENCY_SPEC.chart_type == "bar"

    def test_token_efficiency_spec_title(self):
        from src.pages.cursor_usage._constants import TOKEN_EFFICIENCY_SPEC

        assert TOKEN_EFFICIENCY_SPEC.title == "Token Efficiency by Model (Tokens per $)"

    def test_token_efficiency_spec_x_column(self):
        from src.pages.cursor_usage._constants import TOKEN_EFFICIENCY_SPEC, COLUMN_MAP

        assert TOKEN_EFFICIENCY_SPEC.x_column == COLUMN_MAP["model"]

    def test_token_efficiency_spec_y_columns(self):
        from src.pages.cursor_usage._constants import TOKEN_EFFICIENCY_SPEC

        assert TOKEN_EFFICIENCY_SPEC.y_columns == ["TokensPerCost"]

    def test_token_efficiency_spec_show_legend_false(self):
        from src.pages.cursor_usage._constants import TOKEN_EFFICIENCY_SPEC

        assert TOKEN_EFFICIENCY_SPEC.show_legend is False


class TestModelDistributionChartSpec:
    """MODEL_DISTRIBUTION_SPEC must define a pie chart for cost distribution."""

    def test_model_distribution_spec_exists(self):
        from src.pages.cursor_usage._constants import MODEL_DISTRIBUTION_SPEC

        assert MODEL_DISTRIBUTION_SPEC is not None

    def test_model_distribution_spec_is_chart_spec(self):
        from src.pages.cursor_usage._constants import MODEL_DISTRIBUTION_SPEC
        from src.charts.specs import ChartSpec

        assert isinstance(MODEL_DISTRIBUTION_SPEC, ChartSpec)

    def test_model_distribution_spec_chart_type_is_pie(self):
        from src.pages.cursor_usage._constants import MODEL_DISTRIBUTION_SPEC

        assert MODEL_DISTRIBUTION_SPEC.chart_type == "pie"

    def test_model_distribution_spec_title(self):
        from src.pages.cursor_usage._constants import MODEL_DISTRIBUTION_SPEC

        assert MODEL_DISTRIBUTION_SPEC.title == "Cost Distribution by Model"

    def test_model_distribution_spec_x_column(self):
        from src.pages.cursor_usage._constants import MODEL_DISTRIBUTION_SPEC, COLUMN_MAP

        assert MODEL_DISTRIBUTION_SPEC.x_column == COLUMN_MAP["model"]

    def test_model_distribution_spec_y_columns(self):
        from src.pages.cursor_usage._constants import MODEL_DISTRIBUTION_SPEC, COLUMN_MAP

        assert MODEL_DISTRIBUTION_SPEC.y_columns == [COLUMN_MAP["cost"]]


# ===========================================================================
# TableSpec declaration (Step 5b)
# ===========================================================================

class TestDetailTableSpec:
    """DETAIL_TABLE_SPEC must define the data table for cursor usage details."""

    def test_detail_table_spec_exists(self):
        from src.pages.cursor_usage._constants import DETAIL_TABLE_SPEC

        assert DETAIL_TABLE_SPEC is not None

    def test_detail_table_spec_is_table_spec(self):
        from src.pages.cursor_usage._constants import DETAIL_TABLE_SPEC
        from src.charts.specs import TableSpec

        assert isinstance(DETAIL_TABLE_SPEC, TableSpec)

    def test_detail_table_spec_title(self):
        from src.pages.cursor_usage._constants import DETAIL_TABLE_SPEC

        assert DETAIL_TABLE_SPEC.title == "Detailed Data"

    def test_detail_table_spec_page_size(self):
        from src.pages.cursor_usage._constants import DETAIL_TABLE_SPEC

        assert DETAIL_TABLE_SPEC.page_size == 20

    def test_detail_table_spec_style_table_has_overflow(self):
        from src.pages.cursor_usage._constants import DETAIL_TABLE_SPEC

        assert "overflowX" in DETAIL_TABLE_SPEC.style_table
        assert DETAIL_TABLE_SPEC.style_table["overflowX"] == "auto"

    def test_detail_table_spec_style_cell_text_align(self):
        from src.pages.cursor_usage._constants import DETAIL_TABLE_SPEC

        assert DETAIL_TABLE_SPEC.style_cell["textAlign"] == "left"

    def test_detail_table_spec_style_header_font_weight(self):
        from src.pages.cursor_usage._constants import DETAIL_TABLE_SPEC

        assert DETAIL_TABLE_SPEC.style_header["fontWeight"] == "bold"

    def test_detail_table_spec_column_order(self):
        from src.pages.cursor_usage._constants import DETAIL_TABLE_SPEC, COLUMN_MAP

        expected_order = [
            COLUMN_MAP["date"],
            COLUMN_MAP["user"],
            COLUMN_MAP["model"],
            COLUMN_MAP["kind"],
            COLUMN_MAP["total_tokens"],
            COLUMN_MAP["cost"],
        ]
        assert DETAIL_TABLE_SPEC.column_order == expected_order
