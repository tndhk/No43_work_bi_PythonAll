# cursor_usage チャートデザイン改善計画

## Context

hamm_overview の Content Metadata チャート（pie, stacked_bar, bar）に施したデザイン改善を、cursor_usage のチャート（line, bar, pie）にも展開する。改善内容は: タイトル重複排除（CardHeader があるので図内タイトル不要）、マージン圧縮、テキストラベル表示、displayModeBar 非表示、CSS によるカード密度調整。

## 変更対象チャート（cursor_usage）

| チャート | タイプ | レイアウト | 改善ポイント |
|---------|--------|----------|------------|
| Daily Cost Trend | line | md=12（全幅） | タイトル除去、マージン圧縮、モードバー非表示 |
| Token Efficiency by Model | bar | md=6 | タイトル除去、マージン圧縮、text_template追加、モードバー非表示 |
| Cost Distribution by Model | pie | md=6 | タイトル除去、マージン圧縮、textinfo/textposition追加、凡例再配置、モードバー非表示 |

## 設計判断: CSS クラスの汎用化

hamm_overview で使用中の `hamm-metadata-*` プレフィックスのCSSクラスを、汎用的な `chart-density-*` クラスにリネームする。これにより cursor_usage でも同じCSSルールを再利用でき、将来のページ追加時も重複を防げる。

リネーム対応表:
- `hamm-metadata-row` -> `chart-density-row`
- `hamm-metadata-card` -> `chart-density-card`
- `hamm-metadata-graph` -> `chart-density-graph`

## 実装ステップ（TDD: テスト先行）

### Step 1: CSS クラスの汎用化（hamm_overview リファクタ）

ファイル: `assets/05-charts.css`, `src/pages/hamm_overview/_layout.py`, `tests/unit/pages/hamm_overview/test_layout.py`

- `05-charts.css`: `hamm-metadata-*` -> `chart-density-*` に一括リネーム
- `hamm_overview/_layout.py`: className を `chart-density-*` に変更
- `hamm_overview/test_layout.py`: テスト内の className アサーションを更新

### Step 2: cursor_usage テスト追加（RED フェーズ）

#### 2a. `tests/unit/pages/cursor_usage/test_constants.py` に追加

- `COST_TREND_SPEC.height == 460`
- `TOKEN_EFFICIENCY_SPEC.height == 460`, `text_template == "%{y}"`
- `MODEL_DISTRIBUTION_SPEC.height == 460`, `show_legend == True`

#### 2b. `tests/unit/pages/cursor_usage/test_chart_builders.py` 新規作成

- `build_daily_cost_trend`: `fig.layout.title.text is None`, `fig.layout.margin.t == 8`
- `build_token_efficiency_chart`: `fig.layout.title.text is None`, `fig.layout.margin.t == 8`, `bar_trace.textposition == "inside"`
- `build_model_distribution_chart`: `fig.layout.title.text is None`, `fig.layout.legend.orientation == "h"`, `pie_trace.textinfo == "label+value+percent"`, `pie_trace.textposition == "inside"`

#### 2c. `tests/unit/pages/cursor_usage/test_layout.py` に追加

- Charts Row 1, 2 に `chart-density-row` クラスが付与されている
- 3つの dbc.Card に `chart-density-card` クラスが付与されている
- 3つの dcc.Graph に `chart-density-graph` クラスと `config={"displayModeBar": False, "responsive": True}` がある

### Step 3: cursor_usage 実装（GREEN フェーズ）

#### 3a. `src/pages/cursor_usage/_constants.py`

```
COST_TREND_SPEC:     height=460
TOKEN_EFFICIENCY_SPEC: height=460, text_template="%{y}"
MODEL_DISTRIBUTION_SPEC: height=460
```

#### 3b. `src/pages/cursor_usage/_chart_builders.py`

- `_apply_cu_chart_layout()` ヘルパー追加（hamm_overview の `_apply_metadata_chart_layout` と同パターン）
  - title除去、マージン設定、axis title除去、uniformtext設定
- `build_daily_cost_trend`: 後処理追加 - margin `{"l": 48, "r": 16, "t": 8, "b": 40}`（X軸の日付ラベル考慮）
- `build_token_efficiency_chart`: 後処理追加 - margin `{"l": 24, "r": 8, "t": 8, "b": 44}`, textposition="inside"
- `build_model_distribution_chart`: 後処理追加 - margin `{"l": 8, "r": 8, "t": 8, "b": 34}`, textinfo="label+value+percent", textposition="inside", 水平凡例

#### 3c. `src/pages/cursor_usage/_layout.py`

- Charts Row 1, 2: `className="mb-4 chart-density-row"` 追加
- dbc.Card: `className="chart-density-card"` 追加
- dcc.Graph: `className="chart-density-graph"`, `config={"displayModeBar": False, "responsive": True}` 追加

### Step 4: SPEC.md 更新

ファイル: `src/pages/cursor_usage/SPEC.md`

チャート説明に表示改善の記述を追加:
- 日次コスト推移: 表示領域を拡大し可読性を向上
- トークン効率: バー内に値ラベルを表示
- モデル別コスト割合: 円内にラベル・件数・割合を表示

### Step 5: 検証

- `py_compile` で構文チェック（変更した全 .py ファイル）
- テスト実行（pytest で cursor_usage + hamm_overview の該当テスト）
- コードレビューエージェントで品質確認

## 対象ファイル一覧

| ファイル | 操作 |
|---------|------|
| `assets/05-charts.css` | 編集（クラス名リネーム） |
| `src/pages/hamm_overview/_layout.py` | 編集（クラス名リネーム） |
| `tests/unit/pages/hamm_overview/test_layout.py` | 編集（クラス名リネーム） |
| `src/pages/cursor_usage/_constants.py` | 編集（height, text_template） |
| `src/pages/cursor_usage/_chart_builders.py` | 編集（レイアウト後処理追加） |
| `src/pages/cursor_usage/_layout.py` | 編集（className, config追加） |
| `src/pages/cursor_usage/SPEC.md` | 編集（チャート説明更新） |
| `tests/unit/pages/cursor_usage/test_chart_builders.py` | 新規作成 |
| `tests/unit/pages/cursor_usage/test_constants.py` | 編集（height等のアサーション追加） |
| `tests/unit/pages/cursor_usage/test_layout.py` | 編集（className, configアサーション追加） |

## 再利用する既存コード

- `src/charts/chart_builder.build_chart()` - チャート生成の基盤
- `src/charts/specs.ChartSpec` - Spec定義
- hamm_overview の `_apply_metadata_chart_layout()` パターン（cursor_usage用にコピー＆調整）
