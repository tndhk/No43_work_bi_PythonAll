# Data Layer Architecture Codemap

Generated: 2026-02-06

## Overview

The data layer handles all operations related to data access, transformation, validation, and caching. It abstracts away S3/Parquet complexity and provides clean interfaces for the frontend and ETL layers.

## Module Dependency Map

```
src/data/
├── config.py
│   ├── Settings (Pydantic)
│   └── Environment variable management
│
├── s3_client.py
│   ├── boto3 S3 client wrapper
│   └── Exports: get_s3_client()
│
├── parquet_reader.py
│   ├── Imports: s3_client, pyarrow, pandas
│   ├── Partition support
│   └── Exports: read_parquet(), list_datasets()
│
├── csv_parser.py
│   ├── Imports: pandas, chardet
│   ├── CSV reading with encoding detection
│   └── Exports: parse_csv(), guess_delimiter()
│
├── type_inferrer.py
│   ├── Column type inference (int, float, str, date)
│   └── Exports: infer_types(), convert_column()
│
├── dataset_summarizer.py
│   ├── Imports: pandas
│   ├── Data profiling & statistics
│   └── Exports: summarize_dataset(), get_column_stats()
│
├── filter_engine.py
│   ├── Filter logic implementation
│   ├── Category, date range, custom predicates
│   └── Exports: apply_filters()
│
└── models.py
    ├── Pydantic models for validation
    ├── DatasetMetadata, FilterSpec, etc.
    └── Type-safe data structures
```

## Key Modules & Functions

### config.py

```python
class Settings(BaseSettings):
    s3_endpoint: str
    s3_region: str
    s3_bucket: str
    s3_access_key: str
    s3_secret_key: str
    basic_auth_username: str
    basic_auth_password: str
    # ... (Phase 2/3)

settings: Settings  # Global instance
```

### s3_client.py

```python
def get_s3_client() → boto3.client
    # Returns configured S3 client
```

### parquet_reader.py

```python
def read_parquet(
    s3_path: str,
    columns: Optional[List[str]] = None,
    filters: Optional[List[tuple]] = None,
) → pd.DataFrame
    # Read Parquet from S3 with optional column/row filtering

def list_datasets(prefix: str) → List[str]
    # List available Parquet files in S3

def get_partition_columns(s3_path: str) → List[str]
    # Extract partition columns from Parquet schema
```

### csv_parser.py

```python
def parse_csv(
    file_content: bytes,
    encoding: Optional[str] = None,
) → pd.DataFrame
    # Parse CSV with auto-encoding detection

def guess_delimiter(content: str) → str
    # Detect delimiter (,/;/\t)

def guess_encoding(content: bytes) → str
    # Detect encoding (UTF-8/Shift-JIS/etc.)
```

### type_inferrer.py

```python
def infer_types(df: pd.DataFrame) → Dict[str, type]
    # Returns {column_name: inferred_type}
    # Types: int, float, str, datetime, bool, category

def convert_column(series: pd.Series, target_type: str) → pd.Series
    # Convert column to target type with error handling
```

### dataset_summarizer.py

```python
class DatasetSummary:
    name: str
    row_count: int
    columns: List[ColumnMetadata]
    memory_usage: int
    
class ColumnMetadata:
    name: str
    dtype: str
    null_count: int
    unique_count: int
    min_value: Optional[Any]
    max_value: Optional[Any]
    top_values: List[tuple]  # (value, count)

def summarize_dataset(df: pd.DataFrame) → DatasetSummary
    # Generate comprehensive dataset profile

def get_column_stats(
    df: pd.DataFrame,
    column: str,
) → ColumnMetadata
    # Get statistics for specific column
```

### filter_engine.py

```python
class FilterSpec:
    column: str
    operator: str  # "eq", "in", "gt", "lt", "between", "contains"
    value: Any

def apply_filters(
    df: pd.DataFrame,
    filters: List[FilterSpec],
) → pd.DataFrame
    # Apply all filters to DataFrame
    
    # Supported operators:
    # - "eq": equality
    # - "in": membership
    # - "gt", "lt", "gte", "lte": comparisons
    # - "between": range
    # - "contains": substring (string columns)
    # - "startswith", "endswith": string patterns
```

### models.py

```python
class DatasetRef(BaseModel):
    s3_path: str
    partition_columns: List[str]
    
class FilterRequest(BaseModel):
    filters: List[FilterSpec]
    sort_by: Optional[str]
    limit: Optional[int]
    
class DatasetMetadata(BaseModel):
    name: str
    schema: Dict[str, str]
    last_updated: datetime
    row_count: int
```

## Data Type Support

Supported column types for inference & conversion:

| Type | Detection Method | Examples |
|------|-----------------|----------|
| int | Regex `/^\d+$/` | `123`, `-456` |
| float | Regex `/^\d*\.?\d+([eE][+-]?\d+)?$/` | `1.5`, `1e-3` |
| datetime | Parse with multiple formats | `2026-02-06`, `2026/02/06 10:30` |
| bool | Case-insensitive `true/false` | `true`, `FALSE`, `1`, `0` |
| category | Unique count < threshold | Enum columns |
| str | Default fallback | Text fields |

## Caching Integration

Located in `src/core/cache.py`:

```python
@cache.cached(timeout=300, key_prefix="dataset_")
def read_parquet_cached(s3_path: str) → pd.DataFrame:
    return read_parquet(s3_path)
```

Cache key format: `dataset_{s3_path}_{filter_hash}`

## S3 Path Conventions

```
s3://bi-datasets/
├── raw/                      # Unprocessed data
│   ├── api/
│   ├── rds/
│   └── csv/
│
├── processed/                # Cleaned data (ready for BI)
│   ├── sales/
│   │   └── yearly=2026/monthly=02/
│   ├── inventory/
│   │   └── yearly=2026/monthly=02/
│   └── ...
│
└── archive/                  # Historical data (rare queries)
    └── ...
```

Partition scheme: `yearly=YYYY/monthly=MM/` for time-based data

## Performance Considerations

1. **Column Selection**: Only load necessary columns
2. **Row Filtering**: Use Parquet row group filtering
3. **Partition Pruning**: Filter before reading files
4. **Lazy Evaluation**: Keep data in Parquet until transformation
5. **Type Inference**: Cache inferred schema

Example optimization:

```python
# Bad: Load everything
df = read_parquet("s3://...")
df = df[df["region"] == "APAC"][["sales", "date"]]

# Good: Filter before loading
df = read_parquet(
    "s3://...",
    columns=["sales", "date"],
    filters=[("region", "==", "APAC")],
)
```

## Error Handling

- **S3 Errors**: Retry with exponential backoff
- **Parquet Schema Errors**: Log and skip columns
- **Type Conversion Errors**: Coerce to string
- **Missing Files**: Return empty DataFrame + warning

## Phase 2: LLM Context Building

Additional exports for LLM layer:

```python
def build_lm_context(dataset_ref: DatasetRef) → Dict:
    # Returns:
    # - schema: Column names & types
    # - statistics: Summary stats
    # - sample_data: First N rows
    # - partition_info: Partition columns & values
```

## Testing Strategy

- Unit tests: Mock S3, test parsing/inference
- Integration tests: Use moto for S3 mocking
- Performance tests: Large Parquet files
- Type inference tests: Edge cases (empty strings, nulls)
