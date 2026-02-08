"""Chart aggregation logic for APAC DOT Due Date pivot tables.

Extracts the aggregation (groupby + pivot + grand total + percent
conversion) from the old charts/_pivot_table_builder.py into a
standalone function that returns a DataFrame.  Rendering is handled
by the shared ``build_table()`` in ``src.charts.table_builder``.
"""
from __future__ import annotations

import pandas as pd


def build_pivot_data(
    filtered_df: pd.DataFrame,
    breakdown_tab: str,
    num_percent_mode: str,
    column_map: dict[str, str],
    breakdown_map: dict[str, str],
) -> pd.DataFrame:
    """Aggregate a filtered DataFrame into a pivoted summary table.

    Args:
        filtered_df: Pre-filtered DataFrame to aggregate.
        breakdown_tab: One of the keys in *breakdown_map* (e.g. "area").
        num_percent_mode: ``"num"`` for raw counts, ``"percent"`` for
            column-percentage conversion.
        column_map: Mapping from logical names to DataFrame column names.
        breakdown_map: Mapping from breakdown tab keys to column names.

    Returns:
        A pivoted DataFrame with breakdown values as rows, months as
        columns, a GRAND TOTAL row, and an AVG column.  Ready for
        ``build_table()``.  Returns an empty DataFrame when input is empty.
    """
    if len(filtered_df) == 0:
        return pd.DataFrame()

    breakdown_column = breakdown_map[breakdown_tab]
    work_order_col = column_map["work_order_id"]

    pivot_data = (
        filtered_df
        .groupby([breakdown_column, column_map["month"]])[work_order_col]
        .nunique()
        .reset_index()
    )

    pivot_table = pivot_data.pivot(
        index=breakdown_column,
        columns=column_map["month"],
        values=work_order_col,
    ).fillna(0)

    pivot_table = pivot_table.reindex(sorted(pivot_table.columns), axis=1)

    # Format month columns as strings
    pivot_table.columns = [
        col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
        for col in pivot_table.columns
    ]

    # Add GRAND TOTAL row and AVG column
    pivot_table.loc["GRAND TOTAL"] = pivot_table.sum()
    pivot_table["AVG"] = pivot_table.mean(axis=1).round(0)

    # Convert to percentages if requested
    if num_percent_mode == "percent":
        grand_total_row = pivot_table.loc["GRAND TOTAL"].copy()
        for col in pivot_table.columns:
            if col != "AVG":
                col_total = grand_total_row[col]
                if col_total == 0:
                    pivot_table[col] = 0.0
                else:
                    pivot_table[col] = (
                        pivot_table[col] / col_total * 100
                    ).round(1)
        pivot_table["AVG"] = (
            pivot_table.drop(columns=["AVG"]).mean(axis=1).round(1)
        )

    # Reset index so breakdown column becomes a regular column
    pivot_table = pivot_table.reset_index()
    pivot_table.columns.name = None

    return pivot_table
