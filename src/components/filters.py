"""Filter UI components."""
from dash import dcc
import dash_bootstrap_components as dbc


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
        dbc.CardHeader(column_name),
        dbc.CardBody([
            dcc.Dropdown(
                id=filter_id,
                options=[{"label": opt, "value": opt} for opt in options],
                multi=multi,
                placeholder=f"Select {column_name}...",
            ),
        ]),
    ], className="mb-3")


def create_date_range_filter(
    filter_id: str,
    column_name: str,
    min_date: str | None = None,
    max_date: str | None = None,
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
        dbc.CardHeader(column_name),
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
    ], className="mb-3")
