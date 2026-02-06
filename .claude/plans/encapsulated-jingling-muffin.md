# CSV ETL設定駆動化 - DOMOパターンの横展開

## Context

CSVファイル更新時（ファイル名の日付部分が変わるだけ）に、既存ETLスクリプトの存在に気づかず新規ETLを作成してしまった。根本原因は、CSV ETLがDOMOのようなYAML設定 + 汎用ローダーを持たず、個別スクリプトにハードコードされていること。DOMOパターンをCSVに横展開し、CSV更新時は「ファイルを置くだけ」で完了する仕組みにする。

---

## 実装ステップ

### Step 1: 最新ファイル検出ユーティリティのテスト作成

- ファイル: `tests/etl/test_resolve_csv_path.py`
- テストケース:
  - glob パターンに一致する複数ファイルから最新（ファイル名の辞書順末尾）を返す
  - 一致ファイルが1つだけの場合はそれを返す
  - 一致ファイルが0件の場合は `FileNotFoundError`
  - 完全パス指定（globなし）の場合はそのまま返す

### Step 2: 最新ファイル検出ユーティリティの実装

- ファイル: `backend/etl/resolve_csv_path.py`
- 関数: `resolve_csv_path(source_dir: str, file_pattern: str) -> Path`
- ロジック:
  1. `Path(source_dir).glob(file_pattern)` で一致ファイルを取得
  2. ファイル名の辞書順ソート（ISO日付 `YYYY-MM-DD` は辞書順 = 時系列順）
  3. 最後の要素（最新）を返す
- CsvETLクラスは変更しない（そのまま再利用）

### Step 3: YAML設定ファイルの作成

- ファイル: `backend/config/csv_datasets.yaml`
- スキーマ:

```yaml
datasets:
  - name: "Cursor Usage Events"
    minio_dataset_id: "cursor-usage"
    source_dir: "backend/data_sources"   # project rootからの相対パス
    file_pattern: "team-usage-events-*.csv"  # glob パターン
    partition_column: "Date"
    enabled: true
    description: "Cursor team usage events data"
    # csv_options:            # 省略可（デフォルト: UTF-8, カンマ区切り）
    #   delimiter: ","
    #   encoding: null
```

### Step 4: 汎用ローダースクリプトのテスト作成

- ファイル: `tests/etl/test_load_csv.py`
- テストケース:
  - `load_config()` がYAMLを正しくパース
  - `load_dataset()` が resolve_csv_path -> CsvETL -> run を実行
  - `--list` でデータセット一覧表示
  - `--dry-run` でETL実行されない

### Step 5: 汎用ローダースクリプトの実装

- ファイル: `backend/scripts/load_csv.py`
- `load_domo.py` と同じCLIインターフェース:
  - `--list`: 設定済みCSVデータセット一覧（検出ファイル名も表示）
  - `--dataset "Name"`: 特定データセット実行
  - `--all`: 全enabledデータセット実行
  - `--dry-run`: プレビューのみ
- 内部フロー:
  1. `csv_datasets.yaml` 読み込み
  2. `resolve_csv_path()` で最新CSVファイル特定
  3. `CsvETL(csv_path, partition_column, csv_options)` でETL実行

### Step 6: 既存スクリプトの削除と検証

- `backend/scripts/load_cursor_usage.py` を削除
- 動作検証:
  - `python3 backend/scripts/load_csv.py --list`
  - `python3 backend/scripts/load_csv.py --dataset "Cursor Usage Events" --dry-run`
  - `python3 backend/scripts/load_csv.py --dataset "Cursor Usage Events"`
  - ParquetReaderでデータ読み込み確認

---

## 重要ファイル

| ファイル | 変更内容 |
|----------|----------|
| `backend/etl/resolve_csv_path.py` | 新規: 最新ファイル検出 |
| `backend/config/csv_datasets.yaml` | 新規: CSV データセット設定 |
| `backend/scripts/load_csv.py` | 新規: 汎用ローダー（`load_domo.py`のCSV版） |
| `tests/etl/test_resolve_csv_path.py` | 新規: テスト |
| `tests/etl/test_load_csv.py` | 新規: テスト |
| `backend/scripts/load_cursor_usage.py` | 削除 |

## 再利用する既存コード

- `backend/etl/etl_csv.py` の `CsvETL` クラス: 変更なし、そのまま利用
- `backend/scripts/load_domo.py`: CLI構造・argparse・出力フォーマットのテンプレート
- `src/data/csv_parser.py` の `CsvImportOptions`: csv_optionsの型定義
- `tests/etl/test_etl_csv.py`: テストパターン（tmp_path, mock_s3, Given/When/Then）

## 検証手順

```bash
# 1. テスト実行
python3 -m pytest tests/etl/test_resolve_csv_path.py -v
python3 -m pytest tests/etl/test_load_csv.py -v

# 2. 一覧表示（検出ファイル名が表示される）
python3 backend/scripts/load_csv.py --list

# 3. ドライラン
python3 backend/scripts/load_csv.py --dataset "Cursor Usage Events" --dry-run

# 4. 実行
python3 backend/scripts/load_csv.py --dataset "Cursor Usage Events"

# 5. データ検証
python3 -c "
import sys; sys.path.insert(0, '.')
from src.data.parquet_reader import ParquetReader
reader = ParquetReader()
df = reader.read_dataset('cursor-usage')
print(f'Shape: {df.shape}')
"
```
