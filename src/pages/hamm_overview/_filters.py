"""Filter components for HAMM Overview dashboard."""
from dash import html
from src.components.filters import create_slicer_filter, create_category_filter
from ._constants import (
    FILTER_ID_FILTER_REGION,
    CTRL_ID_FILTER_REGION_CLEAR,
    FILTER_ID_FILTER_YEAR,
    CTRL_ID_FILTER_YEAR_CLEAR,
    FILTER_ID_FILTER_MONTH,
)


def build_filter_layout(opts: dict, title_element=None) -> list:
    """Build filter layout rows."""
    title_row_items = []

    title_row_items.append(
        create_slicer_filter(
            filter_id=FILTER_ID_FILTER_REGION,
            column_name="Region",
            options=opts["region"],
            clear_button_id=CTRL_ID_FILTER_REGION_CLEAR,
        )
    )

    title_row_items.append(
        create_slicer_filter(
            filter_id=FILTER_ID_FILTER_YEAR,
            column_name="Year",
            options=opts["_year"],
            clear_button_id=CTRL_ID_FILTER_YEAR_CLEAR,
        )
    )

    if title_element is not None:
        title_row_items = [title_element] + title_row_items

    title_row = html.Div(
        title_row_items,
        className="mb-3 filter-row-title-2filters",
    )

    detail_row_items = []
    detail_row_items.append(
        create_category_filter(
            filter_id=FILTER_ID_FILTER_MONTH,
            column_name="Month",
            options=opts["_month"],
        )
    )

    detail_row = html.Div(
        detail_row_items,
        className="mb-3 filter-row-1col",
    )

    return [title_row, detail_row]
