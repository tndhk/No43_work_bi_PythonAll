# Data Codemap

Freshness (UTC): 2026-02-10T14:30:00Z
Analysis Scope: `src/data/`, `src/core/`, `src/utils/`, `src/exceptions.py`, data consumers in pages/backend

## Data Layer Structure

- Config and client
  - `src/data/config.py`: settings object (env-driven)
  - `src/data/s3_client.py`: boto3 client factory
- Storage reader and cache
  - `src/data/parquet_reader.py`: dataset read from S3/MinIO (single/partitioned)
  - `src/core/cache.py`: cached dataset retrieval
- Filtering and registry
  - `src/data/filter_engine.py`: category/date filters + filter application + `extract_unique_values`
  - `src/data/data_source_registry.py`: chart-to-dataset resolver from `data_sources.yml`
- Parsing and typing helpers
  - `src/data/csv_parser.py`: CSV parsing with encoding detection
  - `src/data/type_inferrer.py`: schema inference and type application
  - `src/data/models.py`: `ColumnSchema`
- Data source connectors
  - `backend/data_sources/__init__.py`: placeholder for future API/RDS connectors
- Utility modules
  - `src/utils/data_helpers.py`: `safe_load_filter_options`, `strip_timezone`, `resolve_single_dataset_id`, re-exports `extract_unique_values`
  - `src/utils/filter_helpers.py`: `build_filter_set_from_map`
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
  -> used by src/pages/*/_layout.py, src/pages/*/_callbacks.py, src/pages/*/_data_loader.py, src/utils/data_helpers.py

src/utils/data_helpers.py
  -> used by src/pages/*/_data_loader.py (safe_load_filter_options, strip_timezone, extract_unique_values)

src/utils/filter_helpers.py
  -> used by src/pages/*/_data_loader.py (build_filter_set_from_map)
  -> NOTE: page generator template uses inline isin() filtering instead of build_filter_set_from_map

src/utils/callback_helpers.py
  -> used by src/pages/*/_callbacks.py (register_clear_callbacks, ensure_list)

backend/data_sources (Phase 1)
  -> (no active dependencies; skeleton package)
```

## Architecture Relationships

- Runtime read path:
  - page callback -> page `_data_loader.py` -> `get_cached_dataset()` -> `ParquetReader.read_dataset()` -> S3/MinIO
- Runtime filter path (hand-written pages):
  - page `_data_loader.py` -> `build_filter_set_from_map()` / `FilterSet` -> `apply_filters()`
- Runtime filter path (generated pages):
  - page `_data_loader.py` -> inline `df[col].isin(values)` (no FilterSet)
- ETL write path:
  - backend ETL (`BaseETL.load`) writes Parquet to same S3 namespace consumed by `ParquetReader`
- Callback helpers:
  - `register_clear_callbacks()` eliminates boilerplate for filter clear buttons

## Page Data Loader Pattern

Each Tier 2 page has a `_data_loader.py` that follows a common shape:

1. `resolve_dataset_id_for_dashboard()` -- resolves dataset ID from `data_sources.yml` via `data_source_registry`
2. `_prepare_base_df(df)` -- strips timezones, adds derived columns (year, month, fiscal year, etc.)
3. `load_filter_options(reader, dataset_id)` -- returns dict of unique values per filter via `extract_unique_values`
4. `load_and_filter_data(...)` -- loads cached dataset, prepares it, applies filters
5. `build_*()` aggregation functions -- transform filtered data for charts/tables

Pages with complex transformations (e.g. hamm_overview) extract reusable logic into `_custom_logic.py` and re-export through `_data_loader.py`.

The page generator template (`tools/page_generator/templates/data_loader.py.j2`) produces this same structure, but uses inline `isin()` filtering and generates `build_*()` functions from `page_spec.yaml` declarative `data_transform` operations.
