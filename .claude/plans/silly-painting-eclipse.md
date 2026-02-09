# Plan: Chart Density改善をhamm_overviewの全チャートに横展開

## Context

Content Metadata セクション（Original Language, Dialogue, Genre）に適用済みの「Chart Density」パターン（コンパクトなカードパディング、タイトル重複排除、tight margin、ツールバー非表示、responsive表示）を、hamm_overview ページ内の残り5つのチャートに横展開する。

対象チャート:
1. Volume Chart（stacked_bar, 2系列）
2. Issues Ratio（pie）
3. Intervention per Screener Type（stacked_bar, 2系列）
4. User Intervention Breakdown（bar, 単一系列）
5. HAMM Intervention Breakdown（bar, 単一系列）

## 改善パターンの概要（4レイヤー）

| レイヤー | 変更内容 |
|---------|---------|
| `_constants.py` | height=460, 明示的show_legend, text_template追加 |
| `_chart_builders.py` | `apply_compact_chart_layout()` 呼び出し + トレース調整 |
| `_layout.py` | density CSS class + config追加 |
| CSS (`05-charts.css`) | 変更不要（既存ルールで対応） |

---

## Step 1: テスト先行（TDD RED）

対象ファイル:
- `tests/unit/pages/hamm_overview/test_constants.py`
- `tests/unit/pages/hamm_overview/test_chart_builders.py`
- `tests/unit/pages/hamm_overview/test_layout.py`

### 1a. test_constants.py

新規テストクラス追加:

```
class TestErrorChartSpecs:
    - ERROR_RATIO_SPEC: height==460, show_legend==True, chart_type=="pie"
    - ERROR_BY_SCREENER_SPEC: height==460, text_template=="%{y}", chart_type=="stacked_bar"
    - USER_BREAKDOWN_SPEC: height==460, text_template=="%{y}", show_legend==False
    - HAMM_BREAKDOWN_SPEC: height==460, text_template=="%{y}", show_legend==False
```

既存テスト更新:
- `TestVolumeChartSpec.test_volume_chart_spec_height`: 400 -> 460

### 1b. test_chart_builders.py

新規テストクラス追加:

```
class TestErrorChartBuilders:
    (各チャートに対して)
    - test_returns_figure
    - test_title_is_none (apply_compact_chart_layout確認)
    - test_margin_t_is_8 (tight top margin確認)
```

既存テスト更新:
- `TestBuildVolumeChart.test_height_is_400` -> `test_height_is_460` (400 -> 460)
- `TestBuildVolumeChart.test_custom_margin`: margin値更新 (t: 20->8)
- `TestBuildVolumeChart.test_custom_margin` に `title.text is None` アサーション追加

### 1c. test_layout.py

既存テスト更新:
- `TestContentMetadataSection.test_content_metadata_cards_have_class`: 3 -> 8（全density card数）

新規テストクラス追加:

```
class TestVolumeSectionDensity:
    - Volume Chart の dcc.Graph に chart-density-graph class と config あり

class TestErrorDetailsDensity:
    - 4つの Error チャートに chart-density-graph class と config あり
    - Error Details の Row に chart-density-row class あり
    - Error Details の Card に chart-density-card class あり
```

---

## Step 2: _constants.py 修正

ファイル: `src/pages/hamm_overview/_constants.py`

### VOLUME_CHART_SPEC (L143-154)
- `height`: 400 -> 460

### ERROR_RATIO_SPEC (L178-184)
- `height`: 400 -> 460
- 追加: `show_legend=True`

### ERROR_BY_SCREENER_SPEC (L186-196)
- `height`: 400 -> 460
- 追加: `text_template="%{y}"`

### USER_BREAKDOWN_SPEC (L198-207)
- `height`: 400 -> 460
- 追加: `text_template="%{y}"`
- 追加: `show_legend=False`

### HAMM_BREAKDOWN_SPEC (L209-218)
- `height`: 400 -> 460
- 追加: `text_template="%{y}"`
- 追加: `show_legend=False`

---

## Step 3: _chart_builders.py 修正

ファイル: `src/pages/hamm_overview/_chart_builders.py`

### build_volume_chart (L49-72)
手動 `fig.update_layout(...)` を `apply_compact_chart_layout()` に置換:

```python
def build_volume_chart(df):
    fig = build_chart(df, VOLUME_CHART_SPEC)
    if len(fig.data) > 0:
        fig.update_traces(textposition="inside")
    return apply_compact_chart_layout(
        fig,
        margin={"l": 30, "r": 10, "t": 8, "b": 60},
        legend={"orientation": "h", "y": -0.25},
    )
```

### build_error_ratio_chart (L114-123)
pie chart - Original Language パターンに準拠:

```python
def build_error_ratio_chart(df):
    fig = build_chart(df, ERROR_RATIO_SPEC)
    if len(df) > 0 and len(fig.data) > 0:
        fig.update_traces(
            textinfo="label+value+percent",
            textposition="inside",
        )
    return apply_compact_chart_layout(
        fig,
        margin={"l": 8, "r": 8, "t": 8, "b": 34},
        legend={"orientation": "h", "x": 0.0, "y": -0.06},
    )
```

### build_error_by_screener_chart (L126-135)
stacked_bar - Dialogue パターンに準拠:

```python
def build_error_by_screener_chart(df):
    fig = build_chart(df, ERROR_BY_SCREENER_SPEC)
    if len(fig.data) > 0:
        fig.update_traces(textposition="inside")
    return apply_compact_chart_layout(
        fig,
        margin={"l": 16, "r": 70, "t": 8, "b": 30},
        legend={"orientation": "v", "x": 1.02, "xanchor": "left", "y": 0.5, "yanchor": "middle"},
    )
```

### build_user_breakdown_chart (L138-147)
bar (単一系列) - Genre パターンに準拠:

```python
def build_user_breakdown_chart(df):
    fig = build_chart(df, USER_BREAKDOWN_SPEC)
    return apply_compact_chart_layout(
        fig,
        margin={"l": 24, "r": 8, "t": 8, "b": 44},
    )
```

### build_hamm_breakdown_chart (L150-159)
bar (単一系列) - Genre パターンに準拠:

```python
def build_hamm_breakdown_chart(df):
    fig = build_chart(df, HAMM_BREAKDOWN_SPEC)
    return apply_compact_chart_layout(
        fig,
        margin={"l": 24, "r": 8, "t": 8, "b": 44},
    )
```

---

## Step 4: _layout.py 修正

ファイル: `src/pages/hamm_overview/_layout.py`

### Volume Chart (L83-100)
Row class に `chart-density-row` 追加、Volume Chart の Card に `chart-density-card` 追加、dcc.Graph にclass + config追加。
注: Volume Table 側の Card には `chart-density-card` を付与しない（テーブルは対象外）。

```python
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Volume Table", className="card-header"),
            dbc.CardBody([html.Div(id=CHART_ID_VOLUME_TABLE)]),
        ]),
    ], md=6),
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Volume Chart", className="card-header"),
            dbc.CardBody([
                dcc.Graph(
                    id=CHART_ID_VOLUME_CHART,
                    className="chart-density-graph",
                    config={"displayModeBar": False, "responsive": True},
                ),
            ]),
        ], className="chart-density-card"),
    ], md=6),
], className="mb-4 chart-density-row"),
```

### Error Details Row 1 (L177-194)
Row class に `chart-density-row` 追加、両 Card に `chart-density-card` 追加、両 dcc.Graph にclass + config追加。

```python
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Issues Ratio", className="card-header"),
            dbc.CardBody([
                dcc.Graph(
                    id=CHART_ID_ERROR_RATIO,
                    className="chart-density-graph",
                    config={"displayModeBar": False, "responsive": True},
                ),
            ]),
        ], className="chart-density-card"),
    ], md=6),
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Intervention per Screener Type", className="card-header"),
            dbc.CardBody([
                dcc.Graph(
                    id=CHART_ID_ERROR_BY_SCREENER,
                    className="chart-density-graph",
                    config={"displayModeBar": False, "responsive": True},
                ),
            ]),
        ], className="chart-density-card"),
    ], md=6),
], className="mb-3 chart-density-row"),
```

### Error Details Row 2 (L195-212)
同様にRow class + Card class + Graph class/config追加。

```python
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("User Intervention Breakdown", className="card-header"),
            dbc.CardBody([
                dcc.Graph(
                    id=CHART_ID_USER_BREAKDOWN,
                    className="chart-density-graph",
                    config={"displayModeBar": False, "responsive": True},
                ),
            ]),
        ], className="chart-density-card"),
    ], md=6),
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("HAMM Intervention Breakdown", className="card-header"),
            dbc.CardBody([
                dcc.Graph(
                    id=CHART_ID_HAMM_BREAKDOWN,
                    className="chart-density-graph",
                    config={"displayModeBar": False, "responsive": True},
                ),
            ]),
        ], className="chart-density-card"),
    ], md=6),
], className="mb-4 chart-density-row"),
```

---

## Step 5: テスト実行（TDD GREEN）

全テストが通ることを確認:
```bash
python3 -m pytest tests/unit/pages/hamm_overview/ -v
```

---

## 対象ファイル一覧

| ファイル | 変更種別 |
|---------|---------|
| `tests/unit/pages/hamm_overview/test_constants.py` | テスト追加・更新 |
| `tests/unit/pages/hamm_overview/test_chart_builders.py` | テスト追加・更新 |
| `tests/unit/pages/hamm_overview/test_layout.py` | テスト追加・更新 |
| `src/pages/hamm_overview/_constants.py` | ChartSpec更新 |
| `src/pages/hamm_overview/_chart_builders.py` | compact layout適用 |
| `src/pages/hamm_overview/_layout.py` | density class/config追加 |

再利用する既存関数:
- `src/charts/layout_helpers.py:apply_compact_chart_layout()`（既にimport済み）

## 検証方法

1. `python3 -m pytest tests/unit/pages/hamm_overview/ -v` で全テストPASS
2. Docker環境でダッシュボード表示確認（ハードリロード）
3. チャートタイトルがCardHeaderのみに表示（Plotly titleなし）
4. ツールバー非表示、responsive動作
5. 各チャートのデータラベル・凡例が正しく表示
