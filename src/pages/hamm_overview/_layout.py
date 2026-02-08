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
    CHART_ID_KPI_TOTAL_TASKS,
    CHART_ID_KPI_AVG_VIDEO_DURATION,
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
            dmc.ChipGroup(
                id=FILTER_ID_CADENCE,
                children=chips,
                value="weekly",
                multiple=False,
            ),
        ]),
    ], className="filter-card mb-3")


def build_layout() -> html.Div:
    reader = ParquetReader()
    dataset_id = resolve_dataset_id(DASHBOARD_ID, CHART_ID_VOLUME_TABLE)
    opts = load_filter_options(reader, dataset_id)

    title_style = {
        "backgroundColor": "#2f5f8f",
        "color": "white",
        "padding": "24px",
        "borderRadius": "8px",
        "fontSize": "32px",
        "fontWeight": "600",
        "height": "100%",
        "display": "flex",
        "alignItems": "center",
    }

    section_style = {
        "backgroundColor": "#2f5f8f",
        "color": "white",
        "padding": "18px",
        "borderRadius": "8px",
    }

    return html.Div([
        dmc.MantineProvider([
            dbc.Row([
                dbc.Col([
                    html.Div("HAMM Overview 🐷", style=title_style),
                ], md=6),
                dbc.Col([
                    create_slicer_filter(
                        filter_id=FILTER_ID_REGION,
                        column_name="Region",
                        options=opts["regions"],
                        multi=True,
                    ),
                ], md=2),
                dbc.Col([
                    create_slicer_filter(
                        filter_id=FILTER_ID_YEAR,
                        column_name="Year",
                        options=opts["years"],
                        multi=True,
                    ),
                ], md=2),
                dbc.Col([
                    create_category_filter(
                        filter_id=FILTER_ID_MONTH,
                        column_name="Month",
                        options=opts["months"],
                        multi=True,
                    ),
                ], md=2),
            ], className="mb-3 filter-row"),

            html.Div([
                create_category_filter(
                    filter_id=FILTER_ID_TASK_ID,
                    column_name="Task ID",
                    options=opts["task_ids"],
                    multi=False,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_CONTENT_TYPE,
                    column_name="Content Type",
                    options=opts["content_types"],
                    multi=True,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_ORIGINAL_LANGUAGE,
                    column_name="Original Language",
                    options=opts["original_languages"],
                    multi=True,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_DIALOGUE,
                    column_name="Was Dialogue Provided?",
                    options=opts["dialogue_options"],
                    multi=True,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_GENRE,
                    column_name="Genre",
                    options=opts["genres"],
                    multi=True,
                ),
                create_category_filter(
                    filter_id=FILTER_ID_ERROR_CODE,
                    column_name="Error Code",
                    options=opts["error_codes"],
                    multi=True,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_ERROR_TYPE,
                    column_name="Error Type",
                    options=opts["error_types"],
                    multi=True,
                ),
            ], className="mb-3 filter-row-7col"),

            dbc.Row([
                dbc.Col([
                    html.Div(id=CHART_ID_KPI_TOTAL_TASKS),
                ], md=3),
                dbc.Col([
                    html.Div(id=CHART_ID_KPI_AVG_VIDEO_DURATION),
                ], md=3),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H3("Volume", className="mb-2"),
                        html.P(
                            "Please use the filter to select the desired calendar interval and metrics for viewing volume.",
                            className="mb-0",
                        ),
                    ], style=section_style),
                ], md=9),
                dbc.Col([
                    _build_cadence_filter(),
                ], md=3),
            ], className="mb-3"),

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
