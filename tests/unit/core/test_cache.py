"""Tests for TTL cache."""
import pytest
import pandas as pd
from flask import Flask
from src.core.cache import init_cache, get_cached_dataset
from src.data.parquet_reader import ParquetReader
from tests.conftest import upload_parquet_to_s3


@pytest.fixture
def flask_app():
    """Flask app for cache testing."""
    app = Flask(__name__)
    init_cache(app)
    return app


def test_cache_hit(mock_s3, flask_app, sample_df):
    """Test: Cache hit returns cached DataFrame."""
    # Given: Dataset uploaded and cached
    dataset_id = "test_dataset"
    s3_key = f"datasets/{dataset_id}/data/part-0000.parquet"
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key, sample_df)

    reader = ParquetReader()

    with flask_app.app_context():
        # First call: cache miss, should read from S3
        df1 = get_cached_dataset(reader, dataset_id)

        # Second call: cache hit, should return cached data
        df2 = get_cached_dataset(reader, dataset_id)

        # Then: Both should be equal
        pd.testing.assert_frame_equal(df1, df2)


def test_cache_key_by_dataset_id(mock_s3, flask_app, sample_df):
    """Test: Cache key is based on dataset_id only."""
    # Given: Two different datasets
    dataset_id1 = "dataset1"
    dataset_id2 = "dataset2"
    s3_key1 = f"datasets/{dataset_id1}/data/part-0000.parquet"
    s3_key2 = f"datasets/{dataset_id2}/data/part-0000.parquet"

    df1 = sample_df.copy()
    df2 = sample_df.copy()
    df2["extra"] = [1, 2, 3]

    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key1, df1)
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key2, df2)

    reader = ParquetReader()

    with flask_app.app_context():
        # When: Reading both datasets
        result1 = get_cached_dataset(reader, dataset_id1)
        result2 = get_cached_dataset(reader, dataset_id2)

        # Then: Different DataFrames are returned
        assert len(result1.columns) != len(result2.columns)
