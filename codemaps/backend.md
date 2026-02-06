# Backend Codemap

Last Updated: 2026-02-06
Entry Points: `backend/scripts/load_domo.py`, `backend/scripts/load_cursor_usage.py`, `scripts/upload_csv.py`

## Module Dependency Graph

```
backend/
+-- etl/
|   +-- base_etl.py
|   |   Imports: src.data.s3_client, src.data.config
|   |   Exports: BaseETL (ABC)
|   |
|   +-- etl_csv.py
|   |   Imports: base_etl.BaseETL, src.data.csv_parser, src.data.type_inferrer
|   |   Exports: CsvETL
|   |
|   +-- etl_domo.py
|   |   Imports: base_etl.BaseETL, src.data.type_inferrer, requests
|   |   Exports: DomoApiETL
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
|       Imports: base_etl.BaseETL
|       Exports: S3RawETL
|
+-- scripts/
|   +-- load_domo.py
|   |   Imports: etl_domo.DomoApiETL, yaml, dotenv
|   |   CLI: --list, --dataset <name>, --all, --dry-run
|   |
|   +-- load_cursor_usage.py
|   |   Imports: etl_csv.CsvETL
|   |   Loads: CSV -> cursor-usage dataset (partitioned by Date)
|   |
|   +-- clear_dataset.py
|       Imports: src.data.s3_client, src.data.config
|       CLI: <dataset_id>
|
+-- config/
|   +-- domo_datasets.yaml
|       Defines DOMO DataSet mappings (domo_id -> minio_id)
|
+-- data_sources/
    (empty -- reserved for future data source clients)

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
    __init__(csv_path, partition_column=None, csv_options=None)
    extract()    # parse_full(file_bytes, options) via csv_parser
    transform()  # infer_schema(df) + apply_types(df, schema)
    load()       # Overrides to use constructor partition_column
```

Data flow:
```
CSV file (disk) -> parse_full() -> infer_schema() -> apply_types() -> Parquet (S3)
```

### DomoApiETL

```python
class DomoApiETL(BaseETL):
    __init__(dataset_id, client_id=None, client_secret=None,
             partition_column=None, exclude_filter=None)
    extract()    # OAuth2 token -> GET /v1/datasets/{id}/data (CSV export)
    transform()  # infer_schema() + apply_types() + exclude_filter
    run()        # Overrides to pass partition_column to load()
```

Data flow:
```
DOMO API (OAuth2) -> CSV download -> type inference -> exclude filter -> Parquet (S3)
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
  python backend/scripts/load_domo.py --list          # Show configured datasets
  python backend/scripts/load_domo.py --dataset "name" # Load specific dataset
  python backend/scripts/load_domo.py --all            # Load all enabled
  python backend/scripts/load_domo.py --all --dry-run  # Preview only
```

Config: `backend/config/domo_datasets.yaml`

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

### load_cursor_usage.py

Loads a specific CSV file for the cursor-usage dataset.
```
Source: backend/data_sources/team-usage-events-*.csv
Target: cursor-usage (partitioned by Date)
```

### clear_dataset.py

Deletes all S3 objects for a dataset (for re-upload scenarios).
```
Usage: python backend/scripts/clear_dataset.py <dataset_id>
```

### upload_csv.py (scripts/)

Generic CSV upload CLI.
```
Usage: python scripts/upload_csv.py <csv_file> --dataset-id <id> [--partition-col <col>]
```

## S3 Path Convention

```
s3://{bucket}/datasets/{dataset_id}/
  +-- data/part-0000.parquet                        # Non-partitioned
  +-- partitions/date=YYYY-MM-DD/part-0000.parquet  # Partitioned
```

## Error Handling

- BaseETL.load: Fails fast on S3 write errors
- DomoApiETL: OAuth2 errors, HTTP timeouts (30s auth, 300s data)
- CsvETL: File not found, encoding detection failures
- Scripts: Structured try/except with traceback and exit codes

## Testing

```
tests/etl/
  test_base_etl.py         # BaseETL.load S3 writes
  test_etl_csv.py          # CsvETL extract/transform/load
  test_etl_skeletons.py    # Stub classes raise NotImplementedError
tests/scripts/
  test_upload_csv.py       # CLI argument parsing and execution
```

## Related Codemaps

- `codemaps/data.md` -- csv_parser, type_inferrer, s3_client used by ETL
- `codemaps/architecture.md` -- System overview
