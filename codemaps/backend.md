# Backend Codemap

Freshness (UTC): 2026-02-09T12:00:00Z
Analysis Scope: `backend/`, plus backend dependencies in `src/`

## Backend Modules

- `backend/etl/base_etl.py`: abstract ETL contract (`extract`, `transform`, `load`, `run`)
- `backend/etl/etl_csv.py`: CSV -> typed DataFrame -> optional masking -> Parquet load
- `backend/etl/etl_domo.py`: DOMO API CSV export -> typed DataFrame -> optional masking -> Parquet load
- `backend/etl/masking.py`: HMAC masking utility for configured columns
- `backend/etl/resolve_csv_path.py`: latest-file resolver by glob pattern
- `backend/etl/etl_api.py`, `backend/etl/etl_rds.py`, `backend/etl/etl_s3.py`: skeleton ETL classes
- `backend/scripts/load_csv.py`, `backend/scripts/load_domo.py`, `backend/scripts/clear_dataset.py`: CLI entrypoints
- `backend/config/*.yaml`: dataset config for DOMO/CSV loaders

## Dependency Graph

```text
backend/scripts/load_csv.py
  -> backend.etl.etl_csv
  -> backend.etl.resolve_csv_path

backend/scripts/load_domo.py
  -> backend.etl.etl_domo

backend/scripts/clear_dataset.py
  -> src.data.s3_client
  -> src.data.config

backend.etl.base_etl
  -> src.data.s3_client
  -> src.data.config

backend.etl.etl_csv
  -> backend.etl.base_etl
  -> src.data.csv_parser
  -> src.data.type_inferrer
  -> backend.etl.masking

backend.etl.etl_domo
  -> backend.etl.base_etl
  -> src.data.type_inferrer
  -> backend.etl.masking
```

## Exports (Operational Surface)

- ETL classes: `BaseETL`, `CsvETL`, `DomoApiETL`, `ApiETL`, `RdsETL`, `S3RawETL`
- Utilities: `apply_hmac_masking`, `resolve_csv_path`
- Script entrypoints: `main` (`load_csv.py`, `load_domo.py`, `clear_dataset.py`)

## Architecture Relationships

- Backend ETL writes datasets consumed by `src/data/parquet_reader.py` in the Dash runtime.
- Shared configuration boundary is `src/data/config.py` (S3 and credentials).
- Shared storage boundary is S3/MinIO via `src/data/s3_client.py`.
