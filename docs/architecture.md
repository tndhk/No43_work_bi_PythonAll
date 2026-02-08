# System Architecture

Last Updated: 2026-02-08 (rev.4)

## High-Level Architecture

```
+-------------------------------------------------------------+
|                   Frontend (Plotly Dash)                      |
+-------------------------------------------------------------+
|  - Pages API (Multi-page routing)                            |
|  - Sidebar Navigation                                        |
|  - Interactive Charts (Plotly)                               |
|  - Filters & KPI Cards                                       |
|  - Flask-Login Auth (FormAuthProvider)                       |
|  - Warm Professional Light Theme                             |
+----------------+--------------------------------------------+
                 |
                 +---------------------+----------------------+
                 v                     v                      v
         +-------------+      +----------------+    +-----------------+
         |   S3/Parquet|      |  TTL Cache     |    |  Flask Server   |
         |  (Clean Data)      |  (flask-caching)    |  (Gunicorn)     |
         +-------------+      +----------------+    +-----------------+
                 |
                 v
         +-------------------------------------+
         |    Backend ETL Layer                |
         +-------------------------------------+
         | - ETL API (API -> Parquet)          |
         | - ETL S3 (S3 -> Parquet)            |
         | - ETL RDS (RDS -> Parquet)          |
         | - ETL CSV (CSV -> Parquet)          |
         | - ETL DOMO (DOMO API -> Parquet)    |
         | - Data Validators & Transformers    |
         +--------+----------------------------+
                  |
         +--------+--------+-----------+-----------+
         v                 v           v            v
    +--------+      +---------+  +----------+  +----------+
    |  API   |      |   S3    |  |   RDS    |  | CSV/DOMO |
    |Sources |      | Buckets |  |Database  |  |Files/API |
    +--------+      +---------+  +----------+  +----------+
```

## Component Architecture

### src/ Directory Structure

```
src/
+-- auth/                       # Authentication Layer (Flask-Login)
|   +-- __init__.py
|   +-- flask_login_setup.py   # Flask-Login initialization, User model
|   +-- providers.py           # AuthProvider protocol, FormAuthProvider
|   +-- login_layout.py        # Login page UI
|   +-- login_callbacks.py     # Login form callbacks
|   +-- layout_callbacks.py    # Auth-aware layout switching
|
+-- data/                      # Data Access Layer
|   +-- config.py             # Settings & Environment variables (Pydantic)
|   +-- s3_client.py          # S3 client (boto3 wrapper)
|   +-- parquet_reader.py     # Parquet file reading & partitioning
|   +-- csv_parser.py         # CSV parsing & encoding detection
|   +-- type_inferrer.py      # Column type inference
|   +-- dataset_summarizer.py # Data profiling & statistics
|   +-- filter_engine.py      # Filter logic (categorical, date range)
|   +-- models.py             # Pydantic models for type safety
|
+-- charts/                   # Visualization Layer
|   +-- chart_builder.py     # Shared: DataFrame + ChartSpec -> go.Figure (bar/line/pie/stacked_bar)
|   +-- table_builder.py     # Shared: DataFrame + TableSpec -> DataTable
|   +-- empty_states.py      # Empty/error state placeholders (create_empty_figure, etc.)
|   +-- specs.py             # ChartSpec, TableSpec (frozen dataclass definitions)
|   +-- plotly_theme.py       # Plotly Warm Professional Light theme
|   +-- templates.py          # Legacy chart templates (render_*_chart)
|
+-- core/                     # Infrastructure
|   +-- cache.py             # TTL Cache initialization (flask-caching)
|   +-- logging.py           # Structured logging (structlog)
|
+-- utils/                    # Shared Utility Modules
|   +-- data_helpers.py      # Data transformation helpers
|   +-- filter_helpers.py    # Filter building helpers (build_filter_set_from_map)
|   +-- callback_helpers.py  # register_clear_callbacks() for bulk clear-filter wiring
|
+-- pages/                    # Dashboard Pages (Dash Pages API)
|   +-- __init__.py
|   +-- dashboard_home.py    # Home page (card grid)
|   +-- cursor_usage/        # Cursor Usage dashboard (modularized)
|   |   +-- __init__.py      # Page registration + layout()
|   |   +-- _constants.py    # DATASET_ID, ID_PREFIX, COLUMN_MAP
|   |   +-- _data_loader.py  # Data loading & filtering
|   |   +-- _layout.py       # Page layout builder
|   |   +-- _callbacks.py    # Dash callbacks (KPIs, charts, table)
|   +-- apac_dot_due_date/   # APAC DOT Due Date dashboard (modularized)
|   |   +-- __init__.py      # Page registration + layout()
|   |   +-- _constants.py    # DATASET_ID, COLUMN_MAP, DatasetConfig
|   |   +-- _data_loader.py  # Data loading & filtering
|   |   +-- _filters.py      # Filter UI builder (slicer + category)
|   |   +-- _layout.py       # Page layout builder
|   |   +-- _callbacks.py    # Dash callbacks
|   |   +-- charts/
|   |       +-- __init__.py
|   |       +-- _ch00_reference_table.py  # Pivot table builder
|   +-- hamm_overview/       # HAMM Overview dashboard (modularized)
|       +-- __init__.py      # Page registration + layout()
|       +-- _constants.py    # DATASET_ID, ID_PREFIX, COLUMN_MAP, filter/chart IDs
|       +-- _data_loader.py  # Data loading, filtering, cadence column generation
|       +-- _filters.py      # Filter UI builder (slicer + category + cadence chip)
|       +-- _layout.py       # Page layout builder (MantineProvider)
|       +-- _callbacks.py    # Dash callbacks (volume table/chart, task table, slicer clears)
|
+-- components/              # Reusable UI Components
|   +-- __init__.py
|   +-- sidebar.py          # Left navigation sidebar
|   +-- sidebar_callbacks.py # Sidebar callbacks (logout, etc.)
|   +-- filters.py          # Filter selection components
|   +-- cards.py            # KPI card components
|
+-- layout.py               # Main layout (auth-aware container)
+-- exceptions.py           # Custom exception classes
```

### backend/ Directory Structure

```
backend/
+-- config/              # ETL Configuration
|   +-- domo_datasets.yaml  # DOMO DataSet definitions
|   +-- csv_datasets.yaml   # CSV DataSet definitions
|   +-- README.md           # Configuration guide
|
+-- data_sources/        # External Data Sources (stubs)
|   +-- __init__.py
|
+-- etl/                 # ETL Pipeline Scripts
|   +-- base_etl.py     # Abstract base ETL class (extract/transform/load)
|   +-- etl_api.py      # API -> Parquet transformation
|   +-- etl_s3.py       # S3 -> Parquet transformation
|   +-- etl_rds.py      # RDS -> Parquet transformation
|   +-- etl_csv.py      # CSV -> Parquet transformation
|   +-- etl_domo.py     # DOMO API -> Parquet (OAuth2 auth)
|   +-- masking.py      # HMAC-SHA256 masking utility (apply_hmac_masking)
|   +-- resolve_csv_path.py  # CSV file path resolution utility
|
+-- scripts/             # ETL Management Scripts
    +-- load_domo.py         # DOMO dataset loader (YAML config)
    +-- load_csv.py          # CSV dataset loader (YAML config, generic)
    +-- clear_dataset.py     # Dataset deletion utility
```

## Data Flow

### Dashboard Query Flow

```
User Request
    |
[Dash Page Callback]
    |
[Filter Selection]
    |
[Cache Check] --> Hit --> [Return Cached Data]
    | Miss
[S3 Parquet Read]
    |
[CSV Parser / Type Inferrer]
    |
[Filter Engine Application]
    |
[Dataset Summarizer (aggregation)]
    |
[Chart Renderer]
    |
[Cache Store (TTL)]
    |
[Return to Browser]
```

### ETL Pipeline Flow

```
Source Data (API/S3/RDS/CSV/DOMO)
    |
[Data Source Client Connect]
    |
[Extract]
    |
[Transform]
  - Type inference
  - Validation
  - Normalization
  - Exclude filter (DOMO)
    |
[Partition (by date/category)]
    |
[Write to S3 as Parquet]
    |
[Schema Registration (optional)]
```

## Dependency Graph

### Core Dependencies

```
app.py
+-- src.auth.flask_login_setup (Flask-Login)
+-- src.auth.login_callbacks (Login processing)
+-- src.auth.layout_callbacks (Auth-aware layout)
+-- src.components.sidebar_callbacks (Sidebar/logout)
+-- src.core.cache (flask-caching)
+-- src.data.config (Pydantic Settings)
+-- src.layout (Main layout)
    +-- src.components.sidebar
    +-- src.pages.* (Dash Pages)

src/pages/cursor_usage/__init__.py
+-- _layout.build_layout
+-- _callbacks (side-effect import for @callback registration)
    +-- _data_loader.load_and_filter_data
    +-- src.components.cards
    +-- src.charts.templates (render_line_chart, render_bar_chart, render_pie_chart)

src/pages/apac_dot_due_date/__init__.py
+-- _layout.build_layout
+-- _callbacks (side-effect import for @callback registration)
    +-- _data_loader.load_and_filter_data
    +-- _filters.build_filter_layout
    +-- charts._ch00_reference_table.build
    +-- src.utils.filter_helpers

src/pages/hamm_overview/__init__.py
+-- _layout.build_layout
+-- _callbacks (side-effect import for @callback registration)
    +-- _data_loader.load_and_filter_data
    +-- _data_loader.add_cadence_columns
    +-- _filters.build_filter_layout
    +-- _filters.build_cadence_filter
    +-- src.utils.filter_helpers
    +-- dash_mantine_components (ChipGroup for cadence)

src/data/parquet_reader.py
+-- boto3 (S3)
+-- pyarrow (Parquet)
+-- pandas (DataFrame)

src/core/cache.py
+-- flask_caching

src/charts/templates.py
+-- plotly

backend/etl/base_etl.py
+-- src.data.s3_client
+-- src.data.config
+-- pyarrow

backend/etl/etl_domo.py
+-- backend.etl.base_etl
+-- src.data.type_inferrer
+-- requests (DOMO API)
```

## Caching Strategy

- Layer: TTL-based in-memory cache (flask-caching)
- TTL: 3600 seconds (1 hour) -- ETLが日次実行のため長めに設定
- Key: `dataset:<dataset_id>` (フィルタパラメータは含まない)
- フィルタはキャッシュされたDataFrameに対してインメモリで適用
- Fallback: Direct S3 Parquet read on cache miss

## Authentication Flow

1. User accesses dashboard
2. Flask-Login checks session
3. If not authenticated: Redirect to /login
4. User enters credentials on login form
5. FormAuthProvider.authenticate() verifies against .env credentials
6. If valid: Flask-Login creates session, redirect to dashboard
7. If invalid: Show error on login form
8. Layout callbacks switch between login layout and dashboard layout

## Page Modularity Pattern

All Tier 2 pages (Cursor Usage, APAC DOT Due Date, HAMM Overview) follow the modularized page pattern:

```
<page_name>/
  __init__.py          -> register_page + layout()
  _constants.py        -> Dataset ID, column mappings, filter/chart IDs
  _data_loader.py      -> Data I/O (testable, no UI)
  _filters.py          -> Filter UI (testable, no I/O) -- slicer/category/chip builders
  _layout.py           -> Full layout builder
  _callbacks.py        -> @callback registration + slicer clear callbacks
  data_sources.yml     -> chart_id -> dataset_id mapping
  SPEC.md              -> User-facing spec (Japanese)
  charts/              -> (optional) Pure function chart builders
    _ch{NN}_{name}.py  -> build(df, ...) -> (title, component)
```

This pattern enables:
- Independent testing of data logic vs UI logic vs chart logic
- Adding charts without modifying existing code
- Clear separation of concerns per module
- Filter UI extraction via `_filters.py` for reusable filter layout builders

## Phase 2: LLM Integration

```
Chat Input (Vertex AI)
    |
[Context Assembly]
  - Dataset summary (schema, statistics)
  - Sample rows
  - Available filters
    |
[Prompt Engineering]
    |
[Vertex AI Gemini API Call]
    |
[Response Parsing]
  - Extract Python code
  - Extract visualization params
    |
[Sandbox Execution]
  - Safe Python environment
  - Limited to query operations
    |
[Result Rendering]
```

## Phase 3: SAML Authentication

```
Original Form Auth
    |
SAML IdP Integration
    |
Role-based Access Control
    |
Per-page Authorization
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Plotly Dash + Bootstrap | Interactive dashboards |
| UI Components | Dash Bootstrap Components | Responsive UI |
| UI Components | Dash Mantine Components | Chip/Slicer filters (Cadence等) |
| Server | Flask (Gunicorn) | WSGI server |
| Authentication | Flask-Login (Form) | User verification |
| Caching | flask-caching | Performance optimization |
| Data Processing | Pandas, PyArrow | DataFrame operations |
| Data Storage | Parquet (S3) | Columnar storage |
| Cloud Storage | boto3 | AWS S3 integration |
| Visualization | Plotly | Interactive charts |
| Theme | Warm Professional Light | CSS custom properties |
| Logging | structlog | Structured logging |
| ETL Framework | Custom (base_etl.py) | Data transformation |
| LLM (Phase 2) | Vertex AI SDK | Gemini integration |
| Type Checking | Pydantic | Data validation |

## Deployment Architecture

### Development (Docker Compose)

```
Host
+-- Dash App (port 8050)
+-- MinIO (port 9000/9001) - S3 mock
+-- MinIO Init - Bucket setup
+-- Test Runner (profile: test)
```

### Production (AWS)

```
ALB
+-- ECS Cluster (Fargate)
|   +-- Dash App (Gunicorn + Flask)
+-- S3 (Parquet data)
+-- RDS (Data source)
+-- CloudWatch (Logging)
+-- Secrets Manager (Credentials)
```

## Security Considerations

1. Authentication: Flask-Login + FormAuthProvider (local dev) -> SAML (production)
2. S3 Access: IAM roles (production) vs. credentials (dev)
3. Environment Variables: AWS Secrets Manager (production)
4. Code Sandbox: Restricted Python execution (Phase 2)
5. Input Validation: Pydantic models throughout
