# 運用ガイド (RUNBOOK)

最終更新: 2026-02-08

このRUNBOOKは、現行リポジトリで確認できる手順のみを記載する。  
クラウド本番基盤（ECS/EKS/VMなど）の標準手順は、このリポジトリ内に定義がないため `TBD`。

## 1. デプロイ前提

| 項目 | 内容 |
|------|------|
| コンテナ実行 | `docker compose` が利用可能 |
| 設定ファイル | `.env` が存在し、必要変数が設定済み |
| 依存関係 | `Dockerfile.dev` と `requirements.txt` で解決可能 |

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

## 3. モニタリングとアラート

### 現在このリポジトリで定義済み

- `docker-compose.yml` に `dash` と `minio` の `healthcheck` 定義あり
- ログ確認は `docker compose logs` ベース

### アラート設定

- リポジトリ内に通知連携（Slack/PagerDuty/CloudWatch Alarm等）の設定ファイルはなし
- 現行運用: 手動監視が基本
- 自動アラート標準は `TBD`

## 4. トラブルシューティング

### 4.1 アプリが起動しない

確認:
```bash
docker compose logs --tail=200 dash
```

対処:
- `.env` が存在するか確認
- ポート `8050` 競合を解消
- 依存更新後は `docker compose up --build -d` で再ビルド

### 4.2 データが表示されない

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

### 4.3 DOMO ETLが失敗する

対処:
- `.env` に `DOMO_CLIENT_ID` と `DOMO_CLIENT_SECRET` を設定
- 設定確認: `python3 backend/scripts/load_domo.py --list`
- ドライラン: `python3 backend/scripts/load_domo.py --all --dry-run`
- `.env` 値にダブルクォートを含めない

### 4.4 ETLマスキングで失敗する

症状:
- `ETL_MASKING_SECRET is required` 系エラー

対処:
- `.env` に `ETL_MASKING_SECRET` を設定
- 対象datasetの `masking.enabled` 設定を確認

### 4.5 フィルタ比較エラー（timezone）

症状:
- `Invalid comparison between dtype=datetime64[ns, UTC] and Timestamp`

対処:
- datetime列を timezone-naive に変換してからフィルタ処理する
- 例: `pd.to_datetime(col, utc=True).dt.tz_convert(None)`

## 5. ロールバック

### 5.1 アプリのロールバック（Compose運用）

```bash
docker compose down
# 既知の安定コミット/タグへ戻してから
docker compose up --build -d
```

注記:
- コミット/タグ運用ルールはリポジトリ内に固定定義がないため、チーム運用に従うこと。

### 5.2 データのロールバック

```bash
python3 backend/scripts/clear_dataset.py <dataset_id>
python3 backend/scripts/load_domo.py --dataset "<dataset_name>"
```

CSVデータの場合は `load_csv.py` を使用。

## 6. 未定義事項 (TBD)

- 本番環境の標準デプロイ先（ECS/EKS/VM等）
- 本番監視基盤とアラート通知経路
- 本番用シークレット管理標準
