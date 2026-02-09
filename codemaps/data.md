# Data Codemap

Freshness (UTC): 2026-02-10T00:00:00Z
Analysis Scope: `src/data/`, `src/core/`, `src/utils/`, `src/exceptions.py`, data consumers in pages/backend

## Data Layer Structure

- Config and client
  - `src/data/config.py`: settings object (env-driven)
  - `src/data/s3_client.py`: boto3 client factory
- Storage reader and cache
  - `src/data/parquet_reader.py`: dataset read from S3/MinIO (single/partitioned)
  - `src/core/cache.py`: cached dataset retrieval
- Filtering and registry
  - `src/data/filter_engine.py`: category/date filters + filter application
  - `src/data/data_source_registry.py`: chart-to-dataset resolver from `data_sources.yml`
- Parsing and typing helpers
  - `src/data/csv_parser.py`: CSV parsing with encoding detection
  - `src/data/type_inferrer.py`: schema inference and type application
  - `src/data/models.py`: `ColumnSchema`
- Utility modules
  - `src/utils/data_helpers.py`: `safe_load_filter_options`, `strip_timezone`, `resolve_single_dataset_id`
  - `src/utils/filter_helpers.py`: filter construction utilities
  - `src/utils/callback_helpers.py`: `register_clear_callbacks`, `ensure_list`
- Diagnostics and exceptions
  - `src/data/dataset_summarizer.py`
  - `src/exceptions.py`: `DatasetFileNotFoundError`

## Dependency Graph

```text
src/data/config.py
  -> used by src/data/s3_client.py, src/data/parquet_reader.py, src/auth/providers.py, src/auth/login_layout.py, backend/etl/base_etl.py

src/data/s3_client.py
  -> used by src/data/parquet_reader.py, backend/etl/base_etl.py, backend/scripts/clear_dataset.py

src/data/parquet_reader.py
  -> used by src/core/cache.py, src/data/dataset_summarizer.py, src/pages/*/_data_loader.py, src/utils/data_helpers.py

src/data/filter_engine.py
  -> used by src/pages/*/_data_loader.py, src/utils/filter_helpers.py, src/utils/data_helpers.py

src/data/data_source_registry.py
  -> used by src/pages/*/_layout.py, src/pages/*/_callbacks.py, src/utils/data_helpers.py

src/utils/callback_helpers.py
  -> used by src/pages/*/_callbacks.py (register_clear_callbacks, ensure_list)

src/utils/data_helpers.py
  -> used by src/pages/*/_data_loader.py (safe_load_filter_options, strip_timezone)
```

## Architecture Relationships

- Runtime read path:
  - page callback -> page `_data_loader.py` -> `get_cached_dataset()` -> `ParquetReader.read_dataset()` -> S3/MinIO
- Runtime filter path:
  - page `_data_loader.py` -> `build_filter_set_from_map()` / `FilterSet` -> `apply_filters()`
- ETL write path:
  - backend ETL (`BaseETL.load`) writes Parquet to same S3 namespace consumed by `ParquetReader`
- Callback helpers:
  - `register_clear_callbacks()` eliminates boilerplate for filter clear buttons
