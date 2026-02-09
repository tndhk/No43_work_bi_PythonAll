"""Tests for ensure_list utility function."""

import pytest

from src.utils.callback_helpers import ensure_list


class TestEnsureList:
    """ensure_list must normalise various inputs into a plain list."""

    def test_none_returns_empty_list(self):
        """None should be converted to an empty list."""
        assert ensure_list(None) == []

    def test_list_returned_as_is(self):
        """A list value should be returned unchanged."""
        original = ["a", "b", "c"]
        result = ensure_list(original)
        assert result == ["a", "b", "c"]
        assert result is original  # same object, no copy

    def test_empty_list_returned_as_is(self):
        """An empty list should be returned unchanged."""
        original = []
        result = ensure_list(original)
        assert result == []
        assert result is original

    def test_scalar_string_wrapped_in_list(self):
        """A scalar string should be wrapped in a single-element list."""
        assert ensure_list("hello") == ["hello"]

    def test_scalar_int_wrapped_in_list(self):
        """A scalar integer should be wrapped in a single-element list."""
        assert ensure_list(42) == [42]

    def test_scalar_float_wrapped_in_list(self):
        """A scalar float should be wrapped in a single-element list."""
        assert ensure_list(3.14) == [3.14]

    def test_scalar_bool_wrapped_in_list(self):
        """A boolean should be wrapped in a single-element list."""
        assert ensure_list(True) == [True]

    def test_scalar_zero_wrapped_in_list(self):
        """Zero (falsy but not None) should be wrapped, not treated as empty."""
        assert ensure_list(0) == [0]

    def test_scalar_empty_string_wrapped_in_list(self):
        """Empty string (falsy but not None) should be wrapped, not treated as empty."""
        assert ensure_list("") == [""]

    def test_tuple_wrapped_in_list(self):
        """A tuple is not a list, so it should be wrapped in a list."""
        assert ensure_list((1, 2)) == [(1, 2)]

    def test_dict_wrapped_in_list(self):
        """A dict is not a list, so it should be wrapped in a list."""
        assert ensure_list({"key": "val"}) == [{"key": "val"}]

    def test_list_with_none_elements_returned_as_is(self):
        """A list containing None elements should be returned unchanged."""
        assert ensure_list([None, None]) == [None, None]

    def test_nested_list_returned_as_is(self):
        """A nested list should be returned as-is (no flattening)."""
        assert ensure_list([[1, 2], [3]]) == [[1, 2], [3]]
