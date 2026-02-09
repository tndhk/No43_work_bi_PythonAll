"""Data layer for BI Dashboard.

This package provides data access, filtering, and S3/Parquet operations:

- parquet_reader: Read Parquet datasets from S3/MinIO
- s3_client: S3 client wrapper for data storage
- filter_engine: Apply filters to DataFrames
- data_source_registry: Resolve dataset IDs from YAML configs
- csv_parser: Parse CSV files for ETL
- dataset_summarizer: Summarize dataset schemas
- type_inferrer: Infer column types from data
- models: Data models (ColumnSchema)
- config: Pydantic configuration
"""
