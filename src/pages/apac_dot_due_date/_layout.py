"""Layout builder for APAC DOT Due Date Dashboard.

Extracts the page layout construction from __init__.layout() into a
standalone, testable function.
"""
from dash import html
import dash_bootstrap_components as dbc

from src.data.parquet_reader import ParquetReader
from src.data.data_source_registry import resolve_dataset_id
from ._constants import (
    DASHBOARD_ID,
    CHART_ID_REFERENCE_TABLE,
    CHART_ID_REFERENCE_TABLE_TITLE,
    CHART_ID_CHANGE_ISSUE_TABLE,
    CHART_ID_CHANGE_ISSUE_TABLE_TITLE,
)
from ._data_loader import load_filter_options
from ._filters import build_filter_layout


def build_layout() -> html.Div:
    """Build the full APAC DOT Due Date Dashboard layout.

    Returns:
        html.Div containing:
            - H1 page title
            - Filter panel (5 rows via build_filter_layout)
            - Chart 00: Reference Table section
            - Chart 01: DDD Change + Issue Table section
    """
    # Load data to get available options for filters
    reader = ParquetReader()
    dataset_id = resolve_dataset_id(DASHBOARD_ID, CHART_ID_REFERENCE_TABLE)
    dataset_id_2 = resolve_dataset_id(DASHBOARD_ID, CHART_ID_CHANGE_ISSUE_TABLE)
    opts = load_filter_options(reader, dataset_id, dataset_id_2)

    # Build filter rows via _filters module
    filter_rows = build_filter_layout(opts)

    return html.Div([
        html.H1("APAC DOT Due Date Dashboard", className="mb-4"),

        # Filter rows (control, month, prc, category, additional)
        *filter_rows,

        # Reference / Table Section (Chart 00)
        dbc.Row([
            dbc.Col([
                html.H3(id=CHART_ID_REFERENCE_TABLE_TITLE, className="mt-4 mb-3"),
                html.Div(id=CHART_ID_REFERENCE_TABLE),
            ], md=12),
        ]),

        # DDD Change + Issue Table Section (Chart 01)
        dbc.Row([
            dbc.Col([
                html.H3(id=CHART_ID_CHANGE_ISSUE_TABLE_TITLE, className="mt-4 mb-3"),
                html.Div(id=CHART_ID_CHANGE_ISSUE_TABLE),
            ], md=12),
        ]),
    ], className="page-container")
