# Plan: APAC DOT DDD Change + Issue(SQL) ダッシュボード統合

## Context

既存の apac_dot_due_date ダッシュボードに2つ目のDOMOデータソース「APAC DOT DDD Change + Issue(SQL)」を追加する。42,039行/19カラムのデータセットで、既存のReference Tableと同形式のピボットテーブルを2つ目のチャートとして表示する。

Phase 1（YAML設定追加）とPhase 2（スキーマ調査）は完了済み。ETL実行 -> TDDでのダッシュボード統合が残タスク。

### ユーザー確定方針
- COLUMN_MAP_2: 既存と同じ論理キーで新データセットの実カラム名にマッピング。月は `edit month` を使用
- フィルタ共有: `edit month` と既存 `Delivery Completed Month` を同一ドロップダウンで共有（union）
- order_type フィルタは新規データセット (dataset 2) にのみ適用。既存データセット (dataset 1) には適用しない
- amp_av フィルタは dataset 1 にのみ適用（dataset 2 にはカラムなし）
- チャート形式: 既存 Reference Table と同じピボットテーブル形式

---

## Phase 3: ETL実行

### Task 3.1: データ取得・MinIOアップロード
```bash
python3 backend/scripts/load_domo.py --dataset "APAC DOT DDD Change + Issue(SQL)"
```

### Task 3.2: データ検証（scratchpadスクリプト）
```python
from src.data.parquet_reader import ParquetReader
reader = ParquetReader()
df = reader.read_dataset("apac-dot-ddd-change-issue-sql")
print(f"Shape: {df.shape}")
print(df.columns.tolist())
print(df.dtypes)
```
- カラム名のケーシングが DOMO API スキーマと一致するか確認（特に `metric workstream` vs `Metric Workstream`）
- `edit month` カラムの実際の値フォーマットを確認（Timestamp vs 文字列）
- 結果次第で COLUMN_MAP_2 のカラム名を調整

---

## Phase 4+5: TDDダッシュボード統合（6ステップ順次実行）

### Step 1: `_constants.py` -- 新定数追加

対象: `src/pages/apac_dot_due_date/_constants.py`
テスト: `tests/unit/pages/apac_dot_due_date/test_constants.py`

追加する定数:

```python
# L12の後に追加
DATASET_ID_2: str = "apac-dot-ddd-change-issue-sql"

# L31の後に追加
CHART_ID_CHANGE_ISSUE_TABLE: str = f"{ID_PREFIX}chart-01"
CHART_ID_CHANGE_ISSUE_TABLE_TITLE: str = f"{CHART_ID_CHANGE_ISSUE_TABLE}-title"

# L45の後に追加
COLUMN_MAP_2: dict[str, str] = {
    "month": "edit month",
    "area": "business area",
    "category": "metric workstream",        # dataset 1は"Metric Workstream"
    "vendor": "vendor: account name",       # dataset 1は"Vendor: Account Name"
    "order_type": "order types",            # dataset 1は"order tags"
    "job_name": "job name",
    "work_order_id": "work order: work order id",  # dataset 1は"work order id"
}

# L54の後に追加
BREAKDOWN_MAP_2: dict[str, str] = {
    "area": "business area",
    "category": "metric workstream",
    "vendor": "vendor: account name",
}
```

テストで追加するクラス:
- `TestDatasetId2`: 存在、値 `"apac-dot-ddd-change-issue-sql"`、文字列型
- `TestColumnMap2`: 7キー（month/area/category/vendor/order_type/job_name/work_order_id）、amp_av不在、各値検証
- `TestBreakdownMap2`: 3キー、COLUMN_MAP_2のサブセット検証
- `TestChartId01`: CHART_ID_CHANGE_ISSUE_TABLE = `"apac-dot-chart-01"`、タイトルID
- 既存 `TestComponentIds.test_all_component_ids_start_with_id_prefix` に新IDを追加

注意: カラム名はPhase 3のデータ検証結果で調整の可能性あり

---

### Step 2: `data_sources.yml` -- chart-01マッピング追加

対象: `src/pages/apac_dot_due_date/data_sources.yml`
テスト: `tests/unit/pages/apac_dot_due_date/test_data_sources.py`

```yaml
charts:
  apac-dot-chart-00: apac-dot-due-date
  apac-dot-chart-01: apac-dot-ddd-change-issue-sql
```

テスト変更:
- 既存テストのassertを `{CHART_ID_REFERENCE_TABLE, CHART_ID_CHANGE_ISSUE_TABLE}` に更新
- chart-01 が DATASET_ID_2 にマッピングされるassert追加
- `load_dashboard_config.cache_clear()` 必須

---

### Step 3: `charts/_ch01_change_issue_table.py` -- 新チャートビルダー

新規: `src/pages/apac_dot_due_date/charts/_ch01_change_issue_table.py`
テスト新規: `tests/unit/pages/apac_dot_due_date/charts/test_ch01_change_issue_table.py`
変更: `src/pages/apac_dot_due_date/charts/__init__.py`

`_ch00_reference_table.py`（148行）の構造をそのまま踏襲し、以下を変更:
- `from .._constants import BREAKDOWN_MAP_2, COLUMN_MAP_2` を使用
- `_TITLE = "1) DDD Change + Issue : Number of Work Order"`
- `build()` シグネチャは同一: `(filtered_df, breakdown_tab, num_percent_mode) -> tuple[str, Any]`
- ピボットロジック: `groupby(BREAKDOWN_MAP_2[tab], COLUMN_MAP_2["month"])[COLUMN_MAP_2["work_order_id"]].nunique()`

`charts/__init__.py` に追加:
```python
from . import _ch01_change_issue_table
__all__ = ["_ch00_reference_table", "_ch01_change_issue_table"]
```

テスト構造（`test_ch00_reference_table.py`のパターンを踏襲）:
- `_make_sample_df_2()`: COLUMN_MAP_2のカラム名でサンプルデータ生成
- `TestModuleImport`: インポート可能性
- `TestBuildReturnType`: tuple(2)、title含むstr、"Change"or"DDD"
- `TestBuildEmptyDataFrame`: html.P返却
- `TestBuildNumberMode`: DataTable、GRAND TOTAL行、AVG列、nunique計算
- `TestBuildPercentMode`: GRAND TOTAL=100.0
- `TestBuildBreakdownTabs`: `@pytest.mark.parametrize("breakdown_tab", list(BREAKDOWN_MAP_2.keys()))`

---

### Step 4: `_data_loader.py` -- load_and_filter_data_2 + load_filter_options拡張

対象: `src/pages/apac_dot_due_date/_data_loader.py`
テスト: `tests/unit/pages/apac_dot_due_date/test_data_loader.py`

#### 4a: `load_and_filter_data_2()` 追加

```python
def load_and_filter_data_2(
    reader: ParquetReader,
    dataset_id: str,
    selected_months,
    prc_filter_value: str,
    area_values,
    category_values,
    vendor_values,
    order_type_values,          # amp_av_valuesパラメータなし
) -> pd.DataFrame:
```

- `COLUMN_MAP_2` を使用してフィルタカラム名を解決
- PRC フィルタ: `COLUMN_MAP_2["job_name"]`（"job name"）で既存ロジック踏襲
- CategoryFilter: month/area/category/vendor/order_type（amp_avなし）
- amp_av_values パラメータ自体がない（dataset 2にカラム不在）

テスト追加クラス:
- `TestLoadAndFilterData2Basic`: DataFrame返却、フィルタなしで全行
- `TestLoadAndFilterData2NoAmpAv`: `inspect.signature` で amp_av_values パラメータ不在を確認
- `TestLoadAndFilterData2Filters`: edit month フィルタ、order types フィルタ、PRC フィルタ

#### 4b: `load_filter_options()` シグネチャ拡張

```python
def load_filter_options(reader: ParquetReader, dataset_id: str, dataset_id_2: str | None = None) -> dict:
```

変更ロジック:
- `dataset_id_2` が渡された場合:
  - `df2 = get_cached_dataset(reader, dataset_id_2)`
  - `months`: dataset 1 + dataset 2 の union（`sorted(set(months_1 + months_2))`）
  - `order_types`: dataset 2 の `COLUMN_MAP_2["order_type"]` から取得（dataset 1のorder tagsは使わない）
- `dataset_id_2` が None の場合: 既存動作（後方互換）

テスト追加クラス:
- `TestLoadFilterOptionsExtended`: months の union検証、order_types が dataset 2 から取得される検証
- `mock_cache.side_effect = [df1, df2]` で2つのデータセットをモック

---

### Step 5: `_layout.py` -- chart-01セクション追加

対象: `src/pages/apac_dot_due_date/_layout.py`
テスト: `tests/unit/pages/apac_dot_due_date/test_layout.py`

変更内容:
1. import に `CHART_ID_CHANGE_ISSUE_TABLE`, `CHART_ID_CHANGE_ISSUE_TABLE_TITLE` 追加
2. `load_filter_options` 呼び出しに `dataset_id_2` を追加:
```python
dataset_id = resolve_dataset_id(DASHBOARD_ID, CHART_ID_REFERENCE_TABLE)
dataset_id_2 = resolve_dataset_id(DASHBOARD_ID, CHART_ID_CHANGE_ISSUE_TABLE)
opts = load_filter_options(reader, dataset_id, dataset_id_2)
```
3. chart-00 セクションの後に chart-01 セクション追加:
```python
        # DDD Change + Issue Table Section (Chart 01)
        dbc.Row([
            dbc.Col([
                html.H3(id=CHART_ID_CHANGE_ISSUE_TABLE_TITLE, className="mt-4 mb-3"),
                html.Div(id=CHART_ID_CHANGE_ISSUE_TABLE),
            ], md=12),
        ]),
```

テスト追加:
- `TestChartSection` に chart-01-title（H3）と chart-01（Div）の存在確認4テスト追加
- `TestLayoutStructureOrder` の children数検証を 8以上 に更新

---

### Step 6: `_callbacks.py` -- 4 Output + dual load/filter/build

対象: `src/pages/apac_dot_due_date/_callbacks.py`
テスト: `tests/unit/pages/apac_dot_due_date/test_callbacks.py`

変更内容:

1. import追加:
```python
from ._constants import (
    ...,
    CHART_ID_CHANGE_ISSUE_TABLE,
    CHART_ID_CHANGE_ISSUE_TABLE_TITLE,
)
from ._data_loader import load_and_filter_data, load_and_filter_data_2
from .charts import _ch00_reference_table, _ch01_change_issue_table
```

2. Output を 4個に拡張:
```python
Output(CHART_ID_REFERENCE_TABLE_TITLE, "children"),
Output(CHART_ID_REFERENCE_TABLE, "children"),
Output(CHART_ID_CHANGE_ISSUE_TABLE_TITLE, "children"),
Output(CHART_ID_CHANGE_ISSUE_TABLE, "children"),
```

3. `update_all_charts` 関数本体:
```python
try:
    # Dataset 1: order_type NOT applied
    dataset_id_1 = resolve_dataset_id(DASHBOARD_ID, CHART_ID_REFERENCE_TABLE)
    filtered_df_1 = load_and_filter_data(
        reader, dataset_id_1,
        selected_months=selected_months,
        prc_filter_value=prc_filter_value,
        area_values=area_values,
        category_values=category_values,
        vendor_values=vendor_values,
        amp_av_values=amp_av_values,
        order_type_values=None,           # dataset 1にはorder_type適用しない
    )

    # Dataset 2: amp_av NOT applicable
    dataset_id_2 = resolve_dataset_id(DASHBOARD_ID, CHART_ID_CHANGE_ISSUE_TABLE)
    filtered_df_2 = load_and_filter_data_2(
        reader, dataset_id_2,
        selected_months=selected_months,
        prc_filter_value=prc_filter_value,
        area_values=area_values,
        category_values=category_values,
        vendor_values=vendor_values,
        order_type_values=order_type_values,  # dataset 2にorder_type適用
    )

    title_0, comp_0 = _ch00_reference_table.build(filtered_df_1, breakdown_tab, num_percent_mode)
    title_1, comp_1 = _ch01_change_issue_table.build(filtered_df_2, breakdown_tab, num_percent_mode)

    return (title_0, comp_0, title_1, comp_1)

except Exception as e:
    error_msg = html.Div([html.P(f"Error loading data: {str(e)}", className="text-danger")])
    return (
        "0) Reference : Number of Work Order", error_msg,
        "1) DDD Change + Issue : Number of Work Order", error_msg,
    )
```

テスト変更:
- 全既存テストの `len(result) == 2` を `len(result) == 4` に更新
- モックに `_ch01_change_issue_table` と `load_and_filter_data_2` を追加
- `TestLoadAndFilterDataDelegation`:
  - `test_calls_both_load_functions`: load_and_filter_data + load_and_filter_data_2 が各1回呼ばれる
  - `test_dataset1_not_passed_order_type`: load_and_filter_data の order_type_values が None
  - `test_dataset2_passed_order_type`: load_and_filter_data_2 の order_type_values にUI値が渡る
  - `test_dataset2_has_no_amp_av_param`: load_and_filter_data_2 のシグネチャに amp_av_values がない
- `TestErrorHandling`: 4-tuple 返却確認

---

## 注意事項

1. カラム名ケーシング: Dataset 2 は全小文字（`metric workstream`）、Dataset 1 はタイトルケース（`Metric Workstream`）。フィルタ選択肢の値自体が同じケースであることが前提。Phase 3 のデータ検証で確認
2. `lru_cache`: `load_dashboard_config` はキャッシュされる。テストでは `cache_clear()` が必須
3. 後方互換: `load_filter_options(reader, dataset_id)` の既存呼び出しは `dataset_id_2=None` デフォルトで動作維持

---

## 修正ファイル一覧

| ファイル | 変更 | Step |
|---|---|---|
| `backend/config/domo_datasets.yaml` | 完了済み（Phase 1） | - |
| `src/pages/apac_dot_due_date/_constants.py` | DATASET_ID_2, CHART_ID, COLUMN_MAP_2, BREAKDOWN_MAP_2 | 1 |
| `src/pages/apac_dot_due_date/data_sources.yml` | chart-01 マッピング | 2 |
| `src/pages/apac_dot_due_date/charts/_ch01_change_issue_table.py` | 新規作成 | 3 |
| `src/pages/apac_dot_due_date/charts/__init__.py` | import 追加 | 3 |
| `src/pages/apac_dot_due_date/_data_loader.py` | load_and_filter_data_2, load_filter_options拡張 | 4 |
| `src/pages/apac_dot_due_date/_layout.py` | chart-01 セクション + dataset_id_2 渡し | 5 |
| `src/pages/apac_dot_due_date/_callbacks.py` | 4 Output, dual load/build | 6 |
| `tests/unit/.../test_constants.py` | 新定数テスト追加 | 1 |
| `tests/unit/.../test_data_sources.py` | chart-01 assert 追加 | 2 |
| `tests/unit/.../charts/test_ch01_change_issue_table.py` | 新規作成 | 3 |
| `tests/unit/.../test_data_loader.py` | load_and_filter_data_2, 拡張テスト | 4 |
| `tests/unit/.../test_layout.py` | chart-01 セクション検証 | 5 |
| `tests/unit/.../test_callbacks.py` | 4-tuple, dual-load 検証 | 6 |

---

## 検証方法

1. Phase 3後: `ParquetReader.read_dataset("apac-dot-ddd-change-issue-sql")` でデータ読込・カラム名確認
2. 各Step後: `python3 -m pytest tests/unit/pages/apac_dot_due_date/ -v` でTDD RED->GREEN確認
3. 全Step完了後: `python3 -m pytest tests/unit/pages/apac_dot_due_date/ -v` で全テスト通過
4. 統合確認: `docker compose up` -> `/apac-dot-due-date` で2チャート表示確認
