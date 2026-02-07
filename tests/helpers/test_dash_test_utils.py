"""Tests for the shared Dash component tree test utilities.

TDD Step 1 (RED): These tests define the expected behavior of the
shared helper functions before their implementation in dash_test_utils.py.
"""
import pytest
from dash import html, dcc
import dash_bootstrap_components as dbc


# ===========================================================================
# find_component_by_id tests
# ===========================================================================


class TestFindComponentById:
    """find_component_by_id must recursively search a Dash component tree."""

    def test_finds_component_at_root(self):
        """Should find a component when it is the root itself."""
        from tests.helpers.dash_test_utils import find_component_by_id

        comp = html.Div(id="target")
        result = find_component_by_id(comp, "target")
        assert result is comp

    def test_finds_component_in_children_list(self):
        """Should find a component nested in a children list."""
        from tests.helpers.dash_test_utils import find_component_by_id

        target = html.Span(id="target", children="Hello")
        tree = html.Div(children=[html.P("text"), target])

        result = find_component_by_id(tree, "target")
        assert result is target

    def test_finds_deeply_nested_component(self):
        """Should find a component several levels deep."""
        from tests.helpers.dash_test_utils import find_component_by_id

        target = dcc.Input(id="deep-input")
        tree = html.Div(children=[
            html.Div(children=[
                html.Div(children=[target])
            ])
        ])

        result = find_component_by_id(tree, "deep-input")
        assert result is target

    def test_returns_none_when_not_found(self):
        """Should return None when no component matches the id."""
        from tests.helpers.dash_test_utils import find_component_by_id

        tree = html.Div(children=[html.P("text")])
        result = find_component_by_id(tree, "nonexistent")
        assert result is None

    def test_handles_single_child_not_in_list(self):
        """Should handle cases where children is a single component (not a list)."""
        from tests.helpers.dash_test_utils import find_component_by_id

        target = html.Span(id="single-child")
        tree = html.Div(children=target)

        result = find_component_by_id(tree, "single-child")
        assert result is target

    def test_handles_none_children(self):
        """Should not crash when children is None."""
        from tests.helpers.dash_test_utils import find_component_by_id

        tree = html.Div()
        result = find_component_by_id(tree, "target")
        assert result is None

    def test_handles_string_children(self):
        """Should not crash when children is a plain string."""
        from tests.helpers.dash_test_utils import find_component_by_id

        tree = html.Div(children="Just text")
        result = find_component_by_id(tree, "target")
        assert result is None

    def test_finds_first_match_with_duplicate_ids(self):
        """Should return the first matching component when multiple share an id."""
        from tests.helpers.dash_test_utils import find_component_by_id

        first = html.Span(id="dup", children="first")
        second = html.Span(id="dup", children="second")
        tree = html.Div(children=[first, second])

        result = find_component_by_id(tree, "dup")
        assert result is first


# ===========================================================================
# find_components_by_type tests
# ===========================================================================


class TestFindComponentsByType:
    """find_components_by_type must find all components of a given type."""

    def test_finds_single_component(self):
        """Should find a single component of the target type."""
        from tests.helpers.dash_test_utils import find_components_by_type

        tree = html.Div(children=[html.H1("Title"), html.P("text")])
        results = find_components_by_type(tree, html.H1)
        assert len(results) == 1
        assert isinstance(results[0], html.H1)

    def test_finds_multiple_components(self):
        """Should find all components of the target type."""
        from tests.helpers.dash_test_utils import find_components_by_type

        tree = html.Div(children=[
            html.P("one"),
            html.Div(children=[html.P("two")]),
            html.P("three"),
        ])
        results = find_components_by_type(tree, html.P)
        assert len(results) == 3

    def test_returns_empty_list_when_none_found(self):
        """Should return empty list when no component matches the type."""
        from tests.helpers.dash_test_utils import find_components_by_type

        tree = html.Div(children=[html.P("text")])
        results = find_components_by_type(tree, html.H1)
        assert results == []

    def test_includes_root_if_matching_type(self):
        """Should include the root component if it matches the target type."""
        from tests.helpers.dash_test_utils import find_components_by_type

        tree = html.Div(children=[html.P("text")])
        results = find_components_by_type(tree, html.Div)
        assert len(results) >= 1
        assert isinstance(results[0], html.Div)

    def test_handles_none_children(self):
        """Should handle components with no children."""
        from tests.helpers.dash_test_utils import find_components_by_type

        tree = html.Div()
        results = find_components_by_type(tree, html.P)
        assert results == []


# ===========================================================================
# extract_text_recursive tests
# ===========================================================================


class TestExtractTextRecursive:
    """extract_text_recursive must extract all text from a component tree."""

    def test_extracts_simple_string_child(self):
        """Should extract text from a simple string child."""
        from tests.helpers.dash_test_utils import extract_text_recursive

        comp = html.Div(children="Hello World")
        result = extract_text_recursive(comp)
        assert "Hello World" in result

    def test_extracts_nested_text(self):
        """Should extract text from nested components."""
        from tests.helpers.dash_test_utils import extract_text_recursive

        comp = html.Div(children=[
            html.P("First"),
            html.Span(children=[html.B("Second")]),
        ])
        result = extract_text_recursive(comp)
        assert "First" in result
        assert "Second" in result

    def test_returns_empty_string_for_no_children(self):
        """Should return empty string when component has no text children."""
        from tests.helpers.dash_test_utils import extract_text_recursive

        comp = html.Div()
        result = extract_text_recursive(comp)
        assert result == ""

    def test_handles_mixed_string_and_component_children(self):
        """Should handle a list of strings and components mixed."""
        from tests.helpers.dash_test_utils import extract_text_recursive

        comp = html.Div(children=["Text before ", html.B("bold"), " text after"])
        result = extract_text_recursive(comp)
        assert "Text before" in result
        assert "bold" in result
        assert "text after" in result

    def test_returns_string_type(self):
        """Return type must be str."""
        from tests.helpers.dash_test_utils import extract_text_recursive

        comp = html.Div(children="test")
        result = extract_text_recursive(comp)
        assert isinstance(result, str)


# ===========================================================================
# extract_dropdown_options tests
# ===========================================================================


class TestExtractDropdownOptions:
    """extract_dropdown_options must find a dropdown by id and return its options."""

    def test_extracts_options_from_dropdown(self):
        """Should return the options list of a dropdown."""
        from tests.helpers.dash_test_utils import extract_dropdown_options

        options = [{"label": "A", "value": "a"}, {"label": "B", "value": "b"}]
        tree = html.Div(children=[
            dcc.Dropdown(id="my-dd", options=options, value="a"),
        ])

        result = extract_dropdown_options(tree, "my-dd")
        assert result == options

    def test_finds_nested_dropdown(self):
        """Should find a dropdown nested inside multiple containers."""
        from tests.helpers.dash_test_utils import extract_dropdown_options

        options = [{"label": "X", "value": "x"}]
        tree = html.Div(children=[
            html.Div(children=[
                dcc.Dropdown(id="nested-dd", options=options),
            ])
        ])

        result = extract_dropdown_options(tree, "nested-dd")
        assert result == options

    def test_returns_none_when_dropdown_not_found(self):
        """Should return None when no dropdown matches the id."""
        from tests.helpers.dash_test_utils import extract_dropdown_options

        tree = html.Div(children=[html.P("no dropdown")])
        result = extract_dropdown_options(tree, "nonexistent")
        assert result is None

    def test_handles_none_children(self):
        """Should handle tree with None children gracefully."""
        from tests.helpers.dash_test_utils import extract_dropdown_options

        tree = html.Div()
        result = extract_dropdown_options(tree, "target")
        assert result is None


# ===========================================================================
# extract_dropdown_value tests
# ===========================================================================


class TestExtractDropdownValue:
    """extract_dropdown_value must find a dropdown by id and return its value."""

    def test_extracts_value_from_dropdown(self):
        """Should return the value of a dropdown."""
        from tests.helpers.dash_test_utils import extract_dropdown_value

        tree = html.Div(children=[
            dcc.Dropdown(id="my-dd", options=[], value="selected"),
        ])

        result = extract_dropdown_value(tree, "my-dd")
        assert result == "selected"

    def test_extracts_multi_select_value(self):
        """Should return a list value for multi-select dropdowns."""
        from tests.helpers.dash_test_utils import extract_dropdown_value

        tree = html.Div(children=[
            dcc.Dropdown(id="multi-dd", options=[], value=["a", "b"], multi=True),
        ])

        result = extract_dropdown_value(tree, "multi-dd")
        assert result == ["a", "b"]

    def test_returns_none_when_dropdown_not_found(self):
        """Should return None when no dropdown matches the id."""
        from tests.helpers.dash_test_utils import extract_dropdown_value

        tree = html.Div(children=[html.P("no dropdown")])
        result = extract_dropdown_value(tree, "nonexistent")
        assert result is None

    def test_returns_none_for_dropdown_with_no_value_set(self):
        """Should return None when dropdown exists but has no value."""
        from tests.helpers.dash_test_utils import extract_dropdown_value

        tree = html.Div(children=[
            dcc.Dropdown(id="no-val-dd", options=[]),
        ])

        result = extract_dropdown_value(tree, "no-val-dd")
        # dcc.Dropdown default value is None
        assert result is None
