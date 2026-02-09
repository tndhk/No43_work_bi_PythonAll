"""Filter UI layout builder for Cursor Usage Dashboard.

Extracts the filter UI construction logic from layout() into a
standalone, testable function.
"""
import dash_bootstrap_components as dbc

from src.components.filters import create_date_range_filter, create_category_filter
from ._constants import ID_PREFIX


def build_filter_layout(opts: dict) -> list:
    """Build the filter section of the Cursor Usage layout.

    Args:
        opts: Dict returned by load_filter_options(), containing
            min_date, max_date, models, users, kinds.

    Returns:
        List of 2 dbc.Row components:
            [0] Top row (Date Range + Model + User)
            [1] Bottom row (Kind)
    """
    # Row 0: Date, Model, User
    top_row = dbc.Row([
        dbc.Col([
            create_date_range_filter(
                filter_id=f"{ID_PREFIX}filter-date",
                column_name="Date Range",
                min_date=opts["min_date"],
                max_date=opts["max_date"],
            ),
        ], md=4),
        dbc.Col([
            create_category_filter(
                filter_id=f"{ID_PREFIX}filter-model",
                column_name="Model",
                options=opts["models"],
                multi=True,
            ),
        ], md=4),
        dbc.Col([
            create_category_filter(
                filter_id=f"{ID_PREFIX}filter-user",
                column_name="User",
                options=opts["users"],
                multi=True,
            ),
        ], md=4),
    ], className="mb-3")

    # Row 1: Kind
    bottom_row = dbc.Row([
        dbc.Col([
            create_category_filter(
                filter_id=f"{ID_PREFIX}filter-kind",
                column_name="Kind",
                options=opts["kinds"],
                multi=True,
            ),
        ], md=4),
    ], className="mb-4")

    return [top_row, bottom_row]
