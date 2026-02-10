"""Layout for HAMM Overview dashboard.

Auto-generated from page_spec.yaml by tools.page_generator,
then manually customized for Volume section styling and density layout.
"""
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html

from src.components.cards import create_chart_card, create_table_card
from src.data.parquet_reader import ParquetReader
from ._constants import (
    KPI_ID_KPI_TOTAL_SCREENS,
    KPI_ID_KPI_TOTAL_ERV,
    KPI_ID_KPI_TOTAL_PRELIM,
    TABLE_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    TABLE_ID_TASK_TABLE,
    TABLE_ID_LANGUAGE_TABLE,
    CHART_ID_METADATA_ORIGINAL_LANGUAGE,
    CHART_ID_METADATA_DIALOGUE,
    CHART_ID_METADATA_GENRE,
    CHART_ID_ERROR_RATIO,
    CHART_ID_ERROR_BY_SCREENER,
    CHART_ID_USER_BREAKDOWN,
    CHART_ID_BREAKDOWN,
    FILTER_ID_FILTER_CADENCE,
)
from ._filters import build_filter_layout
from ._data_loader import load_filter_options, resolve_dataset_id_for_dashboard


def build_layout() -> html.Div:
    """Build the dashboard layout."""
    reader = ParquetReader()
    dataset_id = resolve_dataset_id_for_dashboard()

    # Load filter options
    opts = load_filter_options(reader, dataset_id)

    # Build title element with 32px font size
    title_element = html.Div(
        "HAMM Overview",
        style={
            "fontSize": "32px",
            "fontWeight": "bold",
            "color": "white",
            "backgroundColor": "#4a7fb5",
            "borderRadius": "8px",
            "padding": "12px 16px",
            "display": "flex",
            "alignItems": "center",
        },
    )

    # Build filters
    filter_rows = build_filter_layout(opts, title_element=title_element)

    # Build main content
    content = []

    # -----------------------------------------------------------------------
    # Volume section: blue background with KPIs + Cadence selector
    # -----------------------------------------------------------------------
    volume_section = html.Div(
        [
            html.H3("Volume", style={"color": "white", "marginBottom": "8px"}),
            html.P(
                "Screening volume by cadence period",
                style={"color": "rgba(255, 255, 255, 0.8)"},
            ),
            dbc.Row([
                dbc.Col([html.Div(id=KPI_ID_KPI_TOTAL_SCREENS)], md=4, className="d-flex"),
                dbc.Col([html.Div(id=KPI_ID_KPI_TOTAL_ERV)], md=4, className="d-flex"),
                dbc.Col([html.Div(id=KPI_ID_KPI_TOTAL_PRELIM)], md=4, className="d-flex"),
            ]),
        ],
        style={
            "backgroundColor": "#2f5f8f",
            "padding": "16px",
            "borderRadius": "8px",
        },
    )

    cadence_card = dbc.Card([
        dbc.CardHeader("Cadence", className="card-header"),
        dbc.CardBody(
            [
                dmc.ChipGroup(
                    id=FILTER_ID_FILTER_CADENCE,
                    children=[
                        dmc.Chip("Weekly", value="weekly", size="sm"),
                        dmc.Chip("Monthly", value="monthly", size="sm"),
                        dmc.Chip("Quarterly", value="quarterly", size="sm"),
                        dmc.Chip("Yearly", value="yearly", size="sm"),
                    ],
                    value="weekly",
                    multiple=False,
                ),
            ],
            className="cadence-chip-body",
        ),
    ], className="cadence-card", style={"height": "100%"})

    content.append(dbc.Row([
        dbc.Col([volume_section], md=9, className="d-flex"),
        dbc.Col([cadence_card], md=3, className="d-flex"),
    ], className="row-gap-sm align-items-stretch"))

    # -----------------------------------------------------------------------
    # Volume table + chart
    # -----------------------------------------------------------------------
    content.append(dbc.Row([
        dbc.Col([create_table_card("Volume Summary", TABLE_ID_VOLUME_TABLE)], md=6),
        dbc.Col([create_chart_card("Volume Chart", CHART_ID_VOLUME_CHART)], md=6),
    ], className="row-gap-md chart-density-row"))

    # -----------------------------------------------------------------------
    # Task Details
    # -----------------------------------------------------------------------
    content.append(dbc.Row([
        dbc.Col([create_table_card("Task Details", TABLE_ID_TASK_TABLE)], md=12),
    ], className="row-gap-md"))

    # -----------------------------------------------------------------------
    # Content Metadata section
    # -----------------------------------------------------------------------
    content.append(html.H3("Content Metadata"))
    content.append(dbc.Row([
        dbc.Col([create_chart_card("Original Language", CHART_ID_METADATA_ORIGINAL_LANGUAGE)], md=4),
        dbc.Col([create_chart_card("Was dialogue Provided?", CHART_ID_METADATA_DIALOGUE)], md=4),
        dbc.Col([create_chart_card("Genre", CHART_ID_METADATA_GENRE)], md=4),
    ], className="row-gap-md chart-density-row"))

    # -----------------------------------------------------------------------
    # Error Details section
    # -----------------------------------------------------------------------
    content.append(dbc.Row([
        dbc.Col([create_chart_card("Issues Ratio (HAMM vs Human Intervention)", CHART_ID_ERROR_RATIO)], md=6),
        dbc.Col([create_chart_card("Intervention per Screener Type", CHART_ID_ERROR_BY_SCREENER)], md=6),
    ], className="row-gap-sm chart-density-row"))

    content.append(dbc.Row([
        dbc.Col([create_chart_card("User Intervention Breakdown", CHART_ID_USER_BREAKDOWN)], md=6),
        dbc.Col([create_chart_card("HAMM Intervention Breakdown", CHART_ID_BREAKDOWN)], md=6),
    ], className="row-gap-md chart-density-row"))

    # -----------------------------------------------------------------------
    # Language Details
    # -----------------------------------------------------------------------
    content.append(dbc.Row([
        dbc.Col([create_table_card("Language Details", TABLE_ID_LANGUAGE_TABLE)], md=12),
    ], className="row-gap-sm"))

    return html.Div([
        dmc.MantineProvider([
            *filter_rows,
            dcc.Loading(content),
        ]),
    ], className="page-container")
