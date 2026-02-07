# Configuration Files

## domo_datasets.yaml

DOMO DataSetの設定を管理するファイルです。

### 設定項目

| 項目 | 必須 | 説明 | 例 |
|------|------|------|-----|
| `name` | ○ | DataSet識別名（人間向け） | "APAC DOT Due Date" |
| `domo_dataset_id` | ○ | DOMO DataSet ID（UUID） | "c1cddf9d-3c25-4464-81bf-ee13e9ab1dd2" |
| `minio_dataset_id` | ○ | MinIOのdataset ID（パス名） | "apac-dot-due-date" |
| `partition_column` | | パーティション分割するカラム名 | "delivery completed date" |
| `description` | | DataSetの説明 | "APAC DOT..." |
| `enabled` | ○ | 有効/無効フラグ | true |

### DataSet ID の確認方法

DOMOのDataSet URLから取得します：

```
https://disney.domo.com/datasources/c1cddf9d-3c25-4464-81bf-ee13e9ab1dd2/details/overview
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                   この部分がdomo_dataset_id
```

### パーティション分割について

**パーティション分割あり:**
```yaml
partition_column: "delivery completed date"
```

S3パス: `datasets/{minio_dataset_id}/partitions/date=YYYY-MM-DD/part-0000.parquet`

**パーティション分割なし:**
```yaml
partition_column: null
```

S3パス: `datasets/{minio_dataset_id}/data/part-0000.parquet`

### DataSet追加手順

1. `domo_datasets.yaml` に新しいDataSetを追加
2. `enabled: true` に設定
3. `backend/scripts/load_domo.py` を実行して取得

```bash
# 特定DataSetのみ取得
python backend/scripts/load_domo.py --dataset "DataSet Name"

# 全DataSet一括取得
python backend/scripts/load_domo.py --all
```

### DataSet無効化

一時的にDataSetの取得を停止する場合：

```yaml
enabled: false
```

### 設定例

```yaml
datasets:
  - name: "Sales Data"
    domo_dataset_id: "12345678-1234-1234-1234-123456789abc"
    minio_dataset_id: "sales-data"
    partition_column: "sale_date"
    description: "Daily sales transactions"
    enabled: true
  
  - name: "Customer Master"
    domo_dataset_id: "87654321-4321-4321-4321-cba987654321"
    minio_dataset_id: "customer-master"
    partition_column: null  # No partitioning
    description: "Customer master data"
    enabled: true
```

---

## csv_datasets.yaml

CSVファイルからのデータロードを管理するファイルです。DOMOパターンと同一の設定駆動方式。

### 設定項目

| 項目 | 必須 | 説明 | 例 |
|------|------|------|-----|
| `name` | ○ | DataSet識別名（人間向け） | "Cursor Usage Events" |
| `minio_dataset_id` | ○ | MinIOのdataset ID（パス名） | "cursor-usage" |
| `source_dir` | ○ | CSVファイルの格納ディレクトリ（project rootからの相対パス） | "backend/data_sources" |
| `file_pattern` | ○ | globパターン | "team-usage-events-*.csv" |
| `partition_column` | | パーティション分割するカラム名 | "Date" |
| `description` | | DataSetの説明 | "Cursor team usage events data" |
| `enabled` | ○ | 有効/無効フラグ | true |
| `csv_options` | | CSV読み込みオプション | delimiter, encoding |

### DataSet追加手順

1. `csv_datasets.yaml` に新しいDataSetを追加
2. `enabled: true` に設定
3. `backend/scripts/load_csv.py` を実行して取得

```bash
# 設定確認
python backend/scripts/load_csv.py --list

# 特定DataSetのみ取得
python backend/scripts/load_csv.py --dataset "DataSet Name"

# 全DataSet一括取得
python backend/scripts/load_csv.py --all

# ドライラン
python backend/scripts/load_csv.py --all --dry-run
```

### 設定例

```yaml
datasets:
  - name: "Cursor Usage Events"
    minio_dataset_id: "cursor-usage"
    source_dir: "backend/data_sources"
    file_pattern: "team-usage-events-*.csv"
    partition_column: "Date"
    enabled: true
    description: "Cursor team usage events data"
    # csv_options:
    #   delimiter: ","
    #   encoding: null
```

---

## 参考

- [DOMO API Documentation](../../../docs/DOMO/DOMO_API_Documentation.md)
- [ETL Workflow Skill](../../../.cursor/skills/etl-workflow/SKILL.md)
