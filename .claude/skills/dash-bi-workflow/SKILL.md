---
name: dash-bi-workflow
description: Plotly DashベースのBIダッシュボード開発ワークフロー。Parquetデータからダッシュボードページ作成、フィルタ・コールバック実装、デバッグまでの流れをガイド。Dashダッシュボード、データ可視化、Plotlyに関連する作業で使用。データ取得・ETLは別スキル（etl-workflow）を参照。
---

# Plotly Dash BIダッシュボード開発ワークフロー

## 前提条件

このスキルは、**既にParquet形式でMinIOにアップロード済みのデータ**を前提とします。

データ取得・ETL処理が必要な場合は、別スキル `etl-workflow` を参照してください。

## クイックスタートチェックリスト

新しいダッシュボードを作成する際は、このチェックリストに従って進めます:

- [ ] Phase 1: データがMinIOにParquet形式でアップロードされていることを確認
- [ ] Phase 2: `src/pages/<page_name>/` パッケージ形式でダッシュボードページを作成
- [ ] Phase 3: フィルタとコールバックを実装
- [ ] Phase 4: デバッグと検証（よくあるバグパターンを確認）

---

## Phase 1: データ確認

### MinIOでのデータ確認

ダッシュボード作成前に、データが正しくアップロードされていることを確認します:

1. MinIOコンソール（http://localhost:9001）にアクセス
2. `bi-datasets` バケットを確認
3. `datasets/{dataset_id}/` 配下にParquetファイルが存在することを確認

### データ構造の確認

必要に応じて、ParquetReaderでデータ構造を確認:

```python
from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset

reader = ParquetReader()
df = get_cached_dataset(reader, "your-dataset-id")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(df.head())
```

---

## Phase 2: ダッシュボードページ作成（パッケージ形式）

### 2-1. ディレクトリ構造作成

`src/pages/<page_name>/` ディレクトリを作成し、以下の構造でファイルを配置します:

```
src/pages/<page_name>/
├── __init__.py          # 必須: Dash登録 + build_layout参照 + コールバックインポート
├── _constants.py        # 必須: DASHBOARD_ID, DATASET_ID, ID_PREFIX, COLUMN_MAP, TABLE_SPECS, CHART_SPECS
├── data_sources.yml     # 必須: chart_id -> dataset_id マッピング
├── _data_loader.py      # 必須: load_filter_options(), load_and_filter_data()
├── _filters.py          # 条件付き必須: フィルタUI構築（フィルタ5個以上の場合）
├── _layout.py           # 必須: build_layout()
├── _callbacks.py        # 必須: コールバック関数群（薄いオーケストレータ）
├── SPEC.md              # 必須: ユーザー向け設計書（日本語）
├── _utils.py            # オプション: ヘルパー関数
└── _chart_builders.py   # オプション: カスタム集計・描画ロジック
```

### 2-2. `_constants.py` - 定数・定義ファイル

```python
"""Constants for the <Page Name> Dashboard page.

Centralizes dataset identifiers, column name mappings, ID prefixes,
and declarative ChartSpec / TableSpec definitions.
"""

from src.charts.specs import ChartSpec, TableSpec

# Dashboard identifier (used for config lookup)
DASHBOARD_ID: str = "your_dashboard"

# S3/Parquet dataset identifier (legacy fallback)
DATASET_ID: str = "your-dataset-id"

# Component ID namespace prefix (for avoiding collisions with other pages)
ID_PREFIX: str = "yd-"

# Chart IDs used in this dashboard
CHART_ID_KPI_TOTAL: str = f"{ID_PREFIX}kpi-total"
CHART_ID_MAIN_CHART: str = f"{ID_PREFIX}chart-main"
CHART_ID_DATA_TABLE: str = f"{ID_PREFIX}data-table"

# Mapping from logical filter/column key to the actual DataFrame column name.
# Keys are short identifiers used in code; values are the raw column names
# as they appear in the Parquet/DataFrame.
COLUMN_MAP: dict[str, str] = {
    "date": "Date",
    "category": "Category",
    "value": "Value",
}

# Clear callback pairs: (filter_id, clear_button_id)
CLEAR_PAIRS: list[tuple[str, str]] = [
    (f"{ID_PREFIX}filter-category", f"{ID_PREFIX}ctrl-clear-category"),
]

# ---------------------------------------------------------------------------
# Chart / Table Specs (declarative definitions)
# ---------------------------------------------------------------------------

MAIN_CHART_SPEC: ChartSpec = ChartSpec(
    title="Main Chart",
    chart_type="line",
    x_column=COLUMN_MAP["date"],
    y_columns=[COLUMN_MAP["value"]],
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
        COLUMN_MAP["category"],
        COLUMN_MAP["value"],
    ],
)
```

### 2-3. `data_sources.yml` - データソースマッピング

```yaml
charts:
  yd-kpi-total: your-dataset-id
  yd-chart-main: your-dataset-id
  yd-data-table: your-dataset-id
```

### 2-4. `_data_loader.py` - データ読込・フィルタリング

```python
"""Data loading and filtering logic for Your Dashboard.

Extracts data access concerns from the page module so that layout()
and update_dashboard() remain thin UI-only functions.
"""
import pandas as pd

from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.data_source_registry import resolve_dataset_id
from src.data.filter_engine import FilterSet, apply_filters
from src.utils.filter_helpers import build_filter_set_from_map
from ._constants import (
    COLUMN_MAP,
    DASHBOARD_ID,
    CHART_ID_KPI_TOTAL,
    CHART_ID_MAIN_CHART,
    CHART_ID_DATA_TABLE,
)


def resolve_dataset_id_for_dashboard() -> str:
    """Resolve the dataset ID for all charts in this dashboard.

    Ensures every chart ID maps to exactly one dataset ID.
    """
    chart_ids = [
        CHART_ID_KPI_TOTAL,
        CHART_ID_MAIN_CHART,
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

        # Extract unique values
        categories = sorted(df[category_col].dropna().unique().tolist())

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
    category_col = COLUMN_MAP["category"]

    # Strip timezone for filter compatibility (Parquet returns UTC-aware)
    df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.tz_convert(None)
    df["DateOnly"] = df[date_col].dt.date

    # Build FilterSet using shared helper
    filter_map = {
        "date": (date_col, start_date, end_date),
        "category": (category_col, category_values),
    }
    filters = build_filter_set_from_map(filter_map)

    return apply_filters(df, filters)
```

### 2-5. `_filters.py` - フィルタUI構築（5個以上のフィルタがある場合）

```python
"""Filter UI layout builder for Your Dashboard."""
from dash import html
import dash_bootstrap_components as dbc

from src.components.filters import create_date_range_filter, create_slicer_filter
from ._constants import ID_PREFIX


def build_filter_layout(opts: dict) -> list:
    """Build the filter section rows for Your Dashboard layout.

    Args:
        opts: Dict returned by load_filter_options(), containing
            categories, min_date, max_date.

    Returns:
        List of html.Div components representing filter rows.
    """
    filter_row = html.Div([
        dbc.Col([
            create_date_range_filter(
                filter_id=f"{ID_PREFIX}filter-date",
                column_name="Date Range",
                min_date=opts["min_date"],
                max_date=opts["max_date"],
            ),
        ], md=6),
        dbc.Col([
            create_slicer_filter(
                filter_id=f"{ID_PREFIX}filter-category",
                column_name="Category",
                options=opts["categories"],
                clear_button_id=f"{ID_PREFIX}ctrl-clear-category",
            ),
        ], md=6),
    ], className="mb-3")

    return [filter_row]
```

### 2-6. `_layout.py` - レイアウト構築

```python
"""Layout builder for Your Dashboard page."""
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.data.parquet_reader import ParquetReader
from ._constants import (
    ID_PREFIX,
    CHART_ID_KPI_TOTAL,
    CHART_ID_MAIN_CHART,
    CHART_ID_DATA_TABLE,
)
from ._data_loader import load_filter_options, resolve_dataset_id_for_dashboard
from ._filters import build_filter_layout


def build_layout():
    """Build and return the dashboard layout."""
    reader = ParquetReader()

    try:
        dataset_id = resolve_dataset_id_for_dashboard()
        opts = load_filter_options(reader, dataset_id)
    except Exception:
        opts = {
            "categories": [],
            "min_date": None,
            "max_date": None,
        }

    filter_rows = build_filter_layout(opts)

    return html.Div([
        html.H1("Your Dashboard Title", className="mb-4"),

        # Filters
        *filter_rows,

        # KPI Cards Row
        dbc.Row([
            dbc.Col([html.Div(id=CHART_ID_KPI_TOTAL)], md=4),
        ], className="mb-4"),

        # Charts Row
        dbc.Row([
            dbc.Col([dcc.Graph(id=CHART_ID_MAIN_CHART)], md=12),
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

### 2-7. `_callbacks.py` - コールバック実装

```python
"""Your Dashboard callbacks module.

Thin orchestration layer: data loading -> aggregation -> shared builders.
All chart/table rendering uses the shared build_chart / build_table
infrastructure with declarative Specs defined in _constants.py.
"""
from dash import callback, Input, Output

from src.data.parquet_reader import ParquetReader
from src.components.cards import create_kpi_card
from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.empty_states import create_empty_figure, create_empty_table, create_error_figure
from src.utils.callback_helpers import register_clear_callbacks
from ._constants import (
    ID_PREFIX,
    CHART_ID_KPI_TOTAL,
    CHART_ID_MAIN_CHART,
    CHART_ID_DATA_TABLE,
    COLUMN_MAP,
    MAIN_CHART_SPEC,
    DETAIL_TABLE_SPEC,
    CLEAR_PAIRS,
)
from ._data_loader import load_and_filter_data, resolve_dataset_id_for_dashboard


@callback(
    [
        Output(CHART_ID_KPI_TOTAL, "children"),
        Output(CHART_ID_MAIN_CHART, "figure"),
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
        category_values: Selected categories from filter (list or None)

    Returns:
        Tuple of (kpi_total, main_chart_fig, table_component)
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
                create_kpi_card("Total", "0"),
                empty_fig,
                create_empty_table(),
            )

        value_col = COLUMN_MAP["value"]

        # Calculate KPIs
        total_value = filtered_df[value_col].sum()

        # KPI Cards
        kpi_total = create_kpi_card("Total", f"{total_value:,.2f}")

        # Chart: Main Chart
        chart_fig = build_chart(filtered_df, MAIN_CHART_SPEC)

        # Data Table
        display_df = filtered_df.head(100)
        _, table_component = build_table(display_df, DETAIL_TABLE_SPEC)

        return (
            kpi_total,
            chart_fig,
            table_component,
        )

    except Exception as e:
        # Error state using shared functions
        error_fig = create_error_figure(error=str(e))

        return (
            create_kpi_card("Total", "Error"),
            error_fig,
            create_empty_table(message=f"Error loading data: {str(e)}"),
        )


# Register clear callbacks for filter clear buttons
register_clear_callbacks(CLEAR_PAIRS)
```

### 2-8. `__init__.py` - Dash登録

```python
"""Your Dashboard page."""
import dash
from ._layout import build_layout


def layout():
    """Return Your Dashboard layout."""
    return build_layout()


dash.register_page(__name__, path="/your-dashboard", name="Your Dashboard", order=1, layout=layout)

# Import callbacks to register them with Dash
from . import _callbacks  # noqa: F401, E402
```

### 2-9. `SPEC.md` - ユーザー向け設計書

```markdown
# Your Dashboard

## 概要
このダッシュボードの目的を説明します。

## データソース
- データセット: your-dataset-id
- 更新頻度: 毎日

## フィルタの使い方

### 日付範囲
データを期間で絞り込みます。

### カテゴリ
特定のカテゴリでフィルタリングします。

## チャート・テーブルの見方

### Main Chart
日別の推移を表示します。

### Detailed Data
フィルタリングされた全データを表示します。
```

### 2-10. `app.py` へのインポート追加

`app.py` に以下を追加:

```python
import src.pages.your_dashboard  # noqa: F401
```

---

## Phase 3: コールバック実装

### 共通基盤の使用

全ページで以下の共通基盤を使用します:

```python
# チャート/テーブル構築
from src.charts.table_builder import build_table
from src.charts.chart_builder import build_chart
from src.charts.specs import TableSpec, ChartSpec

# 空状態・エラー状態
from src.charts.empty_states import (
    create_empty_figure,
    create_empty_table,
    create_error_figure,
)

# フィルタヘルパー
from src.utils.filter_helpers import build_filter_set_from_map

# コールバックヘルパー
from src.utils.callback_helpers import register_clear_callbacks
```

### コールバックパターン

`_callbacks.py` では以下のパターンに従います:

1. 薄いオーケストレータ層（ビジネスロジックは最小限）
2. フィルタ入力受取 -> `data_loader` 呼出 -> `chart_builders` 呼出 -> 戻り値返却
3. 空状態・エラー状態は共通関数を使用
4. クリアコールバックは `register_clear_callbacks(CLEAR_PAIRS)` を末尾で呼ぶ

### キャッシュの活用

`get_cached_dataset()` を使用することで、データ読み込みが高速化されます。初回読み込み時のみS3から取得し、以降はキャッシュから返されます。

---

## Phase 4: デバッグ・検証

### 公式ドキュメント参照ルール

コンポーネント仕様に迷った場合は、まず公式ドキュメントを確認します。

- Dash Core Components: `https://dash.plotly.com/dash-core-components`
- Dropdown: `https://dash.plotly.com/dash-core-components/dropdown`

運用上の優先順位は以下です。

1. 公式仕様（プロパティ、挙動、制約）
2. このスキルのプロジェクト固有ルール（Dash 4.x回避策、ID運用、Docker反映など）

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

#### Bug Pattern 2: CSS z-index問題

**症状:**
ドロップダウンやDatePickerのメニューがKPIカードの後ろに隠れる、マウス位置で不安定に表示される。

**原因:**
Dash 4.x (Radix UI) のポップアップが低いz-indexで表示される。

**解決法:**
`assets/03-components.css` に以下を追加:

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

また、KPIカードのhover効果で `transform` を使っている場合は削除:

```css
.kpi-card:hover {
  /* transform: translateY(-2px); を削除 */
  box-shadow: var(--shadow-md), var(--shadow-glow);
  border-color: var(--border-accent);
}
```

#### Bug Pattern 3: Docker環境でアセットが反映されない

**原因:**
`assets/` や `backend/` がコンテナにマウントされていない。

**解決法:**
`docker-compose.yml` にボリュームマウントを追加:

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

開発完了前に以下を確認:

- [ ] データがMinIOにParquet形式でアップロードされている
- [ ] `data_sources.yml` に全chart_id -> dataset_idマッピングが定義されている
- [ ] `SPEC.md` が作成されている（フィルタ、チャート、テーブルの説明を含む）
- [ ] `app.py` に明示的インポートが追加されている
- [ ] ダッシュボードがエラーなく表示される
- [ ] datetimeカラムのtimezoneが適切に処理されている（`.dt.tz_convert(None)` を使用）
- [ ] ドロップダウン/DatePickerが正しく前面に表示される
- [ ] Docker環境でassetsがマウントされている
- [ ] ハードリロード（Cmd+Shift+R / Ctrl+Shift+F5）でCSSが反映される

---

## インポートパス一覧

### チャート/テーブル構築

```python
from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.specs import ChartSpec, TableSpec
```

### 空状態・エラー状態

```python
from src.charts.empty_states import (
    create_empty_figure,
    create_empty_table,
    create_error_figure,
)
```

### フィルタヘルパー

```python
from src.utils.filter_helpers import build_filter_set_from_map
```

### コールバックヘルパー

```python
from src.utils.callback_helpers import register_clear_callbacks
```

### データソース解決

```python
from src.data.data_source_registry import resolve_dataset_id
```

### データ読込・フィルタリング

```python
from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.filter_engine import (
    FilterSet,
    CategoryFilter,
    DateRangeFilter,
    apply_filters,
    extract_unique_values,
)
```

### UIコンポーネント

```python
from src.components.cards import create_kpi_card
from src.components.filters import (
    create_date_range_filter,
    create_category_filter,
    create_slicer_filter,
)
```

---

## 関連スキル

- **etl-workflow**: データ取得とETL処理（CSV、API、RDS、S3などからParquetへの変換）
- **dash-spec-updater**: SPEC.md更新専用スキル

## 追加リソース

- 詳細なトラブルシューティング: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 実際のコード例: [examples.md](examples.md)
- プロジェクト固有の学習メモ: [`CLAUDE.md`](CLAUDE.md)
