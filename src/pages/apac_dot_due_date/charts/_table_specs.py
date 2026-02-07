"""Human-editable table specs for APAC DOT Due Date charts.

Edit this file to change titles or table appearance. Do not change the
builder logic in _pivot_table_builder.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TableSpec:
    title: str
    style_table: dict[str, Any]
    style_cell: dict[str, Any]
    style_header: dict[str, Any]
    style_data_conditional: list[dict[str, Any]]
    column_display: dict[str, str] = field(default_factory=dict)
    column_order: list[str] = field(default_factory=list)


TABLE_SPECS: dict[str, TableSpec] = {
    "ch00_reference_table": TableSpec(
        title="0) Reference : Number of Work Order",
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
                "if": {"filter_query": "{breakdown_col} = \"GRAND TOTAL\""},
                "fontWeight": "bold",
                "backgroundColor": "#eff6ff",
            }
        ],
    ),
    "ch01_change_issue_table": TableSpec(
        title="1) DDD Change + Issue : Number of Work Order",
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
                "if": {"filter_query": "{breakdown_col} = \"GRAND TOTAL\""},
                "fontWeight": "bold",
                "backgroundColor": "#eff6ff",
            }
        ],
    ),
}
