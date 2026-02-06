# Architecture Codemap

Last Updated: 2026-02-07
Entry Point: `app.py`
Runtime: Python 3.9+ / Plotly Dash 2.14+

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
    | Form provider     |  | Filters      |  | Filters          |
    +------------------+  +------+-------+  +------------------+
                                 |
                    +------------+------------+
                    |                         |
           +-------v--------+      +---------v--------+
           | src/data/       |      | src/charts/       |
           | Data access     |      | Chart templates   |
           | S3/Parquet I/O  |      | Plotly theme      |
           | Filter engine   |      | (Warm Prof Light) |
           +-------+--------+      +------------------+
                   |
          S3 API (boto3)
                   |
           +-------v--------+
           | MinIO / AWS S3  |
           | Parquet files   |
           +----------------+

    === Backend (ETL / Offline) ===

    +------------------+     +-------------------+
    | backend/etl/     |     | backend/scripts/  |
    | BaseETL          |---->| load_domo.py      |
    | CsvETL           |     | load_cursor.py    |
    | DomoApiETL       |     | clear_dataset.py  |
    | ApiETL (stub)    |     +-------------------+
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
| Pages | `src/pages/` | Dashboard pages (3 pages, 1 modularized) | Implemented |
| Components | `src/components/` | Sidebar, filters, KPI cards | Implemented |
| Charts | `src/charts/` | Plotly templates, Warm Professional Light theme | Implemented |
| Data | `src/data/` | S3 client, Parquet reader, filter engine | Implemented |
| Core | `src/core/` | Caching, structured logging | Implemented |
| ETL | `backend/etl/` | Data pipelines (CSV, DOMO impl; API/RDS/S3 stub) | Partial |
| Scripts | `backend/scripts/` | CLI tools for ETL execution | Implemented |
| Config | `backend/config/` | DOMO dataset YAML definitions | Implemented |
| Assets | `assets/` | CSS (reset, typography, layout, components, animations, charts, login) | Implemented |

## Page Modularity

| Page | Path | Structure | Type |
|------|------|-----------|------|
| Home | `/` | `dashboard_home.py` | Single file |
| Cursor Usage | `/cursor-usage` | `cursor_usage.py` | Single file |
| APAC DOT Due Date | `/apac-dot-due-date` | `apac_dot_due_date/` package | Modularized |

The APAC DOT Due Date page uses a modularized package structure:
- `__init__.py` -- page registration + layout() entry
- `_constants.py` -- DATASET_ID, COLUMN_MAP, BREAKDOWN_MAP
- `_data_loader.py` -- load_filter_options(), load_and_filter_data()
- `_filters.py` -- build_filter_layout()
- `_layout.py` -- build_layout()
- `_callbacks.py` -- update_all_charts() @callback
- `charts/_ch00_reference_table.py` -- pivot table builder (pure function)

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
```

## Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Framework | Plotly Dash | >=2.14.0 |
| UI | Dash Bootstrap Components | >=1.5.0 |
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

## Related Codemaps

- `codemaps/backend.md` -- ETL pipelines and scripts
- `codemaps/frontend.md` -- UI components, pages, auth
- `codemaps/data.md` -- Data layer, models, S3 I/O
