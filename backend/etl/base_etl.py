"""Base ETL class for common ETL operations."""
from abc import ABC, abstractmethod
from typing import Optional
import io
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from src.data.s3_client import get_s3_client
from src.data.config import settings


class BaseETL(ABC):
    """Base class for ETL operations.

    Subclasses implement extract() and transform().
    load() provides common S3/Parquet write logic.
    """

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Extract data from data source."""

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data."""

    def load(
        self,
        df: pd.DataFrame,
        dataset_id: str,
        partition_column: Optional[str] = None,
    ) -> None:
        """
        Convert DataFrame to Parquet and upload to S3.

        Args:
            df: DataFrame to upload
            dataset_id: Dataset ID
            partition_column: Date column name for partitioning.
                             None means upload as single file.

        S3 path:
            Non-partitioned: datasets/{id}/data/part-0000.parquet
            Partitioned: datasets/{id}/partitions/date=YYYY-MM-DD/part-0000.parquet
        """
        client = get_s3_client()
        bucket = settings.s3_bucket

        if partition_column and partition_column in df.columns:
            # Partitioned upload
            df[partition_column] = pd.to_datetime(df[partition_column])
            for date_value, partition_df in df.groupby(df[partition_column].dt.date):
                date_str = date_value.isoformat()
                s3_key = (
                    f"datasets/{dataset_id}/partitions/date={date_str}/part-0000.parquet"
                )
                self._upload_parquet(client, bucket, s3_key, partition_df)
        else:
            # Non-partitioned upload
            s3_key = f"datasets/{dataset_id}/data/part-0000.parquet"
            self._upload_parquet(client, bucket, s3_key, df)

    def _upload_parquet(
        self, client, bucket: str, key: str, df: pd.DataFrame
    ) -> None:
        """Helper to upload DataFrame as Parquet to S3."""
        table = pa.Table.from_pandas(df)
        buf = io.BytesIO()
        pq.write_table(table, buf)
        buf.seek(0)
        client.put_object(Bucket=bucket, Key=key, Body=buf.read())

    def run(self, dataset_id: str) -> None:
        """Execute extract -> transform -> load."""
        df = self.extract()
        df = self.transform(df)
        self.load(df, dataset_id)
