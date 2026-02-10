# 03-page-gen 例集

---

## 1. 最小限の page_spec.yaml（KPI 1つ + テーブル 1つ）

```yaml
metadata:
  dashboard_id: "simple_report"
  id_prefix: "sr-"
  dataset_id: "simple-report"
  title: "Simple Report"
  description: "シンプルなレポートダッシュボード"

column_map:
  id: "id"
  name: "name"
  status: "status"
  value: "value"

filters:
  - type: "slicer"
    id: "sr-filter-status"
    label: "Status"
    column: "status"
    has_clear_button: true

layout:
  sections:
    - rows:
        - items:
            - component_id: "sr-kpi-total"
              md: 12
          className: "mb-3"
        - items:
            - component_id: "sr-table-detail"
              md: 12
          className: "mb-4"

components:
  - type: "kpi"
    id: "sr-kpi-total"
    title: "Total Count"
    spec:
      value_column: "id"
      agg_func: "count"
      format: "{:,.0f}"
    bg_color: "#e3f2fd"
    accent_color: "#1976d2"

  - type: "table"
    id: "sr-table-detail"
    title: "Detail Table"
    spec:
      title: "Detail Table"
      style_table:
        overflowX: "auto"
      style_cell:
        textAlign: "left"
        padding: "6px 8px"
      style_header:
        fontWeight: "600"
      sort_action: "native"
      page_size: 20
      column_order:
        - "Name"
        - "Status"
        - "Value"
    data_transform:
      operations:
        - type: "rename"
          mapping:
            name: "Name"
            status: "Status"
            value: "Value"
```

## 2. 標準的な page_spec.yaml（KPI 3つ + チャート 2つ + テーブル 1つ）

```yaml
metadata:
  dashboard_id: "sales_dashboard"
  id_prefix: "sd-"
  dataset_id: "sales-data"
  title: "Sales Dashboard"
  description: "Sales performance dashboard showing revenue, orders, and trends"

column_map:
  id: "order_id"
  date: "order_date"
  region: "region_name"
  product: "product_category"
  revenue: "revenue_amount"
  quantity: "order_quantity"
  status: "order_status"

derived_columns:
  - name: "_year"
    type: "year"
    source_column: "date"
  - name: "_month"
    type: "month"
    source_column: "date"

filters:
  - type: "slicer"
    id: "sd-filter-region"
    label: "Region"
    column: "region"
    has_clear_button: true

  - type: "slicer"
    id: "sd-filter-year"
    label: "Year"
    column: "_year"
    has_clear_button: true

  - type: "category"
    id: "sd-filter-product"
    label: "Product Category"
    column: "product"
    multi: true

layout:
  sections:
    # KPI Cards
    - rows:
        - items:
            - component_id: "sd-kpi-revenue"
              md: 4
            - component_id: "sd-kpi-orders"
              md: 4
            - component_id: "sd-kpi-avg-order"
              md: 4
          className: "mb-3"

    # Charts
    - title: "Trends & Distribution"
      rows:
        - items:
            - component_id: "sd-chart-monthly-revenue"
              md: 6
            - component_id: "sd-chart-region-distribution"
              md: 6
          className: "mb-4"

    # Table
    - rows:
        - items:
            - component_id: "sd-table-orders"
              md: 12
          className: "mb-4"

components:
  # --- KPI Cards ---
  - type: "kpi"
    id: "sd-kpi-revenue"
    title: "Total Revenue"
    spec:
      value_column: "revenue"
      agg_func: "sum"
      format: "${:,.0f}"
    bg_color: "#d4edda"
    accent_color: "#28a745"

  - type: "kpi"
    id: "sd-kpi-orders"
    title: "Total Orders"
    spec:
      value_column: "id"
      agg_func: "count"
      format: "{:,.0f}"
    bg_color: "#e3f2fd"
    accent_color: "#1976d2"

  - type: "kpi"
    id: "sd-kpi-avg-order"
    title: "Average Order Value"
    spec:
      value_column: "revenue"
      agg_func: "mean"
      format: "${:,.2f}"
    bg_color: "#fff3cd"
    accent_color: "#ffc107"

  # --- Charts ---
  - type: "chart"
    id: "sd-chart-monthly-revenue"
    title: "Monthly Revenue Trend"
    spec:
      title: "Monthly Revenue Trend"
      chart_type: "bar"
      x_column: "_month"
      y_columns:
        - "total_revenue"
      height: 460
      text_template: "%{y:$,.0f}"
      show_legend: false
    data_transform:
      operations:
        - type: "group_by"
          group_columns:
            - "_month"
          agg_funcs:
            revenue: "sum"
        - type: "rename"
          mapping:
            revenue: "total_revenue"
        - type: "sort"
          by: "_month"
          ascending: true

  - type: "chart"
    id: "sd-chart-region-distribution"
    title: "Revenue by Region"
    spec:
      title: "Revenue by Region"
      chart_type: "pie"
      x_column: "region"
      y_columns:
        - "total_revenue"
      height: 460
      show_legend: true
    layout_overrides:
      textinfo: "label+value+percent"
      textposition: "inside"
    data_transform:
      operations:
        - type: "group_by"
          group_columns:
            - "region"
          agg_funcs:
            revenue: "sum"
        - type: "rename"
          mapping:
            revenue: "total_revenue"
        - type: "sort"
          by: "total_revenue"
          ascending: false

  # --- Table ---
  - type: "table"
    id: "sd-table-orders"
    title: "Order Details"
    spec:
      title: "Order Details"
      style_table:
        overflowX: "auto"
        height: "500px"
      style_cell:
        textAlign: "left"
        padding: "6px 8px"
        fontSize: "13px"
      style_header:
        fontWeight: "600"
        backgroundColor: "#f8f9fa"
        borderBottom: "2px solid #dee2e6"
      sort_action: "native"
      page_size: 20
      column_order:
        - "Order ID"
        - "Region"
        - "Product"
        - "Revenue"
        - "Quantity"
        - "Status"
    data_transform:
      operations:
        - type: "rename"
          mapping:
            id: "Order ID"
            region: "Region"
            product: "Product"
            revenue: "Revenue"
            quantity: "Quantity"
            status: "Status"
```

## 3. カスタムロジック実装例

### page_spec.yaml（抜粋）
```yaml
custom_logic:
  imports:
    - "compute_fiscal_year"
    - "prepare_summary_df"

derived_columns:
  - name: "_fiscal_year"
    type: "custom"
    function: "compute_fiscal_year"

components:
  - type: "table"
    id: "xx-table-summary"
    title: "Fiscal Summary"
    data_transform:
      operations:
        - type: "custom"
          function: "prepare_summary_df"
```

### _custom_logic.py 実装例
```python
"""Custom logic for the dashboard page.

Functions listed in page_spec.yaml custom_logic.imports.
"""
import pandas as pd


def compute_fiscal_year(df: pd.DataFrame) -> pd.Series:
    """Compute fiscal year from created_at column.

    Fiscal year starts in April: Jan-Mar = previous year.
    """
    dates = pd.to_datetime(df["created_at"])
    fy = dates.dt.year.where(dates.dt.month >= 4, dates.dt.year - 1)
    return "FY" + fy.astype(str)


def prepare_summary_df(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare summary DataFrame for display table.

    Groups by fiscal year and calculates key metrics.
    """
    summary = df.groupby("_fiscal_year").agg(
        total_count=("id", "nunique"),
        completed=("status", lambda x: (x == "Completed").sum()),
        error_rate=("status", lambda x: (x == "Error").sum() / len(x) * 100),
    ).reset_index()

    summary = summary.rename(columns={
        "_fiscal_year": "Fiscal Year",
        "total_count": "Total Count",
        "completed": "Completed",
        "error_rate": "Error Rate (%)",
    })

    summary["Error Rate (%)"] = summary["Error Rate (%)"].round(1)

    return summary
```

## 4. __init__.py テンプレート

```python
"""<Page Display Name> page."""
import dash

from ._layout import build_layout
from . import _callbacks  # noqa: F401


dash.register_page(
    __name__,
    path="/<url-path>",
    name="<Page Display Name>",
    order=<number>,
    layout=build_layout,
)
```

注意点:
- `layout=build_layout` は関数参照（呼び出しではない）
- `_callbacks` のインポートは `register_page` の前後どちらでも可
- `from . import _callbacks` は必須（コールバック登録のトリガー）

## 5. data_sources.yml テンプレート

```yaml
charts:
  # 全てのコンポーネントIDとデータセットIDのマッピング
  # page_spec.yaml の components セクションの全IDを列挙すること

  # KPI Cards
  <id_prefix>kpi-xxx: <dataset_id>
  <id_prefix>kpi-yyy: <dataset_id>

  # Charts
  <id_prefix>chart-xxx: <dataset_id>

  # Tables
  <id_prefix>table-xxx: <dataset_id>
```

ID命名パターン:
- KPI: `{id_prefix}kpi-{name}`
- チャート: `{id_prefix}chart-{name}`
- テーブル: `{id_prefix}table-{name}`

## 6. コード生成コマンド例

```bash
# Step 1: テンプレートコピー
cp tools/page_generator/templates/new_page_spec.yaml src/pages/sales_dashboard/page_spec.yaml

# Step 2: dry-runでバリデーション
python3 -m tools.page_generator src/pages/sales_dashboard --dry-run

# Step 3: 全ファイル生成
python3 -m tools.page_generator src/pages/sales_dashboard

# Step 4: 部分再生成（YAML変更後にlayoutとcallbacksだけ更新）
python3 -m tools.page_generator src/pages/sales_dashboard --files layout callbacks

# Step 5: 利用可能なファイル名確認
# constants, layout, filters, data_loader, callbacks, chart_builders, custom_logic
```

## 7. data_transform パイプライン例

### 積み上げ棒グラフ用パイプライン
```yaml
data_transform:
  operations:
    # 1. 不要データを除外
    - type: "filter"
      exclude:
        status: ["Cancelled"]

    # 2. グループ化
    - type: "group_by"
      group_columns:
        - "_month"
        - "status"
      agg_funcs:
        id: "nunique"

    # 3. ピボット（status値をカラムに展開）
    - type: "pivot"
      index:
        - "_month"
      columns_pivot:
        - "status"
      values:
        - "id"
      fill_value: 0

    # 4. 欠損カラムを補完
    - type: "ensure_columns"
      columns: ["Completed", "Error"]
      default_value: 0

    # 5. ソート
    - type: "sort"
      by: "_month"
      ascending: true
```

### 円グラフ用パイプライン
```yaml
data_transform:
  operations:
    - type: "filter"
      exclude_null: ["category"]

    - type: "group_by"
      group_columns:
        - "category"
      agg_funcs:
        id: "nunique"
      output_name: "count"

    - type: "sort"
      by: "count"
      ascending: false
```

### 合計カラム追加パイプライン
```yaml
data_transform:
  operations:
    - type: "group_by"
      group_columns: ["_month", "status"]
      agg_funcs:
        id: "nunique"

    - type: "pivot"
      index: ["_month"]
      columns_pivot: ["status"]
      values: ["id"]
      fill_value: 0

    - type: "ensure_columns"
      columns: ["Completed", "Error"]
      default_value: 0

    - type: "add_column"
      name: "Total"
      left: "Completed"
      operator: "+"
      right: "Error"

    - type: "rename"
      mapping:
        _month: "Month"
```
