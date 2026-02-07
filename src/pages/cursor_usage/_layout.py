"""Cursor Usage Dashboard layout module."""
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.data.parquet_reader import ParquetReader
from src.components.filters import create_date_range_filter, create_category_filter
from ._constants import DATASET_ID, ID_PREFIX
from ._data_loader import load_filter_options


def build_layout():
    """Build Cursor Usage Dashboard layout.

    Returns:
        Dash layout component tree with filters, KPI cards, charts, and data table.
    """
    # Load data to get available options for filters
    reader = ParquetReader()
    options = load_filter_options(reader, DATASET_ID)

    return html.Div([
        html.H1("Cursor Usage Dashboard", className="mb-4"),

        # Filters
        dbc.Row([
            dbc.Col([
                create_date_range_filter(
                    filter_id=f"{ID_PREFIX}filter-date",
                    column_name="Date Range",
                    min_date=options["min_date"],
                    max_date=options["max_date"],
                ),
            ], md=6),
            dbc.Col([
                create_category_filter(
                    filter_id=f"{ID_PREFIX}filter-model",
                    column_name="Model",
                    options=options["models"],
                    multi=True,
                ),
            ], md=6),
        ], className="mb-4"),

        # KPI Cards
        dbc.Row([
            dbc.Col([
                html.Div(id=f"{ID_PREFIX}kpi-total-cost"),
            ], md=4),
            dbc.Col([
                html.Div(id=f"{ID_PREFIX}kpi-total-tokens"),
            ], md=4),
            dbc.Col([
                html.Div(id=f"{ID_PREFIX}kpi-request-count"),
            ], md=4),
        ], className="mb-4"),

        # Charts Row 1
        dbc.Row([
            dbc.Col([
                dcc.Graph(id=f"{ID_PREFIX}chart-cost-trend"),
            ], md=12),
        ], className="mb-4"),

        # Charts Row 2
        dbc.Row([
            dbc.Col([
                dcc.Graph(id=f"{ID_PREFIX}chart-token-efficiency"),
            ], md=6),
            dbc.Col([
                dcc.Graph(id=f"{ID_PREFIX}chart-model-distribution"),
            ], md=6),
        ], className="mb-4"),

        # Data Table
        dbc.Row([
            dbc.Col([
                html.H3("Detailed Data", className="mb-3"),
                html.Div(id=f"{ID_PREFIX}data-table"),
            ], md=12),
        ]),
    ], className="page-container")
