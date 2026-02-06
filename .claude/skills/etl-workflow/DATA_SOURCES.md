# データソース別詳細ガイド

このドキュメントでは、各データソースからのETL処理の詳細な方法を説明します。

---

## CSV

### ファイルフォーマットの要件

- **エンコーディング**: UTF-8推奨（他のエンコーディングも対応可能）
- **区切り文字**: カンマ（`,`）がデフォルト
- **ヘッダー行**: 1行目のヘッダーが必須

### ファイル配置

```
backend/data_sources/
├── dataset-1-2024-01-01.csv
├── dataset-2-2024-01-01.csv
└── ...
```

### Git/Cursor除外設定

データファイルはリポジトリに含めないため、必ず除外設定を追加します：

**`.gitignore`** に追加：
```
backend/data_sources/
```

**`.cursorignore`** に追加：
```
backend/data_sources/
```

### CsvETLの使用

```python
from backend.etl.etl_csv import CsvETL
from src.data.csv_parser import CsvImportOptions

# デフォルト設定
etl = CsvETL(
    csv_path="backend/data_sources/data.csv",
    partition_column="Date",
)

# カスタム設定
csv_options = CsvImportOptions(
    delimiter=",",
    encoding="utf-8",
    has_header=True,
)

etl = CsvETL(
    csv_path="backend/data_sources/data.csv",
    partition_column="Date",
    csv_options=csv_options,
)

etl.run("dataset-id")
```

### 大容量CSVの処理

**問題:** ファイルサイズが大きく、メモリ不足になる

**解決策:**

1. **チャンク処理を使用:**
```python
class LargeCsvETL(CsvETL):
    def extract(self) -> pd.DataFrame:
        chunks = []
        for chunk in pd.read_csv(
            self.csv_path,
            chunksize=10000,
            encoding="utf-8",
        ):
            chunks.append(chunk)
        return pd.concat(chunks, ignore_index=True)
```

2. **パーティション分割でファイルサイズを削減:**
```python
etl = CsvETL(
    csv_path="large-file.csv",
    partition_column="Date",  # 日付ごとに分割
)
```

### エンコーディング処理

**問題:** 文字化けが発生する

**解決策:**

```python
from src.data.csv_parser import CsvImportOptions

# エンコーディングを指定
csv_options = CsvImportOptions(
    encoding="shift_jis",  # または "cp932", "euc-jp" など
)

etl = CsvETL(
    csv_path="data.csv",
    csv_options=csv_options,
)
```

---

## DOMO API

DOMO APIを使用してDataSetを取得し、Parquetに変換します。

### 概要

- **API種別**: REST API with OAuth2認証
- **データ形式**: CSV形式でエクスポート
- **ETLクラス**: [`backend/etl/etl_domo.py`](../../backend/etl/etl_domo.py) の `DomoApiETL`
- **設定ファイル**: [`backend/config/domo_datasets.yaml`](../../backend/config/domo_datasets.yaml)
- **実行スクリプト**: [`backend/scripts/load_domo.py`](../../backend/scripts/load_domo.py)

### 事前準備

#### 1. API Client作成

1. [developer.domo.com](https://developer.domo.com) にログイン
2. API Clientsページで新規作成
3. 必要なスコープを有効化:
   - `data` - DataSet操作（必須）
   - `dashboard` - Page/Card操作（オプション）
4. Client IDとClient Secretを取得

#### 2. 認証情報の設定

`.env` ファイルに追加:

```env
DOMO_CLIENT_ID=your-client-id-here
DOMO_CLIENT_SECRET=your-client-secret-here
```

#### 3. Pydantic設定の確認

[`src/data/config.py`](../../src/data/config.py) に以下が含まれていることを確認:

```python
class Settings(BaseSettings):
    # ...existing settings...
    
    # DOMO API
    domo_client_id: Optional[str] = None
    domo_client_secret: Optional[str] = None
```

### DataSet設定ファイル

[`backend/config/domo_datasets.yaml`](../../backend/config/domo_datasets.yaml) で全DataSetを一元管理:

```yaml
datasets:
  - name: "APAC DOT Due Date"
    domo_dataset_id: "c1cddf9d-3c25-4464-81bf-ee13e9ab1dd2"
    minio_dataset_id: "apac-dot-due-date"
    partition_column: "delivery completed date"
    description: "APAC DOT join Due Date change"
    enabled: true
  
  - name: "Sales Data"
    domo_dataset_id: "xxx-yyy-zzz"
    minio_dataset_id: "sales-data"
    partition_column: "sale_date"
    description: "Daily sales transactions"
    enabled: true
```

**設定項目:**

| 項目 | 必須 | 説明 | 例 |
|------|------|------|-----|
| `name` | ○ | DataSet識別名（人間向け） | "APAC DOT Due Date" |
| `domo_dataset_id` | ○ | DOMO DataSet ID（UUID） | "c1cddf9d-..." |
| `minio_dataset_id` | ○ | MinIOのdataset ID | "apac-dot-due-date" |
| `partition_column` | | パーティション分割カラム | "delivery completed date" |
| `description` | | DataSetの説明 | "APAC DOT..." |
| `enabled` | ○ | 有効/無効フラグ | true / false |

### DataSet IDの確認

DOMO URLから取得:

```
https://disney.domo.com/datasources/c1cddf9d-3c25-4464-81bf-ee13e9ab1dd2/details/overview
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                   この部分がdomo_dataset_id
```

### 実行方法

#### DataSet一覧を表示

```bash
python backend/scripts/load_domo.py --list
```

出力例:
```
=== Configured DOMO DataSets ===

Total: 2 datasets
Enabled: 2
Disabled: 0

1. [✓] APAC DOT Due Date
   DOMO ID: c1cddf9d-3c25-4464-81bf-ee13e9ab1dd2
   MinIO ID: apac-dot-due-date
   Partition: delivery completed date
```

#### 特定DataSetを取得

```bash
python backend/scripts/load_domo.py --dataset "APAC DOT Due Date"
```

#### 全DataSetを一括取得

```bash
python backend/scripts/load_domo.py --all
```

#### ドライラン（実行内容確認のみ）

```bash
python backend/scripts/load_domo.py --all --dry-run
```

### DomoApiETLクラスの直接使用

設定ファイルを使わず、直接コードで使用する場合:

```python
from backend.etl.etl_domo import DomoApiETL

# ETLインスタンス作成
etl = DomoApiETL(
    dataset_id="c1cddf9d-3c25-4464-81bf-ee13e9ab1dd2",
    partition_column="delivery completed date",
)

# ETL実行
etl.run("apac-dot-due-date")
```

### DataSetメタデータの確認

DataSetの構造を確認するスクリプト:

```bash
python backend/scripts/inspect_domo_dataset.py
```

出力例:
```
=== DataSet Information ===
Name: APAC DOT join Due Date change(first time)
Rows: 119466
Columns: 43
Created: 2024-09-24T07:52:30Z
Updated: 2026-02-06T00:28:20Z

=== Schema ===
Column Name                              Type           
-------------------------------------------------------
delivery completed date                  DATE           
delivery due date                        DATE           
radar product id                         STRING         
...

=== Suggested Partition Columns ===
  - delivery completed date
  - delivery due date
  - Delivery Completed Month
```

### パーティション分割の推奨

#### 日付カラムあり（推奨）

```yaml
partition_column: "delivery completed date"
```

- S3パス: `datasets/{minio_dataset_id}/partitions/date=YYYY-MM-DD/part-0000.parquet`
- 日付範囲フィルタが高速
- データ更新時に特定日付のみ置き換え可能

#### 日付カラムなし

```yaml
partition_column: null
```

- S3パス: `datasets/{minio_dataset_id}/data/part-0000.parquet`
- 常に全データ読み込み
- 小規模DataSetやマスタデータに適している

### DataSet追加手順

1. DOMO URLからDataSet IDを確認
2. （オプション）`inspect_domo_dataset.py`でメタデータ確認
3. `backend/config/domo_datasets.yaml`に設定追加
4. `python backend/scripts/load_domo.py --dataset "New DataSet"`で実行
5. MinIOコンソール（http://localhost:9001）で確認

### 定期実行（スケジューリング）

#### cron

```bash
# 毎日午前2時に全DataSet更新
0 2 * * * cd /path/to/project && source .venv/bin/activate && python backend/scripts/load_domo.py --all
```

#### Airflow

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG(
    'domo_etl',
    start_date=datetime(2026, 1, 1),
    schedule_interval='0 2 * * *',  # 毎日午前2時
)

load_domo = BashOperator(
    task_id='load_domo_datasets',
    bash_command='cd /path/to/project && source .venv/bin/activate && python backend/scripts/load_domo.py --all',
    dag=dag,
)
```

### トラブルシューティング

#### 認証エラー: 401 Unauthorized

**原因:** Client IDまたはClient Secretが間違っている

**対処法:**
1. `.env`ファイルの認証情報を確認
2. ダブルクォートが含まれている場合は削除
3. developer.domo.comでClient Secretを再生成

#### 権限エラー: 403 Forbidden

**原因:** API Clientに必要なスコープが設定されていない

**対処法:**
1. developer.domo.comにアクセス
2. API Clientの設定を開く
3. Scopesセクションで`data`を追加
4. 保存後、スクリプトを再実行

#### DataSet not found: 404

**原因:** DataSet IDが間違っている、またはアクセス権限がない

**対処法:**
1. DOMO URLからDataSet IDを再確認
2. DOMOでDataSetへのアクセス権限を確認

#### S3/MinIO接続エラー

**原因:** MinIO認証情報が設定されていない

**対処法:**

`.env`に追加:
```env
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=bi-datasets
```

### パフォーマンス最適化

#### 大規模DataSet（数十万行以上）

1. **パーティション分割を活用**
   - 日付カラムでパーティション分割
   - クエリ時に必要な日付範囲のみ読み込み

2. **不要なカラムを早期に削除**
   ```python
   class OptimizedDomoETL(DomoApiETL):
       def transform(self, df: pd.DataFrame) -> pd.DataFrame:
           # 必要なカラムのみ選択
           required_columns = ["id", "date", "value"]
           df = df[required_columns]
           return super().transform(df)
   ```

3. **定期実行の時間帯を分散**
   - 複数DataSetがある場合、実行時間を分散
   - DOMO APIのレート制限を考慮

#### API Rate Limit対策

DOMO APIにはレート制限があるため、大量のDataSetを連続実行する場合は注意が必要です。

```bash
# 1つずつ実行（エラー時に停止）
python backend/scripts/load_domo.py --dataset "DataSet 1"
python backend/scripts/load_domo.py --dataset "DataSet 2"

# または、設定ファイルでenabledを調整
```

### セキュリティ

1. **認証情報の管理**
   - `.env`ファイルは`.gitignore`に含まれている
   - Client Secretは絶対にコミットしない
   - 定期的にClient Secretをローテーション

2. **アクセス権限**
   - API ClientにはDataアクセスに必要な最小限のスコープのみ付与
   - 不要なDataSetへのアクセスは制限

3. **データの取り扱い**
   - 機密データはPDP（Personalized Data Permission）で制御
   - MinIOのバックアップを定期的に取得

### 参考リンク

- [DOMO API Documentation](../../docs/DOMO/DOMO_API_Documentation.md)
- [DOMO API Reference](../../docs/DOMO/DOMO_API_Reference.md)
- [Backend Config README](../../backend/config/README.md)
- [ETL Workflow SKILL](SKILL.md)

---

## 汎用API

### 認証方法

#### Bearer Token

```python
class BearerTokenApiETL(ApiETL):
    def __init__(self, endpoint: str, token: str):
        self.endpoint = endpoint
        self.token = token
    
    def extract(self) -> pd.DataFrame:
        response = requests.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.token}"},
        )
        response.raise_for_status()
        return pd.DataFrame(response.json())
```

#### API Key

```python
class ApiKeyETL(ApiETL):
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
    
    def extract(self) -> pd.DataFrame:
        # ヘッダーにAPI Keyを設定
        response = requests.get(
            self.endpoint,
            headers={"X-API-Key": self.api_key},
        )
        # またはクエリパラメータに設定
        # response = requests.get(
        #     self.endpoint,
        #     params={"api_key": self.api_key},
        # )
        response.raise_for_status()
        return pd.DataFrame(response.json())
```

#### Basic Auth

```python
class BasicAuthApiETL(ApiETL):
    def __init__(self, endpoint: str, username: str, password: str):
        self.endpoint = endpoint
        self.auth = (username, password)
    
    def extract(self) -> pd.DataFrame:
        response = requests.get(
            self.endpoint,
            auth=self.auth,
        )
        response.raise_for_status()
        return pd.DataFrame(response.json())
```

### ページネーション処理

**問題:** APIがページネーションをサポートしている

**解決策:**

```python
class PaginatedApiETL(ApiETL):
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
```

### エラーハンドリング

```python
class RobustApiETL(ApiETL):
    def extract(self) -> pd.DataFrame:
        try:
            response = requests.get(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=30,
            )
            response.raise_for_status()
            return pd.DataFrame(response.json())
        
        except requests.exceptions.Timeout:
            raise Exception("API request timeout")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise Exception("Rate limit exceeded")
            raise Exception(f"HTTP error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
```

### レート制限への対応

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class RateLimitedApiETL(ApiETL):
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
```

---

## RDS

### 接続プール管理

**推奨:** SQLAlchemyを使用した接続プール管理

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class RdsETLWithPool(RdsETL):
    def __init__(self, connection_string: str, query: str):
        self.connection_string = connection_string
        self.query = query
        self.engine = create_engine(
            self.connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # 接続の有効性を確認
        )
    
    def extract(self) -> pd.DataFrame:
        df = pd.read_sql_query(self.query, self.engine)
        return df
    
    def __del__(self):
        """クリーンアップ"""
        if hasattr(self, "engine"):
            self.engine.dispose()
```

### SQLクエリ最適化

**推奨事項:**

1. **必要なカラムのみ取得:**
```sql
-- ❌ 非効率
SELECT * FROM large_table;

-- ✅ 効率的
SELECT id, name, date, value FROM large_table;
```

2. **日付範囲でフィルタ:**
```sql
SELECT * FROM events
WHERE date >= '2024-01-01' AND date < '2024-02-01';
```

3. **インデックスを活用:**
```sql
-- インデックスが設定されているカラムでフィルタ
SELECT * FROM events WHERE user_id = 123;
```

### 大量データのストリーミング

**問題:** データ量が大きく、メモリ不足になる

**解決策:**

```python
class StreamingRdsETL(RdsETL):
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
```

### 接続文字列の例

**PostgreSQL:**
```python
connection_string = "postgresql://user:password@host:5432/database"
```

**MySQL:**
```python
connection_string = "mysql+pymysql://user:password@host:3306/database"
```

**環境変数から取得:**
```python
import os
from urllib.parse import quote_plus

connection_string = (
    f"postgresql://{quote_plus(os.getenv('DB_USER'))}:"
    f"{quote_plus(os.getenv('DB_PASSWORD'))}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)
```

---

## S3

### アクセス権限設定

**MinIO（ローカル開発）:**
```python
from src.data.s3_client import get_s3_client

# 環境変数から設定を読み込み
# S3_ENDPOINT=http://minio:9000
# S3_ACCESS_KEY=minioadmin
# S3_SECRET_KEY=minioadmin
```

**AWS S3:**
```python
# AWS認証情報は環境変数またはIAMロールから自動取得
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
# AWS_DEFAULT_REGION
```

### ファイル形式別の読み込み

#### CSV

```python
class S3CsvETL(S3RawETL):
    def extract(self) -> pd.DataFrame:
        client = get_s3_client()
        response = client.get_object(Bucket=self.bucket, Key=self.key)
        return pd.read_csv(response["Body"])
```

#### JSON

```python
class S3JsonETL(S3RawETL):
    def extract(self) -> pd.DataFrame:
        import json
        client = get_s3_client()
        response = client.get_object(Bucket=self.bucket, Key=self.key)
        data = json.loads(response["Body"].read().decode("utf-8"))
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        else:
            raise ValueError("Unexpected JSON format")
```

#### Parquet

```python
class S3ParquetETL(S3RawETL):
    def extract(self) -> pd.DataFrame:
        import pyarrow.parquet as pq
        client = get_s3_client()
        response = client.get_object(Bucket=self.bucket, Key=self.key)
        table = pq.read_table(response["Body"])
        return table.to_pandas()
```

### 複数ファイルの処理

**問題:** S3バケット内に複数のファイルがある

**解決策:**

```python
class MultiFileS3ETL(S3RawETL):
    def __init__(self, bucket: str, prefix: str, file_format: str = "csv"):
        self.bucket = bucket
        self.prefix = prefix
        self.file_format = file_format
    
    def extract(self) -> pd.DataFrame:
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
```

### 増分更新パターン

**問題:** 既存データを更新する必要がある

**解決策:**

```python
class IncrementalS3ETL(S3RawETL):
    def __init__(self, bucket: str, key: str, last_updated_column: str):
        self.bucket = bucket
        self.key = key
        self.last_updated_column = last_updated_column
    
    def extract(self) -> pd.DataFrame:
        # 新しいデータのみ取得（例: APIから）
        # ...
        return new_df
    
    def load(self, df: pd.DataFrame, dataset_id: str, partition_column: Optional[str] = None) -> None:
        # 既存データを読み込み
        client = get_s3_client()
        try:
            response = client.get_object(Bucket=self.bucket, Key=self.key)
            existing_df = pd.read_parquet(response["Body"])
            
            # 新しいデータとマージ
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            
            # 重複を削除（最新のデータを優先）
            combined_df = combined_df.sort_values(self.last_updated_column, ascending=False)
            combined_df = combined_df.drop_duplicates(subset=["id"], keep="first")
            
            df = combined_df
        except client.exceptions.NoSuchKey:
            # 既存データがない場合は新規データのみ
            pass
        
        # 親クラスのloadメソッドを呼び出し
        super().load(df, dataset_id, partition_column)
```

---

## 共通のベストプラクティス

### エラーハンドリング

すべてのETLクラスで適切なエラーハンドリングを実装します：

```python
def extract(self) -> pd.DataFrame:
    try:
        # データ取得処理
        return df
    except Exception as e:
        print(f"Error extracting data: {str(e)}")
        raise
```

### ログ出力

処理の進捗をログに出力します：

```python
import logging

logger = logging.getLogger(__name__)

def run(self, dataset_id: str) -> None:
    logger.info(f"Starting ETL for dataset: {dataset_id}")
    df = self.extract()
    logger.info(f"Extracted {len(df)} rows")
    df = self.transform(df)
    logger.info(f"Transformed data shape: {df.shape}")
    self.load(df, dataset_id)
    logger.info(f"Successfully loaded dataset '{dataset_id}'")
```

### データ検証

transformメソッドでデータ検証を行います：

```python
def transform(self, df: pd.DataFrame) -> pd.DataFrame:
    # 必須カラムの確認
    required_columns = ["id", "date", "value"]
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # 空のデータフレームの確認
    if len(df) == 0:
        raise ValueError("Empty dataframe")
    
    # Type inference
    from src.data.type_inferrer import infer_schema, apply_types
    schema = infer_schema(df)
    return apply_types(df, schema)
```
