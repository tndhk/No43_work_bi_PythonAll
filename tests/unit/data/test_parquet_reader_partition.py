"""Tests for ParquetReader partition support."""
import pytest
from datetime import datetime
from src.data.parquet_reader import ParquetReader
from src.exceptions import DatasetFileNotFoundError
from tests.conftest import upload_parquet_to_s3


def test_has_partitions_non_partitioned(mock_s3, sample_df):
    """Test: _has_partitions returns False for non-partitioned dataset."""
    # Given: Non-partitioned dataset
    dataset_id = "test_dataset"
    s3_key = f"datasets/{dataset_id}/data/part-0000.parquet"
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key, sample_df)

    # When: Checking for partitions
    reader = ParquetReader()

    # Then: Returns False
    assert reader._has_partitions(dataset_id) is False


def test_has_partitions_partitioned(mock_s3, sample_df):
    """Test: _has_partitions returns True for partitioned dataset."""
    # Given: Partitioned dataset
    dataset_id = "test_dataset"
    s3_key1 = f"datasets/{dataset_id}/partitions/date=2024-01-01/part-0000.parquet"
    s3_key2 = f"datasets/{dataset_id}/partitions/date=2024-01-02/part-0000.parquet"
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key1, sample_df)
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key2, sample_df)

    # When: Checking for partitions
    reader = ParquetReader()

    # Then: Returns True
    assert reader._has_partitions(dataset_id) is True


def test_list_partitions(mock_s3, sample_df):
    """Test: _list_partitions returns list of partition dates."""
    # Given: Partitioned dataset
    dataset_id = "test_dataset"
    s3_key1 = f"datasets/{dataset_id}/partitions/date=2024-01-01/part-0000.parquet"
    s3_key2 = f"datasets/{dataset_id}/partitions/date=2024-01-02/part-0000.parquet"
    s3_key3 = f"datasets/{dataset_id}/partitions/date=2024-01-03/part-0000.parquet"
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key1, sample_df)
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key2, sample_df)
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key3, sample_df)

    # When: Listing partitions
    reader = ParquetReader()
    partitions = reader._list_partitions(dataset_id)

    # Then: Returns sorted list of dates
    assert set(partitions) == {"2024-01-01", "2024-01-02", "2024-01-03"}


def test_read_partitioned_all(mock_s3, sample_df):
    """Test: _read_partitioned reads all partitions when date_range is None."""
    # Given: Partitioned dataset with 3 partitions
    dataset_id = "test_dataset"
    df1 = sample_df.copy()
    df2 = sample_df.copy()
    df3 = sample_df.copy()

    s3_key1 = f"datasets/{dataset_id}/partitions/date=2024-01-01/part-0000.parquet"
    s3_key2 = f"datasets/{dataset_id}/partitions/date=2024-01-02/part-0000.parquet"
    s3_key3 = f"datasets/{dataset_id}/partitions/date=2024-01-03/part-0000.parquet"
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key1, df1)
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key2, df2)
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key3, df3)

    # When: Reading without date_range
    reader = ParquetReader()
    result = reader._read_partitioned(dataset_id, date_range=None)

    # Then: All partitions are combined
    assert len(result) == len(df1) * 3


def test_read_partitioned_with_range(mock_s3, sample_df):
    """Test: _read_partitioned reads only partitions in date_range."""
    # Given: Partitioned dataset with 5 partitions
    dataset_id = "test_dataset"
    for i in range(1, 6):
        date_str = f"2024-01-{i:02d}"
        s3_key = f"datasets/{dataset_id}/partitions/date={date_str}/part-0000.parquet"
        upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key, sample_df)

    # When: Reading with date_range (2024-01-02 to 2024-01-04)
    reader = ParquetReader()
    result = reader._read_partitioned(dataset_id, date_range=("2024-01-02", "2024-01-04"))

    # Then: Only 3 partitions are read
    assert len(result) == len(sample_df) * 3


def test_read_dataset_auto_detects_partition(mock_s3, sample_df):
    """Test: read_dataset automatically detects and reads partitioned dataset."""
    # Given: Partitioned dataset
    dataset_id = "test_dataset"
    s3_key1 = f"datasets/{dataset_id}/partitions/date=2024-01-01/part-0000.parquet"
    s3_key2 = f"datasets/{dataset_id}/partitions/date=2024-01-02/part-0000.parquet"
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key1, sample_df)
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key2, sample_df)

    # When: Reading dataset
    reader = ParquetReader()
    result = reader.read_dataset(dataset_id)

    # Then: All partitions are combined
    assert len(result) == len(sample_df) * 2


def test_read_dataset_with_date_range(mock_s3, sample_df):
    """Test: read_dataset with date_range applies partition pruning."""
    # Given: Partitioned dataset
    dataset_id = "test_dataset"
    for i in range(1, 6):
        date_str = f"2024-01-{i:02d}"
        s3_key = f"datasets/{dataset_id}/partitions/date={date_str}/part-0000.parquet"
        upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key, sample_df)

    # When: Reading with date_range
    reader = ParquetReader()
    result = reader.read_dataset(dataset_id, date_range=("2024-01-02", "2024-01-04"))

    # Then: Only filtered partitions are read
    assert len(result) == len(sample_df) * 3
