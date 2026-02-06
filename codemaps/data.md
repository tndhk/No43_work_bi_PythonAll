# Data Layer Codemap

Last Updated: 2026-02-07
Directory: `src/data/`, `src/core/`, `src/exceptions.py`

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
  Exports: CategoryFilter, DateRangeFilter, FilterSet (frozen dataclasses),
           apply_filters()

src/core/cache.py
  Imports: flask_caching, pandas, parquet_reader.ParquetReader
  Exports: cache (Cache instance), init_cache(), get_cached_dataset()

src/core/logging.py
  Imports: structlog
  Exports: setup_logging()

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

Date formats recognized:
```
Date:     %Y-%m-%d, %Y/%m/%d, %Y年%m月%d日
Datetime: %Y-%m-%d %H:%M:%S, %Y-%m-%dT%H:%M:%S, %Y/%m/%d %H:%M:%S
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

@dataclass(frozen=True)
class FilterSet:
    category_filters: list[CategoryFilter] = []
    date_filters: list[DateRangeFilter] = []

def apply_filters(df, filter_set) -> pd.DataFrame
    # Category: isin(values), optional include_null
    # Date: start_date <= col <= end_date (23:59:59 inclusive)
    # Multiple filters: AND combination
    # Returns copy (original not modified)
```

### DatasetSummarizer (dataset_summarizer.py)

```python
@dataclass
class DatasetSummary:
    name: str
    schema: list[dict]
    row_count: int
    column_count: int
    sample_rows: list[dict]
    statistics: dict

class DatasetSummarizer:
    __init__(parquet_reader: ParquetReader)

    summarize(dataset_id, name, max_sample_rows=5) -> DatasetSummary
        # Schema + sample rows + per-column stats (numeric/categorical)

    generate_summary(dataset_id) -> dict
        # Lighter version: schema + statistics + counts (max 1000 rows)
        # Numeric: min, max, mean, std
        # String: unique_count, top_values (top 10)
        # Datetime: min, max (ISO strings)
```

### ColumnSchema (models.py)

```python
@dataclass
class ColumnSchema:
    name: str
    data_type: str
    nullable: bool = False
    description: Optional[str] = None
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
tests/unit/core/
  test_cache.py                  # Cache hit/miss behavior
  test_logging.py                # structlog configuration
tests/unit/
  test_exceptions.py             # DatasetFileNotFoundError
```

## Related Codemaps

- `codemaps/backend.md` -- ETL classes that write data via this layer
- `codemaps/frontend.md` -- Pages that read data via this layer
- `codemaps/architecture.md` -- System overview
