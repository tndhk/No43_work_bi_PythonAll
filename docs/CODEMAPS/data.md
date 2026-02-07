# Data Layer Codemap

Last Updated: 2026-02-07
Runtime: Python 3.x / pandas / pyarrow / boto3
Entry Points: `src/data/parquet_reader.py`, `src/data/filter_engine.py`

## Directory Structure

```
src/data/
  __init__.py
  config.py                  # Pydantic settings (env vars)
  s3_client.py               # boto3 S3 client factory
  parquet_reader.py          # S3 Parquet reader (partition-aware)
  data_loader.py             # Common dataset loader via registry
  data_source_registry.py    # YAML-based chart->dataset resolver
  filter_engine.py           # DataFrame filter primitives
  csv_parser.py              # CSV parsing with encoding detection
  type_inferrer.py           # Column type inference + application
  dataset_summarizer.py      # Dataset metadata/statistics generator
  models.py                  # ColumnSchema dataclass
```

## Key Classes and Functions

### config.py

```python
class Settings(BaseSettings):   # Pydantic
    s3_endpoint, s3_region, s3_bucket, s3_access_key, s3_secret_key
    basic_auth_username, basic_auth_password
    secret_key
    auth_provider_type
    domo_client_id, domo_client_secret

settings = Settings()           # Singleton, reads from .env
```

### s3_client.py

```python
def get_s3_client() -> boto3.client
    # Uses settings.s3_endpoint, s3_region, s3_access_key, s3_secret_key
```

### parquet_reader.py

```python
class ParquetReader:
    read_dataset(dataset_id, date_range=None) -> DataFrame
    list_datasets() -> list[str]
    # Internal:
    _has_partitions(dataset_id) -> bool
    _list_partitions(dataset_id) -> list[str]
    _read_partitioned(dataset_id, date_range) -> DataFrame
    _read_single(dataset_id) -> DataFrame
    _read_file(s3_path) -> DataFrame
```

### data_source_registry.py

```python
load_dashboard_config(dashboard_id) -> dict       # @lru_cache(128)
get_dataset_id(dashboard_id, chart_id) -> str|None
resolve_dataset_id(dashboard_id, chart_id, fallback=None) -> str
    # Returns dataset_id or fallback; raises ValueError if both None
```

Config path: `src/pages/{dashboard_id}/data_sources.yml`

### filter_engine.py

```python
@dataclass(frozen=True)
class CategoryFilter:
    column: str
    values: list[str]
    include_null: bool = False

@dataclass(frozen=True)
class DateRangeFilter:
    column: str
    start_date: str   # ISO 8601
    end_date: str     # ISO 8601

@dataclass              # Mutable (not frozen)
class FilterSet:
    category_filters: list[CategoryFilter]
    date_filters: list[DateRangeFilter]

def apply_filters(df, filter_set) -> DataFrame
    # Category: isin(values), optional isna()
    # Date: start <= col <= end (end at 23:59:59)
    # Multiple filters: AND

def extract_unique_values(df, column) -> list
    # Sorted unique non-NaN values; empty list if column missing
```

### data_loader.py

```python
def load_dataset_for_chart(reader, dashboard_id, chart_id) -> DataFrame
    # Resolves dataset_id via registry, then reads through cache
```

### csv_parser.py

```python
@dataclass(frozen=True)
class CsvImportOptions:
    encoding, delimiter, has_header, null_values

def detect_encoding(file_bytes) -> str
    # chardet + Japanese encoding corrections (cp932, shift_jis)

def parse_preview(file_bytes, max_rows=1000, options=None) -> DataFrame
def parse_full(file_bytes, options=None) -> DataFrame
```

### type_inferrer.py

```python
def infer_column_type(series) -> str
    # Returns: "datetime", "date", "bool", "int64", "float64", "string"
    # Checks in specificity order; samples 1000 rows for large series

def infer_schema(df) -> list[ColumnSchema]
def apply_types(df, schema) -> DataFrame  # Immutable (returns copy)
```

### dataset_summarizer.py

```python
@dataclass
class DatasetSummary:
    name, schema, row_count, column_count, sample_rows, statistics

class DatasetSummarizer:
    summarize(dataset_id, name, max_sample_rows=5) -> DatasetSummary
    generate_summary(dataset_id) -> dict
        # schema + statistics + row/column counts (limited to 1000 rows)
```

### models.py

```python
@dataclass
class ColumnSchema:
    name: str
    data_type: str
    nullable: bool = False
    description: Optional[str] = None
```

### exceptions (src/exceptions.py)

```python
class DatasetFileNotFoundError(RuntimeError):
    s3_path: str
    dataset_id: Optional[str]
```

## Module Dependency Graph

```
src/data/config.py (leaf -- Pydantic, reads .env)
  ^
  |
src/data/s3_client.py
  ^
  |
src/data/parquet_reader.py
  ^         ^
  |         |
  |    src/data/dataset_summarizer.py
  |
src/core/cache.py (get_cached_dataset)
  ^
  |
src/data/data_loader.py <-- src/data/data_source_registry.py
  ^                                   ^
  |                                   |
  +--- src/pages/*/data_loader.py ----+
```

Filter engine is standalone:
```
src/data/filter_engine.py (no internal deps, uses pandas only)
  ^
  |
src/pages/cursor_usage/_data_loader.py
src/pages/apac_dot_due_date/_data_loader.py
```

CSV/type pipeline:
```
src/data/csv_parser.py (chardet, pandas)
  ^
  |
src/data/type_inferrer.py (models.ColumnSchema)
  ^         ^
  |         |
backend/etl/etl_csv.py   backend/etl/etl_domo.py
```

## Data Flow (Read Path)

```
Page callback triggered
  |
  v
Page _data_loader.load_and_filter_data()
  |
  +-- resolve_dataset_id(DASHBOARD_ID, CHART_ID, fallback=DATASET_ID)
  |     |
  |     +-- load_dashboard_config() --> reads data_sources.yml
  |     +-- get_dataset_id() --> chart_id -> dataset_id
  |
  +-- get_cached_dataset(reader, dataset_id)
  |     |
  |     +-- cache.get(key) --> hit? return DataFrame
  |     +-- miss: reader.read_dataset(dataset_id)
  |     |     +-- _has_partitions()?
  |     |     |    Yes -> _read_partitioned() -> pd.concat(parts)
  |     |     |    No  -> _read_single()
  |     |     +-- _read_file() -> pyarrow.parquet -> DataFrame
  |     +-- cache.set(key, df)
  |
  +-- (optional) timezone strip: dt.tz_convert(None)
  |
  +-- FilterSet construction
  |     +-- CategoryFilter(column=COLUMN_MAP[key], values=selection)
  |     +-- DateRangeFilter(column=..., start=..., end=...)
  |
  +-- apply_filters(df, filter_set) --> filtered DataFrame
  |
  v
Return to callback for chart/table rendering
```

## Data Flow (Write Path / ETL)

```
CLI Script (load_csv.py / load_domo.py)
  |
  +-- Load YAML config (csv_datasets.yaml / domo_datasets.yaml)
  |
  +-- For each enabled dataset:
  |     +-- ETL.extract()
  |     |     CSV: resolve_csv_path() -> open file -> csv_parser.parse_full()
  |     |     DOMO: OAuth2 token -> GET /datasets/{id}/data -> pd.read_csv()
  |     |
  |     +-- ETL.transform()
  |     |     type_inferrer.infer_schema() + apply_types()
  |     |     DOMO: optional exclude_filter
  |     |
  |     +-- ETL.load()
  |           pyarrow.Table.from_pandas() -> pq.write_table() -> s3.put_object()
  |           Non-partitioned: datasets/{id}/data/part-0000.parquet
  |           Partitioned:     datasets/{id}/partitions/date=.../part-0000.parquet
```

## Caching Strategy

- Backend: `flask_caching.Cache` (SimpleCache, 300s TTL)
- Cache key: `dataset:{dataset_id}` (filter-independent)
- Filters applied in-memory on the cached full DataFrame
- No cache in standalone ETL scripts (direct `reader.read_dataset()`)

## Testing

| File | Coverage |
|------|----------|
| `tests/unit/data/test_config.py` | Settings loading |
| `tests/unit/data/test_parquet_reader.py` | Single-file reads |
| `tests/unit/data/test_parquet_reader_partition.py` | Partitioned reads |
| `tests/unit/data/test_filter_engine.py` | Category/date filters + extract_unique_values |
| `tests/unit/data/test_data_source_registry.py` | Registry resolution + resolve_dataset_id |
| `tests/unit/data/test_csv_parser.py` | Encoding detection + parsing |
| `tests/unit/data/test_type_inferrer.py` | Type inference logic |
| `tests/unit/data/test_dataset_summarizer.py` | Summary generation |
| `tests/unit/data/test_common_data_loader.py` | load_dataset_for_chart |
| `tests/unit/core/test_cache.py` | Cache init + hit/miss |
| `tests/unit/core/test_logging.py` | Structlog config |
| `tests/unit/test_exceptions.py` | DatasetFileNotFoundError |

## Related Codemaps

- [Architecture](./architecture.md) -- System overview
- [Frontend](./frontend.md) -- Pages that consume data layer
- [Backend](./backend.md) -- ETL pipelines that produce data
