"""S3 Raw Files to Parquet ETL.

SKELETON: This module is a placeholder for future implementation.
Do not use in production until fully implemented.

Future implementation will support:
- JSON, CSV, and other raw file formats from S3
- S3 event-driven triggers
- Schema inference and evolution
"""
from backend.etl.base_etl import BaseETL
import pandas as pd


class S3RawETL(BaseETL):
    """ETL for converting S3 raw files to Parquet.

    SKELETON: Not implemented. Raises NotImplementedError on extract().
    """

    def extract(self) -> pd.DataFrame:
        """Extract data from S3 raw files.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("S3 Raw ETL not implemented - skeleton only")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data (passthrough for skeleton)."""
        return df
