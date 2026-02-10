# コード例集

このドキュメントでは、実際のプロジェクトで使用されているダッシュボード作成のコード例を提供します。

注意: データ取得・ETL処理の例は `01-etl` スキルを参照してください。

---

## ダッシュボードページ例（パッケージ形式）

このプロジェクトでは、パッケージ形式のダッシュボードが標準です。以下の例は `src/pages/cursor_usage/` を簡略化したものです。

### ディレクトリ構造

```
src/pages/cursor_usage/
├── __init__.py          # Dash登録 + layout参照 + コールバックインポート
├── _constants.py        # 定数・Spec定義
├── _data_loader.py      # データ読込・フィルタリング
├── _layout.py           # レイアウト構築
├── _callbacks.py        # コールバック（薄いオーケストレータ）
└── SPEC.md              # ユーザー向け設計書
```

---

### 1. `_constants.py` - 定数・Spec定義

```python
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
CHART_ID_COST_TREND: str = f"{ID_PREFIX}chart-cost-trend"
CHART_ID_DATA_TABLE: str = f"{ID_PREFIX}data-table"

# Mapping from logical filter/column key to the actual DataFrame column name
COLUMN_MAP: dict[str, str] = {
    "date": "Date",
    "model": "Model",
    "cost": "Cost",
    "total_tokens": "Total Tokens",
    "user": "User",
    "kind": "Kind",
}

# ---------------------------------------------------------------------------
# Chart / Table Specs (declarative definitions)
# ---------------------------------------------------------------------------

COST_TREND_SPEC: ChartSpec = ChartSpec(
    title="Daily Cost Trend",
    chart_type="line",
    x_column=COLUMN_MAP["date"],
    y_columns=[COLUMN_MAP["cost"]],
    show_legend=False,
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
        COLUMN_MAP["cost"],
    ],
)
```

---

### 2. `backend/config/domo_datasets.yaml` - データソース設定

```yaml
# DOMO DataSet Configuration
datasets:
  - name: "Cursor Usage Data"
    domo_dataset_id: "abc123-uuid-from-domo"
    minio_dataset_id: "cursor-usage"
    partition_column: "Date"
    enabled: true
    description: "Cursor API usage tracking data"
```

---

### 3. `_data_loader.py` - データ読込・フィルタリング

```python
"""Data loading and filtering logic for Cursor Usage Dashboard."""
import pandas as pd

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.filter_engine import FilterSet, CategoryFilter, DateRangeFilter, apply_filters, extract_unique_values
from src.utils.filter_helpers import build_filter_set_from_map
from ._constants import COLUMN_MAP, DASHBOARD_ID


def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:
    """Load filter option values from cached dataset.

    Returns a dict with keys: models, users, min_date, max_date

    On any exception returns safe defaults (empty lists / None).
    """
    try:
        df = get_cached_dataset(reader, dataset_id)

        date_col = COLUMN_MAP["date"]
        model_col = COLUMN_MAP["model"]
        user_col = COLUMN_MAP["user"]

        # Strip timezone for filter compatibility
        df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.tz_convert(None)
        df["DateOnly"] = df[date_col].dt.date

        # Extract unique values (exclude NaN)
        models = extract_unique_values(df, model_col)
        users = extract_unique_values(df, user_col)

        # Extract date range
        if len(df) > 0:
            min_date = df["DateOnly"].min().isoformat()
            max_date = df["DateOnly"].max().isoformat()
        else:
            min_date = None
            max_date = None

        return {
            "models": models,
            "users": users,
            "min_date": min_date,
            "max_date": max_date,
        }

    except Exception:
        return {
            "models": [],
            "users": [],
            "min_date": None,
            "max_date": None,
        }


def load_and_filter_data(
    reader: ParquetReader,
    dataset_id: str,
    start_date,
    end_date,
    model_values,
    user_values,
) -> pd.DataFrame:
    """Load dataset and apply all filter criteria.

    Args:
        reader: ParquetReader instance.
        dataset_id: S3 dataset identifier.
        start_date: ISO date string (YYYY-MM-DD) or None.
        end_date: ISO date string (YYYY-MM-DD) or None.
        model_values: List of model name strings or None/[].
        user_values: List of user name strings or None/[].

    Returns:
        Filtered DataFrame.
    """
    df = get_cached_dataset(reader, dataset_id)

    date_col = COLUMN_MAP["date"]

    # Strip timezone for filter compatibility (Parquet returns UTC-aware)
    df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.tz_convert(None)
    df["DateOnly"] = df[date_col].dt.date

    # Build FilterSet using helper function
    filter_pairs = [
        ("model", model_values),
        ("user", user_values),
    ]
    filters = build_filter_set_from_map(COLUMN_MAP, filter_pairs)

    # Add date range filter if provided
    if start_date and end_date:
        filters.date_filters.append(
            DateRangeFilter(
                column=date_col,
                start_date=start_date,
                end_date=end_date,
            )
        )

    return apply_filters(df, filters)
```

---

### 4. `_layout.py` - レイアウト構築

```python
"""Cursor Usage Dashboard layout module."""
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.data.parquet_reader import ParquetReader
from src.components.filters import create_date_range_filter, create_category_filter
from ._constants import (
    CHART_ID_KPI_TOTAL_COST,
    CHART_ID_COST_TREND,
    CHART_ID_DATA_TABLE,
    ID_PREFIX,
)
from ._data_loader import load_filter_options


def build_layout():
    """Build Cursor Usage Dashboard layout.

    Returns:
        Dash layout component tree with filters, KPI cards, charts, and data table.
    """
    # Load data to get available options for filters
    reader = ParquetReader()
    dataset_id = "cursor-usage"
    options = load_filter_options(reader, dataset_id)

    return html.Div([
        html.H1("Cursor Usage Dashboard", className="mb-4"),

        # Filters
        dbc.Row([
            dbc.Col([
                create_date_range_filter(
                    filter_id=f"{ID_PREFIX}filter-date",
                    column_name="Date Range",
                    min_date=options["min_date"],
                    max_date=options["max_date"],
                ),
            ], md=4),
            dbc.Col([
                create_category_filter(
                    filter_id=f"{ID_PREFIX}filter-model",
                    column_name="Model",
                    options=options["models"],
                    multi=True,
                ),
            ], md=4),
            dbc.Col([
                create_category_filter(
                    filter_id=f"{ID_PREFIX}filter-user",
                    column_name="User",
                    options=options["users"],
                    multi=True,
                ),
            ], md=4),
        ], className="mb-4"),

        # KPI Cards
        dbc.Row([
            dbc.Col([
                html.Div(id=CHART_ID_KPI_TOTAL_COST),
            ], md=4),
        ], className="mb-4"),

        # Charts
        dbc.Row([
            dbc.Col([
                dcc.Graph(id=CHART_ID_COST_TREND),
            ], md=12),
        ], className="mb-4"),

        # Data Table
        dbc.Row([
            dbc.Col([
                html.H3("Detailed Data", className="mb-3"),
                html.Div(id=CHART_ID_DATA_TABLE),
            ], md=12),
        ]),
    ], className="page-container")
```

---

### 5. `_callbacks.py` - コールバック（薄いオーケストレータ）

```python
"""Cursor Usage Dashboard callbacks module.

Thin orchestration layer: data loading -> aggregation -> shared builders.
All chart/table rendering uses the shared build_chart / build_table
infrastructure with declarative Specs defined in _constants.py.
"""
from dash import callback, Input, Output

from src.data.parquet_reader import ParquetReader
from src.components.cards import create_kpi_card
from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.empty_states import create_empty_figure, create_error_figure, create_empty_table
from src.utils.callback_helpers import register_clear_callbacks
from ._constants import (
    CHART_ID_KPI_TOTAL_COST,
    CHART_ID_COST_TREND,
    CHART_ID_DATA_TABLE,
    COLUMN_MAP,
    ID_PREFIX,
    COST_TREND_SPEC,
    DETAIL_TABLE_SPEC,
)
from ._data_loader import load_and_filter_data


@callback(
    [
        Output(CHART_ID_KPI_TOTAL_COST, "children"),
        Output(CHART_ID_COST_TREND, "figure"),
        Output(CHART_ID_DATA_TABLE, "children"),
    ],
    [
        Input(f"{ID_PREFIX}filter-date", "start_date"),
        Input(f"{ID_PREFIX}filter-date", "end_date"),
        Input(f"{ID_PREFIX}filter-model", "value"),
        Input(f"{ID_PREFIX}filter-user", "value"),
    ],
)
def update_dashboard(start_date, end_date, model_values, user_values):
    """Update dashboard components based on filters.

    Args:
        start_date: Start date from date range filter (ISO string or None)
        end_date: End date from date range filter (ISO string or None)
        model_values: Selected models from dropdown (list or None)
        user_values: Selected users from dropdown (list or None)

    Returns:
        Tuple of (kpi_cost, cost_trend_fig, table_component)
    """
    reader = ParquetReader()
    dataset_id = "cursor-usage"

    try:
        # Load and filter data
        filtered_df = load_and_filter_data(
            reader, dataset_id, start_date, end_date, model_values, user_values
        )

        if len(filtered_df) == 0:
            # Empty state using shared functions
            empty_fig = create_empty_figure(
                message="No data available for selected filters"
            )

            return (
                create_kpi_card("Total Cost", "$0.00"),
                empty_fig,
                create_empty_table(),
            )

        cost_col = COLUMN_MAP["cost"]
        date_col = COLUMN_MAP["date"]

        # Calculate KPIs
        total_cost = filtered_df[cost_col].sum()
        kpi_cost = create_kpi_card("Total Cost", f"${total_cost:.2f}")

        # Chart: Daily Cost Trend
        daily_cost = filtered_df.groupby(filtered_df[date_col].dt.date)[cost_col].sum().reset_index()
        daily_cost.columns = [date_col, cost_col]
        daily_cost = daily_cost.sort_values(date_col)

        cost_trend_fig = build_chart(daily_cost, COST_TREND_SPEC)

        # Data Table
        display_df = filtered_df.copy()
        display_df[date_col] = display_df[date_col].dt.strftime("%Y-%m-%d %H:%M")
        display_df = display_df.head(100)

        _, table_component = build_table(display_df, DETAIL_TABLE_SPEC)

        return (
            kpi_cost,
            cost_trend_fig,
            table_component,
        )

    except Exception as e:
        # Error state using shared functions
        error_fig = create_error_figure(error=str(e))

        return (
            create_kpi_card("Total Cost", "Error"),
            error_fig,
            create_empty_table(message=f"Error loading data: {str(e)}"),
        )


# Register clear button callbacks (if using slicer filters)
# Example: CLEAR_PAIRS = [(FILTER_ID_MODEL, CTRL_ID_CLEAR_MODEL), ...]
# register_clear_callbacks(CLEAR_PAIRS)
```

---

### 6. `__init__.py` - Dash登録

```python
"""Cursor Usage Dashboard page."""
import dash
from ._layout import build_layout


def layout():
    """Return Cursor Usage Dashboard layout."""
    return build_layout()


dash.register_page(__name__, path="/cursor-usage", name="Cursor Usage", order=1, layout=layout)

# Import callbacks to register them with Dash
from . import _callbacks  # noqa: F401, E402
```

---

### 7. `_filters.py` - フィルタUI構築（5個以上のフィルタがある場合）

フィルタが5個以上ある場合は、`_filters.py` に `build_filter_layout()` 関数を定義します。
以下は `hamm_overview` からの参考例:

```python
"""Filter UI layout builder for Hamm Overview dashboard."""
from dash import html
import dash_bootstrap_components as dbc

from src.components.filters import create_category_filter, create_slicer_filter
from ._constants import (
    FILTER_ID_REGION,
    FILTER_ID_YEAR,
    CTRL_ID_CLEAR_REGION,
    CTRL_ID_CLEAR_YEAR,
)


def build_filter_layout(opts: dict, title_element=None) -> list:
    """Build the filter section rows for Hamm Overview layout.

    Args:
        opts: Dict returned by load_filter_options(), containing
            regions, years, etc.
        title_element: Optional element to prepend to the first row
            (e.g. the dashboard title div).

    Returns:
        List of html.Div components representing filter rows.
    """
    filters_row1 = [
        create_slicer_filter(
            filter_id=FILTER_ID_REGION,
            column_name="Region",
            options=opts["regions"],
            clear_button_id=CTRL_ID_CLEAR_REGION,
        ),
        create_slicer_filter(
            filter_id=FILTER_ID_YEAR,
            column_name="Year",
            options=opts["years"],
            clear_button_id=CTRL_ID_CLEAR_YEAR,
        ),
    ]

    if title_element is not None:
        filters_row1 = [title_element] + filters_row1

    title_row = html.Div(
        filters_row1,
        className="mb-3 filter-row-title-2filters",
    )

    return [title_row]
```

クリアボタンコールバックは `_callbacks.py` の末尾で登録:

```python
from src.utils.callback_helpers import register_clear_callbacks
from ._constants import CLEAR_PAIRS

# Clear callback pairs: (filter_id, clear_button_id)
CLEAR_PAIRS = [
    (FILTER_ID_REGION, CTRL_ID_CLEAR_REGION),
    (FILTER_ID_YEAR, CTRL_ID_CLEAR_YEAR),
]

# Register all clear callbacks
register_clear_callbacks(CLEAR_PAIRS)
```

---

## よく使うコールバックパターン

### パターン1: 共通ビルダーを使った単一チャート更新

```python
from src.charts.chart_builder import build_chart
from src.charts.specs import ChartSpec

CHART_SPEC = ChartSpec(
    title="Daily Trend",
    chart_type="line",
    x_column="Date",
    y_columns=["Value"],
)

@callback(
    Output("chart", "figure"),
    [Input("filter-1", "value")],
)
def update_chart(filter_value):
    """Update chart based on filters."""
    df = load_and_filter_data(reader, dataset_id, filter_value)

    # Use shared builder with declarative spec
    return build_chart(df, CHART_SPEC)
```

### パターン2: 共通ビルダーを使った複数出力

```python
from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.components.cards import create_kpi_card

@callback(
    [
        Output("kpi-1", "children"),
        Output("chart", "figure"),
        Output("table", "children"),
    ],
    [Input("filter", "value")],
)
def update_dashboard(filter_value):
    """Update multiple components."""
    df = load_and_filter_data(reader, dataset_id, filter_value)

    # Calculate KPI
    kpi_value = df["Value"].sum()
    kpi1 = create_kpi_card("Total", f"{kpi_value:,.0f}")

    # Build chart using shared builder
    chart_fig = build_chart(df, CHART_SPEC)

    # Build table using shared builder
    _, table_component = build_table(df, TABLE_SPEC)

    return kpi1, chart_fig, table_component
```

### パターン3: エラーハンドリング（共通empty_states使用）

```python
from src.charts.empty_states import create_empty_figure, create_error_figure, create_empty_table

@callback(
    Output("output", "children"),
    [Input("input", "value")],
)
def update_output(input_value):
    """Update output with error handling."""
    try:
        df = load_and_filter_data(reader, dataset_id, input_value)

        if len(df) == 0:
            # Empty state
            return create_empty_figure(message="No data available")

        # Normal processing
        return build_chart(df, CHART_SPEC)

    except Exception as e:
        # Error state
        return create_error_figure(error=str(e))
```

### パターン4: build_filter_set_from_map を使ったフィルタ構築

```python
from src.utils.filter_helpers import build_filter_set_from_map
from src.data.filter_engine import apply_filters

COLUMN_MAP = {
    "region": "notification_company_name",
    "year": "_year",
    "month": "_month",
}

def load_and_filter_data(reader, dataset_id, region_values, year_values, month_values):
    """Load and filter data using helper function."""
    df = get_cached_dataset(reader, dataset_id)

    # Build FilterSet using helper
    filter_pairs = [
        ("region", region_values),
        ("year", year_values),
        ("month", month_values),
    ]
    filters = build_filter_set_from_map(COLUMN_MAP, filter_pairs)

    return apply_filters(df, filters)
```

---

## CSS修正例

### z-index問題の完全な修正

`assets/03-components.css` に追加する完全なコード:

```css
/* Dash 4.x (radix) dropdown/datepicker content */
.dash-dropdown-content,
.dash-options-list,
.dash-dropdown-options,
.dash-datepicker-content,
.dash-datepicker-popover,
.dash-datepicker-overlay,
[data-radix-popper-content-wrapper] {
  z-index: 9999 !important;
}

[data-radix-popper-content-wrapper] > * {
  z-index: 9999 !important;
}

/* ドロップダウンの背景色を明示設定（透明防止） */
.dash-dropdown-content {
  background-color: white;
}

/* カードのhover効果を調整（transformを削除してスタッキングコンテキスト問題を防止） */
.card {
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}

.card:hover {
  box-shadow: var(--shadow-md), var(--shadow-glow);
  border-color: var(--border-accent);
}
```

---

## Docker設定例

### docker-compose.yml の完全な設定

```yaml
services:
  # Dashアプリ
  dash:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8050:8050"
    volumes:
      - ./src:/app/src
      - ./backend:/app/backend
      - ./assets:/app/assets  # 重要: assetsをマウント
      - ./app.py:/app/app.py
    environment:
      - ENV=local
      - S3_ENDPOINT=http://minio:9000
      - S3_REGION=ap-northeast-1
      - S3_BUCKET=bi-datasets
      - S3_ACCESS_KEY=minioadmin
      - S3_SECRET_KEY=minioadmin
      - BASIC_AUTH_USERNAME=${BASIC_AUTH_USERNAME:-admin}
      - BASIC_AUTH_PASSWORD=${BASIC_AUTH_PASSWORD:-changeme}
    depends_on:
      minio:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8050')"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 40s

  # MinIO (S3互換)
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio-data:/data
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9000/minio/health/live || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  # MinIO初期設定
  minio-init:
    image: minio/mc:latest
    depends_on:
      minio:
        condition: service_healthy
    entrypoint: |
      /bin/sh -c "
      sleep 5
      mc alias set local http://minio:9000 minioadmin minioadmin
      mc mb local/bi-datasets --ignore-existing
      exit 0
      "

volumes:
  minio-data:
```

---

## データ処理パターン

### パターン1: 日付でグループ化

```python
# 日付でグループ化して集計
daily_data = df.groupby(df["Date"].dt.date)["Value"].sum().reset_index()
daily_data.columns = ["Date", "TotalValue"]
daily_data = daily_data.sort_values("Date")
```

### パターン2: 複数カラムで集計

```python
# 複数カラムでグループ化して集計
summary = df.groupby(["Category", "SubCategory"]).agg({
    "Value": "sum",
    "Count": "count",
}).reset_index()
```

### パターン3: 計算カラムの追加

```python
# 効率指標を計算
df["Efficiency"] = df["Output"] / df["Input"]
df["Efficiency"] = df["Efficiency"].fillna(0)  # ゼロ除算対策
```

### パターン4: データのフォーマット

```python
# 日付のフォーマット
display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d %H:%M")

# 数値のフォーマット
display_df["Cost"] = display_df["Cost"].apply(lambda x: f"${x:,.2f}")

# パーセンテージのフォーマット
display_df["Rate"] = display_df["Rate"].apply(lambda x: f"{x:.1%}")
```

---

## エラーハンドリングパターン

### パターン1: 空データの処理（共通関数使用）

```python
from src.charts.empty_states import create_empty_figure

if len(filtered_df) == 0:
    return create_empty_figure(message="No data available for selected filters")
```

### パターン2: 例外処理（共通関数使用）

```python
from src.charts.empty_states import create_error_figure, create_empty_table

try:
    df = get_cached_dataset(reader, dataset_id)
    result = process_data(df)
    return result
except FileNotFoundError:
    return create_empty_table(message="Data file not found. Please run ETL script first.")
except Exception as e:
    return create_error_figure(error=str(e))
```

### パターン3: データ検証

```python
# 必要なカラムが存在するか確認
required_columns = ["Date", "Value", "Category"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    return create_error_figure(error=f"Missing columns: {', '.join(missing_columns)}")
```

---

## パフォーマンス最適化パターン

### パターン1: データの事前フィルタリング

```python
# 大量データの場合、必要な期間だけ読み込む
df = get_cached_dataset(reader, dataset_id)

# 日付範囲で事前フィルタリング
if start_date and end_date:
    df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
```

### パターン2: 集計結果のキャッシュ

```python
# 集計結果をキャッシュ（Flask-Caching使用）
from flask_caching import Cache

cache = Cache()

@cache.memoize(timeout=300)  # 5分間キャッシュ
def get_aggregated_data(dataset_id, filters):
    df = get_cached_dataset(reader, dataset_id)
    # Apply filters and aggregate
    return aggregated_result
```

### パターン3: データのサンプリング

```python
# 大量データの場合、表示用にサンプリング
if len(df) > 10000:
    df = df.sample(n=10000, random_state=42)
```
