#!/usr/bin/env python3
"""Scaffold a new Dash BI dashboard page.

Generates a Tier-2 page package under src/pages/{name}/ with all
canonical files following the project conventions.

Usage:
    python3 scripts/scaffold_page.py \\
        --name sales_report \\
        --title "Sales Report Dashboard" \\
        --path "/sales-report" \\
        --dataset-id "sales-data" \\
        --prefix "sr-"
"""
import argparse
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Placeholder tokens (avoids collisions with Python f-strings / $ signs)
# ---------------------------------------------------------------------------
_PH_PAGE_NAME = "__PAGE_NAME__"
_PH_TITLE = "__TITLE__"
_PH_PATH = "__PATH__"
_PH_DATASET_ID = "__DATASET_ID__"
_PH_ID_PREFIX = "__ID_PREFIX__"
_PH_DASHBOARD_ID = "__DASHBOARD_ID__"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TPL_INIT = '''\
"""{title} page."""
import dash

from ._layout import build_layout
from . import _callbacks  # noqa: F401


dash.register_page(
    __name__,
    path="__PATH__",
    name="__TITLE__",
    order=99,
    layout=build_layout,
)
'''

TPL_CONSTANTS = '''\
"""Constants for the __TITLE__ page.

Centralizes dataset identifiers, column name mappings, ID prefixes,
and declarative ChartSpec / TableSpec definitions.
"""

from src.charts.specs import ChartSpec, TableSpec, DEFAULT_STYLE_TABLE, DEFAULT_STYLE_CELL, DEFAULT_STYLE_HEADER

# Dashboard identifier (used for config lookup)
DASHBOARD_ID: str = "__DASHBOARD_ID__"

# S3/Parquet dataset identifier (legacy fallback)
DATASET_ID: str = "__DATASET_ID__"

# Component ID namespace prefix (for avoiding collisions with other pages)
ID_PREFIX: str = "__ID_PREFIX__"

# Chart IDs used in this dashboard
CHART_ID_KPI_PRIMARY: str = f"{ID_PREFIX}kpi-primary"
CHART_ID_KPI_SECONDARY: str = f"{ID_PREFIX}kpi-secondary"
CHART_ID_MAIN_CHART: str = f"{ID_PREFIX}chart-main"
CHART_ID_SUB_CHART: str = f"{ID_PREFIX}chart-sub"
CHART_ID_DATA_TABLE: str = f"{ID_PREFIX}data-table"

# Mapping from logical filter/column key to the actual DataFrame column name.
COLUMN_MAP: dict[str, str] = {
    "date": "Date",
    "category": "Category",
    "value": "Value",
}

# ----- Control IDs (Clear buttons) -----
CTRL_ID_CLEAR_CATEGORY: str = f"{ID_PREFIX}ctrl-clear-category"

# Filter IDs (for reference in clear pairs)
FILTER_ID_CATEGORY: str = f"{ID_PREFIX}filter-category"

# Clear button to filter mapping (used by register_clear_callbacks)
CLEAR_PAIRS: list[tuple[str, str]] = [
    (FILTER_ID_CATEGORY, CTRL_ID_CLEAR_CATEGORY),
]

# ---------------------------------------------------------------------------
# Chart / Table Specs (declarative definitions)
# ---------------------------------------------------------------------------

MAIN_CHART_SPEC: ChartSpec = ChartSpec(
    title="Main Chart",
    chart_type="bar",
    x_column=COLUMN_MAP["category"],
    y_columns=[COLUMN_MAP["value"]],
    show_legend=False,
    height=460,
)

DETAIL_TABLE_SPEC: TableSpec = TableSpec(
    title="Detailed Data",
    style_table=DEFAULT_STYLE_TABLE,
    style_cell=DEFAULT_STYLE_CELL,
    style_header=DEFAULT_STYLE_HEADER,
    style_data_conditional=[],
    page_size=20,
    column_order=[
        COLUMN_MAP["date"],
        COLUMN_MAP["category"],
        COLUMN_MAP["value"],
    ],
)
'''

TPL_DATA_LOADER = '''\
"""Data loading and filtering logic for __TITLE__.

Extracts data access concerns from the page module so that layout()
and update_dashboard() remain thin UI-only functions.
"""
import pandas as pd

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.data_source_registry import resolve_dataset_id
from src.data.filter_engine import apply_filters, extract_unique_values
from src.utils.filter_helpers import build_filter_set_from_map
from ._constants import (
    COLUMN_MAP,
    DASHBOARD_ID,
    CHART_ID_KPI_PRIMARY,
    CHART_ID_KPI_SECONDARY,
    CHART_ID_MAIN_CHART,
    CHART_ID_SUB_CHART,
    CHART_ID_DATA_TABLE,
)


def resolve_dataset_id_for_dashboard() -> str:
    """Resolve the dataset ID for all charts in this dashboard.

    Ensures every chart ID maps to exactly one dataset ID.
    """
    chart_ids = [
        CHART_ID_KPI_PRIMARY,
        CHART_ID_KPI_SECONDARY,
        CHART_ID_MAIN_CHART,
        CHART_ID_SUB_CHART,
        CHART_ID_DATA_TABLE,
    ]
    dataset_ids = {resolve_dataset_id(DASHBOARD_ID, chart_id) for chart_id in chart_ids}
    if len(dataset_ids) != 1:
        raise ValueError(
            f"Multiple dataset IDs found for {DASHBOARD_ID} dashboard: "
            f"{sorted(dataset_ids)}"
        )
    return next(iter(dataset_ids))


def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:
    """Load filter option values from cached dataset.

    Returns a dict with keys:
        categories, min_date, max_date

    On any exception the function returns safe defaults (empty lists / None)
    so that the layout can still render.
    """
    try:
        df = get_cached_dataset(reader, dataset_id)

        date_col = COLUMN_MAP["date"]
        category_col = COLUMN_MAP["category"]

        # Strip timezone for filter compatibility
        df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.tz_convert(None)
        df["DateOnly"] = df[date_col].dt.date

        # Extract unique category values (exclude NaN)
        categories = extract_unique_values(df, category_col)

        # Extract date range
        if len(df) > 0:
            min_date = df["DateOnly"].min().isoformat()
            max_date = df["DateOnly"].max().isoformat()
        else:
            min_date = None
            max_date = None

        return {
            "categories": categories,
            "min_date": min_date,
            "max_date": max_date,
        }

    except Exception:
        return {
            "categories": [],
            "min_date": None,
            "max_date": None,
        }


def load_and_filter_data(
    reader: ParquetReader,
    dataset_id: str,
    start_date,
    end_date,
    category_values,
) -> pd.DataFrame:
    """Load dataset and apply all filter criteria.

    Args:
        reader: ParquetReader instance.
        dataset_id: S3 dataset identifier.
        start_date: ISO date string (YYYY-MM-DD) or None.
        end_date: ISO date string (YYYY-MM-DD) or None.
        category_values: List of category strings or None/[].

    Returns:
        Filtered DataFrame with timezone-naive Date column and DateOnly column.
    """
    df = get_cached_dataset(reader, dataset_id)

    date_col = COLUMN_MAP["date"]

    # Strip timezone for filter compatibility (Parquet returns UTC-aware)
    df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.tz_convert(None)
    df["DateOnly"] = df[date_col].dt.date

    # Build FilterSet using shared helper
    filters = build_filter_set_from_map(
        column_map=COLUMN_MAP,
        filter_pairs=[
            ("category", category_values),
        ],
        date_range=("date", start_date, end_date) if start_date and end_date else None,
    )

    return apply_filters(df, filters)
'''

TPL_FILTERS = '''\
"""Filter UI layout builder for __TITLE__.

Extracts the filter UI construction logic from layout() into a
standalone, testable function.
"""
import dash_bootstrap_components as dbc

from src.components.filters import create_date_range_filter, create_category_filter
from ._constants import ID_PREFIX


def build_filter_layout(opts: dict) -> list:
    """Build the filter section of the layout.

    Args:
        opts: Dict returned by load_filter_options(), containing
            min_date, max_date, categories.

    Returns:
        List of dbc.Row components for the filter section.
    """
    # Row 0: Date, Category
    top_row = dbc.Row([
        dbc.Col([
            create_date_range_filter(
                filter_id=f"{ID_PREFIX}filter-date",
                column_name="Date Range",
                min_date=opts["min_date"],
                max_date=opts["max_date"],
            ),
        ], md=4),
        dbc.Col([
            create_category_filter(
                filter_id=f"{ID_PREFIX}filter-category",
                column_name="Category",
                options=opts["categories"],
                multi=True,
            ),
        ], md=4),
    ], className="mb-3")

    return [top_row]
'''

TPL_LAYOUT = '''\
"""__TITLE__ layout module."""
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.data.parquet_reader import ParquetReader
from ._constants import (
    CHART_ID_KPI_PRIMARY,
    CHART_ID_KPI_SECONDARY,
    CHART_ID_MAIN_CHART,
    CHART_ID_SUB_CHART,
    CHART_ID_DATA_TABLE,
    MAIN_CHART_SPEC,
    DETAIL_TABLE_SPEC,
)
from ._data_loader import load_filter_options, resolve_dataset_id_for_dashboard
from ._filters import build_filter_layout


def build_layout():
    """Build the dashboard layout.

    Returns:
        Dash layout component tree with filters, KPI cards, charts, and data table.
    """
    # Load data to get available options for filters
    reader = ParquetReader()
    dataset_id = resolve_dataset_id_for_dashboard()
    options = load_filter_options(reader, dataset_id)

    # Build filter rows
    filter_rows = build_filter_layout(options)

    return html.Div([
        html.H1("__TITLE__", className="mb-4"),

        # Filters
        *filter_rows,

        # KPI Cards
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    html.Div(id=CHART_ID_KPI_PRIMARY),
                ], md=6),
                dbc.Col([
                    html.Div(id=CHART_ID_KPI_SECONDARY),
                ], md=6),
            ], className="mb-4"),
        ]),

        # Charts
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(MAIN_CHART_SPEC.title, className="card-header"),
                        dbc.CardBody([
                            dcc.Graph(
                                id=CHART_ID_MAIN_CHART,
                                className="chart-density-graph",
                                config={"displayModeBar": False, "responsive": True},
                            ),
                        ]),
                    ], className="chart-density-card"),
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(
                                id=CHART_ID_SUB_CHART,
                                className="chart-density-graph",
                                config={"displayModeBar": False, "responsive": True},
                            ),
                        ]),
                    ], className="chart-density-card"),
                ], md=6),
            ], className="mb-4 chart-density-row"),
        ]),

        # Data Table
        dcc.Loading([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(DETAIL_TABLE_SPEC.title, className="card-header"),
                        dbc.CardBody([
                            html.Div(id=CHART_ID_DATA_TABLE),
                        ]),
                    ]),
                ], md=12),
            ]),
        ]),
    ], className="page-container")
'''

TPL_CALLBACKS = '''\
"""__TITLE__ callbacks module.

Thin orchestration layer: data loading -> aggregation -> shared builders.
All chart/table rendering uses the shared build_chart / build_table
infrastructure with declarative Specs defined in _constants.py.
"""
from dash import callback, Input, Output

from src.data.parquet_reader import ParquetReader
from src.components.cards import create_kpi_card
from src.charts.empty_states import create_empty_figure, create_error_figure, create_empty_table
from src.utils.callback_helpers import register_clear_callbacks
from ._constants import (
    CHART_ID_KPI_PRIMARY,
    CHART_ID_KPI_SECONDARY,
    CHART_ID_MAIN_CHART,
    CHART_ID_SUB_CHART,
    CHART_ID_DATA_TABLE,
    COLUMN_MAP,
    ID_PREFIX,
    CLEAR_PAIRS,
)
from ._data_loader import load_and_filter_data, resolve_dataset_id_for_dashboard
from ._chart_builders import (
    build_main_chart,
    build_detail_table,
)


@callback(
    [
        Output(CHART_ID_KPI_PRIMARY, "children"),
        Output(CHART_ID_KPI_SECONDARY, "children"),
        Output(CHART_ID_MAIN_CHART, "figure"),
        Output(CHART_ID_SUB_CHART, "figure"),
        Output(CHART_ID_DATA_TABLE, "children"),
    ],
    [
        Input(f"{ID_PREFIX}filter-date", "start_date"),
        Input(f"{ID_PREFIX}filter-date", "end_date"),
        Input(f"{ID_PREFIX}filter-category", "value"),
    ],
)
def update_dashboard(start_date, end_date, category_values):
    """Update dashboard components based on filters.

    Args:
        start_date: Start date from date range filter (ISO string or None)
        end_date: End date from date range filter (ISO string or None)
        category_values: Selected categories from dropdown (list or None)

    Returns:
        Tuple of (kpi_primary, kpi_secondary, main_fig, sub_fig, table_component)
    """
    reader = ParquetReader()

    try:
        # Load and filter data
        dataset_id = resolve_dataset_id_for_dashboard()

        filtered_df = load_and_filter_data(
            reader, dataset_id, start_date, end_date, category_values
        )

        if len(filtered_df) == 0:
            # Empty state using shared functions
            empty_fig = create_empty_figure(
                message="No data available for selected filters"
            )

            return (
                create_kpi_card("Primary KPI", "0"),
                create_kpi_card("Secondary KPI", "0"),
                empty_fig,
                empty_fig,
                create_empty_table(),
            )

        value_col = COLUMN_MAP["value"]

        # Calculate KPIs
        total_value = filtered_df[value_col].sum()
        record_count = len(filtered_df)

        # KPI Cards
        kpi_primary = create_kpi_card("Primary KPI", f"{total_value:,.0f}")
        kpi_secondary = create_kpi_card("Secondary KPI", f"{record_count:,}")

        # Build charts using chart_builders
        main_fig = build_main_chart(filtered_df)

        # Build data table
        _, table_component = build_detail_table(filtered_df)

        return (
            kpi_primary,
            kpi_secondary,
            main_fig,
            main_fig,  # TODO: Replace with build_sub_chart
            table_component,
        )

    except Exception as e:
        # Error state using shared functions
        error_fig = create_error_figure(error=str(e))

        return (
            create_kpi_card("Primary KPI", "Error"),
            create_kpi_card("Secondary KPI", "Error"),
            error_fig,
            error_fig,
            create_empty_table(message=f"Error loading data: {str(e)}"),
        )


# ---------------------------------------------------------------------------
# Clear-filter callbacks (registered via shared helper)
# ---------------------------------------------------------------------------
register_clear_callbacks(CLEAR_PAIRS)
'''

TPL_CHART_BUILDERS = '''\
"""Chart builders for __TITLE__.

Contains aggregation logic for charts. Uses shared build_chart/build_table
infrastructure with specs from _constants.py.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.layout_helpers import apply_compact_chart_layout
from ._constants import (
    COLUMN_MAP,
    MAIN_CHART_SPEC,
    DETAIL_TABLE_SPEC,
)


def build_main_chart(df: pd.DataFrame):
    """Build the main chart.

    Args:
        df: Filtered DataFrame.

    Returns:
        Plotly figure for the main chart.
    """
    category_col = COLUMN_MAP["category"]
    value_col = COLUMN_MAP["value"]

    agg_df = df.groupby(category_col)[value_col].sum().reset_index()
    agg_df = agg_df.sort_values(value_col, ascending=False)

    fig = build_chart(agg_df, MAIN_CHART_SPEC)
    return apply_compact_chart_layout(
        fig,
        margin={"l": 48, "r": 16, "t": 8, "b": 40},
    )


def build_detail_table(df: pd.DataFrame):
    """Build detailed data table.

    Args:
        df: Filtered DataFrame.

    Returns:
        Tuple of (title, table_component).
    """
    date_col = COLUMN_MAP["date"]

    display_df = df.copy()
    if date_col in display_df.columns:
        display_df[date_col] = pd.to_datetime(display_df[date_col]).dt.strftime("%Y-%m-%d")

    return build_table(display_df, DETAIL_TABLE_SPEC)
'''

TPL_SPEC_MD = '''\
# __TITLE__

## 概要
__TITLE__のダッシュボードです。データの可視化と分析を行います。

## データソース
- __DATASET_ID__ データセット

## フィルタの使い方

### 日付範囲
対象期間を指定できます。日付範囲を絞り込むことで、特定期間のデータを分析できます。

### Category
カテゴリでフィルタリングできます。複数のカテゴリを選択して比較分析が可能です。

## チャート・テーブルの見方

### メインチャート（棒グラフ）
カテゴリ別の集計値を表示します。

### 詳細データテーブル
日付、カテゴリ、値などの詳細データを一覧表示します。個別レコードレベルでデータを確認できます。
'''

TPL_DATA_SOURCES_YML = '''\
charts:
  __ID_PREFIX__kpi-primary: __DATASET_ID__
  __ID_PREFIX__kpi-secondary: __DATASET_ID__
  __ID_PREFIX__chart-main: __DATASET_ID__
  __ID_PREFIX__chart-sub: __DATASET_ID__
  __ID_PREFIX__data-table: __DATASET_ID__
'''

# ---------------------------------------------------------------------------
# File generation
# ---------------------------------------------------------------------------

# Map of filename -> template content
TEMPLATES: dict[str, str] = {
    "__init__.py": TPL_INIT,
    "_constants.py": TPL_CONSTANTS,
    "_data_loader.py": TPL_DATA_LOADER,
    "_filters.py": TPL_FILTERS,
    "_layout.py": TPL_LAYOUT,
    "_callbacks.py": TPL_CALLBACKS,
    "_chart_builders.py": TPL_CHART_BUILDERS,
    "SPEC.md": TPL_SPEC_MD,
    "data_sources.yml": TPL_DATA_SOURCES_YML,
}


def _substitute(content: str, replacements: dict[str, str]) -> str:
    """Replace all placeholder tokens in a template string."""
    result = content
    for token, value in replacements.items():
        result = result.replace(token, value)
    return result


def scaffold_page(
    pages_dir: Path,
    name: str,
    title: str,
    path: str,
    dataset_id: str,
    prefix: str,
) -> Path:
    """Generate a new dashboard page package.

    Args:
        pages_dir: The parent directory where the page package will be created
                   (typically ``src/pages``).
        name: Page / directory name (e.g. ``sales_report``).
        title: Human-readable page title.
        path: URL path (e.g. ``/sales-report``).
        dataset_id: S3/Parquet dataset identifier.
        prefix: Component ID prefix (e.g. ``sr-``).

    Returns:
        Path to the created package directory.

    Raises:
        SystemExit: If the target directory already exists.
    """
    target_dir = pages_dir / name

    if target_dir.exists():
        print(f"Error: Directory already exists: {target_dir}", file=sys.stderr)
        raise SystemExit(1)

    # Derive dashboard_id from name (same convention as cursor_usage)
    dashboard_id = name

    replacements = {
        _PH_PAGE_NAME: name,
        _PH_TITLE: title,
        _PH_PATH: path,
        _PH_DATASET_ID: dataset_id,
        _PH_ID_PREFIX: prefix,
        _PH_DASHBOARD_ID: dashboard_id,
    }

    # Create directory
    target_dir.mkdir(parents=True, exist_ok=False)

    # Write each file
    for filename, template in TEMPLATES.items():
        file_path = target_dir / filename
        content = _substitute(template, replacements)
        file_path.write_text(content, encoding="utf-8")

    return target_dir


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scaffold a new Dash BI dashboard page.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Page name (used as directory name under src/pages/)",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Display title for the dashboard page",
    )
    parser.add_argument(
        "--path",
        required=True,
        help="URL path (e.g. /sales-report)",
    )
    parser.add_argument(
        "--dataset-id",
        required=True,
        help="S3/Parquet dataset identifier",
    )
    parser.add_argument(
        "--prefix",
        required=True,
        help="Component ID prefix (e.g. sr-)",
    )

    args = parser.parse_args()

    # Determine the src/pages directory relative to this script
    project_root = Path(__file__).resolve().parent.parent
    pages_dir = project_root / "src" / "pages"

    if not pages_dir.is_dir():
        print(f"Error: Pages directory not found: {pages_dir}", file=sys.stderr)
        raise SystemExit(1)

    target_dir = scaffold_page(
        pages_dir=pages_dir,
        name=args.name,
        title=args.title,
        path=args.path,
        dataset_id=args.dataset_id,
        prefix=args.prefix,
    )

    # Print summary
    print(f"Created page package: {target_dir}")
    print()
    print("Generated files:")
    for filename in sorted(TEMPLATES.keys()):
        print(f"  {target_dir / filename}")
    print()
    print("Next steps:")
    print(f"  1. Edit _constants.py to define your COLUMN_MAP and ChartSpecs")
    print(f"  2. Edit _data_loader.py to match your dataset columns")
    print(f"  3. Edit _filters.py to add/remove filter controls")
    print(f"  4. Edit _chart_builders.py to implement chart aggregation logic")
    print(f"  5. Edit _layout.py to arrange components")
    print(f"  6. Edit _callbacks.py to wire up inputs/outputs")
    print(f"  7. Update SPEC.md with dashboard documentation")
    print()
    print("The page will be auto-discovered by Dash's pages mechanism.")
    print(f"Access it at: {args.path}")


if __name__ == "__main__":
    main()
