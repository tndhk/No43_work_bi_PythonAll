"""Filter UI layout builder for Hamm Overview dashboard."""
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from src.components.filters import create_category_filter, create_slicer_filter
from ._constants import (
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


def build_cadence_filter() -> dbc.Card:
    """Build the Cadence chip-group filter card."""
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


def build_filter_layout(opts: dict, title_element=None) -> list:
    """Build the filter section rows for Hamm Overview layout.

    Args:
        opts: Dict returned by load_filter_options(), containing
            regions, years, months, task_ids, content_types,
            original_languages, dialogue_options, genres,
            error_codes, error_types.
        title_element: Optional element to prepend to the first row
            (e.g. the dashboard title div).

    Returns:
        List of 2 html.Div components:
            [0] Title row (with optional title_element) + Region, Year,
                Month filters  (className="filter-row-title-3filters")
            [1] Detail row with 7 category/slicer filters
                (className="filter-row-7col")
    """
    # -- Row 0: title + 3 primary filters ----------------------------
    filters_row1 = [
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
    ]

    if title_element is not None:
        filters_row1 = [title_element] + filters_row1

    title_row = html.Div(
        filters_row1,
        className="mb-3 filter-row-title-3filters",
    )

    # -- Row 1: 7 detail filters ------------------------------------
    detail_row = html.Div([
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
    ], className="mb-3 filter-row-7col")

    return [title_row, detail_row]
