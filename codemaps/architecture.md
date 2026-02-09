# Architecture Codemap

Freshness (UTC): 2026-02-10T00:00:00Z
Analysis Scope: `app.py`, `src/`, `backend/`

## High-Level Structure

1. Runtime app: `app.py` (Dash app init, auth wiring, callback registration, page imports)
2. Frontend/UI: `src/pages/`, `src/components/`, `src/auth/`, `src/layout.py`
3. Data access: `src/data/`, `src/core/cache.py`, `src/utils/`
4. Visualization contracts: `src/charts/`
5. Offline ingestion: `backend/etl/`, `backend/scripts/`, `backend/config/`
6. CI/CD: `.github/workflows/ci.yml` (lint, typecheck, test -- 3 parallel jobs)

## Architecture Relationships

```text
Browser
  -> app.py (Dash/Flask)
    -> src/auth/* (login/session)
    -> src/layout.py + src/auth/layout_callbacks.py (authenticated shell)
    -> src/pages/* (Dash Pages)
      -> src/components/* (filters/cards/sidebar)
      -> src/data/* + src/core/cache.py (dataset load/filter)
      -> src/charts/* (figure/table build)
      -> src/utils/* (callback_helpers, data_helpers, filter_helpers)
    -> S3/MinIO via src/data/s3_client.py + src/data/parquet_reader.py

backend/scripts/*
  -> backend/etl/*
    -> src/data/{s3_client,type_inferrer,csv_parser,config}
    -> S3/MinIO (Parquet write)
```

## Dependency Listing (Top-Level Imports)

- `app.py` imports `src.auth.*`, `src.components.sidebar_callbacks`, `src.core.cache`, `src.layout`, `src.data.config`, and explicit page packages (`src.pages.apac_dot_due_date`, `src.pages.cursor_usage`, `src.pages.hamm_overview`).
- `src/pages/*` imports primarily from:
  - `src.data.parquet_reader`, `src.core.cache`, `src.data.filter_engine`, `src.data.data_source_registry`
  - `src.charts.chart_builder`, `src.charts.table_builder`, `src.charts.empty_states`
  - `src.components.filters`, `src.components.cards`
  - `src.utils.callback_helpers`, `src.utils.data_helpers`
- `backend/etl/*` imports:
  - shared base `backend.etl.base_etl`
  - transformation helpers `src.data.csv_parser`, `src.data.type_inferrer`
  - masking `backend.etl.masking`
  - storage config/client `src.data.config`, `src.data.s3_client`

## Export Surface (Major Entrypoints)

- App/runtime: `create_layout`, `register_*_callbacks`, `init_login_manager`, `init_cache`
- Data layer: `ParquetReader`, `get_dataset_id`/`resolve_dataset_id`, `get_cached_dataset`, `apply_filters`
- UI builders: `build_chart`, `build_table`, `create_*_filter`, `create_kpi_card`, `create_kpi_card_with_delta`
- Chart types: `bar`, `line`, `pie`, `stacked_bar`, `scatter`, `area`, `horizontal_bar`
- Callback helpers: `register_clear_callbacks`
- Data helpers: `safe_load_filter_options`, `strip_timezone`, `resolve_single_dataset_id`
- ETL: `BaseETL`, `CsvETL`, `DomoApiETL`, `resolve_csv_path`, script `main()` functions

## CI/CD Pipeline

```text
.github/workflows/ci.yml
  triggers: push(main), pull_request(main)
  concurrency: cancel-in-progress per branch

  jobs (parallel):
    lint       -> ruff check src/
    typecheck  -> pip install requirements.txt + requirements-dev.txt -> mypy src/
    test       -> pip install requirements.txt + requirements-dev.txt -> pytest -v --tb=short
```

## Dependency Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Runtime dependencies (Dash, pandas, boto3, etc.) |
| `requirements-dev.txt` | Dev/test dependencies (pytest, ruff, mypy, moto) |
| `pyproject.toml` | Project metadata, tool configs (pytest, ruff, mypy, coverage) |
| `Dockerfile.dev` | Dev container (installs both requirements files) |

## Notes

- This codemap is derived from current repository imports/definitions only.
- No unverified external infrastructure assumptions are included.
