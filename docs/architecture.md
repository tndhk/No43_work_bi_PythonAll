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

詳細なディレクトリ構造は [CONTRIB.md](CONTRIB.md) セクション6 を参照。

主要なコンポーネントレイヤー:
- `src/auth/`: 認証レイヤー（Flask-Login）
- `src/data/`: データアクセスレイヤー（S3, Parquet, フィルタ）
- `src/charts/`: 可視化レイヤー（チャート・テーブルビルダー、Spec定義）
- `src/pages/`: ダッシュボードページ（Dash Pages API）
- `src/components/`: 再利用可能UIコンポーネント（サイドバー、フィルタ、KPIカード）
- `backend/etl/`: ETLパイプライン（BaseETL、各種ETL実装）
- `backend/config/`: ETL設定ファイル（YAML）

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
    +-- src.charts.chart_builder (build_chart)
    +-- src.charts.table_builder (build_table)
    +-- src.charts.empty_states

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

技術スタックの詳細は [tech-spec.md](tech-spec.md) セクション1 を参照。

主要な技術:
- Frontend: Plotly Dash 4.x + Dash Bootstrap Components + Dash Mantine Components
- Server: Flask (Gunicorn) + Flask-Login
- Data: Pandas, PyArrow, boto3 (S3/Parquet)
- Visualization: Plotly (Warm Professional Light theme)
- Infrastructure: flask-caching (TTL), structlog (構造化ログ)
- ETL: Custom framework (BaseETL)

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
