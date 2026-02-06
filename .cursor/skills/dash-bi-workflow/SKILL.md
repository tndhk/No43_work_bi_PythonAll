---
name: dash-bi-workflow
description: Plotly DashベースのBIダッシュボード開発ワークフロー。データセット配置、ETL処理（CSV→Parquet→MinIO）、ダッシュボードページ作成、デバッグまでの一連の流れをガイド。Dashダッシュボード、データ可視化、ETL、Parquetに関連する作業で使用。
---

# Plotly Dash BIダッシュボード開発ワークフロー

## クイックスタートチェックリスト

新しいダッシュボードを作成する際は、このチェックリストに従って進めます：

- [ ] Phase 1: データセットを `backend/data_sources/` に配置
- [ ] Phase 1: `.gitignore` と `.cursorignore` に `backend/data_sources/` を追加
- [ ] Phase 2: `backend/scripts/` にETLスクリプトを作成
- [ ] Phase 2: ETLスクリプトを実行してMinIOにParquetファイルをアップロード
- [ ] Phase 3: `src/pages/` にダッシュボードページを作成
- [ ] Phase 4: フィルタとコールバックを実装
- [ ] Phase 5: デバッグと検証（よくあるバグパターンを確認）

---

## Phase 1: データセット準備

### 配置場所

CSVデータファイルは `backend/data_sources/` ディレクトリに配置します。

```
backend/data_sources/
├── team-usage-events-15944373-2026-01-28.csv
└── ...
```

### Git/Cursor除外設定

データファイルはリポジトリに含めないため、必ず除外設定を追加します：

**`.gitignore`** に追加：
```
backend/data_sources/
```

**`.cursorignore`** に追加：
```
backend/data_sources/
```

### ファイル命名規則

推奨フォーマット: `{dataset-name}-{identifier}-{date}.csv`

例: `team-usage-events-15944373-2026-01-28.csv`

---

## Phase 2: ETL実装

### ETLスクリプト作成

`backend/scripts/` ディレクトリにETLスクリプトを作成します。

**テンプレート:**

```python
"""ETL script to load CSV data to MinIO S3 as Parquet."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.etl.etl_csv import CsvETL


def main():
    """Load CSV to S3."""
    csv_path = project_root / "backend" / "data_sources" / "your-file.csv"
    
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
    
    print(f"Loading CSV from: {csv_path}")
    
    # Create ETL instance
    etl = CsvETL(
        csv_path=str(csv_path),
        partition_column="Date",  # パーティション分割するカラム名
    )
    
    # Run ETL
    dataset_id = "your-dataset-id"
    print(f"Running ETL for dataset: {dataset_id}")
    etl.run(dataset_id)
    
    print(f"Successfully loaded dataset '{dataset_id}' to S3")


if __name__ == "__main__":
    main()
```

### partition_column の選び方

- 日付カラムがある場合: `"Date"` を指定（推奨）
- パーティション分割しない場合: `None` を指定
- パーティション分割により、クエリパフォーマンスが向上します

### ETL実行と確認

```bash
python backend/scripts/load_your_dataset.py
```

MinIOコンソール（http://localhost:9001）でアップロードを確認します。

---

## Phase 3: ダッシュボードページ作成

### ページファイル作成

`src/pages/` ディレクトリに新しいページファイルを作成します。

**基本構造:**

```python
"""Your Dataset Dashboard page."""
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

dash.register_page(__name__, path="/your-path", name="Your Dashboard", order=1)


def layout():
    """Dashboard layout."""
    dataset_id = "your-dataset-id"
    
    # Load data to get available options for filters
    reader = ParquetReader()
    try:
        df = get_cached_dataset(reader, dataset_id)
        
        # CRITICAL: Strip timezone from datetime columns
        df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_convert(None)
        df["DateOnly"] = df["Date"].dt.date
        
        # Get unique values for filters
        categories = sorted(df["Category"].unique().tolist())
        min_date = df["DateOnly"].min().isoformat()
        max_date = df["DateOnly"].max().isoformat()
    except Exception:
        categories = []
        min_date = None
        max_date = None
    
    return html.Div([
        html.H1("Your Dashboard Title", className="mb-4"),
        
        # Filters Row
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
                    filter_id="category-filter",
                    column_name="Category",
                    options=categories,
                    multi=True,
                ),
            ], md=6),
        ], className="mb-4"),
        
        # KPI Cards Row
        dbc.Row([
            dbc.Col([html.Div(id="kpi-1")], md=4),
            dbc.Col([html.Div(id="kpi-2")], md=4),
            dbc.Col([html.Div(id="kpi-3")], md=4),
        ], className="mb-4"),
        
        # Charts Row
        dbc.Row([
            dbc.Col([dcc.Graph(id="chart-1")], md=12),
        ], className="mb-4"),
        
        # Data Table
        dbc.Row([
            dbc.Col([
                html.H3("Detailed Data", className="mb-3"),
                html.Div(id="data-table"),
            ], md=12),
        ]),
    ], className="page-container")
```

### コンポーネントの活用

既存コンポーネントを活用します：

- **KPIカード**: `create_kpi_card(title, value, subtitle=None)` - [`src/components/cards.py`](src/components/cards.py)
- **日付範囲フィルタ**: `create_date_range_filter(...)` - [`src/components/filters.py`](src/components/filters.py)
- **カテゴリフィルタ**: `create_category_filter(...)` - [`src/components/filters.py`](src/components/filters.py)
- **チャート**: `render_line_chart()`, `render_bar_chart()`, `render_pie_chart()` - [`src/charts/templates.py`](src/charts/templates.py)

---

## Phase 4: コールバック実装

### 基本パターン

フィルタ変更時にダッシュボード全体を更新するコールバック：

```python
@callback(
    [
        Output("kpi-1", "children"),
        Output("kpi-2", "children"),
        Output("chart-1", "figure"),
        Output("data-table", "children"),
    ],
    [
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        Input("category-filter", "value"),
    ],
)
def update_dashboard(start_date, end_date, category_values):
    """Update dashboard components based on filters."""
    dataset_id = "your-dataset-id"
    reader = ParquetReader()
    
    try:
        # Load data with cache
        df = get_cached_dataset(reader, dataset_id)
        
        # CRITICAL: Strip timezone from datetime columns
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
        
        if category_values:
            filters.category_filters.append(
                CategoryFilter(
                    column="Category",
                    values=category_values,
                )
            )
        
        # Apply filters
        filtered_df = apply_filters(df, filters)
        
        if len(filtered_df) == 0:
            # Empty state handling
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No data available for selected filters",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
            )
            empty_fig.update_layout(height=400)
            
            return (
                create_kpi_card("Metric 1", "0"),
                create_kpi_card("Metric 2", "0"),
                empty_fig,
                html.P("No data available", className="text-muted"),
            )
        
        # Calculate KPIs
        kpi1_value = filtered_df["Value"].sum()
        kpi2_value = len(filtered_df)
        
        # Create KPI cards
        kpi1 = create_kpi_card("Metric 1", f"{kpi1_value:,.0f}")
        kpi2 = create_kpi_card("Metric 2", f"{kpi2_value:,}")
        
        # Create charts
        chart_fig = render_line_chart(
            dataset=filtered_df.groupby("Date")["Value"].sum().reset_index(),
            filters=None,
            params={"x_column": "Date", "y_column": "Value"},
        )
        
        # Create data table (Dash 4.x compatible)
        display_df = filtered_df[["Date", "Category", "Value"]].copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d %H:%M")
        
        table_component = dash_table.DataTable(
            data=display_df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in display_df.columns],
            page_size=20,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px"},
            style_header={"fontWeight": "bold"},
        )
        
        return (
            kpi1,
            kpi2,
            chart_fig,
            table_component,
        )
    
    except Exception as e:
        # Error state handling
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
            create_kpi_card("Metric 1", "Error"),
            create_kpi_card("Metric 2", "Error"),
            empty_fig,
            error_msg,
        )
```

### キャッシュの活用

`get_cached_dataset()` を使用することで、データ読み込みが高速化されます。初回読み込み時のみS3から取得し、以降はキャッシュから返されます。

---

## Phase 5: デバッグ・検証

### よくあるバグパターン

詳細は [TROUBLESHOOTING.md](TROUBLESHOOTING.md) を参照してください。

#### Bug Pattern 1: Timezone-aware datetime エラー

**症状:**
```
TypeError: Invalid comparison between dtype=datetime64[ns, UTC] and Timestamp
```

**原因:**
Parquetから読み込んだdatetimeカラムがUTC timezone付きで、フィルタリング時のTimestampとの比較でエラーが発生します。

**解決法:**
```python
# データ読み込み後、必ずtimezoneを除去
df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_convert(None)
```

#### Bug Pattern 2: Dash 4.x API変更

**症状:**
```
The `html.Div` component (version 4.0.0) received an unexpected keyword argument: `dangerously_allow_html`
```

**原因:**
Dash 4.0で `dangerously_allow_html` 属性が削除されました。

**解決法:**
テーブル表示には `dash_table.DataTable` を直接使用します：

```python
# ❌ 使えない
html.Div(html_table, dangerously_allow_html=True)

# ✅ 正しい
dash_table.DataTable(
    data=df.to_dict("records"),
    columns=[{"name": c, "id": c} for c in df.columns],
    page_size=20,
)
```

#### Bug Pattern 3: CSS z-index問題

**症状:**
ドロップダウンやDatePickerのメニューがKPIカードの後ろに隠れる、マウス位置で不安定に表示される。

**原因:**
Dash 4.x (Radix UI) のポップアップが低いz-indexで表示される。

**解決法:**
`assets/03-components.css` に以下を追加：

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
```

また、KPIカードのhover効果で `transform` を使っている場合は削除：

```css
.kpi-card:hover {
  /* transform: translateY(-2px); を削除 */
  box-shadow: var(--shadow-md), var(--shadow-glow);
  border-color: var(--border-accent);
}
```

#### Bug Pattern 4: Docker環境でアセットが反映されない

**原因:**
`assets/` や `backend/` がコンテナにマウントされていない。

**解決法:**
`docker-compose.yml` にボリュームマウントを追加：

```yaml
services:
  dash:
    volumes:
      - ./src:/app/src
      - ./backend:/app/backend
      - ./assets:/app/assets  # 追加
      - ./app.py:/app/app.py
```

CSS変更後はブラウザでハードリロード（Cmd+Shift+R / Ctrl+Shift+F5）を実行します。

### 検証チェックリスト

開発完了前に以下を確認：

- [ ] CSVファイルが `.gitignore` と `.cursorignore` に追加されている
- [ ] ETLスクリプトが正常に実行され、MinIOにParquetファイルがアップロードされている
- [ ] ダッシュボードがエラーなく表示される
- [ ] datetimeカラムのtimezoneが適切に処理されている（`.dt.tz_convert(None)` を使用）
- [ ] Dash 4.x互換のコンポーネントを使用している（`dash_table.DataTable` を使用）
- [ ] ドロップダウン/DatePickerが正しく前面に表示される
- [ ] Docker環境でassetsとbackendがマウントされている
- [ ] ハードリロード（Cmd+Shift+R / Ctrl+Shift+F5）でCSSが反映される

---

## 追加リソース

- 詳細なトラブルシューティング: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 実際のコード例: [examples.md](examples.md)
- プロジェクト固有の学習メモ: [`CLAUDE.md`](CLAUDE.md)
