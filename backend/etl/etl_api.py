"""API to Parquet ETL.

SKELETON: This module is a placeholder for future implementation.
Do not use in production until fully implemented.

Future implementation will support:
- REST API endpoints with pagination
- OAuth/API key authentication
- Rate limiting and retry logic
"""
from backend.etl.base_etl import BaseETL
import pandas as pd


class ApiETL(BaseETL):
    """ETL for converting API data to Parquet.

    SKELETON: Not implemented. Raises NotImplementedError on extract().
    """

    def extract(self) -> pd.DataFrame:
        """Extract data from API.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("API ETL not implemented - skeleton only")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data (passthrough for skeleton)."""
        return df
