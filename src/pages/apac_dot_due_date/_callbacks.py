"""Dash callbacks for APAC DOT Due Date Dashboard page.

Extracted from __init__.py to separate callback registration from page
registration.  Importing this module triggers callback registration via
the ``@callback`` decorator as a side effect.
"""
from dash import callback, html, Input, Output

from src.data.parquet_reader import ParquetReader
from src.data.data_source_registry import resolve_dataset_id
from ._constants import (
    DASHBOARD_ID,
    DATASET_ID,
    CHART_ID_REFERENCE_TABLE,
    CHART_ID_REFERENCE_TABLE_TITLE,
    CTRL_ID_NUM_PERCENT,
    CTRL_ID_BREAKDOWN,
    FILTER_ID_MONTH,
    FILTER_ID_PRC,
    FILTER_ID_AREA,
    FILTER_ID_CATEGORY,
    FILTER_ID_VENDOR,
    FILTER_ID_AMP_AV,
    FILTER_ID_ORDER_TYPE,
)
from ._data_loader import load_and_filter_data
from .charts import _ch00_reference_table


@callback(
    [
        Output(CHART_ID_REFERENCE_TABLE_TITLE, "children"),
        Output(CHART_ID_REFERENCE_TABLE, "children"),
    ],
    [
        Input(CTRL_ID_NUM_PERCENT, "value"),
        Input(CTRL_ID_BREAKDOWN, "active_tab"),
        Input(FILTER_ID_MONTH, "value"),
        Input(FILTER_ID_PRC, "value"),
        Input(FILTER_ID_AREA, "value"),
        Input(FILTER_ID_CATEGORY, "value"),
        Input(FILTER_ID_VENDOR, "value"),
        Input(FILTER_ID_AMP_AV, "value"),
        Input(FILTER_ID_ORDER_TYPE, "value"),
    ],
)
def update_all_charts(
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
    """Update all charts based on filter inputs.

    Creates a ParquetReader, calls load_and_filter_data once, and passes
    the result to _ch00_reference_table.build().
    """
    reader = ParquetReader()

    try:
        dataset_id = resolve_dataset_id(DASHBOARD_ID, CHART_ID_REFERENCE_TABLE, fallback=DATASET_ID)
        filtered_df = load_and_filter_data(
            reader,
            dataset_id,
            selected_months=selected_months,
            prc_filter_value=prc_filter_value,
            area_values=area_values,
            category_values=category_values,
            vendor_values=vendor_values,
            amp_av_values=amp_av_values,
            order_type_values=order_type_values,
        )

        return _ch00_reference_table.build(filtered_df, breakdown_tab, num_percent_mode)

    except Exception as e:
        error_msg = html.Div([
            html.P(f"Error loading data: {str(e)}", className="text-danger"),
        ])

        return (
            "0) Reference : Number of Work Order",
            error_msg,
        )
