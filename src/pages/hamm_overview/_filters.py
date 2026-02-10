"""Filter components for HAMM Overview dashboard.

Auto-generated from page_spec.yaml by tools.page_generator.
"""
from dash import html
from src.components.filters import (
    create_slicer_filter,
    create_category_filter,
)
from ._constants import (
    FILTER_ID_FILTER_REGION,
    FILTER_ID_FILTER_YEAR,
    FILTER_ID_FILTER_CONTENT_TYPE,
    FILTER_ID_FILTER_ORIGINAL_LANGUAGE,
    FILTER_ID_FILTER_DIALOGUE,
    FILTER_ID_FILTER_GENRE,
    FILTER_ID_FILTER_ERROR_TYPE,
    FILTER_ID_FILTER_MONTH,
    FILTER_ID_FILTER_TASK_ID,
    FILTER_ID_FILTER_ERROR_CODE,
    CTRL_ID_CLEAR_REGION,
    CTRL_ID_CLEAR_YEAR,
    CTRL_ID_CLEAR_CONTENT_TYPE,
    CTRL_ID_CLEAR_ORIGINAL_LANGUAGE,
    CTRL_ID_CLEAR_DIALOGUE,
    CTRL_ID_CLEAR_GENRE,
    CTRL_ID_CLEAR_ERROR_TYPE,
)


def build_filter_layout(opts: dict, title_element=None) -> list:
    """Build filter layout rows.

    Args:
        opts: Dictionary of filter options
        title_element: Optional title element to prepend to first row

    Returns:
        List of filter row elements
    """

    # Row 1 slicer filters (3 filters + title)
    row1_filters = [
        create_slicer_filter(
            filter_id=FILTER_ID_FILTER_REGION,
            column_name="Region",
            options=opts["regions"],
            clear_button_id=CTRL_ID_CLEAR_REGION,
        ),
        create_slicer_filter(
            filter_id=FILTER_ID_FILTER_YEAR,
            column_name="Year",
            options=opts["years"],
            clear_button_id=CTRL_ID_CLEAR_YEAR,
        ),
        create_slicer_filter(
            filter_id=FILTER_ID_FILTER_CONTENT_TYPE,
            column_name="Content Type",
            options=opts["content_types"],
            clear_button_id=CTRL_ID_CLEAR_CONTENT_TYPE,
        ),
    ]

    if title_element is not None:
        first_row = html.Div(
            [title_element] + row1_filters,
            className="mb-3 filter-row-title-3filters",
        )
    else:
        first_row = html.Div(
            row1_filters,
            className="mb-3 filter-row-title-3filters",
        )

    # Row 2: 7 columns (4 slicer filters + 3 category filters)
    row2_items = [
        create_slicer_filter(
            filter_id=FILTER_ID_FILTER_ORIGINAL_LANGUAGE,
            column_name="Original Language",
            options=opts["original_languages"],
            clear_button_id=CTRL_ID_CLEAR_ORIGINAL_LANGUAGE,
        ),
        create_slicer_filter(
            filter_id=FILTER_ID_FILTER_DIALOGUE,
            column_name="Was Dialogue Provided?",
            options=opts["dialogue_options"],
            clear_button_id=CTRL_ID_CLEAR_DIALOGUE,
        ),
        create_slicer_filter(
            filter_id=FILTER_ID_FILTER_GENRE,
            column_name="Genre",
            options=opts["genres"],
            clear_button_id=CTRL_ID_CLEAR_GENRE,
        ),
        create_slicer_filter(
            filter_id=FILTER_ID_FILTER_ERROR_TYPE,
            column_name="Error Type",
            options=opts["error_types"],
            clear_button_id=CTRL_ID_CLEAR_ERROR_TYPE,
        ),
        create_category_filter(
            filter_id=FILTER_ID_FILTER_MONTH,
            column_name="Month",
            options=opts["months"],
        ),
        create_category_filter(
            filter_id=FILTER_ID_FILTER_TASK_ID,
            column_name="Task ID",
            options=opts["task_ids"],
            multi=True,
        ),
        create_category_filter(
            filter_id=FILTER_ID_FILTER_ERROR_CODE,
            column_name="Error Code",
            options=opts["error_codes"],
        ),
    ]

    second_row = html.Div(
        row2_items,
        className="mb-3 filter-row-7col",
    )

    return [first_row, second_row]
