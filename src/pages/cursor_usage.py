"""Cursor Usage Dashboard page."""
import dash
from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.filter_engine import FilterSet, CategoryFilter, DateRangeFilter, apply_filters
from src.components.filters import create_date_range_filter, create_category_filter
from src.components.cards import create_kpi_card
from src.charts.templates import render_line_chart, render_bar_chart, render_pie_chart

dash.register_page(__name__, path="/cursor-usage", name="Cursor Usage", order=1)


def layout():
    """Cursor Usage Dashboard layout."""
    dataset_id = "cursor-usage"

    # Load data to get available options for filters
    reader = ParquetReader()
    try:
        df = get_cached_dataset(reader, dataset_id)

        # Extract date from ISO datetime string (strip timezone for filter compatibility)
        df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_convert(None)
        df["DateOnly"] = df["Date"].dt.date

        # Get unique models for filter
        models = sorted(df["Model"].unique().tolist())
        min_date = df["DateOnly"].min().isoformat()
        max_date = df["DateOnly"].max().isoformat()
    except Exception:
        # If data not loaded yet, use defaults
        models = []
        min_date = None
        max_date = None

    return html.Div([
        html.H1("Cursor Usage Dashboard", className="mb-4"),

        # Filters
        dbc.Row([
            dbc.Col([
                create_date_range_filter(
                    filter_id="date-filter",
                    column_name="Date Range",
                    min_date=min_date,
                    max_date=max_date,
                ),
            ], md=6),
            dbc.Col([
                create_category_filter(
                    filter_id="model-filter",
                    column_name="Model",
                    options=models,
                    multi=True,
                ),
            ], md=6),
        ], className="mb-4"),

        # KPI Cards
        dbc.Row([
            dbc.Col([
                html.Div(id="kpi-total-cost"),
            ], md=4),
            dbc.Col([
                html.Div(id="kpi-total-tokens"),
            ], md=4),
            dbc.Col([
                html.Div(id="kpi-request-count"),
            ], md=4),
        ], className="mb-4"),

        # Charts Row 1
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-cost-trend"),
            ], md=12),
        ], className="mb-4"),

        # Charts Row 2
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-token-efficiency"),
            ], md=6),
            dbc.Col([
                dcc.Graph(id="chart-model-distribution"),
            ], md=6),
        ], className="mb-4"),

        # Data Table
        dbc.Row([
            dbc.Col([
                html.H3("Detailed Data", className="mb-3"),
                html.Div(id="data-table"),
            ], md=12),
        ]),
    ], className="page-container")


@callback(
    [
        Output("kpi-total-cost", "children"),
        Output("kpi-total-tokens", "children"),
        Output("kpi-request-count", "children"),
        Output("chart-cost-trend", "figure"),
        Output("chart-token-efficiency", "figure"),
        Output("chart-model-distribution", "figure"),
        Output("data-table", "children"),
    ],
    [
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        Input("model-filter", "value"),
    ],
)
def update_dashboard(start_date, end_date, model_values):
    """Update dashboard components based on filters."""
    dataset_id = "cursor-usage"
    reader = ParquetReader()

    try:
        # Load data
        df = get_cached_dataset(reader, dataset_id)

        # Convert Date column to datetime (strip timezone for filter compatibility)
        df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_convert(None)
        df["DateOnly"] = df["Date"].dt.date

        # Build filters
        filters = FilterSet()

        if start_date and end_date:
            filters.date_filters.append(
                DateRangeFilter(
                    column="Date",
                    start_date=start_date,
                    end_date=end_date,
                )
            )

        if model_values:
            filters.category_filters.append(
                CategoryFilter(
                    column="Model",
                    values=model_values,
                )
            )

        # Apply filters
        filtered_df = apply_filters(df, filters)

        if len(filtered_df) == 0:
            # Empty state
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No data available for selected filters",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
            )
            empty_fig.update_layout(height=400)

            return (
                create_kpi_card("Total Cost", "$0.00"),
                create_kpi_card("Total Tokens", "0"),
                create_kpi_card("Request Count", "0"),
                empty_fig,
                empty_fig,
                empty_fig,
                html.P("No data available", className="text-muted"),
            )

        # Calculate KPIs
        total_cost = filtered_df["Cost"].sum()
        total_tokens = filtered_df["Total Tokens"].sum()
        request_count = len(filtered_df)

        # KPI Cards
        kpi_cost = create_kpi_card("Total Cost", f"${total_cost:.2f}")
        kpi_tokens = create_kpi_card("Total Tokens", f"{total_tokens:,}")
        kpi_requests = create_kpi_card("Request Count", f"{request_count:,}")

        # Chart 1: Daily Cost Trend
        daily_cost = filtered_df.groupby(filtered_df["Date"].dt.date)["Cost"].sum().reset_index()
        daily_cost.columns = ["Date", "Cost"]
        daily_cost = daily_cost.sort_values("Date")

        cost_trend_fig = render_line_chart(
            dataset=daily_cost,
            filters=None,
            params={
                "x_column": "Date",
                "y_column": "Cost",
            },
        )
        cost_trend_fig.update_layout(
            title="Daily Cost Trend",
            xaxis_title="Date",
            yaxis_title="Cost ($)",
        )

        # Chart 2: Token Efficiency by Model
        model_stats = filtered_df.groupby("Model").agg({
            "Total Tokens": "sum",
            "Cost": "sum",
        }).reset_index()
        model_stats["TokensPerCost"] = model_stats["Total Tokens"] / model_stats["Cost"]
        model_stats = model_stats.sort_values("TokensPerCost", ascending=False)

        efficiency_fig = render_bar_chart(
            dataset=model_stats,
            filters=None,
            params={
                "x_column": "Model",
                "y_column": "TokensPerCost",
            },
        )
        efficiency_fig.update_layout(
            title="Token Efficiency by Model (Tokens per $)",
            xaxis_title="Model",
            yaxis_title="Tokens per Cost",
        )

        # Chart 3: Model Distribution
        model_dist = filtered_df.groupby("Model")["Cost"].sum().reset_index()
        model_dist.columns = ["Model", "Cost"]

        distribution_fig = render_pie_chart(
            dataset=model_dist,
            filters=None,
            params={
                "names_column": "Model",
                "values_column": "Cost",
            },
        )
        distribution_fig.update_layout(
            title="Cost Distribution by Model",
        )

        # Data Table
        display_df = filtered_df[[
            "Date", "User", "Model", "Kind",
            "Total Tokens", "Cost"
        ]].copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d %H:%M")
        display_df = display_df.head(100)

        table_component = dash_table.DataTable(
            data=display_df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in display_df.columns],
            page_size=20,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px"},
            style_header={"fontWeight": "bold"},
        )

        return (
            kpi_cost,
            kpi_tokens,
            kpi_requests,
            cost_trend_fig,
            efficiency_fig,
            distribution_fig,
            table_component,
        )

    except Exception as e:
        # Error state
        error_msg = html.Div([
            html.P(f"Error loading data: {str(e)}", className="text-danger"),
        ])

        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
        )
        empty_fig.update_layout(height=400)

        return (
            create_kpi_card("Total Cost", "Error"),
            create_kpi_card("Total Tokens", "Error"),
            create_kpi_card("Request Count", "Error"),
            empty_fig,
            empty_fig,
            empty_fig,
            error_msg,
        )
