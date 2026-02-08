"""Tests for backend/scripts/load_domo.py."""
from unittest.mock import patch, MagicMock

from backend.scripts.load_domo import load_dataset


@patch("backend.scripts.load_domo.DomoApiETL")
def test_load_domo_passes_masking_to_etl(mock_etl_cls):
    """load_dataset should pass masking config into DomoApiETL."""
    mock_etl = MagicMock()
    mock_etl_cls.return_value = mock_etl

    config = {
        "name": "Sample DOMO",
        "domo_dataset_id": "dataset-id",
        "minio_dataset_id": "minio-id",
        "partition_column": "date_col",
        "enabled": True,
        "masking": {
            "enabled": True,
            "strict": True,
            "columns": ["employee_id"],
        },
    }

    ok = load_dataset(config, dry_run=False)

    assert ok is True
    mock_etl_cls.assert_called_once_with(
        dataset_id="dataset-id",
        partition_column="date_col",
        exclude_filter=None,
        masking=config["masking"],
    )
    mock_etl.run.assert_called_once_with("minio-id")


@patch("backend.scripts.load_domo.DomoApiETL")
def test_load_domo_dry_run_does_not_run_etl(mock_etl_cls):
    """dry_run should not instantiate ETL class."""
    config = {
        "name": "Sample DOMO",
        "domo_dataset_id": "dataset-id",
        "minio_dataset_id": "minio-id",
        "partition_column": None,
        "enabled": True,
    }

    ok = load_dataset(config, dry_run=True)

    assert ok is True
    mock_etl_cls.assert_not_called()
