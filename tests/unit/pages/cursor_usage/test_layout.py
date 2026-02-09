"""Tests for cursor_usage layout module."""
from unittest.mock import patch, MagicMock
from dash import html, dcc
import dash_bootstrap_components as dbc
import pytest

from tests.helpers.dash_test_utils import find_components


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


# ---------------------------------------------------------------------------
# Helper: recursive component finder (same as hamm_overview test_layout)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Shared layout fixture for chart-density tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def layout():
    """Build layout with mocked data dependencies."""
    import src.pages.cursor_usage._layout as _layout_mod

    mock_opts = {
        "min_date": "2024-01-01",
        "max_date": "2024-12-31",
        "models": ["gpt-4", "claude-3"],
        "users": ["user1", "user2"],
        "kinds": ["chat", "completion"],
    }
    with patch.object(
        _layout_mod, "load_filter_options", return_value=mock_opts
    ), patch.object(
        _layout_mod, "ParquetReader", return_value=MagicMock()
    ), patch.object(
        _layout_mod, "resolve_dataset_id_for_dashboard", return_value="cursor-usage-dataset"
    ):
        return _layout_mod.build_layout()


# ---------------------------------------------------------------------------
# Chart density CSS class tests (RED -- not yet implemented)
# ---------------------------------------------------------------------------

class TestChartRowDensityClass:
    """Charts Row 1 and Row 2 must have 'chart-density-row' className."""

    def test_charts_row_1_has_density_class(self, layout):
        """The dbc.Row containing CHART_ID_COST_TREND must have 'chart-density-row'."""
        from src.pages.cursor_usage._constants import CHART_ID_COST_TREND

        rows = find_components(
            layout,
            lambda c: isinstance(c, dbc.Row)
            and "chart-density-row" in (getattr(c, "className", None) or ""),
        )
        # Find the row that contains the cost trend chart
        matching = [
            r for r in rows
            if find_components(
                r,
                lambda c: isinstance(c, dcc.Graph)
                and getattr(c, "id", None) == CHART_ID_COST_TREND,
            )
        ]
        assert len(matching) >= 1, (
            "Expected Charts Row 1 (containing cost trend) to have "
            "'chart-density-row' in className"
        )

    def test_charts_row_2_has_density_class(self, layout):
        """The dbc.Row containing token efficiency and model distribution must have 'chart-density-row'."""
        from src.pages.cursor_usage._constants import CHART_ID_TOKEN_EFFICIENCY

        rows = find_components(
            layout,
            lambda c: isinstance(c, dbc.Row)
            and "chart-density-row" in (getattr(c, "className", None) or ""),
        )
        matching = [
            r for r in rows
            if find_components(
                r,
                lambda c: isinstance(c, dcc.Graph)
                and getattr(c, "id", None) == CHART_ID_TOKEN_EFFICIENCY,
            )
        ]
        assert len(matching) >= 1, (
            "Expected Charts Row 2 (containing token efficiency) to have "
            "'chart-density-row' in className"
        )


class TestChartCardDensityClass:
    """All 3 chart dbc.Cards must have 'chart-density-card' className."""

    def test_three_chart_cards_have_density_class(self, layout):
        cards = find_components(
            layout,
            lambda c: isinstance(c, dbc.Card)
            and "chart-density-card" in (getattr(c, "className", None) or ""),
        )
        assert len(cards) == 3, (
            f"Expected 3 dbc.Card with 'chart-density-card' class, got {len(cards)}"
        )


class TestChartGraphDensityClassAndConfig:
    """All 3 chart dcc.Graphs must have 'chart-density-graph' className and compact config."""

    def _get_chart_graph_ids(self):
        from src.pages.cursor_usage._constants import (
            CHART_ID_COST_TREND,
            CHART_ID_TOKEN_EFFICIENCY,
            CHART_ID_MODEL_DISTRIBUTION,
        )
        return {CHART_ID_COST_TREND, CHART_ID_TOKEN_EFFICIENCY, CHART_ID_MODEL_DISTRIBUTION}

    def test_three_chart_graphs_have_density_class(self, layout):
        expected_ids = self._get_chart_graph_ids()
        graphs = find_components(
            layout,
            lambda c: isinstance(c, dcc.Graph)
            and getattr(c, "id", None) in expected_ids,
        )
        assert len(graphs) == 3, f"Expected 3 chart graphs, got {len(graphs)}"

        for graph in graphs:
            class_name = getattr(graph, "className", "") or ""
            assert "chart-density-graph" in class_name, (
                f"Graph id={graph.id} should have 'chart-density-graph' in className, "
                f"got '{class_name}'"
            )

    def test_three_chart_graphs_have_compact_config(self, layout):
        expected_ids = self._get_chart_graph_ids()
        graphs = find_components(
            layout,
            lambda c: isinstance(c, dcc.Graph)
            and getattr(c, "id", None) in expected_ids,
        )
        assert len(graphs) == 3, f"Expected 3 chart graphs, got {len(graphs)}"

        for graph in graphs:
            config = getattr(graph, "config", None) or {}
            assert config.get("displayModeBar") is False, (
                f"Graph id={graph.id} should have displayModeBar=False"
            )
            assert config.get("responsive") is True, (
                f"Graph id={graph.id} should have responsive=True"
            )
