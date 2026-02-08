# Backend Codemap

Last Updated: 2026-02-08
Freshness: 2026-02-08T15:30:00Z
Entry Points: `backend/scripts/load_domo.py`, `backend/scripts/load_csv.py`, `scripts/upload_csv.py`

## Module Dependency Graph

```
backend/
+-- etl/
|   +-- base_etl.py
|   |   Imports: src.data.s3_client, src.data.config
|   |   Exports: BaseETL (ABC)
|   |
|   +-- etl_csv.py
|   |   Imports: base_etl.BaseETL, src.data.csv_parser, src.data.type_inferrer, masking
|   |   Exports: CsvETL
|   |
|   +-- etl_domo.py
|   |   Imports: base_etl.BaseETL, src.data.type_inferrer, requests, masking
|   |   Exports: DomoApiETL
|   |
|   +-- masking.py
|   |   Imports: hashlib, hmac, pandas
|   |   Exports: apply_hmac_masking(df, columns, secret, strict)
|   |
|   +-- etl_api.py    [stub - NotImplementedError]
|   |   Imports: base_etl.BaseETL
|   |   Exports: ApiETL
|   |
|   +-- etl_rds.py    [stub - NotImplementedError]
|   |   Imports: base_etl.BaseETL
|   |   Exports: RdsETL
|   |
|   +-- etl_s3.py     [stub - NotImplementedError]
|   |   Imports: base_etl.BaseETL
|   |   Exports: S3RawETL
|   |
|   +-- resolve_csv_path.py
|       Imports: pathlib.Path
|       Exports: resolve_csv_path(source_dir, file_pattern) -> Path
|
+-- scripts/
|   +-- load_domo.py
|   |   Imports: etl_domo.DomoApiETL, yaml, dotenv
|   |   CLI: --list, --dataset <name>, --all, --dry-run
|   |
|   +-- load_csv.py
|   |   Imports: etl_csv.CsvETL, yaml, dotenv
|   |   CLI: --list, --dataset <name>, --all, --dry-run
|   |
|   +-- clear_dataset.py
|       Imports: src.data.s3_client, src.data.config
|       CLI: <dataset_id>
|
+-- config/
|   +-- domo_datasets.yaml
|       Defines 3 DOMO datasets:
|         - APAC DOT Due Date (apac-dot-due-date, partitioned by delivery completed date)
|         - APAC DOT DDD Change + Issue (apac-dot-ddd-change-issue-sql, partitioned by edit month)
|         - Hamm_Dashboard (hamm-dashboard, non-partitioned)
|   +-- csv_datasets.yaml
|       Defines 1 CSV dataset:
|         - Cursor Usage Events (cursor-usage, partitioned by Date)
|
+-- data_sources/
    CSV source files (e.g. team-usage-events-*.csv)

scripts/
+-- upload_csv.py
    Imports: etl_csv.CsvETL
    CLI: <csv_file> --dataset-id <id> [--partition-col <col>]
```

## BaseETL Class

```python
class BaseETL(ABC):
    extract() -> pd.DataFrame         # Abstract: read from source
    transform(df) -> pd.DataFrame     # Abstract: apply transformations
    load(df, dataset_id, partition_column=None) -> None
        # Writes to S3: datasets/{id}/data/part-0000.parquet
        # Or partitioned: datasets/{id}/partitions/date=YYYY-MM-DD/part-0000.parquet
    run(dataset_id) -> None            # extract -> transform -> load
```

## Implemented ETL Classes

### CsvETL

```python
class CsvETL(BaseETL):
    __init__(csv_path, partition_column=None, csv_options=None, masking=None)
    extract()    # parse_full(file_bytes, options) via csv_parser
    transform()  # infer_schema(df) + apply_types(df, schema) + optional masking
    load()       # Overrides to use constructor partition_column
```

Data flow:
```
CSV file (disk) -> parse_full() -> infer_schema() -> apply_types()
  -> [optional] apply_hmac_masking() -> Parquet (S3)
```

### DomoApiETL

```python
class DomoApiETL(BaseETL):
    __init__(dataset_id, client_id=None, client_secret=None,
             partition_column=None, exclude_filter=None, masking=None)
    extract()    # OAuth2 token -> GET /v1/datasets/{id}/data (CSV export)
    transform()  # infer_schema() + apply_types() + exclude_filter + optional masking
    run()        # Overrides to pass partition_column to load()
```

Data flow:
```
DOMO API (OAuth2) -> CSV download -> type inference
  -> exclude filter -> [optional] HMAC masking -> Parquet (S3)
```

### masking.py

```python
def apply_hmac_masking(df, columns, secret, strict=True) -> pd.DataFrame
    # HMAC-SHA256 masking for PII columns
    # Requires ETL_MASKING_SECRET env var
    # strict=True raises on missing columns; strict=False skips them
    # Preserves NULL values (only masks non-null entries)
```

YAML config pattern (in domo_datasets.yaml / csv_datasets.yaml):
```yaml
masking:
  enabled: true
  strict: true
  columns:
    - "email"
    - "employee_id"
```

### resolve_csv_path

```python
def resolve_csv_path(source_dir: str, file_pattern: str) -> Path
    # Resolves the latest CSV file matching a glob pattern in a directory
    # Files sorted lexicographically; last entry returned
    # ISO-date suffixes (YYYY-MM-DD) map to chronological order
    # Raises FileNotFoundError if no matches
```

### Stub ETL Classes (Phase 1 skeleton)

| Class | File | Status |
|-------|------|--------|
| ApiETL | etl_api.py | NotImplementedError |
| RdsETL | etl_rds.py | NotImplementedError |
| S3RawETL | etl_s3.py | NotImplementedError |

## Scripts

### load_domo.py

YAML-driven DOMO dataset loader.

```
Usage:
  python3 backend/scripts/load_domo.py --list           # Show configured datasets
  python3 backend/scripts/load_domo.py --dataset "name" # Load specific dataset
  python3 backend/scripts/load_domo.py --all            # Load all enabled
  python3 backend/scripts/load_domo.py --all --dry-run  # Preview only
```

Config: `backend/config/domo_datasets.yaml`

### load_csv.py

YAML-driven CSV dataset loader.

```
Usage:
  python3 backend/scripts/load_csv.py --list           # Show configured datasets
  python3 backend/scripts/load_csv.py --dataset "name" # Load specific dataset
  python3 backend/scripts/load_csv.py --all            # Load all enabled
  python3 backend/scripts/load_csv.py --all --dry-run  # Preview only
```

Config: `backend/config/csv_datasets.yaml`

### clear_dataset.py

Deletes all S3 objects for a dataset (for re-upload scenarios).
```
Usage: python3 backend/scripts/clear_dataset.py <dataset_id>
```

### upload_csv.py (scripts/)

Generic CSV upload CLI.
```
Usage: python3 scripts/upload_csv.py <csv_file> --dataset-id <id> [--partition-col <col>]
```

## S3 Path Convention

```
s3://{bucket}/datasets/{dataset_id}/
  +-- data/part-0000.parquet                        # Non-partitioned
  +-- partitions/date=YYYY-MM-DD/part-0000.parquet  # Partitioned
```

## Dataset Registry (DOMO)

| Name | DOMO ID | MinIO ID | Partition | Exclude Filter |
|------|---------|----------|-----------|----------------|
| APAC DOT Due Date | c1cddf9d-... | apac-dot-due-date | delivery completed date | exclude_flg = "Not Exclude" |
| APAC DOT DDD Change+Issue | 2aff337e-... | apac-dot-ddd-change-issue-sql | edit month | exclude_flg = "Not Exclude" |
| Hamm_Dashboard | 0bc70adb-... | hamm-dashboard | (none) | (none) |

## Dataset Registry (CSV)

| Name | MinIO ID | Source | Partition |
|------|----------|--------|-----------|
| Cursor Usage Events | cursor-usage | backend/data_sources/team-usage-events-*.csv | Date |

## Error Handling

- BaseETL.load: Fails fast on S3 write errors
- DomoApiETL: OAuth2 errors, HTTP timeouts (30s auth, 300s data)
- CsvETL: File not found, encoding detection failures
- masking: ValueError on missing secret or missing columns (strict mode)
- resolve_csv_path: FileNotFoundError if dir missing or no matches
- Scripts: Structured try/except with traceback and exit codes

## Testing

```
tests/etl/
  test_base_etl.py         # BaseETL.load S3 writes
  test_etl_csv.py          # CsvETL extract/transform/load
  test_etl_domo.py         # DomoApiETL extract/transform
  test_etl_skeletons.py    # Stub classes raise NotImplementedError
  test_masking.py          # HMAC masking logic
  test_resolve_csv_path.py # CSV path resolution
  test_load_csv.py         # CSV loader script
  test_load_domo.py        # DOMO loader script

tests/scripts/
  test_upload_csv.py       # upload_csv.py script
```
