# 開発者ガイド (CONTRIB)

最終更新: 2026-02-07 (rev.4)

## このドキュメントについて

- 役割: 開発者向けクイックスタート、開発コマンド、プロジェクト構造の説明
- 関連: 技術仕様は `docs/tech-spec.md` を参照
- 情報源:
  - `.env.example`
  - 既存の runbook (`docs/RUNBOOK.md`)

---

## 1. 前提条件

| ツール | バージョン |
|--------|-----------|
| Docker / Docker Compose | 最新安定版 |
| Python | 3.9+ |

---

## 2. 開発ワークフローとセットアップ

### クイックスタート

```bash
# 1. 環境変数ファイル作成
cp .env.example .env

# 2. 全サービス起動
docker compose up --build
```

| サービス | URL | 説明 |
|---------|-----|------|
| Dashアプリ | http://localhost:8050 | Plotly Dashダッシュボード（ログイン画面が表示される） |
| MinIO Console | http://localhost:9001 | S3互換ストレージ (admin: minioadmin/minioadmin) |

> Docker Compose 設定は `docker-compose.yml` を参照

### ローカル実行（Dockerを使わない場合）

```bash
# 仮想環境作成
python3 -m venv .venv
source .venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt

# アプリ起動
python3 app.py
```

---

## 3. 環境変数 (.env.example)

`.env.example` を `.env` にコピーして設定します。

| 変数名 | デフォルト値 | 目的 | 形式・バリデーション |
|--------|--------------|------|----------------------|
| `S3_ENDPOINT` | `http://localhost:9000` | S3エンドポイント。ローカル開発時は MinIO を想定 | URL形式。AWS本番では空文字列でも可 |
| `S3_REGION` | `ap-northeast-1` | S3リージョン | AWSリージョン文字列 |
| `S3_BUCKET` | `bi-datasets` | データセットバケット名 | 英数字・ハイフン |
| `S3_ACCESS_KEY` | `minioadmin` | S3アクセスキー（ローカル開発は MinIO デフォルト） | 文字列。IAMロール使用時は空可 |
| `S3_SECRET_KEY` | `minioadmin` | S3シークレットキー（ローカル開発は MinIO デフォルト） | 文字列。IAMロール使用時は空可 |
| `BASIC_AUTH_USERNAME` | `admin` | フォームログインのユーザー名 | 非空文字列 |
| `BASIC_AUTH_PASSWORD` | `changeme` | フォームログインのパスワード | 非空文字列 |

---

## 4. 開発コマンド

### Python開発

| コマンド | 説明 |
|---------|------|
| `python3 app.py` | Dashアプリ起動（開発モード、ポート8050） |
| `pytest` | テスト実行 |
| `pytest --cov=src` | カバレッジ付きテスト |
| `pytest --cov=src --cov-report=html` | HTMLカバレッジレポート生成 |
| `pytest -v -k "test_name"` | 特定テストのみ実行 |
| `ruff check src/` | リンティング |
| `ruff format src/` | フォーマット |
| `mypy src/` | 型チェック |

### Docker Compose

| コマンド | 説明 |
|---------|------|
| `docker compose up --build` | 全サービス起動（dash + minio + minio-init） |
| `docker compose up -d --build` | バックグラウンド起動 |
| `docker compose down` | 停止 |
| `docker compose down -v` | 停止 + ボリューム削除（MinIOデータも消える） |
| `docker compose logs -f dash` | Dashアプリログ確認 |
| `docker compose logs -f minio` | MinIOログ確認 |
| `docker compose run --rm test` | テスト実行（Docker内） |
| `docker compose run --rm test pytest -k "test_name"` | 特定テストのみ（Docker内） |
| `docker compose run --rm test pytest --cov=src` | カバレッジ付き（Docker内） |

### ETL実行

| コマンド | 説明 |
|---------|------|
| `python3 backend/scripts/load_domo.py --all` | DOMO ETL全データセット実行 |
| `python3 backend/scripts/load_csv.py --all` | CSV ETL全データセット実行 |
| `python3 backend/scripts/load_domo.py --dataset "Name"` | DOMO ETL個別実行 |
| `python3 backend/scripts/load_csv.py --dataset "Name"` | CSV ETL個別実行 |
| `python3 backend/scripts/clear_dataset.py <dataset_id>` | データセット削除 |
| `python3 scripts/upload_csv.py <csv_file> --dataset-id <id> [--partition-col <col>]` | CSVアップロードCLI |

DOMO ETL の設定は `backend/config/domo_datasets.yaml` で管理する。詳細は `backend/config/README.md` を参照。

### CSVアップロードCLIの使用例

```bash
# パーティションなし（単一ファイル）
python3 scripts/upload_csv.py data.csv --dataset-id my-dataset

# 日付カラムでパーティション分割
python3 scripts/upload_csv.py data.csv --dataset-id my-dataset --partition-col date
```

ETL は cron / systemd timer で定期実行する想定。

---

## 5. テスト

### テスト基準

| コンポーネント | 基準 |
|---------------|------|
| Python | pytest pass |

### カバレッジ要件

- 日常開発では `pytest --cov=src` の実行を推奨
- 重要変更では `--cov-report=term-missing` で未網羅の確認を推奨

### テスト実行

```bash
# 仮想環境で実行
source .venv/bin/activate
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html
```

### Dockerでテスト実行

```bash
# 全テスト実行
docker compose run --rm test

# 特定テストのみ
docker compose run --rm test pytest -v -k "test_config"

# カバレッジ付き
docker compose run --rm test pytest --cov=src --cov-report=term-missing
```

> test サービスは `profiles: [test]` を使用しているため、`docker compose up` では起動しません。
> `tests/` ディレクトリはボリュームマウントされているため、ローカルの変更が即座に反映されます。

---

## 6. プロジェクト構造

```
work_BI_PythonAll/
  app.py                         # Dashアプリエントリーポイント
  requirements.txt               # 依存パッケージ
  .env.example                   # 環境変数テンプレート
  docker-compose.yml             # Docker Compose設定（dash, minio, minio-init, test）
  Dockerfile.dev                 # 開発用Dockerfile (python:3.9-slim)
  pyproject.toml                 # pytest/ruff/mypy設定
  CLAUDE.md                      # プロジェクト開発メモ
  src/
    data/
      config.py                  # Pydantic Settings（環境変数管理）
      data_loader.py             # 共通データローダー
      data_source_registry.py    # chart_id -> dataset_id レジストリ
      parquet_reader.py          # Parquetファイル読み込み
      filter_engine.py           # フィルタロジック
    pages/
      cursor_usage/
        data_sources.yml         # Cursor Usageのデータソース設定
      apac_dot_due_date/
        data_sources.yml         # APAC DOT Due Dateのデータソース設定
  docs/
    CONTRIB.md
    RUNBOOK.md
    architecture.md
    tech-spec.md
```

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
# Python（リンティング、型チェック、テスト）
ruff check src/ && mypy src/ && pytest --cov=src

# フォーマット確認（変更がある場合は自動修正）
ruff format --check src/
```
