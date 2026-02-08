"""Tests for ETL masking utilities."""
import pandas as pd
import pytest

from backend.etl.masking import apply_hmac_masking


def test_apply_hmac_masking_hashes_values_and_keeps_null():
    """Masking hashes non-null values and keeps nulls."""
    df = pd.DataFrame(
        {
            "email": ["alice@example.com", None, "bob@example.com"],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )

    result = apply_hmac_masking(
        df=df,
        columns=["email"],
        secret="test-secret",
        strict=True,
    )

    assert result.loc[0, "email"] != "alice@example.com"
    assert result.loc[2, "email"] != "bob@example.com"
    assert isinstance(result.loc[0, "email"], str)
    assert len(result.loc[0, "email"]) == 64
    assert pd.isna(result.loc[1, "email"])


def test_apply_hmac_masking_raises_when_column_missing_in_strict_mode():
    """Strict mode should fail when configured column is missing."""
    df = pd.DataFrame({"name": ["Alice"]})

    with pytest.raises(ValueError, match="Missing masking columns"):
        apply_hmac_masking(
            df=df,
            columns=["email"],
            secret="test-secret",
            strict=True,
        )


def test_apply_hmac_masking_raises_when_secret_is_empty():
    """Masking should fail without secret."""
    df = pd.DataFrame({"email": ["alice@example.com"]})

    with pytest.raises(ValueError, match="ETL_MASKING_SECRET"):
        apply_hmac_masking(
            df=df,
            columns=["email"],
            secret="",
            strict=True,
        )
