"""Tests for KPI card and shared chart/table card components."""
import pytest
import dash_bootstrap_components as dbc
from dash import dcc, html
from src.components.cards import (
    create_kpi_card,
    create_chart_card,
    create_table_card,
    DEFAULT_GRAPH_CONFIG,
)


def test_create_kpi_card_with_int_value():
    """Test: KPI card with integer value."""
    # Given: Title and integer value
    title = "Total Sales"
    value = 1000
    
    # When: Creating KPI card
    card = create_kpi_card(title, value)
    
    # Then: Card component is created
    assert isinstance(card, dbc.Card)
    assert card is not None


def test_create_kpi_card_with_float_value():
    """Test: KPI card with float value."""
    # Given: Title and float value
    title = "Average Price"
    value = 99.99
    
    # When: Creating KPI card
    card = create_kpi_card(title, value)
    
    # Then: Card component is created
    assert isinstance(card, dbc.Card)
    assert card is not None


def test_create_kpi_card_with_string_value():
    """Test: KPI card with string value."""
    # Given: Title and string value
    title = "Status"
    value = "Active"
    
    # When: Creating KPI card
    card = create_kpi_card(title, value)
    
    # Then: Card component is created
    assert isinstance(card, dbc.Card)
    assert card is not None


def test_create_kpi_card_with_subtitle():
    """Test: KPI card with subtitle."""
    # Given: Title, value, and subtitle
    title = "Total Sales"
    value = 1000
    subtitle = "+5% vs last month"
    
    # When: Creating KPI card with subtitle
    card = create_kpi_card(title, value, subtitle)
    
    # Then: Card component is created
    assert isinstance(card, dbc.Card)
    assert card is not None


def test_create_kpi_card_without_subtitle():
    """Test: KPI card without subtitle."""
    # Given: Title and value only (no subtitle)
    title = "Total Sales"
    value = 1000

    # When: Creating KPI card without subtitle
    card = create_kpi_card(title, value)

    # Then: Card component is created
    assert isinstance(card, dbc.Card)
    assert card is not None


# ---------------------------------------------------------------------------
# bg_color / accent_color options (new feature)
# ---------------------------------------------------------------------------

class TestCreateKpiCardBgColor:
    """Tests for bg_color parameter on create_kpi_card."""

    def test_bg_color_applies_background_style(self):
        """bg_color specified -> card style contains backgroundColor."""
        # Given
        bg = "#f0f8ff"

        # When
        card = create_kpi_card("Revenue", 42000, bg_color=bg)

        # Then: style dict includes backgroundColor
        style = card.style or {}
        assert style.get("backgroundColor") == bg, (
            f"Expected backgroundColor={bg!r}, got style={style!r}"
        )

    def test_bg_color_none_keeps_default_style(self):
        """bg_color=None (default) -> no backgroundColor injected."""
        # When
        card = create_kpi_card("Revenue", 42000)

        # Then: style should not have backgroundColor key
        style = card.style or {}
        assert "backgroundColor" not in style, (
            f"backgroundColor should not be present when bg_color is None, "
            f"got style={style!r}"
        )

    def test_bg_color_with_subtitle(self):
        """bg_color works alongside subtitle parameter."""
        bg = "#ffe0e0"
        card = create_kpi_card("Errors", 7, subtitle="critical", bg_color=bg)

        style = card.style or {}
        assert style.get("backgroundColor") == bg
        assert isinstance(card, dbc.Card)


class TestCreateKpiCardAccentColor:
    """Tests for accent_color parameter on create_kpi_card."""

    def test_accent_color_applies_border_top(self):
        """accent_color specified -> card style contains borderTop."""
        # Given
        accent = "#e57f7f"

        # When
        card = create_kpi_card("Volume", 100, accent_color=accent)

        # Then
        style = card.style or {}
        expected_border = f"4px solid {accent}"
        assert style.get("borderTop") == expected_border, (
            f"Expected borderTop={expected_border!r}, got style={style!r}"
        )

    def test_accent_color_none_keeps_default_style(self):
        """accent_color=None (default) -> no borderTop injected."""
        card = create_kpi_card("Volume", 100)

        style = card.style or {}
        assert "borderTop" not in style, (
            f"borderTop should not be present when accent_color is None, "
            f"got style={style!r}"
        )

    def test_accent_color_with_subtitle(self):
        """accent_color works alongside subtitle parameter."""
        accent = "#5f8fc7"
        card = create_kpi_card("Tasks", 55, subtitle="+3", accent_color=accent)

        style = card.style or {}
        expected_border = f"4px solid {accent}"
        assert style.get("borderTop") == expected_border


class TestCreateKpiCardBgAndAccentCombined:
    """Tests for using bg_color and accent_color together."""

    def test_both_colors_applied(self):
        """Both bg_color and accent_color produce combined style."""
        bg = "#f0f8ff"
        accent = "#e57f7f"

        card = create_kpi_card("Combined", 999, bg_color=bg, accent_color=accent)

        style = card.style or {}
        assert style.get("backgroundColor") == bg
        assert style.get("borderTop") == f"4px solid {accent}"

    def test_neither_color_no_style_keys(self):
        """Neither bg_color nor accent_color -> no extra style keys."""
        card = create_kpi_card("Plain", 0)

        style = card.style or {}
        assert "backgroundColor" not in style
        assert "borderTop" not in style

    def test_backward_compatibility_positional_args(self):
        """Existing positional calls (title, value, subtitle) still work."""
        card = create_kpi_card("Title", 123, "sub")
        assert isinstance(card, dbc.Card)
        # No style keys added when color params are omitted
        style = card.style or {}
        assert "backgroundColor" not in style
        assert "borderTop" not in style


# ---------------------------------------------------------------------------
# create_chart_card
# ---------------------------------------------------------------------------

class TestCreateChartCard:
    """Tests for create_chart_card shared API."""

    def test_returns_card_with_header_and_graph(self):
        """Given title and chart_id, When creating chart card, Then Card with CardHeader and dcc.Graph."""
        # Given: 有効なカードタイトルとチャートID
        card = create_chart_card("Test Chart", "chart-id")
        # When: 共有チャートカードを生成する
        assert isinstance(card, dbc.Card)
        assert "chart-density-card" in (card.className or "")
        # CardHeader + CardBody with dcc.Graph
        header = card.children[0]
        body = card.children[1]
        # Then: 標準ヘッダー/ボディ/Graph構成と既定設定が適用される
        assert isinstance(header, dbc.CardHeader)
        assert header.children == "Test Chart"
        assert "card-header" in (header.className or "")
        assert isinstance(body, dbc.CardBody)
        graph = body.children[0]
        assert isinstance(graph, dcc.Graph)
        assert graph.id == "chart-id"
        assert "chart-density-graph" in (graph.className or "")
        assert graph.config == {"displayModeBar": False, "responsive": True}

    def test_default_config_used(self):
        """When no graph_config provided, Then DEFAULT_GRAPH_CONFIG is applied."""
        # Given: graph_config を明示しない入力
        card = create_chart_card("X", "y")
        # When: カードを生成する
        body = card.children[1]
        graph = body.children[0]
        # Then: 既定の Graph 設定が利用される
        assert graph.config == DEFAULT_GRAPH_CONFIG


# ---------------------------------------------------------------------------
# create_table_card
# ---------------------------------------------------------------------------

class TestCreateTableCard:
    """Tests for create_table_card shared API."""

    def test_returns_card_with_header_and_div(self):
        """Given title and table_id, When creating table card, Then Card with CardHeader and html.Div."""
        # Given: 有効なタイトルとテーブルID
        card = create_table_card("Test Table", "table-id")
        # When: 共有テーブルカードを生成する
        assert isinstance(card, dbc.Card)
        header = card.children[0]
        body = card.children[1]
        # Then: ヘッダーとテーブルコンテナDivが作成される
        assert isinstance(header, dbc.CardHeader)
        assert header.children == "Test Table"
        assert body.children[0].id == "table-id"
        assert isinstance(body.children[0], html.Div)

    def test_header_id_for_dynamic_title(self):
        """When header_id provided, Then CardHeader has id attribute."""
        # Given: 動的ヘッダー向けの header_id が指定される
        card = create_table_card("", "t1", header_id="header-1")
        # When: テーブルカードを生成する
        header = card.children[0]
        # Then: CardHeader に id が設定される
        assert header.id == "header-1"
