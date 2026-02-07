# src/pages/ リファクタリング計画

## Context

現在2つのTier 2ページ（`cursor_usage`, `apac_dot_due_date`）が存在し、同じパターンのコードが重複している。3つ目以降のページ追加時にコピペが増え続ける構造になっている。一方、2ページの性質は大きく異なる（KPI+チャート vs ピボットテーブル）ため、過度な抽象化は逆効果。

目標: 実際に重複している「リーフユーティリティ」のみを共通化し、不要なコードを削除する。

---

## 改善一覧（優先度順）

### 1. `extract_unique_values` ヘルパーの抽出 [Small]

`_data_loader.py` で6回（apac_dot）+ 1回（cursor）繰り返される同一パターンを1関数に:

```python
# 現状（apac_dot_due_date/_data_loader.py で6回繰り返し）
sorted(df[COLUMN_MAP["area"]].dropna().unique().tolist())
    if COLUMN_MAP["area"] in df.columns else []
```

対象ファイル:
- `src/data/filter_engine.py` -- `extract_unique_values(df, column)` を追加
- `src/pages/apac_dot_due_date/_data_loader.py` -- 6箇所を置換
- `src/pages/cursor_usage/_data_loader.py` -- 1箇所を置換
- `tests/unit/data/test_filter_engine.py` -- テスト追加

### 2. `apac_dot_due_date` の ID_PREFIX 一貫性修正 [Small]

`_filters.py` と `_callbacks.py` でハードコード文字列 `"apac-dot-..."` を使用しており、`ID_PREFIX` 定数と不整合。全コンポーネントIDを `_constants.py` に集約する。

対象ファイル:
- `src/pages/apac_dot_due_date/_constants.py` -- ID定数を追加（FILTER_ID_MONTH, CTRL_ID_NUM_PERCENT 等）
- `src/pages/apac_dot_due_date/_filters.py` -- 定数をimportして使用
- `src/pages/apac_dot_due_date/_callbacks.py` -- 定数をimportして使用
- `src/pages/apac_dot_due_date/_layout.py` -- 定数をimportして使用
- `tests/unit/pages/apac_dot_due_date/test_constants.py` -- テスト追加

### 3. `resolve_dataset_id` の共通化 [Small]

4箇所で `get_dataset_id() + None判定 + エラー/フォールバック` パターンが重複:

```python
# cursor_usage: ValueError送出
dataset_id = get_dataset_id(DASHBOARD_ID, CHART_ID_COST_TREND)
if dataset_id is None:
    raise ValueError(...)

# apac_dot_due_date: フォールバック
dataset_id = get_dataset_id(DASHBOARD_ID, CHART_ID_REFERENCE_TABLE) or DATASET_ID
```

対象ファイル:
- `src/data/data_source_registry.py` -- `resolve_dataset_id(dashboard_id, chart_id, fallback=None)` を追加
- `src/pages/cursor_usage/_layout.py` -- 使用
- `src/pages/cursor_usage/_callbacks.py` -- 使用
- `src/pages/apac_dot_due_date/_layout.py` -- fallback付きで使用
- `src/pages/apac_dot_due_date/_callbacks.py` -- fallback付きで使用
- `tests/unit/data/test_data_source_registry.py` -- テスト追加

### 4. `FilterSet` の `frozen=True` 削除 [Small]

`FilterSet` は `frozen=True` だが、両ページの `_data_loader.py` でリストに `.append()` している。frozen制約が形骸化しており、将来の混乱を招く。

対象ファイル:
- `src/data/filter_engine.py` -- `FilterSet` から `frozen=True` を除去
- `tests/unit/data/test_filter_engine.py` -- 既存テスト通過を確認

### 5. テストヘルパーの共通化 [Small]

Dashコンポーネントツリーの再帰検索関数が複数テストファイルに重複:
- `_find_component_by_id`
- `_extract_text_recursive`
- `_extract_dropdown_options` / `_extract_dropdown_value`

対象ファイル:
- 新規: `tests/helpers/__init__.py`, `tests/helpers/dash_test_utils.py`
- `tests/unit/pages/apac_dot_due_date/test_layout.py` -- importに切替
- `tests/unit/pages/apac_dot_due_date/test_callbacks.py` -- importに切替
- `tests/unit/pages/test_apac_dot_due_date.py` -- importに切替

### 6. `src/charts/templates.py` のデッドコード削除 [Small]

以下は未使用またはDash 4.x非互換:
- `render_summary_number` -- 未使用
- `render_table` -- `dangerously_allow_html=True` でDash 4.x非互換、未使用
- `render_pivot_table` -- 同上
- `CHART_TEMPLATES` / `get_chart_template` / `get_all_chart_types` -- 未使用レジストリ

残すべき関数: `render_bar_chart`, `render_line_chart`, `render_pie_chart` のみ（`cursor_usage/_callbacks.py` が使用）

対象ファイル:
- `src/charts/templates.py` -- 不要コード削除
- `tests/unit/charts/test_templates.py` -- 対応テスト削除

---

## 見送った改善（過度な抽象化を避ける）

| 案 | 見送り理由 |
|---|---|
| `__init__.py` の共通テンプレート化 | 14行のボイラープレート。コピペで十分。抽象化コスト > 節約 |
| `_data_loader.py` のベースクラス | 2ページの戻り値構造が完全に異なる（3キー vs 9キー）。ジェネリックにすると過度に複雑 |
| 共通レイアウトビルダー | H1+フィルタ以外の構造が全く違う。フック地獄になる |
| コールバックエラーハンドラの共通化 | 出力タプルの形状が異なる（7要素 vs 2要素）。共通化不可能 |
| ParquetReaderのシングルトン化 | ステートレスで生成コストが低い。グローバル状態を増やすデメリットの方が大きい |

---

## 実装順序

各改善は独立しているため、並行実行が可能。推奨順序:

```
1. extract_unique_values  -- filter_engine.py を触る
2. FilterSet frozen修正  -- 同ファイル、1と同時に実施
3. ID_PREFIX修正         -- apac_dot_due_date に閉じた変更
4. resolve_dataset_id    -- data_source_registry.py を触る
5. テストヘルパー共通化   -- テストのみの変更
6. デッドコード削除       -- 最後（影響範囲を最小化）
```

## TDDアプローチ

全ステップで以下の順序を遵守:
1. RED: 新機能のテストを先に書く（失敗を確認）
2. GREEN: 最小の実装でテストを通す
3. REFACTOR: 既存コードを新しいユーティリティに切り替え
4. VERIFY: 全既存テストの通過を確認（`python3 -m pytest tests/`）

## 検証方法

```bash
# 全テスト実行
python3 -m pytest tests/ -v

# カバレッジ確認
python3 -m pytest tests/ --cov=src --cov-report=term-missing

# アプリ起動確認（手動）
python3 app.py
# -> http://localhost:8050 で両ページが正常表示されることを確認
```
