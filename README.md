# BI Dashboard

Plotly Dash ベースの BI ダッシュボードアプリケーション。

## 主な機能

- S3/MinIO から Parquet データを読み込み、インタラクティブなダッシュボードを表示
- Flask-Login によるフォーム認証
- 設定駆動の ETL パイプライン（CSV、DOMO API 対応）

## クイックスタート

### Docker Compose（推奨）

```bash
cp .env.example .env
docker compose up --build
```

- Dash: http://localhost:8050
- MinIO Console: http://localhost:9001

### ローカル開発

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| [CONTRIB.md](docs/CONTRIB.md) | 開発者ガイド（セットアップ、コマンド、テスト） |
| [RUNBOOK.md](docs/RUNBOOK.md) | 運用ガイド（デプロイ、モニタリング、トラブルシューティング） |
| [architecture.md](docs/architecture.md) | システムアーキテクチャ |
| [tech-spec.md](docs/tech-spec.md) | 技術仕様 |
| [CLAUDE.md](CLAUDE.md) | AI アシスタント向け開発ルール |

## プロジェクト構造

```
├── src/              # アプリケーションソース
│   ├── pages/        # ダッシュボードページ
│   ├── components/   # UI コンポーネント
│   ├── charts/       # チャート・テーブル構築
│   ├── data/         # データアクセス層
│   ├── auth/         # 認証
│   ├── core/         # キャッシュ、ロギング
│   └── utils/        # ヘルパー関数
├── backend/          # ETL バックエンド
│   ├── config/       # ETL 設定（YAML）
│   ├── etl/          # ETL 実装
│   └── scripts/      # ETL ローダー
├── tests/            # テストコード
├── assets/           # CSS
└── docs/             # ドキュメント
```

## テスト

```bash
pytest
pytest --cov=src --cov=backend --cov-report=html
```

## ライセンス

Proprietary
