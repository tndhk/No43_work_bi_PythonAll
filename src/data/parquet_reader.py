import io
from typing import Optional
import pandas as pd
import pyarrow.parquet as pq
from botocore.exceptions import ClientError

from src.data.s3_client import get_s3_client
from src.data.config import settings
from src.exceptions import DatasetFileNotFoundError


class ParquetReader:
    """Reads Parquet files from S3 with automatic partition detection."""

    def __init__(self):
        self.client = get_s3_client()
        self.bucket = settings.s3_bucket

    def read_dataset(
        self,
        dataset_id: str,
        date_range: Optional[tuple[str, str]] = None,
    ) -> pd.DataFrame:
        """Read dataset with automatic partition detection and filtering.

        Args:
            dataset_id: Dataset identifier
            date_range: Optional (start_date, end_date) in ISO 8601 format (YYYY-MM-DD).
                       Used for partition pruning.

        Returns:
            Combined DataFrame from all matching partitions or single file.
        """
        if self._has_partitions(dataset_id):
            return self._read_partitioned(dataset_id, date_range)
        return self._read_single(dataset_id)

    def _has_partitions(self, dataset_id: str) -> bool:
        """Check if dataset uses partition structure (datasets/{id}/partitions/)."""
        prefix = f"datasets/{dataset_id}/partitions/"
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=1,
            )
            return "Contents" in response
        except ClientError:
            return False

    def _list_partitions(self, dataset_id: str) -> list[str]:
        """List available partitions for dataset.

        Returns:
            Sorted list of date strings (e.g., ["2024-01-01", "2024-01-02"])
        """
        prefix = f"datasets/{dataset_id}/partitions/"
        partitions = []

        try:
            paginator = self.client.get_paginator("list_objects_v2")
            for page in paginator.paginate(
                Bucket=self.bucket,
                Prefix=prefix,
                Delimiter="/",
            ):
                for p in page.get("CommonPrefixes", []):
                    date_part = p["Prefix"].rstrip("/").split("/")[-1]
                    if date_part.startswith("date="):
                        partitions.append(date_part.split("=", 1)[1])
        except ClientError:
            pass

        return sorted(partitions)

    def _read_partitioned(
        self,
        dataset_id: str,
        date_range: Optional[tuple[str, str]] = None,
    ) -> pd.DataFrame:
        """Read partitioned dataset with optional date range filtering.

        Args:
            dataset_id: Dataset identifier
            date_range: Optional (start_date, end_date) for partition pruning.

        Returns:
            Combined DataFrame from filtered partitions.

        Raises:
            DatasetFileNotFoundError: If no valid partitions found.
        """
        all_partitions = self._list_partitions(dataset_id)

        if date_range:
            start_date, end_date = date_range
            partitions_to_read = [
                p for p in all_partitions
                if start_date <= p <= end_date
            ]
        else:
            partitions_to_read = all_partitions

        if not partitions_to_read:
            raise DatasetFileNotFoundError(
                s3_path=f"datasets/{dataset_id}/partitions/",
                dataset_id=dataset_id,
            )

        dfs = []
        for partition_date in partitions_to_read:
            s3_path = f"datasets/{dataset_id}/partitions/date={partition_date}/part-0000.parquet"
            try:
                dfs.append(self._read_file(s3_path))
            except DatasetFileNotFoundError:
                continue

        if not dfs:
            raise DatasetFileNotFoundError(
                s3_path=f"datasets/{dataset_id}/partitions/",
                dataset_id=dataset_id,
            )

        return pd.concat(dfs, ignore_index=True)

    def _read_single(self, dataset_id: str) -> pd.DataFrame:
        """Read non-partitioned dataset."""
        s3_path = f"datasets/{dataset_id}/data/part-0000.parquet"
        return self._read_file(s3_path)

    def _read_file(self, s3_path: str) -> pd.DataFrame:
        """Read single Parquet file from S3.

        Raises:
            DatasetFileNotFoundError: If file not found.
        """
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=s3_path)
            parquet_data = response["Body"].read()
            return pq.ParquetFile(io.BytesIO(parquet_data)).read().to_pandas()
        except ClientError as e:
            if e.response["Error"]["Code"] in ("NoSuchKey", "404", "NotFound"):
                raise DatasetFileNotFoundError(s3_path=s3_path) from e
            raise

    def list_datasets(self) -> list[str]:
        """Get list of available datasets."""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix="datasets/",
                Delimiter="/"
            )
            return [p["Prefix"].split("/")[1] for p in response.get("CommonPrefixes", [])]
        except ClientError:
            return []
