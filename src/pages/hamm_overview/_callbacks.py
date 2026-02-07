"""Callbacks for Hamm Overview dashboard."""
from typing import Iterable
import pandas as pd
from dash import callback, Input, Output, html, dash_table
import plotly.graph_objects as go

from src.data.parquet_reader import ParquetReader
from src.components.cards import create_kpi_card
from ._constants import (
    COLUMN_MAP,
    CHART_ID_VOLUME_TABLE,
    CHART_ID_VOLUME_CHART,
    CHART_ID_TASK_TABLE,
    CHART_ID_KPI_TOTAL_TASKS,
    CHART_ID_KPI_AVG_VIDEO_DURATION,
    FILTER_ID_REGION,
    FILTER_ID_YEAR,
    FILTER_ID_MONTH,
    FILTER_ID_TASK_ID,
    FILTER_ID_CONTENT_TYPE,
    FILTER_ID_ORIGINAL_LANGUAGE,
    FILTER_ID_DIALOGUE,
    FILTER_ID_GENRE,
    FILTER_ID_ERROR_CODE,
    FILTER_ID_ERROR_TYPE,
    FILTER_ID_CADENCE,
    DERIVED_FISCAL_YEAR,
    DERIVED_FISCAL_QUARTER,
    DERIVED_ISO_WEEK,
    DERIVED_START_DATE,
    DERIVED_END_DATE,
)
from ._data_loader import (
    resolve_dataset_id_for_dashboard,
    load_and_filter_data,
    add_cadence_columns,
)


PRELIM_LABEL = "Prelim"
ERV_LABEL = "ERV"
SORT_START_COL = "_sort_start_dt"


def _ensure_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _build_volume_table(df: pd.DataFrame) -> html.Div:
    if df.empty:
        return html.P("No data available", className="text-muted")

    display_columns = [
        "Fiscal Year",
        "Fiscal Quarter",
        "ISO Week",
        "Start Date",
        "End Date",
        PRELIM_LABEL,
        ERV_LABEL,
        "VOLUME TOTAL",
    ]

    table_component = dash_table.DataTable(
        data=df[display_columns].to_dict("records"),
        columns=[{"name": c, "id": c} for c in display_columns],
        sort_action="native",
        sort_by=[{"column_id": "Start Date", "direction": "desc"}],
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "8px"},
        style_header={"fontWeight": "bold"},
    )
    return table_component


def _build_volume_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if df.empty:
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
        )
        fig.update_layout(height=400)
        return fig

    fig.add_bar(
        x=df["Start Date"],
        y=df[ERV_LABEL],
        name=ERV_LABEL,
        marker_color="#f6b3b3",
    )
    fig.add_bar(
        x=df["Start Date"],
        y=df[PRELIM_LABEL],
        name=PRELIM_LABEL,
        marker_color="#e57f7f",
    )

    fig.update_layout(
        barmode="stack",
        height=400,
        margin={"l": 30, "r": 10, "t": 20, "b": 60},
        legend={"orientation": "h", "y": -0.2},
        xaxis_title="",
        yaxis_title="",
    )

    return fig


def _build_task_table(df: pd.DataFrame) -> html.Div:
    if df.empty:
        return html.P("No data available", className="text-muted")

    created_col = COLUMN_MAP["created_at"]
    completed_col = COLUMN_MAP["completed_at"]

    display_df = df.copy()
    display_df["Job Created"] = display_df[created_col].dt.strftime("%Y-%m-%d %H:%M")
    display_df["Completed / Err"] = display_df[completed_col].dt.strftime("%Y-%m-%d %H:%M")

    total_duration = display_df[completed_col] - display_df[created_col]
    total_duration = total_duration.fillna(pd.Timedelta(0))

    display_df["Total Duration"] = total_duration.dt.components.apply(
        lambda row: f"{int(row['days'] * 24 + row['hours']):02d}:{int(row['minutes']):02d}:{int(row['seconds']):02d}",
        axis=1,
    )

    missing_completed = display_df[completed_col].isna()
    display_df.loc[missing_completed, "Total Duration"] = ""

    table_columns = {
        "Task ID": COLUMN_MAP["id"],
        "Task Name": COLUMN_MAP["title"],
        "Content Type": COLUMN_MAP["content_type"],
        "Task Status": COLUMN_MAP["status"],
        "Source File Duration": COLUMN_MAP["video_duration"],
        "Audio Details": COLUMN_MAP["audio_details"],
    }

    ordered_columns = [
        "Task ID",
        "Task Name",
        "Content Type",
        "Task Status",
        "Source File Duration",
        "Audio Details",
        "Job Created",
        "Completed / Err",
        "Total Duration",
    ]

    output_df = pd.DataFrame({
        display_name: display_df[column_name]
        for display_name, column_name in table_columns.items()
    })

    output_df["Job Created"] = display_df["Job Created"]
    output_df["Completed / Err"] = display_df["Completed / Err"]
    output_df["Total Duration"] = display_df["Total Duration"]

    table_component = dash_table.DataTable(
        data=output_df[ordered_columns].to_dict("records"),
        columns=[{"name": c, "id": c} for c in ordered_columns],
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "8px"},
        style_header={"fontWeight": "bold"},
    )
    return table_component


def _normalize_filter_values(*values: Iterable) -> list[list]:
    return [_ensure_list(v) for v in values]

def _parse_start_date(value: str) -> pd.Timestamp:
    return pd.to_datetime(value, format="%d-%b-%y", errors="coerce")


def _strip_sort_column(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[SORT_START_COL], errors="ignore")


def _build_volume_summary(df: pd.DataFrame, cadence: str) -> pd.DataFrame:
    df = add_cadence_columns(df, cadence)

    group_cols = [
        DERIVED_FISCAL_YEAR,
        DERIVED_FISCAL_QUARTER,
        DERIVED_ISO_WEEK,
        DERIVED_START_DATE,
        DERIVED_END_DATE,
        COLUMN_MAP["content_type"],
    ]

    summary = (
        df.groupby(group_cols)[COLUMN_MAP["id"]]
        .nunique()
        .reset_index(name="count")
    )

    pivot = summary.pivot_table(
        index=[
            DERIVED_FISCAL_YEAR,
            DERIVED_FISCAL_QUARTER,
            DERIVED_ISO_WEEK,
            DERIVED_START_DATE,
            DERIVED_END_DATE,
        ],
        columns=COLUMN_MAP["content_type"],
        values="count",
        fill_value=0,
    ).reset_index()

    for label in (PRELIM_LABEL, ERV_LABEL):
        if label not in pivot.columns:
            pivot[label] = 0

    pivot["VOLUME TOTAL"] = pivot[PRELIM_LABEL] + pivot[ERV_LABEL]

    pivot = pivot.rename(columns={
        DERIVED_FISCAL_YEAR: "Fiscal Year",
        DERIVED_FISCAL_QUARTER: "Fiscal Quarter",
        DERIVED_ISO_WEEK: "ISO Week",
        DERIVED_START_DATE: "Start Date",
        DERIVED_END_DATE: "End Date",
    })

    pivot = pivot[[
        "Fiscal Year",
        "Fiscal Quarter",
        "ISO Week",
        "Start Date",
        "End Date",
        PRELIM_LABEL,
        ERV_LABEL,
        "VOLUME TOTAL",
    ]]

    pivot[SORT_START_COL] = pivot["Start Date"].apply(_parse_start_date)

    pivot = pivot.sort_values(by=[SORT_START_COL, "End Date"], kind="mergesort")

    return pivot


@callback(
    Output(CHART_ID_KPI_TOTAL_TASKS, "children"),
    Output(CHART_ID_KPI_AVG_VIDEO_DURATION, "children"),
    Output(CHART_ID_VOLUME_TABLE, "children"),
    Output(CHART_ID_VOLUME_CHART, "figure"),
    Output(CHART_ID_TASK_TABLE, "children"),
    Input(FILTER_ID_REGION, "value"),
    Input(FILTER_ID_YEAR, "value"),
    Input(FILTER_ID_MONTH, "value"),
    Input(FILTER_ID_TASK_ID, "value"),
    Input(FILTER_ID_CONTENT_TYPE, "value"),
    Input(FILTER_ID_ORIGINAL_LANGUAGE, "value"),
    Input(FILTER_ID_DIALOGUE, "value"),
    Input(FILTER_ID_GENRE, "value"),
    Input(FILTER_ID_ERROR_CODE, "value"),
    Input(FILTER_ID_ERROR_TYPE, "value"),
    Input(FILTER_ID_CADENCE, "value"),
)
def update_dashboard(
    region_values,
    year_values,
    month_values,
    task_id_value,
    content_type_values,
    original_language_values,
    dialogue_values,
    genre_values,
    error_code_values,
    error_type_values,
    cadence_value,
):
    reader = ParquetReader()
    dataset_id = resolve_dataset_id_for_dashboard()

    normalized = _normalize_filter_values(
        region_values,
        year_values,
        month_values,
        task_id_value,
        content_type_values,
        original_language_values,
        dialogue_values,
        genre_values,
        error_code_values,
        error_type_values,
    )

    (
        region_values,
        year_values,
        month_values,
        task_ids,
        content_type_values,
        original_language_values,
        dialogue_values,
        genre_values,
        error_code_values,
        error_type_values,
    ) = normalized

    cadence = cadence_value or "weekly"

    try:
        df = load_and_filter_data(
            reader,
            dataset_id,
            region_values,
            year_values,
            month_values,
            task_ids,
            content_type_values,
            original_language_values,
            dialogue_values,
            genre_values,
            error_code_values,
            error_type_values,
        )

        total_tasks = df[COLUMN_MAP["id"]].nunique()
        kpi_total_tasks = create_kpi_card("Total Tasks", f"{total_tasks:,}")

        avg_seconds = df["_video_duration_seconds"].mean()
        if pd.isna(avg_seconds):
            avg_duration_str = "N/A"
        else:
            mins, secs = divmod(int(avg_seconds), 60)
            hrs, mins = divmod(mins, 60)
            avg_duration_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        kpi_avg_duration = create_kpi_card("Average Video Duration", avg_duration_str)

        volume_summary = _build_volume_summary(df, cadence)
        volume_chart_df = _strip_sort_column(volume_summary)
        volume_table_df = _strip_sort_column(
            volume_summary.sort_values(
                by=[SORT_START_COL],
                ascending=False,
                kind="mergesort",
            )
        )

        volume_table = _build_volume_table(volume_table_df)
        volume_chart = _build_volume_chart(volume_chart_df)
        task_table = _build_task_table(df)

        return kpi_total_tasks, kpi_avg_duration, volume_table, volume_chart, task_table

    except Exception as exc:
        error_msg = html.P(f"Error loading data: {exc}", className="text-danger")
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Error loading data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
        )
        empty_fig.update_layout(height=400)
        kpi_error = create_kpi_card("Total Tasks", "0")
        kpi_error_duration = create_kpi_card("Average Video Duration", "N/A")
        return kpi_error, kpi_error_duration, error_msg, empty_fig, error_msg
