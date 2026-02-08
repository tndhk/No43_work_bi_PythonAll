# Architecture Codemap

Last Updated: 2026-02-08
Freshness: 2026-02-08T15:30:00Z
Entry Point: `app.py`
Runtime: Python 3.9+ / Plotly Dash 4.x

## System Architecture

```
                         +------------------+
                         |   Browser/User   |
                         +--------+---------+
                                  |
                         HTTP :8050 (Dash)
                                  |
                   +--------------+--------------+
                   |         app.py               |
                   |  (Dash + Flask server)       |
                   |  - Flask-Login auth          |
                   |  - Flask-Caching             |
                   |  - Dash Pages routing        |
                   +---------+----+----+----------+
                             |    |    |
              +--------------+    |    +---------------+
              |                   |                    |
    +---------v--------+  +------v-------+  +---------v--------+
    | src/auth/         |  | src/pages/   |  | src/components/  |
    | Authentication    |  | Page views   |  | UI components    |
    | Flask-Login       |  | Callbacks    |  | Sidebar/Cards/   |
    | Form provider     |  | Filters      |  | Filters/Slicers  |
    +------------------+  +------+-------+  +------------------+
                                 |
                    +------------+------------+
                    |            |            |
           +-------v--------+  |  +---------v--------+
           | src/data/       |  |  | src/charts/       |
           | Data access     |  |  | Chart templates   |
           | S3/Parquet I/O  |  |  | Plotly theme      |
           | Filter engine   |  |  | (Warm Prof Light) |
           | Dataset registry|  |  +------------------+
           +-------+--------+  |
                   |            +-------v--------+
          S3 API (boto3)        | src/utils/      |
                   |            | data_helpers    |
           +-------v--------+  | filter_helpers  |
           | MinIO / AWS S3  |  +----------------+
           | Parquet files   |
           +----------------+

    === Backend (ETL / Offline) ===

    +------------------+     +-------------------+
    | backend/etl/     |     | backend/scripts/  |
    | BaseETL          |---->| load_domo.py      |
    | CsvETL           |     | load_csv.py       |
    | DomoApiETL       |     | clear_dataset.py  |
    | masking.py       |     +-------------------+
    | ApiETL (stub)    |
    | RdsETL (stub)    |
    | S3RawETL (stub)  |
    | resolve_csv_path |
    +--------+---------+
             |
    +--------v---------+     +-------------------+
    | DOMO API         |     | CSV files         |
    | (OAuth2 REST)    |     | (local disk)      |
    +------------------+     +-------------------+
```

## Layer Overview

| Layer | Directory | Purpose | Status |
|-------|-----------|---------|--------|
| Entry | `app.py` | Dash app init, callback registration | Implemented |
| Auth | `src/auth/` | Flask-Login, form auth provider | Implemented |
| Pages | `src/pages/` | Dashboard pages (4 pages, 3 modularized) | Implemented |
| Components | `src/components/` | Sidebar, filters, KPI cards, slicer chips | Implemented |
| Charts | `src/charts/` | Plotly templates, Warm Professional Light theme | Implemented |
| Data | `src/data/` | S3 client, Parquet reader, filter engine, dataset registry | Implemented |
| Utils | `src/utils/` | Shared helpers (data_helpers, filter_helpers) | Implemented |
| Core | `src/core/` | Caching, structured logging | Implemented |
| ETL | `backend/etl/` | Data pipelines (CSV, DOMO impl; API/RDS/S3 stub) + masking | Partial |
| Scripts | `backend/scripts/` | CLI tools for ETL execution | Implemented |
| Config | `backend/config/` | DOMO/CSV dataset YAML definitions | Implemented |
| Assets | `assets/` | CSS (reset, typography, layout, components, animations, charts, login) | Implemented |

## Page Modularity

| Page | Path | Structure | Type |
|------|------|-----------|------|
| Home | `/` | `dashboard_home.py` | Single file (Tier 1) |
| Cursor Usage | `/cursor-usage` | `cursor_usage/` package | Modularized (Tier 2) |
| APAC DOT Due Date | `/apac-dot-due-date` | `apac_dot_due_date/` package | Modularized (Tier 2) |
| Hamm Overview | `/hamm-overview` | `hamm_overview/` package | Modularized (Tier 2) |

Modularized pages share the canonical structure:
- `__init__.py` -- page registration + `build_layout` reference + callback import
- `_constants.py` -- DATASET_ID, ID_PREFIX, COLUMN_MAP, chart/filter/control IDs
- `_data_loader.py` -- `load_filter_options()`, `load_and_filter_data()`
- `_layout.py` -- `build_layout()` -> html.Div
- `_callbacks.py` -- Dash callbacks
- `_filters.py` -- filter UI construction (when 5+ filters)
- `data_sources.yml` -- chart_id -> dataset_id mapping
- `SPEC.md` -- user-facing spec (Japanese)

## Dependency Flow

```
app.py
  +-> src.auth.flask_login_setup   (init_login_manager)
  +-> src.auth.login_callbacks     (register_login_callbacks)
  +-> src.auth.layout_callbacks    (register_layout_callbacks)
  +-> src.components.sidebar_callbacks (register_sidebar_callbacks)
  +-> src.core.cache               (init_cache)
  +-> src.layout                   (create_layout)
  +-> src.data.config              (settings)
  +-> src.pages.apac_dot_due_date  (explicit import)
  +-> src.pages.cursor_usage       (explicit import)
  +-> src.pages.hamm_overview      (explicit import)

pages/*
  +-> src.data.data_source_registry (resolve_dataset_id)
  +-> src.core.cache                (get_cached_dataset)
  +-> src.data.parquet_reader       (ParquetReader)
  +-> src.data.filter_engine        (apply_filters, extract_unique_values)
  +-> src.utils.filter_helpers      (build_filter_set_from_map)
  +-> src.utils.data_helpers        (safe_load_filter_options, strip_timezone)
  +-> src.components.filters        (create_slicer_filter, create_category_filter)
```

## Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Framework | Plotly Dash | 4.x |
| UI | Dash Bootstrap Components | >=1.5.0 |
| UI | Dash Mantine Components | (slicer chips) |
| Auth | Flask-Login | >=0.6.3 |
| Data | pandas / PyArrow | >=2.0.0 / >=14.0.0 |
| Storage | boto3 (S3/MinIO) | >=1.34.0 |
| Config | pydantic-settings | >=2.0.0 |
| Caching | Flask-Caching | >=2.0.0 |
| Logging | structlog | >=23.0.0 |
| Charts | Plotly | >=5.0.0 |
| Encoding | chardet | >=5.0.0 |
| Testing | pytest + moto[s3] | >=7.0.0 / >=5.0.0 |

## Deployment

```
docker-compose.yml
  services:
    dash      - Dash app (:8050)
    minio     - S3-compatible storage (:9000/:9001)
    minio-init - Bucket initialization
    test      - pytest runner (profile: test)
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| S3_ENDPOINT | S3/MinIO endpoint URL | None |
| S3_REGION | AWS region | ap-northeast-1 |
| S3_BUCKET | S3 bucket name | bi-datasets |
| S3_ACCESS_KEY | S3 access key | None |
| S3_SECRET_KEY | S3 secret key | None |
| BASIC_AUTH_USERNAME | Login username | admin |
| BASIC_AUTH_PASSWORD | Login password | changeme |
| SECRET_KEY | Flask session secret | auto-generated |
| AUTH_PROVIDER_TYPE | Auth backend type | form |
| DOMO_CLIENT_ID | DOMO API client ID | None |
| DOMO_CLIENT_SECRET | DOMO API client secret | None |
| ETL_MASKING_SECRET | HMAC secret for ETL column masking | None |

## Related Codemaps

- `codemaps/backend.md` -- ETL pipelines and scripts
- `codemaps/frontend.md` -- UI components, pages, auth
- `codemaps/data.md` -- Data layer, models, S3 I/O
