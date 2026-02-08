"""Tests for DomoApiETL transform masking behavior."""
import pandas as pd
import pytest

from backend.etl.etl_domo import DomoApiETL


def test_domo_transform_raises_when_mask_column_missing(monkeypatch):
    """Strict masking should fail if configured column is missing."""
    monkeypatch.setenv("ETL_MASKING_SECRET", "test-secret")
    etl = DomoApiETL(
        dataset_id="dummy-dataset",
        client_id="dummy-client",
        client_secret="dummy-secret",
        masking={
            "enabled": True,
            "strict": True,
            "columns": ["email"],
        },
    )
    df = pd.DataFrame({"name": ["Alice"]})

    with pytest.raises(ValueError, match="Missing masking columns"):
        etl.transform(df)
