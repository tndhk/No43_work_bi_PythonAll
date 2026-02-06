import io
import pandas as pd
import pyarrow.parquet as pq
from botocore.exceptions import ClientError

from src.data.s3_client import get_s3_client
from src.data.config import settings


class ParquetReader:
    """S3からParquetファイルを読み込む"""

    def __init__(self):
        self.client = get_s3_client()
        self.bucket = settings.s3_bucket

    def read_dataset(self, dataset_id: str) -> pd.DataFrame:
        """データセットを読み込む
        
        Args:
            dataset_id: データセットID
            
        Returns:
            DataFrame
        """
        s3_path = f"datasets/{dataset_id}/data/part-0000.parquet"
        return self._read_file(s3_path)

    def _read_file(self, s3_path: str) -> pd.DataFrame:
        """単一Parquetファイルを読み込む"""
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=s3_path)
            parquet_data = response["Body"].read()
            parquet_file = pq.ParquetFile(io.BytesIO(parquet_data))
            return parquet_file.read().to_pandas()
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("NoSuchKey", "404", "NotFound"):
                raise FileNotFoundError(f"Dataset not found: {s3_path}") from e
            raise

    def list_datasets(self) -> list[str]:
        """利用可能なデータセット一覧を取得"""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix="datasets/",
                Delimiter="/"
            )
            prefixes = response.get("CommonPrefixes", [])
            return [p["Prefix"].split("/")[1] for p in prefixes]
        except ClientError:
            return []
