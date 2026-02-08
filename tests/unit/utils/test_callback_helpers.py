"""Tests for callback_helpers module."""
from unittest.mock import patch, MagicMock
import pytest

import dash

from src.utils.callback_helpers import register_clear_callbacks


class TestRegisterClearCallbacks:
    """register_clear_callbacks must register Dash callbacks correctly."""

    def test_empty_pairs_registers_no_callbacks(self):
        """No callbacks should be registered when clear_pairs is empty."""
        with patch("src.utils.callback_helpers.callback") as mock_callback:
            register_clear_callbacks([])
            mock_callback.assert_not_called()

    def test_single_pair_registers_one_callback(self):
        """A single (filter_id, button_id) pair should register exactly one callback."""
        with patch("src.utils.callback_helpers.callback") as mock_callback:
            mock_callback.return_value = lambda fn: fn
            register_clear_callbacks([
                ("cu-filter-date", "cu-clear-date"),
            ])
            assert mock_callback.call_count == 1

    def test_multiple_pairs_register_multiple_callbacks(self):
        """Each pair should register its own callback."""
        with patch("src.utils.callback_helpers.callback") as mock_callback:
            mock_callback.return_value = lambda fn: fn
            register_clear_callbacks([
                ("cu-filter-date", "cu-clear-date"),
                ("cu-filter-model", "cu-clear-model"),
                ("cu-filter-region", "cu-clear-region"),
            ])
            assert mock_callback.call_count == 3

    def test_callback_uses_correct_output(self):
        """Output should target (filter_id, 'value')."""
        with patch("src.utils.callback_helpers.callback") as mock_callback:
            mock_callback.return_value = lambda fn: fn
            register_clear_callbacks([
                ("my-filter", "my-button"),
            ])
            call_args = mock_callback.call_args
            output = call_args[0][0]
            assert output.component_id == "my-filter"
            assert output.component_property == "value"

    def test_callback_uses_correct_input(self):
        """Input should target (button_id, 'n_clicks')."""
        with patch("src.utils.callback_helpers.callback") as mock_callback:
            mock_callback.return_value = lambda fn: fn
            register_clear_callbacks([
                ("my-filter", "my-button"),
            ])
            call_args = mock_callback.call_args
            input_dep = call_args[0][1]
            assert input_dep.component_id == "my-button"
            assert input_dep.component_property == "n_clicks"

    def test_callback_sets_prevent_initial_call(self):
        """prevent_initial_call=True should be set on each callback."""
        with patch("src.utils.callback_helpers.callback") as mock_callback:
            mock_callback.return_value = lambda fn: fn
            register_clear_callbacks([
                ("my-filter", "my-button"),
            ])
            call_kwargs = mock_callback.call_args[1]
            assert call_kwargs.get("prevent_initial_call") is True

    def test_callback_returns_no_update_when_n_clicks_is_none(self):
        """When n_clicks is None, the callback should return dash.no_update."""
        captured_fns = []

        def fake_callback(*args, **kwargs):
            def decorator(fn):
                captured_fns.append(fn)
                return fn
            return decorator

        with patch("src.utils.callback_helpers.callback", side_effect=fake_callback):
            register_clear_callbacks([
                ("my-filter", "my-button"),
            ])

        assert len(captured_fns) == 1
        result = captured_fns[0](None)
        assert result is dash.no_update

    def test_callback_returns_no_update_when_n_clicks_is_zero(self):
        """When n_clicks is 0, the callback should return dash.no_update."""
        captured_fns = []

        def fake_callback(*args, **kwargs):
            def decorator(fn):
                captured_fns.append(fn)
                return fn
            return decorator

        with patch("src.utils.callback_helpers.callback", side_effect=fake_callback):
            register_clear_callbacks([
                ("my-filter", "my-button"),
            ])

        result = captured_fns[0](0)
        assert result is dash.no_update

    def test_callback_returns_default_value_on_click(self):
        """When n_clicks > 0, the callback should return default_value (empty list)."""
        captured_fns = []

        def fake_callback(*args, **kwargs):
            def decorator(fn):
                captured_fns.append(fn)
                return fn
            return decorator

        with patch("src.utils.callback_helpers.callback", side_effect=fake_callback):
            register_clear_callbacks([
                ("my-filter", "my-button"),
            ])

        result = captured_fns[0](1)
        assert result == []

    def test_custom_default_value(self):
        """When a custom default_value is provided, it should be returned on click."""
        captured_fns = []

        def fake_callback(*args, **kwargs):
            def decorator(fn):
                captured_fns.append(fn)
                return fn
            return decorator

        with patch("src.utils.callback_helpers.callback", side_effect=fake_callback):
            register_clear_callbacks(
                [("my-filter", "my-button")],
                default_value=None,
            )

        result = captured_fns[0](1)
        assert result is None

    def test_each_pair_gets_independent_callback(self):
        """Each pair should produce its own callable with correct IDs."""
        captured_fns = []
        captured_outputs = []

        def fake_callback(*args, **kwargs):
            def decorator(fn):
                captured_fns.append(fn)
                captured_outputs.append(args[0])
                return fn
            return decorator

        with patch("src.utils.callback_helpers.callback", side_effect=fake_callback):
            register_clear_callbacks([
                ("filter-a", "button-a"),
                ("filter-b", "button-b"),
            ])

        assert len(captured_fns) == 2
        assert captured_outputs[0].component_id == "filter-a"
        assert captured_outputs[1].component_id == "filter-b"

        # Both callbacks should work independently
        assert captured_fns[0](1) == []
        assert captured_fns[1](1) == []
        assert captured_fns[0](None) is dash.no_update
        assert captured_fns[1](0) is dash.no_update

    def test_high_n_clicks_value_returns_default(self):
        """Large n_clicks values should still return default_value."""
        captured_fns = []

        def fake_callback(*args, **kwargs):
            def decorator(fn):
                captured_fns.append(fn)
                return fn
            return decorator

        with patch("src.utils.callback_helpers.callback", side_effect=fake_callback):
            register_clear_callbacks([
                ("my-filter", "my-button"),
            ])

        result = captured_fns[0](999)
        assert result == []
