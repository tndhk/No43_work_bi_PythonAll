"""Constants for the Hamm Overview dashboard."""

from src.charts.specs import ChartSpec, TableSpec

DASHBOARD_ID: str = "hamm_overview"
DATASET_ID: str = "hamm-dashboard"
ID_PREFIX: str = "hamm-"

# Chart IDs
CHART_ID_VOLUME_TABLE: str = f"{ID_PREFIX}volume-table"
CHART_ID_VOLUME_CHART: str = f"{ID_PREFIX}volume-chart"
CHART_ID_TASK_TABLE: str = f"{ID_PREFIX}task-table"
CHART_ID_ERROR_RATIO: str = f"{ID_PREFIX}error-ratio"
CHART_ID_ERROR_BY_SCREENER: str = f"{ID_PREFIX}error-by-screener"
CHART_ID_USER_BREAKDOWN: str = f"{ID_PREFIX}user-breakdown"
CHART_ID_HAMM_BREAKDOWN: str = f"{ID_PREFIX}hamm-breakdown"
CHART_ID_METADATA_ORIGINAL_LANGUAGE: str = f"{ID_PREFIX}metadata-original-language"
CHART_ID_METADATA_DIALOGUE: str = f"{ID_PREFIX}metadata-dialogue"
CHART_ID_METADATA_GENRE: str = f"{ID_PREFIX}metadata-genre"

# KPI Card IDs
CHART_ID_KPI_TOTAL_SCREENS = f"{ID_PREFIX}kpi-total-screens"
CHART_ID_KPI_TOTAL_ERV     = f"{ID_PREFIX}kpi-total-erv"
CHART_ID_KPI_TOTAL_PRELIM  = f"{ID_PREFIX}kpi-total-prelim"

# KPI Card colors
KPI_COLOR_SCREENS = {"bg": "#d6e4f0", "accent": "#2f5f8f"}
KPI_COLOR_ERV     = {"bg": "#f6b3b3", "accent": "#e57f7f"}
KPI_COLOR_PRELIM  = {"bg": "#e57f7f", "accent": "#c0392b"}

# Filter IDs
FILTER_ID_REGION: str = f"{ID_PREFIX}filter-region"
FILTER_ID_YEAR: str = f"{ID_PREFIX}filter-year"
FILTER_ID_MONTH: str = f"{ID_PREFIX}filter-month"
FILTER_ID_TASK_ID: str = f"{ID_PREFIX}filter-task-id"
FILTER_ID_CONTENT_TYPE: str = f"{ID_PREFIX}filter-content-type"
FILTER_ID_ORIGINAL_LANGUAGE: str = f"{ID_PREFIX}filter-original-language"
FILTER_ID_DIALOGUE: str = f"{ID_PREFIX}filter-dialogue"
FILTER_ID_GENRE: str = f"{ID_PREFIX}filter-genre"
FILTER_ID_ERROR_CODE: str = f"{ID_PREFIX}filter-error-code"
FILTER_ID_ERROR_TYPE: str = f"{ID_PREFIX}filter-error-type"
FILTER_ID_CADENCE: str = f"{ID_PREFIX}filter-cadence"

# Per-slicer clear control IDs
CTRL_ID_CLEAR_REGION: str = f"{ID_PREFIX}ctrl-clear-region"
CTRL_ID_CLEAR_YEAR: str = f"{ID_PREFIX}ctrl-clear-year"
CTRL_ID_CLEAR_CONTENT_TYPE: str = f"{ID_PREFIX}ctrl-clear-content-type"
CTRL_ID_CLEAR_ORIGINAL_LANGUAGE: str = f"{ID_PREFIX}ctrl-clear-original-language"
CTRL_ID_CLEAR_DIALOGUE: str = f"{ID_PREFIX}ctrl-clear-dialogue"
CTRL_ID_CLEAR_GENRE: str = f"{ID_PREFIX}ctrl-clear-genre"
CTRL_ID_CLEAR_ERROR_TYPE: str = f"{ID_PREFIX}ctrl-clear-error-type"

# Clear callback pairs: (filter_id, clear_button_id)
CLEAR_PAIRS: list[tuple[str, str]] = [
    (FILTER_ID_REGION, CTRL_ID_CLEAR_REGION),
    (FILTER_ID_YEAR, CTRL_ID_CLEAR_YEAR),
    (FILTER_ID_CONTENT_TYPE, CTRL_ID_CLEAR_CONTENT_TYPE),
    (FILTER_ID_ORIGINAL_LANGUAGE, CTRL_ID_CLEAR_ORIGINAL_LANGUAGE),
    (FILTER_ID_DIALOGUE, CTRL_ID_CLEAR_DIALOGUE),
    (FILTER_ID_GENRE, CTRL_ID_CLEAR_GENRE),
    (FILTER_ID_ERROR_TYPE, CTRL_ID_CLEAR_ERROR_TYPE),
]

# Derived column names
DERIVED_YEAR: str = "_year"
DERIVED_MONTH: str = "_month"
DERIVED_FISCAL_YEAR: str = "_fiscal_year"
DERIVED_FISCAL_QUARTER: str = "_fiscal_quarter"
DERIVED_ISO_WEEK: str = "_iso_week"
DERIVED_START_DATE: str = "_start_date"
DERIVED_END_DATE: str = "_end_date"

# Mapping from logical keys to DataFrame column names
COLUMN_MAP: dict[str, str] = {
    "id": "id",
    "title": "title",
    "status": "status",
    "created_at": "created_at",
    "completed_at": "completed_at",
    "region": "notification_company_name",
    "content_type": "video_type_description",
    "original_language": "original_language_name",
    "dialogue": "was dialogue provided?",
    "genre": "genre_name",
    "error_code": "error code",
    "error_type": "error user vs system",
    "error_description": "error description",
    "video_duration": "video_duration",
    "audio_details": "audio location",
}

# Label constants for volume summary (status-based)
COMPLETED_LABEL: str = "Completed"
INVALID_LABEL: str = "Invalid"

# Label constants for KPI cards (content type-based)
PRELIM_LABEL: str = "Prelim"
ERV_LABEL: str = "ERV"

# Internal sort column used in volume summary
SORT_START_COL: str = "_sort_start_dt"

# Compact table styling shared by volume and task tables
_COMPACT_CELL: dict = {
    "textAlign": "left",
    "padding": "4px 6px",
    "fontSize": "0.75rem",
    "whiteSpace": "nowrap",
}
_COMPACT_HEADER: dict = {
    "fontWeight": "bold",
    "fontSize": "0.75rem",
    "padding": "4px 6px",
}

# ---------------------------------------------------------------------------
# Chart / Table Specs (declarative definitions)
# ---------------------------------------------------------------------------

VOLUME_TABLE_SPEC: TableSpec = TableSpec(
    title="Volume Summary",
    style_table={"overflowX": "auto", "height": "400px", "overflowY": "auto"},
    style_cell=_COMPACT_CELL,
    style_header=_COMPACT_HEADER,
    style_data_conditional=[],
    sort_action="native",
    page_size=20,
    column_order=[
        "Fiscal Year",
        "Fiscal Quarter",
        "ISO Week",
        "Start Date",
        "End Date",
        COMPLETED_LABEL,
        INVALID_LABEL,
        "VOLUME TOTAL",
    ],
)

VOLUME_CHART_SPEC: ChartSpec = ChartSpec(
    title="Volume Chart",
    chart_type="stacked_bar",
    x_column="Start Date",
    y_columns=[COMPLETED_LABEL, INVALID_LABEL],
    color_map={
        COMPLETED_LABEL: "#2d6a2e",
        INVALID_LABEL: "#9ca3af",
    },
    text_template="%{y}",
    height=400,
)

TASK_TABLE_SPEC: TableSpec = TableSpec(
    title="Task Details",
    style_table={"overflowX": "auto"},
    style_cell=_COMPACT_CELL,
    style_header=_COMPACT_HEADER,
    style_data_conditional=[],
    sort_action="native",
    page_size=20,
    column_order=[
        "Task ID",
        "Task Name",
        "Content Type",
        "Task Status",
        "Source File Duration",
        "Audio Details",
        "Job Created",
        "Completed / Err",
        "Total Duration",
    ],
)

# Error Details Chart Specs
ERROR_RATIO_SPEC: ChartSpec = ChartSpec(
    title="Issues Ratio (HAMM vs Human Intervention)",
    chart_type="pie",
    x_column="error_type",
    y_columns=["count"],
    height=400,
)

ERROR_BY_SCREENER_SPEC: ChartSpec = ChartSpec(
    title="Intervention per Screener Type",
    chart_type="stacked_bar",
    x_column="video_type_description",
    y_columns=["User", "HAMM"],
    color_map={
        "User": "#e57f7f",
        "HAMM": "#5f8fc7",
    },
    height=400,
)

USER_BREAKDOWN_SPEC: ChartSpec = ChartSpec(
    title="User Intervention Breakdown",
    chart_type="bar",
    x_column="error_description",
    y_columns=["count"],
    color_map={
        "count": "#e57f7f",
    },
    height=400,
)

HAMM_BREAKDOWN_SPEC: ChartSpec = ChartSpec(
    title="HAMM Intervention Breakdown",
    chart_type="bar",
    x_column="error_description",
    y_columns=["count"],
    color_map={
        "count": "#5f8fc7",
    },
    height=400,
)

# Content Metadata Chart Specs
ORIGINAL_LANGUAGE_SPEC: ChartSpec = ChartSpec(
    title="Original Language",
    chart_type="pie",
    x_column="original_language",
    y_columns=["count"],
    color_map={
        "Japanese": "#6EA5C8",
        "Korean": "#A8D184",
    },
    height=400,
)

DIALOGUE_SPEC: ChartSpec = ChartSpec(
    title="Was dialogue Provided?",
    chart_type="stacked_bar",
    x_column="content_type",
    y_columns=["Yes", "No"],
    color_map={
        "Yes": "#4F89B5",
        "No": "#D22D27",
    },
    height=400,
)

GENRE_SPEC: ChartSpec = ChartSpec(
    title="Genre",
    chart_type="bar",
    x_column="genre",
    y_columns=["count"],
    color_map={
        "count": "#7FAECC",
    },
    height=400,
)
