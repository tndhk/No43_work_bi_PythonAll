"""Constants for HAMM Overview dashboard."""
from src.charts.specs import ChartSpec, TableSpec

# Dashboard metadata
DASHBOARD_ID = "hamm_overview"
DATASET_ID = "hamm-dashboard"
ID_PREFIX = "hamm-"

# Filter IDs
FILTER_ID_FILTER_REGION = f"{ID_PREFIX}filter-region"
CTRL_ID_FILTER_REGION_CLEAR = f"{ID_PREFIX}filter-region-clear"
FILTER_ID_FILTER_YEAR = f"{ID_PREFIX}filter-year"
CTRL_ID_FILTER_YEAR_CLEAR = f"{ID_PREFIX}filter-year-clear"
FILTER_ID_FILTER_MONTH = f"{ID_PREFIX}filter-month"

# Component IDs
KPI_ID_KPI_TOTAL_SCREENS = f"{ID_PREFIX}kpi-total-screens"
KPI_ID_KPI_TOTAL_ERV = f"{ID_PREFIX}kpi-total-erv"
KPI_ID_KPI_TOTAL_PRELIM = f"{ID_PREFIX}kpi-total-prelim"
TABLE_ID_VOLUME_TABLE = f"{ID_PREFIX}volume-table"
CHART_ID_VOLUME_CHART = f"{ID_PREFIX}volume-chart"

# Clear callback pairs: (filter_id, clear_button_id)
CLEAR_PAIRS: list[tuple[str, str]] = [
    (FILTER_ID_FILTER_REGION, CTRL_ID_FILTER_REGION_CLEAR),
    (FILTER_ID_FILTER_YEAR, CTRL_ID_FILTER_YEAR_CLEAR),
]

# Derived column names
DERIVED_YEAR = "_year"
DERIVED_MONTH = "_month"
DERIVED_FISCAL_YEAR = "_fiscal_year"

# Mapping from logical keys to DataFrame column names
COLUMN_MAP: dict[str, str] = {
    "id": "id",
    "title": "title",
    "status": "status",
    "created_at": "created_at",
    "region": "notification_company_name",
}

# ---------------------------------------------------------------------------
# Chart Specs (declarative definitions)
# ---------------------------------------------------------------------------

VOLUME_CHART_SPEC = ChartSpec(
    title="Volume Chart",
    chart_type="stacked_bar",
    x_column="_month",
    y_columns=["Completed", "Invalid"],
    color_map={"Completed": "#2d6a2e", "Invalid": "#9ca3af"},
    height=460,
    show_legend=True,
    orientation="v",
)

# ---------------------------------------------------------------------------
# Table Specs (declarative definitions)
# ---------------------------------------------------------------------------

VOLUME_TABLE_SPEC = TableSpec(
    title="Volume Summary",
    style_table={"height": "400px", "overflowX": "auto"},
    style_cell={"padding": "6px 8px", "textAlign": "left"},
    style_header={"fontWeight": "600"},
    style_data_conditional=[],
    sort_action="native",
    page_size=20,
    column_order=["Fiscal Year", "Month", "Completed", "Invalid"],
    filter_action="none",
)
