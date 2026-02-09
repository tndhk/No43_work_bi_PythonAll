"""Cursor Usage Dashboard callbacks module.

Thin orchestration layer: data loading -> aggregation -> shared builders.
All chart/table rendering uses the shared build_chart / build_table
infrastructure with declarative Specs defined in _constants.py.
"""
from dash import callback, Input, Output

from src.data.parquet_reader import ParquetReader
from src.components.cards import create_kpi_card
from src.charts.empty_states import create_empty_figure, create_error_figure, create_empty_table
from src.utils.callback_helpers import register_clear_callbacks
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
    CLEAR_PAIRS,
)
from ._data_loader import load_and_filter_data, resolve_dataset_id_for_dashboard
from ._chart_builders import (
    build_daily_cost_trend,
    build_token_efficiency_chart,
    build_model_distribution_chart,
    build_detail_table,
)


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

        cost_col = COLUMN_MAP["cost"]
        total_tokens_col = COLUMN_MAP["total_tokens"]

        # Calculate KPIs
        total_cost = filtered_df[cost_col].sum()
        total_tokens = filtered_df[total_tokens_col].sum()
        request_count = len(filtered_df)

        # KPI Cards
        kpi_cost = create_kpi_card("Total Cost", f"${total_cost:.2f}")
        kpi_tokens = create_kpi_card("Total Tokens", f"{total_tokens:,}")
        kpi_requests = create_kpi_card("Request Count", f"{request_count:,}")

        # Build charts using chart_builders
        cost_trend_fig = build_daily_cost_trend(filtered_df)
        efficiency_fig = build_token_efficiency_chart(filtered_df)
        distribution_fig = build_model_distribution_chart(filtered_df)

        # Build data table
        _, table_component = build_detail_table(filtered_df)

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


# ---------------------------------------------------------------------------
# Clear-filter callbacks (registered via shared helper)
# ---------------------------------------------------------------------------
register_clear_callbacks(CLEAR_PAIRS)
