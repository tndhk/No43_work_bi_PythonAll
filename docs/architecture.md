# System Architecture

Last Updated: 2026-02-06

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (Plotly Dash)                    │
├─────────────────────────────────────────────────────────────┤
│  - Pages API (Multi-page routing)                           │
│  - Sidebar Navigation                                       │
│  - Interactive Charts (Plotly)                              │
│  - Filters & KPI Cards                                      │
│  - Basic Auth (Dash-Auth)                                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────────┬──────────────────────┐
                 ▼                     ▼                      ▼
         ┌─────────────┐      ┌────────────────┐    ┌─────────────────┐
         │   S3/Parquet│      │  TTL Cache     │    │  Flask Server   │
         │  (Clean Data)      │  (flask-caching)    │  (Gunicorn)     │
         └─────────────┘      └────────────────┘    └─────────────────┘
                 │
                 ▼
         ┌─────────────────────────────────────┐
         │    Backend ETL Layer                │
         ├─────────────────────────────────────┤
         │ - ETL API (API -> Parquet)          │
         │ - ETL S3 (S3 -> Parquet)            │
         │ - ETL RDS (RDS -> Parquet)          │
         │ - ETL CSV (CSV -> Parquet)          │
         │ - Data Validators & Transformers    │
         └────────┬────────────────────────────┘
                  │
         ┌────────┴────────┬────────────┬─────────────┐
         ▼                 ▼            ▼             ▼
    ┌────────┐      ┌─────────┐  ┌──────────┐  ┌──────────┐
    │  API   │      │   S3    │  │   RDS    │  │ CSV File │
    │Sources │      │ Buckets │  │Database  │  │Upload    │
    └────────┘      └─────────┘  └──────────┘  └──────────┘
```

## Component Architecture

### src/ Directory Structure

```
src/
├── auth/                    # Authentication Layer
│   └── basic_auth.py       # Basic Auth setup (Dash-Auth)
│
├── data/                   # Data Access Layer
│   ├── config.py          # Settings & Environment variables
│   ├── s3_client.py       # S3 client (boto3 wrapper)
│   ├── parquet_reader.py  # Parquet file reading & partitioning
│   ├── csv_parser.py      # CSV parsing & encoding detection
│   ├── type_inferrer.py   # Column type inference
│   ├── dataset_summarizer.py # Data profiling & statistics
│   ├── filter_engine.py   # Filter logic (categorical, date range)
│   └── models.py          # Pydantic models for type safety
│
├── charts/                # Visualization Layer
│   └── templates.py       # Chart template library (Line, Bar, Pie, etc.)
│
├── core/                  # Infrastructure
│   ├── cache.py          # TTL Cache initialization (flask-caching)
│   └── logging.py        # Structured logging (structlog)
│
├── pages/                 # Dashboard Pages (Dash Pages API)
│   ├── __init__.py
│   └── dashboard_home.py # Home page
│
├── components/           # Reusable UI Components
│   ├── __init__.py
│   ├── sidebar.py       # Left navigation sidebar
│   ├── filters.py       # Filter selection components
│   └── cards.py         # KPI card components
│
├── callbacks/            # Page-specific Callbacks (Phase 1)
│   └── __init__.py      # Callback registration
│
├── llm/                  # LLM Features (Phase 2)
│   ├── __init__.py
│   ├── vertex_client.py # Vertex AI SDK integration
│   ├── sandbox.py       # Code execution sandbox
│   └── chat_panel.py    # Chat UI component
│
├── layout.py            # Main layout with sidebar
├── callbacks.py         # Global callbacks
└── exceptions.py        # Custom exception classes
```

### backend/ Directory Structure

```
backend/
├── data_sources/        # External Data Sources
│   ├── api_client.py   # HTTP API client
│   ├── s3_client.py    # S3 data source client
│   └── rds_client.py   # RDS/PostgreSQL client
│
└── etl/                 # ETL Pipeline Scripts
    ├── base_etl.py     # Abstract base ETL class
    ├── etl_api.py      # API → Parquet transformation
    ├── etl_s3.py       # S3 → Parquet transformation
    ├── etl_rds.py      # RDS → Parquet transformation
    └── etl_csv.py      # CSV → Parquet transformation
```

## Data Flow

### Dashboard Query Flow

```
User Request
    ↓
[Dash Page Callback]
    ↓
[Filter Selection]
    ↓
[Cache Check] ─→ Hit → [Return Cached Data]
    ↓ Miss
[S3 Parquet Read]
    ↓
[CSV Parser / Type Inferrer]
    ↓
[Filter Engine Application]
    ↓
[Dataset Summarizer (aggregation)]
    ↓
[Chart Renderer]
    ↓
[Cache Store (TTL)]
    ↓
[Return to Browser]
```

### ETL Pipeline Flow

```
Source Data (API/S3/RDS/CSV)
    ↓
[Data Source Client Connect]
    ↓
[Extract]
    ↓
[Transform]
  - Type inference
  - Validation
  - Normalization
    ↓
[Partition (by date/category)]
    ↓
[Write to S3 as Parquet]
    ↓
[Schema Registration (optional)]
```

## Dependency Graph

### Core Dependencies

```
app.py
├── src.auth.basic_auth (Dash-Auth)
├── src.core.cache (flask-caching)
└── src.layout (Main layout)
    ├── src.components.sidebar
    └── src.pages.* (Dash Pages)

src/data/parquet_reader.py
├── boto3 (S3)
├── pyarrow (Parquet)
└── pandas (DataFrame)

src/core/cache.py
└── flask_caching

src/charts/templates.py
└── plotly

backend/etl/base_etl.py
├── src.data.* (Data utilities)
└── boto3
```

## Caching Strategy

- **Layer**: TTL-based in-memory cache (flask-caching)
- **TTL**: 300-3600 seconds (configurable per dataset)
- **Key**: `<dataset_id>_<filter_hash>`
- **Fallback**: Direct S3 Parquet read on cache miss

## Authentication Flow

1. User accesses dashboard
2. Dash-Auth middleware intercepts request
3. Basic Auth check (username/password from .env)
4. If authenticated: Render page
5. If not: Redirect to login

## Phase 2: LLM Integration

```
Chat Input (Vertex AI)
    ↓
[Context Assembly]
  - Dataset summary (schema, statistics)
  - Sample rows
  - Available filters
    ↓
[Prompt Engineering]
    ↓
[Vertex AI Gemini API Call]
    ↓
[Response Parsing]
  - Extract Python code
  - Extract visualization params
    ↓
[Sandbox Execution]
  - Safe Python environment
  - Limited to query operations
    ↓
[Result Rendering]
```

## Phase 3: SAML Authentication

```
Original Basic Auth
    ↓
SAML IdP Integration
    ↓
Role-based Access Control
    ↓
Per-page Authorization
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Plotly Dash + Bootstrap | Interactive dashboards |
| UI Components | Dash Bootstrap Components | Responsive UI |
| Server | Flask (Gunicorn) | WSGI server |
| Authentication | Dash-Auth (Basic) | User verification |
| Caching | flask-caching | Performance optimization |
| Data Processing | Pandas, PyArrow | DataFrame operations |
| Data Storage | Parquet (S3) | Columnar storage |
| Cloud Storage | boto3 | AWS S3 integration |
| Visualization | Plotly | Interactive charts |
| Logging | structlog | Structured logging |
| ETL Framework | Custom (base_etl.py) | Data transformation |
| LLM (Phase 2) | Vertex AI SDK | Gemini integration |
| Type Checking | Pydantic | Data validation |

## Deployment Architecture

### Development (Docker Compose)

```
Host
├── Dash App (port 8050)
├── MinIO (port 9001) - S3 mock
└── PostgreSQL (port 5432) - optional
```

### Production (AWS)

```
ALB
├── ECS Cluster (Fargate)
│   └── Dash App (Gunicorn + Flask)
├── S3 (Parquet data)
├── RDS (Data source)
└── CloudWatch (Logging)
```

## Security Considerations

1. **Authentication**: Basic Auth (local dev) → SAML (production)
2. **S3 Access**: IAM roles (production) vs. credentials (dev)
3. **Environment Variables**: AWS Secrets Manager (production)
4. **Code Sandbox**: Restricted Python execution (Phase 2)
5. **Input Validation**: Pydantic models throughout
