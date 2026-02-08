"""Helper functions for registering common Dash callback patterns.

Eliminates boilerplate for clear-filter callbacks that are duplicated
across multiple dashboard pages.
"""
from typing import Any

import dash
from dash import callback, Input, Output


def register_clear_callbacks(
    clear_pairs: list[tuple[str, str]],
    default_value: Any = [],
) -> None:
    """Register clear-filter callbacks in bulk.

    For each (filter_id, button_id) pair, registers a Dash callback that:
    - Listens to Input(button_id, "n_clicks")
    - Returns default_value to Output(filter_id, "value") when clicked
    - Returns dash.no_update when n_clicks is None or 0

    Args:
        clear_pairs: List of (filter_id, button_id) tuples.
            filter_id: The component ID of the filter to clear.
            button_id: The component ID of the clear button.
        default_value: Value to set the filter to when cleared.
            Defaults to an empty list.

    Example:
        >>> register_clear_callbacks([
        ...     ("cu-filter-date", "cu-clear-date"),
        ...     ("cu-filter-model", "cu-clear-model"),
        ... ])
    """
    def _make_clear_fn(dv: Any) -> callable:
        """Create a clear callback that returns *dv* on click."""
        def _clear(n_clicks):
            if not n_clicks:
                return dash.no_update
            return dv
        return _clear

    for filter_id, button_id in clear_pairs:
        callback(
            Output(filter_id, "value"),
            Input(button_id, "n_clicks"),
            prevent_initial_call=True,
        )(_make_clear_fn(default_value))
