"""Reusable spec dataclasses for tables and charts.

TableSpec -- declarative configuration for Dash DataTable.
ChartSpec -- declarative configuration for Plotly charts.

Both are frozen (immutable) to prevent accidental mutation after creation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TableSpec:
    """Declarative specification for a Dash DataTable.

    Required fields describe the table title and styling.
    Optional fields control sorting, pagination, filtering, column display
    and column ordering.
    """

    # --- required ---
    title: str
    style_table: dict[str, Any]
    style_cell: dict[str, Any]
    style_header: dict[str, Any]
    style_data_conditional: list[dict[str, Any]]

    # --- optional (with defaults) ---
    column_display: dict[str, str] = field(default_factory=dict)
    column_order: list[str] = field(default_factory=list)
    sort_action: str = "none"
    page_size: int = 0
    filter_action: str = "none"


@dataclass(frozen=True)
class ChartSpec:
    """Declarative specification for a Plotly chart.

    Required fields describe the chart title, type, and axis columns.
    Optional fields control visual appearance such as colour mapping,
    height, bar grouping mode, axis labels and legend visibility.
    """

    # --- required ---
    title: str
    chart_type: str
    x_column: str
    y_columns: list[str]

    # --- optional (with defaults) ---
    color_map: dict[str, str] | None = None
    height: int = 400
    barmode: str | None = None
    labels: dict[str, str] | None = None
    show_legend: bool = True
