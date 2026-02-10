"""Constants for the APAC DOT Due Date Dashboard page.

Centralizes dataset identifiers, column name mappings, table specs,
and ID prefixes to avoid hardcoded strings scattered across layout
and callback code.
"""
from dataclasses import dataclass

from src.charts.specs import TableSpec, DEFAULT_STYLE_TABLE, DEFAULT_STYLE_CELL, DEFAULT_STYLE_HEADER

# Dashboard identifier (used for config lookup)
DASHBOARD_ID: str = "apac_dot_due_date"

# S3/Parquet dataset identifier (legacy fallback)
DATASET_ID: str = "apac-dot-due-date"

# S3/Parquet dataset identifier for change-issue data
DATASET_ID_2: str = "apac-dot-ddd-change-issue-sql"

# Component ID namespace prefix (for avoiding collisions with other pages)
ID_PREFIX: str = "apac-dot-"

# ----- Control IDs -----
CTRL_ID_NUM_PERCENT: str = f"{ID_PREFIX}ctrl-num-percent"
CTRL_ID_BREAKDOWN: str = f"{ID_PREFIX}ctrl-breakdown"
CTRL_ID_CLEAR_MONTH: str = f"{ID_PREFIX}ctrl-clear-month"
CTRL_ID_CLEAR_PRC: str = f"{ID_PREFIX}ctrl-clear-prc"
CTRL_ID_CLEAR_AREA: str = f"{ID_PREFIX}ctrl-clear-area"
CTRL_ID_CLEAR_CATEGORY: str = f"{ID_PREFIX}ctrl-clear-category"
CTRL_ID_CLEAR_VENDOR: str = f"{ID_PREFIX}ctrl-clear-vendor"
CTRL_ID_CLEAR_AMP_AV: str = f"{ID_PREFIX}ctrl-clear-amp-av"
CTRL_ID_CLEAR_ORDER_TYPE: str = f"{ID_PREFIX}ctrl-clear-order-type"

# ----- Filter IDs -----
FILTER_ID_MONTH: str = f"{ID_PREFIX}filter-month"
FILTER_ID_PRC: str = f"{ID_PREFIX}filter-prc"
FILTER_ID_AREA: str = f"{ID_PREFIX}filter-area"
FILTER_ID_CATEGORY: str = f"{ID_PREFIX}filter-category"
FILTER_ID_VENDOR: str = f"{ID_PREFIX}filter-vendor"
FILTER_ID_AMP_AV: str = f"{ID_PREFIX}filter-amp-av"
FILTER_ID_ORDER_TYPE: str = f"{ID_PREFIX}filter-order-type"

# ----- KPI IDs -----
KPI_ID_TOTAL_WORK_ORDERS: str = f"{ID_PREFIX}kpi-total-work-orders"

# ----- Chart IDs -----
CHART_ID_REFERENCE_TABLE: str = f"{ID_PREFIX}chart-00"
CHART_ID_REFERENCE_TABLE_TITLE: str = f"{CHART_ID_REFERENCE_TABLE}-title"
CHART_ID_CHANGE_ISSUE_TABLE: str = f"{ID_PREFIX}chart-01"
CHART_ID_CHANGE_ISSUE_TABLE_TITLE: str = f"{CHART_ID_CHANGE_ISSUE_TABLE}-title"


@dataclass(frozen=True)
class DatasetConfig:
    """Configuration for a dataset used in this dashboard.

    Groups all dataset-specific settings: column mappings, chart IDs,
    table specs, and which filters should be skipped.
    """

    dataset_id: str
    chart_id: str
    chart_title_id: str
    column_map: dict[str, str]
    breakdown_map: dict[str, str]
    table_spec_key: str
    skip_filters: frozenset[str] = frozenset()


# Dataset configurations grouped by logical name.
# Each entry defines column mappings, chart IDs, and filter exclusions.
DATASETS: dict[str, DatasetConfig] = {
    "reference": DatasetConfig(
        dataset_id="apac-dot-due-date",
        chart_id=CHART_ID_REFERENCE_TABLE,
        chart_title_id=CHART_ID_REFERENCE_TABLE_TITLE,
        column_map={
            "month": "Delivery Completed Month",
            "area": "business area",
            "category": "Metric Workstream",
            "vendor": "Vendor: Account Name",
            "amp_av": "AMP VS AV Scope",
            "order_type": "order tags",
            "job_name": "job name",
            "work_order_id": "work order id",
        },
        breakdown_map={
            "area": "business area",
            "category": "Metric Workstream",
            "vendor": "Vendor: Account Name",
        },
        table_spec_key="ch00_reference_table",
        skip_filters=frozenset(["order_type"]),
    ),
    "change_issue": DatasetConfig(
        dataset_id="apac-dot-ddd-change-issue-sql",
        chart_id=CHART_ID_CHANGE_ISSUE_TABLE,
        chart_title_id=CHART_ID_CHANGE_ISSUE_TABLE_TITLE,
        column_map={
            "month": "edit month",
            "area": "business area",
            "category": "metric workstream",
            "vendor": "vendor: account name",
            "order_type": "order types",
            "job_name": "job name",
            "work_order_id": "work order: work order id",
        },
        breakdown_map={
            "area": "business area",
            "category": "metric workstream",
            "vendor": "vendor: account name",
        },
        table_spec_key="ch01_change_issue_table",
        skip_filters=frozenset(["amp_av"]),
    ),
}


# ---------------------------------------------------------------------------
# Table specifications (previously in charts/_table_specs.py)
# Uses the shared TableSpec from src.charts.specs.
# ---------------------------------------------------------------------------
TABLE_SPECS: dict[str, TableSpec] = {
    "ch00_reference_table": TableSpec(
        title="0) Reference : Number of Work Order",
        style_table=DEFAULT_STYLE_TABLE,
        style_cell=DEFAULT_STYLE_CELL,
        style_header=DEFAULT_STYLE_HEADER,
        style_data_conditional=[
            {
                "if": {"filter_query": "{breakdown_col} = \"GRAND TOTAL\""},
                "fontWeight": "bold",
                "backgroundColor": "#eff6ff",
            }
        ],
        page_size=20,
    ),
    "ch01_change_issue_table": TableSpec(
        title="1) DDD Change + Issue : Number of Work Order",
        style_table=DEFAULT_STYLE_TABLE,
        style_cell=DEFAULT_STYLE_CELL,
        style_header=DEFAULT_STYLE_HEADER,
        style_data_conditional=[
            {
                "if": {"filter_query": "{breakdown_col} = \"GRAND TOTAL\""},
                "fontWeight": "bold",
                "backgroundColor": "#eff6ff",
            }
        ],
        page_size=20,
    ),
}


# ---------------------------------------------------------------------------
# Clear-filter callback pairs (filter_id, clear_button_id)
# ---------------------------------------------------------------------------
CLEAR_PAIRS: list[tuple[str, str]] = [
    (FILTER_ID_MONTH, CTRL_ID_CLEAR_MONTH),
    (FILTER_ID_AREA, CTRL_ID_CLEAR_AREA),
    (FILTER_ID_CATEGORY, CTRL_ID_CLEAR_CATEGORY),
    (FILTER_ID_VENDOR, CTRL_ID_CLEAR_VENDOR),
    (FILTER_ID_AMP_AV, CTRL_ID_CLEAR_AMP_AV),
    (FILTER_ID_ORDER_TYPE, CTRL_ID_CLEAR_ORDER_TYPE),
]

# PRC clear pair (single-select, uses default_value=None)
CLEAR_PAIR_PRC: tuple[str, str] = (FILTER_ID_PRC, CTRL_ID_CLEAR_PRC)
