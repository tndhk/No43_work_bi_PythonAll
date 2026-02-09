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

参考実装: [`src/pages/cursor_usage/_constants.py`](../../src/pages/cursor_usage/_constants.py)

主要な構成要素:

- `DASHBOARD_ID`: ダッシュボード識別子（data_sources.yml参照用）
- `DATASET_ID`: レガシー/フォールバック用データセットID
- `ID_PREFIX`: コンポーネントID名前空間（他ページとの衝突防止）
- `CHART_ID_*`: 各チャート/テーブルのID定義
- `COLUMN_MAP`: 論理名 → DataFrameカラム名のマッピング
- `CLEAR_PAIRS`: クリアボタンのペア定義 `[(filter_id, clear_button_id)]`
- `ChartSpec` / `TableSpec`: チャート・テーブルの宣言的定義

コード例（抜粋）:

```python
from src.charts.specs import ChartSpec, TableSpec

DASHBOARD_ID: str = "your_dashboard"
DATASET_ID: str = "your-dataset-id"
ID_PREFIX: str = "yd-"

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

参考実装: [`src/pages/cursor_usage/_data_loader.py`](../../src/pages/cursor_usage/_data_loader.py)

このファイルは以下の関数を提供します:

1. `resolve_dataset_id_for_dashboard()`: 全チャートが単一データセットを使用することを保証
2. `load_filter_options()`: フィルタの選択肢を読み込み（カテゴリ、日付範囲等）
3. `load_and_filter_data()`: データ読込とフィルタリングを実行

主要な処理:

```python
from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset
from src.data.filter_engine import apply_filters
from src.utils.filter_helpers import build_filter_set_from_map

def load_filter_options(reader: ParquetReader, dataset_id: str) -> dict:
    """フィルタオプションを読み込み"""
    df = get_cached_dataset(reader, dataset_id)
    
    # Timezone除去（Parquetは UTC-aware で返す）
    df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.tz_convert(None)
    
    # ユニーク値抽出
    categories = sorted(df[category_col].dropna().unique().tolist())
    # ...

def load_and_filter_data(reader, dataset_id, start_date, end_date, categories):
    """データ読込とフィルタリング"""
    df = get_cached_dataset(reader, dataset_id)
    
    # build_filter_set_from_map でFilterSet構築
    filter_map = {
        "date": (date_col, start_date, end_date),
        "category": (category_col, categories),
    }
    filters = build_filter_set_from_map(filter_map)
    
    return apply_filters(df, filters)
```

複数データセットの例: [`src/pages/apac_dot_due_date/_data_loader.py`](../../src/pages/apac_dot_due_date/_data_loader.py)

### 2-5. `_filters.py` - フィルタUI構築（5個以上のフィルタがある場合）

参考実装: [`src/pages/apac_dot_due_date/_filters.py`](../../src/pages/apac_dot_due_date/_filters.py)

フィルタが5個未満の場合は、`_layout.py`に直接記述することも可能です。

主要な構造:

```python
from src.components.filters import (
    create_date_range_filter,
    create_slicer_filter,
)

def build_filter_layout(opts: dict) -> list:
    """フィルタセクションのレイアウトを構築
    
    Args:
        opts: load_filter_options()の戻り値
    
    Returns:
        html.Div のリスト
    """
    filter_row = html.Div([
        dbc.Col([create_date_range_filter(...)], md=6),
        dbc.Col([create_slicer_filter(...)], md=6),
    ], className="mb-3")
    
    return [filter_row]
```

### 2-6. `_layout.py` - レイアウト構築

参考実装: [`src/pages/cursor_usage/_layout.py`](../../src/pages/cursor_usage/_layout.py)

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

参考実装: [`src/pages/cursor_usage/_callbacks.py`](../../src/pages/cursor_usage/_callbacks.py)

薄いオーケストレータ層として実装します:

1. フィルタ入力を受け取る
2. `load_and_filter_data()` でデータ取得
3. 集計・計算を実行
4. `build_chart()` / `build_table()` で描画
5. 空状態・エラー状態は共通関数を使用

基本パターン:

```python
from dash import callback, Input, Output
from src.charts.chart_builder import build_chart
from src.charts.table_builder import build_table
from src.charts.empty_states import create_empty_figure, create_empty_table
from src.utils.callback_helpers import register_clear_callbacks

@callback(
    [Output(CHART_ID_KPI, "children"),
     Output(CHART_ID_CHART, "figure"),
     Output(CHART_ID_TABLE, "children")],
    [Input(f"{ID_PREFIX}filter-date", "start_date"),
     Input(f"{ID_PREFIX}filter-date", "end_date"),
     Input(f"{ID_PREFIX}filter-category", "value")],
)
def update_dashboard(start_date, end_date, categories):
    """ダッシュボード更新コールバック"""
    try:
        # データ読込・フィルタリング
        filtered_df = load_and_filter_data(...)
        
        if len(filtered_df) == 0:
            return (create_kpi_card("Total", "0"),
                    create_empty_figure(),
                    create_empty_table())
        
        # 集計
        total = filtered_df["value"].sum()
        
        # 描画（Spec使用）
        kpi = create_kpi_card("Total", f"{total:,.2f}")
        chart_fig = build_chart(filtered_df, CHART_SPEC)
        _, table = build_table(filtered_df, TABLE_SPEC)
        
        return (kpi, chart_fig, table)
        
    except Exception as e:
        return (create_kpi_card("Error", "—"),
                create_error_figure(error=str(e)),
                create_empty_table())

# クリアボタン登録
register_clear_callbacks(CLEAR_PAIRS)
```

### 2-8. `__init__.py` - Dash登録

参考実装: [`src/pages/cursor_usage/__init__.py`](../../src/pages/cursor_usage/__init__.py)

```python
"""Your Dashboard page."""
import dash
from ._layout import build_layout

def layout():
    return build_layout()

dash.register_page(
    __name__,
    path="/your-dashboard",
    name="Your Dashboard",
    order=1,
    layout=layout
)

from . import _callbacks  # noqa: F401, E402
```

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
