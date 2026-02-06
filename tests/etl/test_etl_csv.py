"""Tests for CsvETL."""
import pytest
import pandas as pd
import tempfile
import os
from backend.etl.etl_csv import CsvETL
from tests.conftest import upload_parquet_to_s3


@pytest.fixture
def csv_file(tmp_path):
    """Create a temporary CSV file for testing."""
    csv_path = tmp_path / "test.csv"
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "amount": [100.0, 200.0, 300.0],
        "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
    })
    df.to_csv(csv_path, index=False)
    return str(csv_path)


def test_csv_etl_extract(csv_file):
    """Test: CsvETL extracts data from CSV file."""
    # Given: CsvETL instance
    etl = CsvETL(csv_file)

    # When: Extracting data
    df = etl.extract()

    # Then: DataFrame is loaded
    assert len(df) == 3
    assert "id" in df.columns
    assert "name" in df.columns


def test_csv_etl_transform(csv_file):
    """Test: CsvETL transforms data (type inference and application)."""
    # Given: CsvETL instance
    etl = CsvETL(csv_file)

    # When: Running transform
    df_extracted = etl.extract()
    df_transformed = etl.transform(df_extracted)

    # Then: Types are inferred and applied
    assert pd.api.types.is_integer_dtype(df_transformed["id"])
    assert pd.api.types.is_float_dtype(df_transformed["amount"])


def test_csv_etl_run(mock_s3, csv_file):
    """Test: CsvETL run executes full ETL flow."""
    # Given: CsvETL instance
    etl = CsvETL(csv_file)
    dataset_id = "test_dataset"

    # When: Running full ETL flow
    etl.run(dataset_id)

    # Then: Parquet file exists in S3
    s3_key = f"datasets/{dataset_id}/data/part-0000.parquet"
    response = mock_s3.head_object(Bucket="bi-datasets", Key=s3_key)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_csv_etl_run_with_partition(mock_s3, csv_file):
    """Test: CsvETL run with partition column."""
    # Given: CsvETL instance with partition column
    etl = CsvETL(csv_file, partition_column="date")
    dataset_id = "test_dataset"

    # When: Running ETL flow
    etl.run(dataset_id)

    # Then: Partitioned files exist in S3
    s3_key = f"datasets/{dataset_id}/partitions/date=2024-01-01/part-0000.parquet"
    response = mock_s3.head_object(Bucket="bi-datasets", Key=s3_key)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
