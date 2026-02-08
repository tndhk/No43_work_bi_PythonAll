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
        ),
    ], md=2),  # 16.7%幅
    dbc.Col([
        create_slicer_filter(
            filter_id="filter-2",
            column_name="Filter 2",
            options=options2,
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

## 実装例: HAMM Overviewレイアウト

### 完全なレイアウトコード

```python
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

    return html.Div([
        dmc.MantineProvider([
            # Row 1: タイトル50% + フィルタ3個（Bootstrap Grid）
            dbc.Row([
                dbc.Col([
                    html.Div("HAMM Overview 🐷", style=title_style),
                ], md=6),
                dbc.Col([
                    create_slicer_filter(
                        filter_id=FILTER_ID_REGION,
                        column_name="Region",
                        options=opts["regions"],
                        multi=True,
                    ),
                ], md=2),
                dbc.Col([
                    create_slicer_filter(
                        filter_id=FILTER_ID_YEAR,
                        column_name="Year",
                        options=opts["years"],
                        multi=True,
                    ),
                ], md=2),
                dbc.Col([
                    create_category_filter(
                        filter_id=FILTER_ID_MONTH,
                        column_name="Month",
                        options=opts["months"],
                        multi=True,
                    ),
                ], md=2),
            ], className="mb-3 filter-row"),

            # Row 2: 7フィルタ均等配置（CSS Grid）
            html.Div([
                create_category_filter(
                    filter_id=FILTER_ID_TASK_ID,
                    column_name="Task ID",
                    options=opts["task_ids"],
                    multi=False,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_CONTENT_TYPE,
                    column_name="Content Type",
                    options=opts["content_types"],
                    multi=True,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_ORIGINAL_LANGUAGE,
                    column_name="Original Language",
                    options=opts["original_languages"],
                    multi=True,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_DIALOGUE,
                    column_name="Was Dialogue Provided?",
                    options=opts["dialogue_options"],
                    multi=True,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_GENRE,
                    column_name="Genre",
                    options=opts["genres"],
                    multi=True,
                ),
                create_category_filter(
                    filter_id=FILTER_ID_ERROR_CODE,
                    column_name="Error Code",
                    options=opts["error_codes"],
                    multi=True,
                ),
                create_slicer_filter(
                    filter_id=FILTER_ID_ERROR_TYPE,
                    column_name="Error Type",
                    options=opts["error_types"],
                    multi=True,
                ),
            ], className="mb-3 filter-row-7col"),

            # KPIカード、チャート、テーブルなど...
        ]),
    ], className="page-container")
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
