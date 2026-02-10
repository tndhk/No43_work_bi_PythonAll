# 02-page-spec 設計例集

---

## 例1: 最小構成ダッシュボードの設計プロセス

### シナリオ

「サポートチケットのデータがParquetにある。まずは件数とステータス一覧が見たい。」

### Step 1: データ探索

```python
from src.data.parquet_reader import ParquetReader

reader = ParquetReader()
df = reader.read_dataset("support-tickets")
```

探索結果:

```
行数: 12,450
カラム: ticket_id (int64), subject (object), status (object), priority (object),
        created_at (datetime64[ns, UTC]), assigned_to (object), category (object)

カーディナリティ:
  status: 4 (Open, In Progress, Resolved, Closed)
  priority: 3 (Low, Medium, High)
  assigned_to: 25
  category: 8

NULL率:
  assigned_to: 15%
  category: 3%
```

### Step 2: 設計判断

metadata の判断:
- dashboard_id: `support_tickets` （URLパスとして簡潔）
- id_prefix: `st-` （2文字 + ハイフン、他ページと重複なし）
- dataset_id: `support-tickets` （MinIO上のID）

column_map の判断:
- `ticket_id`, `subject`, `status`, `priority`, `created_at` を使用
- `assigned_to` は NULL率15%あるが、フィルタで使いたいのでマッピング
- `category` もマッピング
- 論理名: `ticket_id` → `id`, `subject` → `title`（短縮化）

derived_columns の判断:
- `created_at` があるので `_year` と `_month` は追加する
- 会計年度は不要（社内運用では暦年管理）

filters の判断:
- status (4値) → slicer: メイン分類、複数選択が有用
- priority (3値) → chip_group: 固定3値、視認性重視
- assigned_to (25値) → category (multi=true): 中カーディナリティ
- category (8値) → slicer: サブ分類

components の判断:
- KPI: 「総チケット数」のみ（最小構成）
- テーブル: チケット一覧（全フィールド表示）

### Step 3: 完成YAML

```yaml
metadata:
  dashboard_id: "support_tickets"
  id_prefix: "st-"
  dataset_id: "support-tickets"
  title: "Support Tickets"

column_map:
  id: "ticket_id"
  title: "subject"
  status: "status"
  priority: "priority"
  created_at: "created_at"
  assigned_to: "assigned_to"
  category: "category"

derived_columns:
  - name: "_year"
    type: "year"
    source_column: "created_at"
  - name: "_month"
    type: "month"
    source_column: "created_at"

filters:
  - type: "slicer"
    id: "filter-status"
    label: "Status"
    column: "status"
    has_clear_button: true

  - type: "chip_group"
    id: "filter-priority"
    label: "Priority"
    options: ["Low", "Medium", "High"]
    default: null

  - type: "category"
    id: "filter-assigned-to"
    label: "Assigned To"
    column: "assigned_to"
    multi: true

  - type: "slicer"
    id: "filter-category"
    label: "Category"
    column: "category"
    has_clear_button: true

layout:
  sections:
    - rows:
        - items:
            - component_id: "kpi-total"
              md: 12
          className: "mb-3"
        - items:
            - component_id: "table-tickets"
              md: 12
          className: "mb-4"

components:
  - type: "kpi"
    id: "kpi-total"
    title: "Total Tickets"
    spec:
      value_column: "id"
      agg_func: "nunique"
      format: "{:,.0f}"
    bg_color: "#e3f2fd"
    accent_color: "#1976d2"

  - type: "table"
    id: "table-tickets"
    title: "Ticket List"
    spec:
      title: "Ticket List"
      style_table:
        overflowX: "auto"
        height: "500px"
      style_cell:
        textAlign: "left"
        padding: "6px 8px"
      style_header:
        fontWeight: "600"
        backgroundColor: "#f8f9fa"
        borderBottom: "2px solid #dee2e6"
      sort_action: "native"
      page_size: 20
      column_order:
        - "Ticket ID"
        - "Subject"
        - "Status"
        - "Priority"
        - "Category"
        - "Assigned To"
        - "Created"
    data_transform:
      operations:
        - type: "rename"
          mapping:
            id: "Ticket ID"
            title: "Subject"
            status: "Status"
            priority: "Priority"
            category: "Category"
            assigned_to: "Assigned To"
            created_at: "Created"
```

### 判断の根拠まとめ

| 判断ポイント | 選択 | 理由 |
|-------------|------|------|
| KPI数 | 1つ | 最小構成。後から追加可能 |
| チャートなし | 意図的省略 | まずデータ確認が目的。次フェーズで追加 |
| status → slicer | カーディナリティ4 | 複数ステータス同時確認に有用 |
| priority → chip_group | 固定3値 | 視覚的に選びやすい。データ由来でなく固定値 |
| assigned_to → category | カーディナリティ25 | ドロップダウンが適切。slicer だと長すぎる |

---

## 例2: 中規模ダッシュボードの設計プロセス

### シナリオ

「月次のコンテンツ制作進捗を可視化したい。地域別・コンテンツ種別でフィルタし、月次推移チャートとサマリテーブルが必要。KPIで全体像を把握し、ステータス別の構成比も見たい。」

### Step 1: データ探索結果

```
行数: 45,200
カラム: content_id (object), title (object), content_type (object),
        status (object), region (object), language (object),
        created_date (datetime64[ns, UTC]), completed_date (datetime64[ns]),
        word_count (int64), reviewer (object)

カーディナリティ:
  content_type: 5 (Article, Video, Podcast, Infographic, eBook)
  status: 6 (Draft, Review, Approved, Published, Archived, Rejected)
  region: 4 (APAC, EMEA, Americas, Global)
  language: 12
  reviewer: 35

NULL率:
  completed_date: 42% (Draft/Review のレコード)
  reviewer: 18%
  word_count: 5%
```

### Step 2: 設計判断の思考プロセス

column_map の判断:
- `content_id` → `id`: 標準的な命名
- `content_type` → `content_type`: そのまま（十分短い）
- `created_date` → `created_at`: プロジェクト内の命名規則に合わせる
- `completed_date` → `completed_at`: 同上
- `word_count` → `word_count`: そのまま
- `reviewer` はNULL率18%だがフィルタでは使わないので column_map には含めるがフィルタ化しない

derived_columns の判断:
- `_year`, `_month` は必須（月次推移チャートで使用）
- 会計年度: 必要ないが、将来追加しやすいよう `created_at` を source に

filters の判断:
- region (4値) → slicer: メイン分類
- content_type (5値) → slicer: メイン分類
- status (6値) → slicer: メイン分類
- language (12値) → slicer: サブ分類
- `_year` → slicer: 年フィルタ
- reviewer (35値) → フィルタ化しない（NULL率高く、メイン用途でない）

components の判断:
- KPI 3つ: 「総コンテンツ数」「Published数」「平均ワード数」
  - 3つでBootstrapの4-4-4レイアウトに適合
- チャート 2つ:
  - 月次推移（stacked_bar）: status別の月次件数 → 進捗トレンドが一目でわかる
  - ステータス構成比（pie）: 全体の状況把握
- テーブル 1つ: 月別サマリ（Published/Rejected/Other の件数）

layout の判断:
- Section 1: KPI 3列
- Section 2: チャート 2列（月次推移 + 円グラフ）
- Section 3: テーブル 全幅

data_transform の設計:
- 月次推移チャート: group_by(_month, status) → pivot(status) → ensure_columns → sort
- 円グラフ: group_by(status) → sort
- テーブル: group_by(_month, status) → pivot(status) → ensure_columns → add_column(Total) → rename → sort

### Step 3: 完成YAML

```yaml
metadata:
  dashboard_id: "content_progress"
  id_prefix: "cp-"
  dataset_id: "content-production"
  title: "Content Production Progress"
  description: "コンテンツ制作の進捗状況を地域・種別・ステータス別に可視化"

column_map:
  id: "content_id"
  title: "title"
  content_type: "content_type"
  status: "status"
  region: "region"
  language: "language"
  created_at: "created_date"
  completed_at: "completed_date"
  word_count: "word_count"
  reviewer: "reviewer"
  # 派生カラムエイリアス
  year: "_year"

derived_columns:
  - name: "_year"
    type: "year"
    source_column: "created_at"
  - name: "_month"
    type: "month"
    source_column: "created_at"

filters:
  - type: "slicer"
    id: "filter-region"
    label: "Region"
    column: "region"
    has_clear_button: true

  - type: "slicer"
    id: "filter-year"
    label: "Year"
    column: "year"
    has_clear_button: true

  - type: "slicer"
    id: "filter-content-type"
    label: "Content Type"
    column: "content_type"
    has_clear_button: true

  - type: "slicer"
    id: "filter-status"
    label: "Status"
    column: "status"
    has_clear_button: true

  - type: "slicer"
    id: "filter-language"
    label: "Language"
    column: "language"
    has_clear_button: true

layout:
  sections:
    # KPI Cards
    - rows:
        - items:
            - component_id: "kpi-total"
              md: 4
            - component_id: "kpi-published"
              md: 4
            - component_id: "kpi-avg-words"
              md: 4
          className: "mb-3"

    # Charts
    - title: "Trends & Distribution"
      rows:
        - items:
            - component_id: "chart-monthly-trend"
              md: 6
            - component_id: "chart-status-distribution"
              md: 6
          className: "mb-4"

    # Summary Table
    - rows:
        - items:
            - component_id: "table-monthly-summary"
              md: 12
          className: "mb-4"

components:
  # --- KPI Cards ---
  - type: "kpi"
    id: "kpi-total"
    title: "Total Content Items"
    spec:
      value_column: "id"
      agg_func: "nunique"
      format: "{:,.0f}"
    bg_color: "#e3f2fd"
    accent_color: "#1976d2"

  - type: "kpi"
    id: "kpi-published"
    title: "Published"
    spec:
      value_column: "id"
      agg_func: "nunique"
      format: "{:,.0f}"
    bg_color: "#d4edda"
    accent_color: "#28a745"
    data_transform:
      operations:
        - type: "filter"
          include:
            status: ["Published"]

  - type: "kpi"
    id: "kpi-avg-words"
    title: "Avg Word Count"
    spec:
      value_column: "word_count"
      agg_func: "mean"
      format: "{:,.0f}"
    bg_color: "#fff3cd"
    accent_color: "#ffc107"

  # --- Charts ---
  - type: "chart"
    id: "chart-monthly-trend"
    title: "Monthly Production Trend"
    spec:
      title: "Monthly Production Trend"
      chart_type: "stacked_bar"
      x_column: "_month"
      y_columns:
        - "Published"
        - "Approved"
        - "Review"
        - "Draft"
      color_map:
        Published: "#28a745"
        Approved: "#17a2b8"
        Review: "#ffc107"
        Draft: "#6c757d"
      height: 460
      text_template: "%{y}"
    layout_overrides:
      margin: { l: 30, r: 10, t: 8, b: 60 }
      legend: { orientation: "h", y: -0.25 }
      textposition: "inside"
    data_transform:
      operations:
        - type: "filter"
          exclude:
            status: ["Archived", "Rejected"]
        - type: "group_by"
          group_columns:
            - "_month"
            - "status"
          agg_funcs:
            id: "nunique"
        - type: "pivot"
          index:
            - "_month"
          columns_pivot:
            - "status"
          values:
            - "id"
          fill_value: 0
        - type: "ensure_columns"
          columns: ["Published", "Approved", "Review", "Draft"]
          default_value: 0
        - type: "sort"
          by: "_month"
          ascending: true

  - type: "chart"
    id: "chart-status-distribution"
    title: "Status Distribution"
    spec:
      title: "Status Distribution"
      chart_type: "pie"
      x_column: "status"
      y_columns: ["count"]
      height: 460
      show_legend: true
    layout_overrides:
      margin: { l: 8, r: 8, t: 8, b: 34 }
      legend: { orientation: "h", x: 0.0, y: -0.06 }
      textinfo: "label+value+percent"
      textposition: "inside"
    data_transform:
      operations:
        - type: "group_by"
          group_columns:
            - "status"
          agg_funcs:
            id: "nunique"
          output_name: "count"
        - type: "sort"
          by: "count"
          ascending: false

  # --- Table ---
  - type: "table"
    id: "table-monthly-summary"
    title: "Monthly Summary"
    spec:
      title: "Monthly Summary"
      style_table:
        overflowX: "auto"
        height: "400px"
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
        - "Month"
        - "Published"
        - "Approved"
        - "Review"
        - "Draft"
        - "Total"
    data_transform:
      operations:
        - type: "filter"
          exclude:
            status: ["Archived", "Rejected"]
        - type: "group_by"
          group_columns:
            - "_month"
            - "status"
          agg_funcs:
            id: "nunique"
        - type: "pivot"
          index:
            - "_month"
          columns_pivot:
            - "status"
          values:
            - "id"
          fill_value: 0
        - type: "ensure_columns"
          columns: ["Published", "Approved", "Review", "Draft"]
          default_value: 0
        - type: "add_column"
          name: "Total"
          expression: "df['Published'] + df['Approved'] + df['Review'] + df['Draft']"
        - type: "rename"
          mapping:
            _month: "Month"
        - type: "sort"
          by: "Month"
          ascending: true
          parse_date:
            Month: "%Y-%m"
```

### 設計判断の根拠まとめ

| 判断ポイント | 選択 | 理由 |
|-------------|------|------|
| KPI 3つ | Total / Published / Avg Words | 全体像、成果指標、品質指標の3軸 |
| stacked_bar | 月次推移 | 各ステータスの構成と合計の推移を同時表現 |
| pie | ステータス構成比 | 全体に占める割合の把握（6カテゴリは上限近い） |
| Archived/Rejected を除外 | filter操作 | アクティブなステータスのみ集計（ノイズ除去） |
| reviewer をフィルタ化しない | NULL率18% + 用途限定 | メインの分析軸ではない。必要時に追加可 |
| language → slicer | カーディナリティ12 | 10-50の範囲。slicer が適切 |
| テーブルに add_column | Total列追加 | 横合計で月ごとの総件数を表示 |
| 色設計 | ステータスと意味を対応 | Published=緑(成功)、Draft=灰(未着手) |
| parse_date ソート | Month カラム | "2024-01"形式を日付として正しくソート |

---

## 設計のアンチパターン

### アンチパターン 1: 全カラムを column_map に入れる

```yaml
# 悪い例: 使わないカラムも全部マッピング
column_map:
  id: "content_id"
  title: "title"
  content_type: "content_type"
  status: "status"
  region: "region"
  language: "language"
  created_at: "created_date"
  completed_at: "completed_date"
  word_count: "word_count"
  reviewer: "reviewer"
  internal_notes: "internal_notes"      # 使わない
  last_modified_by: "last_modified_by"  # 使わない
  system_flag: "system_flag"            # 使わない
```

問題: column_map に不要なカラムがあると、フィルタやコンポーネントで誤って参照する可能性がある。また、メンテナンス時にどのカラムが実際に使われているか判断しにくい。

### アンチパターン 2: カーディナリティを無視したフィルタ選択

```yaml
# 悪い例: カーディナリティ200のカラムに slicer
- type: "slicer"
  id: "filter-reviewer"
  label: "Reviewer"
  column: "reviewer"
  has_clear_button: true
  # → 200人分のチェックリストが表示される。UIが崩壊する
```

正しい選択: category (multi=true) にして検索可能なドロップダウンにする。

### アンチパターン 3: data_transform の操作順序ミス

```yaml
# 悪い例: rename してから group_by
data_transform:
  operations:
    - type: "rename"
      mapping:
        status: "Status"
    - type: "group_by"
      group_columns: ["_month", "Status"]  # rename後の名前で参照 → エラーになる可能性
      agg_funcs:
        id: "nunique"
```

正しい順序: filter → group_by → pivot → rename → sort。rename は最後に近い位置で行う。

### アンチパターン 4: ensure_columns の省略

```yaml
# 悪い例: pivot 後に ensure_columns なし
- type: "pivot"
  index: ["_month"]
  columns_pivot: ["status"]
  values: ["id"]
  fill_value: 0
# → フィルタで特定ステータスが除外された場合、y_columns に指定したカラムが存在しないエラー
```

stacked_bar の y_columns に列挙するカラム名は、pivot 後に存在しない可能性がある。ensure_columns で補完が必須。
