# 開発者ガイド (CONTRIB)

最終更新: 2026-02-08

## 1. 前提条件

| 項目 | 要件 |
|------|------|
| Python | 3.9以上 (`pyproject.toml` の `requires-python`) |
| Docker | `docker compose` が使えること |
| 環境変数 | `.env.example` を `.env` にコピーして設定 |

## 2. セットアップ

### Docker Compose で起動

```bash
cp .env.example .env
docker compose up --build
```

確認先:
- Dash: `http://localhost:8050`
- MinIO Console: `http://localhost:9001`

### ローカルで直接起動

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## 3. `package.json` scripts 参照

このリポジトリのルートには `package.json` が存在しないため、npm scripts は未定義。

| Script Name | Command | Purpose |
|-------------|---------|---------|
| (none) | N/A | `package.json` がないため該当なし |

## 4. 実行コマンド一覧

| コマンド | 用途 |
|---------|------|
| `python3 app.py` | Dashアプリ起動 |
| `pytest` | 全テスト実行 |
| `pytest --cov=src --cov-report=term-missing` | カバレッジ付きテスト |
| `ruff check src/` | Lint |
| `mypy src/` | 型チェック |
| `docker compose up --build -d` | コンテナ起動（dash/minio/minio-init） |
| `docker compose logs -f dash` | Dashログ監視 |
| `docker compose run --rm test` | `test` サービスのデフォルトテスト実行 |
| `python3 backend/scripts/load_domo.py --list` | DOMO ETL対象一覧 |
| `python3 backend/scripts/load_domo.py --dataset \"<name>\"` | DOMO ETL単体実行 |
| `python3 backend/scripts/load_domo.py --all [--dry-run]` | DOMO ETL一括実行/ドライラン |
| `python3 backend/scripts/load_csv.py --list` | CSV ETL対象一覧 |
| `python3 backend/scripts/load_csv.py --dataset \"<name>\"` | CSV ETL単体実行 |
| `python3 backend/scripts/load_csv.py --all [--dry-run]` | CSV ETL一括実行/ドライラン |
| `python3 backend/scripts/clear_dataset.py <dataset_id>` | データセットのS3/MinIOオブジェクト削除 |
| `python3 scripts/upload_csv.py <csv> --dataset-id <id> [--partition-col <col>]` | 単体CSVアップロード |

`test` サービスは `profiles: [test]` なので `docker compose up` では自動起動しない。

## 5. 環境変数 (`.env.example`)

| 変数 | 目的 | 形式 | 既定値 (`.env.example`) | バリデーション/注意点 |
|------|------|------|-------------------------|----------------------|
| `S3_ENDPOINT` | S3/MinIO接続先 | URL or 空文字 | `http://localhost:9000` | `src/data/config.py` では省略可。Docker Composeのdashは `http://minio:9000` を使用 |
| `S3_REGION` | リージョン設定 | 文字列 | `ap-northeast-1` | `src/data/config.py` の既定値も同じ |
| `S3_BUCKET` | データ保存先バケット | 文字列 | `bi-datasets` | `src/data/config.py` の既定値も同じ |
| `S3_ACCESS_KEY` | S3アクセスキー | 文字列 | `minioadmin` | `src/data/config.py` では省略可 |
| `S3_SECRET_KEY` | S3シークレットキー | 文字列 | `minioadmin` | `src/data/config.py` では省略可 |
| `BASIC_AUTH_USERNAME` | フォーム認証ユーザー名 | 非空文字列 | `admin` | 未設定時は `settings.basic_auth_username` にフォールバック |
| `BASIC_AUTH_PASSWORD` | フォーム認証パスワード | 非空文字列 | `changeme` | 未設定時は `settings.basic_auth_password` にフォールバック |
| `DOMO_CLIENT_ID` | DOMO API認証 | 文字列 | 空 | `backend/etl/etl_domo.py` でDOMO ETL実行時は必須 |
| `DOMO_CLIENT_SECRET` | DOMO API認証 | 文字列 | 空 | `backend/etl/etl_domo.py` でDOMO ETL実行時は必須 |
| `ETL_MASKING_SECRET` | ETLマスキング用秘密鍵 | 文字列 | 空 | `masking.enabled: true` のdatasetでは必須 (`backend/etl/masking.py`) |

補足:
- `.env` の値にダブルクォートを含めない運用が前提（`CLAUDE.md` のETL注意点）。

## 6. テスト手順とカバレッジ要件

### 実行手順

```bash
pytest
pytest --cov=src --cov-report=term-missing
docker compose run --rm test
```

### 要件

- 強制閾値:
  - `pyproject.toml` に `--cov-fail-under` は未設定。閾値の自動強制は現状なし。
- 目標値:
  - `docs/tech-spec.md` のテスト戦略に「単体テスト 80%」の目標記載あり。

実運用では、PR前に `ruff check src/`、`mypy src/`、`pytest --cov=src` を実行する。
