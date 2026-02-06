# ETL実装例

このドキュメントでは、実際のプロジェクトで使用できるETL実装例を提供します。

---

## CSV ETLの完全な例

### 基本的なCSV ETLスクリプト

[`backend/scripts/load_cursor_usage.py`](backend/scripts/load_cursor_usage.py) の実装例：

```python
"""ETL script to load Cursor usage CSV data to MinIO S3 as Parquet."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.etl.etl_csv import CsvETL


def main():
    """Load Cursor usage CSV to S3."""
    csv_path = project_root / "backend" / "data_sources" / "team-usage-events-15944373-2026-01-28.csv"
    
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
    
    print(f"Loading CSV from: {csv_path}")
    
    # Create ETL instance
    etl = CsvETL(
        csv_path=str(csv_path),
        partition_column="Date",  # Partition by date
    )
    
    # Run ETL
    dataset_id = "cursor-usage"
    print(f"Running ETL for dataset: {dataset_id}")
    etl.run(dataset_id)
    
    print(f"Successfully loaded dataset '{dataset_id}' to S3")


if __name__ == "__main__":
    main()
```

### カスタムCSVオプションを使用する例

```python
from backend.etl.etl_csv import CsvETL
from src.data.csv_parser import CsvImportOptions

def main():
    csv_path = "backend/data_sources/data.csv"
    
    # カスタムCSVオプション
    csv_options = CsvImportOptions(
        delimiter=",",
        encoding="utf-8",
        has_header=True,
    )
    
    etl = CsvETL(
        csv_path=csv_path,
        partition_column="Date",
        csv_options=csv_options,
    )
    
    etl.run("dataset-id")
```

---

## カスタムAPI ETLの実装例

### 基本的なAPI ETL

```python
"""Custom API ETL implementation."""
from backend.etl.etl_api import ApiETL
import requests
import pandas as pd
from typing import Optional
from src.data.type_inferrer import infer_schema, apply_types


class CustomApiETL(ApiETL):
    """カスタムAPI ETL実装例"""
    
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
    
    def extract(self) -> pd.DataFrame:
        """APIからデータを取得"""
        response = requests.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        
        # JSONをDataFrameに変換
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict) and "data" in data:
            return pd.DataFrame(data["data"])
        else:
            raise ValueError("Unexpected API response format")
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """データを変換"""
        schema = infer_schema(df)
        return apply_types(df, schema)


# 使用例
def main():
    etl = CustomApiETL(
        endpoint="https://api.example.com/data",
        api_key="your-api-key",
    )
    etl.run("api-dataset")
```

### ページネーション対応API ETL

```python
class PaginatedApiETL(ApiETL):
    """ページネーション対応のAPI ETL"""
    
    def __init__(self, base_endpoint: str, api_key: str):
        self.base_endpoint = base_endpoint
        self.api_key = api_key
    
    def extract(self) -> pd.DataFrame:
        all_data = []
        page = 1
        
        while True:
            endpoint = f"{self.base_endpoint}?page={page}"
            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                break
            
            all_data.extend(data["results"])
            
            # 次のページがあるか確認
            if not data.get("has_next"):
                break
            
            page += 1
        
        return pd.DataFrame(all_data)
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        schema = infer_schema(df)
        return apply_types(df, schema)
```

### レート制限対応API ETL

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class RateLimitedApiETL(ApiETL):
    """レート制限対応のAPI ETL"""
    
    def __init__(self, endpoint: str, api_key: str, requests_per_second: float = 1.0):
        self.endpoint = endpoint
        self.api_key = api_key
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0
    
    def _rate_limit(self):
        """レート制限を守る"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
    
    def extract(self) -> pd.DataFrame:
        session = requests.Session()
        
        # リトライ戦略を設定
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        self._rate_limit()
        response = session.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        schema = infer_schema(df)
        return apply_types(df, schema)
```

---

## RDS ETLの実装例

### 基本的なRDS ETL

```python
"""Custom RDS ETL implementation."""
from backend.etl.etl_rds import RdsETL
import pandas as pd
from sqlalchemy import create_engine
from src.data.type_inferrer import infer_schema, apply_types


class CustomRdsETL(RdsETL):
    """カスタムRDS ETL実装例"""
    
    def __init__(self, connection_string: str, query: str):
        self.connection_string = connection_string
        self.query = query
    
    def extract(self) -> pd.DataFrame:
        """RDSからデータを取得"""
        engine = create_engine(self.connection_string)
        df = pd.read_sql_query(self.query, engine)
        engine.dispose()
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """データを変換"""
        schema = infer_schema(df)
        return apply_types(df, schema)


# 使用例
def main():
    connection_string = "postgresql://user:password@host:5432/database"
    query = """
        SELECT id, name, date, value
        FROM events
        WHERE date >= '2024-01-01'
    """
    
    etl = CustomRdsETL(
        connection_string=connection_string,
        query=query,
    )
    etl.run("rds-dataset")
```

### 接続プールを使用するRDS ETL

```python
from sqlalchemy.pool import QueuePool

class RdsETLWithPool(RdsETL):
    """接続プールを使用するRDS ETL"""
    
    def __init__(self, connection_string: str, query: str):
        self.connection_string = connection_string
        self.query = query
        self.engine = create_engine(
            self.connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
    
    def extract(self) -> pd.DataFrame:
        df = pd.read_sql_query(self.query, self.engine)
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        schema = infer_schema(df)
        return apply_types(df, schema)
    
    def __del__(self):
        """クリーンアップ"""
        if hasattr(self, "engine"):
            self.engine.dispose()
```

### ストリーミングRDS ETL

```python
class StreamingRdsETL(RdsETL):
    """大量データをストリーミングで処理するRDS ETL"""
    
    def __init__(self, connection_string: str, query: str, chunk_size: int = 10000):
        self.connection_string = connection_string
        self.query = query
        self.chunk_size = chunk_size
    
    def extract(self) -> pd.DataFrame:
        engine = create_engine(self.connection_string)
        chunks = []
        
        # チャンクごとに読み込み
        for chunk in pd.read_sql_query(
            self.query,
            engine,
            chunksize=self.chunk_size,
        ):
            chunks.append(chunk)
        
        engine.dispose()
        return pd.concat(chunks, ignore_index=True)
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        schema = infer_schema(df)
        return apply_types(df, schema)
```

---

## S3 ETLの実装例

### 基本的なS3 CSV ETL

```python
"""Custom S3 ETL implementation."""
from backend.etl.etl_s3 import S3RawETL
import pandas as pd
from src.data.s3_client import get_s3_client
from src.data.type_inferrer import infer_schema, apply_types


class S3CsvETL(S3RawETL):
    """S3からCSVを読み込むETL"""
    
    def __init__(self, bucket: str, key: str):
        self.bucket = bucket
        self.key = key
    
    def extract(self) -> pd.DataFrame:
        """S3からCSVを取得"""
        client = get_s3_client()
        response = client.get_object(Bucket=self.bucket, Key=self.key)
        return pd.read_csv(response["Body"])
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """データを変換"""
        schema = infer_schema(df)
        return apply_types(df, schema)


# 使用例
def main():
    etl = S3CsvETL(
        bucket="source-bucket",
        key="data/file.csv",
    )
    etl.run("s3-dataset")
```

### S3 JSON ETL

```python
import json

class S3JsonETL(S3RawETL):
    """S3からJSONを読み込むETL"""
    
    def __init__(self, bucket: str, key: str):
        self.bucket = bucket
        self.key = key
    
    def extract(self) -> pd.DataFrame:
        """S3からJSONを取得"""
        client = get_s3_client()
        response = client.get_object(Bucket=self.bucket, Key=self.key)
        data = json.loads(response["Body"].read().decode("utf-8"))
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        else:
            raise ValueError("Unexpected JSON format")
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        schema = infer_schema(df)
        return apply_types(df, schema)
```

### 複数ファイルを処理するS3 ETL

```python
class MultiFileS3ETL(S3RawETL):
    """S3バケット内の複数ファイルを処理するETL"""
    
    def __init__(self, bucket: str, prefix: str, file_format: str = "csv"):
        self.bucket = bucket
        self.prefix = prefix
        self.file_format = file_format
    
    def extract(self) -> pd.DataFrame:
        """プレフィックスに一致するすべてのファイルを読み込み"""
        client = get_s3_client()
        
        # プレフィックスに一致するすべてのオブジェクトを取得
        paginator = client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket, Prefix=self.prefix)
        
        all_dataframes = []
        
        for page in pages:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                
                # ファイル形式に応じて読み込み
                response = client.get_object(Bucket=self.bucket, Key=key)
                
                if self.file_format == "csv":
                    df = pd.read_csv(response["Body"])
                elif self.file_format == "json":
                    import json
                    data = json.loads(response["Body"].read().decode("utf-8"))
                    df = pd.DataFrame(data if isinstance(data, list) else [data])
                else:
                    continue
                
                all_dataframes.append(df)
        
        return pd.concat(all_dataframes, ignore_index=True)
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        schema = infer_schema(df)
        return apply_types(df, schema)
```

---

## エラーハンドリングパターン

### 包括的なエラーハンドリング

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RobustETL(ApiETL):
    """エラーハンドリングを強化したETL"""
    
    def extract(self) -> pd.DataFrame:
        try:
            response = requests.get(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data)
        
        except requests.exceptions.Timeout:
            logger.error("API request timeout")
            raise Exception("API request timeout")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error("Rate limit exceeded")
                raise Exception("Rate limit exceeded")
            logger.error(f"HTTP error: {e.response.status_code}")
            raise Exception(f"HTTP error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # 必須カラムの確認
            required_columns = ["id", "date", "value"]
            missing = set(required_columns) - set(df.columns)
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            
            # 空のデータフレームの確認
            if len(df) == 0:
                logger.warning("Empty dataframe")
                return df
            
            schema = infer_schema(df)
            return apply_types(df, schema)
        
        except Exception as e:
            logger.error(f"Transform error: {str(e)}")
            raise
```

---

## 大量データ処理パターン

### チャンク処理を使用するCSV ETL

```python
class LargeCsvETL(CsvETL):
    """大容量CSVをチャンク処理するETL"""
    
    def extract(self) -> pd.DataFrame:
        chunks = []
        chunk_size = 10000
        
        for chunk in pd.read_csv(
            self.csv_path,
            chunksize=chunk_size,
            encoding="utf-8",
        ):
            chunks.append(chunk)
        
        return pd.concat(chunks, ignore_index=True)
```

### メモリ効率的な処理

```python
class MemoryEfficientETL(ApiETL):
    """メモリ効率的なETL"""
    
    def extract(self) -> pd.DataFrame:
        # 必要なカラムのみ取得
        response = requests.get(self.endpoint)
        data = response.json()
        df = pd.DataFrame(data)
        
        # 不要なカラムを早期に削除
        df = df[["id", "date", "value"]]  # 必要なカラムのみ
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # データ型変換でメモリ使用量を削減
        df["id"] = df["id"].astype("int32")  # int64からint32へ
        df["value"] = df["value"].astype("float32")  # float64からfloat32へ
        
        schema = infer_schema(df)
        return apply_types(df, schema)
```

---

## 増分更新パターン

### 増分更新を行うETL

```python
from typing import Optional

class IncrementalETL(ApiETL):
    """増分更新を行うETL"""
    
    def __init__(self, endpoint: str, api_key: str, last_updated_column: str):
        super().__init__()
        self.endpoint = endpoint
        self.api_key = api_key
        self.last_updated_column = last_updated_column
    
    def extract(self) -> pd.DataFrame:
        # 新しいデータのみ取得（例: 最終更新日時でフィルタ）
        params = {
            "updated_since": self._get_last_update_time(),
        }
        response = requests.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            params=params,
        )
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def load(
        self,
        df: pd.DataFrame,
        dataset_id: str,
        partition_column: Optional[str] = None,
    ) -> None:
        """既存データとマージしてからアップロード"""
        from src.data.s3_client import get_s3_client
        from src.data.parquet_reader import ParquetReader
        
        # 既存データを読み込み
        client = get_s3_client()
        reader = ParquetReader()
        
        try:
            existing_df = reader.read_dataset(dataset_id)
            
            # 新しいデータとマージ
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            
            # 重複を削除（最新のデータを優先）
            combined_df = combined_df.sort_values(
                self.last_updated_column,
                ascending=False,
            )
            combined_df = combined_df.drop_duplicates(subset=["id"], keep="first")
            
            df = combined_df
        except Exception:
            # 既存データがない場合は新規データのみ
            pass
        
        # 親クラスのloadメソッドを呼び出し
        super().load(df, dataset_id, partition_column)
    
    def _get_last_update_time(self) -> str:
        """最後の更新日時を取得（実装は環境に依存）"""
        # 例: データベースやファイルから取得
        return "2024-01-01T00:00:00Z"
```

---

## ETLスクリプトの完全な例

### 環境変数を使用するETLスクリプト

```python
"""ETL script with environment variables."""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.etl.etl_csv import CsvETL


def main():
    """Load data to MinIO using environment variables."""
    # 環境変数から設定を取得
    dataset_id = os.getenv("DATASET_ID", "default-dataset")
    csv_filename = os.getenv("CSV_FILENAME", "data.csv")
    partition_column = os.getenv("PARTITION_COLUMN", "Date")
    
    csv_path = project_root / "backend" / "data_sources" / csv_filename
    
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
    
    print(f"Loading CSV from: {csv_path}")
    print(f"Dataset ID: {dataset_id}")
    print(f"Partition column: {partition_column}")
    
    etl = CsvETL(
        csv_path=str(csv_path),
        partition_column=partition_column if partition_column != "None" else None,
    )
    
    etl.run(dataset_id)
    print(f"Successfully loaded dataset '{dataset_id}' to S3")


if __name__ == "__main__":
    main()
```

### コマンドライン引数を使用するETLスクリプト

```python
"""ETL script with command line arguments."""
import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.etl.etl_csv import CsvETL


def main():
    """Load data to MinIO using command line arguments."""
    parser = argparse.ArgumentParser(description="Load CSV data to MinIO")
    parser.add_argument("csv_file", help="Path to CSV file")
    parser.add_argument("dataset_id", help="Dataset ID")
    parser.add_argument(
        "--partition-column",
        help="Partition column name",
        default="Date",
    )
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
    
    print(f"Loading CSV from: {csv_path}")
    print(f"Dataset ID: {args.dataset_id}")
    
    etl = CsvETL(
        csv_path=str(csv_path),
        partition_column=args.partition_column if args.partition_column else None,
    )
    
    etl.run(args.dataset_id)
    print(f"Successfully loaded dataset '{args.dataset_id}' to S3")


if __name__ == "__main__":
    main()
```
