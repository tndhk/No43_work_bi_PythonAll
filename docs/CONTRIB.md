# 開発者ガイド (CONTRIB)

最終更新: 2026-02-06

## このドキュメントについて

- 役割: 開発者向けクイックスタートガイド、開発コマンド、プロジェクト構造の説明
- 関連: 技術仕様は [tech-spec.md](tech-spec.md) を参照

## フェーズ分割

- Phase 1: ダッシュボード基盤（マルチページ、サイドバー、チャート、フィルタ、キャッシュ、ETL）
- Phase 2: LLM 質問機能（Vertex AI 連携、チャットパネル、サンドボックス実行）
- Phase 3: 本番認証（SAML）、ロール管理

---

## 1. 前提条件

| ツール | バージョン |
|--------|-----------|
| Docker / Docker Compose | 最新安定版 |
| Python | 3.9+ |

---

## 2. クイックスタート

```bash
# 1. 環境変数ファイル作成
cp .env.example .env

# 2. 全サービス起動
docker compose up --build
```

| サービス | URL | 説明 |
|---------|-----|------|
| Dashアプリ | http://localhost:8050 | Plotly Dashダッシュボード |
| MinIO Console | http://localhost:9001 | S3互換ストレージ (admin: minioadmin/minioadmin) |

> docker-compose設定の詳細は `docker-compose.yml` を参照

---

## 3. 環境変数

`.env.example` を `.env` にコピーして設定。

### 環境変数一覧

| カテゴリ | 変数名 | デフォルト値 | 説明 |
|---------|--------|-------------|------|
| S3 | `S3_ENDPOINT` | `http://localhost:4566` | S3エンドポイント（ローカル開発時はMinIO） |
| S3 | `S3_REGION` | `ap-northeast-1` | S3リージョン |
| S3 | `S3_BUCKET` | `bi-datasets` | Datasetバケット名 |
| S3 | `S3_ACCESS_KEY` | `test` | S3アクセスキー（ローカルのみ） |
| S3 | `S3_SECRET_KEY` | `test` | S3シークレットキー（ローカルのみ） |
| 認証 | `BASIC_AUTH_USERNAME` | `admin` | Basic認証ユーザ名（ローカル開発） |
| 認証 | `BASIC_AUTH_PASSWORD` | `changeme` | Basic認証パスワード（ローカル開発） |
| Vertex AI（Phase 2） | `GOOGLE_APPLICATION_CREDENTIALS` | - | サービスアカウント JSON パス |
| Vertex AI（Phase 2） | `VERTEX_AI_PROJECT` | - | GCP プロジェクト ID |
| Vertex AI（Phase 2） | `VERTEX_AI_LOCATION` | `asia-northeast1` | Vertex AI リージョン |

---

## 4. 開発コマンド

### Python開発

| コマンド | 説明 |
|---------|------|
| `python app.py` | Dashアプリ起動（開発モード） |
| `pytest` | テスト実行 |
| `pytest --cov=src` | カバレッジ付きテスト |
| `pytest -v -k "test_name"` | 特定テストのみ実行 |
| `ruff check src/` | リンティング |
| `ruff format src/` | フォーマット |
| `mypy src/` | 型チェック |

### Docker Compose

| コマンド | 説明 |
|---------|------|
| `docker compose up --build` | 全サービス起動 |
| `docker compose up -d --build` | バックグラウンド起動 |
| `docker compose down` | 停止 |
| `docker compose down -v` | 停止 + データ削除 |
| `docker compose logs -f dash` | Dashアプリログ確認 |
| `docker compose logs -f minio` | MinIOログ確認 |

### ETL実行

| コマンド | 説明 |
|---------|------|
| `python backend/etl/etl_api.py` | API ETL実行 |
| `python backend/etl/etl_s3.py` | S3 ETL実行 |
| `python backend/etl/etl_rds.py` | RDS ETL実行 |
| `python backend/etl/etl_csv.py` | CSV ETL実行 |
| `python scripts/upload_csv.py <file.csv>` | CSVアップロードCLI |

ETL は cron / systemd timer で定期実行する想定。

---

## 5. テスト

### テスト基準

| コンポーネント | 基準 |
|---------------|------|
| Python | pytest pass |

### テスト実行

```bash
# 仮想環境で実行
source .venv/bin/activate
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html
```

---

## 6. コーディング規約

### Python

- フォーマッタ/リンタ: Ruff (line-length: 100, target: py39)
- 型チェック: mypy (strict, 一部 allow_untyped_defs)
- 命名: snake_case (変数/関数), PascalCase (クラス)
- テスト: pytest

---

## 7. Git ワークフロー

### ブランチ命名

- `feature/xxx` - 機能開発
- `fix/xxx` - バグ修正
- `docs/xxx` - ドキュメント
- `refactor/xxx` - リファクタリング

### コミットメッセージ

```
<type>: <summary>

<body (optional)>
```

type: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### PR前チェック

```bash
# Python
ruff check src/ && mypy src/ && pytest --cov=src
```

---

## 8. プロジェクト構造

```
No42_work_bi_PythonAll/
├── app.py                    # Dashアプリエントリーポイント
├── requirements.txt          # 依存パッケージ
├── .env.example             # 環境変数テンプレート
├── docker-compose.yml       # Docker Compose設定
├── Dockerfile.dev           # 開発用Dockerfile
├── pyproject.toml          # pytest/ruff/mypy設定
├── src/
│   ├── __init__.py
│   ├── auth/                # 認証
│   │   └── basic_auth.py   # Basic認証設定
│   ├── data/               # データ層
│   │   ├── config.py      # 設定管理
│   │   ├── s3_client.py   # S3クライアント
│   │   ├── parquet_reader.py  # Parquet読み込み
│   │   ├── csv_parser.py   # CSV解析
│   │   ├── type_inferrer.py   # 型推論
│   │   ├── dataset_summarizer.py  # データセット統計
│   │   └── models.py      # データモデル
│   ├── charts/             # チャート
│   │   └── templates.py   # チャートテンプレート
│   ├── core/               # コア機能
│   │   └── logging.py     # ログ設定
│   ├── pages/              # ページ定義（Phase 1）
│   │   ├── __init__.py
│   │   ├── dashboard_home.py
│   │   └── ...            # 各ページの Python ファイル
│   ├── components/          # UIコンポーネント（Phase 1）
│   │   ├── __init__.py
│   │   ├── filters.py     # フィルタコンポーネント
│   │   ├── cards.py        # KPIカード
│   │   └── ...
│   ├── callbacks/          # コールバック（Phase 1）
│   │   ├── __init__.py
│   │   └── ...            # ページごとのコールバック
│   ├── llm/                # LLM機能（Phase 2）
│   │   ├── __init__.py
│   │   ├── vertex_client.py  # Vertex AI クライアント
│   │   ├── sandbox.py     # コードサンドボックス
│   │   └── chat_panel.py  # チャットパネルUI
│   ├── exceptions.py      # カスタム例外
│   ├── layout.py          # Dashレイアウト（共通）
│   └── callbacks.py       # Dashコールバック（共通）
├── backend/                # ETLレイヤー（Phase 1）
│   ├── data_sources/       # データソース接続
│   │   ├── api_client.py
│   │   ├── s3_client.py
│   │   └── rds_client.py
│   └── etl/                # ETLスクリプト
│       ├── etl_api.py
│       ├── etl_s3.py
│       ├── etl_rds.py
│       └── etl_csv.py
└── scripts/                # CLIツール
    └── upload_csv.py        # CSVアップロードCLI
```

### ディレクトリ説明

- `src/pages/`: 各ダッシュボードページの Python 定義ファイル
- `src/components/`: 再利用可能な UI コンポーネント（フィルタ、カード等）
- `src/callbacks/`: ページごとのコールバック関数
- `src/llm/`: LLM 質問機能（Phase 2）
- `backend/data_sources/`: 各種データソースへの接続クライアント
- `backend/etl/`: ETL スクリプト（データソースごとに独立）
- `scripts/`: CLI ツール（CSV アップロード等）

---

## 9. 主要依存パッケージ

| パッケージ | バージョン | 用途 |
|-----------|-----------|------|
| dash | >=2.14.0 | Webフレームワーク |
| dash-bootstrap-components | >=1.5.0 | Bootstrap UIコンポーネント |
| dash-auth | >=2.0.0 | Basic認証 |
| pandas | >=2.0.0 | データフレーム処理 |
| pyarrow | >=14.0.0 | Parquet読み書き |
| boto3 | >=1.34.0 | AWS SDK (S3) |
| plotly | >=5.0.0 | 可視化 |
| chardet | >=5.0.0 | エンコーディング検出 |
| numpy | >=1.24.0 | 数値計算 |
| structlog | >=23.0.0 | 構造化ログ |
| python-dotenv | >=1.0.0 | 環境変数管理 |
| pydantic-settings | >=2.0.0 | 設定管理 |
| flask-caching | >=2.0.0 | TTLキャッシュ（Phase 1） |
| google-cloud-aiplatform | >=1.0.0 | Vertex AI SDK（Phase 2） |

---

## 10. 開発フロー

### Phase 1: ダッシュボード基盤

1. マルチページルーティング実装（Dash Pages API）
2. 左サイドバーナビゲーション実装
3. ページ定義の仕組み構築（`src/pages/`）
4. チャート表示 UI（既存テンプレート活用）
5. フィルタ UI コンポーネント（カテゴリ/日付）
6. TTL キャッシュ実装
7. パーティション読み込み対応
8. ETL スクリプト群作成（`backend/etl/`）
9. CLI アップロードツール作成

### Phase 2: LLM 質問機能

1. Vertex AI クライアント実装
2. チャットパネル UI 実装
3. コンテキスト構築（DatasetSummary + サンプル）
4. コードサンドボックス実装
5. LLM レスポンス解析・実行

### Phase 3: 本番認証・ロール管理

1. SAML 認証実装
2. ロール管理機能
3. ページ単位アクセス制御

## 11. 関連ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| `docs/tech-spec.md` | 技術仕様書 |
| `docs/RUNBOOK.md` | 本番運用・トラブルシューティングガイド |
| `docs/architecture.md` | システムアーキテクチャ図 |
| `CLAUDE.md` | プロジェクト開発メモ |
