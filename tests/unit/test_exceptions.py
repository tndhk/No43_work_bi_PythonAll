"""Tests for custom exception classes."""
import pytest
from src.exceptions import DatasetFileNotFoundError


def test_dataset_file_not_found_error_without_dataset_id():
    """Test: DatasetFileNotFoundError without dataset_id."""
    # Given: s3_path only
    s3_path = "datasets/test/data.parquet"
    
    # When: Creating exception without dataset_id
    error = DatasetFileNotFoundError(s3_path)
    
    # Then: Attributes are set correctly
    assert error.s3_path == s3_path
    assert error.dataset_id is None
    
    # Then: Message contains only s3_path
    assert str(error) == f"Dataset file not found: {s3_path}"


def test_dataset_file_not_found_error_with_dataset_id():
    """Test: DatasetFileNotFoundError with dataset_id."""
    # Given: s3_path and dataset_id
    s3_path = "datasets/test/data.parquet"
    dataset_id = "test_dataset"
    
    # When: Creating exception with dataset_id
    error = DatasetFileNotFoundError(s3_path, dataset_id)
    
    # Then: Attributes are set correctly
    assert error.s3_path == s3_path
    assert error.dataset_id == dataset_id
    
    # Then: Message contains both s3_path and dataset_id
    assert str(error) == f"Dataset file not found: {s3_path} (dataset_id: {dataset_id})"


def test_dataset_file_not_found_error_is_runtime_error():
    """Test: DatasetFileNotFoundError is a subclass of RuntimeError."""
    # Given: s3_path
    s3_path = "datasets/test/data.parquet"
    
    # When: Creating exception
    error = DatasetFileNotFoundError(s3_path)
    
    # Then: It is an instance of RuntimeError
    assert isinstance(error, RuntimeError)
