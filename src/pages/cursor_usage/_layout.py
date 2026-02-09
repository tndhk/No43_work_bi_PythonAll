"""Cursor Usage Dashboard layout module."""
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.data.parquet_reader import ParquetReader
from ._constants import (
    CHART_ID_KPI_TOTAL_COST,
    CHART_ID_KPI_TOTAL_TOKENS,
    CHART_ID_KPI_REQUEST_COUNT,
    CHART_ID_COST_TREND,
    CHART_ID_TOKEN_EFFICIENCY,
    CHART_ID_MODEL_DISTRIBUTION,
    CHART_ID_DATA_TABLE,
    COST_TREND_SPEC,
    TOKEN_EFFICIENCY_SPEC,
    MODEL_DISTRIBUTION_SPEC,
    DETAIL_TABLE_SPEC,
)
from ._data_loader import load_filter_options, resolve_dataset_id_for_dashboard
from ._filters import build_filter_layout


def build_layout():
    """Build Cursor Usage Dashboard layout.

    Returns:
        Dash layout component tree with filters, KPI cards, charts, and data table.
    """
    # Load data to get available options for filters
    reader = ParquetReader()
    dataset_id = resolve_dataset_id_for_dashboard()
    options = load_filter_options(reader, dataset_id)

    # Build filter rows
    filter_rows = build_filter_layout(options)

    return html.Div([
        html.H1("Cursor Usage Dashboard", className="mb-4"),

        # Filters
        filter_rows[0],
        filter_rows[1],

        # KPI Cards
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    html.Div(id=CHART_ID_KPI_TOTAL_COST),
                ], md=4),
                dbc.Col([
                    html.Div(id=CHART_ID_KPI_TOTAL_TOKENS),
                ], md=4),
                dbc.Col([
                    html.Div(id=CHART_ID_KPI_REQUEST_COUNT),
                ], md=4),
            ], className="mb-4"),
        ]),

        # Charts Row 1
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(COST_TREND_SPEC.title, className="card-header"),
                        dbc.CardBody([
                            dcc.Graph(
                                id=CHART_ID_COST_TREND,
                                className="chart-density-graph",
                                config={"displayModeBar": False, "responsive": True},
                            ),
                        ]),
                    ], className="chart-density-card"),
                ], md=12),
            ], className="mb-4 chart-density-row"),
        ]),

        # Charts Row 2
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(TOKEN_EFFICIENCY_SPEC.title, className="card-header"),
                        dbc.CardBody([
                            dcc.Graph(
                                id=CHART_ID_TOKEN_EFFICIENCY,
                                className="chart-density-graph",
                                config={"displayModeBar": False, "responsive": True},
                            ),
                        ]),
                    ], className="chart-density-card"),
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(MODEL_DISTRIBUTION_SPEC.title, className="card-header"),
                        dbc.CardBody([
                            dcc.Graph(
                                id=CHART_ID_MODEL_DISTRIBUTION,
                                className="chart-density-graph",
                                config={"displayModeBar": False, "responsive": True},
                            ),
                        ]),
                    ], className="chart-density-card"),
                ], md=6),
            ], className="mb-4 chart-density-row"),
        ]),

        # Data Table
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(DETAIL_TABLE_SPEC.title, className="card-header"),
                        dbc.CardBody([
                            html.Div(id=CHART_ID_DATA_TABLE),
                        ]),
                    ]),
                ], md=12),
            ]),
        ]),
    ], className="page-container")
