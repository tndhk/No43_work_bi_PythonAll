# 運用ガイド (RUNBOOK)

Last Updated: 2026-02-06

## このドキュメントについて

- 役割: デプロイメント、モニタリング、トラブルシューティング、ロールバック手順
- 関連: 開発者ガイドは [CONTRIB.md](CONTRIB.md)、技術仕様は [tech-spec.md](tech-spec.md) を参照

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

### 必須環境変数（本番環境）

| 変数 | 説明 | 備考 |
|------|------|------|
| `S3_ENDPOINT` | AWS S3 エンドポイント | 本番: `https://s3.ap-northeast-1.amazonaws.com` |
| `S3_REGION` | AWS リージョン | `ap-northeast-1` |
| `S3_BUCKET` | データセットバケット | 本番用 S3 バケット名 |
| `S3_ACCESS_KEY` | IAM アクセスキー | AWS Secrets Manager より取得 |
| `S3_SECRET_KEY` | IAM シークレットキー | AWS Secrets Manager より取得 |
| `BASIC_AUTH_USERNAME` | 認証ユーザー名 | 本番は SAML に置き換え（Phase 3） |
| `BASIC_AUTH_PASSWORD` | 認証パスワード | AWS Secrets Manager より取得 |
| `RDS_HOST` | RDS エンドポイント | RDS インスタンスのエンドポイント |
| `RDS_PORT` | RDS ポート | 通常 `5432` |
| `RDS_USER` | RDS ユーザー | Secrets Manager より取得 |
| `RDS_PASSWORD` | RDS パスワード | AWS Secrets Manager より取得 |
| `RDS_DATABASE` | データベース名 | - |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP サービスアカウント JSON | Phase 2 以降（Vertex AI） |
| `VERTEX_AI_PROJECT` | GCP プロジェクト ID | Phase 2 以降 |
| `VERTEX_AI_LOCATION` | Vertex AI リージョン | `asia-northeast1` |

### AWS Secrets Manager でシークレット管理

```bash
# 本番シークレットの登録例
aws secretsmanager create-secret \
  --name bi-dashboard-secrets \
  --secret-string '{"S3_ACCESS_KEY":"xxx","S3_SECRET_KEY":"yyy",...}'

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

**症状**: ECS タスクが起動直後に停止

**原因の調査**:

```bash
# ログを確認
aws logs tail /ecs/bi-dashboard --follow

# タスク定義を確認
aws ecs describe-tasks --cluster bi-dashboard-cluster --tasks <TASK_ARN>
```

**解決策**:

- 環境変数が正しく設定されているか確認
- S3 バケットへのアクセス権限確認
- RDS へのネットワーク接続確認
- Docker イメージのビルドエラーを確認

### Issue 2: S3 からデータが読み込めない

**症状**: "Failed to load Parquet files from S3"

**原因の調査**:

```bash
# IAM アクセスキーの権限確認
aws iam get-user

# S3 バケットへのアクセステスト
aws s3 ls s3://bi-datasets/

# オブジェクトの確認
aws s3 ls s3://bi-datasets/ --recursive
```

**解決策**:

- IAM ポリシーが `s3:GetObject` / `s3:ListBucket` を含むか確認
- バケットのリージョンが正しいか確認
- ファイル名にタイポがないか確認
- ファイル形式が Parquet か確認

### Issue 3: メモリ不足エラー

**症状**: "MemoryError" / "OOM Killed"

**解決策**:

- ECS タスク定義のメモリ制限を増加
- 大きな Parquet ファイルを分割
- Parquet フィルタリングの推進（列フィルタ、行グループフィルタ）

### Issue 4: キャッシュが効いていない

**症状**: 毎回フル読み込みされている

**確認方法**:

```bash
# キャッシュディレクトリの確認
ls -la /tmp/flask_cache

# キャッシュファイルのタイムスタンプ確認
stat /tmp/flask_cache/...
```

**解決策**:

- キャッシュ TTL 設定を確認（`src/core/cache.py`）
- Redis キャッシュバックエンドの使用を検討
- キャッシュキーの衝突確認

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

---

## 7. 定期メンテナンス

### 日次タスク

- ログの監視（エラーがないか）
- S3 データ同期の確認

### 週次タスク

- キャッシュの有効性確認
- ダッシュボードレスポンス時間の測定
- ETL ジョブの成功確認

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
- [ ] RDS インスタンス作成 & 初期データロード
- [ ] ECR リポジトリ作成
- [ ] ECS クラスター & サービス作成
- [ ] CloudWatch ロググループ作成
- [ ] AWS Secrets Manager でシークレット登録
- [ ] SSL/TLS 証明書の設定
- [ ] DNS / ロードバランサー設定
- [ ] バックアップ戦略の実装
- [ ] 災害復旧計画の文書化

---

## 9. 参考資料

- AWS ECS デプロイメントガイド: https://docs.aws.amazon.com/ja_jp/AmazonECS/latest/developerguide/
- AWS Secrets Manager: https://docs.aws.amazon.com/ja_jp/secretsmanager/
- CloudWatch ログ: https://docs.aws.amazon.com/ja_jp/AmazonCloudWatch/latest/logs/
