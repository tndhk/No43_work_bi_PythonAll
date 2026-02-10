"""Cursor Usage Dashboard layout module."""
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.components.cards import create_chart_card, create_table_card
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
        html.H1("Cursor Usage Dashboard", className="row-gap-md"),

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
            ], className="row-gap-md"),
        ]),

        # Charts Row 1
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    create_chart_card(COST_TREND_SPEC.title, CHART_ID_COST_TREND),
                ], md=12),
            ], className="row-gap-md chart-density-row"),
        ]),

        # Charts Row 2
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    create_chart_card(TOKEN_EFFICIENCY_SPEC.title, CHART_ID_TOKEN_EFFICIENCY),
                ], md=6),
                dbc.Col([
                    create_chart_card(MODEL_DISTRIBUTION_SPEC.title, CHART_ID_MODEL_DISTRIBUTION),
                ], md=6),
            ], className="row-gap-md chart-density-row"),
        ]),

        # Data Table
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    create_table_card(DETAIL_TABLE_SPEC.title, CHART_ID_DATA_TABLE),
                ], md=12),
            ]),
        ]),
    ], className="page-container")
