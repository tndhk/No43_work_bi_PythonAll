"""Chart 0 -- Reference Table: Number of Work Order.

Pure function that builds a pivot-table DataTable from a filtered DataFrame.
No side-effects, no I/O -- only DataFrame manipulation and Dash component
construction.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
from dash import dash_table, html

from src.pages.apac_dot_due_date._constants import BREAKDOWN_MAP, COLUMN_MAP

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_TITLE = "0) Reference : Number of Work Order"


def build(
    filtered_df: pd.DataFrame,
    breakdown_tab: str,
    num_percent_mode: str,
) -> tuple[str, Any]:
    """Build the reference pivot table.

    Parameters
    ----------
    filtered_df:
        Already-filtered DataFrame containing at least ``work order id``,
        the month column, and the breakdown dimension columns.
    breakdown_tab:
        Key into ``BREAKDOWN_MAP`` (e.g. ``"area"``, ``"category"``, ``"vendor"``).
    num_percent_mode:
        ``"number"`` for raw counts or ``"percent"`` for percentage of column total.

    Returns
    -------
    tuple[str, Any]
        ``(title_string, dash_component)`` where the component is either a
        ``dash_table.DataTable`` or an ``html.P`` placeholder when the data is
        empty.
    """
    # ------------------------------------------------------------------
    # Empty guard
    # ------------------------------------------------------------------
    if len(filtered_df) == 0:
        return (
            _TITLE,
            html.P("No data available for selected filters", className="text-muted"),
        )

    # ------------------------------------------------------------------
    # Determine breakdown column
    # ------------------------------------------------------------------
    breakdown_column = BREAKDOWN_MAP[breakdown_tab]

    # ------------------------------------------------------------------
    # Group by breakdown column + month, count unique work order IDs
    # ------------------------------------------------------------------
    pivot_data = (
        filtered_df
        .groupby([breakdown_column, COLUMN_MAP["month"]])["work order id"]
        .nunique()
        .reset_index()
    )

    # ------------------------------------------------------------------
    # Create pivot table
    # ------------------------------------------------------------------
    pivot_table = pivot_data.pivot(
        index=breakdown_column,
        columns=COLUMN_MAP["month"],
        values="work order id",
    ).fillna(0)

    # Sort month columns chronologically
    pivot_table = pivot_table.reindex(sorted(pivot_table.columns), axis=1)

    # Convert Timestamp column names to strings for JSON serialization
    pivot_table.columns = [
        col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
        for col in pivot_table.columns
    ]

    # ------------------------------------------------------------------
    # Add GRAND TOTAL row
    # ------------------------------------------------------------------
    pivot_table.loc["GRAND TOTAL"] = pivot_table.sum()

    # ------------------------------------------------------------------
    # Add Average column
    # ------------------------------------------------------------------
    pivot_table["AVG"] = pivot_table.mean(axis=1).round(0)

    # ------------------------------------------------------------------
    # Convert to percentage if requested
    # ------------------------------------------------------------------
    if num_percent_mode == "percent":
        grand_total_row = pivot_table.loc["GRAND TOTAL"].copy()
        for col in pivot_table.columns:
            if col != "AVG":
                pivot_table[col] = (
                    pivot_table[col] / grand_total_row[col] * 100
                ).round(1)
        # Recalculate AVG for percentage mode
        pivot_table["AVG"] = (
            pivot_table.drop(columns=["AVG"]).mean(axis=1).round(1)
        )

    # ------------------------------------------------------------------
    # Prepare for DataTable
    # ------------------------------------------------------------------
    pivot_table = pivot_table.reset_index()
    pivot_table.columns.name = None

    columns = [{"name": col, "id": col} for col in pivot_table.columns]
    data = pivot_table.to_dict("records")

    table_component = dash_table.DataTable(
        data=data,
        columns=columns,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontSize": "14px",
        },
        style_header={
            "fontWeight": "bold",
            "backgroundColor": "#2563eb",
            "color": "white",
        },
        style_data_conditional=[
            {
                "if": {"filter_query": f'{{{breakdown_column}}} = "GRAND TOTAL"'},
                "fontWeight": "bold",
                "backgroundColor": "#eff6ff",
            }
        ],
    )

    return (_TITLE, table_component)
