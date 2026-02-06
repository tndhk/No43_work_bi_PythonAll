---
name: etl-workflow
description: データ取得とETL処理のワークフロー。CSV、API、RDS、S3などの各種データソースからParquet形式への変換とMinIOアップロード。ETL、データパイプライン、BaseETL、CsvETL、ApiETLに関連する作業で使用。ダッシュボード作成は別スキル（dash-bi-workflow）を参照。
---

# ETLワークフロー

## 前提条件

このスキルは、データソースからParquet形式への変換とMinIOへのアップロードに特化しています。

ダッシュボード作成が必要な場合は、`dash-bi-workflow` スキルを参照してください。

## クイックスタートチェックリスト

データソース別のチェックリスト：

### CSV
- [ ] CSVファイルを `backend/data_sources/` に配置
- [ ] `.gitignore` と `.cursorignore` に `backend/data_sources/` を追加
- [ ] `backend/scripts/` にETLスクリプトを作成
- [ ] ETLスクリプトを実行してMinIOにアップロード

### API
- [ ] APIエンドポイントと認証情報を確認
- [ ] `ApiETL` を継承したカスタムETLクラスを作成
- [ ] `backend/scripts/` にETLスクリプトを作成
- [ ] ETLスクリプトを実行してMinIOにアップロード

### RDS
- [ ] データベース接続情報を確認
- [ ] SQLクエリを作成
- [ ] `RdsETL` を継承したカスタムETLクラスを作成
- [ ] `backend/scripts/` にETLスクリプトを作成
- [ ] ETLスクリプトを実行してMinIOにアップロード

### S3
- [ ] S3バケットとキーを確認
- [ ] アクセス権限を確認
- [ ] `S3RawETL` を継承したカスタムETLクラスを作成
- [ ] `backend/scripts/` にETLスクリプトを作成
- [ ] ETLスクリプトを実行してMinIOにアップロード

---

## BaseETLアーキテクチャ

すべてのETLクラスは [`backend/etl/base_etl.py`](backend/etl/base_etl.py) の `BaseETL` を継承します。

### BaseETLの構造

```python
class BaseETL(ABC):
    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """データソースからデータを抽出"""
    
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """データを変換"""
    
    def load(
        self,
        df: pd.DataFrame,
        dataset_id: str,
        partition_column: Optional[str] = None,
    ) -> None:
        """ParquetとしてMinIOにアップロード"""
    
    def run(self, dataset_id: str) -> None:
        """ETLパイプライン実行: extract -> transform -> load"""
```

### ETLパイプラインの流れ

```mermaid
flowchart LR
    Source[Data Source] --> Extract[extract]
    Extract --> Transform[transform]
    Transform --> Load[load]
    Load --> MinIO[MinIO Parquet]
```

1. **extract()**: データソースから生データを取得してDataFrameに変換
2. **transform()**: データ型の推論、クリーニング、正規化
3. **load()**: Parquet形式に変換してMinIOにアップロード

---

## データソース別パターン

### Pattern 1: CSV

#### ファイル配置

CSVファイルは `backend/data_sources/` ディレクトリに配置します。

```
backend/data_sources/
├── team-usage-events-15944373-2026-01-28.csv
└── ...
```

#### Git/Cursor除外設定

データファイルはリポジトリに含めないため、必ず除外設定を追加します：

**`.gitignore`** に追加：
```
backend/data_sources/
```

**`.cursorignore`** に追加：
```
backend/data_sources/
```

#### CsvETLの使用

[`backend/etl/etl_csv.py`](backend/etl/etl_csv.py) の `CsvETL` クラスを使用します。

**基本使用例:**

```python
from backend.etl.etl_csv import CsvETL

etl = CsvETL(
    csv_path="backend/data_sources/your-file.csv",
    partition_column="Date",  # パーティション分割するカラム名
)

etl.run("dataset-id")
```

**特徴:**
- CSVパーサーを使用した自動型推論
- Type inferrerによるデータ型の自動変換
- パーティション分割対応

詳細は [DATA_SOURCES.md](DATA_SOURCES.md#csv) を参照してください。

---

### Pattern 2: API

#### ApiETLの実装

[`backend/etl/etl_api.py`](backend/etl/etl_api.py) の `ApiETL` は現在skeleton実装のため、カスタムクラスを作成する必要があります。

**テンプレート:**

```python
from backend.etl.etl_api import ApiETL
import requests
import pandas as pd
from typing import Optional

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
        # Type inference, cleaning
        from src.data.type_inferrer import infer_schema, apply_types
        
        schema = infer_schema(df)
        return apply_types(df, schema)
```

**認証パターン:**

- **Bearer Token**: `headers={"Authorization": f"Bearer {token}"}`
- **API Key**: `headers={"X-API-Key": api_key}` または `params={"api_key": api_key}`
- **Basic Auth**: `auth=(username, password)`

詳細は [DATA_SOURCES.md](DATA_SOURCES.md#api) を参照してください。

---

### Pattern 3: RDS

#### RdsETLの実装

[`backend/etl/etl_rds.py`](backend/etl/etl_rds.py) の `RdsETL` は現在skeleton実装のため、カスタムクラスを作成する必要があります。

**テンプレート:**

```python
from backend.etl.etl_rds import RdsETL
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

class CustomRdsETL(RdsETL):
    """カスタムRDS ETL実装例"""
    
    def __init__(self, connection_string: str, query: str):
        self.connection_string = connection_string
        self.query = query
    
    def extract(self) -> pd.DataFrame:
        """RDSからデータを取得"""
        # SQLAlchemyを使用（推奨）
        engine = create_engine(self.connection_string)
        df = pd.read_sql_query(self.query, engine)
        engine.dispose()
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """データを変換"""
        from src.data.type_inferrer import infer_schema, apply_types
        
        schema = infer_schema(df)
        return apply_types(df, schema)
```

**接続文字列の例:**

- **PostgreSQL**: `postgresql://user:password@host:port/database`
- **MySQL**: `mysql+pymysql://user:password@host:port/database`

詳細は [DATA_SOURCES.md](DATA_SOURCES.md#rds) を参照してください。

---

### Pattern 4: S3

#### S3RawETLの実装

[`backend/etl/etl_s3.py`](backend/etl/etl_s3.py) の `S3RawETL` は現在skeleton実装のため、カスタムクラスを作成する必要があります。

**テンプレート:**

```python
from backend.etl.etl_s3 import S3RawETL
import pandas as pd
from src.data.s3_client import get_s3_client

class CustomS3ETL(S3RawETL):
    """カスタムS3 ETL実装例"""
    
    def __init__(self, bucket: str, key: str, file_format: str = "csv"):
        self.bucket = bucket
        self.key = key
        self.file_format = file_format
    
    def extract(self) -> pd.DataFrame:
        """S3からデータを取得"""
        client = get_s3_client()
        response = client.get_object(Bucket=self.bucket, Key=self.key)
        
        if self.file_format == "csv":
            return pd.read_csv(response["Body"])
        elif self.file_format == "json":
            import json
            data = json.loads(response["Body"].read())
            return pd.DataFrame(data)
        elif self.file_format == "parquet":
            import pyarrow.parquet as pq
            return pq.read_table(response["Body"]).to_pandas()
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """データを変換"""
        from src.data.type_inferrer import infer_schema, apply_types
        
        schema = infer_schema(df)
        return apply_types(df, schema)
```

詳細は [DATA_SOURCES.md](DATA_SOURCES.md#s3) を参照してください。

---

## パーティション分割

### パーティション分割のメリット

- **クエリパフォーマンスの向上**: 日付範囲フィルタが効率的
- **データ管理の容易さ**: 日付ごとにファイルが分離
- **コスト削減**: 必要なパーティションのみ読み込み

### パーティション戦略

#### 日次データ

```python
etl = CsvETL(
    csv_path="data.csv",
    partition_column="Date",  # 日付カラムで分割
)
```

#### パーティション不要

```python
etl = CsvETL(
    csv_path="data.csv",
    partition_column=None,  # 単一ファイルとしてアップロード
)
```

### S3パス構造

**パーティション分割あり:**
```
datasets/{dataset_id}/
└── partitions/
    ├── date=2024-01-01/
    │   └── part-0000.parquet
    ├── date=2024-01-02/
    │   └── part-0000.parquet
    └── ...
```

**パーティション分割なし:**
```
datasets/{dataset_id}/
└── data/
    └── part-0000.parquet
```

---

## ETLスクリプト作成ガイド

### 配置場所

`backend/scripts/` ディレクトリにETLスクリプトを作成します。

### 命名規則

`load_{dataset_name}.py`

例: `load_cursor_usage.py`, `load_sales_data.py`

### 基本構造

```python
"""ETL script to load {dataset} data to MinIO S3 as Parquet."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.etl.etl_csv import CsvETL  # または他のETL


def main():
    """Load data to MinIO."""
    # データソースの設定
    csv_path = project_root / "backend" / "data_sources" / "your-file.csv"
    
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
    
    print(f"Loading data from: {csv_path}")
    
    # ETLインスタンスの作成
    etl = CsvETL(
        csv_path=str(csv_path),
        partition_column="Date",
    )
    
    # ETL実行
    dataset_id = "your-dataset-id"
    print(f"Running ETL for dataset: {dataset_id}")
    etl.run(dataset_id)
    
    print(f"Successfully loaded dataset '{dataset_id}' to S3")


if __name__ == "__main__":
    main()
```

### 実行方法

```bash
# 仮想環境をアクティベート
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate  # Windows

# ETLスクリプトを実行
python backend/scripts/load_your_dataset.py
```

---

## よくある問題と解決策

### 大量データの処理

**問題:** メモリ不足でエラーが発生する

**解決策:**
- チャンク処理を使用
- パーティション分割でファイルサイズを削減
- 不要なカラムを早期に削除

```python
# チャンク処理の例（CSVの場合）
def extract(self) -> pd.DataFrame:
    chunks = []
    for chunk in pd.read_csv(self.csv_path, chunksize=10000):
        chunks.append(chunk)
    return pd.concat(chunks, ignore_index=True)
```

### API Rate Limit

**問題:** APIのレート制限に引っかかる

**解決策:**
- リトライロジックとバックオフを実装
- リクエスト間隔を調整

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def extract(self) -> pd.DataFrame:
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    response = session.get(self.endpoint, headers=...)
    # ...
```

### データ型の不一致

**問題:** データ型が正しく推論されない

**解決策:**
- Type inferrerを活用
- 必要に応じて手動で型変換

```python
def transform(self, df: pd.DataFrame) -> pd.DataFrame:
    from src.data.type_inferrer import infer_schema, apply_types
    
    schema = infer_schema(df)
    df = apply_types(df, schema)
    
    # 手動で型変換が必要な場合
    df["custom_column"] = pd.to_datetime(df["custom_column"], format="%Y-%m-%d")
    
    return df
```

### 接続エラー

**問題:** データベースやAPIへの接続が失敗する

**解決策:**
- 接続情報の確認
- タイムアウト設定の調整
- リトライメカニズムの実装

---

## 検証チェックリスト

ETL実行後、以下を確認します：

- [ ] データソースからの取得が成功
- [ ] データ型が適切に推論・変換されている
- [ ] パーティション分割が正しく機能（該当する場合）
- [ ] MinIOにParquetファイルがアップロードされている
- [ ] MinIOコンソール（http://localhost:9001）でファイルを確認
- [ ] ParquetReaderで読み込みテスト成功

**読み込みテスト:**

```python
from src.data.parquet_reader import ParquetReader
from src.core.cache import get_cached_dataset

reader = ParquetReader()
df = get_cached_dataset(reader, "your-dataset-id")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(df.head())
```

---

## 関連スキル

- **dash-bi-workflow**: Parquetデータからダッシュボード作成

## 追加リソース

- データソース別の詳細ガイド: [DATA_SOURCES.md](DATA_SOURCES.md)
- 実際のコード例: [examples.md](examples.md)
