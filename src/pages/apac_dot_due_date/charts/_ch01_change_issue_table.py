"""Chart 1 -- DDD Change + Issue Table: Number of Work Order.

Pure function that builds a pivot-table DataTable from a filtered DataFrame.
No side-effects, no I/O -- only DataFrame manipulation and Dash component
construction.

Uses COLUMN_MAP_2 / BREAKDOWN_MAP_2 for the change-issue dataset schema.
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from ._pivot_table_builder import build_pivot_table
from ._table_specs import TABLE_SPECS
from .._constants import BREAKDOWN_MAP_2, COLUMN_MAP_2

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build(
    filtered_df: pd.DataFrame,
    breakdown_tab: str,
    num_percent_mode: str,
) -> tuple[str, Any]:
    """Build the DDD Change + Issue pivot table.

    Parameters
    ----------
    filtered_df:
        Already-filtered DataFrame containing at least the work order id
        column (COLUMN_MAP_2), the month column, and the breakdown dimension
        columns from COLUMN_MAP_2.
    breakdown_tab:
        Key into ``BREAKDOWN_MAP_2`` (e.g. ``"area"``, ``"category"``,
        ``"vendor"``).
    num_percent_mode:
        ``"number"`` for raw counts or ``"percent"`` for percentage of column
        total.

    Returns
    -------
    tuple[str, Any]
        ``(title_string, dash_component)`` where the component is either a
        ``dash_table.DataTable`` or an ``html.P`` placeholder when the data
        is empty.
    """
    return build_pivot_table(
        filtered_df=filtered_df,
        breakdown_tab=breakdown_tab,
        num_percent_mode=num_percent_mode,
        column_map=COLUMN_MAP_2,
        breakdown_map=BREAKDOWN_MAP_2,
        table_spec=TABLE_SPECS["ch01_change_issue_table"],
    )
