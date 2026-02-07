# 運用ガイド (RUNBOOK)

Last Updated: 2026-02-07 (rev.4)

## このドキュメントについて

- 役割: デプロイメント、モニタリング、トラブルシューティング、ロールバック手順
- 関連: 開発者ガイドは `docs/CONTRIB.md`、技術仕様は `docs/tech-spec.md` を参照

---

## 1. デプロイメント前の確認

### 前提条件

- Docker / Docker Compose 最新安定版
- AWS CLI がセットアップ済み
- 本番環境の AWS credentials が利用可能
- 本番 S3 バケット、RDS、その他リソースが構築済み

### デプロイ前チェックリスト

```bash
# 1. すべてのテストが通っているか確認
pytest --cov=src

# 2. リンティング、型チェック、フォーマット確認
ruff check src/
mypy src/

# 3. Git ワークフロー確認
git status                    # ローカル変更がない
git log -1 --oneline          # 最新コミット確認
git branch                    # ブランチ確認
```

---

## 2. デプロイメント手順

### ローカル環境からの本番デプロイ（AWS ECS / Fargate 想定）

#### Step 1: Docker イメージの構築

```bash
# イメージを構築
docker build -t bi-dashboard:latest .

# ECR にタグ付け
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.ap-northeast-1.amazonaws.com

docker tag bi-dashboard:latest <ACCOUNT_ID>.dkr.ecr.ap-northeast-1.amazonaws.com/bi-dashboard:latest
```

#### Step 2: ECR にプッシュ

```bash
docker push <ACCOUNT_ID>.dkr.ecr.ap-northeast-1.amazonaws.com/bi-dashboard:latest
```

#### Step 3: ECS タスク定義を更新

```bash
# タスク定義 JSON を編集してイメージリビジョンを更新
aws ecs register-task-definition --cli-input-json file://task-definition.json

# デプロイ（サービス更新）
aws ecs update-service \
  --cluster bi-dashboard-cluster \
  --service bi-dashboard-service \
  --force-new-deployment
```

#### Step 4: デプロイ状況の確認

```bash
# サービスのタスク状況を確認
aws ecs describe-services --cluster bi-dashboard-cluster --services bi-dashboard-service

# ログを確認
aws logs tail /ecs/bi-dashboard --follow
```

---

## 3. 環境設定（本番）

### ベース環境変数（.env.example 由来）

ローカル開発向けの変数一覧は [CONTRIB.md](CONTRIB.md) sec.3 を参照。本番運用での主な違い:

- `S3_ENDPOINT`: 本番では `https://s3.ap-northeast-1.amazonaws.com` または空文字列
- `S3_ACCESS_KEY` / `S3_SECRET_KEY`: AWS Secrets Manager より取得（IAMロール使用時は不要）
- `BASIC_AUTH_PASSWORD`: AWS Secrets Manager より取得。Phase 3で SAML に置き換え

### 追加設定（.env.example 以外）

本番運用では以下の設定が必要になる場合があります。`.env.example` には含まれていないため、運用側で明示的に管理します。

| 変数 | 説明 | 備考 |
|------|------|------|
| `SECRET_KEY` | Flaskセッション秘密鍵 | Secrets Manager より取得（本番では固定値が必要） |
| `AUTH_PROVIDER_TYPE` | 認証プロバイダ種別 | `form`（Phase 3で `saml` に切替可能） |
| `DOMO_CLIENT_ID` | DOMO API Client ID | DOMO Developer Portalで発行 |
| `DOMO_CLIENT_SECRET` | DOMO API Client Secret | DOMO Developer Portalで発行 |
| `RDS_HOST` | RDS エンドポイント | RDS 使用時のみ |
| `RDS_PORT` | RDS ポート | 通常 `5432` |
| `RDS_USER` | RDS ユーザー | Secrets Manager より取得 |
| `RDS_PASSWORD` | RDS パスワード | Secrets Manager より取得 |
| `RDS_DATABASE` | データベース名 | - |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP サービスアカウント JSON | Vertex AI 使用時 |
| `VERTEX_AI_PROJECT` | GCP プロジェクト ID | Vertex AI 使用時 |
| `VERTEX_AI_LOCATION` | Vertex AI リージョン | `asia-northeast1` |

### AWS Secrets Manager でシークレット管理

```bash
# 本番シークレットの登録例
aws secretsmanager create-secret \
  --name bi-dashboard-secrets \
  --secret-string '{"S3_ACCESS_KEY":"xxx","S3_SECRET_KEY":"yyy","SECRET_KEY":"zzz","BASIC_AUTH_PASSWORD":"aaa"}'

# ECS タスク定義から参照
"secrets": [
  {
    "name": "S3_ACCESS_KEY",
    "valueFrom": "arn:aws:secretsmanager:ap-northeast-1:ACCOUNT_ID:secret:bi-dashboard-secrets:S3_ACCESS_KEY::"
  }
]
```

---

## 4. モニタリング

### ログ確認

```bash
# CloudWatch ログを監視
aws logs tail /ecs/bi-dashboard --follow

# エラーレベルのログのみ取得
aws logs filter-log-events \
  --log-group-name /ecs/bi-dashboard \
  --filter-pattern "ERROR"
```

### メトリクス確認

- CPU 使用率
- メモリ使用率
- HTTP レスポンスコード
- S3 API 呼び出し数

### アラート設定（CloudWatch）

```bash
# CPU > 80% でアラート
aws cloudwatch put-metric-alarm \
  --alarm-name bi-dashboard-cpu-high \
  --alarm-description "CPU usage high" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

---

## 5. 一般的な問題とトラブルシューティング

### Issue 1: ダッシュボードが起動しない

症状: ECS タスクが起動直後に停止

原因の調査:

```bash
# ログを確認
aws logs tail /ecs/bi-dashboard --follow

# タスク定義を確認
aws ecs describe-tasks --cluster bi-dashboard-cluster --tasks <TASK_ARN>
```

解決策:

- 環境変数が正しく設定されているか確認（特に `SECRET_KEY`）
- S3 バケットへのアクセス権限確認
- Docker イメージのビルドエラーを確認

### Issue 2: S3 からデータが読み込めない

症状: "Dataset file not found" エラー、または空のダッシュボード

原因の調査:

```bash
# IAM アクセスキーの権限確認
aws iam get-user

# S3 バケットへのアクセステスト
aws s3 ls s3://bi-datasets/

# オブジェクトの確認
aws s3 ls s3://bi-datasets/datasets/ --recursive
```

解決策:

- IAM ポリシーが `s3:GetObject` / `s3:ListBucket` を含むか確認
- バケットのリージョンが正しいか確認
- `datasets/<dataset_id>/data/part-0000.parquet` または `datasets/<dataset_id>/partitions/` のパス構造を確認
- ファイル形式が Parquet か確認

### Issue 3: メモリ不足エラー

症状: "MemoryError" / "OOM Killed"

解決策:

- ECS タスク定義のメモリ制限を増加
- 大きな Parquet ファイルを分割
- Parquet フィルタリングの推進（列フィルタ、行グループフィルタ）

### Issue 4: キャッシュが効いていない

症状: 毎回フル読み込みされている（ログでキャッシュミスが頻発）

確認方法:

- キャッシュは `flask-caching` の `SimpleCache`（インメモリ）を使用
- TTL はデフォルト300秒（5分）
- キャッシュキー: `dataset:<dataset_id>`

解決策:

- キャッシュ TTL 設定を確認（`src/core/cache.py`）
- プロセスが再起動されていないか確認（SimpleCacheはプロセスメモリに保持）
- 本番でスケールアウトする場合は Redis キャッシュバックエンドの使用を検討
- キャッシュキーの衝突確認

### Issue 5: ログインできない

症状: ログインフォームでユーザー名/パスワードを入力してもログインできない

原因の調査:

- `BASIC_AUTH_USERNAME` と `BASIC_AUTH_PASSWORD` 環境変数が正しく設定されているか確認
- `SECRET_KEY` が設定されているか確認（セッション管理に必須）

解決策:

- 環境変数の値にダブルクォートが含まれていないか確認（`.env`ファイルでは `BASIC_AUTH_PASSWORD=changeme` と記載、`"changeme"` は誤り）
- `SECRET_KEY` を固定値に設定（プロセス再起動でセッションが無効化されるのを防ぐ）

### Issue 6: DOMO ETLが失敗する

症状: `load_domo.py` 実行時にエラー

原因の調査:

```bash
# 設定ファイルを確認
cat backend/config/domo_datasets.yaml

# ドライランで設定内容確認
python backend/scripts/load_domo.py --all --dry-run
```

解決策:

- `DOMO_CLIENT_ID` と `DOMO_CLIENT_SECRET` が `.env` に設定されているか確認
- `.env` の値にダブルクォートが含まれていないか確認
- DOMO Dataset IDが正しいか確認（DOMOのURL末尾のUUID）
- ネットワーク接続を確認（`api.domo.com` へのアクセス）

### Issue 7: Dash 4.x ドロップダウンが背面に隠れる

症状: DateRangeやDropdownのプルダウンがKPIカードの背面に隠れる

原因: Dash 4.x (Radix) のポップアップの z-index が低い

解決策:

- `assets/03-components.css` に z-index 修正が含まれているか確認
- Docker利用時は `./assets:/app/assets` のボリュームマウントを確認
- ブラウザのハードリロード（Ctrl+Shift+R）で確認

### Issue 8: APAC DOT Due Date フィルタ値が表示されない

症状: フィルタドロップダウンの選択肢が空、またはフィルタが機能しない

原因の調査:

- S3にデータセット `apac-dot-due-date` が存在するか確認
- `_data_loader.load_filter_options()` がエラーなく完了しているか確認（エラー時は空リストを返す）

解決策:

- DOMO ETLでデータをロード: `python backend/scripts/load_domo.py --dataset "APAC DOT join Due Date change(first time)"`
- Parquetファイルのカラム名が `_constants.py` の `COLUMN_MAP` と一致しているか確認
- キャッシュが古い場合はアプリ再起動でキャッシュクリア

---

## 6. ロールバック手順

### 本番環境でのロールバック

#### 方法 1: 前のタスク定義にロールバック

```bash
# 前のタスク定義リビジョンを取得
aws ecs describe-task-definition \
  --task-definition bi-dashboard:1 \
  --region ap-northeast-1

# ロールバック（サービス更新）
aws ecs update-service \
  --cluster bi-dashboard-cluster \
  --service bi-dashboard-service \
  --task-definition bi-dashboard:1 \
  --force-new-deployment
```

#### 方法 2: 前の Docker イメージをデプロイ

```bash
# ECR イメージ履歴を確認
aws ecr describe-images --repository-name bi-dashboard

# 前のイメージをタグ
docker pull <ACCOUNT_ID>.dkr.ecr.ap-northeast-1.amazonaws.com/bi-dashboard:previous-tag
docker tag <ACCOUNT_ID>.dkr.ecr.ap-northeast-1.amazonaws.com/bi-dashboard:previous-tag <ACCOUNT_ID>.dkr.ecr.ap-northeast-1.amazonaws.com/bi-dashboard:latest
docker push <ACCOUNT_ID>.dkr.ecr.ap-northeast-1.amazonaws.com/bi-dashboard:latest

# タスク定義を更新してデプロイ
aws ecs update-service --cluster bi-dashboard-cluster --service bi-dashboard-service --force-new-deployment
```

### データのロールバック

DOMO ETLで取り込んだデータに問題がある場合:

```bash
# 問題のあるデータセットを削除
python backend/scripts/clear_dataset.py <dataset_id>

# 正しいデータを再取り込み
python backend/scripts/load_domo.py --dataset "Dataset Name"
```

---

## 7. 定期メンテナンス

### 日次タスク

- ログの監視（エラーがないか）
- S3 データ同期の確認

### 週次タスク

- キャッシュの有効性確認
- ダッシュボードレスポンス時間の測定
- ETL ジョブの成功確認（DOMOデータの最新性）

### 月次タスク

- セキュリティアップデート確認
- 依存パッケージのセキュリティ脆弱性チェック
- ディスク容量と AWS リソース使用量の確認

```bash
# 依存パッケージの脆弱性チェック
pip-audit requirements.txt
```

---

## 8. 本番初期設定チェックリスト

- [ ] S3 バケット作成 & IAM ポリシー設定
- [ ] ECR リポジトリ作成
- [ ] ECS クラスター & サービス作成
