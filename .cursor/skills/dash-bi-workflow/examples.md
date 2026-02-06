# コード例集

このドキュメントでは、実際のプロジェクトで使用されているダッシュボード作成のコード例を提供します。

**注意**: データ取得・ETL処理の例は `etl-workflow` スキルを参照してください。

---

## ダッシュボードページ例

### 完全なダッシュボードページ

`src/pages/cursor_usage.py` の実装例：

```python
"""Cursor Usage Dashboard page."""
import dash
from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.filter_engine import FilterSet, CategoryFilter, DateRangeFilter, apply_filters
from src.components.filters import create_date_range_filter, create_category_filter
from src.components.cards import create_kpi_card
from src.charts.templates import render_line_chart, render_bar_chart, render_pie_chart

dash.register_page(__name__, path="/cursor-usage", name="Cursor Usage", order=1)


def layout():
    """Cursor Usage Dashboard layout."""
    dataset_id = "cursor-usage"

    # Load data to get available options for filters
    reader = ParquetReader()
    try:
        df = get_cached_dataset(reader, dataset_id)

        # Extract date from ISO datetime string (strip timezone for filter compatibility)
        df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_convert(None)
        df["DateOnly"] = df["Date"].dt.date

        # Get unique models for filter
        models = sorted(df["Model"].unique().tolist())
        min_date = df["DateOnly"].min().isoformat()
        max_date = df["DateOnly"].max().isoformat()
    except Exception:
        # If data not loaded yet, use defaults
        models = []
        min_date = None
        max_date = None

    return html.Div([
        html.H1("Cursor Usage Dashboard", className="mb-4"),

        # Filters
        dbc.Row([
            dbc.Col([
                create_date_range_filter(
                    filter_id="date-filter",
                    column_name="Date Range",
                    min_date=min_date,
                    max_date=max_date,
                ),
            ], md=6),
            dbc.Col([
                create_category_filter(
                    filter_id="model-filter",
                    column_name="Model",
                    options=models,
                    multi=True,
                ),
            ], md=6),
        ], className="mb-4"),

        # KPI Cards
        dbc.Row([
            dbc.Col([
                html.Div(id="kpi-total-cost"),
            ], md=4),
            dbc.Col([
                html.Div(id="kpi-total-tokens"),
            ], md=4),
            dbc.Col([
                html.Div(id="kpi-request-count"),
            ], md=4),
        ], className="mb-4"),

        # Charts Row 1
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-cost-trend"),
            ], md=12),
        ], className="mb-4"),

        # Charts Row 2
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-token-efficiency"),
            ], md=6),
            dbc.Col([
                dcc.Graph(id="chart-model-distribution"),
            ], md=6),
        ], className="mb-4"),

        # Data Table
        dbc.Row([
            dbc.Col([
                html.H3("Detailed Data", className="mb-3"),
                html.Div(id="data-table"),
            ], md=12),
        ]),
    ], className="page-container")


@callback(
    [
        Output("kpi-total-cost", "children"),
        Output("kpi-total-tokens", "children"),
        Output("kpi-request-count", "children"),
        Output("chart-cost-trend", "figure"),
        Output("chart-token-efficiency", "figure"),
        Output("chart-model-distribution", "figure"),
        Output("data-table", "children"),
    ],
    [
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        Input("model-filter", "value"),
    ],
)
def update_dashboard(start_date, end_date, model_values):
    """Update dashboard components based on filters."""
    dataset_id = "cursor-usage"
    reader = ParquetReader()

    try:
        # Load data
        df = get_cached_dataset(reader, dataset_id)

        # Convert Date column to datetime (strip timezone for filter compatibility)
        df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_convert(None)
        df["DateOnly"] = df["Date"].dt.date

        # Build filters
        filters = FilterSet()

        if start_date and end_date:
            filters.date_filters.append(
                DateRangeFilter(
                    column="Date",
                    start_date=start_date,
                    end_date=end_date,
                )
            )

        if model_values:
            filters.category_filters.append(
                CategoryFilter(
                    column="Model",
                    values=model_values,
                )
            )

        # Apply filters
        filtered_df = apply_filters(df, filters)

        if len(filtered_df) == 0:
            # Empty state
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No data available for selected filters",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
            )
            empty_fig.update_layout(height=400)

            return (
                create_kpi_card("Total Cost", "$0.00"),
                create_kpi_card("Total Tokens", "0"),
                create_kpi_card("Request Count", "0"),
                empty_fig,
                empty_fig,
                empty_fig,
                html.P("No data available", className="text-muted"),
            )

        # Calculate KPIs
        total_cost = filtered_df["Cost"].sum()
        total_tokens = filtered_df["Total Tokens"].sum()
        request_count = len(filtered_df)

        # KPI Cards
        kpi_cost = create_kpi_card("Total Cost", f"${total_cost:.2f}")
        kpi_tokens = create_kpi_card("Total Tokens", f"{total_tokens:,}")
        kpi_requests = create_kpi_card("Request Count", f"{request_count:,}")

        # Chart 1: Daily Cost Trend
        daily_cost = filtered_df.groupby(filtered_df["Date"].dt.date)["Cost"].sum().reset_index()
        daily_cost.columns = ["Date", "Cost"]
        daily_cost = daily_cost.sort_values("Date")

        cost_trend_fig = render_line_chart(
            dataset=daily_cost,
            filters=None,
            params={
                "x_column": "Date",
                "y_column": "Cost",
            },
        )
        cost_trend_fig.update_layout(
            title="Daily Cost Trend",
            xaxis_title="Date",
            yaxis_title="Cost ($)",
        )

        # Chart 2: Token Efficiency by Model
        model_stats = filtered_df.groupby("Model").agg({
            "Total Tokens": "sum",
            "Cost": "sum",
        }).reset_index()
        model_stats["TokensPerCost"] = model_stats["Total Tokens"] / model_stats["Cost"]
        model_stats = model_stats.sort_values("TokensPerCost", ascending=False)

        efficiency_fig = render_bar_chart(
            dataset=model_stats,
            filters=None,
            params={
                "x_column": "Model",
                "y_column": "TokensPerCost",
            },
        )
        efficiency_fig.update_layout(
            title="Token Efficiency by Model (Tokens per $)",
            xaxis_title="Model",
            yaxis_title="Tokens per Cost",
        )

        # Chart 3: Model Distribution
        model_dist = filtered_df.groupby("Model")["Cost"].sum().reset_index()
        model_dist.columns = ["Model", "Cost"]

        distribution_fig = render_pie_chart(
            dataset=model_dist,
            filters=None,
            params={
                "names_column": "Model",
                "values_column": "Cost",
            },
        )
        distribution_fig.update_layout(
            title="Cost Distribution by Model",
        )

        # Data Table (Dash 4.x compatible)
        display_df = filtered_df[[
            "Date", "User", "Model", "Kind",
            "Total Tokens", "Cost"
        ]].copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d %H:%M")
        display_df = display_df.head(100)

        table_component = dash_table.DataTable(
            data=display_df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in display_df.columns],
            page_size=20,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px"},
            style_header={"fontWeight": "bold"},
        )

        return (
            kpi_cost,
            kpi_tokens,
            kpi_requests,
            cost_trend_fig,
            efficiency_fig,
            distribution_fig,
            table_component,
        )

    except Exception as e:
        # Error state
        error_msg = html.Div([
            html.P(f"Error loading data: {str(e)}", className="text-danger"),
        ])

        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
        )
        empty_fig.update_layout(height=400)

        return (
            create_kpi_card("Total Cost", "Error"),
            create_kpi_card("Total Tokens", "Error"),
            create_kpi_card("Request Count", "Error"),
            empty_fig,
            empty_fig,
            empty_fig,
            error_msg,
        )
```

---

## よく使うコールバックパターン

### パターン1: シンプルなフィルタ連動

```python
@callback(
    Output("chart", "figure"),
    [
        Input("filter-1", "value"),
        Input("filter-2", "value"),
    ],
)
def update_chart(filter1_value, filter2_value):
    """Update chart based on filters."""
    df = get_cached_dataset(reader, dataset_id)
    
    # Apply filters
    if filter1_value:
        df = df[df["Column1"] == filter1_value]
    if filter2_value:
        df = df[df["Column2"].isin(filter2_value)]
    
    # Create chart
    fig = render_line_chart(
        dataset=df,
        filters=None,
        params={"x_column": "Date", "y_column": "Value"},
    )
    
    return fig
```

### パターン2: 複数出力のコールバック

```python
@callback(
    [
        Output("kpi-1", "children"),
        Output("kpi-2", "children"),
        Output("chart", "figure"),
    ],
    [Input("filter", "value")],
)
def update_dashboard(filter_value):
    """Update multiple components."""
    df = get_cached_dataset(reader, dataset_id)
    
    if filter_value:
        df = df[df["Category"] == filter_value]
    
    # Calculate KPIs
    kpi1_value = df["Value"].sum()
    kpi2_value = len(df)
    
    # Create components
    kpi1 = create_kpi_card("Total", f"{kpi1_value:,.0f}")
    kpi2 = create_kpi_card("Count", f"{kpi2_value:,}")
    
    fig = render_bar_chart(
        dataset=df.groupby("Date")["Value"].sum().reset_index(),
        filters=None,
        params={"x_column": "Date", "y_column": "Value"},
    )
    
    return kpi1, kpi2, fig
```

### パターン3: エラーハンドリング付き

```python
@callback(
    Output("output", "children"),
    [Input("input", "value")],
)
def update_output(input_value):
    """Update output with error handling."""
    try:
        # Process data
        df = get_cached_dataset(reader, dataset_id)
        result = process_data(df, input_value)
        
        return html.Div([
            html.H3("Results"),
            html.P(str(result)),
        ])
    
    except Exception as e:
        # Error state
        return html.Div([
            html.P(f"Error: {str(e)}", className="text-danger"),
        ], className="alert alert-danger")
```

---

## CSS修正例

### z-index問題の完全な修正

`assets/03-components.css` に追加する完全なコード：

```css
/* Dash 4.x (radix) dropdown/datepicker content */
.dash-dropdown-content,
.dash-options-list,
.dash-dropdown-options,
.dash-datepicker-content,
.dash-datepicker-popover,
.dash-datepicker-overlay,
[data-radix-popper-content-wrapper] {
  position: relative !important;
  z-index: 9999 !important;
}

[data-radix-popper-content-wrapper] > * {
  z-index: 9999 !important;
}

/* KPIカードのhover効果を調整（transformを削除） */
.kpi-card:hover {
  /* transform: translateY(-2px); を削除 */
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

### パターン1: 空データの処理

```python
if len(filtered_df) == 0:
    empty_fig = go.Figure()
    empty_fig.add_annotation(
        text="No data available for selected filters",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
    )
    empty_fig.update_layout(height=400)
    return empty_fig
```

### パターン2: 例外処理

```python
try:
    df = get_cached_dataset(reader, dataset_id)
    # Process data
    result = process_data(df)
    return result
except FileNotFoundError:
    return html.Div([
        html.P("Data file not found. Please run ETL script first.", className="text-warning"),
    ])
except Exception as e:
    return html.Div([
        html.P(f"Error: {str(e)}", className="text-danger"),
    ])
```

### パターン3: データ検証

```python
# 必要なカラムが存在するか確認
required_columns = ["Date", "Value", "Category"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    return html.Div([
        html.P(f"Missing columns: {', '.join(missing_columns)}", className="text-danger"),
    ])
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
