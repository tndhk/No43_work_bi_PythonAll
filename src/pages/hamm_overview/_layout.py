"""Layout builder for Hamm Overview dashboard."""
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from src.data.parquet_reader import ParquetReader
from src.data.data_source_registry import resolve_dataset_id
from src.components.filters import create_category_filter, create_slicer_filter
from ._constants import (
    DASHBOARD_ID,
    CHART_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    CHART_ID_TASK_TABLE,
    FILTER_ID_REGION,
    FILTER_ID_YEAR,
    FILTER_ID_MONTH,
    FILTER_ID_TASK_ID,
    FILTER_ID_CONTENT_TYPE,
    FILTER_ID_ORIGINAL_LANGUAGE,
    FILTER_ID_DIALOGUE,
    FILTER_ID_GENRE,
    FILTER_ID_ERROR_CODE,
    FILTER_ID_ERROR_TYPE,
    FILTER_ID_CADENCE,
    CTRL_ID_CLEAR_REGION,
    CTRL_ID_CLEAR_YEAR,
    CTRL_ID_CLEAR_CONTENT_TYPE,
    CTRL_ID_CLEAR_ORIGINAL_LANGUAGE,
    CTRL_ID_CLEAR_DIALOGUE,
    CTRL_ID_CLEAR_GENRE,
    CTRL_ID_CLEAR_ERROR_TYPE,
)
from ._data_loader import load_filter_options


def _build_cadence_filter() -> dbc.Card:
    cadence_options = ["weekly", "monthly", "quarterly", "yearly"]
    chips = [
        dmc.Chip(opt, value=opt, size="sm", variant="outline")
        for opt in cadence_options
    ]
    return dbc.Card([
        dbc.CardHeader("Cadence", className="filter-header"),
        dbc.CardBody([
            html.Div(
                dmc.ChipGroup(
                    id=FILTER_ID_CADENCE,
                    children=chips,
                    value="weekly",
                    multiple=False,
                ),
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "6px"},
            ),
        ], className="cadence-chip-body"),
    ], className="filter-card mb-3")


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

    return html.Div([
        dmc.MantineProvider([
            html.Div([
                html.Div("HAMM Overview 🐷", style=title_style),
                create_slicer_filter(
                    filter_id=FILTER_ID_REGION,
                    column_name="Region",
                    options=opts["regions"],
                    clear_button_id=CTRL_ID_CLEAR_REGION,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_YEAR,
                    column_name="Year",
                    options=opts["years"],
                    clear_button_id=CTRL_ID_CLEAR_YEAR,
                ),
                create_category_filter(
                    filter_id=FILTER_ID_MONTH,
                    column_name="Month",
                    options=opts["months"],
                ),
            ], className="mb-3 filter-row-title-3filters"),

            html.Div([
                create_category_filter(
                    filter_id=FILTER_ID_TASK_ID,
                    column_name="Task ID",
                    options=opts["task_ids"],
                    multi=True,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_CONTENT_TYPE,
                    column_name="Content Type",
                    options=opts["content_types"],
                    clear_button_id=CTRL_ID_CLEAR_CONTENT_TYPE,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_ORIGINAL_LANGUAGE,
                    column_name="Original Language",
                    options=opts["original_languages"],
                    clear_button_id=CTRL_ID_CLEAR_ORIGINAL_LANGUAGE,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_DIALOGUE,
                    column_name="Was Dialogue Provided?",
                    options=opts["dialogue_options"],
                    clear_button_id=CTRL_ID_CLEAR_DIALOGUE,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_GENRE,
                    column_name="Genre",
                    options=opts["genres"],
                    clear_button_id=CTRL_ID_CLEAR_GENRE,
                ),
                create_category_filter(
                    filter_id=FILTER_ID_ERROR_CODE,
                    column_name="Error Code",
                    options=opts["error_codes"],
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_ERROR_TYPE,
                    column_name="Error Type",
                    options=opts["error_types"],
                    clear_button_id=CTRL_ID_CLEAR_ERROR_TYPE,
                ),
            ], className="mb-3 filter-row-7col"),

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
                    _build_cadence_filter(),
                ], md=5, className="d-flex"),
            ], className="mb-3 align-items-stretch"),

            dbc.Row([
                dbc.Col([
                    html.H4("Volume Table", className="mb-2"),
                    html.Div(id=CHART_ID_VOLUME_TABLE),
                ], md=6),
                dbc.Col([
                    html.H4("Volume Chart", className="mb-2"),
                    dcc.Graph(id=CHART_ID_VOLUME_CHART),
                ], md=6),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    html.H4("Task Details", className="mb-2"),
                    html.Div(id=CHART_ID_TASK_TABLE),
                ], md=12),
            ]),
        ]),  # End MantineProvider
    ], className="page-container")
