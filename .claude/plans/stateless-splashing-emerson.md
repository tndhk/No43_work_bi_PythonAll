# APAC DOT Due Date ページのモジュール化設計

## Context

`src/pages/apac_dot_due_date.py`（367行）に今後10個程度のチャート/テーブルを追加予定。
現在のモノリシック構造では1ファイルが1000行超になる見込みのため、フォルダ/ファイル分割とダッシュボード階層化を設計する。

## 方針: 単一ページ + パッケージ化（Approach B）

推奨度: ☆☆☆☆☆（5/5）

7つのフィルタを全チャートで共有するため、Dashの単一ページ内でタブ切り替え + チャートビルダーを別モジュールに抽出する構成が最適。

理由:
- フィルタ状態の共有が自然（単一コールバックスコープ内で完結）
- `dcc.Store`やURLパラメータによるクロスページ状態管理が不要
- サイドバー・ホームページの変更不要
- 各チャートビルダーが純粋関数となりテストが容易

別アプローチとの比較:
- Approach A（別ページ登録）: ☆（1/5） - フィルタ共有が煩雑、サイドバー改修必要
- Hybrid: ☆☆（2/5） - 10チャート程度なら過剰設計

## 提案するファイル構造

```
src/pages/
    dashboard_home.py              # 既存（変更なし）
    cursor_usage.py                # 既存（変更なし）
    apac_dot_due_date.py           # 削除 -> パッケージに変換
    apac_dot_due_date/
        __init__.py                # register_page() + layout()定義（~40行）
        _constants.py              # DATASET_ID, カラム名マッピング, ID_PREFIX（~30行）
        _data_loader.py            # load_filter_options(), load_and_filter_data()（~70行）
        _filters.py                # build_filter_layout() - フィルタUI構築（~60行）
        _layout.py                 # build_layout() - ページ全体のレイアウト組立（~70行）
        _callbacks.py              # @callback登録 + update_all_charts()（~100行）
        charts/
            __init__.py            # 全チャートビルダーのre-export
            _ch00_reference_table.py   # 現在の唯一のピボットテーブル（~80行）
            _ch01_xxx.py               # 新規チャート1
            _ch02_xxx.py               # 新規チャート2
            ...                        # 最大10個程度
```

## 各ファイルの責務

### `__init__.py`（エントリポイント）
- `dash.register_page()` 呼び出し（Dashがページとして認識する唯一のファイル）
- `layout()` 関数定義（`_layout.build_layout()` に委譲）
- `_callbacks` モジュールの副作用インポート（コールバック登録）

### `_constants.py`（定数・マッピング）
- `DATASET_ID = "apac-dot-due-date"`
- `COLUMN_MAP` - フィルタIDからDataFrameカラム名へのマッピング
- `BREAKDOWN_MAP` - タブIDからカラム名へのマッピング
- `ID_PREFIX = "apac-dot-"` - コンポーネントID衝突回避用プレフィックス

### `_data_loader.py`（データ読み込み・フィルタリング）
- `load_filter_options()` -> dict: フィルタ選択肢をキャッシュデータから取得
- `load_and_filter_data(...)` -> DataFrame: PRC/FilterSetによるフィルタリング済みデータ返却

### `_filters.py`（フィルタUIレイアウト）
- `build_filter_layout(options)` -> list[dbc.Row]: フィルタウィジェット群の構築
- 既存の`create_category_filter`等のコンポーネントを活用

### `_layout.py`（ページレイアウト組立）
- `build_layout()` -> html.Div: フィルタパネル + チャートタブ/プレースホルダー
- `dbc.Tabs` でチャートを論理グループ（Reference / Trend / Vendorなど）に分類

### `_callbacks.py`（コールバック）
- 単一 `@callback`: 全フィルタInput -> 全チャートOutput
- `load_and_filter_data()` を1回呼び出し、各チャートビルダーに渡す
- 空データ時のハンドリング

### `charts/_chNN_*.py`（各チャートビルダー）
- 各ファイルに `build(filtered_df, breakdown_tab, num_percent_mode)` 関数
- 純粋関数: DataFrame入力 -> Dashコンポーネント出力
- 個別にユニットテスト可能

## コンポーネントID命名規則

衝突回避のため全IDにページプレフィックスを付与:

```
{ID_PREFIX}{section}-{widget}
例: apac-dot-filter-month, apac-dot-ctrl-breakdown, apac-dot-chart-00
```

現在のID（`filter-month`, `area-filter`等）は全て一括リネーム。

## ダッシュボード階層化について

現時点ではサイドバー/ホームページの変更は不要。
将来20チャート超に成長した場合の拡張パス:
- `dbc.Tabs` のネスト（タブ内タブ）
- `register_page()` に `group` メタデータを追加してサイドバーをグループ化
- URL階層化（`/apac-dot-due-date/trend`, `/apac-dot-due-date/vendor`）

## 実装ステップ（TDDアプローチ）

### Step 1: パッケージ構造作成（動作変更なし）
- `src/pages/apac_dot_due_date/` ディレクトリ作成
- 既存コードを `__init__.py` にそのまま移動
- `src/pages/apac_dot_due_date.py` 削除
- テスト: 既存テスト全パス確認

### Step 2: `_constants.py` 抽出
- テスト先行: 定数値の検証テスト作成
- 実装: DATASET_ID, COLUMN_MAP, BREAKDOWN_MAP を抽出
- テスト: 全パス確認

### Step 3: `_data_loader.py` 抽出
- テスト先行: load_filter_options / load_and_filter_data のテスト作成
- 実装: データ読み込み・フィルタ構築ロジックを抽出
- テスト: 全パス確認

### Step 4: `_filters.py` 抽出
- テスト先行: build_filter_layout のテスト作成
- 実装: フィルタUI構築を抽出
- テスト: 全パス確認

### Step 5: `_layout.py` 抽出
- テスト先行: build_layout のテスト作成
- 実装: レイアウト組立を抽出（`__init__.py` の `layout()` は1行委譲に）
- テスト: 全パス確認

### Step 6: `charts/_ch00_reference_table.py` 抽出
- テスト先行: build() 関数のテスト作成（各種DataFrame入力パターン）
- 実装: ピボットテーブル構築ロジックを抽出
- テスト: 全パス確認

### Step 7: `_callbacks.py` 抽出
- テスト先行: update_all_charts のテスト作成
- 実装: コールバック登録を抽出
- テスト: 全パス確認

### Step 8: コンポーネントIDリネーム
- テスト先行: 新IDでのテスト更新
- 実装: `ID_PREFIX` を全IDに適用
- テスト: 全パス確認 + ブラウザ手動確認

### Step 9以降: 新チャート追加（個別に繰り返し）
- `charts/_chNN_*.py` を追加
- `_layout.py` にプレースホルダー追加
- `_callbacks.py` にOutput追加
- テスト追加

## 注意事項

- Dashのページスキャナーは `pages_folder` を再帰走査する。`_`プレフィックスファイルは `register_page()` を呼ばないため安全
- コールバック内の `@callback` デコレータはグローバル登録のため、`__init__.py` でのインポート順序に注意
- 既存テスト（`test_apac_dot_due_date.py`）のモックパスが変更になる（例: `src.pages.apac_dot_due_date._data_loader.ParquetReader`）
- チャート数が15を超えた場合、タブごとにコールバック分割を検討

## 検証方法

1. 各ステップごとに `pytest tests/unit/pages/test_apac_dot_due_date.py` でテスト通過確認
2. `python app.py` でアプリ起動、`/apac-dot-due-date` にアクセスしてフィルタ・テーブル動作確認
3. サイドバーに「APAC DOT Due Date」リンクが表示されること確認
4. ホームページのカードグリッドに表示されること確認

## 対象ファイル

- `src/pages/apac_dot_due_date.py` -> 削除（パッケージに変換）
- `src/pages/apac_dot_due_date/` -> 新規ディレクトリ（7ファイル + charts/サブディレクトリ）
- `tests/unit/pages/test_apac_dot_due_date.py` -> モックパス更新
- `src/components/sidebar.py` -> 変更なし（確認のみ）
- `app.py` -> 変更なし（確認のみ）
