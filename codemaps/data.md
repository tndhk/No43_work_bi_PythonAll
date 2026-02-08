# Data Layer Codemap

Last Updated: 2026-02-08
Freshness: 2026-02-08T15:30:00Z
Directory: `src/data/`, `src/core/`, `src/utils/`, `src/exceptions.py`

## Module Dependency Graph

```
src/data/config.py
  Imports: pydantic_settings, secrets
  Exports: Settings (BaseSettings), settings (global instance)

src/data/s3_client.py
  Imports: boto3, config.settings
  Exports: get_s3_client() -> boto3.client

src/data/models.py
  Imports: dataclasses
  Exports: ColumnSchema (dataclass)

src/data/parquet_reader.py
  Imports: pandas, pyarrow.parquet, botocore,
           s3_client.get_s3_client, config.settings,
           exceptions.DatasetFileNotFoundError
  Exports: ParquetReader (class)

src/data/csv_parser.py
  Imports: chardet, pandas
  Exports: CsvImportOptions (frozen dataclass),
           detect_encoding(), parse_preview(), parse_full()

src/data/type_inferrer.py
  Imports: pandas, datetime, models.ColumnSchema
  Exports: infer_column_type(), infer_schema(), apply_types()

src/data/dataset_summarizer.py
  Imports: pandas, numpy, parquet_reader.ParquetReader
  Exports: DatasetSummary (dataclass), DatasetSummarizer (class)

src/data/filter_engine.py
  Imports: pandas, datetime
  Exports: CategoryFilter, DateRangeFilter, FilterSet (dataclasses),
           apply_filters(), extract_unique_values()

src/data/data_source_registry.py
  Imports: yaml, pathlib.Path, functools.lru_cache
  Exports: load_dashboard_config(), get_dataset_id(), resolve_dataset_id()

src/data/data_loader.py
  Imports: pandas, core.cache.get_cached_dataset,
           parquet_reader.ParquetReader, data_source_registry.get_dataset_id
  Exports: load_dataset_for_chart()

src/core/cache.py
  Imports: flask_caching, pandas, parquet_reader.ParquetReader
  Exports: cache (Cache instance), init_cache(), get_cached_dataset()

src/core/logging.py
  Imports: structlog
  Exports: setup_logging()

src/utils/data_helpers.py
  Imports: parquet_reader, cache, filter_engine, data_source_registry
  Exports: safe_load_filter_options(), strip_timezone(),
           resolve_single_dataset_id()

src/utils/filter_helpers.py
  Imports: filter_engine (FilterSet, CategoryFilter, DateRangeFilter)
  Exports: build_filter_set_from_map()

src/exceptions.py
  Exports: DatasetFileNotFoundError(RuntimeError)
```

## Key Classes and Functions

### Settings (config.py)

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    s3_endpoint: Optional[str]
    s3_region: str = "ap-northeast-1"
    s3_bucket: str = "bi-datasets"
    s3_access_key: Optional[str]
    s3_secret_key: Optional[str]
    basic_auth_username: str = "admin"
    basic_auth_password: str = "changeme"
    secret_key: str            # auto-generated
    auth_provider_type: str = "form"
    domo_client_id: Optional[str]
    domo_client_secret: Optional[str]

settings = Settings()  # Global singleton
```

### Dataset Registry (data_source_registry.py)

```python
def load_dashboard_config(dashboard_id: str) -> dict
    # Reads src/pages/{dashboard_id}/data_sources.yml
    # Validates "charts" mapping; lru_cache(128)

def get_dataset_id(dashboard_id: str, chart_id: str) -> Optional[str]
    # Returns dataset_id for chart_id, or None if not found

def resolve_dataset_id(dashboard_id, chart_id, fallback=None) -> str
    # Like get_dataset_id but raises ValueError when not found (unless fallback)
```

### Common Loader (data_loader.py)

```python
def load_dataset_for_chart(reader: ParquetReader, dashboard_id: str, chart_id: str) -> pd.DataFrame
    # Resolves dataset_id via registry
    # Loads dataset via get_cached_dataset
```

### ParquetReader (parquet_reader.py)

```python
class ParquetReader:
    __init__()
        # Creates S3 client and reads bucket from settings

    read_dataset(dataset_id, date_range=None) -> pd.DataFrame
        # Auto-detects partition vs single file
        # date_range: Optional[tuple[str, str]] for partition pruning

    list_datasets() -> list[str]
        # Lists dataset IDs under datasets/ prefix

    # Internal methods:
    _has_partitions(dataset_id) -> bool
    _list_partitions(dataset_id) -> list[str]
    _read_partitioned(dataset_id, date_range) -> pd.DataFrame
    _read_single(dataset_id) -> pd.DataFrame
    _read_file(s3_path) -> pd.DataFrame
```

S3 path resolution:
```
read_dataset("my-data")
  -> _has_partitions("my-data")
     Check: datasets/my-data/partitions/ exists?
  -> Yes: _read_partitioned (concat matching date= partitions)
  -> No:  _read_single (datasets/my-data/data/part-0000.parquet)
```

### CsvImportOptions / parse functions (csv_parser.py)

```python
@dataclass(frozen=True)
class CsvImportOptions:
    encoding: Optional[str] = None   # Auto-detect if None
    delimiter: str = ","
    has_header: bool = True
    null_values: list[str] = []

def detect_encoding(file_bytes) -> str
    # chardet + Japanese encoding corrections (ASCII->UTF-8, ISO-8859-1->CP932)

def parse_preview(file_bytes, max_rows=1000, options=None) -> pd.DataFrame
def parse_full(file_bytes, options=None) -> pd.DataFrame
```

### Type Inference (type_inferrer.py)

```python
def infer_column_type(series) -> str
    # Returns: "datetime" | "date" | "bool" | "int64" | "float64" | "string"
    # Priority: datetime > date > bool > int64 > float64 > string
    # Samples 1000 rows for large series

def infer_schema(df) -> List[ColumnSchema]
    # Returns ColumnSchema per column (name, data_type, nullable)

def apply_types(df, schema) -> pd.DataFrame
    # Applies inferred types to DataFrame copy (immutable operation)
```

### Filter Engine (filter_engine.py)

```python
@dataclass(frozen=True)
class CategoryFilter:
    column: str
    values: list[str]
    include_null: bool = False

@dataclass(frozen=True)
class DateRangeFilter:
    column: str
    start_date: str  # ISO 8601
    end_date: str    # ISO 8601

@dataclass
class FilterSet:
    category_filters: list[CategoryFilter] = field(default_factory=list)
    date_filters: list[DateRangeFilter] = field(default_factory=list)

def apply_filters(df, filter_set) -> pd.DataFrame
    # Category: isin(values), optional include_null
    # Date: start_date <= col <= end_date (23:59:59 inclusive)
    # Multiple filters: AND combination
    # Returns copy (original not modified)

def extract_unique_values(df, column) -> list
    # Sorted unique values excluding NaN/None
    # Returns [] if column missing
```

Note: FilterSet changed from `frozen=True` to mutable `@dataclass` to support
`build_filter_set_from_map()` which appends filters to lists.

### Shared Helpers (src/utils/)

```python
# data_helpers.py
def safe_load_filter_options(reader, dataset_id, extract_columns, prepare_fn=None) -> dict
    # Load unique values from specified columns, with empty-list defaults on error

def strip_timezone(df, column) -> pd.DataFrame
    # Convert UTC-aware datetime column to timezone-naive (Parquet compatibility)

def resolve_single_dataset_id(dashboard_id, chart_ids) -> str
    # Validate all charts use same dataset; raise ValueError if mismatch

# filter_helpers.py
def build_filter_set_from_map(column_map, filter_pairs, date_range=None) -> FilterSet
    # Build FilterSet from column_map keys + (key, values) pairs
    # Reduces boilerplate in page _data_loader modules
```

### DatasetSummarizer (dataset_summarizer.py)

```python
@dataclass
class DatasetSummary:
    name, schema, row_count, column_count, sample_rows, statistics

class DatasetSummarizer:
    __init__(parquet_reader: ParquetReader)
    summarize(dataset_id, name, max_sample_rows=5) -> DatasetSummary
    generate_summary(dataset_id) -> dict
```

### Cache (core/cache.py)

```python
cache = Cache()  # Flask-Caching instance

def init_cache(server) -> None
    # SimpleCache, 300s TTL

def get_cached_dataset(reader: ParquetReader, dataset_id: str) -> pd.DataFrame
    # Cache key: "dataset:{dataset_id}"
    # Miss: reader.read_dataset(dataset_id)
```

### Exceptions (exceptions.py)

```python
class DatasetFileNotFoundError(RuntimeError):
    __init__(s3_path: str, dataset_id: Optional[str] = None)
    # Attributes: s3_path, dataset_id
```

## Data Flow (Read Path)

```
Page callback
  |
  data_source_registry.resolve_dataset_id(dashboard_id, chart_id)
  |
  get_cached_dataset(reader, dataset_id)
  |
  [Cache hit?]
  |
  No -> ParquetReader.read_dataset(dataset_id)
  |       |
  |       [Partitioned?]
  |       |
  |       Yes -> concat(date= partitions)
  |       No  -> read single file
  |
  pd.DataFrame
  |
  [Page-specific prep: tz strip, derived columns, month normalization]
  |
  build_filter_set_from_map(column_map, filter_pairs) -> FilterSet
  |
  apply_filters(df, FilterSet)
  |
  Filtered DataFrame -> Charts / Tables / KPIs
```

## Data Flow (Write Path)

```
ETL script
  |
  BaseETL.extract() -> raw DataFrame
  |
  BaseETL.transform() -> clean DataFrame
  |  (type inference + exclude filter + optional HMAC masking)
  |
  BaseETL.load(df, dataset_id, partition_column)
  |
  [partition_column?]
  |
  Yes -> groupby(date) -> per-partition Parquet files
  No  -> single Parquet file
  |
  S3 put_object (via get_s3_client)
```

## S3 Path Conventions

```
s3://{bucket}/
  datasets/
    {dataset_id}/
      data/
        part-0000.parquet         # Non-partitioned
      partitions/
        date=2026-01-01/
          part-0000.parquet       # Partitioned by date
        date=2026-01-02/
          part-0000.parquet
```

## Active Datasets

| Dataset ID | Source | Partition | Used By |
|------------|--------|-----------|---------|
| cursor-usage | CSV (local) | Date | Cursor Usage page |
| apac-dot-due-date | DOMO API | delivery completed date | APAC DOT page (reference) |
| apac-dot-ddd-change-issue-sql | DOMO API | edit month | APAC DOT page (change+issue) |
| hamm-dashboard | DOMO API | (none) | Hamm Overview page |

## Testing

```
tests/unit/data/
  test_config.py                 # Settings loading
  test_csv_parser.py             # Encoding detection, parse_preview, parse_full
  test_type_inferrer.py          # Column type inference edge cases
  test_dataset_summarizer.py     # Summary generation
  test_filter_engine.py          # Category/date filtering
  test_parquet_reader.py         # Single file reading (moto)
  test_parquet_reader_partition.py # Partitioned reading (moto)
  test_data_source_registry.py   # Dashboard config registry
  test_common_data_loader.py     # Registry-backed loader

tests/unit/core/
  test_cache.py                  # Cache hit/miss behavior
  test_logging.py                # structlog configuration

tests/unit/utils/
  test_data_helpers.py           # safe_load_filter_options, strip_timezone, resolve_single_dataset_id
  test_filter_helpers.py         # build_filter_set_from_map

tests/unit/
  test_exceptions.py             # DatasetFileNotFoundError
  test_layout.py                 # create_layout
```

## Related Codemaps

- `codemaps/backend.md` -- ETL classes that write data via this layer
- `codemaps/frontend.md` -- Pages that read data via this layer
- `codemaps/architecture.md` -- System overview
