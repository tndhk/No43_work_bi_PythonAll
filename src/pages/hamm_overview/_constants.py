"""Constants for HAMM Overview dashboard.

Auto-generated from page_spec.yaml by tools.page_generator,
then manually extended with aliases for backward compatibility.
"""
from src.charts.specs import ChartSpec, TableSpec, COMPACT_STYLE_CELL, COMPACT_STYLE_HEADER

# Dashboard metadata
DASHBOARD_ID: str = "hamm_overview"
DATASET_ID: str = "hamm-dashboard"
ID_PREFIX: str = "hamm-"

# Content type labels
ERV_LABEL: str = "ERV"
PRELIM_LABEL: str = "Prelim"

# ---------------------------------------------------------------------------
# Filter IDs
# ---------------------------------------------------------------------------

FILTER_ID_FILTER_REGION: str = f"{ID_PREFIX}filter-region"
CTRL_ID_FILTER_REGION_CLEAR: str = f"{ID_PREFIX}filter-region-clear"

FILTER_ID_FILTER_YEAR: str = f"{ID_PREFIX}filter-year"
CTRL_ID_FILTER_YEAR_CLEAR: str = f"{ID_PREFIX}filter-year-clear"

FILTER_ID_FILTER_CONTENT_TYPE: str = f"{ID_PREFIX}filter-content-type"
CTRL_ID_FILTER_CONTENT_TYPE_CLEAR: str = f"{ID_PREFIX}filter-content-type-clear"

FILTER_ID_FILTER_ORIGINAL_LANGUAGE: str = f"{ID_PREFIX}filter-original-language"
CTRL_ID_FILTER_ORIGINAL_LANGUAGE_CLEAR: str = f"{ID_PREFIX}filter-original-language-clear"

FILTER_ID_FILTER_DIALOGUE: str = f"{ID_PREFIX}filter-dialogue"
CTRL_ID_FILTER_DIALOGUE_CLEAR: str = f"{ID_PREFIX}filter-dialogue-clear"

FILTER_ID_FILTER_GENRE: str = f"{ID_PREFIX}filter-genre"
CTRL_ID_FILTER_GENRE_CLEAR: str = f"{ID_PREFIX}filter-genre-clear"

FILTER_ID_FILTER_ERROR_TYPE: str = f"{ID_PREFIX}filter-error-type"
CTRL_ID_FILTER_ERROR_TYPE_CLEAR: str = f"{ID_PREFIX}filter-error-type-clear"

FILTER_ID_FILTER_MONTH: str = f"{ID_PREFIX}filter-month"
FILTER_ID_FILTER_TASK_ID: str = f"{ID_PREFIX}filter-task-id"
FILTER_ID_FILTER_ERROR_CODE: str = f"{ID_PREFIX}filter-error-code"
FILTER_ID_FILTER_CADENCE: str = f"{ID_PREFIX}filter-cadence"

# Short aliases expected by tests
FILTER_ID_REGION: str = FILTER_ID_FILTER_REGION
FILTER_ID_YEAR: str = FILTER_ID_FILTER_YEAR
FILTER_ID_CONTENT_TYPE: str = FILTER_ID_FILTER_CONTENT_TYPE
FILTER_ID_ORIGINAL_LANGUAGE: str = FILTER_ID_FILTER_ORIGINAL_LANGUAGE
FILTER_ID_DIALOGUE: str = FILTER_ID_FILTER_DIALOGUE
FILTER_ID_GENRE: str = FILTER_ID_FILTER_GENRE
FILTER_ID_ERROR_TYPE: str = FILTER_ID_FILTER_ERROR_TYPE

# Clear control ID aliases (short form)
CTRL_ID_CLEAR_REGION: str = f"{ID_PREFIX}ctrl-clear-region"
CTRL_ID_CLEAR_YEAR: str = f"{ID_PREFIX}ctrl-clear-year"
CTRL_ID_CLEAR_CONTENT_TYPE: str = f"{ID_PREFIX}ctrl-clear-content-type"
CTRL_ID_CLEAR_ORIGINAL_LANGUAGE: str = f"{ID_PREFIX}ctrl-clear-original-language"
CTRL_ID_CLEAR_DIALOGUE: str = f"{ID_PREFIX}ctrl-clear-dialogue"
CTRL_ID_CLEAR_GENRE: str = f"{ID_PREFIX}ctrl-clear-genre"
CTRL_ID_CLEAR_ERROR_TYPE: str = f"{ID_PREFIX}ctrl-clear-error-type"

# ---------------------------------------------------------------------------
# Component IDs
# ---------------------------------------------------------------------------

KPI_ID_KPI_TOTAL_SCREENS: str = f"{ID_PREFIX}kpi-total-screens"
KPI_ID_KPI_TOTAL_ERV: str = f"{ID_PREFIX}kpi-total-erv"
KPI_ID_KPI_TOTAL_PRELIM: str = f"{ID_PREFIX}kpi-total-prelim"

# KPI chart ID aliases
CHART_ID_KPI_TOTAL_SCREENS: str = KPI_ID_KPI_TOTAL_SCREENS
CHART_ID_KPI_TOTAL_ERV: str = KPI_ID_KPI_TOTAL_ERV
CHART_ID_KPI_TOTAL_PRELIM: str = KPI_ID_KPI_TOTAL_PRELIM

TABLE_ID_VOLUME_TABLE: str = f"{ID_PREFIX}volume-table"
CHART_ID_VOLUME_CHART: str = f"{ID_PREFIX}volume-chart"
TABLE_ID_TASK_TABLE: str = f"{ID_PREFIX}task-table"
TABLE_ID_LANGUAGE_TABLE: str = f"{ID_PREFIX}language-table"

CHART_ID_ERROR_RATIO: str = f"{ID_PREFIX}error-ratio"
CHART_ID_ERROR_BY_SCREENER: str = f"{ID_PREFIX}error-by-screener"
CHART_ID_USER_BREAKDOWN: str = f"{ID_PREFIX}user-breakdown"
CHART_ID_BREAKDOWN: str = f"{ID_PREFIX}hamm-breakdown"

CHART_ID_METADATA_ORIGINAL_LANGUAGE: str = f"{ID_PREFIX}metadata-original-language"
CHART_ID_METADATA_DIALOGUE: str = f"{ID_PREFIX}metadata-dialogue"
CHART_ID_METADATA_GENRE: str = f"{ID_PREFIX}metadata-genre"

# Table/Chart ID aliases (CHART_ID_* form for tables and hamm breakdown)
CHART_ID_VOLUME_TABLE: str = TABLE_ID_VOLUME_TABLE
CHART_ID_TASK_TABLE: str = TABLE_ID_TASK_TABLE
CHART_ID_LANGUAGE_TABLE: str = TABLE_ID_LANGUAGE_TABLE
CHART_ID_HAMM_BREAKDOWN: str = CHART_ID_BREAKDOWN

# ---------------------------------------------------------------------------
# Clear callback pairs: (filter_id, clear_button_id)
# ---------------------------------------------------------------------------
CLEAR_PAIRS: list[tuple[str, str]] = [
    (FILTER_ID_FILTER_REGION, CTRL_ID_FILTER_REGION_CLEAR),
    (FILTER_ID_FILTER_YEAR, CTRL_ID_FILTER_YEAR_CLEAR),
    (FILTER_ID_FILTER_CONTENT_TYPE, CTRL_ID_FILTER_CONTENT_TYPE_CLEAR),
    (FILTER_ID_FILTER_ORIGINAL_LANGUAGE, CTRL_ID_FILTER_ORIGINAL_LANGUAGE_CLEAR),
    (FILTER_ID_FILTER_DIALOGUE, CTRL_ID_FILTER_DIALOGUE_CLEAR),
    (FILTER_ID_FILTER_GENRE, CTRL_ID_FILTER_GENRE_CLEAR),
    (FILTER_ID_FILTER_ERROR_TYPE, CTRL_ID_FILTER_ERROR_TYPE_CLEAR),
]

# ---------------------------------------------------------------------------
# Derived column names
# ---------------------------------------------------------------------------
DERIVED_YEAR: str = "_year"
DERIVED_MONTH: str = "_month"
DERIVED_FISCAL_YEAR: str = "_fiscal_year"
DERIVED_FISCAL_QUARTER: str = "_fiscal_quarter"
DERIVED_ISO_WEEK: str = "_iso_week"
DERIVED_START_DATE: str = "_start_date"
DERIVED_END_DATE: str = "_end_date"
DERIVED_VIDEO_DURATION_SECONDS: str = "_video_duration_seconds"

# ---------------------------------------------------------------------------
# Mapping from logical keys to DataFrame column names
# ---------------------------------------------------------------------------
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
    "language_count": "number of languages",
    "additional_languages": "additional languages",
}

# ---------------------------------------------------------------------------
# Chart Specs (declarative definitions)
# ---------------------------------------------------------------------------

VOLUME_CHART_SPEC: ChartSpec = ChartSpec(
    title="Volume Chart",
    chart_type="stacked_bar",
    x_column="Start Date",
    y_columns=["Completed", "Invalid"],
    color_map={"Completed": "#2d6a2e", "Invalid": "#9ca3af"},
    text_template="%{y}",
    height=460,
    show_legend=True,
    orientation="v",
)

ERROR_RATIO_SPEC: ChartSpec = ChartSpec(
    title="Issues Ratio (HAMM vs Human Intervention)",
    chart_type="pie",
    x_column="error_type",
    y_columns=["count"],
    height=460,
    show_legend=True,
    orientation="v",
)

ERROR_BY_SCREENER_SPEC: ChartSpec = ChartSpec(
    title="Intervention per Screener Type",
    chart_type="stacked_bar",
    x_column="video_type_description",
    y_columns=["User", "HAMM"],
    color_map={"HAMM": "#5f8fc7", "User": "#e57f7f"},
    text_template="%{y}",
    height=460,
    show_legend=True,
    orientation="v",
)

USER_BREAKDOWN_SPEC: ChartSpec = ChartSpec(
    title="User Intervention Breakdown",
    chart_type="bar",
    x_column="error_description",
    y_columns=["count"],
    color_map={"count": "#e57f7f"},
    text_template="%{y}",
    height=460,
    show_legend=False,
    orientation="v",
)

BREAKDOWN_SPEC: ChartSpec = ChartSpec(
    title="HAMM Intervention Breakdown",
    chart_type="bar",
    x_column="error_description",
    y_columns=["count"],
    color_map={"count": "#5f8fc7"},
    text_template="%{y}",
    height=460,
    show_legend=False,
    orientation="v",
)

METADATA_ORIGINAL_LANGUAGE_SPEC: ChartSpec = ChartSpec(
    title="Original Language",
    chart_type="pie",
    x_column="original_language",
    y_columns=["count"],
    color_map={"Japanese": "#6EA5C8", "Korean": "#A8D184"},
    height=460,
    show_legend=True,
    orientation="v",
)

METADATA_DIALOGUE_SPEC: ChartSpec = ChartSpec(
    title="Was dialogue Provided?",
    chart_type="stacked_bar",
    x_column="content_type",
    y_columns=["Yes", "No"],
    color_map={"No": "#D22D27", "Yes": "#4F89B5"},
    text_template="%{y}",
    height=460,
    show_legend=True,
    orientation="v",
)

METADATA_GENRE_SPEC: ChartSpec = ChartSpec(
    title="Genre",
    chart_type="bar",
    x_column="genre",
    y_columns=["count"],
    color_map={"count": "#7FAECC"},
    text_template="%{y}",
    height=460,
    show_legend=False,
    orientation="v",
)

# Short aliases for chart specs
HAMM_BREAKDOWN_SPEC: ChartSpec = BREAKDOWN_SPEC
ORIGINAL_LANGUAGE_SPEC: ChartSpec = METADATA_ORIGINAL_LANGUAGE_SPEC
DIALOGUE_SPEC: ChartSpec = METADATA_DIALOGUE_SPEC
GENRE_SPEC: ChartSpec = METADATA_GENRE_SPEC

# ---------------------------------------------------------------------------
# Table Specs (declarative definitions, compact styling)
# ---------------------------------------------------------------------------

VOLUME_TABLE_SPEC: TableSpec = TableSpec(
    title="Volume Summary",
    style_table={"height": "400px", "overflowX": "auto", "overflowY": "auto"},
    style_cell=COMPACT_STYLE_CELL,
    style_header=COMPACT_STYLE_HEADER,
    style_data_conditional=[],
    sort_action="native",
    page_size=20,
    column_order=[
        "Fiscal Year", "Fiscal Quarter", "ISO Week",
        "Start Date", "End Date", "Completed", "Invalid", "VOLUME TOTAL",
    ],
    filter_action="none",
)

TASK_TABLE_SPEC: TableSpec = TableSpec(
    title="Task Details",
    style_table={"overflowX": "auto"},
    style_cell=COMPACT_STYLE_CELL,
    style_header=COMPACT_STYLE_HEADER,
    style_data_conditional=[],
    sort_action="native",
    page_size=20,
    column_order=[
        "Task ID", "Task Name", "Content Type", "Task Status",
        "Source File Duration", "Audio Details",
        "Job Created", "Completed / Err", "Total Duration",
    ],
    filter_action="none",
)

LANGUAGE_TABLE_SPEC: TableSpec = TableSpec(
    title="Language per Task",
    style_table={"overflowX": "auto"},
    style_cell=COMPACT_STYLE_CELL,
    style_header=COMPACT_STYLE_HEADER,
    style_data_conditional=[
        {
            "if": {"filter_query": '{Status} = "Completed"'},
            "backgroundColor": "#d4edda",
        },
        {
            "if": {"filter_query": '{Content Type} = "ERV"'},
            "backgroundColor": "#f8d7da",
        },
        {
            "if": {"filter_query": '{Content Type} = "Prelim"'},
            "backgroundColor": "#f8d7da",
        },
    ],
    sort_action="native",
    page_size=20,
    column_order=[
        "Task ID", "Task Name", "Content Type", "Status",
        "Language Count", "Additional Languages",
    ],
    filter_action="none",
)
