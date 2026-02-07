"""Constants for the APAC DOT Due Date Dashboard page.

Centralizes dataset identifiers, column name mappings, and ID prefixes
to avoid hardcoded strings scattered across layout and callback code.
"""

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

# Mapping from logical filter ID to the actual DataFrame column name.
# Keys are short identifiers used in code; values are the raw column names
# as they appear in the Parquet/DataFrame.
COLUMN_MAP: dict[str, str] = {
    "month": "Delivery Completed Month",
    "area": "business area",
    "category": "Metric Workstream",
    "vendor": "Vendor: Account Name",
    "amp_av": "AMP VS AV Scope",
    "order_type": "order tags",
    "job_name": "job name",
    "work_order_id": "work order id",
}

# Mapping from logical filter ID to the DataFrame column name for change-issue data.
COLUMN_MAP_2: dict[str, str] = {
    "month": "edit month",
    "area": "business area",
    "category": "metric workstream",
    "vendor": "vendor: account name",
    "order_type": "order types",
    "job_name": "job name",
    "work_order_id": "work order: work order id",
}

# Mapping from breakdown tab ID to the DataFrame column used for pivot grouping.
# This is a subset of COLUMN_MAP -- only the columns that make sense as
# breakdown dimensions in the pivot table.
BREAKDOWN_MAP: dict[str, str] = {
    "area": "business area",
    "category": "Metric Workstream",
    "vendor": "Vendor: Account Name",
}

# Mapping from breakdown tab ID to the DataFrame column for change-issue pivot grouping.
# This is a subset of COLUMN_MAP_2 -- only the columns that make sense as
# breakdown dimensions in the pivot table.
BREAKDOWN_MAP_2: dict[str, str] = {
    "area": "business area",
    "category": "metric workstream",
    "vendor": "vendor: account name",
}
