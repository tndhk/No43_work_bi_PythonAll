# Fix: APAC DOT Due Date テーブルの "Infinity" ページネーション

## Context

APAC DOT Due Date ページの "Number of Work Order" テーブルでページネーションが "1 / Infinity" と表示される。
ユーザーはキャッシュの問題を疑ったが、調査の結果、根本原因は `page_size=0` がDataTableに渡されていることによる除算エラー（`total_rows / 0 = Infinity`）。

## 根本原因（2箇所）

### Bug 1: TABLE_SPECS に `page_size` が未指定
- `src/pages/apac_dot_due_date/_constants.py:124-166`
- 両方の TableSpec（`ch00_reference_table`, `ch01_change_issue_table`）に `page_size` が設定されていない
- `src/charts/specs.py:34` のデフォルト値 `page_size: int = 0` が使われる
- DataTable は `page_size=0` を受けると `page_count = total_rows / 0 = Infinity` と計算する
- 比較: `hamm_overview/_constants.py` は正しく `page_size=20` を指定している

### Bug 2: `resolved_spec` が `page_size` を引き継がない
- `src/pages/apac_dot_due_date/_callbacks.py:94-102`
- コールバック内で `resolved_spec` を構築する際に `page_size`, `sort_action`, `filter_action` を転送していない
- Bug 1 を修正しても、この箇所でデフォルト値 `0` に戻ってしまう

## 修正プラン

### Step 1: `_constants.py` に `page_size=20` を追加
- ファイル: `src/pages/apac_dot_due_date/_constants.py`
- 両方の TABLE_SPECS エントリに `page_size=20` を追加

### Step 2: `_callbacks.py` の `resolved_spec` にフィールド転送を追加
- ファイル: `src/pages/apac_dot_due_date/_callbacks.py:94-102`
- `page_size=table_spec.page_size`, `sort_action=table_spec.sort_action`, `filter_action=table_spec.filter_action` を追加

### Step 3: `table_builder.py` に防御ガードを追加
- ファイル: `src/charts/table_builder.py:61`
- `page_size=spec.page_size if spec.page_size > 0 else 20` のようなガードを追加
- 今後同じバグが他ページで再発するのを防止

### Step 4: テスト作成・実行
- `_constants.py` の TABLE_SPECS に `page_size > 0` の検証テストを追加
- `table_builder.py` の `page_size=0` ガードのテストを追加
- 既存テスト実行で回帰がないことを確認

## 修正対象ファイル
- `src/pages/apac_dot_due_date/_constants.py` (lines 124, 145)
- `src/pages/apac_dot_due_date/_callbacks.py` (lines 94-102)
- `src/charts/table_builder.py` (line 61)
- `tests/unit/pages/apac_dot_due_date/test_constants.py` (新規 or 追記)

## 検証方法
1. 単体テスト実行: `python3 -m pytest tests/unit/pages/apac_dot_due_date/ -v`
2. table_builder テスト: `python3 -m pytest tests/ -k "table_builder" -v`
3. アプリ起動後、APAC DOT Due Date ページでテーブルのページネーションが正常（例: "1 / 3"）になることを確認
