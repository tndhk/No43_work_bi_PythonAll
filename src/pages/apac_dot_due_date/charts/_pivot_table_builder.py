"""Common pivot-table builder for APAC DOT Due Date tables."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

import pandas as pd
from dash import dash_table, html

from ._table_specs import TableSpec


def build_pivot_table(
    filtered_df: pd.DataFrame,
    breakdown_tab: str,
    num_percent_mode: str,
    column_map: dict[str, str],
    breakdown_map: dict[str, str],
    table_spec: TableSpec,
) -> tuple[str, Any]:
    """Build a pivot-table DataTable from a filtered DataFrame."""
    if len(filtered_df) == 0:
        return (
            table_spec.title,
            html.P("No data available for selected filters", className="text-muted"),
        )

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

    pivot_table.columns = [
        col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
        for col in pivot_table.columns
    ]

    pivot_table.loc["GRAND TOTAL"] = pivot_table.sum()
    pivot_table["AVG"] = pivot_table.mean(axis=1).round(0)

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

    pivot_table = pivot_table.reset_index()
    pivot_table.columns.name = None

    if table_spec.column_order:
        ordered = [col for col in table_spec.column_order if col in pivot_table.columns]
        remaining = [col for col in pivot_table.columns if col not in ordered]
        pivot_table = pivot_table[ordered + remaining]

    columns = [
        {"name": table_spec.column_display.get(col, col), "id": col}
        for col in pivot_table.columns
    ]
    data = pivot_table.to_dict("records")

    style_data_conditional = deepcopy(table_spec.style_data_conditional)
    for rule in style_data_conditional:
        if not isinstance(rule, dict):
            continue
        condition = rule.get("if")
        if not isinstance(condition, dict):
            continue
        filter_query = condition.get("filter_query")
        if isinstance(filter_query, str):
            condition["filter_query"] = filter_query.replace(
                "{breakdown_col}", f"{{{breakdown_column}}}"
            )

    table_component = dash_table.DataTable(
        data=data,
        columns=columns,
        style_table=deepcopy(table_spec.style_table),
        style_cell=deepcopy(table_spec.style_cell),
        style_header=deepcopy(table_spec.style_header),
        style_data_conditional=style_data_conditional,
    )

    return (table_spec.title, table_component)
