# レイアウトパターン集

このドキュメントでは、Plotly Dashダッシュボードで使用する実践的なレイアウトパターンを提供します。

---

## フィルタ行レイアウトパターン

ダッシュボードのフィルタ行には、2つの主要なアプローチがあります。

### パターン選択ガイド

| パターン | 使い分け | 実装方法 | メリット | デメリット |
|----------|----------|----------|---------|---------|
| Bootstrap Grid | フィルタ6個以下<br>非対称幅が必要 | `dbc.Row` + `dbc.Col` with `md` | 柔軟な幅調整<br>高さ揃えが容易 | 多列時にコード冗長 |
| CSS Grid | フィルタ7個以上<br>均等幅で1行配置 | `html.Div` + `.filter-row-Ncol` | コード簡潔<br>均等配置が容易 | 非対称幅には不向き |

### フィルタ5個以上の場合: _filters.py への委譲

フィルタが5個以上ある場合は、`_filters.py` にフィルタレイアウト構築を分離します。

```python
# _filters.py
from dash import html
from src.components.filters import create_slicer_filter, create_category_filter
from ._constants import (
    FILTER_ID_REGION,
    FILTER_ID_YEAR,
    CTRL_ID_CLEAR_REGION,
    CTRL_ID_CLEAR_YEAR,
    # ... その他のID定義
)

def build_filter_layout(opts: dict, title_element=None) -> list:
    """フィルタ行を構築して返す。

    Args:
        opts: load_filter_options()が返すフィルタオプション辞書
        title_element: 任意で第1行に追加するタイトル要素

    Returns:
        html.Div要素のリスト（複数のフィルタ行）
    """
    # タイトル + 主要フィルタ3個（Bootstrap Grid or CSS Grid）
    filters_row1 = [
        create_slicer_filter(
            filter_id=FILTER_ID_REGION,
            column_name="Region",
            options=opts["regions"],
            clear_button_id=CTRL_ID_CLEAR_REGION,  # クリアボタンID
        ),
        create_slicer_filter(
            filter_id=FILTER_ID_YEAR,
            column_name="Year",
            options=opts["years"],
            clear_button_id=CTRL_ID_CLEAR_YEAR,
        ),
        # ... その他のフィルタ
    ]

    if title_element is not None:
        filters_row1 = [title_element] + filters_row1

    title_row = html.Div(filters_row1, className="mb-3 filter-row-title-3filters")

    # 詳細フィルタ7個（CSS Grid）
    detail_row = html.Div([
        create_category_filter(...),
        create_slicer_filter(...),
        # ... 計7個
    ], className="mb-3 filter-row-7col")

    return [title_row, detail_row]


# _layout.py
from ._filters import build_filter_layout

def build_layout() -> html.Div:
    # データ読み込み
    opts = load_filter_options(...)

    # タイトル要素の定義
    title_element = html.Div("Dashboard Title", style=title_style)

    # フィルタ行を委譲
    filter_rows = build_filter_layout(opts, title_element=title_element)

    return html.Div([
        dmc.MantineProvider([
            filter_rows[0],  # タイトル行 + 主要フィルタ
            filter_rows[1],  # 詳細フィルタ行
            # KPI, チャート, テーブル...
        ]),
    ], className="page-container")
```

---

## Bootstrap Grid パターン

### 基本実装

```python
# Row 1: タイトル50% + フィルタ3個（各16.7%）
dbc.Row([
    dbc.Col([
        html.Div("Dashboard Title", style=title_style),
    ], md=6),  # 50%幅
    dbc.Col([
        create_slicer_filter(
            filter_id="filter-1",
            column_name="Filter 1",
            options=options1,
            clear_button_id="clear-filter-1",  # クリアボタンID（任意）
        ),
    ], md=2),  # 16.7%幅
    dbc.Col([
        create_slicer_filter(
            filter_id="filter-2",
            column_name="Filter 2",
            options=options2,
            clear_button_id="clear-filter-2",
        ),
    ], md=2),
    dbc.Col([
        create_category_filter(
            filter_id="filter-3",
            column_name="Filter 3",
            options=options3,
        ),
    ], md=2),
], className="mb-3 filter-row")
```

### clear_button_id パラメータ

`create_slicer_filter()` および `create_category_filter()` は `clear_button_id` パラメータをサポートします。これにより、フィルタ内にクリアボタンを追加でき、ユーザーが選択をリセットできます。

```python
from src.components.filters import create_slicer_filter
from ._constants import FILTER_ID_REGION, CTRL_ID_CLEAR_REGION

create_slicer_filter(
    filter_id=FILTER_ID_REGION,
    column_name="Region",
    options=options,
    multi=True,
    clear_button_id=CTRL_ID_CLEAR_REGION,  # クリアボタンIDを指定
)
```

コールバック登録（`_callbacks.py`）:

```python
from src.utils.callback_helpers import register_clear_callbacks
from ._constants import CLEAR_PAIRS

# CLEAR_PAIRS は _constants.py で定義
# CLEAR_PAIRS = [
#     (CTRL_ID_CLEAR_REGION, FILTER_ID_REGION),
#     (CTRL_ID_CLEAR_YEAR, FILTER_ID_YEAR),
#     # ...
# ]

# コールバック関数定義の最後に追加
register_clear_callbacks(CLEAR_PAIRS)
```

### タイトルカードのスタイル（高さ揃え）

```python
title_style = {
    "backgroundColor": "#2f5f8f",
    "color": "white",
    "padding": "24px",
    "borderRadius": "8px",
    "fontSize": "32px",
    "fontWeight": "600",
    "height": "100%",           # 高さをカラムに合わせる
    "display": "flex",          # フレックスレイアウト
    "alignItems": "center",     # 垂直中央揃え
}
```

### Bootstrap Gridカラム幅

| md値 | 幅（%） | 用途例 |
|------|---------|-------|
| md=12 | 100% | 全幅タイトル、1列レイアウト |
| md=6 | 50% | 2列レイアウト、タイトル+フィルタ |
| md=4 | 33.3% | 3列レイアウト、KPIカード3個 |
| md=3 | 25% | 4列レイアウト、均等4分割 |
| md=2 | 16.7% | 6列レイアウト、タイトル50%+フィルタ3個 |

---

## CSS Grid パターン

### 基本実装（7列均等配置）

```python
# Row 2: 7フィルタを均等配置
html.Div([
    create_category_filter(
        filter_id="filter-1",
        column_name="Filter 1",
        options=options1,
    ),
    create_slicer_filter(
        filter_id="filter-2",
        column_name="Filter 2",
        options=options2,
    ),
    # ... 残り5個のフィルタ
], className="mb-3 filter-row-7col")
```

注意: `dbc.Col`でラップしません。直接子要素として配置します。

### CSS定義（`assets/03-components.css`）

```css
/* 7列均等グリッド */
.filter-row-7col {
  display: grid !important;
  grid-template-columns: repeat(7, 1fr);  /* 7列均等（各14.3%幅） */
  gap: 1rem;                              /* 列間の間隔 */
  align-items: stretch;                   /* 高さを揃える */
}

/* カードヘッダーのテキスト切り詰め */
.filter-row-7col .filter-header,
.filter-row-7col .card-header {
  white-space: nowrap;         /* 折り返さない */
  overflow: hidden;            /* はみ出しを隠す */
  text-overflow: ellipsis;     /* "..." で切り詰め */
}

/* グリッドセル内でカードを高さ100%に */
.filter-row-7col > .filter-card {
  height: 100%;
  margin-bottom: 0;
}
```

### カスタマイズ例（5列、8列など）

```css
/* 5列均等グリッド（各20%幅） */
.filter-row-5col {
  display: grid !important;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
  align-items: stretch;
}

/* 8列均等グリッド（各12.5%幅） */
.filter-row-8col {
  display: grid !important;
  grid-template-columns: repeat(8, 1fr);
  gap: 1rem;
  align-items: stretch;
}
```

---

## 密集レイアウト向けCSSカスタマイズ

7列以上のグリッドでは、カード内のパディングを縮小してスペースを節約します。

### フィルタカードのコンパクト化

```css
/* 7列グリッド内のフィルタカード: パディング縮小 */
.filter-row-7col .filter-card {
  padding: 0.5rem !important;
}

.filter-row-7col .filter-card .card-header {
  padding: 0.5rem !important;
  margin-bottom: 0.5rem !important;
  font-size: 0.85rem !important;    /* ヘッダー文字サイズも縮小 */
}

.filter-row-7col .filter-card .card-body {
  padding: 0.5rem !important;
}
```

---

## Mantine Chip（スライサーフィルタ）のテキスト切り詰め

### 問題: 長いテキストでレイアウトが崩れる

Mantine Chipを使用するスライサーフィルタで、テキストが長い場合（例: "Crime/Mystery/Thriller"）、ピルが縦に積み重なったり、カードからはみ出したりします。

### 解決策: CSS Gridグリッド内でのChip最適化

```css
/* 7列グリッド内のChip: テキスト切り詰め対応 */
.filter-row-7col .mantine-Chip-label {
  max-width: 100%;
  white-space: nowrap;         /* 折り返さない */
  overflow: hidden;            /* はみ出しを隠す */
  text-overflow: ellipsis;     /* "..." で切り詰め */
  display: inline-block;
  font-size: 0.7rem !important;    /* フォントサイズ縮小 */
  padding: 3px 8px !important;     /* パディング縮小 */
}

/* 7列グリッド内のChipGroup: 横並び配置 */
.filter-row-7col .mantine-ChipGroup-root {
  display: flex !important;
  flex-direction: row !important;     /* 横並び（縦積み防止） */
  flex-wrap: wrap !important;         /* 折り返し許可 */
  gap: 3px !important;                /* Chip間の間隔縮小 */
  align-items: flex-start !important;
}

.filter-row-7col .mantine-Chip-root {
  margin: 0 !important;
  flex-shrink: 0;                     /* Chipが縮まない */
}
```

### 通常サイズのChip（6列以下のレイアウト）

```css
/* デフォルトのMantine Chip styling（変更不要） */
.mantine-Chip-label {
  background-color: var(--bg-elevated) !important;
  color: var(--text-secondary) !important;
  border: 1px solid var(--border-subtle) !important;
  border-radius: 16px !important;
  padding: 4px 12px !important;
  font-size: 0.8rem !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}
```

---

## dmc.MantineProvider のラップスコープ

`dmc.MantineProvider` は Mantine コンポーネント（Chip, ChipGroup など）を使用する際に必要です。ラップするスコープには2つのパターンがあります。

### パターンA: ページ全体をラップ

```python
def build_layout() -> html.Div:
    return html.Div([
        dmc.MantineProvider([
            # フィルタ行
            html.Div([...], className="filter-row-7col"),
            # KPI行
            dbc.Row([...]),
            # チャート行
            dbc.Row([...]),
        ]),
    ], className="page-container")
```

利点: 全体で一貫したMantineテーマを適用可能
欠点: 不要な箇所までMantineプロバイダに依存

### パターンB: フィルタ行のみをラップ（hamm_overview）

```python
def build_layout() -> html.Div:
    filter_rows = build_filter_layout(opts, title_element=title_element)

    return html.Div([
        dmc.MantineProvider([
            filter_rows[0],  # タイトル行 + 主要フィルタ
            filter_rows[1],  # 詳細フィルタ行
        ]),  # MantineProviderはフィルタ行のみ
        # KPI行（Mantineプロバイダ外）
        dbc.Row([...]),
        # チャート行（Mantineプロバイダ外）
        dbc.Row([...]),
    ], className="page-container")
```

利点: 必要な範囲にのみMantine依存を限定
欠点: Mantineコンポーネントをフィルタ外で使う場合は別途ラップが必要

どちらのパターンも有効です。Mantineコンポーネントを使用する範囲に応じて選択してください。

---

## 実装例: HAMM Overviewレイアウト

### 完全なレイアウトコード（_layout.py）

```python
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from src.data.parquet_reader import ParquetReader
from src.data.data_source_registry import resolve_dataset_id
from ._constants import DASHBOARD_ID, CHART_ID_VOLUME_TABLE, CHART_ID_VOLUME_CHART
from ._data_loader import load_filter_options
from ._filters import build_filter_layout

def build_layout() -> html.Div:
    # データ読み込みとフィルタオプション取得
    reader = ParquetReader()
    dataset_id = resolve_dataset_id(DASHBOARD_ID, CHART_ID_VOLUME_TABLE)
    opts = load_filter_options(reader, dataset_id)

    # タイトルスタイル（高さ揃え）
    title_style = {
        "backgroundColor": "#2f5f8f",
        "color": "white",
        "padding": "24px",
        "borderRadius": "8px",
        "fontSize": "32px",
        "fontWeight": "600",
        "height": "100%",
        "display": "flex",
        "alignItems": "center",
    }

    # タイトル要素を作成
    title_element = html.Div("HAMM Overview \U0001f437", style=title_style)

    # フィルタ行を委譲（_filters.py）
    filter_rows = build_filter_layout(opts, title_element=title_element)

    return html.Div([
        dmc.MantineProvider([
            filter_rows[0],  # タイトル行 + 主要フィルタ3個
            filter_rows[1],  # 詳細フィルタ7個
        ]),  # MantineProviderはフィルタ行のみ（パターンB）

        # KPI行、チャート行など（Mantineプロバイダ外）
        dbc.Row([
            dbc.Col([
                html.H4("Volume Chart", className="mb-2"),
                dcc.Graph(id=CHART_ID_VOLUME_CHART),
            ], md=12),
        ], className="mb-4"),
    ], className="page-container")
```

### フィルタレイアウトコード（_filters.py）

```python
from dash import html
from src.components.filters import create_category_filter, create_slicer_filter
from ._constants import (
    FILTER_ID_REGION,
    FILTER_ID_YEAR,
    FILTER_ID_MONTH,
    FILTER_ID_TASK_ID,
    # ... その他のID
    CTRL_ID_CLEAR_REGION,
    CTRL_ID_CLEAR_YEAR,
    # ... その他のクリアボタンID
)

def build_filter_layout(opts: dict, title_element=None) -> list:
    """フィルタ行を構築して返す。

    Args:
        opts: load_filter_options()が返すフィルタオプション辞書
        title_element: 任意で第1行に追加するタイトル要素

    Returns:
        html.Div要素のリスト（2行分）
    """
    # タイトル + 主要フィルタ3個
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
        create_category_filter(
            filter_id=FILTER_ID_MONTH,
            column_name="Month",
            options=opts["months"],
        ),
    ]

    if title_element is not None:
        filters_row1 = [title_element] + filters_row1

    title_row = html.Div(filters_row1, className="mb-3 filter-row-title-3filters")

    # 詳細フィルタ7個（CSS Grid）
    detail_row = html.Div([
        create_category_filter(
            filter_id=FILTER_ID_TASK_ID,
            column_name="Task ID",
            options=opts["task_ids"],
            multi=True,
        ),
        # ... 残り6個のフィルタ（clear_button_id付き）
    ], className="mb-3 filter-row-7col")

    return [title_row, detail_row]
```

### 完全なCSS（`assets/03-components.css`）

```css
/* ===== Bootstrap Grid フィルタ行 ===== */
.filter-row {
  display: flex;
  align-items: stretch;  /* 高さを揃える */
}

.filter-row > [class*="col"] {
  display: flex;
}

.filter-row > [class*="col"] > .filter-card {
  width: 100%;
}

/* ===== CSS Grid フィルタ行（7列均等） ===== */
.filter-row-7col {
  display: grid !important;
  grid-template-columns: repeat(7, 1fr);
  gap: 1rem;
  align-items: stretch;
}

/* カードヘッダーのテキスト切り詰め */
.filter-row-7col .filter-header,
.filter-row-7col .card-header {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* グリッドセル内でカードを高さ100%に */
.filter-row-7col > .filter-card {
  height: 100%;
  margin-bottom: 0;
}

/* 7列グリッド内のフィルタカード: パディング縮小 */
.filter-row-7col .filter-card {
  padding: 0.5rem !important;
}

.filter-row-7col .filter-card .card-header {
  padding: 0.5rem !important;
  margin-bottom: 0.5rem !important;
  font-size: 0.85rem !important;
}

.filter-row-7col .filter-card .card-body {
  padding: 0.5rem !important;
}

/* ===== Mantine Chip（スライサーフィルタ） ===== */
/* 7列グリッド内のChip: テキスト切り詰め対応 */
.filter-row-7col .mantine-Chip-label {
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  font-size: 0.7rem !important;
  padding: 3px 8px !important;
}

/* 7列グリッド内のChipGroup: 横並び配置 */
.filter-row-7col .mantine-ChipGroup-root {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: wrap !important;
  gap: 3px !important;
  align-items: flex-start !important;
}

.filter-row-7col .mantine-Chip-root {
  margin: 0 !important;
  flex-shrink: 0;
}
```

---

## ベストプラクティス

### フィルタ行レイアウト選択

1. フィルタ6個以下 → Bootstrap Grid（`dbc.Row` + `dbc.Col`）
2. フィルタ7個以上 → CSS Grid（`html.Div` + `.filter-row-Ncol`）
3. 非対称幅が必要（タイトル50% + フィルタ3個など） → Bootstrap Grid

### Mantine Chipの最適化

- 7列以上のグリッドでは必ずChip用CSSを追加
- `flex-direction: row` を明示的に設定（縦積み防止）
- `text-overflow: ellipsis` でテキスト切り詰め

### 高さ揃え

- Bootstrap Grid: `className="filter-row"` + `.filter-row { align-items: stretch; }`
- CSS Grid: `align-items: stretch` をグリッドに設定
- タイトルカード: `height: 100%` + `display: flex` + `alignItems: center`

### Docker環境での確認

CSS変更後は必ず:
1. `docker-compose.yml` で `./assets:/app/assets` がマウントされているか確認
2. ブラウザでハードリロード（Cmd+Shift+R / Ctrl+Shift+F5）

---

## トラブルシューティング

### 問題: Chipが縦に積み重なる

原因: ChipGroupの`flex-direction`が設定されていない

解決策:
```css
.filter-row-7col .mantine-ChipGroup-root {
  flex-direction: row !important;
}
```

### 問題: テキストが切り詰められない

原因: `text-overflow: ellipsis` には `white-space: nowrap` と `overflow: hidden` が必要

解決策:
```css
.filter-row-7col .mantine-Chip-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

### 問題: カードの高さが揃わない

原因: グリッドコンテナまたはフレックスコンテナで `align-items: stretch` が設定されていない

解決策:
```css
.filter-row-7col {
  align-items: stretch;
}
```

---

## 参照

- 実装例: `src/pages/hamm_overview/_layout.py`
- CSS定義: `assets/03-components.css` L135-410
- コンポーネント: `src/components/filters.py`
