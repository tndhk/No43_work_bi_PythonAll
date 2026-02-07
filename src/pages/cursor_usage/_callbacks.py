"""Cursor Usage Dashboard callbacks module."""
from dash import html, callback, Input, Output, dash_table
import plotly.graph_objects as go

from src.data.parquet_reader import ParquetReader
from src.data.data_source_registry import resolve_dataset_id
from src.components.cards import create_kpi_card
from src.charts.templates import render_line_chart, render_bar_chart, render_pie_chart
from ._constants import DASHBOARD_ID, CHART_ID_COST_TREND, ID_PREFIX
from ._data_loader import load_and_filter_data


@callback(
    [
        Output(f"{ID_PREFIX}kpi-total-cost", "children"),
        Output(f"{ID_PREFIX}kpi-total-tokens", "children"),
        Output(f"{ID_PREFIX}kpi-request-count", "children"),
        Output(f"{ID_PREFIX}chart-cost-trend", "figure"),
        Output(f"{ID_PREFIX}chart-token-efficiency", "figure"),
        Output(f"{ID_PREFIX}chart-model-distribution", "figure"),
        Output(f"{ID_PREFIX}data-table", "children"),
    ],
    [
        Input(f"{ID_PREFIX}filter-date", "start_date"),
        Input(f"{ID_PREFIX}filter-date", "end_date"),
        Input(f"{ID_PREFIX}filter-model", "value"),
    ],
)
def update_dashboard(start_date, end_date, model_values):
    """Update dashboard components based on filters.

    Args:
        start_date: Start date from date range filter (ISO string or None)
        end_date: End date from date range filter (ISO string or None)
        model_values: Selected models from dropdown (list or None)

    Returns:
        Tuple of (kpi_cost, kpi_tokens, kpi_requests, cost_trend_fig,
                  efficiency_fig, distribution_fig, table_component)
    """
    reader = ParquetReader()

    try:
        # Load and filter data
        dataset_id = resolve_dataset_id(DASHBOARD_ID, CHART_ID_COST_TREND)

        filtered_df = load_and_filter_data(
            reader, dataset_id, start_date, end_date, model_values
        )

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
