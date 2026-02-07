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
    CHART_ID_REFERENCE_TABLE,
    CHART_ID_REFERENCE_TABLE_TITLE,
    CHART_ID_CHANGE_ISSUE_TABLE,
    CHART_ID_CHANGE_ISSUE_TABLE_TITLE,
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
from ._data_loader import load_and_filter_data, load_and_filter_data_2
from .charts import _ch00_reference_table, _ch01_change_issue_table


@callback(
    [
        Output(CHART_ID_REFERENCE_TABLE_TITLE, "children"),
        Output(CHART_ID_REFERENCE_TABLE, "children"),
        Output(CHART_ID_CHANGE_ISSUE_TABLE_TITLE, "children"),
        Output(CHART_ID_CHANGE_ISSUE_TABLE, "children"),
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

    Creates a ParquetReader, calls load_and_filter_data for dataset 1
    and load_and_filter_data_2 for dataset 2, and passes each result
    to the corresponding chart builder.
    """
    reader = ParquetReader()

    try:
        # Dataset 1: order_type NOT applied
        dataset_id_1 = resolve_dataset_id(DASHBOARD_ID, CHART_ID_REFERENCE_TABLE)
        filtered_df_1 = load_and_filter_data(
            reader,
            dataset_id_1,
            selected_months=selected_months,
            prc_filter_value=prc_filter_value,
            area_values=area_values,
            category_values=category_values,
            vendor_values=vendor_values,
            amp_av_values=amp_av_values,
            order_type_values=None,           # dataset 1 does not use order_type
        )

        # Dataset 2: amp_av NOT applicable
        dataset_id_2 = resolve_dataset_id(DASHBOARD_ID, CHART_ID_CHANGE_ISSUE_TABLE)
        filtered_df_2 = load_and_filter_data_2(
            reader,
            dataset_id_2,
            selected_months=selected_months,
            prc_filter_value=prc_filter_value,
            area_values=area_values,
            category_values=category_values,
            vendor_values=vendor_values,
            order_type_values=order_type_values,  # dataset 2 uses order_type
        )

        title_0, comp_0 = _ch00_reference_table.build(filtered_df_1, breakdown_tab, num_percent_mode)
        title_1, comp_1 = _ch01_change_issue_table.build(filtered_df_2, breakdown_tab, num_percent_mode)

        return (title_0, comp_0, title_1, comp_1)

    except Exception as e:
        msg = f"Error loading data: {str(e)}"

        return (
            "0) Reference : Number of Work Order",
            html.Div([html.P(msg, className="text-danger")]),
            "1) DDD Change + Issue : Number of Work Order",
            html.Div([html.P(msg, className="text-danger")]),
        )
