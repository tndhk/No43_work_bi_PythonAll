"""Dash callbacks for APAC DOT Due Date Dashboard page.

Extracted from __init__.py to separate callback registration from page
registration.  Importing this module triggers callback registration via
the ``@callback`` decorator and ``register_clear_callbacks()`` as side
effects.
"""
from copy import deepcopy

from dash import callback, html, Input, Output

from src.data.parquet_reader import ParquetReader
from src.data.data_source_registry import resolve_dataset_id
from src.charts.table_builder import build_table
from src.charts.empty_states import create_empty_table, create_error_figure  # noqa: F401
from src.utils.callback_helpers import register_clear_callbacks
from src.components.cards import create_kpi_card
from ._chart_builders import build_pivot_data
from ._constants import (
    DASHBOARD_ID,
    KPI_ID_TOTAL_WORK_ORDERS,
    DATASETS,
    TABLE_SPECS,
    CTRL_ID_NUM_PERCENT,
    CTRL_ID_BREAKDOWN,
    CLEAR_PAIRS,
    CLEAR_PAIR_PRC,
    FILTER_ID_MONTH,
    FILTER_ID_PRC,
    FILTER_ID_AREA,
    FILTER_ID_CATEGORY,
    FILTER_ID_VENDOR,
    FILTER_ID_AMP_AV,
    FILTER_ID_ORDER_TYPE,
)
from ._data_loader import load_and_filter_data


def _coerce_single_value(value, default: str) -> str:
    """Normalize callback value to a single scalar or the default.

    Unlike ``ensure_list`` (which normalizes to a list), this extracts the
    first element when a list is given, or returns the *default* value for
    empty/None input.
    """
    if isinstance(value, list):
        return value[0] if value else default
    if value is None:
        return default
    return value


def build_pivot_table(
    filtered_df,
    breakdown_tab,
    num_percent_mode,
    column_map,
    breakdown_map,
    table_spec,
):
    """Aggregate data and render as a titled DataTable.

    Combines build_pivot_data() for aggregation with build_table()
    for rendering.  The {breakdown_col} placeholder in
    style_data_conditional is resolved before rendering.
    """
    if len(filtered_df) == 0:
        return (table_spec.title, create_empty_table())

    pivot_df = build_pivot_data(
        filtered_df=filtered_df,
        breakdown_tab=breakdown_tab,
        num_percent_mode=num_percent_mode,
        column_map=column_map,
        breakdown_map=breakdown_map,
    )

    # Resolve {breakdown_col} placeholder in style_data_conditional
    breakdown_column = breakdown_map[breakdown_tab]
    resolved_conditional = deepcopy(table_spec.style_data_conditional)
    for rule in resolved_conditional:
        if not isinstance(rule, dict):
            continue
        condition = rule.get("if")
        if not isinstance(condition, dict):
            continue
        filter_query = condition.get("filter_query")
        if isinstance(filter_query, str):
            condition["filter_query"] = filter_query.replace(
                "{breakdown_col}", f"{{{breakdown_column}}}"
            )

    # Create a spec with resolved conditionals for rendering
    from src.charts.specs import TableSpec as SharedTableSpec
    resolved_spec = SharedTableSpec(
        title=table_spec.title,
        style_table=table_spec.style_table,
        style_cell=table_spec.style_cell,
        style_header=table_spec.style_header,
        style_data_conditional=resolved_conditional,
        column_display=table_spec.column_display,
        column_order=table_spec.column_order,
        page_size=table_spec.page_size,
        sort_action=table_spec.sort_action,
        filter_action=table_spec.filter_action,
    )

    return build_table(pivot_df, resolved_spec)


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
    then builds pivot tables using build_pivot_data + build_table.
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

            # Build pivot table (aggregation + rendering)
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
            create_kpi_card("Total Work Orders", f"{total_work_orders:,}"),
            *chart_results[0],  # reference table (title, component)
            *chart_results[1],  # change_issue table (title, component)
        )

    except Exception as e:
        error_msg = html.P(f"Error loading data: {e}", className="text-danger")
        ref_config = DATASETS["reference"]
        change_config = DATASETS["change_issue"]

        return (
            create_kpi_card("Total Work Orders", "0"),
            TABLE_SPECS[ref_config.table_spec_key].title,
            error_msg,
            TABLE_SPECS[change_config.table_spec_key].title,
            error_msg,
        )


# ---------------------------------------------------------------------------
# Clear-filter callbacks (registered via shared helper)
# ---------------------------------------------------------------------------

# Multi-select filters: reset to empty list
register_clear_callbacks(CLEAR_PAIRS)

# PRC is single-select: reset to None
register_clear_callbacks(
    [CLEAR_PAIR_PRC],
    default_value=None,
)
