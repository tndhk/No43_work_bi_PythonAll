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


# ---------------------------------------------------------------------------
# Default table style constants (reusable across pages)
# ---------------------------------------------------------------------------
DEFAULT_STYLE_TABLE: dict[str, Any] = {"overflowX": "auto"}
DEFAULT_STYLE_CELL: dict[str, Any] = {
    "textAlign": "left",
    "padding": "8px",
    "fontSize": "14px",
}
DEFAULT_STYLE_HEADER: dict[str, Any] = {
    "fontWeight": "bold",
    "backgroundColor": "#2563eb",
    "color": "white",
}
# Compact variant for dense tables (e.g. hamm_overview)
COMPACT_STYLE_CELL: dict[str, Any] = {
    "textAlign": "left",
    "padding": "2px 4px",
    "fontSize": "0.75rem",
    "whiteSpace": "nowrap",
}
COMPACT_STYLE_HEADER: dict[str, Any] = {
    "fontWeight": "bold",
    "fontSize": "0.75rem",
    "padding": "2px 4px",
    "whiteSpace": "normal",
}


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
    orientation: str = "v"  # "v" for vertical (default), "h" for horizontal bars
    text_template: str | None = None  # Data labels template (e.g., "%{y:.1f}")
    hover_template: str | None = None  # Hover tooltip template (e.g., "%{x}<br>%{y:.2f}")
