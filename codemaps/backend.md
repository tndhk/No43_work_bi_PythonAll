# Backend Architecture Codemap

Generated: 2026-02-06

## Overview

The backend layer handles data extraction, transformation, and loading (ETL) operations. It reads from various data sources (APIs, S3, RDS, CSV files) and outputs clean Parquet files to S3.

## Module Dependency Map

```
backend/
├── etl/
│   ├── base_etl.py
│   │   └── Abstract base class for all ETL implementations
│   │   └── Provides: run(), validate(), transform()
│   │
│   ├── etl_api.py
│   │   ├── Imports: base_etl, data_sources.api_client
│   │   └── Transforms API responses → Parquet
│   │
│   ├── etl_s3.py
│   │   ├── Imports: base_etl, s3_client
│   │   └── Copies/transforms S3 files → Parquet
│   │
│   ├── etl_rds.py
│   │   ├── Imports: base_etl, data_sources.rds_client
│   │   └── Queries RDS → Parquet
│   │
│   └── etl_csv.py
│       ├── Imports: base_etl, src.data.csv_parser
│       └── Parses CSV → Parquet
│
└── data_sources/
    ├── api_client.py
    │   └── HTTP client for external APIs
    │
    ├── s3_client.py
    │   ├── S3 connection & file operations
    │   └── Reuses: src.data.s3_client
    │
    └── rds_client.py
        └── PostgreSQL/RDS connection pool
```

## Key Exports

### base_etl.py

```python
class BaseETL(ABC):
    - run() → None           # Execute ETL pipeline
    - validate() → bool      # Validate input data
    - extract() → DataFrame  # Abstract: extract from source
    - transform() → DataFrame # Abstract: apply transformations
    - load(df) → None        # Write to S3 Parquet
```

### etl_api.py

```python
class APIETLJob(BaseETL):
    - __init__(api_endpoint, ...)
    - extract() → DataFrame  # Fetch from REST API
    - transform() → DataFrame # Parse & normalize
```

### etl_s3.py

```python
class S3ETLJob(BaseETL):
    - __init__(bucket, prefix, ...)
    - extract() → DataFrame  # Read from S3
    - transform() → DataFrame # Apply transformations
```

### etl_rds.py

```python
class RDSETLJob(BaseETL):
    - __init__(query, connection_string, ...)
    - extract() → DataFrame  # Query RDS
    - transform() → DataFrame # Clean & validate
```

### etl_csv.py

```python
class CSVETLJob(BaseETL):
    - __init__(file_path, ...)
    - extract() → DataFrame  # Read CSV
    - transform() → DataFrame # Type inference & cleaning
```

### data_sources/api_client.py

```python
class APIClient:
    - get(endpoint) → dict
    - post(endpoint, data) → dict
    - retry_logic() → with exponential backoff
```

### data_sources/rds_client.py

```python
class RDSClient:
    - execute(query) → DataFrame
    - connect() → Connection
    - disconnect() → None
```

## Data Transformation Pipeline

```
Raw Source Data
    ↓
[extract()]
    ↓
Intermediate DataFrame
    ↓
[validate()]
    ↓
[transform()]
    ├─ Type inference
    ├─ Null handling
    ├─ Column normalization
    └─ Filtering/aggregation
    ↓
Clean DataFrame
    ↓
[load()]
    ↓
S3 Parquet Output
```

## ETL Orchestration

Typically run via:
- **cron jobs** (daily/hourly scheduled)
- **systemd timers** (alternative to cron)
- **Lambda triggers** (event-based)
- **CLI invocation** (manual testing)

Example cron entry:
```bash
0 2 * * * python /app/backend/etl/etl_api.py
0 3 * * * python /app/backend/etl/etl_rds.py
```

## Error Handling

All ETL classes inherit error handling from `BaseETL`:
- Validation errors → logs & skips batch
- Connection errors → retry with backoff
- Transform errors → detailed logging for debugging
- S3 write errors → fail fast & alert

## Testing Strategy

- Unit tests: Mock data sources, test transforms
- Integration tests: Test with real S3/RDS (in CI)
- Data quality tests: Schema validation, row counts
