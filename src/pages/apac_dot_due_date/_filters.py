"""Filter UI layout builder for APAC DOT Due Date Dashboard.

Extracts the filter UI construction logic from layout() into a
standalone, testable function.
"""
from dash import dcc
import dash_bootstrap_components as dbc

from src.components.filters import create_slicer_filter
from ._constants import (
    CTRL_ID_NUM_PERCENT,
    CTRL_ID_BREAKDOWN,
    CTRL_ID_CLEAR_MONTH,
    CTRL_ID_CLEAR_PRC,
    CTRL_ID_CLEAR_AREA,
    CTRL_ID_CLEAR_CATEGORY,
    CTRL_ID_CLEAR_VENDOR,
    CTRL_ID_CLEAR_AMP_AV,
    CTRL_ID_CLEAR_ORDER_TYPE,
    FILTER_ID_MONTH,
    FILTER_ID_PRC,
    FILTER_ID_AREA,
    FILTER_ID_CATEGORY,
    FILTER_ID_VENDOR,
    FILTER_ID_AMP_AV,
    FILTER_ID_ORDER_TYPE,
)

def build_filter_layout(filter_options: dict) -> list:
    """Build the filter section of the APAC DOT Due Date layout.

    Args:
        filter_options: Dict returned by load_filter_options(), containing
            months, areas, workstreams, vendors, amp_vs_av, order_types,
            total_count, prc_count, non_prc_count.

    Returns:
        List of 2 dbc.Row components:
            [0] Top row (Num/% + Break Down + Filter Month + PRC)
            [1] Bottom row (Area + Category + Vendor + AMP VS AV + Order Type)
    """
    months = filter_options["months"]
    areas = filter_options["areas"]
    workstreams = filter_options["workstreams"]
    vendors = filter_options["vendors"]
    amp_vs_av = filter_options["amp_vs_av"]
    order_types = filter_options["order_types"]

    # Row 0: Top controls
    top_row = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Num or %", className="filter-header"),
                dbc.CardBody([
                    dcc.RadioItems(
                        id=CTRL_ID_NUM_PERCENT,
                        options=[
                            {"label": " Num", "value": "num"},
                            {"label": " %", "value": "percent"},
                        ],
                        value="num",
                        inline=True,
                    ),
                ]),
            ], className="filter-card mb-3"),
        ], md=2),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Break Down", className="filter-header"),
                dbc.CardBody([
                    dcc.RadioItems(
                        id=CTRL_ID_BREAKDOWN,
                        options=[
                            {"label": " Area", "value": "area"},
                            {"label": " Category", "value": "category"},
                            {"label": " Vendor", "value": "vendor"},
                        ],
                        value="area",
                        inline=True,
                    ),
                ]),
            ], className="filter-card mb-3"),
        ], md=2),
        dbc.Col([
            create_slicer_filter(
                filter_id=FILTER_ID_MONTH,
                column_name="Filter Month",
                options=months,
                multi=True,
                default_value=None,
                clear_button_id=CTRL_ID_CLEAR_MONTH,
            ),
        ], md=5),
        dbc.Col([
            create_slicer_filter(
                filter_id=FILTER_ID_PRC,
                column_name="PRC",
                options=[
                    {"label": "PRC Only", "value": "prc_only"},
                    {"label": "PRC not Included", "value": "prc_not_included"},
                ],
                multi=False,
                default_value="prc_not_included",
                clear_button_id=CTRL_ID_CLEAR_PRC,
            ),
        ], md=3),
    ], className="apac-dot-filter-row-top")

    # Row 1: Bottom category filters
    bottom_row = dbc.Row([
        dbc.Col([
            create_slicer_filter(
                filter_id=FILTER_ID_AREA,
                column_name="Area",
                options=areas,
                multi=True,
                default_value=None,
                clear_button_id=CTRL_ID_CLEAR_AREA,
            ),
        ], md=2),
        dbc.Col([
            create_slicer_filter(
                filter_id=FILTER_ID_CATEGORY,
                column_name="Category",
                options=workstreams,
                multi=True,
                default_value=None,
                clear_button_id=CTRL_ID_CLEAR_CATEGORY,
            ),
        ], md=2),
        dbc.Col([
            create_slicer_filter(
                filter_id=FILTER_ID_VENDOR,
                column_name="Vendor",
                options=vendors,
                multi=True,
                default_value=None,
                clear_button_id=CTRL_ID_CLEAR_VENDOR,
            ),
        ], md=3),
        dbc.Col([
            create_slicer_filter(
                filter_id=FILTER_ID_AMP_AV,
                column_name="AMP VS AV",
                options=amp_vs_av,
                multi=True,
                default_value=None,
                clear_button_id=CTRL_ID_CLEAR_AMP_AV,
            ),
        ], md=2),
        dbc.Col([
            create_slicer_filter(
                filter_id=FILTER_ID_ORDER_TYPE,
                column_name="Order Type",
                options=order_types,
                multi=True,
                default_value=None,
                clear_button_id=CTRL_ID_CLEAR_ORDER_TYPE,
            ),
        ], md=3),
    ], className="apac-dot-filter-row-bottom")

    return [top_row, bottom_row]
