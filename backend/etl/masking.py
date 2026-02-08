"""Masking utilities for ETL pipelines."""
import hashlib
import hmac
from typing import Iterable

import pandas as pd


def apply_hmac_masking(
    df: pd.DataFrame,
    columns: Iterable[str],
    secret: str,
    strict: bool = True,
) -> pd.DataFrame:
    """Apply HMAC-SHA256 masking to selected DataFrame columns.

    Args:
        df: Source DataFrame.
        columns: Columns to mask.
        secret: HMAC secret (from ETL_MASKING_SECRET).
        strict: If True, raise when any configured column is missing.
    """
    if not secret:
        raise ValueError("ETL_MASKING_SECRET is required when masking is enabled")

    columns = list(columns or [])
    if not columns:
        raise ValueError("Masking columns must be provided when masking is enabled")

    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns and strict:
        raise ValueError(f"Missing masking columns: {missing_columns}")

    target_columns = [col for col in columns if col in df.columns]
    if not target_columns:
        return df

    masked_df = df.copy()
    secret_bytes = secret.encode("utf-8")

    for column in target_columns:
        mask = masked_df[column].notna()
        masked_df.loc[mask, column] = masked_df.loc[mask, column].astype(str).map(
            lambda value: hmac.new(
                secret_bytes, value.encode("utf-8"), hashlib.sha256
            ).hexdigest()
        )

    return masked_df
