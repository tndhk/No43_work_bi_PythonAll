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
    KPI_ID_TOTAL_WORK_ORDERS,
    DATASETS,
    CTRL_ID_NUM_PERCENT,
    CTRL_ID_BREAKDOWN,
    CTRL_ID_CLEAR_MONTH,
    CTRL_ID_CLEAR_PRC,
    CTRL_ID_CLEAR_AREA,
    CTRL_ID_CLEAR_CATEGORY,
    CTRL_ID_CLEAR_VENDOR,
    CTRL_ID_CLEAR_AMP_AV,
    CTRL_ID_CLEAR_ORDER_TYPE,
    FILTER_ID_MONTH,
    FILTER_ID_PRC,
    FILTER_ID_AREA,
    FILTER_ID_CATEGORY,
    FILTER_ID_VENDOR,
    FILTER_ID_AMP_AV,
    FILTER_ID_ORDER_TYPE,
)
from ._data_loader import load_and_filter_data
from .charts._pivot_table_builder import build_pivot_table
from .charts._table_specs import TABLE_SPECS


def _coerce_single_value(value, default: str) -> str:
    """Normalize potentially list-like UI values to a single string."""
    if isinstance(value, list):
        return value[0] if value else default
    if value is None:
        return default
    return value


@callback(
    [
        Output(KPI_ID_TOTAL_WORK_ORDERS, "children"),
        Output(DATASETS["reference"].chart_title_id, "children"),
        Output(DATASETS["reference"].chart_id, "children"),
        Output(DATASETS["change_issue"].chart_title_id, "children"),
        Output(DATASETS["change_issue"].chart_id, "children"),
    ],
    [
        Input(CTRL_ID_NUM_PERCENT, "value"),
        Input(CTRL_ID_BREAKDOWN, "value"),
        Input(FILTER_ID_MONTH, "value"),
        Input(FILTER_ID_PRC, "value"),
        Input(FILTER_ID_AREA, "value"),
        Input(FILTER_ID_CATEGORY, "value"),
        Input(FILTER_ID_VENDOR, "value"),
        Input(FILTER_ID_AMP_AV, "value"),
        Input(FILTER_ID_ORDER_TYPE, "value"),
    ],
)
def update_dashboard(
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
    """Update dashboard based on filter inputs.

    Loops through DATASETS configuration to load and filter each dataset,
    then builds pivot tables using the shared build_pivot_table function.
    """
    reader = ParquetReader()
    prc_filter_value = _coerce_single_value(prc_filter_value, "all")

    try:
        chart_results = []
        ref_config = DATASETS["reference"]
        filtered_df_for_kpi = None

        # Process each dataset configuration
        for ds_key, ds_cfg in DATASETS.items():
            dataset_id = resolve_dataset_id(DASHBOARD_ID, ds_cfg.chart_id)

            # Apply filters, skipping those in skip_filters
            filtered_df = load_and_filter_data(
                reader,
                dataset_id,
                ds_cfg.column_map,
                selected_months=selected_months,
                prc_filter_value=prc_filter_value,
                area_values=area_values,
                category_values=category_values,
                vendor_values=vendor_values,
                amp_av_values=None if "amp_av" in ds_cfg.skip_filters else amp_av_values,
                order_type_values=None if "order_type" in ds_cfg.skip_filters else order_type_values,
            )

            # Save reference dataset for KPI calculation
            if ds_key == "reference":
                filtered_df_for_kpi = filtered_df

            # Build pivot table directly (no wrapper needed)
            title, comp = build_pivot_table(
                filtered_df=filtered_df,
                breakdown_tab=breakdown_tab,
                num_percent_mode=num_percent_mode,
                column_map=ds_cfg.column_map,
                breakdown_map=ds_cfg.breakdown_map,
                table_spec=TABLE_SPECS[ds_cfg.table_spec_key],
            )
            chart_results.append((title, comp))

        # Calculate total work orders (using work_order_id column from reference dataset)
        work_order_col = ref_config.column_map.get("work_order_id")
        if work_order_col and work_order_col in filtered_df_for_kpi.columns:
            total_work_orders = filtered_df_for_kpi[work_order_col].nunique()
        else:
            total_work_orders = len(filtered_df_for_kpi)

        return (
            f"{total_work_orders:,}",
            *chart_results[0],  # reference table (title, component)
            *chart_results[1],  # change_issue table (title, component)
        )

    except Exception as e:
        msg = f"Error loading data: {str(e)}"
        ref_config = DATASETS["reference"]
        change_config = DATASETS["change_issue"]

        return (
            "0",
            TABLE_SPECS[ref_config.table_spec_key].title,
            html.Div([html.P(msg, className="text-danger")]),
            TABLE_SPECS[change_config.table_spec_key].title,
            html.Div([html.P(msg, className="text-danger")]),
        )


@callback(
    Output(FILTER_ID_MONTH, "value"),
    Input(CTRL_ID_CLEAR_MONTH, "n_clicks"),
    prevent_initial_call=True,
)
def clear_month(_n_clicks):
    return []


@callback(
    Output(FILTER_ID_PRC, "value"),
    Input(CTRL_ID_CLEAR_PRC, "n_clicks"),
    prevent_initial_call=True,
)
def clear_prc(_n_clicks):
    return None


@callback(
    Output(FILTER_ID_AREA, "value"),
    Input(CTRL_ID_CLEAR_AREA, "n_clicks"),
    prevent_initial_call=True,
)
def clear_area(_n_clicks):
    return []


@callback(
    Output(FILTER_ID_CATEGORY, "value"),
    Input(CTRL_ID_CLEAR_CATEGORY, "n_clicks"),
    prevent_initial_call=True,
)
def clear_category(_n_clicks):
    return []


@callback(
    Output(FILTER_ID_VENDOR, "value"),
    Input(CTRL_ID_CLEAR_VENDOR, "n_clicks"),
    prevent_initial_call=True,
)
def clear_vendor(_n_clicks):
    return []


@callback(
    Output(FILTER_ID_AMP_AV, "value"),
    Input(CTRL_ID_CLEAR_AMP_AV, "n_clicks"),
    prevent_initial_call=True,
)
def clear_amp_av(_n_clicks):
    return []


@callback(
    Output(FILTER_ID_ORDER_TYPE, "value"),
    Input(CTRL_ID_CLEAR_ORDER_TYPE, "n_clicks"),
    prevent_initial_call=True,
)
def clear_order_type(_n_clicks):
    return []
