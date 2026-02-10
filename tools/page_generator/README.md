# Page Generator

最終更新: 2026-02-10

## 概要

`page_generator` は、YAMLベースの設定ファイル（`page_spec.yaml`）からDashダッシュボードページの全コードを自動生成するツールです。

### 何ができるか

- YAMLファイル1つから6-7個のPythonファイルを自動生成
- フィルタ、KPIカード、チャート、テーブルのコード自動生成
- データ変換パイプライン（filter, groupby, pivot等）のコード生成
- レイアウト、コールバック、チャートビルダーのコード生成
- スキーマバリデーションによる設定ミスの事前検出

### システム要件

- Python 3.9以上
- 標準ライブラリのみ（追加インストール不要）
  - `pathlib`, `argparse`, `yaml`, `jinja2`（プロジェクトの依存関係に含まれる）

## インストール

インストール不要です。本ツールはプロジェクトに含まれています。

## 使い方

### 基本的なコマンド

```bash
# 全ファイル生成
python3 -m tools.page_generator <page_directory>

# 例: hamm_overviewページのコード生成
python3 -m tools.page_generator src/pages/hamm_overview
```

### オプション

#### --files: 特定ファイルのみ生成

```bash
# constantsとlayoutのみ生成
python3 -m tools.page_generator src/pages/my_page --files constants layout

# 複数ファイル指定
python3 -m tools.page_generator src/pages/my_page --files constants layout filters callbacks
```

利用可能なファイル名:
- `constants` - `_constants.py`
- `layout` - `_layout.py`
- `filters` - `_filters.py`
- `data_loader` - `_data_loader.py`
- `callbacks` - `_callbacks.py`
- `chart_builders` - `_chart_builders.py`
- `custom_logic` - `_custom_logic.py`（page_spec.yamlにcustom_logicセクションがある場合のみ）

#### --dry-run: 確認のみ（実際には生成しない）

```bash
# 生成されるファイルを確認するだけ
python3 -m tools.page_generator src/pages/my_page --dry-run
```

出力例:
```
[DRY RUN] Would generate:
  src/pages/my_page/_constants.py
  src/pages/my_page/_layout.py
  src/pages/my_page/_filters.py
  src/pages/my_page/_data_loader.py
  src/pages/my_page/_callbacks.py
  src/pages/my_page/_chart_builders.py
```

### 使用例

#### 例1: 新規ページの全ファイル生成

```bash
# 1. ディレクトリ作成
mkdir src/pages/sales_dashboard

# 2. page_spec.yaml作成
# テンプレートをコピーして編集
cp tools/page_generator/templates/new_page_spec.yaml src/pages/sales_dashboard/page_spec.yaml

# 3. 全ファイル生成
python3 -m tools.page_generator src/pages/sales_dashboard
```

#### 例2: 既存ページの一部ファイル再生成

```bash
# レイアウトとフィルタのみ再生成
python3 -m tools.page_generator src/pages/hamm_overview --files layout filters
```

#### 例3: ドライラン確認後に生成

```bash
# 1. ドライランで確認
python3 -m tools.page_generator src/pages/my_page --dry-run

# 2. 問題なければ実行
python3 -m tools.page_generator src/pages/my_page
```

## 生成されるファイル

### _constants.py

定数とID定義を生成します。

内容:
- `DASHBOARD_ID` - ダッシュボードID
- `ID_PREFIX` - コンポーネントID接頭辞
- `DATASET_ID` - データセットID
- `COLUMN_MAP` - 論理名→物理名マッピング
- 各フィルタのID定義
- 各コンポーネントのID定義
- `ChartSpec` と `TableSpec` のインスタンス

### _layout.py

レイアウト構築ロジックを生成します。

内容:
- `build_layout()` - メインレイアウトビルダー
- フィルタエリアのレイアウト
- コンポーネント（KPI、チャート、テーブル）のレイアウト
- Bootstrap 12グリッドシステムに基づく配置
- `dbc.Card` によるコンポーネントのラップ

### _filters.py

フィルタUIを生成します。

内容:
- `build_filters()` - フィルタUI構築
- 各フィルタタイプ（slicer, category, dropdown, date, chip_group）の生成
- クリアボタンの生成（必要時）

### _data_loader.py

データ読込ロジックを生成します。

内容:
- `load_filter_options()` - フィルタ選択肢の読込
- `load_and_filter_data()` - データ読込とフィルタリング
- 派生カラムの生成（year, month等）
- フィルタエンジンの適用

### _callbacks.py

Dashコールバックを生成します。

内容:
- KPIカード更新コールバック
- チャート更新コールバック
- テーブル更新コールバック
- フィルタクリアボタンのコールバック（`register_clear_callbacks`）

### _chart_builders.py

チャート/テーブル構築ロジックを生成します。

内容:
- 各チャート/テーブルのビルダー関数
- データ変換パイプライン（filter, groupby, pivot等）
- `build_chart()` / `build_table()` の呼び出し
- エラーハンドリング（empty_states）

### _custom_logic.py（オプション）

カスタムロジックのスケルトンを生成します（`page_spec.yaml` に `custom_logic` セクションがある場合のみ）。

内容:
- インポート済み関数のスケルトン
- 型ヒント付き関数定義
- Docstring付き

注意: 実装は手動で追加する必要があります。

## トラブルシューティング

### コマンドが見つからない

```bash
# エラー例
python3: No module named tools.page_generator
```

対処法:
1. プロジェクトルートディレクトリで実行しているか確認
2. `tools/page_generator/__main__.py` が存在するか確認

```bash
# プロジェクトルートに移動
cd /path/to/work_BI_PythonAll

# 再実行
python3 -m tools.page_generator src/pages/my_page
```

### validation error

```bash
# エラー例
ValidationError: 1 validation error for PageSpec
filters.0.column
  Field required [type=missing, input_value={...}, input_type=dict]
```

対処法:
1. エラーメッセージのフィールドパスを確認（例: `filters.0.column`）
2. `page_spec.yaml` の該当箇所を確認
3. `docs/page-spec-reference.md` を参照して修正

よくあるエラー:
- `Field required` - 必須フィールドが未設定
- `Duplicate IDs found` - 重複するID（全てのIDは一意である必要がある）
- `references unknown column` - column_mapに未定義のカラムを参照している
- `references unknown component_id` - layoutで未定義のcomponent_idを参照している

### 生成されたコードが動かない

#### 1. SyntaxError

```bash
# エラー例
SyntaxError: invalid syntax
```

対処法:
1. 生成されたコードの構文エラー箇所を確認
2. `page_spec.yaml` の対応する箇所を確認
3. 特殊文字やクォートのエスケープを確認

#### 2. ImportError

```bash
# エラー例
ImportError: cannot import name 'my_custom_function' from '_custom_logic'
```

対処法:
1. `_custom_logic.py` に関数が実装されているか確認
2. 関数名のスペルミスを確認
3. `page_spec.yaml` の `custom_logic.imports` を確認

#### 3. KeyError

```bash
# エラー例
KeyError: 'status'
```

対処法:
1. データセットに該当カラムが存在するか確認
2. `column_map` に定義されているか確認
3. 派生カラムの場合、`derived_columns` に定義されているか確認

#### 4. コールバックエラー

ブラウザの開発者ツール（F12）でコンソールエラーを確認します。

```
# よくあるコールバックエラー
- Input/Outputのコンポーネントが存在しない → IDの typo を確認
- コールバック関数が未定義 → _callbacks.py の生成を確認
- データ変換エラー → _chart_builders.py のロジックを確認
```

### ファイルが上書きされた

生成されたファイルは既存ファイルを上書きします。

対処法:
1. `git diff` で変更内容を確認
2. 必要に応じて `git checkout` で復元
3. 今後は `--dry-run` で確認してから実行

```bash
# 変更内容を確認
git diff src/pages/my_page/_constants.py

# 復元（慎重に）
git checkout src/pages/my_page/_constants.py
```

## 開発者向け情報

### ディレクトリ構造

```
tools/page_generator/
  __init__.py              # パッケージ初期化
  __main__.py              # エントリーポイント（python -m 実行用）
  cli.py                   # CLIロジック
  schema.py                # Pydanticスキーマ定義
  parser.py                # YAML解析とバリデーション
  operations.py            # データ変換操作（filter, groupby, pivot等）
  generators/              # コード生成器
    __init__.py
    constants_gen.py       # _constants.py生成
    layout_gen.py          # _layout.py生成
    filters_gen.py         # _filters.py生成
    data_loader_gen.py     # _data_loader.py生成
    callbacks_gen.py       # _callbacks.py生成
    chart_builders_gen.py  # _chart_builders.py生成
  templates/               # Jinja2テンプレート
    constants.py.j2
    layout.py.j2
    filters.py.j2
    data_loader.py.j2
    callbacks.py.j2
    chart_builders.py.j2
    custom_logic.py.j2
    new_page_spec.yaml     # 新規ページ作成用テンプレート
  test_*.py                # 単体テスト
  test_*.yaml              # テスト用YAML
```

### スキーマ（schema.py）

`page_spec.yaml` の構造を定義するPydanticモデル。

主要モデル:
- `PageSpec` - トップレベル
- `MetadataSpec` - メタデータ
- `FilterSpec` - フィルタ定義
- `ComponentSpec` - コンポーネント定義（KPI/chart/table）
- `ChartSpecYAML` - チャート仕様
- `TableSpecYAML` - テーブル仕様
- `KPICardSpec` - KPIカード仕様
- `DataTransformSpec` - データ変換仕様
- `LayoutSpec` - レイアウト定義

バリデーション:
- 必須フィールドチェック
- ID重複チェック
- カラム参照チェック
- コンポーネント参照チェック

### テンプレート（templates/）

Jinja2テンプレートでコード生成。

テンプレート変数:
- `spec` - `PageSpec` オブジェクト
- `metadata` - メタデータ
- `filters` - フィルタリスト
- `components` - コンポーネントリスト
- `layout` - レイアウト定義

フィルター:
- カスタムフィルターなし（標準Jinja2フィルターのみ使用）

### テストの実行方法

```bash
# 全テスト実行
pytest tools/page_generator/

# 特定テスト実行
pytest tools/page_generator/test_parser.py
pytest tools/page_generator/test_generators_basic.py

# カバレッジ付き実行
pytest --cov=tools.page_generator tools/page_generator/
```

主要テスト:
- `test_parser.py` - YAML解析とバリデーション
- `test_validation.py` - スキーマバリデーション
- `test_generators_basic.py` - constants, layout, filters生成
- `test_data_loader_gen.py` - data_loader生成
- `test_callbacks_chart_builders_gen.py` - callbacks, chart_builders生成
- `test_operations.py` - データ変換操作
- `test_cli.py` - CLIテスト
- `test_complex_spec.py` - 複雑なスペックのテスト

テストデータ:
- `test_minimal.yaml` - 最小限のスペック
- `test_complex.yaml` - 全機能を含むスペック

## 関連ドキュメント

- `docs/page-spec-reference.md` - `page_spec.yaml` の完全なリファレンス
- `docs/CONTRIB.md` セクション9 - SPEC-Driven Dashboard Page Creation
- `docs/tech-spec.md` - チャート構築API、データ変換仕様
- `src/pages/hamm_overview/page_spec.yaml` - 実稼働ページの実装例

## FAQ

### Q: 既存ページをSPEC-Drivenに移行できますか？

A: はい、既存コードから `page_spec.yaml` を逆生成することで移行可能です。ただし、現時点では手動作成が必要です。

手順:
1. 既存の `_constants.py` から `metadata`, `column_map` を抽出
2. 既存の `_filters.py` から `filters` を抽出
3. 既存の `_layout.py` から `layout` を抽出
4. 既存の `_chart_builders.py` から `components` と `data_transform` を抽出
5. `page_spec.yaml` を作成
6. コード生成して動作確認
7. カスタムロジックを `_custom_logic.py` へ移行

### Q: 生成されたコードを手動編集しても大丈夫ですか？

A: 推奨しません。次回の生成で上書きされます。

代替案:
1. `page_spec.yaml` を編集して再生成
2. カスタムロジックは `_custom_logic.py` に分離
3. どうしても必要な場合は `--files` で該当ファイルを生成対象から除外

### Q: 複雑なダッシュボードは対応できますか？

A: はい、`hamm_overview` のような複雑なダッシュボードも対応できます。

対応機能:
- 複数のフィルタタイプ（slicer, category, dropdown, date, chip_group）
- KPIカード、チャート、テーブルの混在
- 複雑なデータ変換パイプライン（filter, groupby, pivot等）
- カスタムロジックの分離

### Q: テンプレートをカスタマイズできますか？

A: はい、`tools/page_generator/templates/` のJinja2テンプレートを編集することでカスタマイズ可能です。

注意:
- テンプレート変更は全ページに影響します
- スキーマ（schema.py）との整合性を保つ必要があります
- テスト（test_generators_*.py）も更新が必要です

## ライセンス

本プロジェクトと同じライセンスに従います。
