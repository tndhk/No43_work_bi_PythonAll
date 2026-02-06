"""APAC DOT Due Date Dashboard page."""
import dash
from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.filter_engine import FilterSet, CategoryFilter, apply_filters
from src.components.filters import create_category_filter

dash.register_page(__name__, path="/apac-dot-due-date", name="APAC DOT Due Date", order=2)


def layout():
    """APAC DOT Due Date Dashboard layout."""
    dataset_id = "apac-dot-due-date"

    # Load data to get available options for filters
    reader = ParquetReader()
    try:
        df = get_cached_dataset(reader, dataset_id)

        # Get unique values for filters
        months = sorted(df["Delivery Completed Month"].unique().tolist()) if "Delivery Completed Month" in df.columns else []
        areas = sorted(df["business area"].unique().tolist()) if "business area" in df.columns else []
        workstreams = sorted(df["Metric Workstream"].unique().tolist()) if "Metric Workstream" in df.columns else []
        vendors = sorted(df["Vendor: Account Name"].unique().tolist()) if "Vendor: Account Name" in df.columns else []
        amp_vs_av = sorted(df["AMP VS AV Scope"].unique().tolist()) if "AMP VS AV Scope" in df.columns else []
        order_types = sorted(df["order tags"].unique().tolist()) if "order tags" in df.columns else []
        
        # Count for PRC filter
        total_count = len(df)
        prc_count = len(df[df["job name"].str.contains("PRC", case=False, na=False)]) if "job name" in df.columns else 0
        non_prc_count = total_count - prc_count
    except Exception:
        # If data not loaded yet, use defaults
        months = []
        areas = []
        workstreams = []
        vendors = []
        amp_vs_av = []
        order_types = []
        total_count = 0
        prc_count = 0
        non_prc_count = 0

    return html.Div([
        html.H1("APAC DOT Due Date Dashboard", className="mb-4"),

        # Control Row: Num/% and Break Down
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Num or %", className="filter-header"),
                    dbc.CardBody([
                        dcc.RadioItems(
                            id="num-percent-toggle",
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
                            id="breakdown-tabs",
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
        ]),

        # Filter Month Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filter Month", className="filter-header"),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id="filter-month",
                            options=[{"label": m, "value": m} for m in months],
                            value=months,  # Default: all selected
                            multi=True,
                            placeholder="Select all (26)" if len(months) == 26 else "Select months...",
                        ),
                    ]),
                ], className="filter-card mb-3"),
            ], md=12),
        ]),

        # PRC Filter Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("PRC", className="filter-header"),
                    dbc.CardBody([
                        dcc.RadioItems(
                            id="prc-filter",
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
        ]),

        # Category Filters Row
        dbc.Row([
            dbc.Col([
                create_category_filter(
                    filter_id="area-filter",
                    column_name="Area",
                    options=areas,
                    multi=True,
                ),
            ], md=3),
            dbc.Col([
                create_category_filter(
                    filter_id="category-filter",
                    column_name="Category",
                    options=workstreams,
                    multi=True,
                ),
            ], md=3),
            dbc.Col([
                create_category_filter(
                    filter_id="vendor-filter",
                    column_name="Vendor",
                    options=vendors,
                    multi=True,
                ),
            ], md=3),
        ]),

        # Additional Filters Row
        dbc.Row([
            dbc.Col([
                create_category_filter(
                    filter_id="amp-av-filter",
                    column_name="AMP VS AV",
                    options=amp_vs_av,
                    multi=True,
                ),
            ], md=3),
            dbc.Col([
                create_category_filter(
                    filter_id="order-type-filter",
                    column_name="Order Type",
                    options=order_types,
                    multi=True,
                ),
            ], md=3),
        ]),

        # Reference / Table Section
        dbc.Row([
            dbc.Col([
                html.H3(id="table-title", className="mt-4 mb-3"),
                html.Div(id="apac-table"),
            ], md=12),
        ]),
    ], className="page-container")


@callback(
    [
        Output("table-title", "children"),
        Output("apac-table", "children"),
    ],
    [
        Input("num-percent-toggle", "value"),
        Input("breakdown-tabs", "active_tab"),
        Input("filter-month", "value"),
        Input("prc-filter", "value"),
        Input("area-filter", "value"),
        Input("category-filter", "value"),
        Input("vendor-filter", "value"),
        Input("amp-av-filter", "value"),
        Input("order-type-filter", "value"),
    ],
)
def update_table(
    num_percent_mode,
    breakdown_tab,
    selected_months,
    prc_filter_value,
    area_values,
    category_values,
    vendor_values,
    amp_av_values,
    order_type_values,
):
    """Update table based on filters."""
    dataset_id = "apac-dot-due-date"
    reader = ParquetReader()

    try:
        # Load data
        df = get_cached_dataset(reader, dataset_id)

        # Build filters
        filters = FilterSet()

        # Month filter
        if selected_months:
            filters.category_filters.append(
                CategoryFilter(
                    column="Delivery Completed Month",
                    values=selected_months,
                )
            )

        # PRC filter (custom logic)
        if prc_filter_value == "prc_only":
            df = df[df["job name"].str.contains("PRC", case=False, na=False)]
        elif prc_filter_value == "prc_not_included":
            df = df[~df["job name"].str.contains("PRC", case=False, na=False)]

        # Area filter
        if area_values:
            filters.category_filters.append(
                CategoryFilter(column="business area", values=area_values)
            )

        # Category filter
        if category_values:
            filters.category_filters.append(
                CategoryFilter(column="Metric Workstream", values=category_values)
            )

        # Vendor filter
        if vendor_values:
            filters.category_filters.append(
                CategoryFilter(column="Vendor: Account Name", values=vendor_values)
            )

        # AMP VS AV filter
        if amp_av_values:
            filters.category_filters.append(
                CategoryFilter(column="AMP VS AV Scope", values=amp_av_values)
            )

        # Order Type filter
        if order_type_values:
            filters.category_filters.append(
                CategoryFilter(column="order tags", values=order_type_values)
            )

        # Apply filters
        filtered_df = apply_filters(df, filters)

        if len(filtered_df) == 0:
            # Empty state
            return (
                "0) Reference : Number of Work Order",
                html.P("No data available for selected filters", className="text-muted"),
            )

        # Determine breakdown column
        breakdown_column_map = {
            "area": "business area",
            "category": "Metric Workstream",
            "vendor": "Vendor: Account Name",
        }
        breakdown_column = breakdown_column_map[breakdown_tab]

        # Group by breakdown column and month, count unique work order IDs
        pivot_data = filtered_df.groupby(
            [breakdown_column, "Delivery Completed Month"]
        )["work order id"].nunique().reset_index()

        # Create pivot table
        pivot_table = pivot_data.pivot(
            index=breakdown_column,
            columns="Delivery Completed Month",
            values="work order id",
        ).fillna(0)

        # Sort columns (months) chronologically
        pivot_table = pivot_table.reindex(sorted(pivot_table.columns), axis=1)
        
        # Convert Timestamp column names to strings for JSON serialization
        pivot_table.columns = [col.strftime("%Y-%m-%d") if hasattr(col, 'strftime') else str(col) for col in pivot_table.columns]

        # Add GRAND TOTAL row
        pivot_table.loc["GRAND TOTAL"] = pivot_table.sum()

        # Add Average column
        pivot_table["AVG"] = pivot_table.mean(axis=1).round(0)

        # Convert to percentage if needed
        if num_percent_mode == "percent":
            # Calculate percentage based on GRAND TOTAL for each column
            grand_total_row = pivot_table.loc["GRAND TOTAL"].copy()
            for col in pivot_table.columns:
                if col != "AVG":
                    pivot_table[col] = (pivot_table[col] / grand_total_row[col] * 100).round(1)
            # Recalculate AVG for percentage mode
            pivot_table["AVG"] = pivot_table.drop(columns=["AVG"]).mean(axis=1).round(1)

        # Reset index to make breakdown column a regular column
        pivot_table = pivot_table.reset_index()
        pivot_table.columns.name = None

        # Prepare data for DataTable
        columns = [{"name": col, "id": col} for col in pivot_table.columns]
        data = pivot_table.to_dict("records")

        # Create DataTable
        table_component = dash_table.DataTable(
            data=data,
            columns=columns,
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "padding": "8px",
                "fontSize": "14px",
            },
            style_header={
                "fontWeight": "bold",
                "backgroundColor": "#4A5568",
                "color": "white",
            },
            style_data_conditional=[
                {
                    "if": {"filter_query": f'{{{breakdown_column}}} = "GRAND TOTAL"'},
                    "fontWeight": "bold",
                    "backgroundColor": "#EDF2F7",
                }
            ],
        )

        # Table title
        table_title = f"0) Reference : Number of Work Order"

        return (table_title, table_component)

    except Exception as e:
        # Error state
        error_msg = html.Div([
            html.P(f"Error loading data: {str(e)}", className="text-danger"),
        ])

        return (
            "0) Reference : Number of Work Order",
            error_msg,
        )
