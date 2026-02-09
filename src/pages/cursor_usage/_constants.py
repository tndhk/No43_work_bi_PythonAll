"""Constants for the Cursor Usage Dashboard page.

Centralizes dataset identifiers, column name mappings, ID prefixes,
and declarative ChartSpec / TableSpec definitions.
"""

from src.charts.specs import ChartSpec, TableSpec

# Dashboard identifier (used for config lookup)
DASHBOARD_ID: str = "cursor_usage"

# S3/Parquet dataset identifier (legacy fallback)
DATASET_ID: str = "cursor-usage"

# Component ID namespace prefix (for avoiding collisions with other pages)
ID_PREFIX: str = "cu-"

# Chart IDs used in this dashboard
CHART_ID_KPI_TOTAL_COST: str = f"{ID_PREFIX}kpi-total-cost"
CHART_ID_KPI_TOTAL_TOKENS: str = f"{ID_PREFIX}kpi-total-tokens"
CHART_ID_KPI_REQUEST_COUNT: str = f"{ID_PREFIX}kpi-request-count"
CHART_ID_COST_TREND: str = f"{ID_PREFIX}chart-cost-trend"
CHART_ID_TOKEN_EFFICIENCY: str = f"{ID_PREFIX}chart-token-efficiency"
CHART_ID_MODEL_DISTRIBUTION: str = f"{ID_PREFIX}chart-model-distribution"
CHART_ID_DATA_TABLE: str = f"{ID_PREFIX}data-table"

# Mapping from logical filter/column key to the actual DataFrame column name.
# Keys are short identifiers used in code; values are the raw column names
# as they appear in the Parquet/DataFrame.
COLUMN_MAP: dict[str, str] = {
    "date": "Date",
    "model": "Model",
    "cost": "Cost",
    "total_tokens": "Total Tokens",
    "user": "User",
    "kind": "Kind",
}

# ----- Control IDs (Clear buttons) -----
CTRL_ID_CLEAR_MODEL: str = f"{ID_PREFIX}ctrl-clear-model"
CTRL_ID_CLEAR_USER: str = f"{ID_PREFIX}ctrl-clear-user"
CTRL_ID_CLEAR_KIND: str = f"{ID_PREFIX}ctrl-clear-kind"

# Filter IDs (for reference in clear pairs)
FILTER_ID_MODEL: str = f"{ID_PREFIX}filter-model"
FILTER_ID_USER: str = f"{ID_PREFIX}filter-user"
FILTER_ID_KIND: str = f"{ID_PREFIX}filter-kind"

# Clear button to filter mapping (used by register_clear_callbacks)
CLEAR_PAIRS: list[tuple[str, str]] = [
    (FILTER_ID_MODEL, CTRL_ID_CLEAR_MODEL),
    (FILTER_ID_USER, CTRL_ID_CLEAR_USER),
    (FILTER_ID_KIND, CTRL_ID_CLEAR_KIND),
]

# ---------------------------------------------------------------------------
# Chart / Table Specs (declarative definitions)
# ---------------------------------------------------------------------------

COST_TREND_SPEC: ChartSpec = ChartSpec(
    title="Daily Cost Trend",
    chart_type="line",
    x_column=COLUMN_MAP["date"],
    y_columns=[COLUMN_MAP["cost"]],
    show_legend=False,
    height=460,
)

TOKEN_EFFICIENCY_SPEC: ChartSpec = ChartSpec(
    title="Token Efficiency by Model (Tokens per $)",
    chart_type="bar",
    x_column=COLUMN_MAP["model"],
    y_columns=["TokensPerCost"],
    show_legend=False,
    height=460,
    text_template="%{y}",
)

MODEL_DISTRIBUTION_SPEC: ChartSpec = ChartSpec(
    title="Cost Distribution by Model",
    chart_type="pie",
    x_column=COLUMN_MAP["model"],
    y_columns=[COLUMN_MAP["cost"]],
    height=460,
    show_legend=True,
)

DETAIL_TABLE_SPEC: TableSpec = TableSpec(
    title="Detailed Data",
    style_table={"overflowX": "auto"},
    style_cell={"textAlign": "left", "padding": "8px"},
    style_header={"fontWeight": "bold"},
    style_data_conditional=[],
    page_size=20,
    column_order=[
        COLUMN_MAP["date"],
        COLUMN_MAP["user"],
        COLUMN_MAP["model"],
        COLUMN_MAP["kind"],
        COLUMN_MAP["total_tokens"],
        COLUMN_MAP["cost"],
    ],
)
