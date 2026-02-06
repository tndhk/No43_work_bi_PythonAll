"""Common pytest fixtures for test suite."""
import os
import pytest
import boto3
from moto import mock_aws
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import io


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables for all tests."""
    monkeypatch.setenv("S3_ENDPOINT", "")
    monkeypatch.setenv("S3_REGION", "ap-northeast-1")
    monkeypatch.setenv("S3_BUCKET", "bi-datasets")
    monkeypatch.setenv("S3_ACCESS_KEY", "test")
    monkeypatch.setenv("S3_SECRET_KEY", "test")


@pytest.fixture
def mock_s3():
    """Mock S3 using moto and provide a bucket-ready client."""
    with mock_aws():
        client = boto3.client("s3", region_name="ap-northeast-1")
        client.create_bucket(
            Bucket="bi-datasets",
            CreateBucketConfiguration={"LocationConstraint": "ap-northeast-1"},
        )
        yield client


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample DataFrame for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "amount": [100.0, 200.0, 300.0],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        "category": ["A", "B", "A"],
    })


def upload_parquet_to_s3(client, bucket: str, key: str, df: pd.DataFrame) -> None:
    """Helper function to upload a DataFrame as Parquet to S3."""
    table = pa.Table.from_pandas(df)
    buf = io.BytesIO()
    pq.write_table(table, buf)
    buf.seek(0)
    client.put_object(Bucket=bucket, Key=key, Body=buf.read())
