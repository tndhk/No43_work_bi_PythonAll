"""API to Parquet ETL (skeleton for Phase 1)."""
from backend.etl.base_etl import BaseETL
import pandas as pd


class ApiETL(BaseETL):
    """ETL for converting API data to Parquet (skeleton)."""

    def extract(self) -> pd.DataFrame:
        """Extract data from API (not implemented)."""
        raise NotImplementedError("API ETL not implemented in Phase 1")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data (not implemented)."""
        return df
