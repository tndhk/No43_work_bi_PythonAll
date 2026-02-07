"""Cursor Usage Dashboard layout module."""
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.data.parquet_reader import ParquetReader
from src.components.filters import create_date_range_filter, create_category_filter
from ._constants import (
    CHART_ID_KPI_TOTAL_COST,
    CHART_ID_KPI_TOTAL_TOKENS,
    CHART_ID_KPI_REQUEST_COUNT,
    CHART_ID_COST_TREND,
    CHART_ID_TOKEN_EFFICIENCY,
    CHART_ID_MODEL_DISTRIBUTION,
    CHART_ID_DATA_TABLE,
    ID_PREFIX,
)
from ._data_loader import load_filter_options, resolve_dataset_id_for_dashboard


def build_layout():
    """Build Cursor Usage Dashboard layout.

    Returns:
        Dash layout component tree with filters, KPI cards, charts, and data table.
    """
    # Load data to get available options for filters
    reader = ParquetReader()
    dataset_id = resolve_dataset_id_for_dashboard()
    options = load_filter_options(reader, dataset_id)

    return html.Div([
        html.H1("Cursor Usage Dashboard", className="mb-4"),

        # Filters Row 1
        dbc.Row([
            dbc.Col([
                create_date_range_filter(
                    filter_id=f"{ID_PREFIX}filter-date",
                    column_name="Date Range",
                    min_date=options["min_date"],
                    max_date=options["max_date"],
                ),
            ], md=4),
            dbc.Col([
                create_category_filter(
                    filter_id=f"{ID_PREFIX}filter-model",
                    column_name="Model",
                    options=options["models"],
                    multi=True,
                ),
            ], md=4),
            dbc.Col([
                create_category_filter(
                    filter_id=f"{ID_PREFIX}filter-user",
                    column_name="User",
                    options=options["users"],
                    multi=True,
                ),
            ], md=4),
        ], className="mb-3"),

        # Filters Row 2
        dbc.Row([
            dbc.Col([
                create_category_filter(
                    filter_id=f"{ID_PREFIX}filter-kind",
                    column_name="Kind",
                    options=options["kinds"],
                    multi=True,
                ),
            ], md=4),
        ], className="mb-4"),

        # KPI Cards
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

        # Charts Row 1
        dbc.Row([
            dbc.Col([
                dcc.Graph(id=CHART_ID_COST_TREND),
            ], md=12),
        ], className="mb-4"),

        # Charts Row 2
        dbc.Row([
            dbc.Col([
                dcc.Graph(id=CHART_ID_TOKEN_EFFICIENCY),
            ], md=6),
            dbc.Col([
                dcc.Graph(id=CHART_ID_MODEL_DISTRIBUTION),
            ], md=6),
        ], className="mb-4"),

        # Data Table
        dbc.Row([
            dbc.Col([
                html.H3("Detailed Data", className="mb-3"),
                html.Div(id=CHART_ID_DATA_TABLE),
            ], md=12),
        ]),
    ], className="page-container")
