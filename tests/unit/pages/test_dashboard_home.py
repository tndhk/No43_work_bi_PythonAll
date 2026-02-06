"""Tests for dashboard home page."""
import pytest
from unittest.mock import patch, MagicMock
from dash import html
import pandas as pd
from src.pages.dashboard_home import layout, load_dataset_options, update_preview


def test_layout_returns_div():
    """Test: layout() returns html.Div."""
    # Given: Layout function
    
    # When: Calling layout
    result = layout()
    
    # Then: Result is a Div component
    assert isinstance(result, html.Div)
    assert result is not None


def test_load_dataset_options_success():
    """Test: load_dataset_options() returns options list on success."""
    # Given: Mock ParquetReader with datasets
    mock_datasets = ["dataset1", "dataset2", "dataset3"]
    mock_reader = MagicMock()
    mock_reader.list_datasets.return_value = mock_datasets
    
    # When: Loading dataset options
    with patch("src.pages.dashboard_home.ParquetReader", return_value=mock_reader):
        result = load_dataset_options(None)
    
    # Then: Options list is returned
    assert result == [{"label": "dataset1", "value": "dataset1"}, 
                      {"label": "dataset2", "value": "dataset2"},
                      {"label": "dataset3", "value": "dataset3"}]


def test_load_dataset_options_exception():
    """Test: load_dataset_options() returns empty list on exception."""
    # Given: Mock ParquetReader that raises exception
    mock_reader = MagicMock()
    mock_reader.list_datasets.side_effect = Exception("S3 error")
    
    # When: Loading dataset options
    with patch("src.pages.dashboard_home.ParquetReader", return_value=mock_reader):
        result = load_dataset_options(None)
    
    # Then: Empty list is returned
    assert result == []


def test_update_preview_with_none_dataset_id():
    """Test: update_preview() returns placeholder when dataset_id is None."""
    # Given: None dataset_id
    
    # When: Updating preview
    result = update_preview(None)
    
    # Then: Placeholder message is returned
    assert isinstance(result, html.P)
    assert "データセットを選択してください" in str(result)


def test_update_preview_success():
    """Test: update_preview() returns DataTable on success."""
    # Given: Mock ParquetReader with DataFrame
    dataset_id = "test_dataset"
    mock_df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "amount": [100.0, 200.0, 300.0],
    })
    mock_reader = MagicMock()
    mock_reader.read_dataset.return_value = mock_df
    
    # When: Updating preview
    with patch("src.pages.dashboard_home.ParquetReader", return_value=mock_reader):
        result = update_preview(dataset_id)
    
    # Then: DataTable is returned
    from dash import dash_table
    assert isinstance(result, dash_table.DataTable)
    assert result is not None


def test_update_preview_file_not_found():
    """Test: update_preview() returns error message on FileNotFoundError."""
    # Given: Mock ParquetReader that raises FileNotFoundError
    dataset_id = "nonexistent_dataset"
    mock_reader = MagicMock()
    mock_reader.read_dataset.side_effect = FileNotFoundError("File not found")
    
    # When: Updating preview
    with patch("src.pages.dashboard_home.ParquetReader", return_value=mock_reader):
        result = update_preview(dataset_id)
    
    # Then: Error message is returned
    assert isinstance(result, html.P)
    assert "データセットが見つかりません" in str(result)


def test_update_preview_general_exception():
    """Test: update_preview() returns error message on general exception."""
    # Given: Mock ParquetReader that raises general exception
    dataset_id = "test_dataset"
    mock_reader = MagicMock()
    mock_reader.read_dataset.side_effect = ValueError("Invalid data")
    
    # When: Updating preview
    with patch("src.pages.dashboard_home.ParquetReader", return_value=mock_reader):
        result = update_preview(dataset_id)
    
    # Then: Error message is returned
    assert isinstance(result, html.P)
    assert "エラー" in str(result)
