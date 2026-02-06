"""S3 Raw to Parquet ETL (skeleton for Phase 1)."""
from backend.etl.base_etl import BaseETL
import pandas as pd


class S3RawETL(BaseETL):
    """ETL for converting S3 Raw data to Parquet (skeleton)."""

    def extract(self) -> pd.DataFrame:
        """Extract data from S3 Raw (not implemented)."""
        raise NotImplementedError("S3 Raw ETL not implemented in Phase 1")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data (not implemented)."""
        return df
