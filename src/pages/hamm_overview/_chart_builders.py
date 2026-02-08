"""Chart and table builders for Hamm Overview dashboard.

Extracts rendering logic from _callbacks.py into pure functions:
- build_volume_table: renders volume summary as DataTable
- build_volume_chart: renders volume summary as stacked bar chart
- build_task_table: renders task detail as DataTable
"""
from __future__ import annotations

import pandas as pd
from dash import dash_table, html
import plotly.graph_objects as go

from src.charts.empty_states import create_empty_figure, create_empty_table
from ._constants import (
    COLUMN_MAP,
    PRELIM_LABEL,
    ERV_LABEL,
    VOLUME_TABLE_SPEC,
    VOLUME_CHART_SPEC,
    TASK_TABLE_SPEC,
)


def build_volume_table(df: pd.DataFrame) -> dash_table.DataTable | html.P:
    """Render volume summary DataFrame as a compact DataTable.

    Args:
        df: Volume summary DataFrame with columns: Fiscal Year,
            Fiscal Quarter, ISO Week, Start Date, End Date,
            Prelim, ERV, VOLUME TOTAL.

    Returns:
        A DataTable component, or html.P empty-state placeholder.
    """
    if df.empty:
        return create_empty_table()

    spec = VOLUME_TABLE_SPEC
    display_columns = spec.column_order

    table = dash_table.DataTable(
        data=df[display_columns].to_dict("records"),
        columns=[{"name": c, "id": c} for c in display_columns],
        sort_action=spec.sort_action,
        page_size=spec.page_size,
        style_table=dict(spec.style_table),
        style_cell=dict(spec.style_cell),
        style_header=dict(spec.style_header),
    )
    return table


def build_volume_chart(df: pd.DataFrame) -> go.Figure:
    """Render volume summary DataFrame as a stacked bar chart.

    Args:
        df: Volume summary DataFrame with Start Date, Prelim, ERV columns.

    Returns:
        A go.Figure with stacked bar traces, or empty-state figure.
    """
    if df.empty:
        return create_empty_figure(message="No data available", height=400)

    spec = VOLUME_CHART_SPEC

    fig = go.Figure()

    # Add traces in spec y_columns order (ERV first, then Prelim)
    for y_col in spec.y_columns:
        fig.add_bar(
            x=df[spec.x_column],
            y=df[y_col],
            name=y_col,
            marker_color=spec.color_map[y_col],
        )

    fig.update_layout(
        barmode="stack",
        height=spec.height,
        margin={"l": 30, "r": 10, "t": 20, "b": 60},
        legend={"orientation": "h", "y": -0.2},
        xaxis_title="",
        yaxis_title="",
    )

    return fig


def build_task_table(df: pd.DataFrame) -> dash_table.DataTable | html.P:
    """Render task detail DataFrame as a compact DataTable.

    Computes derived columns (Job Created, Completed / Err, Total Duration)
    from created_at and completed_at, then renders as DataTable.

    Args:
        df: Task detail DataFrame with COLUMN_MAP columns.

    Returns:
        A DataTable component, or html.P empty-state placeholder.
    """
    if df.empty:
        return create_empty_table()

    created_col = COLUMN_MAP["created_at"]
    completed_col = COLUMN_MAP["completed_at"]

    display_df = df.copy()
    display_df["Job Created"] = display_df[created_col].dt.strftime("%Y-%m-%d %H:%M")
    display_df["Completed / Err"] = display_df[completed_col].dt.strftime(
        "%Y-%m-%d %H:%M"
    )

    total_duration = display_df[completed_col] - display_df[created_col]
    total_duration = total_duration.fillna(pd.Timedelta(0))

    display_df["Total Duration"] = total_duration.dt.components.apply(
        lambda row: (
            f"{int(row['days'] * 24 + row['hours']):02d}"
            f":{int(row['minutes']):02d}"
            f":{int(row['seconds']):02d}"
        ),
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

    spec = TASK_TABLE_SPEC
    ordered_columns = spec.column_order

    output_df = pd.DataFrame(
        {
            display_name: display_df[column_name]
            for display_name, column_name in table_columns.items()
        }
    )

    output_df["Job Created"] = display_df["Job Created"]
    output_df["Completed / Err"] = display_df["Completed / Err"]
    output_df["Total Duration"] = display_df["Total Duration"]

    # Sort by Task ID (as numeric)
    output_df = output_df.sort_values(
        by="Task ID",
        key=lambda x: pd.to_numeric(x, errors="coerce").fillna(0),
    )

    table = dash_table.DataTable(
        data=output_df[ordered_columns].to_dict("records"),
        columns=[{"name": c, "id": c} for c in ordered_columns],
        sort_action=spec.sort_action,
        page_size=spec.page_size,
        style_table=dict(spec.style_table),
        style_cell=dict(spec.style_cell),
        style_header=dict(spec.style_header),
    )
    return table
