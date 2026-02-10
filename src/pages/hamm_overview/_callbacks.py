"""Callbacks for HAMM Overview dashboard."""
from dash import callback, Input, Output, html

from src.data.parquet_reader import ParquetReader
from src.charts.empty_states import create_error_figure
from src.utils.callback_helpers import ensure_list, register_clear_callbacks
from src.components.cards import create_kpi_card
from ._constants import (
    COLUMN_MAP,
    KPI_ID_KPI_TOTAL_SCREENS,
    KPI_ID_KPI_TOTAL_ERV,
    KPI_ID_KPI_TOTAL_PRELIM,
    TABLE_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    FILTER_ID_FILTER_REGION,
    FILTER_ID_FILTER_YEAR,
    FILTER_ID_FILTER_MONTH,
    CLEAR_PAIRS,
)
from ._data_loader import (
    resolve_dataset_id_for_dashboard,
    load_and_filter_data,
    FILTER_COLUMN_MAP,
    aggregate_volume_table,
    aggregate_volume_chart,
)
from ._chart_builders import (
    build_volume_table,
    build_volume_chart,
)


def _create_count_kpi(df, title, bg_color, accent_color, id_col="id"):
    """Create a KPI card showing nunique count."""
    value = df[id_col].nunique()
    return create_kpi_card(title, f"{value:,.0f}", bg_color=bg_color, accent_color=accent_color)


@callback(
    Output(KPI_ID_KPI_TOTAL_SCREENS, "children"),
    Output(KPI_ID_KPI_TOTAL_ERV, "children"),
    Output(KPI_ID_KPI_TOTAL_PRELIM, "children"),
    Output(TABLE_ID_VOLUME_TABLE, "children"),
    Output(CHART_ID_VOLUME_CHART, "figure"),
    Input(FILTER_ID_FILTER_REGION, "value"),
    Input(FILTER_ID_FILTER_YEAR, "value"),
    Input(FILTER_ID_FILTER_MONTH, "value"),
)
def update_dashboard(filter_region_values, filter_year_values, filter_month_values):
    """Update all dashboard components based on filter selections."""
    reader = ParquetReader()
    dataset_id = resolve_dataset_id_for_dashboard()

    filter_pairs = [
        ("region", ensure_list(filter_region_values)),
        ("_year", ensure_list(filter_year_values)),
        ("_month", ensure_list(filter_month_values)),
    ]

    try:
        df = load_and_filter_data(reader, dataset_id, FILTER_COLUMN_MAP, filter_pairs)

        kpi_total_screens_card = _create_count_kpi(
            df, "Total Screens Processed", "#d6e4f0", "#2f5f8f",
        )
        kpi_total_erv_card = _create_count_kpi(
            df, "Total ERV Processed", "#f6b3b3", "#e57f7f",
        )
        kpi_total_prelim_card = _create_count_kpi(
            df, "Total Prelim Processed", "#e57f7f", "#c0392b",
        )

        volume_chart_df = aggregate_volume_chart(df)
        volume_chart_fig = build_volume_chart(volume_chart_df)

        volume_table_df = aggregate_volume_table(df)
        _, volume_table_table = build_volume_table(volume_table_df)

        return (
            kpi_total_screens_card,
            kpi_total_erv_card,
            kpi_total_prelim_card,
            volume_table_table,
            volume_chart_fig,
        )

    except Exception as exc:
        error_fig = create_error_figure(error=str(exc))
        return (
            create_kpi_card("Total Screens Processed", "Error"),
            create_kpi_card("Total ERV Processed", "Error"),
            create_kpi_card("Total Prelim Processed", "Error"),
            html.P(f"Error loading data: {exc}", className="text-danger"),
            error_fig,
        )


# ---------------------------------------------------------------------------
# Clear-filter callbacks (registered via shared helper)
# ---------------------------------------------------------------------------
register_clear_callbacks(CLEAR_PAIRS)
