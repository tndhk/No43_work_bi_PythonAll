"""Cursor Usage Dashboard callbacks module."""
from dash import html, callback, Input, Output, dash_table
import plotly.graph_objects as go

from src.data.parquet_reader import ParquetReader
from src.components.cards import create_kpi_card
from src.charts.templates import render_line_chart, render_bar_chart, render_pie_chart
from ._constants import (
    CHART_ID_KPI_TOTAL_COST,
    CHART_ID_KPI_TOTAL_TOKENS,
    CHART_ID_KPI_REQUEST_COUNT,
    CHART_ID_COST_TREND,
    CHART_ID_TOKEN_EFFICIENCY,
    CHART_ID_MODEL_DISTRIBUTION,
    CHART_ID_DATA_TABLE,
    COLUMN_MAP,
    ID_PREFIX,
)
from ._data_loader import load_and_filter_data, resolve_dataset_id_for_dashboard


@callback(
    [
        Output(CHART_ID_KPI_TOTAL_COST, "children"),
        Output(CHART_ID_KPI_TOTAL_TOKENS, "children"),
        Output(CHART_ID_KPI_REQUEST_COUNT, "children"),
        Output(CHART_ID_COST_TREND, "figure"),
        Output(CHART_ID_TOKEN_EFFICIENCY, "figure"),
        Output(CHART_ID_MODEL_DISTRIBUTION, "figure"),
        Output(CHART_ID_DATA_TABLE, "children"),
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
        dataset_id = resolve_dataset_id_for_dashboard()

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

        date_col = COLUMN_MAP["date"]
        cost_col = COLUMN_MAP["cost"]
        total_tokens_col = COLUMN_MAP["total_tokens"]
        model_col = COLUMN_MAP["model"]
        user_col = COLUMN_MAP["user"]
        kind_col = COLUMN_MAP["kind"]

        # Calculate KPIs
        total_cost = filtered_df[cost_col].sum()
        total_tokens = filtered_df[total_tokens_col].sum()
        request_count = len(filtered_df)

        # KPI Cards
        kpi_cost = create_kpi_card("Total Cost", f"${total_cost:.2f}")
        kpi_tokens = create_kpi_card("Total Tokens", f"{total_tokens:,}")
        kpi_requests = create_kpi_card("Request Count", f"{request_count:,}")

        # Chart 1: Daily Cost Trend
        daily_cost = filtered_df.groupby(filtered_df[date_col].dt.date)[cost_col].sum().reset_index()
        daily_cost.columns = [date_col, cost_col]
        daily_cost = daily_cost.sort_values(date_col)

        cost_trend_fig = render_line_chart(
            dataset=daily_cost,
            filters=None,
            params={
                "x_column": date_col,
                "y_column": cost_col,
            },
        )
        cost_trend_fig.update_layout(
            title="Daily Cost Trend",
            xaxis_title="Date",
            yaxis_title="Cost ($)",
        )

        # Chart 2: Token Efficiency by Model
        model_stats = filtered_df.groupby(model_col).agg({
            total_tokens_col: "sum",
            cost_col: "sum",
        }).reset_index()
        model_stats["TokensPerCost"] = model_stats[total_tokens_col] / model_stats[cost_col]
        model_stats = model_stats.sort_values("TokensPerCost", ascending=False)

        efficiency_fig = render_bar_chart(
            dataset=model_stats,
            filters=None,
            params={
                "x_column": model_col,
                "y_column": "TokensPerCost",
            },
        )
        efficiency_fig.update_layout(
            title="Token Efficiency by Model (Tokens per $)",
            xaxis_title="Model",
            yaxis_title="Tokens per Cost",
        )

        # Chart 3: Model Distribution
        model_dist = filtered_df.groupby(model_col)[cost_col].sum().reset_index()
        model_dist.columns = [model_col, cost_col]

        distribution_fig = render_pie_chart(
            dataset=model_dist,
            filters=None,
            params={
                "names_column": model_col,
                "values_column": cost_col,
            },
        )
        distribution_fig.update_layout(
            title="Cost Distribution by Model",
        )

        # Data Table
        display_df = filtered_df[[
            date_col, user_col, model_col, kind_col,
            total_tokens_col, cost_col
        ]].copy()
        display_df[date_col] = display_df[date_col].dt.strftime("%Y-%m-%d %H:%M")
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
