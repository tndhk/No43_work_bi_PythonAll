# 開発者ガイド (CONTRIB)

最終更新: 2026-02-07

## このドキュメントについて

- 役割: 開発者向けクイックスタートガイド、開発コマンド、プロジェクト構造の説明
- 関連: 技術仕様は [tech-spec.md](tech-spec.md) を参照
- 情報源: このドキュメントはソースコード、`.env.example`、`docker-compose.yml`、`requirements.txt` から生成

## フェーズ分割

- Phase 1: ダッシュボード基盤（マルチページ、サイドバー、チャート、フィルタ、キャッシュ、ETL） -- 実装済
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
| Dashアプリ | http://localhost:8050 | Plotly Dashダッシュボード（ログイン画面が表示される） |
| MinIO Console | http://localhost:9001 | S3互換ストレージ (admin: minioadmin/minioadmin) |

> docker-compose設定の詳細は `docker-compose.yml` を参照

---

## 3. 環境変数

`.env.example` を `.env` にコピーして設定。

### 環境変数一覧（.env.example 由来）

| カテゴリ | 変数名 | デフォルト値 | 説明 | バリデーション |
|---------|--------|-------------|------|---------------|
| S3 | `S3_ENDPOINT` | `http://localhost:9000` | S3エンドポイント。ローカル開発時はMinIO。Docker Compose使用時は `http://minio:9000` が自動設定される | URL形式。空文字列可（本番AWS時） |
| S3 | `S3_REGION` | `ap-northeast-1` | S3リージョン | AWSリージョン文字列 |
| S3 | `S3_BUCKET` | `bi-datasets` | Datasetバケット名 | 英数字・ハイフン |
| S3 | `S3_ACCESS_KEY` | `minioadmin` | S3アクセスキー。ローカル開発時はMinIOのデフォルト | 文字列。IAMロール使用時は空可 |
| S3 | `S3_SECRET_KEY` | `minioadmin` | S3シークレットキー。ローカル開発時はMinIOのデフォルト | 文字列。IAMロール使用時は空可 |
| 認証 | `BASIC_AUTH_USERNAME` | `admin` | フォームログインのユーザ名 | 非空文字列 |
| 認証 | `BASIC_AUTH_PASSWORD` | `changeme` | フォームログインのパスワード | 非空文字列 |

### 追加環境変数（config.py 由来、.env.example 未記載）

以下の変数は `src/data/config.py` の `Settings` クラスで定義されているが、`.env.example` には未記載。必要に応じて `.env` に追加する。

| カテゴリ | 変数名 | デフォルト値 | 説明 |
|---------|--------|-------------|------|
| Flask | `SECRET_KEY` | 自動生成（`secrets.token_urlsafe(32)`） | Flaskセッション秘密鍵。本番では固定値を設定すること |
| 認証 | `AUTH_PROVIDER_TYPE` | `form` | 認証プロバイダ種別。将来は `saml` に切替可能 |
| DOMO | `DOMO_CLIENT_ID` | `None` | DOMO API Client ID（DOMO ETL使用時に必要） |
| DOMO | `DOMO_CLIENT_SECRET` | `None` | DOMO API Client Secret（DOMO ETL使用時に必要） |

### 将来の環境変数（Phase 2）

| カテゴリ | 変数名 | デフォルト値 | 説明 |
|---------|--------|-------------|------|
| Vertex AI | `GOOGLE_APPLICATION_CREDENTIALS` | - | サービスアカウント JSON パス |
| Vertex AI | `VERTEX_AI_PROJECT` | - | GCP プロジェクト ID |
| Vertex AI | `VERTEX_AI_LOCATION` | `asia-northeast1` | Vertex AI リージョン |

> Docker Composeを使用する場合、`docker-compose.yml`内で S3 関連の環境変数が自動設定されます。`.env`ファイルはDocker Compose外で直接アプリを実行する場合に使用します。

---

## 4. 開発コマンド

### Python開発

| コマンド | 説明 |
|---------|------|
| `python app.py` | Dashアプリ起動（開発モード、ポート8050） |
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
| `python backend/etl/etl_api.py` | API ETL実行 |
| `python backend/etl/etl_s3.py` | S3 ETL実行 |
| `python backend/etl/etl_rds.py` | RDS ETL実行 |
| `python backend/etl/etl_csv.py` | CSV ETL実行 |
| `python backend/etl/etl_domo.py` | DOMO API ETL（DomoApiETLクラスをインポートして使用） |
| `python scripts/upload_csv.py <csv_file> --dataset-id <id> [--partition-col <col>]` | CSVアップロードCLI |

### DOMO ETL管理スクリプト

| コマンド | 説明 |
|---------|------|
| `python backend/scripts/load_domo.py --list` | 設定済みDOMOデータセット一覧 |
| `python backend/scripts/load_domo.py --dataset "NAME"` | 特定DOMOデータセットをロード |
| `python backend/scripts/load_domo.py --all` | 有効な全DOMOデータセットをロード |
| `python backend/scripts/load_domo.py --all --dry-run` | ドライラン（実行せず内容確認） |
| `python backend/scripts/load_cursor_usage.py` | Cursor利用CSVをS3にロード |
| `python backend/scripts/clear_dataset.py <dataset_id>` | 指定データセットをS3から削除 |

DOMO ETLの設定は `backend/config/domo_datasets.yaml` で管理する。詳細は `backend/config/README.md` を参照。

### CSVアップロードCLIの使用例

```bash
# パーティションなし（単一ファイル）
python scripts/upload_csv.py data.csv --dataset-id my-dataset

# 日付カラムでパーティション分割
python scripts/upload_csv.py data.csv --dataset-id my-dataset --partition-col date
```

ETL は cron / systemd timer で定期実行する想定。

---

## 5. テスト

### テスト基準

| コンポーネント | 基準 |
|---------------|------|
| Python | pytest pass |

### テスト構成

```
tests/
  conftest.py                     # 共通フィクスチャ（mock_s3, sample_parquet_file等）
  unit/
    auth/
      test_session_auth.py          # Flask-Login認証テスト
    charts/
      test_templates.py             # チャートテンプレートテスト
      test_plotly_theme.py          # Plotlyテーマテスト
    components/
      test_filters.py               # フィルタコンポーネントテスト
      test_cards.py                 # KPIカードテスト
      test_sidebar.py               # サイドバーテスト
    core/
      test_cache.py                 # キャッシュテスト
      test_logging.py               # ログテスト
    data/
      test_config.py                # 設定テスト
      test_csv_parser.py            # CSVパーサーテスト
      test_dataset_summarizer.py    # データセット統計テスト
      test_filter_engine.py         # フィルタエンジンテスト
      test_parquet_reader.py        # Parquetリーダーテスト
      test_parquet_reader_partition.py # パーティション読み込みテスト
      test_type_inferrer.py         # 型推論テスト
    pages/
      test_dashboard_home.py        # ホームページテスト
      test_apac_dot_due_date.py     # APAC DOT Due Dateページ統合テスト
      apac_dot_due_date/            # APAC DOT Due Dateモジュール別テスト
        test_constants.py             # 定数テスト
        test_data_loader.py           # データロード・フィルタテスト
        test_filters.py               # フィルタUI構成テスト
        test_layout.py                # レイアウト構成テスト
        test_callbacks.py             # コールバックテスト
        charts/
          test_ch00_reference_table.py # Reference Tableチャートテスト
    test_exceptions.py              # 例外テスト
    test_layout.py                  # レイアウトテスト
  etl/
    test_base_etl.py                # BaseETLテスト
    test_etl_csv.py                 # CSV ETLテスト
    test_etl_skeletons.py           # ETLスケルトンテスト
    test_resolve_csv_path.py        # CSV パス解決テスト
  scripts/
    test_upload_csv.py              # CSVアップロードCLIテスト
```

### テスト実行

```bash
# 仮想環境で実行
source .venv/bin/activate
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html
```

### Dockerでテスト実行（推奨）

```bash
# 全テスト実行
docker compose run --rm test

# 特定テストのみ
docker compose run --rm test pytest -v -k "test_config"

# カバレッジ付き
docker compose run --rm test pytest --cov=src --cov-report=term-missing
```

> testサービスは `profiles: [test]` を使用しているため、`docker compose up` では起動しません。
> `tests/` ディレクトリはボリュームマウントされているため、ローカルの変更が即座に反映されます。

---

## 6. コーディング規約

### Python

- フォーマッタ/リンタ: Ruff (line-length: 100, target: py39)
- 型チェック: mypy (strict, 一部 allow_untyped_defs)
- 命名: snake_case (変数/関数), PascalCase (クラス)
- テスト: pytest
- S3モック: moto[s3]

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

---

## 8. プロジェクト構造

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
    __init__.py
    exceptions.py                # カスタム例外（DatasetFileNotFoundError）
    layout.py                    # メインレイアウト（認証に応じてコンテンツ切替）
    auth/                        # 認証レイヤー（Flask-Login）
      __init__.py
      flask_login_setup.py       # Flask-Login初期化、Userモデル
      providers.py               # AuthProviderプロトコル、FormAuthProvider
      login_layout.py            # ログインページUI
      login_callbacks.py         # ログイン処理コールバック
      layout_callbacks.py        # 認証状態に応じたレイアウト切替
    data/                        # データアクセス層
      __init__.py
      config.py                  # Pydantic Settings（環境変数管理）
      s3_client.py               # S3クライアント（boto3 wrapper）
      parquet_reader.py          # Parquetファイル読み込み & パーティション対応
      csv_parser.py              # CSV解析 & エンコーディング検出（chardet）
      type_inferrer.py           # カラム型推論
      dataset_summarizer.py      # データセット統計プロファイリング
      filter_engine.py           # フィルタロジック（カテゴリ、日付範囲）
      models.py                  # Pydanticデータモデル
    charts/                      # 可視化レイヤー
      __init__.py
      templates.py               # チャートテンプレート（Line, Bar, Pie, Table, Pivot等）
      plotly_theme.py            # Plotlyテーマ設定（Warm Professional Light）
    core/                        # インフラ層
      __init__.py
      cache.py                   # TTLキャッシュ初期化（flask-caching, SimpleCache, 300秒）
      logging.py                 # 構造化ログ（structlog）
    pages/                       # ダッシュボードページ（Dash Pages API）
      __init__.py
      dashboard_home.py          # ホームページ（登録ページ一覧カード表示）
      cursor_usage.py            # Cursor利用状況ダッシュボード
      apac_dot_due_date/         # APAC DOT Due Date ダッシュボード（モジュール化）
        __init__.py              # Dash register_page & layout() 定義
        _constants.py            # データセットID、カラムマッピング、ID接頭辞
        _data_loader.py          # データ読み込み & フィルタ適用ロジック
        _filters.py              # フィルタUI構成ビルダー
        _layout.py               # ページレイアウト構成ビルダー
        _callbacks.py            # Dashコールバック登録（@callback）
        charts/                  # チャートビルダーサブパッケージ
          __init__.py            # サブパッケージ定義
          _ch00_reference_table.py # Chart 0: Reference Tableピボットテーブル
    components/                  # 再利用可能UIコンポーネント
      __init__.py
      sidebar.py                 # 左ナビゲーションサイドバー
      sidebar_callbacks.py       # サイドバーコールバック（ログアウト等）
      filters.py                 # フィルタ選択コンポーネント（日付範囲、カテゴリ）
      cards.py                   # KPIカードコンポーネント
  backend/                       # ETLレイヤー
    __init__.py
    config/                      # ETL設定
      domo_datasets.yaml         # DOMOデータセット定義
      README.md                  # 設定ファイルの使い方
    data_sources/                # データソース接続（未実装スタブ）
      __init__.py
    etl/                         # ETLスクリプト
      __init__.py
      base_etl.py                # 抽象BaseETLクラス（extract/transform/load）
      etl_api.py                 # API -> Parquet
      etl_s3.py                  # S3 Raw -> Parquet
      etl_rds.py                 # RDS -> Parquet
      etl_csv.py                 # CSV -> Parquet
      etl_domo.py                # DOMO API -> Parquet（OAuth2認証）
      resolve_csv_path.py        # CSVファイルパス解決ユーティリティ
    scripts/                     # ETL管理スクリプト
      __init__.py
      load_domo.py               # DOMOデータセットローダー（YAML設定ベース）
      load_cursor_usage.py       # Cursor利用CSVローダー
      clear_dataset.py           # データセット削除ユーティリティ
  scripts/                       # CLIツール
    __init__.py
    upload_csv.py                # CSVアップロードCLI
  assets/                        # 静的アセット（Warm Professional Light テーマ）
    00-reset.css                 # CSSリセット、CSS Custom Properties（カラーパレット）
    01-typography.css            # タイポグラフィ（Noto Sans JP, Inter）
    02-layout.css                # レイアウト（サイドバー、ページ構造）
    03-components.css            # コンポーネントスタイル（カード、フィルタ、ドロップダウンz-index修正含む）
    04-animations.css            # アニメーション
    05-charts.css                # チャートスタイル
    06-login.css                 # ログインページスタイル
  tests/                         # テスト
    conftest.py                  # 共通フィクスチャ
    unit/                        # ユニットテスト
      pages/
        apac_dot_due_date/       # APAC DOT モジュール別テスト
          charts/                # チャートビルダーテスト
    etl/                         # ETLテスト
    scripts/                     # CLIテスト
  docs/                          # ドキュメント
    CONTRIB.md                   # 開発者ガイド（このファイル）
    RUNBOOK.md                   # 運用ガイド
    tech-spec.md                 # 技術仕様書
    architecture.md              # アーキテクチャ図
  codemaps/                      # コードマップ
    architecture.md
    frontend.md
    backend.md
    data.md
```

### ディレクトリ説明

- `src/pages/`: 各ダッシュボードページの Python 定義ファイル（Dash Pages API で自動登録）
- `src/pages/apac_dot_due_date/`: モジュール化されたページパッケージ（詳細は「APAC DOT Due Date モジュール化設計」セクションを参照）
- `src/components/`: 再利用可能な UI コンポーネント（サイドバー、フィルタ、カード等）
- `src/auth/`: Flask-Login ベースの認証レイヤー（FormAuthProvider + 将来SAML対応のProviderプロトコル）
- `src/data/`: データアクセス層（S3/Parquet読み込み、フィルタ適用、型推論、設定管理）
- `src/charts/`: チャートテンプレートとテーマ設定（Warm Professional Light テーマ）
- `src/core/`: キャッシュとログの共通インフラ
- `backend/etl/`: ETL スクリプト（データソースごとに独立、BaseETLを継承）
- `backend/scripts/`: ETL 管理スクリプト（DOMO ローダー、データセット削除等）
- `backend/config/`: ETL 設定ファイル（DOMO データセット YAML）
- `scripts/`: CLI ツール（CSV アップロード）
- `assets/`: CSS スタイルシート（番号順に読み込まれる、Warm Professional Light テーマ）

---

## 9. 主要依存パッケージ

| パッケージ | バージョン | 用途 |
|-----------|-----------|------|
| dash | >=2.14.0 | Webフレームワーク |
| dash-bootstrap-components | >=1.5.0 | Bootstrap UIコンポーネント |
| flask-login | >=0.6.3 | セッション認証（Flask-Login） |
| flask-caching | >=2.0.0 | TTLキャッシュ |
| pandas | >=2.0.0 | データフレーム処理 |
| pyarrow | >=14.0.0 | Parquet読み書き |
| boto3 | >=1.34.0 | AWS SDK (S3) |
| plotly | >=5.0.0 | 可視化 |
| chardet | >=5.0.0 | エンコーディング検出 |
| numpy | >=1.24.0 | 数値計算 |
| structlog | >=23.0.0 | 構造化ログ |
| python-dotenv | >=1.0.0 | 環境変数管理 |
| pydantic-settings | >=2.0.0 | 設定管理（型安全） |
| moto[s3] | >=5.0.0 | S3モック（テスト用） |
| pytest | >=7.0.0 | テストフレームワーク |
| pytest-cov | >=4.0.0 | カバレッジレポート |

> 旧バージョンのドキュメントに記載されていた `dash-auth` は使用されていません。認証は `flask-login` + カスタム `FormAuthProvider` で実装されています。

---

## 10. 認証アーキテクチャ

現在の認証は Flask-Login + FormAuthProvider で実装されている。

```
ブラウザ -> /login -> login_layout.py (ログイン画面)
                     -> login_callbacks.py (フォーム送信処理)
                     -> providers.py (FormAuthProvider.authenticate)
                     -> flask_login_setup.py (Userモデル、セッション管理)
                     -> layout_callbacks.py (認証状態に応じてレイアウト切替)
```

- 未認証: ログインページを表示
- 認証済: サイドバー + ページコンテンツを表示
- ログアウト: sidebar_callbacks.py で処理

### 将来のSAML対応（Phase 3）

`src/auth/providers.py` に `AuthProvider` プロトコルが定義されており、`SAMLAuthProvider` を追加することでSAML認証に切替可能。切替は `AUTH_PROVIDER_TYPE` 環境変数で制御する想定。

---

## 11. APAC DOT Due Date モジュール化設計

### 設計背景

APAC DOT Due Date ダッシュボードは、当初 `src/pages/apac_dot_due_date.py` の単一ファイルに実装されていた。機能拡張に伴い以下の問題が顕在化したため、モジュール化を実施した:

- 単一ファイルが肥大化し、責務が混在
- フィルタUI、データロード、コールバック、チャート構築が密結合
- 個別テストが困難

### モジュール構造と責務

```
src/pages/apac_dot_due_date/
  __init__.py              # Dash register_page + layout() エントリーポイント
  _constants.py            # 定数定義（DATASET_ID, ID_PREFIX, COLUMN_MAP, BREAKDOWN_MAP）
  _data_loader.py          # データ読み込み（load_filter_options, load_and_filter_data）
  _filters.py              # フィルタUIビルダー（build_filter_layout -> 5つのdbc.Row）
  _layout.py               # ページレイアウトビルダー（build_layout -> html.Div）
  _callbacks.py            # Dashコールバック登録（update_all_charts）
  charts/
    __init__.py            # チャートサブパッケージ
    _ch00_reference_table.py  # Chart 0: ピボットテーブル（build関数）
```

| モジュール | 責務 | 依存先 |
|-----------|------|--------|
| `__init__.py` | ページ登録、layout()定義 | `_layout`, `_callbacks` |
| `_constants.py` | ハードコード文字列の一元管理 | なし（純粋な定数） |
| `_data_loader.py` | S3データ読み込み、フィルタ適用 | `ParquetReader`, `cache`, `filter_engine`, `_constants` |
| `_filters.py` | フィルタUIコンポーネント構築 | `dcc`, `dbc`, `components.filters` |
| `_layout.py` | ページ全体のレイアウト構築 | `_constants`, `_data_loader`, `_filters` |
| `_callbacks.py` | Dashコールバック（ユーザー操作 -> チャート更新） | `_constants`, `_data_loader`, `charts` |
| `charts/_ch00_reference_table.py` | ピボットテーブル構築（純粋関数、I/Oなし） | `_constants`, `dash_table` |

### データフロー

```
[ユーザー操作: フィルタ変更]
    |
    v
[_callbacks.py: update_all_charts()]
    |
    +-> _data_loader.load_and_filter_data()
    |     +-> get_cached_dataset() -> S3/Parquet読み込み
    |     +-> PRC custom filter
    |     +-> apply_filters(df, FilterSet)
    |
    +-> charts._ch00_reference_table.build(filtered_df, breakdown, mode)
          +-> pivot: breakdown_column x month
          +-> GRAND TOTAL行 + AVG列追加
          +-> パーセントモード変換（任意）
          +-> DataTable構築
    |
    v
[画面: タイトル + DataTable を表示]
```

### 命名規則

- プライベートモジュール: `_` プレフィックス（`_constants.py`, `_layout.py` 等）
- チャートモジュール: `_ch{番号:02d}_{snake_case名}.py` 形式
- コンポーネントID: `apac-dot-` プレフィックス（他ページとの衝突回避）

### 今後のチャート追加手順

新しいチャートを APAC DOT Due Date ページに追加する手順:

1. `charts/` に `_ch{NN}_{name}.py` を作成
   - `build(filtered_df, ...) -> tuple[str, Any]` 関数を定義
   - 純粋関数として実装（I/Oなし、DataFrame操作 + Dashコンポーネント構築のみ）

2. `_layout.py` にチャート表示エリアを追加
   - `html.H3(id="apac-dot-chart-{NN}-title")` + `html.Div(id="apac-dot-chart-{NN}")`

3. `_callbacks.py` の `update_all_charts` を更新
   - Output に新チャートのタイトルとコンテンツを追加
   - 新チャートの `build()` を呼び出し、返り値を return タプルに追加

4. テストを追加
   - `tests/unit/pages/apac_dot_due_date/charts/test_ch{NN}_{name}.py`
   - `build()` の正常系、空データ、エッジケースをテスト

---

## 12. 開発フロー

### Phase 1: ダッシュボード基盤（実装済）

1. マルチページルーティング実装（Dash Pages API）
2. 左サイドバーナビゲーション実装
3. ページ定義の仕組み構築（`src/pages/`）
4. チャート表示 UI（テンプレート: Line, Bar, Pie, Table, Pivot, Summary Number）
5. フィルタ UI コンポーネント（カテゴリ/日付範囲）
6. TTL キャッシュ実装（flask-caching, SimpleCache, 300秒）
7. パーティション読み込み対応
8. ETL スクリプト群作成（`backend/etl/`）
9. CLI アップロードツール作成
10. Flask-Login認証実装（FormAuthProvider）
11. DOMO API ETL実装
12. 実ダッシュボード実装（Cursor Usage, APAC DOT Due Date）
13. APAC DOT Due Date ページモジュール化（パッケージ構造 + charts サブパッケージ）
14. デザインテーマ移行（Minimal Luxury Dark -> Warm Professional Light）

### Phase 2: LLM 質問機能

1. Vertex AI クライアント実装
2. チャットパネル UI 実装
3. コンテキスト構築（DatasetSummary + サンプル）
4. コードサンドボックス実装
5. LLM レスポンス解析・実行

### Phase 3: 本番認証・ロール管理

1. SAML 認証実装（SAMLAuthProvider）
2. ロール管理機能
3. ページ単位アクセス制御

## 13. 関連ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| `docs/tech-spec.md` | 技術仕様書 |
| `docs/RUNBOOK.md` | 本番運用・トラブルシューティングガイド |
| `docs/architecture.md` | システムアーキテクチャ図 |
| `backend/config/README.md` | DOMO DataSet設定の使い方 |
| `CLAUDE.md` | プロジェクト開発メモ |
| `codemaps/architecture.md` | アーキテクチャコードマップ |
| `codemaps/frontend.md` | フロントエンドコードマップ |
| `codemaps/backend.md` | バックエンドコードマップ |
| `codemaps/data.md` | データ層コードマップ |
