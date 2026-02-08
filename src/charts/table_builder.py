"""Shared table builder: DataFrame + TableSpec -> (title, DataTable).

This module extracts the *rendering* portion that was previously embedded
in page-specific builders (e.g. ``_pivot_table_builder.py``).  Aggregation
/ pivot logic is intentionally excluded -- that remains in the caller.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

import pandas as pd
from dash import dash_table, html

from src.charts.empty_states import create_empty_table
from src.charts.specs import TableSpec


def build_table(
    df: pd.DataFrame,
    spec: TableSpec,
) -> tuple[str, Any]:
    """Convert a DataFrame and a TableSpec into a titled DataTable.

    Args:
        df: Data to display.  An empty DataFrame triggers the empty-state
            fallback (returns ``html.P`` instead of ``DataTable``).
        spec: Declarative table configuration.

    Returns:
        A ``(title, component)`` tuple where *component* is either a
        ``dash_table.DataTable`` or an ``html.P`` empty-state placeholder.
    """
    if len(df) == 0:
        return (spec.title, create_empty_table())

    # --- column ordering ---------------------------------------------------
    if spec.column_order:
        ordered = [col for col in spec.column_order if col in df.columns]
        remaining = [col for col in df.columns if col not in ordered]
        df = df[ordered + remaining]

    # --- column definitions (with display names) ---------------------------
    columns = [
        {"name": spec.column_display.get(col, col), "id": col}
        for col in df.columns
    ]

    data = df.to_dict("records")

    # --- page_size guard: 0 is invalid for pagination, default to 20 -----
    page_size = spec.page_size if spec.page_size > 0 else 20

    # --- build DataTable ---------------------------------------------------
    table = dash_table.DataTable(
        data=data,
        columns=columns,
        style_table=deepcopy(spec.style_table),
        style_cell=deepcopy(spec.style_cell),
        style_header=deepcopy(spec.style_header),
        style_data_conditional=deepcopy(spec.style_data_conditional),
        sort_action=spec.sort_action,
        filter_action=spec.filter_action,
        page_size=page_size,
    )

    return (spec.title, table)
