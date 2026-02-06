"""Tests for BaseETL."""
import pytest
import pandas as pd
from abc import ABC
from backend.etl.base_etl import BaseETL
from tests.conftest import upload_parquet_to_s3


class ConcreteETL(BaseETL):
    """Concrete implementation for testing."""

    def extract(self) -> pd.DataFrame:
        return pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df["col3"] = df["col1"] * 2
        return df


def test_base_etl_extract_transform(mock_s3):
    """Test: BaseETL extract and transform flow."""
    # Given: Concrete ETL implementation
    etl = ConcreteETL()

    # When: Running extract and transform
    df_extracted = etl.extract()
    df_transformed = etl.transform(df_extracted)

    # Then: Transform adds new column
    assert "col3" in df_transformed.columns
    assert len(df_transformed) == len(df_extracted)


def test_base_etl_load_non_partitioned(mock_s3, sample_df):
    """Test: BaseETL load writes non-partitioned dataset to S3."""
    # Given: ETL instance and DataFrame
    etl = ConcreteETL()
    dataset_id = "test_dataset"

    # When: Loading to S3
    etl.load(sample_df, dataset_id, partition_column=None)

    # Then: File exists in S3
    s3_key = f"datasets/{dataset_id}/data/part-0000.parquet"
    response = mock_s3.head_object(Bucket="bi-datasets", Key=s3_key)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_base_etl_load_partitioned(mock_s3):
    """Test: BaseETL load writes partitioned dataset to S3."""
    # Given: ETL instance and DataFrame with date column
    etl = ConcreteETL()
    df = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-01"]),
        "value": [1, 2, 3],
    })
    dataset_id = "test_dataset"

    # When: Loading with partition column
    etl.load(df, dataset_id, partition_column="date")

    # Then: Partitioned files exist in S3
    s3_key1 = f"datasets/{dataset_id}/partitions/date=2024-01-01/part-0000.parquet"
    s3_key2 = f"datasets/{dataset_id}/partitions/date=2024-01-02/part-0000.parquet"
    response1 = mock_s3.head_object(Bucket="bi-datasets", Key=s3_key1)
    response2 = mock_s3.head_object(Bucket="bi-datasets", Key=s3_key2)
    assert response1["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert response2["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_base_etl_run(mock_s3):
    """Test: BaseETL run executes extract -> transform -> load."""
    # Given: ETL instance
    etl = ConcreteETL()
    dataset_id = "test_dataset"

    # When: Running full ETL flow
    etl.run(dataset_id)

    # Then: File exists in S3
    s3_key = f"datasets/{dataset_id}/data/part-0000.parquet"
    response = mock_s3.head_object(Bucket="bi-datasets", Key=s3_key)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
