# Backend Codemap

Last Updated: 2026-02-07
Runtime: Python 3.x
Entry Points: `backend/scripts/load_domo.py`, `backend/scripts/load_csv.py`

## Directory Structure

```
backend/
  __init__.py
  config/
    domo_datasets.yaml       # DOMO API ETL dataset definitions
    csv_datasets.yaml        # CSV file ETL dataset definitions
  data_sources/              # Raw CSV source files
  etl/
    __init__.py
    base_etl.py              # Abstract base class (extract/transform/load)
    etl_csv.py               # CSV -> Parquet ETL (implemented)
    etl_domo.py              # DOMO API -> Parquet ETL (implemented)
    etl_api.py               # REST API -> Parquet (skeleton)
    etl_rds.py               # RDS/DB -> Parquet (skeleton)
    etl_s3.py                # S3 Raw -> Parquet (skeleton)
    resolve_csv_path.py      # Glob-based CSV file resolver
  scripts/
    __init__.py
    load_csv.py              # CLI: CSV ETL runner (--list/--dataset/--all)
    load_domo.py             # CLI: DOMO ETL runner (--list/--dataset/--all)
    clear_dataset.py         # CLI: Delete dataset from S3/MinIO
```

## ETL Class Hierarchy

```
BaseETL (ABC)
  |-- extract() -> DataFrame        [abstract]
  |-- transform(df) -> DataFrame    [abstract]
  |-- load(df, dataset_id, partition_column=None)  [concrete]
  |-- run(dataset_id)               [concrete: extract->transform->load]
  |
  +-- CsvETL          [implemented]
  |     extract: csv_parser.parse_full()
  |     transform: type_inferrer.infer_schema() + apply_types()
  |     load: override to use constructor's partition_column
  |
  +-- DomoApiETL      [implemented]
  |     extract: DOMO REST API (OAuth2 -> CSV export -> DataFrame)
  |     transform: type_inferrer + optional exclude_filter
  |     run: override to pass partition_column
  |
  +-- ApiETL          [skeleton -- NotImplementedError]
  +-- RdsETL          [skeleton -- NotImplementedError]
  +-- S3RawETL        [skeleton -- NotImplementedError]
```

## Module Dependency Graph

```
backend/scripts/load_csv.py
  +-- backend.etl.etl_csv.CsvETL
  |     +-- src.data.csv_parser (parse_full, CsvImportOptions)
  |     +-- src.data.type_inferrer (infer_schema, apply_types)
  |     +-- backend.etl.base_etl.BaseETL
  |           +-- src.data.s3_client (get_s3_client)
  |           +-- src.data.config (settings)
  +-- backend.etl.resolve_csv_path

backend/scripts/load_domo.py
  +-- backend.etl.etl_domo.DomoApiETL
  |     +-- requests (HTTP)
  |     +-- src.data.type_inferrer (infer_schema, apply_types)
  |     +-- backend.etl.base_etl.BaseETL
  |           +-- src.data.s3_client (get_s3_client)
  |           +-- src.data.config (settings)

backend/scripts/clear_dataset.py
  +-- src.data.s3_client (get_s3_client)
  +-- src.data.config (settings)
```

## YAML Configuration

### domo_datasets.yaml

```yaml
datasets:
  - name: "APAC DOT join Due Date change(first time)"
    domo_dataset_id: "c1cddf9d-..."
    minio_dataset_id: "apac-dot-due-date"
    partition_column: "delivery completed date"
    enabled: true
    exclude_filter:
      column: "exclude_flg"
      keep_value: "Not Exclude"
```

### csv_datasets.yaml

```yaml
datasets:
  - name: "Cursor Usage Events"
    minio_dataset_id: "cursor-usage"
    source_dir: "backend/data_sources"
    file_pattern: "team-usage-events-*.csv"
    partition_column: "Date"
    enabled: true
```

## Scripts

### load_csv.py

| Flag | Behavior |
|------|----------|
| `--list` | Display all configured CSV datasets |
| `--dataset "Name"` | Load a specific dataset by name |
| `--all` | Load all enabled datasets |
| `--dry-run` | Show plan without executing |
| `--config path` | Custom YAML config path |

### load_domo.py

| Flag | Behavior |
|------|----------|
| `--list` | Display all configured DOMO datasets |
| `--dataset "Name"` | Load a specific dataset by name |
| `--all` | Load all enabled datasets |
| `--dry-run` | Show plan without executing |

### clear_dataset.py

Usage: `python3 backend/scripts/clear_dataset.py <dataset_id>`

Deletes all S3 objects under `datasets/{dataset_id}/`.

## S3 Path Convention

```
datasets/
  {dataset_id}/
    data/
      part-0000.parquet            # Non-partitioned
    partitions/
      date=YYYY-MM-DD/
        part-0000.parquet          # Partitioned by date
```

## ETL Data Flow

```
Source (DOMO API / CSV file)
  |
  v
extract() --> raw DataFrame
  |
  v
transform() --> typed DataFrame (type_inferrer) + optional filters
  |
  v
load() --> Parquet via pyarrow --> S3/MinIO (boto3)
```

## resolve_csv_path

Utility in `backend/etl/resolve_csv_path.py`:
- Accepts `source_dir` and `file_pattern` (glob)
- Returns the lexicographically last match (latest ISO-date-suffixed file)
- Raises `FileNotFoundError` if no matches

## Testing

| File | Coverage |
|------|----------|
| `tests/etl/test_base_etl.py` | BaseETL abstract contract |
| `tests/etl/test_etl_csv.py` | CsvETL pipeline |
| `tests/etl/test_etl_skeletons.py` | Skeleton classes raise NotImplementedError |
| `tests/etl/test_load_csv.py` | load_csv.py CLI integration |
| `tests/etl/test_resolve_csv_path.py` | Glob resolution logic |
| `tests/scripts/test_upload_csv.py` | Script-level tests |

## Related Codemaps

- [Architecture](./architecture.md) -- System overview
- [Data](./data.md) -- Data layer shared with ETL (s3_client, config, type_inferrer)
- [Frontend](./frontend.md) -- Pages that consume ETL output
