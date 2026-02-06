"""RDS/DB to Parquet ETL (skeleton for Phase 1)."""
from backend.etl.base_etl import BaseETL
import pandas as pd


class RdsETL(BaseETL):
    """ETL for converting RDS/DB data to Parquet (skeleton)."""

    def extract(self) -> pd.DataFrame:
        """Extract data from RDS/DB (not implemented)."""
        raise NotImplementedError("RDS ETL not implemented in Phase 1")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data (not implemented)."""
        return df
