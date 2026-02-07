# APAC DOT Due Date ページが表示されない問題の修正

## Context

モジュール化実装（パッケージ変換）後、APAC DOT Due Dateページがサイドバー/ホームに表示されなくなった。
Cursor-usageのみ表示され、エラーも出ない。

## 根本原因

Dashの `_import_layouts_from_pages`（`dash/_pages.py:431`）が `.py` ファイルをスキャン時に `_` 始まりファイルを除外する:

```python
if file.startswith("_") or file.startswith(".") or not file.endswith(".py"):
    continue
```

`__init__.py` は `_` で始まるためスキップされ、`dash.register_page()` が実行されない。
結果、`page_registry` に未登録 → サイドバー/ホームに非表示。

## 修正方針: `app.py` で明示的インポート

`app.py` の `Dash()` コンストラクタ後に1行追加するだけ。

理由:
- Python標準のインポート機構で `__init__.py` が実行され、`register_page()` が呼ばれる
- 相対インポートも正しく解決される
- パッケージ構造の変更不要
- テストへの影響なし

## 実装ステップ

### Step 1: `app.py` に明示的インポート追加

`app = Dash(...)` ブロック（25行目）の直後、`app.server.config`（28行目）の前に追加:

```python
# Package-style pages require explicit import because Dash's page scanner
# skips __init__.py (starts with '_'). See: dash/_pages.py line 431
import src.pages.apac_dot_due_date  # noqa: F401
```

### Step 2: CLAUDE.md にパッケージページの規約を追記

```markdown
### Package-style Pages（パッケージ形式のページ）
- 単一ファイルページ（例: `cursor_usage.py`）はDashが自動検出する
- パッケージ形式（例: `apac_dot_due_date/`）は `app.py` に明示的importが必要
- 理由: Dashのスキャナーが `__init__.py` を `_` 始まりとしてスキップする
- 新規パッケージページ追加時: `app.py` に `import src.pages.<name>  # noqa: F401` を追加
```

## 対象ファイル

- `app.py` -- 1行追加（明示的インポート）
- `CLAUDE.md` -- 規約追記

## 検証方法

1. `python app.py` でアプリ起動
2. サイドバーに「APAC DOT Due Date」リンクが表示されること確認
3. `/apac-dot-due-date` にアクセスしてフィルタ・テーブル動作確認
4. ホームページのカードグリッドに表示されること確認
5. 既存テストが全パスすること確認
