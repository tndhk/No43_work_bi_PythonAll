# APAC DOT Due Date - フィルター値が表示されない問題の修正

## Context

APAC DOT Due Dateダッシュボードで、Area / Category / Vendor / AMP VS AV / Order Type のドロップダウンフィルターの値が表示されず、選択できない状態。

## 原因分析

`src/pages/apac_dot_due_date.py` の `layout()` 関数（行26-31）で、フィルターオプションの生成に問題がある:

```python
areas = sorted(df["business area"].unique().tolist())
```

`unique().tolist()` はNaN値を含む場合 `float('nan')` を返す。
`sorted()` でstr型とfloat(NaN)型の混在リストをソートすると `TypeError` が発生する。
行37の `except Exception` で全てキャッチされ、全フィルターリストが空 `[]` にフォールバックする。

結果: 全ドロップダウンのoptionsが空になり、値が表示されない。

## 修正方針

`layout()` 内のフィルターオプション生成で、NaN値を除外してからソートする。

## 修正対象ファイル

- `src/pages/apac_dot_due_date.py` (行26-31)

## 修正内容

### Step 1: テスト作成 (TDD)

`tests/unit/pages/test_apac_dot_due_date.py` にユニットテストを追加:

- NaN混在データでも `layout()` がフィルターオプションを正しく生成すること
- NaN値がフィルターオプションに含まれないこと

### Step 2: layout() のフィルターオプション生成を修正

行26-31を以下のパターンに変更:

```python
months = sorted(df["Delivery Completed Month"].dropna().unique().tolist())
areas = sorted(df["business area"].dropna().unique().tolist())
workstreams = sorted(df["Metric Workstream"].dropna().unique().tolist())
vendors = sorted(df["Vendor: Account Name"].dropna().unique().tolist())
amp_vs_av = sorted(df["AMP VS AV Scope"].dropna().unique().tolist())
order_types = sorted(df["order tags"].dropna().unique().tolist())
```

各カラムの `.unique()` 前に `.dropna()` を挿入することで、NaN値を除外してからソートする。

### Step 3: テスト実行と検証

- ユニットテストが通ること
- ローカルでダッシュボードを起動し、フィルタードロップダウンに値が表示されることを確認

## 検証方法

1. `pytest tests/unit/pages/test_apac_dot_due_date.py -v` でテスト実行
2. `python -m src.app` でローカル起動し、`/apac-dot-due-date` ページでフィルターの動作確認
