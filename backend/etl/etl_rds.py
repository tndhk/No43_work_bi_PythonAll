"""RDS/Database to Parquet ETL.

SKELETON: This module is a placeholder for future implementation.
Do not use in production until fully implemented.

Future implementation will support:
- PostgreSQL, MySQL, and other RDS databases
- SQLAlchemy connection pooling
- Incremental extraction with watermarks
"""
from backend.etl.base_etl import BaseETL
import pandas as pd


class RdsETL(BaseETL):
    """ETL for converting RDS/Database data to Parquet.

    SKELETON: Not implemented. Raises NotImplementedError on extract().
    """

    def extract(self) -> pd.DataFrame:
        """Extract data from RDS/Database.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("RDS ETL not implemented - skeleton only")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data (passthrough for skeleton)."""
        return df
