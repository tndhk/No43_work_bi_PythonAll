"""Cursor Usage Dashboard callbacks module.

Thin orchestration layer: data loading -> aggregation -> shared builders.
All chart/table rendering uses the shared build_chart / build_table
infrastructure with declarative Specs defined in _constants.py.
"""
from dash import callback, Input, Output

from src.data.parquet_reader import ParquetReader
from src.components.cards import create_kpi_card
from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.empty_states import create_empty_figure, create_error_figure, create_empty_table
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
    COST_TREND_SPEC,
    TOKEN_EFFICIENCY_SPEC,
    MODEL_DISTRIBUTION_SPEC,
    DETAIL_TABLE_SPEC,
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
        Input(f"{ID_PREFIX}filter-user", "value"),
        Input(f"{ID_PREFIX}filter-kind", "value"),
    ],
)
def update_dashboard(start_date, end_date, model_values, user_values, kind_values):
    """Update dashboard components based on filters.

    Args:
        start_date: Start date from date range filter (ISO string or None)
        end_date: End date from date range filter (ISO string or None)
        model_values: Selected models from dropdown (list or None)
        user_values: Selected users from dropdown (list or None)
        kind_values: Selected kinds from dropdown (list or None)

    Returns:
        Tuple of (kpi_cost, kpi_tokens, kpi_requests, cost_trend_fig,
                  efficiency_fig, distribution_fig, table_component)
    """
    reader = ParquetReader()

    try:
        # Load and filter data
        dataset_id = resolve_dataset_id_for_dashboard()

        filtered_df = load_and_filter_data(
            reader, dataset_id, start_date, end_date, model_values, user_values, kind_values
        )

        if len(filtered_df) == 0:
            # Empty state using shared functions
            empty_fig = create_empty_figure(
                message="No data available for selected filters"
            )

            return (
                create_kpi_card("Total Cost", "$0.00"),
                create_kpi_card("Total Tokens", "0"),
                create_kpi_card("Request Count", "0"),
                empty_fig,
                empty_fig,
                empty_fig,
                create_empty_table(),
            )

        date_col = COLUMN_MAP["date"]
        cost_col = COLUMN_MAP["cost"]
        total_tokens_col = COLUMN_MAP["total_tokens"]
        model_col = COLUMN_MAP["model"]

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

        cost_trend_fig = build_chart(daily_cost, COST_TREND_SPEC)

        # Chart 2: Token Efficiency by Model
        model_stats = filtered_df.groupby(model_col).agg({
            total_tokens_col: "sum",
            cost_col: "sum",
        }).reset_index()
        model_stats["TokensPerCost"] = model_stats[total_tokens_col] / model_stats[cost_col]
        model_stats = model_stats.sort_values("TokensPerCost", ascending=False)

        efficiency_fig = build_chart(model_stats, TOKEN_EFFICIENCY_SPEC)

        # Chart 3: Model Distribution
        model_dist = filtered_df.groupby(model_col)[cost_col].sum().reset_index()
        model_dist.columns = [model_col, cost_col]

        distribution_fig = build_chart(model_dist, MODEL_DISTRIBUTION_SPEC)

        # Data Table
        display_df = filtered_df.copy()
        display_df[date_col] = display_df[date_col].dt.strftime("%Y-%m-%d %H:%M")
        display_df = display_df.head(100)

        _, table_component = build_table(display_df, DETAIL_TABLE_SPEC)

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
        # Error state using shared functions
        error_fig = create_error_figure(error=str(e))

        return (
            create_kpi_card("Total Cost", "Error"),
            create_kpi_card("Total Tokens", "Error"),
            create_kpi_card("Request Count", "Error"),
            error_fig,
            error_fig,
            error_fig,
            create_empty_table(message=f"Error loading data: {str(e)}"),
        )
