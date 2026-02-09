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

参考実装: [`src/pages/hamm_overview/_constants.py`](../../src/pages/hamm_overview/_constants.py)

主要な構成要素:

- `DASHBOARD_ID`: ダッシュボード識別子（data_sources.yml参照用）
- `DATASET_ID`: レガシー/フォールバック用データセットID
- `ID_PREFIX`: コンポーネントID名前空間（他ページとの衝突防止）
- `CHART_ID_*`: 各チャート/テーブルのID定義
- `FILTER_ID_*`: 各フィルタのID定義
- `CTRL_ID_CLEAR_*`: 各クリアボタンのID定義
- `COLUMN_MAP`: 論理名 → DataFrameカラム名のマッピング
- `DERIVED_*`: 派生カラム名（`_year`, `_month` 等、データ加工で追加するカラム）
- `CLEAR_PAIRS`: クリアボタンのペア定義 `[(filter_id, clear_button_id)]`
- `ChartSpec` / `TableSpec`: チャート・テーブルの宣言的定義

#### ID命名規則

コンポーネントIDは以下の命名規則に従います:

| 種別 | プレフィックス | 例 |
|------|---------------|-----|
| チャート/テーブル | `CHART_ID_*` | `CHART_ID_VOLUME_TABLE`, `CHART_ID_ERROR_RATIO` |
| フィルタ | `FILTER_ID_*` | `FILTER_ID_REGION`, `FILTER_ID_YEAR` |
| クリアボタン | `CTRL_ID_CLEAR_*` | `CTRL_ID_CLEAR_REGION`, `CTRL_ID_CLEAR_YEAR` |

全てのIDには `ID_PREFIX` を付与し、他ページとの衝突を防止します。

コード例（抜粋）:

```python
from src.charts.specs import ChartSpec, TableSpec

DASHBOARD_ID: str = "your_dashboard"
DATASET_ID: str = "your-dataset-id"
ID_PREFIX: str = "yd-"

# Chart IDs
CHART_ID_MAIN_TABLE: str = f"{ID_PREFIX}main-table"
CHART_ID_MAIN_CHART: str = f"{ID_PREFIX}main-chart"

# Filter IDs
FILTER_ID_REGION: str = f"{ID_PREFIX}filter-region"
FILTER_ID_YEAR: str = f"{ID_PREFIX}filter-year"

# Per-slicer clear control IDs
CTRL_ID_CLEAR_REGION: str = f"{ID_PREFIX}ctrl-clear-region"
CTRL_ID_CLEAR_YEAR: str = f"{ID_PREFIX}ctrl-clear-year"

# Clear callback pairs: (filter_id, clear_button_id)
CLEAR_PAIRS: list[tuple[str, str]] = [
    (FILTER_ID_REGION, CTRL_ID_CLEAR_REGION),
    (FILTER_ID_YEAR, CTRL_ID_CLEAR_YEAR),
]

# Derived column names (created during data processing)
DERIVED_YEAR: str = "_year"
DERIVED_MONTH: str = "_month"

# Mapping from logical keys to DataFrame column names
COLUMN_MAP: dict[str, str] = {
    "date": "Date",
    "category": "Category",
    "value": "Value",
}

MAIN_CHART_SPEC: ChartSpec = ChartSpec(
    title="Main Chart",
    chart_type="line",
    x_column=COLUMN_MAP["date"],
    y_columns=[COLUMN_MAP["value"]],
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

参考実装: [`src/pages/hamm_overview/_data_loader.py`](../../src/pages/hamm_overview/_data_loader.py)

このファイルは以下の関数を提供します:

1. `resolve_dataset_id_for_dashboard()`: 全チャートが単一データセットを使用することを保証
2. `load_filter_options()`: フィルタの選択肢を読み込み（カテゴリ、日付範囲等）
3. `load_and_filter_data()`: データ読込とフィルタリングを実行

#### FILTER_COLUMN_MAP パターン

`COLUMN_MAP` に派生カラムを追加した `FILTER_COLUMN_MAP` を定義し、フィルタリング時に使用します:

```python
from ._constants import COLUMN_MAP, DERIVED_YEAR, DERIVED_MONTH

# Extend COLUMN_MAP with derived columns for filter_set_from_map compatibility
FILTER_COLUMN_MAP: dict[str, str] = {
    **COLUMN_MAP,
    "year": DERIVED_YEAR,
    "month": DERIVED_MONTH,
}
```

#### 主要な処理

```python
from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.filter_engine import apply_filters
from src.utils.filter_helpers import build_filter_set_from_map

def _prepare_base_df(df: pd.DataFrame) -> pd.DataFrame:
    """データの前処理（timezone除去、派生カラム追加）"""
    df = df.copy()
    
    # Timezone除去（Parquetは UTC-aware で返す）
    df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.tz_convert(None)
    
    # 派生カラム追加
    df[DERIVED_YEAR] = df[date_col].dt.strftime("%Y")
    df[DERIVED_MONTH] = df[date_col].dt.strftime("%b")
    
    return df

def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:
    """フィルタオプションを読み込み"""
    df = get_cached_dataset(reader, dataset_id)
    df = _prepare_base_df(df)
    
    # ユニーク値抽出
    return {
        "years": sorted(df[DERIVED_YEAR].dropna().unique().tolist()),
        "months": df[DERIVED_MONTH].dropna().unique().tolist(),
        "categories": sorted(df[category_col].dropna().unique().tolist()),
        # ...
    }

def load_and_filter_data(
    reader: ParquetReader,
    dataset_id: str,
    column_map: dict[str, str],
    filter_pairs: list[tuple[str, list]],
) -> pd.DataFrame:
    """データ読込とフィルタリング
    
    Args:
        reader: ParquetReader instance
        dataset_id: Dataset ID to load
        column_map: FILTER_COLUMN_MAP (includes derived columns)
        filter_pairs: List of (logical_key, values) tuples from callback
    """
    df = get_cached_dataset(reader, dataset_id)
    df = _prepare_base_df(df)
    
    # build_filter_set_from_map でFilterSet構築
    filter_map = {}
    for key, values in filter_pairs:
        if values:
            filter_map[key] = (column_map[key], values)
    
    filters = build_filter_set_from_map(filter_map)
    return apply_filters(df, filters)
```

複数データセットの例: [`src/pages/apac_dot_due_date/_data_loader.py`](../../src/pages/apac_dot_due_date/_data_loader.py)

### 2-5. `_filters.py` - フィルタUI構築（5個以上のフィルタがある場合）

参考実装: [`src/pages/hamm_overview/_filters.py`](../../src/pages/hamm_overview/_filters.py)

フィルタが5個未満の場合は、`_layout.py`に直接記述することも可能です。

#### Slicer フィルタとクリアボタン

`create_slicer_filter()` には `clear_button_id` パラメータがあり、ヘッダー内にクリアボタンを統合できます:

```python
from src.components.filters import create_slicer_filter
from ._constants import FILTER_ID_REGION, CTRL_ID_CLEAR_REGION

create_slicer_filter(
    filter_id=FILTER_ID_REGION,
    column_name="Region",
    options=opts["regions"],
    clear_button_id=CTRL_ID_CLEAR_REGION,  # ヘッダーにクリアボタン追加
)
```

#### 主要な構造

```python
from dash import html
import dash_bootstrap_components as dbc
from src.components.filters import (
    create_category_filter,
    create_slicer_filter,
)
from ._constants import (
    FILTER_ID_REGION,
    FILTER_ID_YEAR,
    CTRL_ID_CLEAR_REGION,
    CTRL_ID_CLEAR_YEAR,
)

def build_filter_layout(opts: dict) -> list:
    """フィルタセクションのレイアウトを構築
    
    Args:
        opts: load_filter_options()の戻り値
    
    Returns:
        html.Div のリスト
    """
    # Row 1: Primary filters
    primary_row = html.Div([
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
    ], className="mb-3 filter-row")
    
    return [primary_row]
```

### 2-6. `_layout.py` - レイアウト構築

参考実装: [`src/pages/hamm_overview/_layout.py`](../../src/pages/hamm_overview/_layout.py)

主要な処理フロー:

1. ParquetReaderを初期化
2. `resolve_dataset_id_for_dashboard()` でデータセットID取得
3. `load_filter_options()` でフィルタオプション読み込み
4. `build_filter_layout()` でフィルタUI構築（または直接記述）
5. レイアウトを返す

基本構造:

```python
from dash import html, dcc
import dash_bootstrap_components as dbc

def build_layout():
    """ダッシュボードレイアウトを構築"""
    reader = ParquetReader()
    dataset_id = resolve_dataset_id_for_dashboard()
    opts = load_filter_options(reader, dataset_id)
    
    return html.Div([
        html.H1("Title", className="mb-4"),
        
        # フィルタ
        *build_filter_layout(opts),
        
        # KPI Cards
        dbc.Row([dbc.Col([html.Div(id=CHART_ID_KPI)])], className="mb-4"),
        
        # チャート
        dbc.Row([dbc.Col([dcc.Graph(id=CHART_ID_CHART)])], className="mb-4"),
        
        # テーブル
        dbc.Row([dbc.Col([html.Div(id=CHART_ID_TABLE)])]),
    ], className="page-container")
```

#### チャート/テーブルのカード配置（必須ルール）

全てのチャート、テーブル、KPIカードは `dbc.Card` で囲むこと。

理由:
- ページ全体の灰色背景（`--bg-base`）との対比で視認性向上
- フィルターエリアとのデザイン統一
- `assets/03-components.css` のカードスタイルが自動適用（白背景、境界線、ホバー効果）

推奨構造:

```python
# チャート配置の例
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Chart Title", className="card-header"),
            dbc.CardBody([
                dcc.Graph(id=CHART_ID),
            ]),
        ]),
    ], md=6),
], className="mb-4")

# テーブル配置の例
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Table Title", className="card-header"),
            dbc.CardBody([
                html.Div(id=TABLE_ID),
            ]),
        ]),
    ], md=12),
], className="mb-4")
```

参考実装: [`src/pages/hamm_overview/_layout.py`](../../src/pages/hamm_overview/_layout.py)

### 2-7. `_callbacks.py` - コールバック実装

参考実装: [`src/pages/hamm_overview/_callbacks.py`](../../src/pages/hamm_overview/_callbacks.py)

薄いオーケストレータ層として実装します:

1. フィルタ入力を受け取る
2. `filter_pairs` リストを構築
3. `load_and_filter_data()` でデータ取得
4. 集計・計算を実行
5. `build_chart()` / `build_table()` で描画
6. 空状態・エラー状態は共通関数を使用

#### filter_pairs パターン

コールバック内で `filter_pairs` リストを構築し、`load_and_filter_data()` に渡します:

```python
def _ensure_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

filter_pairs = [
    ("region", _ensure_list(region_values)),
    ("year", _ensure_list(year_values)),
    ("month", _ensure_list(month_values)),
    ("content_type", _ensure_list(content_type_values)),
]

df = load_and_filter_data(reader, dataset_id, FILTER_COLUMN_MAP, filter_pairs)
```

#### 基本パターン

```python
from dash import callback, Input, Output
from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.empty_states import create_empty_figure, create_empty_table
from src.utils.callback_helpers import register_clear_callbacks
from ._data_loader import FILTER_COLUMN_MAP, load_and_filter_data

@callback(
    Output(CHART_ID_TABLE, "children"),
    Output(CHART_ID_CHART, "figure"),
    Input(FILTER_ID_REGION, "value"),
    Input(FILTER_ID_YEAR, "value"),
    Input(FILTER_ID_MONTH, "value"),
)
def update_dashboard(region_values, year_values, month_values):
    """ダッシュボード更新コールバック"""
    reader = ParquetReader()
    dataset_id = resolve_dataset_id_for_dashboard()
    
    filter_pairs = [
        ("region", _ensure_list(region_values)),
        ("year", _ensure_list(year_values)),
        ("month", _ensure_list(month_values)),
    ]
    
    try:
        df = load_and_filter_data(reader, dataset_id, FILTER_COLUMN_MAP, filter_pairs)
        
        if len(df) == 0:
            return create_empty_table(), create_empty_figure()
        
        # 描画（Spec使用）
        _, table = build_table(df, TABLE_SPEC)
        chart_fig = build_chart(df, CHART_SPEC)
        
        return table, chart_fig
        
    except Exception as exc:
        error_msg = html.P(f"Error loading data: {exc}", className="text-danger")
        return error_msg, create_empty_figure(message="Error loading data")

# クリアボタン登録
register_clear_callbacks(CLEAR_PAIRS)
```

### 2-8. `__init__.py` - Dash登録

参考実装: [`src/pages/hamm_overview/__init__.py`](../../src/pages/hamm_overview/__init__.py)

```python
"""Your Dashboard page."""
import dash

from ._layout import build_layout
from . import _callbacks  # noqa: F401


dash.register_page(
    __name__,
    path="/your-dashboard",
    name="Your Dashboard",
    order=1,
    layout=build_layout,
)
```

注意点:
- `layout=build_layout` と関数参照を渡す（関数呼び出しではない）
- `_callbacks` のインポートは `register_page` の前でも後でもよいが、明示的にインポートすること

### 2-9. `SPEC.md` - ユーザー向け設計書

参考実装: [`src/pages/cursor_usage/SPEC.md`](../../src/pages/cursor_usage/SPEC.md)

ユーザー向けドキュメント（日本語、技術詳細なし）:

- 概要: ダッシュボードの目的
- データソース: データセットID、更新頻度
- フィルタの使い方: 各フィルタの説明
- チャート・テーブルの見方: 各コンポーネントの解説
- KPIカード: 該当する場合

詳細は `dash-spec-updater` スキルを参照してください。

### 2-10. `app.py` へのインポート追加

`app.py` に以下を追加:

```python
import src.pages.your_dashboard  # noqa: F401
```

---

## フィルタ追加時の修正順序

既存のダッシュボードに新しいフィルタを追加する場合、以下の順序で修正します:

1. `_constants.py`: ID定義を追加
   - `FILTER_ID_*`: フィルタID
   - `CTRL_ID_CLEAR_*`: クリアボタンID（Slicerの場合）
   - `CLEAR_PAIRS`: クリアペアに追加

2. `_data_loader.py`: データ処理を追加
   - `FILTER_COLUMN_MAP`: 派生カラムの場合は追加
   - `load_filter_options()`: フィルタオプションの抽出を追加

3. `_filters.py`: UI作成を追加
   - `build_filter_layout()`: フィルタUIを追加

4. `_callbacks.py`: コールバック入力を追加
   - `Input()`: 新しいフィルタのInputを追加
   - `filter_pairs`: 新しいフィルタのペアを追加

5. `_layout.py`: 通常は自動配置（`build_filter_layout()` 経由）

この順序で依存関係が構成されるため、逆順で修正するとインポートエラーが発生します。

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
[data-radix-popper-content-wrapper] {
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
- [ ] 全てのID定数が `_constants.py` に定義されている（`FILTER_ID_*`, `CHART_ID_*`, `CTRL_ID_CLEAR_*`）
- [ ] `CLEAR_PAIRS` にSlicerフィルタのクリアペアが全て登録されている
- [ ] `register_clear_callbacks(CLEAR_PAIRS)` が `_callbacks.py` 末尾で呼ばれている

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
