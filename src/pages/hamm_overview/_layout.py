"""Layout builder for Hamm Overview dashboard."""
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from src.data.parquet_reader import ParquetReader
from src.data.data_source_registry import resolve_dataset_id
from ._constants import (
    DASHBOARD_ID,
    CHART_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    CHART_ID_TASK_TABLE,
    CHART_ID_LANGUAGE_TABLE,
    CHART_ID_ERROR_RATIO,
    CHART_ID_ERROR_BY_SCREENER,
    CHART_ID_USER_BREAKDOWN,
    CHART_ID_HAMM_BREAKDOWN,
    CHART_ID_METADATA_ORIGINAL_LANGUAGE,
    CHART_ID_METADATA_DIALOGUE,
    CHART_ID_METADATA_GENRE,
    CHART_ID_KPI_TOTAL_SCREENS,
    CHART_ID_KPI_TOTAL_ERV,
    CHART_ID_KPI_TOTAL_PRELIM,
)
from ._data_loader import load_filter_options
from ._filters import build_filter_layout, build_cadence_filter


def _chart_card(title: str, chart_id: str) -> dbc.Card:
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
    return dbc.Card([
        dbc.CardHeader(title, className="card-header"),
        dbc.CardBody([
            html.Div(id=table_id),
        ], className="p-1"),
    ])


def build_layout() -> html.Div:
    reader = ParquetReader()
    dataset_id = resolve_dataset_id(DASHBOARD_ID, CHART_ID_VOLUME_TABLE)
    opts = load_filter_options(reader, dataset_id)

    _SECTION_BASE = {
        "backgroundColor": "#2f5f8f",
        "color": "white",
        "borderRadius": "8px",
    }

    title_style = {
        **_SECTION_BASE,
        "padding": "24px",
        "fontSize": "32px",
        "fontWeight": "600",
        "height": "100%",
        "display": "flex",
        "alignItems": "center",
    }

    section_style = {**_SECTION_BASE, "padding": "12px"}

    title_element = html.Div("HAMM Overview", style=title_style)
    filter_rows = build_filter_layout(opts, title_element=title_element)

    return html.Div([
        dmc.MantineProvider([
            filter_rows[0],
            filter_rows[1],

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H3("Volume", className="mb-2", style={"color": "white"}),
                        html.P(
                            "Please use the filter to select the desired calendar interval and metrics for viewing volume.",
                            className="mb-0",
                            style={"color": "rgba(255,255,255,0.85)"},
                        ),
                    ], style={**section_style, "height": "100%"}),
                ], md=7, className="d-flex"),
                dbc.Col([
                    build_cadence_filter(),
                ], md=5, className="d-flex"),
            ], className="mb-3 align-items-stretch"),

            # KPI Cards row
            dbc.Row([
                dbc.Col([html.Div(id=CHART_ID_KPI_TOTAL_SCREENS)], md=4),
                dbc.Col([html.Div(id=CHART_ID_KPI_TOTAL_ERV)], md=4),
                dbc.Col([html.Div(id=CHART_ID_KPI_TOTAL_PRELIM)], md=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    _table_card("Volume Table", CHART_ID_VOLUME_TABLE),
                ], md=6),
                dbc.Col([
                    _chart_card("Volume Chart", CHART_ID_VOLUME_CHART),
                ], md=6),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    _table_card("Task Details", CHART_ID_TASK_TABLE),
                ], md=12),
            ], className="mb-4"),

            # Content Metadata header section
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H3("Content Metadata", className="mb-2", style={"color": "white"}),
                    ], style={**section_style, "height": "100%"}),
                ], md=12),
            ], className="mb-3"),

            # Content Metadata charts
            dbc.Row([
                dbc.Col([
                    _chart_card("Original Language", CHART_ID_METADATA_ORIGINAL_LANGUAGE),
                ], md=4),
                dbc.Col([
                    _chart_card("Was dialogue Provided?", CHART_ID_METADATA_DIALOGUE),
                ], md=4),
                dbc.Col([
                    _chart_card("Genre", CHART_ID_METADATA_GENRE),
                ], md=4),
            ], className="mb-4 chart-density-row"),

            # Error Details header section
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H3("Error Details", className="mb-2", style={"color": "white"}),
                        html.P(
                            "Error analysis showing User vs HAMM intervention breakdown by screener type and error description.",
                            className="mb-0",
                            style={"color": "rgba(255,255,255,0.85)"},
                        ),
                    ], style={**section_style, "height": "100%"}),
                ], md=12),
            ], className="mb-3"),

            # Error Details charts
            dbc.Row([
                dbc.Col([
                    _chart_card("Issues Ratio", CHART_ID_ERROR_RATIO),
                ], md=6),
                dbc.Col([
                    _chart_card("Intervention per Screener Type", CHART_ID_ERROR_BY_SCREENER),
                ], md=6),
            ], className="mb-3 chart-density-row"),
            dbc.Row([
                dbc.Col([
                    _chart_card("User Intervention Breakdown", CHART_ID_USER_BREAKDOWN),
                ], md=6),
                dbc.Col([
                    _chart_card("HAMM Intervention Breakdown", CHART_ID_HAMM_BREAKDOWN),
                ], md=6),
            ], className="mb-4 chart-density-row"),

            # Language per Task table
            dbc.Row([
                dbc.Col([
                    _table_card("Language per Task", CHART_ID_LANGUAGE_TABLE),
                ], md=12),
            ], className="mb-4"),
        ]),  # End MantineProvider
    ], className="page-container")
