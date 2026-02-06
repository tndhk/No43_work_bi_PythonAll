"""Filter UI layout builder for APAC DOT Due Date Dashboard.

Extracts the filter UI construction logic from layout() into a
standalone, testable function.
"""
from dash import dcc
import dash_bootstrap_components as dbc

from src.components.filters import create_category_filter


def build_filter_layout(filter_options: dict) -> list[dbc.Row]:
    """Build the filter section of the APAC DOT Due Date layout.

    Args:
        filter_options: Dict returned by load_filter_options(), containing
            months, areas, workstreams, vendors, amp_vs_av, order_types,
            total_count, prc_count, non_prc_count.

    Returns:
        List of 5 dbc.Row components:
            [0] Control row (Num/% toggle + Break Down tabs)
            [1] Month filter row
            [2] PRC filter row
            [3] Category filters row (Area, Category, Vendor)
            [4] Additional filters row (AMP VS AV, Order Type)
    """
    months = filter_options["months"]
    areas = filter_options["areas"]
    workstreams = filter_options["workstreams"]
    vendors = filter_options["vendors"]
    amp_vs_av = filter_options["amp_vs_av"]
    order_types = filter_options["order_types"]
    total_count = filter_options["total_count"]

    # Row 0: Control Row - Num/% and Break Down
    control_row = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Num or %", className="filter-header"),
                dbc.CardBody([
                    dcc.RadioItems(
                        id="apac-dot-ctrl-num-percent",
                        options=[
                            {"label": " Num", "value": "num"},
                            {"label": " %", "value": "percent"},
                        ],
                        value="num",
                        inline=True,
                    ),
                ]),
            ], className="filter-card mb-3"),
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Break Down", className="filter-header"),
                dbc.CardBody([
                    dbc.Tabs(
                        id="apac-dot-ctrl-breakdown",
                        active_tab="area",
                        children=[
                            dbc.Tab(label="Area", tab_id="area"),
                            dbc.Tab(label="Category", tab_id="category"),
                            dbc.Tab(label="Vendor", tab_id="vendor"),
                        ],
                    ),
                ]),
            ], className="filter-card mb-3"),
        ], md=9),
    ])

    # Row 1: Filter Month
    month_row = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filter Month", className="filter-header"),
                dbc.CardBody([
                    dcc.Dropdown(
                        id="apac-dot-filter-month",
                        options=[{"label": m, "value": m} for m in months],
                        value=months,
                        multi=True,
                        placeholder=(
                            f"Select all ({len(months)})"
                            if len(months) == 26
                            else "Select months..."
                        ),
                    ),
                ]),
            ], className="filter-card mb-3"),
        ], md=12),
    ])

    # Row 2: PRC Filter
    prc_row = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("PRC", className="filter-header"),
                dbc.CardBody([
                    dcc.RadioItems(
                        id="apac-dot-filter-prc",
                        options=[
                            {"label": f" Select all ({total_count})", "value": "all"},
                            {"label": " PRC Only", "value": "prc_only"},
                            {"label": " PRC not Included", "value": "prc_not_included"},
                        ],
                        value="all",
                        inline=False,
                    ),
                ]),
            ], className="filter-card mb-3"),
        ], md=12),
    ])

    # Row 3: Category Filters (Area, Category, Vendor)
    category_row = dbc.Row([
        dbc.Col([
            create_category_filter(
                filter_id="apac-dot-filter-area",
                column_name="Area",
                options=areas,
                multi=True,
            ),
        ], md=3),
        dbc.Col([
            create_category_filter(
                filter_id="apac-dot-filter-category",
                column_name="Category",
                options=workstreams,
                multi=True,
            ),
        ], md=3),
        dbc.Col([
            create_category_filter(
                filter_id="apac-dot-filter-vendor",
                column_name="Vendor",
                options=vendors,
                multi=True,
            ),
        ], md=3),
    ])

    # Row 4: Additional Filters (AMP VS AV, Order Type)
    additional_row = dbc.Row([
        dbc.Col([
            create_category_filter(
                filter_id="apac-dot-filter-amp-av",
                column_name="AMP VS AV",
                options=amp_vs_av,
                multi=True,
            ),
        ], md=3),
        dbc.Col([
            create_category_filter(
                filter_id="apac-dot-filter-order-type",
                column_name="Order Type",
                options=order_types,
                multi=True,
            ),
        ], md=3),
    ])

    return [control_row, month_row, prc_row, category_row, additional_row]
