# Architecture Codemap

Last Updated: 2026-02-07
Runtime: Python 3.x / Plotly Dash 4.x / Flask
Entry Point: `app.py`

## System Architecture

```
                     +---------------------+
                     |      Browser        |
                     +----------+----------+
                                |
                     +----------v----------+
                     |  Dash Application   |
                     |  (app.py)           |
                     +----------+----------+
                                |
              +-----------------+------------------+
              |                 |                  |
   +----------v-----+  +-------v-------+  +------v--------+
   |  Auth Layer     |  |  Page Layer   |  |  Components   |
   |  src/auth/      |  |  src/pages/   |  |  src/         |
   |  Flask-Login    |  |  Dash pages   |  |  components/  |
   +----------+------+  +-------+-------+  +------+--------+
              |                 |                  |
              |          +------v--------+         |
              |          |  Data Layer   +---------+
              |          |  src/data/    |
              |          +------+--------+
              |                 |
              |     +-----------+-----------+
              |     |                       |
         +----v-----v---+          +--------v--------+
         |  Core Layer   |          |  S3 / MinIO     |
         |  src/core/    |          |  (Parquet)      |
         +---------------+          +-----------------+
                                            ^
                                            |
                                   +--------+--------+
                                   |  ETL Pipelines  |
                                   |  backend/etl/   |
                                   +--------+--------+
                                            |
                           +----------------+-----------------+
                           |                |                 |
                     +-----v-----+   +------v------+   +-----v-----+
                     |  DOMO API |   |  CSV Files  |   |  (Future) |
                     |           |   |             |   |  RDS / S3 |
                     +-----------+   +-------------+   +-----------+
```

## Layer Overview

| Layer | Directory | Purpose | Key Files |
|-------|-----------|---------|-----------|
| Entry | `.` | App bootstrap, server config | `app.py` |
| Auth | `src/auth/` | Login, session, providers | `flask_login_setup.py`, `providers.py`, `login_callbacks.py`, `layout_callbacks.py` |
| Pages | `src/pages/` | Dashboard pages (Tier 1/2) | `dashboard_home.py`, `cursor_usage/`, `apac_dot_due_date/` |
| Components | `src/components/` | Reusable UI parts | `cards.py`, `filters.py`, `sidebar.py` |
| Charts | `src/charts/` | Chart templates, theming | `templates.py`, `plotly_theme.py` |
| Data | `src/data/` | Config, S3 I/O, filtering, registry | `config.py`, `parquet_reader.py`, `filter_engine.py`, `data_source_registry.py` |
| Core | `src/core/` | Caching, logging | `cache.py`, `logging.py` |
| ETL | `backend/etl/` | Extract-Transform-Load pipelines | `base_etl.py`, `etl_csv.py`, `etl_domo.py` |
| Scripts | `backend/scripts/` | CLI tools for ETL/ops | `load_csv.py`, `load_domo.py`, `clear_dataset.py` |
| Config | `backend/config/` | YAML dataset definitions | `domo_datasets.yaml`, `csv_datasets.yaml` |
| Assets | `assets/` | CSS stylesheets (7 files) | `00-reset.css` .. `06-login.css` |

## Dependency Flow

```
app.py
  +-- src.auth.flask_login_setup   (init_login_manager)
  +-- src.auth.login_callbacks     (register_login_callbacks)
  +-- src.auth.layout_callbacks    (register_layout_callbacks)
  +-- src.components.sidebar_callbacks (register_sidebar_callbacks)
  +-- src.core.cache               (init_cache)
  +-- src.layout                   (create_layout)
  +-- src.data.config              (settings)
  +-- src.pages.apac_dot_due_date  (explicit import)
  +-- src.pages.cursor_usage       (explicit import)
```

## Page Modularity (Tier 1 / Tier 2)

| Page | Tier | Format | Route | Callbacks | Data |
|------|------|--------|-------|-----------|------|
| Home | 1 | Single file | `/` | No | No |
| Cursor Usage | 2 | Package (5 files) | `/cursor-usage` | Yes (1 callback) | Yes (S3 via registry) |
| APAC DOT Due Date | 2 | Package (7 files + charts/) | `/apac-dot-due-date` | Yes (1 callback) | Yes (S3 via registry) |

## Data Source Resolution

Each Tier-2 page resolves its dataset ID at runtime:

```
_constants.py  --DASHBOARD_ID-->  data_sources.yml  --chart_id-->  dataset_id (S3 key)
                                       |
              data_source_registry.resolve_dataset_id()
                                       |
                              fallback: _constants.DATASET_ID
```

## Key Design Decisions

1. FilterSet is mutable (frozen=False) -- filters are appended dynamically in data loaders.
2. Chart templates (`templates.py`) contain only 3 generic builders (bar, line, pie) at 114 lines after dead-code removal.
3. ID collision prevention: every component ID is namespaced via `ID_PREFIX` (e.g. `cu-`, `apac-dot-`).
4. Timezone handling: Parquet stores UTC timestamps; pages strip timezone via `dt.tz_convert(None)` before filtering.
5. Package-style pages require explicit import in `app.py` because Dash's page scanner skips `__init__.py`.
6. `extract_unique_values()` centralizes unique-value extraction for filter dropdowns across all pages.
7. Test helpers in `tests/helpers/dash_test_utils.py` provide shared component-tree search utilities.

## Codebase Metrics

| Metric | Value |
|--------|-------|
| Total Python files (src + backend) | 60 |
| Total lines (src + backend) | ~4,150 |
| Test files | 53 |
| CSS asset files | 7 |
| YAML config files | 5 (2 ETL + 2 data_sources + docker-compose) |
| Dashboard pages | 3 (1 Tier-1 + 2 Tier-2) |
| ETL pipelines (implemented) | 2 (CSV, DOMO) |
| ETL pipelines (skeleton) | 3 (API, RDS, S3 Raw) |

## Related Codemaps

- [Frontend](./frontend.md) -- Pages, components, callbacks, CSS
- [Backend](./backend.md) -- ETL pipelines, scripts, config
- [Data](./data.md) -- Data models, S3 I/O, filtering, caching
