"""Tests for dataset summarizer."""
import pytest
import pandas as pd
from src.data.dataset_summarizer import DatasetSummarizer
from src.data.parquet_reader import ParquetReader
from tests.conftest import upload_parquet_to_s3


def test_generate_summary(mock_s3, sample_df):
    """Test: Dataset summary generation."""
    # Given: Dataset uploaded to S3
    dataset_id = "test_dataset"
    s3_key = f"datasets/{dataset_id}/data/part-0000.parquet"
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key, sample_df)

    # When: Generating summary
    reader = ParquetReader()
    summarizer = DatasetSummarizer(reader)
    summary = summarizer.generate_summary(dataset_id)

    # Then: Summary contains expected keys
    assert "schema" in summary
    assert "statistics" in summary
    assert "row_count" in summary
    assert "column_count" in summary


def test_generate_summary_schema(mock_s3, sample_df):
    """Test: Summary schema information."""
    # Given: Dataset uploaded
    dataset_id = "test_dataset"
    s3_key = f"datasets/{dataset_id}/data/part-0000.parquet"
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key, sample_df)

    # When: Generating summary
    reader = ParquetReader()
    summarizer = DatasetSummarizer(reader)
    summary = summarizer.generate_summary(dataset_id)

    # Then: Schema contains column information
    assert len(summary["schema"]) == len(sample_df.columns)
    assert all("name" in col for col in summary["schema"])
    assert all("dtype" in col for col in summary["schema"])
    assert all("nullable" in col for col in summary["schema"])


def test_generate_summary_statistics(mock_s3, sample_df):
    """Test: Summary statistics generation."""
    # Given: Dataset uploaded
    dataset_id = "test_dataset"
    s3_key = f"datasets/{dataset_id}/data/part-0000.parquet"
    upload_parquet_to_s3(mock_s3, "bi-datasets", s3_key, sample_df)

    # When: Generating summary
    reader = ParquetReader()
    summarizer = DatasetSummarizer(reader)
    summary = summarizer.generate_summary(dataset_id)

    # Then: Statistics contain per-column stats
    assert "statistics" in summary
    for col in sample_df.columns:
        assert col in summary["statistics"]
        assert "null_count" in summary["statistics"][col]
