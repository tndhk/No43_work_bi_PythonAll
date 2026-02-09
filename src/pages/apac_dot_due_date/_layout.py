"""Layout builder for APAC DOT Due Date Dashboard.

Extracts the page layout construction from __init__.layout() into a
standalone, testable function.
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from src.data.parquet_reader import ParquetReader
from src.data.data_source_registry import resolve_dataset_id
from ._constants import (
    DASHBOARD_ID,
    KPI_ID_TOTAL_WORK_ORDERS,
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
            - Top information banner
            - Filter panel (2 rows via build_filter_layout)
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

        dbc.Card([
            dbc.CardBody([
                html.H2(
                    "Dive Deep to check if On-Time metrics is truly 100%.",
                    className="apac-dot-info-title",
                ),
                html.P(
                    'Background : In APAC DOMO Metrics Summary, On-Time metrics show "almost 100% On-Time" every month. '
                    "Wondering if this is truly 100% On-Time.",
                    className="apac-dot-info-text",
                ),
                html.P(
                    "How : To see the data about Due Date Change history in DOT, as Due Date Change may cause 100% On-Time.",
                    className="apac-dot-info-text",
                ),
            ]),
        ], id="apac-dot-info-banner", className="apac-dot-info-banner mb-4"),

        # Filter rows (top and bottom) require MantineProvider for slicers
        dmc.MantineProvider([filter_rows[0], filter_rows[1]]),

        # KPI Cards Section
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    html.Div(id=KPI_ID_TOTAL_WORK_ORDERS),
                ], md=3),
            ], className="mt-3 mb-4"),
        ]),

        # Reference / Table Section (Chart 00)
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(id=CHART_ID_REFERENCE_TABLE_TITLE, className="card-header"),
                        dbc.CardBody([
                            html.Div(id=CHART_ID_REFERENCE_TABLE),
                        ]),
                    ]),
                ], md=12),
            ], className="mt-4 mb-3"),
        ]),

        # DDD Change + Issue Table Section (Chart 01)
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(id=CHART_ID_CHANGE_ISSUE_TABLE_TITLE, className="card-header"),
                        dbc.CardBody([
                            html.Div(id=CHART_ID_CHANGE_ISSUE_TABLE),
                        ]),
                    ]),
                ], md=12),
            ], className="mt-4 mb-3"),
        ]),
    ], className="page-container")
