# ページ設計統一: 2層ポリシー導入 + cursor_usage パッケージ化

## Context

`src/pages/` に2つのページパターンが混在している:
- 単一ファイル: `cursor_usage.py` (295行), `dashboard_home.py` (53行)
- パッケージ形式: `apac_dot_due_date/` (8ファイル, 643行)

問題点:
- 新規ページ作成時にどちらのパターンに従うか不明確
- `cursor_usage.py` はコンポーネントIDに接頭辞がなく、将来のID衝突リスクあり
- `cursor_usage.py` はテストがゼロ (パッケージ化で `_data_loader.py` 等の単体テストが可能に)

## 方針: 2層ポリシー

| 層 | 条件 | 形式 | 対象 |
|---|---|---|---|
| Tier 1 | コールバックなし, データ読込なし | 単一ファイル | `dashboard_home.py` のみ |
| Tier 2 | コールバックあり or データ読込あり | パッケージ形式 | `cursor_usage`, `apac_dot_due_date`, 今後の全新規ページ |

## 実装タスク

### Task 1: テスト作成 (TDD - テストファースト)

`tests/unit/pages/cursor_usage/` を作成し、分離後の各モジュールに対するテストを先に書く:

- `test_constants.py` - DATASET_ID, ID_PREFIX, COLUMN_MAP の存在と型を検証
- `test_data_loader.py` - `load_filter_options()`, `load_and_filter_data()` のテスト
  - 参考: `tests/unit/pages/apac_dot_due_date/test_data_loader.py` のパターンを踏襲

### Task 2: `_constants.py` 作成

```
src/pages/cursor_usage/_constants.py
```

抽出対象:
- `DATASET_ID = "cursor-usage"` (現在インラインで2箇所に散在)
- `ID_PREFIX = "cu-"` (新規追加 - ID衝突防止)
- `COLUMN_MAP` - 論理名からDataFrameカラム名へのマッピング

### Task 3: `_data_loader.py` 作成

```
src/pages/cursor_usage/_data_loader.py
```

`cursor_usage.py` から抽出:
- `load_filter_options(reader, dataset_id)` - layout用のフィルタ選択肢取得 (現在L22-39)
- `load_and_filter_data(reader, dataset_id, start_date, end_date, model_values)` - データ読込+フィルタ適用 (現在L125-154)

timezone除去 (`pd.to_datetime(..., utc=True).dt.tz_convert(None)`) もここに集約。

### Task 4: `_layout.py` 作成

```
src/pages/cursor_usage/_layout.py
```

- `build_layout()` 関数 (現在の `layout()` L18-101)
- 全コンポーネントIDに `ID_PREFIX` を適用:
  - `"date-filter"` -> `f"{ID_PREFIX}filter-date"`
  - `"model-filter"` -> `f"{ID_PREFIX}filter-model"`
  - `"kpi-total-cost"` -> `f"{ID_PREFIX}kpi-total-cost"` 等

### Task 5: `_callbacks.py` 作成

```
src/pages/cursor_usage/_callbacks.py
```

- `update_dashboard()` コールバック (現在L104-294)
- Input/OutputのコンポーネントIDを `ID_PREFIX` 付きに更新
- `_data_loader.py` の関数を利用

### Task 6: `__init__.py` 作成 + 旧ファイル削除

```python
# src/pages/cursor_usage/__init__.py
"""Cursor Usage Dashboard page."""
import dash
from ._layout import build_layout

def layout():
    return build_layout()

dash.register_page(__name__, path="/cursor-usage", name="Cursor Usage", order=1, layout=layout)
from . import _callbacks  # noqa: F401
```

- 旧 `src/pages/cursor_usage.py` を削除
- `app.py` に `import src.pages.cursor_usage  # noqa: F401` を追加

### Task 7: CLAUDE.md にポリシー追記

「ページ設計ポリシー」セクションを追加:
- 2層ポリシーの説明
- パッケージ形式のカノニカル構造 (必須5ファイル + オプション2ファイル)
- ID_PREFIX 必須ルール

### Task 8: 動作確認

- 全テスト実行 (`python3 -m pytest`)
- アプリ起動確認 (`docker compose up` or ローカル実行)
- `/cursor-usage` ページのフィルタ/チャート/テーブル動作確認

## 対象ファイル

変更:
- `app.py` - パッケージインポート追加

新規作成:
- `src/pages/cursor_usage/__init__.py`
- `src/pages/cursor_usage/_constants.py`
- `src/pages/cursor_usage/_data_loader.py`
- `src/pages/cursor_usage/_layout.py`
- `src/pages/cursor_usage/_callbacks.py`
- `tests/unit/pages/cursor_usage/test_constants.py`
- `tests/unit/pages/cursor_usage/test_data_loader.py`

削除:
- `src/pages/cursor_usage.py`

参考 (既存パターン):
- `src/pages/apac_dot_due_date/` - パッケージ形式のテンプレート
- `tests/unit/pages/apac_dot_due_date/` - テストパターン
