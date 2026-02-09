# Volume Table/Chart: Prelim/ERV -> Completed/Invalid ピボット軸変更

## Context

hamm_overview ダッシュボードの Volume Table と Volume Chart は、現在 `content_type` (Prelim/ERV) でピボットしている。
ユーザー要件により、ピボット軸を `status` (Completed/Invalid) に変更する。
Cancelled ステータスは引き続き除外。他のチャート/テーブル（Task Details, Issues Ratio 等）は変更なし。

## 変更ファイル一覧

| # | ファイル | 変更内容 |
|---|---------|---------|
| 1 | `src/pages/hamm_overview/_constants.py` | ラベル定数・Spec定義の変更 |
| 2 | `src/pages/hamm_overview/_data_loader.py` | `build_volume_summary()` のピボットロジック変更 |
| 3 | `src/pages/hamm_overview/_chart_builders.py` | docstringのみ更新（Prelim/ERV -> Completed/Invalid） |
| 4 | `src/pages/hamm_overview/SPEC.md` | Volume セクションの説明更新 |
| 5 | `tests/unit/pages/hamm_overview/test_constants.py` | Spec テストのアサーション更新 |
| 6 | `tests/unit/pages/hamm_overview/test_data_loader.py` | Volume summary テストのフィクスチャ・アサーション更新 |
| 7 | `tests/unit/pages/hamm_overview/test_chart_builders.py` | Volume フィクスチャ・トレース名・色アサーション更新 |

## Step 1: テスト更新（TDD - Red Phase）

### 1-1. `tests/unit/pages/hamm_overview/test_constants.py`

- `TestVolumeTableSpec.test_volume_table_spec_column_order`:
  `["Fiscal Year", "Fiscal Quarter", "ISO Week", "Start Date", "End Date", "Prelim", "ERV", "VOLUME TOTAL"]`
  ->
  `["Fiscal Year", "Fiscal Quarter", "ISO Week", "Start Date", "End Date", "Completed", "Invalid", "VOLUME TOTAL"]`

- `TestVolumeChartSpec.test_volume_chart_spec_y_columns`:
  `["ERV", "Prelim"]` -> `["Completed", "Invalid"]`

- `TestVolumeChartSpec.test_volume_chart_spec_color_map`:
  `{"ERV": "#f6b3b3", "Prelim": "#e57f7f"}` -> `{"Completed": "#2d6a2e", "Invalid": "#9ca3af"}`

- 新規テスト `test_volume_chart_spec_text_template`: `VOLUME_CHART_SPEC.text_template == "%{y}"` を検証

### 1-2. `tests/unit/pages/hamm_overview/test_data_loader.py`

- `_make_prepared_df()` フィクスチャ:
  - `status` 列に `"Invalid"` を追加（例: ID "3" を `"Cancelled"` -> `"Cancelled"`, ID "2" を `"Invalid"` に変更、新行 ID "5" を `"Invalid"` で追加）
  - 具体的には:
    ```python
    "status": ["Completed", "Invalid", "Cancelled", "Completed", "Invalid"],
    ```
    （5行に拡張。他の列も5行に合わせる）

- `TestBuildVolumeSummaryInDataLoader`:
  - `test_has_expected_columns`: `"Prelim", "ERV"` -> `"Completed", "Invalid"`
  - `test_excludes_cancelled_status`: total が Cancelled 除外の行数に一致するよう更新
  - `test_volume_total_is_sum_of_prelim_and_erv` -> `test_volume_total_is_sum_of_completed_and_invalid`:
    `row["Prelim"] + row["ERV"]` -> `row["Completed"] + row["Invalid"]`

### 1-3. `tests/unit/pages/hamm_overview/test_chart_builders.py`

- `volume_df` フィクスチャ: `"Prelim"` / `"ERV"` カラムを `"Completed"` / `"Invalid"` に変更
- `empty_volume_df` フィクスチャ: 同上
- `TestBuildVolumeChart`:
  - `test_trace_names`: `"ERV"`, `"Prelim"` -> `"Completed"`, `"Invalid"`
  - `test_erv_marker_color` -> `test_completed_marker_color`: `"#2d6a2e"` を検証
  - `test_prelim_marker_color` -> `test_invalid_marker_color`: `"#9ca3af"` を検証
- `TestBuildVolumeTable.test_has_all_display_columns`: `"Prelim"`, `"ERV"` -> `"Completed"`, `"Invalid"`

## Step 2: 実装（Green Phase）

### 2-1. `src/pages/hamm_overview/_constants.py`

- ラベル定数の変更:
  ```python
  # 旧:
  PRELIM_LABEL: str = "Prelim"
  ERV_LABEL: str = "ERV"
  # 新:
  COMPLETED_LABEL: str = "Completed"
  INVALID_LABEL: str = "Invalid"
  ```

- `VOLUME_TABLE_SPEC.column_order` 更新:
  ```python
  column_order=[
      "Fiscal Year", "Fiscal Quarter", "ISO Week",
      "Start Date", "End Date",
      COMPLETED_LABEL, INVALID_LABEL,
      "VOLUME TOTAL",
  ],
  ```

- `VOLUME_CHART_SPEC` 更新:
  ```python
  VOLUME_CHART_SPEC: ChartSpec = ChartSpec(
      title="Volume Chart",
      chart_type="stacked_bar",
      x_column="Start Date",
      y_columns=[COMPLETED_LABEL, INVALID_LABEL],
      color_map={
          COMPLETED_LABEL: "#2d6a2e",
          INVALID_LABEL: "#9ca3af",
      },
      text_template="%{y}",
      height=400,
  )
  ```

### 2-2. `src/pages/hamm_overview/_data_loader.py`

- import 変更: `PRELIM_LABEL, ERV_LABEL` -> `COMPLETED_LABEL, INVALID_LABEL`

- `build_volume_summary()` の変更:
  1. 除外ステータスを `["Cancelled"]` のみに（`"Invalid"` を除外リストから削除）
  2. group_cols: `COLUMN_MAP["content_type"]` -> `COLUMN_MAP["status"]`
  3. pivot_table: `columns=COLUMN_MAP["content_type"]` -> `columns=COLUMN_MAP["status"]`
  4. ラベル確認: `PRELIM_LABEL, ERV_LABEL` -> `COMPLETED_LABEL, INVALID_LABEL`
  5. VOLUME TOTAL: `pivot[PRELIM_LABEL] + pivot[ERV_LABEL]` -> `pivot[COMPLETED_LABEL] + pivot[INVALID_LABEL]`
  6. 最終カラム選択の更新

### 2-3. `src/pages/hamm_overview/_chart_builders.py`

- docstring のみ更新（Prelim/ERV の記述を Completed/Invalid に変更）
- ロジックの変更なし（Specに委譲しているため）

### 2-4. `src/pages/hamm_overview/SPEC.md`

- Volume セクションの説明を「コンテンツタイプ別」から「ステータス別（Completed/Invalid）」に更新

## Step 3: 検証

1. テスト実行:
   ```bash
   python3 -m pytest tests/unit/pages/hamm_overview/ -v
   ```

2. 全テストがパスすることを確認

3. アプリ起動して目視確認（任意）:
   ```bash
   python3 app.py
   ```
   - Volume Table: Completed / Invalid カラムが表示されること
   - Volume Chart: 緑(Completed) / グレー(Invalid) の積み上げ棒グラフが表示されること
   - データラベルが各バーセグメントに表示されること
