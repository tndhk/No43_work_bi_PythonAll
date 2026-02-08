"""Tests for TableSpec and ChartSpec dataclasses."""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# TableSpec tests
# ---------------------------------------------------------------------------

class TestTableSpec:
    """Tests for the TableSpec frozen dataclass."""

    def test_import(self):
        """TableSpec can be imported from src.charts.specs."""
        from src.charts.specs import TableSpec  # noqa: F401

    def test_create_with_all_required_fields(self):
        """TableSpec can be instantiated with all required fields."""
        from src.charts.specs import TableSpec

        spec = TableSpec(
            title="Test Table",
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
            style_header={"fontWeight": "bold"},
            style_data_conditional=[],
        )
        assert spec.title == "Test Table"
        assert spec.style_table == {"overflowX": "auto"}
        assert spec.style_cell == {"textAlign": "left"}
        assert spec.style_header == {"fontWeight": "bold"}
        assert spec.style_data_conditional == []

    def test_default_column_display_is_empty_dict(self):
        """column_display defaults to an empty dict."""
        from src.charts.specs import TableSpec

        spec = TableSpec(
            title="T",
            style_table={},
            style_cell={},
            style_header={},
            style_data_conditional=[],
        )
        assert spec.column_display == {}

    def test_default_column_order_is_empty_list(self):
        """column_order defaults to an empty list."""
        from src.charts.specs import TableSpec

        spec = TableSpec(
            title="T",
            style_table={},
            style_cell={},
            style_header={},
            style_data_conditional=[],
        )
        assert spec.column_order == []

    def test_default_sort_action_is_none_string(self):
        """sort_action defaults to 'none'."""
        from src.charts.specs import TableSpec

        spec = TableSpec(
            title="T",
            style_table={},
            style_cell={},
            style_header={},
            style_data_conditional=[],
        )
        assert spec.sort_action == "none"

    def test_default_page_size_is_zero(self):
        """page_size defaults to 0 (no pagination)."""
        from src.charts.specs import TableSpec

        spec = TableSpec(
            title="T",
            style_table={},
            style_cell={},
            style_header={},
            style_data_conditional=[],
        )
        assert spec.page_size == 0

    def test_default_filter_action_is_none_string(self):
        """filter_action defaults to 'none'."""
        from src.charts.specs import TableSpec

        spec = TableSpec(
            title="T",
            style_table={},
            style_cell={},
            style_header={},
            style_data_conditional=[],
        )
        assert spec.filter_action == "none"

    def test_override_new_defaults(self):
        """New optional fields can be overridden at construction time."""
        from src.charts.specs import TableSpec

        spec = TableSpec(
            title="T",
            style_table={},
            style_cell={},
            style_header={},
            style_data_conditional=[],
            sort_action="native",
            page_size=25,
            filter_action="native",
        )
        assert spec.sort_action == "native"
        assert spec.page_size == 25
        assert spec.filter_action == "native"

    def test_frozen_prevents_mutation(self):
        """TableSpec is frozen -- attribute assignment raises."""
        from src.charts.specs import TableSpec

        spec = TableSpec(
            title="T",
            style_table={},
            style_cell={},
            style_header={},
            style_data_conditional=[],
        )
        with pytest.raises(AttributeError):
            spec.title = "Changed"

    def test_default_factory_isolation(self):
        """Each instance gets its own default mutable containers."""
        from src.charts.specs import TableSpec

        spec_a = TableSpec(
            title="A",
            style_table={},
            style_cell={},
            style_header={},
            style_data_conditional=[],
        )
        spec_b = TableSpec(
            title="B",
            style_table={},
            style_cell={},
            style_header={},
            style_data_conditional=[],
        )
        assert spec_a.column_display is not spec_b.column_display
        assert spec_a.column_order is not spec_b.column_order


# ---------------------------------------------------------------------------
# ChartSpec tests
# ---------------------------------------------------------------------------

class TestChartSpec:
    """Tests for the ChartSpec frozen dataclass."""

    def test_import(self):
        """ChartSpec can be imported from src.charts.specs."""
        from src.charts.specs import ChartSpec  # noqa: F401

    def test_create_with_required_fields(self):
        """ChartSpec can be instantiated with required fields only."""
        from src.charts.specs import ChartSpec

        spec = ChartSpec(
            title="Revenue by Region",
            chart_type="bar",
            x_column="region",
            y_columns=["revenue"],
        )
        assert spec.title == "Revenue by Region"
        assert spec.chart_type == "bar"
        assert spec.x_column == "region"
        assert spec.y_columns == ["revenue"]

    def test_multiple_y_columns(self):
        """y_columns accepts multiple column names."""
        from src.charts.specs import ChartSpec

        spec = ChartSpec(
            title="T",
            chart_type="bar",
            x_column="x",
            y_columns=["a", "b", "c"],
        )
        assert spec.y_columns == ["a", "b", "c"]

    def test_default_color_map_is_none(self):
        """color_map defaults to None."""
        from src.charts.specs import ChartSpec

        spec = ChartSpec(
            title="T", chart_type="bar", x_column="x", y_columns=["y"]
        )
        assert spec.color_map is None

    def test_default_height_is_400(self):
        """height defaults to 400."""
        from src.charts.specs import ChartSpec

        spec = ChartSpec(
            title="T", chart_type="bar", x_column="x", y_columns=["y"]
        )
        assert spec.height == 400

    def test_default_barmode_is_none(self):
        """barmode defaults to None."""
        from src.charts.specs import ChartSpec

        spec = ChartSpec(
            title="T", chart_type="bar", x_column="x", y_columns=["y"]
        )
        assert spec.barmode is None

    def test_default_labels_is_none(self):
        """labels defaults to None."""
        from src.charts.specs import ChartSpec

        spec = ChartSpec(
            title="T", chart_type="bar", x_column="x", y_columns=["y"]
        )
        assert spec.labels is None

    def test_default_show_legend_is_true(self):
        """show_legend defaults to True."""
        from src.charts.specs import ChartSpec

        spec = ChartSpec(
            title="T", chart_type="bar", x_column="x", y_columns=["y"]
        )
        assert spec.show_legend is True

    def test_override_all_optional_fields(self):
        """All optional fields can be overridden at construction time."""
        from src.charts.specs import ChartSpec

        color_map = {"A": "#ff0000", "B": "#00ff00"}
        labels = {"revenue": "Revenue ($)"}
        spec = ChartSpec(
            title="Custom",
            chart_type="line",
            x_column="date",
            y_columns=["revenue", "cost"],
            color_map=color_map,
            height=600,
            barmode="group",
            labels=labels,
            show_legend=False,
        )
        assert spec.color_map == color_map
        assert spec.height == 600
        assert spec.barmode == "group"
        assert spec.labels == labels
        assert spec.show_legend is False

    def test_frozen_prevents_mutation(self):
        """ChartSpec is frozen -- attribute assignment raises."""
        from src.charts.specs import ChartSpec

        spec = ChartSpec(
            title="T", chart_type="bar", x_column="x", y_columns=["y"]
        )
        with pytest.raises(AttributeError):
            spec.title = "Changed"

    def test_frozen_prevents_y_columns_reassignment(self):
        """Cannot reassign y_columns on a frozen instance."""
        from src.charts.specs import ChartSpec

        spec = ChartSpec(
            title="T", chart_type="bar", x_column="x", y_columns=["y"]
        )
        with pytest.raises(AttributeError):
            spec.y_columns = ["z"]
