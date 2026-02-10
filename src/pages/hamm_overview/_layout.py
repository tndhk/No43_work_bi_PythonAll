"""Layout for HAMM Overview dashboard."""
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html

from src.data.parquet_reader import ParquetReader
from src.data.data_source_registry import resolve_dataset_id
from ._constants import (
    DASHBOARD_ID,
    KPI_ID_KPI_TOTAL_SCREENS,
    KPI_ID_KPI_TOTAL_ERV,
    KPI_ID_KPI_TOTAL_PRELIM,
    TABLE_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
)
from ._filters import build_filter_layout
from ._data_loader import load_filter_options


def _chart_card(title: str, chart_id: str) -> dbc.Card:
    """Create a card containing a chart."""
    return dbc.Card([
        dbc.CardHeader(title, className="card-header"),
        dbc.CardBody([
            dcc.Graph(
                id=chart_id,
                className="chart-density-graph",
                config={"displayModeBar": False, "responsive": True},
            ),
        ], className="p-1"),
    ], className="chart-density-card")


def _table_card(title: str, table_id: str) -> dbc.Card:
    """Create a card containing a table."""
    return dbc.Card([
        dbc.CardHeader(title, className="card-header"),
        dbc.CardBody([
            html.Div(id=table_id),
        ], className="p-1"),
    ])


def build_layout() -> html.Div:
    """Build the dashboard layout."""
    reader = ParquetReader()
    dataset_id = resolve_dataset_id(DASHBOARD_ID, "id")
    opts = load_filter_options(reader, dataset_id)
    title_element = html.H1("HAMM Overview", className="page-title")
    filter_rows = build_filter_layout(opts, title_element=title_element)

    content = []

    content.append(dbc.Row([
        dbc.Col([html.Div(id=KPI_ID_KPI_TOTAL_SCREENS)], md=4),
        dbc.Col([html.Div(id=KPI_ID_KPI_TOTAL_ERV)], md=4),
        dbc.Col([html.Div(id=KPI_ID_KPI_TOTAL_PRELIM)], md=4),
    ], className="mb-3"))

    content.append(dbc.Row([
        dbc.Col([_table_card("Volume Summary", TABLE_ID_VOLUME_TABLE)], md=6),
        dbc.Col([_chart_card("Volume Chart", CHART_ID_VOLUME_CHART)], md=6),
    ], className="mb-4"))

    return html.Div([
        dmc.MantineProvider([
            *filter_rows,
            dcc.Loading(content),
        ]),
    ], className="page-container")
