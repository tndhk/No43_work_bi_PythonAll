"""Tests for empty state factory functions.

These helpers consolidate duplicated empty-figure / empty-table patterns
currently scattered across 6+ locations in callback modules.
"""
from __future__ import annotations

import plotly.graph_objects as go
import pytest


# ---------------------------------------------------------------------------
# create_empty_figure
# ---------------------------------------------------------------------------

class TestCreateEmptyFigure:
    """Tests for create_empty_figure()."""

    def test_import(self):
        """Function can be imported from src.charts.empty_states."""
        from src.charts.empty_states import create_empty_figure  # noqa: F401

    def test_returns_go_figure(self):
        """Returns a plotly Figure instance."""
        from src.charts.empty_states import create_empty_figure

        result = create_empty_figure()
        assert isinstance(result, go.Figure)

    def test_default_message(self):
        """Default annotation text is 'No data available'."""
        from src.charts.empty_states import create_empty_figure

        fig = create_empty_figure()
        annotations = fig.layout.annotations
        assert len(annotations) == 1
        assert annotations[0].text == "No data available"

    def test_custom_message(self):
        """Annotation text can be overridden."""
        from src.charts.empty_states import create_empty_figure

        fig = create_empty_figure(message="Nothing here")
        assert fig.layout.annotations[0].text == "Nothing here"

    def test_default_height(self):
        """Default height is 400."""
        from src.charts.empty_states import create_empty_figure

        fig = create_empty_figure()
        assert fig.layout.height == 400

    def test_custom_height(self):
        """Height can be overridden."""
        from src.charts.empty_states import create_empty_figure

        fig = create_empty_figure(height=600)
        assert fig.layout.height == 600

    def test_annotation_centered(self):
        """Annotation is positioned at center (0.5, 0.5) with paper reference."""
        from src.charts.empty_states import create_empty_figure

        fig = create_empty_figure()
        ann = fig.layout.annotations[0]
        assert ann.x == 0.5
        assert ann.y == 0.5
        assert ann.xref == "paper"
        assert ann.yref == "paper"
        assert ann.showarrow is False

    def test_no_data_traces(self):
        """Empty figure should have no data traces."""
        from src.charts.empty_states import create_empty_figure

        fig = create_empty_figure()
        assert len(fig.data) == 0


# ---------------------------------------------------------------------------
# create_empty_table
# ---------------------------------------------------------------------------

class TestCreateEmptyTable:
    """Tests for create_empty_table()."""

    def test_import(self):
        """Function can be imported from src.charts.empty_states."""
        from src.charts.empty_states import create_empty_table  # noqa: F401

    def test_returns_dash_html_p(self):
        """Returns a dash html.P component."""
        from dash import html

        from src.charts.empty_states import create_empty_table

        result = create_empty_table()
        assert isinstance(result, html.P)

    def test_default_message(self):
        """Default text is 'No data available'."""
        from src.charts.empty_states import create_empty_table

        result = create_empty_table()
        assert result.children == "No data available"

    def test_custom_message(self):
        """Custom text can be provided."""
        from src.charts.empty_states import create_empty_table

        result = create_empty_table(message="Empty table")
        assert result.children == "Empty table"

    def test_css_class(self):
        """Component has the 'text-muted' CSS class."""
        from src.charts.empty_states import create_empty_table

        result = create_empty_table()
        assert result.className == "text-muted"


# ---------------------------------------------------------------------------
# create_error_figure
# ---------------------------------------------------------------------------

class TestCreateErrorFigure:
    """Tests for create_error_figure()."""

    def test_import(self):
        """Function can be imported from src.charts.empty_states."""
        from src.charts.empty_states import create_error_figure  # noqa: F401

    def test_returns_go_figure(self):
        """Returns a plotly Figure instance."""
        from src.charts.empty_states import create_error_figure

        result = create_error_figure("Something broke")
        assert isinstance(result, go.Figure)

    def test_error_message_in_annotation(self):
        """The error string is included in the annotation text."""
        from src.charts.empty_states import create_error_figure

        fig = create_error_figure("DB timeout")
        assert fig.layout.annotations[0].text == "DB timeout"

    def test_default_height(self):
        """Default height is 400."""
        from src.charts.empty_states import create_error_figure

        fig = create_error_figure("err")
        assert fig.layout.height == 400

    def test_custom_height(self):
        """Height can be overridden."""
        from src.charts.empty_states import create_error_figure

        fig = create_error_figure("err", height=300)
        assert fig.layout.height == 300

    def test_annotation_centered(self):
        """Annotation is positioned at center (0.5, 0.5) with paper reference."""
        from src.charts.empty_states import create_error_figure

        fig = create_error_figure("err")
        ann = fig.layout.annotations[0]
        assert ann.x == 0.5
        assert ann.y == 0.5
        assert ann.xref == "paper"
        assert ann.yref == "paper"
        assert ann.showarrow is False

    def test_error_font_color_is_red(self):
        """Error annotation uses red font color to signal an error state."""
        from src.charts.empty_states import create_error_figure

        fig = create_error_figure("err")
        ann = fig.layout.annotations[0]
        assert ann.font.color == "red"

    def test_no_data_traces(self):
        """Error figure should have no data traces."""
        from src.charts.empty_states import create_error_figure

        fig = create_error_figure("err")
        assert len(fig.data) == 0
