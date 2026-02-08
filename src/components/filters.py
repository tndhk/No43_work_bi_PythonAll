"""Filter UI components."""
from typing import Optional
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc


def create_category_filter(
    filter_id: str,
    column_name: str,
    options: list[str],
    multi: bool = True,
) -> dbc.Card:
    """
    Create a category filter (Dropdown) component.

    Args:
        filter_id: Component ID (for callbacks)
        column_name: Target column name (for label display)
        options: List of options
        multi: Allow multiple selection

    Returns:
        Card-wrapped filter component
    """
    return dbc.Card([
        dbc.CardHeader(column_name, className="filter-header"),
        dbc.CardBody([
            dcc.Dropdown(
                id=filter_id,
                options=[{"label": opt, "value": opt} for opt in options],
                multi=multi,
                placeholder=f"Select {column_name}...",
            ),
        ]),
    ], className="filter-card mb-3")


def create_date_range_filter(
    filter_id: str,
    column_name: str,
    min_date: Optional[str] = None,
    max_date: Optional[str] = None,
) -> dbc.Card:
    """
    Create a date range filter (DatePickerRange) component.

    Args:
        filter_id: Component ID (for callbacks)
        column_name: Target column name (for label display)
        min_date: Minimum selectable date (ISO 8601)
        max_date: Maximum selectable date (ISO 8601)

    Returns:
        Card-wrapped filter component
    """
    return dbc.Card([
        dbc.CardHeader(column_name, className="filter-header"),
        dbc.CardBody([
            dcc.DatePickerRange(
                id=filter_id,
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=min_date,
                end_date=max_date,
                display_format="YYYY-MM-DD",
            ),
        ]),
    ], className="filter-card mb-3")


def create_slicer_filter(
    filter_id: str,
    column_name: str,
    options: list,
    multi: bool = True,
    default_value: Optional[object] = None,
    clear_button_id: Optional[str] = None,
) -> dbc.Card:
    """
    Create a slicer-style filter using Mantine ChipGroup.

    Args:
        filter_id: Component ID (for callbacks)
        column_name: Target column name (for label display)
        options: List of option labels or list of {"label","value"} dicts
        multi: Allow multiple selection (default True)
        default_value: Default selected value(s)
        clear_button_id: Optional clear button ID shown in header

    Returns:
        Card-wrapped slicer filter component
    """
    chips = []
    for opt in options:
        if isinstance(opt, dict):
            label = str(opt.get("label", opt.get("value", "")))
            value = str(opt.get("value", label))
        else:
            label = str(opt)
            value = str(opt)
        chips.append(dmc.Chip(label, value=value, size="sm", variant="outline"))

    if multi:
        if default_value is None:
            chip_value = []
        elif isinstance(default_value, list):
            chip_value = default_value
        else:
            chip_value = [default_value]
    else:
        if isinstance(default_value, list):
            chip_value = default_value[0] if default_value else None
        else:
            chip_value = default_value

    header_children = column_name
    if clear_button_id:
        header_children = html.Div([
            html.Span(column_name),
            dbc.Button(
                "Clear",
                id=clear_button_id,
                color="link",
                size="sm",
                className="p-0 slicer-clear-btn",
            ),
        ], className="d-flex justify-content-between align-items-center w-100")

    return dbc.Card([
        dbc.CardHeader(header_children, className="filter-header"),
        dbc.CardBody([
            html.Div(
                dmc.ChipGroup(
                    id=filter_id,
                    children=chips,
                    value=chip_value,
                    multiple=multi,
                ),
                style={"display": "flex", "flexWrap": "wrap", "gap": "4px"},
            ),
        ]),
    ], className="filter-card slicer-filter mb-3")
