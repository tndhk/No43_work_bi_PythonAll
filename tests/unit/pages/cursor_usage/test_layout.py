"""Tests for cursor_usage layout module."""
from unittest.mock import patch, MagicMock
import pytest


class TestBuildLayout:
    """Tests for build_layout function."""

    @pytest.fixture
    def mock_filter_options(self):
        """Mock filter options returned by load_filter_options."""
        return {
            "min_date": "2024-01-01",
            "max_date": "2024-12-31",
            "models": ["gpt-4", "claude-3"],
            "users": ["user1", "user2"],
            "kinds": ["chat", "completion"],
        }

    @pytest.fixture
    def mock_reader(self):
        """Mock ParquetReader."""
        return MagicMock()

    def test_build_layout_returns_div(self, mock_filter_options, mock_reader):
        """
        Given: Filter options are available
        When: build_layout is called
        Then: Returns a Dash html.Div component
        """
        with patch(
            "src.pages.cursor_usage._layout.ParquetReader",
            return_value=mock_reader,
        ), patch(
            "src.pages.cursor_usage._layout.resolve_dataset_id_for_dashboard",
            return_value="cursor-usage-dataset",
        ), patch(
            "src.pages.cursor_usage._layout.load_filter_options",
            return_value=mock_filter_options,
        ):
            from src.pages.cursor_usage._layout import build_layout
            from dash import html

            result = build_layout()

            assert isinstance(result, html.Div)

    def test_build_layout_contains_title(self, mock_filter_options, mock_reader):
        """
        Given: Filter options are available
        When: build_layout is called
        Then: Layout contains H1 title
        """
        with patch(
            "src.pages.cursor_usage._layout.ParquetReader",
            return_value=mock_reader,
        ), patch(
            "src.pages.cursor_usage._layout.resolve_dataset_id_for_dashboard",
            return_value="cursor-usage-dataset",
        ), patch(
            "src.pages.cursor_usage._layout.load_filter_options",
            return_value=mock_filter_options,
        ):
            from src.pages.cursor_usage._layout import build_layout
            from dash import html
            from tests.helpers.dash_test_utils import find_components_by_type

            result = build_layout()
            h1_list = find_components_by_type(result, html.H1)

            assert len(h1_list) > 0
            h1 = h1_list[0]
            assert "Cursor Usage" in h1.children

    def test_build_layout_contains_filters(self, mock_filter_options, mock_reader):
        """
        Given: Filter options are available
        When: build_layout is called
        Then: Layout contains filter components
        """
        with patch(
            "src.pages.cursor_usage._layout.ParquetReader",
            return_value=mock_reader,
        ), patch(
            "src.pages.cursor_usage._layout.resolve_dataset_id_for_dashboard",
            return_value="cursor-usage-dataset",
        ), patch(
            "src.pages.cursor_usage._layout.load_filter_options",
            return_value=mock_filter_options,
        ):
            from src.pages.cursor_usage._layout import build_layout
            from tests.helpers.dash_test_utils import find_component_by_id
            from src.pages.cursor_usage._constants import ID_PREFIX

            result = build_layout()

            # Check filter IDs exist
            date_filter = find_component_by_id(result, f"{ID_PREFIX}filter-date")
            model_filter = find_component_by_id(result, f"{ID_PREFIX}filter-model")
            user_filter = find_component_by_id(result, f"{ID_PREFIX}filter-user")
            kind_filter = find_component_by_id(result, f"{ID_PREFIX}filter-kind")

            assert date_filter is not None
            assert model_filter is not None
            assert user_filter is not None
            assert kind_filter is not None

    def test_build_layout_contains_kpi_cards(self, mock_filter_options, mock_reader):
        """
        Given: Filter options are available
        When: build_layout is called
        Then: Layout contains KPI card placeholders
        """
        with patch(
            "src.pages.cursor_usage._layout.ParquetReader",
            return_value=mock_reader,
        ), patch(
            "src.pages.cursor_usage._layout.resolve_dataset_id_for_dashboard",
            return_value="cursor-usage-dataset",
        ), patch(
            "src.pages.cursor_usage._layout.load_filter_options",
            return_value=mock_filter_options,
        ):
            from src.pages.cursor_usage._layout import build_layout
            from src.pages.cursor_usage._constants import (
                CHART_ID_KPI_TOTAL_COST,
                CHART_ID_KPI_TOTAL_TOKENS,
                CHART_ID_KPI_REQUEST_COUNT,
            )
            from tests.helpers.dash_test_utils import find_component_by_id

            result = build_layout()

            kpi_cost = find_component_by_id(result, CHART_ID_KPI_TOTAL_COST)
            kpi_tokens = find_component_by_id(result, CHART_ID_KPI_TOTAL_TOKENS)
            kpi_requests = find_component_by_id(result, CHART_ID_KPI_REQUEST_COUNT)

            assert kpi_cost is not None
            assert kpi_tokens is not None
            assert kpi_requests is not None

    def test_build_layout_contains_charts(self, mock_filter_options, mock_reader):
        """
        Given: Filter options are available
        When: build_layout is called
        Then: Layout contains chart components
        """
        with patch(
            "src.pages.cursor_usage._layout.ParquetReader",
            return_value=mock_reader,
        ), patch(
            "src.pages.cursor_usage._layout.resolve_dataset_id_for_dashboard",
            return_value="cursor-usage-dataset",
        ), patch(
            "src.pages.cursor_usage._layout.load_filter_options",
            return_value=mock_filter_options,
        ):
            from src.pages.cursor_usage._layout import build_layout
            from src.pages.cursor_usage._constants import (
                CHART_ID_COST_TREND,
                CHART_ID_TOKEN_EFFICIENCY,
                CHART_ID_MODEL_DISTRIBUTION,
                CHART_ID_DATA_TABLE,
            )
            from tests.helpers.dash_test_utils import find_component_by_id

            result = build_layout()

            cost_trend = find_component_by_id(result, CHART_ID_COST_TREND)
            token_eff = find_component_by_id(result, CHART_ID_TOKEN_EFFICIENCY)
            model_dist = find_component_by_id(result, CHART_ID_MODEL_DISTRIBUTION)
            data_table = find_component_by_id(result, CHART_ID_DATA_TABLE)

            assert cost_trend is not None
            assert token_eff is not None
            assert model_dist is not None
            assert data_table is not None
