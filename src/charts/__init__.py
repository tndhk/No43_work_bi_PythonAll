"""Chart templates and utilities.

Public API:
    - build_chart: Build Plotly charts from DataFrame + ChartSpec
    - build_table: Build Dash DataTables from DataFrame + TableSpec
    - ChartSpec: Declarative chart configuration
    - TableSpec: Declarative table configuration
    - create_empty_figure: Empty state figure factory
    - create_empty_table: Empty state table factory
    - create_error_figure: Error state figure factory
"""
from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.specs import ChartSpec, TableSpec
from src.charts.empty_states import (
    create_empty_figure,
    create_empty_table,
    create_error_figure,
)

__all__ = [
    "build_chart",
    "build_table",
    "ChartSpec",
    "TableSpec",
    "create_empty_figure",
    "create_empty_table",
    "create_error_figure",
]
