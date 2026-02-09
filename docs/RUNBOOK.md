# 運用ガイド (RUNBOOK)

最終更新: 2026-02-09

このRUNBOOKは、現行リポジトリで確認できる手順のみを記載する。
クラウド本番基盤（ECS/EKS/VMなど）の標準手順は、このリポジトリ内に定義がないため [TBD]。

## 1. デプロイ前提

| 項目 | 内容 |
|------|------|
| コンテナ実行 | `docker compose` が利用可能 (`docker-compose` は非推奨) |
| 設定ファイル | `.env` が存在し、必要変数が設定済み |
| 依存関係 | `Dockerfile.dev` (Python 3.9-slim) と `requirements.txt` で解決 |

最低チェック:

```bash
ruff check src/
mypy src/
pytest --cov=src --cov-report=term-missing
```

## 2. デプロイ手順（現行リポジトリ運用）

### 手順A: Composeで更新起動

```bash
cp .env.example .env  # 初回のみ
docker compose down
docker compose up --build -d
```

### 手順B: 起動確認

```bash
docker compose ps
docker compose logs --tail=100 dash
docker compose logs --tail=100 minio
```

確認ポイント:
- `dash` と `minio` が `healthy`
- Dashにアクセスできる (`http://localhost:8050`)
- MinIO Consoleにアクセスできる (`http://localhost:9001`)

### 手順C: 初回データ投入

```bash
# DOMO ETL (DOMO_CLIENT_ID/DOMO_CLIENT_SECRET が .env に設定済みであること)
python3 backend/scripts/load_domo.py --all

# CSV ETL (CSVファイルが backend/data_sources/ に配置済みであること)
python3 backend/scripts/load_csv.py --all
```

## 3. モニタリングとアラート

### 現在このリポジトリで定義済み

- `docker-compose.yml` に `dash` と `minio` の `healthcheck` 定義あり
  - `dash`: `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8050')"` -- 10秒間隔、5回リトライ、start_period 40秒
  - `minio`: `curl -f http://localhost:9000/minio/health/live` -- 10秒間隔、5回リトライ、start_period 10秒
- ログ確認は `docker compose logs` ベース
- アプリケーションログ: structlog による構造化JSON出力

### アラート設定

- リポジトリ内に通知連携（Slack/PagerDuty/CloudWatch Alarm等）の設定ファイルはなし
- 現行運用: 手動監視が基本
- 自動アラート標準は [TBD]

## 4. ETL運用手順

ETLコマンドの詳細な一覧は [CONTRIB.md](CONTRIB.md) セクション3 を参照。

### 4.1 DOMO ETL

運用時の確認ポイント:
- 実行前にドライランで確認: `python3 backend/scripts/load_domo.py --all --dry-run`
- 登録データセット一覧確認: `python3 backend/scripts/load_domo.py --list`

現在の登録データセット (3件):
- APAC DOT join Due Date change(first time) -> apac-dot-due-date (除外フィルタ: exclude_flg)
- APAC DOT DDD Change + Issue(SQL) -> apac-dot-ddd-change-issue-sql (除外フィルタ: exclude_flg)
- Hamm_Dashboard -> hamm-dashboard

### 4.2 CSV ETL

運用時の確認ポイント:
- 実行前にドライランで確認: `python3 backend/scripts/load_csv.py --all --dry-run`
- 登録データセット一覧確認: `python3 backend/scripts/load_csv.py --list`

現在の登録データセット (1件):
- Cursor Usage Events -> cursor-usage (backend/data_sources/team-usage-events-*.csv)

### 4.3 データセット再投入

既存データを削除してから再投入する手順:

```bash
# 既存データを削除
python3 backend/scripts/clear_dataset.py <dataset_id>

# DOMOデータセットの場合
python3 backend/scripts/load_domo.py --dataset "<dataset_name>"

# CSVデータセットの場合
python3 backend/scripts/load_csv.py --dataset "<dataset_name>"
```

### 4.4 単体CSVアップロード (設定ファイル不要)

```bash
python3 scripts/upload_csv.py <csv_file> --dataset-id <id> [--partition-col <col>]
```

## 5. MinIO操作

### 5.1 MinIOコンソール

- URL: `http://localhost:9001`
- ユーザー: `minioadmin` / パスワード: `minioadmin`
- バケット: `bi-datasets`

### 5.2 MinIOデータ確認 (CLI)

```bash
# MinIO Clientを使用 (docker exec経由)
docker compose exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker compose exec minio mc ls local/bi-datasets/datasets/
```

### 5.3 MinIOボリュームリセット

```bash
docker compose down -v
docker compose up --build -d
# 再度データ投入が必要
python3 backend/scripts/load_domo.py --all
python3 backend/scripts/load_csv.py --all
```

## 6. トラブルシューティング

### 6.1 アプリが起動しない

確認:
```bash
docker compose logs --tail=200 dash
```

対処:
- `.env` が存在するか確認
- ポート `8050` 競合を解消
- 依存更新後は `docker compose up --build -d` で再ビルド

### 6.2 データが表示されない

確認:
```bash
docker compose logs --tail=200 dash
```

対処:
- `S3_ENDPOINT/S3_BUCKET` を再確認
- MinIO利用時は `minio-init` により `bi-datasets` バケットが作成されているか確認
- 必要データをETLで再投入:
  - `python3 backend/scripts/load_domo.py --all`
  - `python3 backend/scripts/load_csv.py --all`

### 6.3 DOMO ETLが失敗する

対処:
- `.env` に `DOMO_CLIENT_ID` と `DOMO_CLIENT_SECRET` を設定
- 設定確認: `python3 backend/scripts/load_domo.py --list`
- ドライラン: `python3 backend/scripts/load_domo.py --all --dry-run`
- `.env` 値にダブルクォートを含めない

### 6.4 CSV ETLが失敗する

対処:
- CSVファイルが `backend/data_sources/` に存在するか確認
- ファイルパターンが `csv_datasets.yaml` のglobと一致するか確認
- 設定確認: `python3 backend/scripts/load_csv.py --list`

### 6.5 ETLマスキングで失敗する

症状:
- `ETL_MASKING_SECRET is required` 系エラー

対処:
- `.env` に `ETL_MASKING_SECRET` を設定
- 対象datasetの `masking.enabled` 設定を確認

### 6.6 フィルタ比較エラー（timezone）

症状:
- `Invalid comparison between dtype=datetime64[ns, UTC] and Timestamp`

対処:
- datetime列を timezone-naive に変換してからフィルタ処理する
- 例: `pd.to_datetime(col, utc=True).dt.tz_convert(None)`

### 6.7 MinIOが起動しない

確認:
```bash
docker compose logs --tail=100 minio
docker compose ps
```

対処:
- ポート `9000`/`9001` 競合を解消
- volume をリセット: `docker compose down -v && docker compose up --build -d`

### 6.8 Dashドロップダウンが背面に隠れる

症状:
- ドロップダウンやDatePickerのポップアップが他のカード背面に回る

原因:
- Dash 4.x (Radix UI) のz-index不足とCSSスタッキングコンテキストの問題

対処:
- `assets/` のCSSで `[data-radix-popper-content-wrapper]` に `z-index: 9999 !important` を設定
- `.card` の `transition` を `box-shadow` と `border-color` に限定
- `.card:hover` の `transform` を削除

## 7. ロールバック

### 7.1 アプリのロールバック（Compose運用）

```bash
docker compose down
# 既知の安定コミット/タグへ戻してから
docker compose up --build -d
```

注記:
- コミット/タグ運用ルールはリポジトリ内に固定定義がないため、チーム運用に従うこと。

### 7.2 データのロールバック

```bash
python3 backend/scripts/clear_dataset.py <dataset_id>
python3 backend/scripts/load_domo.py --dataset "<dataset_name>"
```

CSVデータの場合は `load_csv.py` を使用。

## 8. 環境変数リファレンス

`.env.example` の全変数一覧は [CONTRIB.md](CONTRIB.md) セクション4 を参照。

必須変数チェック:
```bash
# 最小構成（ダッシュボードのみ）
S3_ENDPOINT, S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY
BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD

# DOMO ETL実行時に追加で必要
DOMO_CLIENT_ID, DOMO_CLIENT_SECRET

# マスキング有効データセットで追加で必要
ETL_MASKING_SECRET
```

## 9. 未定義事項 [TBD]

- 本番環境の標準デプロイ先（ECS/EKS/VM等） [TBD]
- 本番監視基盤とアラート通知経路 [TBD]
- 本番用シークレット管理標準 [TBD]
- ETL自動スケジューリング（cron/systemd timer の標準設定） [TBD]
- CI/CDパイプライン定義 [TBD]
- バックアップ/リストア手順 [TBD]
