# System Architecture

Last Updated: 2026-02-07

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
|   +-- templates.py          # Chart template library (Line, Bar, Pie, etc.)
|   +-- plotly_theme.py       # Plotly Warm Professional Light theme
|
+-- core/                     # Infrastructure
|   +-- cache.py             # TTL Cache initialization (flask-caching)
|   +-- logging.py           # Structured logging (structlog)
|
+-- pages/                    # Dashboard Pages (Dash Pages API)
|   +-- __init__.py
|   +-- dashboard_home.py    # Home page (card grid)
|   +-- cursor_usage.py      # Cursor Usage dashboard
|   +-- apac_dot_due_date/   # APAC DOT Due Date dashboard (modularized)
|       +-- __init__.py      # Page registration + layout()
|       +-- _constants.py    # DATASET_ID, COLUMN_MAP, BREAKDOWN_MAP
|       +-- _data_loader.py  # Data loading & filtering
|       +-- _filters.py      # Filter UI builder
|       +-- _layout.py       # Page layout builder
|       +-- _callbacks.py    # Dash callbacks
|       +-- charts/
|           +-- __init__.py
|           +-- _ch00_reference_table.py  # Pivot table builder
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
|   +-- resolve_csv_path.py  # CSV file path resolution utility
|
+-- scripts/             # ETL Management Scripts
    +-- load_domo.py         # DOMO dataset loader (YAML config)
    +-- load_cursor_usage.py # Cursor usage CSV loader
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

src/pages/apac_dot_due_date/__init__.py
+-- _layout.build_layout
+-- _callbacks (side-effect import for @callback registration)
    +-- _data_loader.load_and_filter_data
    +-- charts._ch00_reference_table.build

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
- TTL: 300-3600 seconds (configurable per dataset)
- Key: `<dataset_id>_<filter_hash>`
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

The APAC DOT Due Date page demonstrates the modularized page pattern:

```
apac_dot_due_date/
  __init__.py          -> register_page + layout()
  _constants.py        -> Dataset ID, column mappings
  _data_loader.py      -> Data I/O (testable, no UI)
  _filters.py          -> Filter UI (testable, no I/O)
  _layout.py           -> Full layout builder
  _callbacks.py        -> @callback registration
  charts/
    _ch{NN}_{name}.py  -> Pure function: build(df, ...) -> (title, component)
```

This pattern enables:
- Independent testing of data logic vs UI logic vs chart logic
- Adding charts without modifying existing code
- Clear separation of concerns per module

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
