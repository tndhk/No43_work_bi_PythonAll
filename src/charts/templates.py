"""Chart templates for Plotly Dash."""
from typing import Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html
from src.charts.plotly_theme import apply_theme


def render_summary_number(
    dataset: pd.DataFrame,
    filters: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> html.Div:
    """Render a summary number card.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (not used in this template)
        params: Optional parameters:
            - value_column: Column name to aggregate (default: first column)
            - agg_func: Aggregation function (default: "sum")

    Returns:
        Dash HTML Div component
    """
    if params is None:
        params = {}

    value_column = params.get("value_column", dataset.columns[0])
    agg_func = params.get("agg_func", "sum")

    # Apply aggregation
    if agg_func == "sum":
        current_value = dataset[value_column].sum()
    elif agg_func == "mean":
        current_value = dataset[value_column].mean()
    elif agg_func == "count":
        current_value = len(dataset)
    elif agg_func == "max":
        current_value = dataset[value_column].max()
    elif agg_func == "min":
        current_value = dataset[value_column].min()
    else:
        current_value = dataset[value_column].sum()

    # Format display
    if current_value >= 1_000_000:
        display = f"{current_value / 1_000_000:.1f}M"
    elif current_value >= 1_000:
        display = f"{current_value / 1_000:.1f}K"
    else:
        display = f"{current_value:,.0f}"

    return html.Div(
        [
            html.Div(
                display,
                className="summary-number-value",
            ),
            html.Div(
                value_column,
                className="summary-number-label",
            ),
        ],
        className="summary-number-container",
    )


def render_bar_chart(
    dataset: pd.DataFrame,
    filters: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> go.Figure:
    """Render a bar chart.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (not used in this template)
        params: Optional parameters:
            - x_column: X-axis column (default: first column)
            - y_column: Y-axis column (default: second column)

    Returns:
        Plotly Figure object
    """
    if params is None:
        params = {}

    x_column = params.get("x_column", dataset.columns[0])
    y_column = params.get("y_column", dataset.columns[1] if len(dataset.columns) > 1 else dataset.columns[0])

    fig = px.bar(
        dataset,
        x=x_column,
        y=y_column,
        title=f"{y_column} by {x_column}",
    )
    fig.update_layout(
        height=400,
        showlegend=False,
    )
    return apply_theme(fig)


def render_line_chart(
    dataset: pd.DataFrame,
    filters: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> go.Figure:
    """Render a line chart.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (not used in this template)
        params: Optional parameters:
            - x_column: X-axis column (default: first column)
            - y_column: Y-axis column (default: second column)

    Returns:
        Plotly Figure object
    """
    if params is None:
        params = {}

    x_column = params.get("x_column", dataset.columns[0])
    y_column = params.get("y_column", dataset.columns[1] if len(dataset.columns) > 1 else dataset.columns[0])

    fig = px.line(
        dataset,
        x=x_column,
        y=y_column,
        title=f"{y_column} over {x_column}",
    )
    fig.update_layout(
        height=400,
        showlegend=False,
    )
    return apply_theme(fig)


def render_pie_chart(
    dataset: pd.DataFrame,
    filters: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> go.Figure:
    """Render a pie chart.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (not used in this template)
        params: Optional parameters:
            - names_column: Category column (default: first column)
            - values_column: Values column (default: second column)

    Returns:
        Plotly Figure object
    """
    if params is None:
        params = {}

    names_column = params.get("names_column", dataset.columns[0])
    values_column = params.get("values_column", dataset.columns[1] if len(dataset.columns) > 1 else dataset.columns[0])

    fig = px.pie(
        dataset,
        names=names_column,
        values=values_column,
        title=f"{values_column} by {names_column}",
    )
    fig.update_layout(
        height=400,
    )
    return apply_theme(fig)


def render_table(
    dataset: pd.DataFrame,
    filters: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> html.Div:
    """Render a data table.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (not used in this template)
        params: Optional parameters (not used)

    Returns:
        Dash HTML Div component with table
    """
    html_table = dataset.to_html(
        classes="table-auto w-full",
        table_id="data-table",
        escape=False,
    )

    return html.Div(
        html.Div(
            html.Div(
                [
                    html.Div(
                        html_table,
                        dangerously_allow_html=True,
                    ),
                ],
            ),
            className="data-table-container",
        ),
    )


def render_pivot_table(
    dataset: pd.DataFrame,
    filters: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> html.Div:
    """Render a pivot table.

    Args:
        dataset: DataFrame to render
        filters: Optional filters (not used in this template)
        params: Optional parameters:
            - index_column: Row column (default: first column)
            - columns_column: Column column (default: second column, optional)
            - values_column: Values column (default: last column)
            - agg_func: Aggregation function (default: "sum")

    Returns:
        Dash HTML Div component with pivot table
    """
    if params is None:
        params = {}

    index_column = params.get("index_column", dataset.columns[0])
    columns_column = params.get("columns_column", dataset.columns[1] if len(dataset.columns) > 1 else None)
    values_column = params.get("values_column", dataset.columns[-1])
    agg_func = params.get("agg_func", "sum")

    # Create pivot table
    if columns_column:
        pivot_table = pd.pivot_table(
            dataset,
            index=index_column,
            columns=columns_column,
            values=values_column,
            aggfunc=agg_func,
            fill_value=0,
        )
    else:
        pivot_table = pd.pivot_table(
            dataset,
            index=index_column,
            values=values_column,
            aggfunc=agg_func,
        )

    html_table = pivot_table.to_html(
        classes="table-auto w-full",
        table_id="pivot-table",
        escape=False,
    )

    return html.Div(
        html.Div(
            html.Div(
                [
                    html.Div(
                        html_table,
                        dangerously_allow_html=True,
                    ),
                ],
            ),
            className="data-table-container",
        ),
    )


# Chart type registry
CHART_TEMPLATES = {
    "summary-number": {
        "name": "Summary Number",
        "description": "大きな数字 + トレンド表示",
        "render": render_summary_number,
    },
    "bar": {
        "name": "Bar Chart",
        "description": "棒グラフ",
        "render": render_bar_chart,
    },
    "line": {
        "name": "Line Chart",
        "description": "折れ線グラフ",
        "render": render_line_chart,
    },
    "pie": {
        "name": "Pie Chart",
        "description": "円グラフ",
        "render": render_pie_chart,
    },
    "table": {
        "name": "Table",
        "description": "テーブル",
        "render": render_table,
    },
    "pivot": {
        "name": "Pivot Table",
        "description": "ピボットテーブル",
        "render": render_pivot_table,
    },
}


def get_chart_template(chart_type: str) -> dict[str, Any]:
    """Get chart template by type.

    Args:
        chart_type: Chart type identifier

    Returns:
        Chart template dictionary
    """
    return CHART_TEMPLATES.get(chart_type, CHART_TEMPLATES["table"])


def get_all_chart_types() -> list[str]:
    """Get all available chart types.

    Returns:
        List of chart type identifiers
    """
    return list(CHART_TEMPLATES.keys())
