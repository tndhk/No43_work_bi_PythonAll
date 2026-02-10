# page_spec.yaml リファレンス

最終更新: 2026-02-10

## 概要

`page_spec.yaml` は、Dashダッシュボードページの構造と挙動を宣言的に定義するための設定ファイルです。

### 目的と利点

従来の手書きコード（500-1000行）を100-200行のYAML設定に置き換え、以下の利点を実現します。

- 開発速度10倍向上: コード生成により新規ページを5-10分で作成可能
- 保守性向上: ビジネスロジックがYAMLで一元管理され、変更が容易
- 品質向上: スキーマバリデーションにより設定ミスを事前検出
- 統一性: 全ページで同一のパターンとベストプラクティスを強制

### 従来の手書き vs SPEC-Driven

| 項目 | 従来の手書き | SPEC-Driven |
|------|-------------|------------|
| コード量 | 500-1000行 | 100-200行（YAML） |
| 開発時間 | 2-4時間 | 5-10分 |
| 保守性 | 散在するロジック | 一元化された設定 |
| バリデーション | なし | スキーマバリデーション |
| 一貫性 | 手動維持 | 自動保証 |

## トップレベル構造

```yaml
metadata:        # ダッシュボードメタデータ
column_map:      # 論理名→物理名のマッピング
derived_columns: # 派生カラム定義（オプション）
filters:         # フィルタ定義
layout:          # レイアウト構造
components:      # コンポーネント定義（KPI、チャート、テーブル）
custom_logic:    # カスタムロジック（オプション）
```

## セクション詳細

### metadata

ダッシュボードの基本情報を定義します。

```yaml
metadata:
  dashboard_id: "hamm_overview"      # ページID（URL: /hamm_overview）
  id_prefix: "hamm-"                 # コンポーネントID接頭辞
  dataset_id: "hamm-dashboard"       # データセットID
  title: "HAMM Overview"             # ページタイトル
  description: "HAMM overview..."    # 説明（SPEC.md用）
```

| フィールド | 必須 | 説明 | 例 |
|-----------|-----|------|-----|
| dashboard_id | Yes | ページ識別子（URL、ディレクトリ名） | `"hamm_overview"` |
| id_prefix | Yes | 全コンポーネントID接頭辞（ID衝突防止） | `"hamm-"` |
| dataset_id | Yes | データソースID（S3/MinIO） | `"hamm-dashboard"` |
| title | Yes | ページ表示タイトル | `"HAMM Overview"` |
| description | No | ページ説明（SPEC.md生成用） | `"HAMM overview dashboard..."` |

### column_map

論理名（YAML内で使用）と物理名（Parquet内のカラム名）のマッピングを定義します。

```yaml
column_map:
  id: "id"
  title: "title"
  status: "status"
  created_at: "created_at"
  region: "notification_company_name"
  content_type: "video_type_description"
```

論理名は短く読みやすい名前、物理名は実際のデータソースのカラム名を指定します。

使用例:
- フィルタ: `column: "region"` → 実際は `"notification_company_name"` でフィルタリング
- チャート: `x_column: "status"` → 実際は `"status"` カラムを使用

### derived_columns

データソースに存在しないカラムを、既存カラムから派生して作成します。

```yaml
derived_columns:
  - name: "_year"
    type: "year"
    source_column: "created_at"

  - name: "_month"
    type: "month"
    source_column: "created_at"

  - name: "_fiscal_year"
    type: "fiscal_year"
    source_column: "created_at"

  - name: "duration_seconds"
    type: "timedelta_to_seconds"
    source_column: "video_duration"

  - name: "custom_field"
    type: "custom"
    function: "compute_custom_field"
    depends_on: ["status", "region"]
```

#### 対応する派生タイプ

| type | 説明 | 必要フィールド | 例 |
|------|------|---------------|-----|
| `year` | datetimeから年を抽出 | `source_column` | 2024 |
| `month` | datetimeから月を抽出 | `source_column` | "2024-01" |
| `datetime_year` | datetimeから年を抽出（別名） | `source_column` | 2024 |
| `datetime_month` | datetimeから月を抽出（別名） | `source_column` | "2024-01" |
| `fiscal_year` | 会計年度を計算（4月開始） | `source_column` | "FY2024" |
| `fiscal_quarter` | 会計四半期を計算 | `source_column` | "Q1" |
| `iso_week` | ISO週番号を抽出 | `source_column` | "2024-W01" |
| `timedelta_to_seconds` | timedelta を秒数に変換 | `source_column` | 3600 |
| `date_extract` | 日付から任意の要素を抽出 | `source_column`, `format` | カスタム |
| `custom` | カスタム関数で計算 | `function`, `depends_on` | - |

customタイプの場合、`_custom_logic.py` に対応する関数を実装する必要があります。

### filters

ダッシュボードで使用するフィルタを定義します。

```yaml
filters:
  - type: "slicer"
    id: "filter-region"
    label: "Region"
    column: "region"
    has_clear_button: true
    clear_button_id: "clear-region"

  - type: "category"
    id: "filter-month"
    label: "Month"
    column: "_month"
    multi: false

  - type: "dropdown"
    id: "filter-content-type"
    label: "Content Type"
    column: "content_type"
    multi: true
    placeholder: "Select content types..."

  - type: "date"
    id: "filter-date-range"
    label: "Date Range"
    column: "created_at"

  - type: "chip_group"
    id: "filter-cadence"
    label: "Cadence"
    column: "cadence"
    options:
      - "Weekly"
      - "Bi-weekly"
      - "Monthly"
```

#### フィルタタイプ

| type | 説明 | column必須 | その他のフィールド |
|------|------|-----------|------------------|
| `slicer` | 複数選択可能なリスト | Yes | `has_clear_button`, `clear_button_id` |
| `category` | カテゴリ選択（単一/複数） | Yes | `multi`, `default_value` |
| `dropdown` | ドロップダウン選択 | Yes | `multi`, `placeholder`, `default_value` |
| `date` | 日付範囲選択 | Yes | - |
| `chip_group` | チップ型選択 | No | `options` |

#### 共通フィールド

| フィールド | 必須 | 説明 | デフォルト |
|-----------|-----|------|----------|
| id | Yes | コンポーネントID（`id_prefix` + 識別子） | - |
| label | Yes | 表示ラベル | - |
| column | Depends | フィルタ対象カラム（chip_group以外は必須） | - |
| has_clear_button | No | クリアボタン表示（slicerのみ） | false |
| clear_button_id | No | クリアボタンのID | - |
| multi | No | 複数選択可否（category, dropdownのみ） | false |
| placeholder | No | プレースホルダーテキスト（dropdownのみ） | - |
| options | No | 固定オプションリスト（chip_groupのみ） | - |
| default_value | No | デフォルト値 | - |

### layout

コンポーネントの配置を定義します。Bootstrap 12グリッドシステムを使用します。

```yaml
layout:
  sections:
    # Section 1: KPIカード
    - title: "Key Metrics"
      description: "Main performance indicators"
      rows:
        - items:
            - component_id: "kpi-total"
              md: 4
            - component_id: "kpi-active"
              md: 4
            - component_id: "kpi-completed"
              md: 4
          className: "mb-3"

    # Section 2: チャートとテーブル
    - rows:
        - items:
            - component_id: "volume-table"
              md: 6
            - component_id: "volume-chart"
              md: 6
          className: "mb-4"
```

#### 構造

```
layout
  └─ sections (list)
      ├─ title (optional)
      ├─ description (optional)
      └─ rows (list)
          ├─ className (optional)
          └─ items (list)
              ├─ component_id (required)
              ├─ md (required, 1-12)
              └─ className (optional)
```

| フィールド | 必須 | 説明 | デフォルト |
|-----------|-----|------|----------|
| sections | Yes | セクションリスト | - |
| title | No | セクションタイトル | - |
| description | No | セクション説明 | - |
| rows | Yes | 行リスト | - |
| items | Yes | 行内のコンポーネント配置 | - |
| component_id | Yes | 配置するコンポーネントのID | - |
| md | Yes | Bootstrap幅（1-12） | 12 |
| className | No | CSSクラス | - |

### components

KPIカード、チャート、テーブルを定義します。

#### KPIカード

```yaml
- type: "kpi"
  id: "kpi-total-screens"
  title: "Total Screens Processed"
  bg_color: "#d6e4f0"
  accent_color: "#2f5f8f"
  spec:
    value_column: "id"
    agg_func: "nunique"
    format: "{:,.0f}"
    subtitle: "All time"
  data_source: "filtered_data"
```

KPIカードspecフィールド:

| フィールド | 必須 | 説明 | デフォルト |
|-----------|-----|------|----------|
| value_column | No | 集計対象カラム | - |
| agg_func | Yes | 集計関数 | "sum" |
| format | No | 数値フォーマット | "{:,.0f}" |
| subtitle | No | サブタイトル | - |
| color_bg | No | 背景色（spec外で指定も可） | - |
| color_accent | No | アクセント色（spec外で指定も可） | - |

集計関数（agg_func）:
- `sum`: 合計
- `count`: 件数
- `mean`: 平均
- `median`: 中央値
- `max`: 最大
- `min`: 最小
- `nunique`: ユニーク件数

#### チャート

```yaml
- type: "chart"
  id: "volume-chart"
  title: "Volume Chart"
  spec:
    title: "Volume Chart"
    chart_type: "stacked_bar"
    x_column: "_month"
    y_columns:
      - "Completed"
      - "Invalid"
    color_map:
      Completed: "#2d6a2e"
      Invalid: "#9ca3af"
    height: 460
    text_template: "%{y}"
    show_legend: true
  data_source: "filtered_data"
  data_transform:
    operations:
      - type: "group_by"
        group_columns:
          - "_month"
          - "status"
        agg_funcs:
          id: "nunique"
```

チャートspecフィールド:

| フィールド | 必須 | 説明 | デフォルト |
|-----------|-----|------|----------|
| title | Yes | チャートタイトル | - |
| chart_type | Yes | チャートタイプ | - |
| x_column | Yes | X軸カラム | - |
| y_columns | Yes | Y軸カラムリスト | - |
| color_map | No | 系列色マッピング | 自動 |
| height | No | チャート高さ（px） | 400 |
| barmode | No | バーモード（group/stack） | - |
| labels | No | 軸ラベルマッピング | - |
| show_legend | No | 凡例表示 | true |
| orientation | No | 向き（v/h） | "v" |
| text_template | No | データラベルテンプレート | - |
| hover_template | No | ホバーテンプレート | - |

チャートタイプ（chart_type）:
- `bar`: 縦棒グラフ
- `stacked_bar`: 積み上げ棒グラフ
- `grouped_bar`: グループ化棒グラフ
- `line`: 折れ線グラフ
- `pie`: 円グラフ
- `scatter`: 散布図

#### テーブル

```yaml
- type: "table"
  id: "volume-table"
  title: "Volume Summary"
  spec:
    title: "Volume Summary"
    style_table:
      overflowX: "auto"
      height: "400px"
    style_cell:
      textAlign: "left"
      padding: "6px 8px"
    style_header:
      fontWeight: "600"
    style_data_conditional:
      - if:
          filter_query: '{Status} = "Completed"'
        backgroundColor: "#d4edda"
    sort_action: "native"
    page_size: 20
    filter_action: "native"
    column_order:
      - "Fiscal Year"
      - "Month"
      - "Completed"
      - "Invalid"
    column_display:
      _fiscal_year: "Fiscal Year"
      _month: "Month"
  data_source: "filtered_data"
  data_transform:
    operations:
      - type: "group_by"
        group_columns:
          - "_fiscal_year"
          - "_month"
          - "status"
        agg_funcs:
          id: "nunique"
```

テーブルspecフィールド:

| フィールド | 必須 | 説明 | デフォルト |
|-----------|-----|------|----------|
| title | Yes | テーブルタイトル | - |
| style_table | No | テーブルスタイル（dict） | {} |
| style_cell | No | セルスタイル（dict） | {} |
| style_header | No | ヘッダースタイル（dict） | {} |
| style_data_conditional | No | 条件付きスタイル（list） | [] |
| column_display | No | カラム名表示マッピング | {} |
| column_order | No | カラム表示順 | [] |
| sort_action | No | ソート機能（none/native） | "none" |
| page_size | No | ページサイズ（0=無効） | 0 |
| filter_action | No | フィルタ機能（none/native） | "none" |

### data_transform

コンポーネントごとのデータ変換パイプラインを定義します。

```yaml
data_transform:
  params:
    - "selected_region"
    - "selected_year"
  operations:
    - type: "filter"
      include:
        content_type: ["ERV"]

    - type: "group_by"
      group_columns:
        - "_fiscal_year"
        - "_month"
      agg_funcs:
        id: "nunique"

    - type: "pivot"
      index:
        - "_month"
      columns_pivot:
        - "status"
      values:
        - "count"
      fill_value: 0

    - type: "sort"
      by: "_month"
      ascending: true

    - type: "rename"
      mapping:
        id: "Count"
        _fiscal_year: "Fiscal Year"
```

#### params

コールバックから渡されるパラメータ名のリストです。フィルタ値などを参照する場合に使用します。

```yaml
params:
  - "selected_region"
  - "selected_year"
  - "selected_month"
```

#### operations

データ変換の操作リストです。上から順に実行されます。

##### filter

条件に基づいてデータをフィルタリングします。

```yaml
# include: 指定した値に一致する行のみを含める
- type: "filter"
  include:
    content_type: ["ERV", "Prelim"]
    status: ["Completed"]

# exclude: 指定した値に一致する行を除外
- type: "filter"
  exclude:
    status: ["Cancelled"]

# exclude_null: 指定カラムのnull値を除外
- type: "filter"
  exclude_null:
    - "created_at"
    - "region"

# filter_query: pandas query構文で複雑な条件指定
- type: "filter"
  filter_query: "status == 'Completed' and duration > 100"
```

##### group_by / groupby

データをグループ化して集計します。

```yaml
- type: "group_by"
  group_columns:
    - "_fiscal_year"
    - "_month"
    - "status"
  agg_funcs:
    id: "nunique"
    duration: "sum"
  output_name: "total_count"  # 単一集計時の出力カラム名
```

集計関数:
- `sum`, `count`, `mean`, `median`, `max`, `min`, `nunique`

##### pivot

データをピボットテーブルに変換します。

```yaml
- type: "pivot"
  index:
    - "_month"
  columns_pivot:
    - "status"
  values:
    - "count"
  fill_value: 0
```

実行前:
```
_month    status      count
2024-01   Completed   100
2024-01   Invalid     10
2024-02   Completed   120
```

実行後:
```
_month    Completed   Invalid
2024-01   100         10
2024-02   120         0
```

##### sort

データをソートします。

```yaml
# 単純なソート
- type: "sort"
  by: "_month"
  ascending: true

# 日付パース付きソート
- type: "sort"
  by: "_month"
  ascending: false
  parse_date:
    _month: "%Y-%m"

# 数値パース付きソート
- type: "sort"
  by: "count"
  ascending: false
  numeric: true
```

##### rename

カラム名を変更します。

```yaml
- type: "rename"
  mapping:
    id: "Task ID"
    _fiscal_year: "Fiscal Year"
    _month: "Month"
```

##### add_column

新しいカラムを追加します。

```yaml
# 算術演算
- type: "add_column"
  name: "total_cost"
  left: "unit_price"
  operator: "*"
  right: "quantity"

# カスタム式
- type: "add_column"
  name: "completion_rate"
  expression: "df['completed'] / df['total'] * 100"
```

演算子: `+`, `-`, `*`, `/`

##### ensure_columns

存在しないカラムをデフォルト値で作成します。

```yaml
- type: "ensure_columns"
  columns:
    - "Completed"
    - "Invalid"
    - "Cancelled"
  default_value: 0
```

##### count_rows

行数をカウントします。

```yaml
- type: "count_rows"
  output_key: "total_count"
```

##### custom

カスタム関数を呼び出します。

```yaml
- type: "custom"
  function: "apply_custom_transformation"
  args:
    param1: "value1"
    param2: 100
```

対応する関数を `_custom_logic.py` に実装する必要があります。

```python
def apply_custom_transformation(df: pd.DataFrame, param1: str, param2: int) -> pd.DataFrame:
    # カスタム処理
    return df
```

### custom_logic

複雑なロジックや再利用可能な関数を `_custom_logic.py` に分離する場合に使用します。

```yaml
custom_logic:
  imports:
    - "add_cadence_columns"
    - "prepare_task_display_df"
    - "compute_custom_metric"
```

これらの関数は `_custom_logic.py` で定義する必要があります。

```python
# _custom_logic.py
import pandas as pd

def add_cadence_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add cadence-related columns to DataFrame."""
    # 実装
    return df

def prepare_task_display_df(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare DataFrame for task table display."""
    # 実装
    return df
```

## 使用例

### 最小限のpage_spec.yaml

```yaml
metadata:
  dashboard_id: "simple_dashboard"
  id_prefix: "sd-"
  dataset_id: "simple-dataset"
  title: "Simple Dashboard"

column_map:
  id: "id"
  name: "name"
  value: "value"

filters:
  - type: "slicer"
    id: "sd-filter-name"
    label: "Name"
    column: "name"

layout:
  sections:
    - rows:
        - items:
            - component_id: "sd-kpi-total"
              md: 12

components:
  - type: "kpi"
    id: "sd-kpi-total"
    title: "Total Value"
    spec:
      value_column: "value"
      agg_func: "sum"
    bg_color: "#e3f2fd"
    accent_color: "#1976d2"
```

### KPIカードの例

```yaml
# シンプルなKPI
- type: "kpi"
  id: "kpi-total"
  title: "Total Count"
  spec:
    value_column: "id"
    agg_func: "count"
    format: "{:,.0f}"
  bg_color: "#e3f2fd"
  accent_color: "#1976d2"

# フィルタ付きKPI
- type: "kpi"
  id: "kpi-completed"
  title: "Completed Tasks"
  spec:
    value_column: "id"
    agg_func: "nunique"
    format: "{:,.0f}"
    subtitle: "Last 30 days"
  bg_color: "#d4edda"
  accent_color: "#28a745"
  data_transform:
    operations:
      - type: "filter"
        include:
          status: ["Completed"]
```

### チャートの例

```yaml
# 積み上げ棒グラフ
- type: "chart"
  id: "chart-volume"
  title: "Volume by Status"
  spec:
    title: "Volume by Status"
    chart_type: "stacked_bar"
    x_column: "_month"
    y_columns:
      - "Completed"
      - "In Progress"
      - "Failed"
    color_map:
      Completed: "#2d6a2e"
      "In Progress": "#4F89B5"
      Failed: "#D22D27"
    height: 460
    text_template: "%{y}"
  data_transform:
    operations:
      - type: "group_by"
        group_columns:
          - "_month"
          - "status"
        agg_funcs:
          id: "count"
      - type: "pivot"
        index:
          - "_month"
        columns_pivot:
          - "status"
        values:
          - "id"
        fill_value: 0

# 円グラフ
- type: "chart"
  id: "chart-distribution"
  title: "Status Distribution"
  spec:
    title: "Status Distribution"
    chart_type: "pie"
    x_column: "status"
    y_columns:
      - "count"
    height: 400
  data_transform:
    operations:
      - type: "group_by"
        group_columns:
          - "status"
        agg_funcs:
          id: "count"
```

### テーブルの例

```yaml
# シンプルなテーブル
- type: "table"
  id: "table-summary"
  title: "Summary Table"
  spec:
    title: "Summary Table"
    style_table:
      overflowX: "auto"
    style_cell:
      textAlign: "left"
      padding: "8px"
    style_header:
      fontWeight: "bold"
    sort_action: "native"
    page_size: 10
    column_order:
      - "Region"
      - "Count"
      - "Total"
  data_transform:
    operations:
      - type: "group_by"
        group_columns:
          - "region"
        agg_funcs:
          id: "count"
      - type: "rename"
        mapping:
          region: "Region"
          id: "Count"

# 条件付きスタイル付きテーブル
- type: "table"
  id: "table-details"
  title: "Task Details"
  spec:
    title: "Task Details"
    style_table:
      overflowX: "auto"
      height: "500px"
    style_cell:
      textAlign: "left"
    style_data_conditional:
      - if:
          filter_query: '{Status} = "Completed"'
        backgroundColor: "#d4edda"
      - if:
          filter_query: '{Status} = "Failed"'
        backgroundColor: "#f8d7da"
    sort_action: "native"
    filter_action: "native"
    page_size: 20
```

### data_transformの例

```yaml
# 複数操作のパイプライン
data_transform:
  params:
    - "selected_region"
    - "selected_year"
  operations:
    # 1. フィルタリング
    - type: "filter"
      include:
        content_type: ["ERV", "Prelim"]
      exclude_null:
        - "created_at"

    # 2. グループ化
    - type: "group_by"
      group_columns:
        - "_fiscal_year"
        - "_month"
        - "status"
      agg_funcs:
        id: "nunique"
        duration: "sum"

    # 3. ピボット
    - type: "pivot"
      index:
        - "_fiscal_year"
        - "_month"
      columns_pivot:
        - "status"
      values:
        - "id"
      fill_value: 0

    # 4. カラム追加
    - type: "add_column"
      name: "Total"
      left: "Completed"
      operator: "+"
      right: "Invalid"

    # 5. カラム名変更
    - type: "rename"
      mapping:
        _fiscal_year: "Fiscal Year"
        _month: "Month"

    # 6. ソート
    - type: "sort"
      by: "Month"
      ascending: true
      parse_date:
        Month: "%Y-%m"
```

## ベストプラクティス

### ID命名規則

全てのIDは `id_prefix` を付与し、ページ間での衝突を防ぎます。

```yaml
metadata:
  id_prefix: "hamm-"

filters:
  - id: "hamm-filter-region"    # Good: prefix付き
  - id: "filter-region"          # Bad: prefixなし

components:
  - id: "hamm-kpi-total"         # Good: prefix付き
  - id: "kpi-total"              # Bad: prefixなし
```

命名パターン:
- フィルタ: `{prefix}filter-{name}`
- KPI: `{prefix}kpi-{name}`
- チャート: `{prefix}chart-{name}`
- テーブル: `{prefix}table-{name}`

### 派生カラムの使い方

頻繁に使用する集計軸（年、月など）は派生カラムとして定義します。

```yaml
# Good: 派生カラムとして定義
derived_columns:
  - name: "_year"
    type: "year"
    source_column: "created_at"
  - name: "_month"
    type: "month"
    source_column: "created_at"

# 各コンポーネントで再利用
components:
  - type: "chart"
    spec:
      x_column: "_month"  # 派生カラムを使用
```

```yaml
# Bad: コンポーネントごとに変換
components:
  - type: "chart"
    data_transform:
      operations:
        - type: "add_column"
          name: "_month"
          expression: "df['created_at'].dt.strftime('%Y-%m')"
```

### custom_logicへの分離基準

以下の場合は `_custom_logic.py` へロジックを分離します。

1. 複雑なビジネスロジック
   - 10行以上のデータ変換
   - 複数カラムにまたがる複雑な計算

2. 再利用可能なロジック
   - 複数コンポーネントで使用される処理
   - 他のページでも使われる可能性のある処理

3. テスト可能性
   - 単体テストが必要な処理
   - エッジケースが多い処理

```yaml
# Good: 複雑なロジックは分離
custom_logic:
  imports:
    - "add_cadence_columns"
    - "prepare_task_display_df"

components:
  - type: "table"
    id: "table-tasks"
    data_transform:
      operations:
        - type: "custom"
          function: "prepare_task_display_df"
```

```yaml
# Bad: YAML内に複雑なロジック埋め込み
components:
  - type: "table"
    data_transform:
      operations:
        - type: "add_column"
          expression: "..."  # 長い複雑な式
        - type: "add_column"
          expression: "..."  # さらに複雑な式
```

### レイアウト設計のコツ

1. Bootstrap 12グリッドシステムを活用

```yaml
# KPIカードは3列または4列
- items:
    - component_id: "kpi-1"
      md: 4  # 3列 (12 / 4 = 3)
    - component_id: "kpi-2"
      md: 4
    - component_id: "kpi-3"
      md: 4

# チャートとテーブルは2列
- items:
    - component_id: "table-1"
      md: 6  # 2列 (12 / 6 = 2)
    - component_id: "chart-1"
      md: 6

# 全幅コンポーネント
- items:
    - component_id: "table-details"
      md: 12  # 1列
```

2. セクションでグループ化

```yaml
layout:
  sections:
    # Section 1: KPIs
    - title: "Key Metrics"
      rows:
        - items: [...]

    # Section 2: Charts
    - title: "Analysis"
      description: "Volume and trend analysis"
      rows:
        - items: [...]

    # Section 3: Details
    - rows:
        - items: [...]
```

3. 適切な余白設定

```yaml
rows:
  - items: [...]
    className: "mb-3"  # KPIカード: 小さい余白
  - items: [...]
    className: "mb-4"  # チャート/テーブル: 大きい余白
```

### データ変換の最適化

1. 早い段階でフィルタリング

```yaml
# Good: 先にフィルタ
operations:
  - type: "filter"
    include:
      status: ["Completed"]
  - type: "group_by"
    group_columns: ["_month"]
    agg_funcs: { id: "count" }
```

```yaml
# Bad: 集計後にフィルタ
operations:
  - type: "group_by"
    group_columns: ["_month", "status"]
    agg_funcs: { id: "count" }
  - type: "filter"
    include:
      status: ["Completed"]
```

2. パラメータの活用

```yaml
# コールバックから渡されるフィルタ値を使用
data_transform:
  params:
    - "selected_region"
    - "selected_year"
  operations:
    # これらのパラメータは自動的にフィルタリングに使用される
    - type: "group_by"
      group_columns: ["_month"]
      agg_funcs: { id: "count" }
```

3. 必要なカラムのみを残す

```yaml
# ピボット後、不要なカラムを削除
operations:
  - type: "pivot"
    index: ["_month"]
    columns_pivot: ["status"]
    values: ["count"]
  - type: "rename"
    mapping:
      # 表示に必要なカラムのみリネーム
      _month: "Month"
      Completed: "Completed Count"
```

### バリデーションエラーの対処

コード生成時のバリデーションエラーは、スキーマに違反する設定を指摘します。

```bash
# エラー例
ValidationError: 1 validation error for PageSpec
filters.0.column
  Field required [type=missing, input_value={...}, input_type=dict]
```

対処法:
1. エラーメッセージのフィールドパスを確認（例: `filters.0.column`）
2. 該当箇所の設定を確認
3. 本リファレンスの該当セクションを参照して修正

よくあるエラー:
- `Field required`: 必須フィールドが未設定
- `Duplicate IDs found`: 重複するID
- `references unknown column`: column_mapに未定義のカラム参照
- `references unknown component_id`: layoutで未定義のcomponent_id参照

## 参考実装

完全な実装例は以下を参照してください。

- `src/pages/hamm_overview/page_spec.yaml` - 実稼働ページの完全な実装
- `tools/page_generator/test_complex.yaml` - 全機能を網羅したテスト実装
- `tools/page_generator/test_minimal.yaml` - 最小限の実装例

## 関連ドキュメント

- `docs/CONTRIB.md` セクション9: SPEC-Driven Dashboard Page Creation
- `tools/page_generator/README.md`: コード生成ツールの使い方
- `docs/tech-spec.md`: チャート構築API、データ変換仕様
