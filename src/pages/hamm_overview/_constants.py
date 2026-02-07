"""Constants for the Hamm Overview dashboard."""

DASHBOARD_ID: str = "hamm_overview"
DATASET_ID: str = "hamm-dashboard"
ID_PREFIX: str = "hamm-"

# Chart IDs
CHART_ID_VOLUME_TABLE: str = f"{ID_PREFIX}volume-table"
CHART_ID_VOLUME_CHART: str = f"{ID_PREFIX}volume-chart"
CHART_ID_TASK_TABLE: str = f"{ID_PREFIX}task-table"

# KPI Card IDs
CHART_ID_KPI_TOTAL_TASKS: str = f"{ID_PREFIX}kpi-total-tasks"
CHART_ID_KPI_AVG_VIDEO_DURATION: str = f"{ID_PREFIX}kpi-avg-video-duration"

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
    "video_duration": "video_duration",
    "audio_details": "audio location",
}
