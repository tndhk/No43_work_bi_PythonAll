"""Tests for ParquetReader (smoke test for foundation)."""
import pytest
from src.data.parquet_reader import ParquetReader
from tests.conftest import upload_parquet_to_s3


def test_read_dataset_smoke(mock_s3, sample_df):
    """Smoke test: Read a dataset from S3."""
    # Given: Parquet file uploaded to S3
    dataset_id = "test_dataset"
    s3_key = f"datasets/{dataset_id}/data/part-0000.parquet"
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key, sample_df)

    # When: Reading the dataset
    reader = ParquetReader()
    result = reader.read_dataset(dataset_id)

    # Then: DataFrame is returned correctly
    assert isinstance(result, type(sample_df))
    assert len(result) == len(sample_df)
    assert list(result.columns) == list(sample_df.columns)
