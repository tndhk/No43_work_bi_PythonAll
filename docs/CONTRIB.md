# 開発者ガイド (CONTRIB)

最終更新: 2026-02-10

## 1. 前提条件

| 項目 | 要件 |
|------|------|
| Python | 3.9以上 (`pyproject.toml` の `requires-python`) |
| Docker | `docker compose` が使えること (`docker-compose` は非推奨) |
| 環境変数 | `.env.example` を `.env` にコピーして設定 |
| OS | macOS の場合 `python3` を使用 (`python` コマンドは存在しない場合あり) |

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
pip install -r requirements-dev.txt   # 開発・テスト用依存
python3 app.py
```

依存ファイルの役割:

| ファイル | 内容 |
|----------|------|
| `requirements.txt` | ランタイム依存（Dash, pandas, boto3 等） |
| `requirements-dev.txt` | 開発・テスト依存（pytest, ruff, mypy, moto） |

## 3. 実行コマンド一覧

### アプリケーション

| コマンド | 用途 |
|---------|------|
| `python3 app.py` | Dashアプリ起動 |
| `docker compose up --build -d` | コンテナ起動（dash/minio/minio-init） |
| `docker compose logs -f dash` | Dashログ監視 |
| `docker compose ps` | コンテナ状態確認 |

### テスト・品質

| コマンド | 用途 |
|---------|------|
| `pytest` | 全テスト実行（カバレッジは `pyproject.toml` の `addopts` で自動付与） |
| `pytest -v --tb=short` | 詳細表示・短縮トレースバック（CI相当） |
| `docker compose run --rm test` | `test` サービスのデフォルトテスト実行 |
| `ruff check src/` | Lint（ruff >=0.4.0） |
| `mypy src/` | 型チェック（mypy >=1.9.0、設定は `pyproject.toml` の `[tool.mypy]`） |

PR前の品質チェック（3点セット）:

```bash
ruff check src/
mypy src/
pytest -v --tb=short
```

これらは GitHub Actions CI でも同じ内容が並列実行される（セクション10参照）。

### ETL

| コマンド | 用途 |
|---------|------|
| `python3 backend/scripts/load_domo.py --list` | DOMO ETL対象一覧 |
| `python3 backend/scripts/load_domo.py --dataset "<name>"` | DOMO ETL単体実行 |
| `python3 backend/scripts/load_domo.py --all [--dry-run]` | DOMO ETL一括実行/ドライラン |
| `python3 backend/scripts/load_csv.py --list` | CSV ETL対象一覧 |
| `python3 backend/scripts/load_csv.py --dataset "<name>"` | CSV ETL単体実行 |
| `python3 backend/scripts/load_csv.py --all [--dry-run]` | CSV ETL一括実行/ドライラン |
| `python3 backend/scripts/clear_dataset.py <dataset_id>` | データセットのS3/MinIOオブジェクト削除 |
| `python3 scripts/upload_csv.py <csv> --dataset-id <id> [--partition-col <col>]` | 単体CSVアップロード |

`test` サービスは `profiles: [test]` なので `docker compose up` では自動起動しない。

## 4. 環境変数 (`.env.example`)

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
| `ETL_MASKING_SECRET` | ETLマスキング用秘密鍵 (HMAC-SHA256) | 文字列 | 空 | `masking.enabled: true` のdatasetでは必須 (`backend/etl/masking.py`) |

補足:
- `.env` の値にダブルクォートを含めない運用が前提（`CLAUDE.md` のETL注意点）。

## 5. テスト手順とカバレッジ要件

### テストディレクトリ構造

```
tests/
  conftest.py              # 共通フィクスチャ
  helpers/
    dash_test_utils.py     # Dashテスト用ユーティリティ
    test_dash_test_utils.py
  unit/
    auth/                  # 認証テスト
      test_session_auth.py
    charts/                # チャート/テーブルビルダーテスト
      test_chart_builder.py
      test_empty_states.py
      test_plotly_theme.py
      test_specs.py
      test_table_builder.py
      test_templates.py
    components/            # UIコンポーネントテスト
      test_cards.py
      test_filters.py
      test_sidebar.py
    core/                  # キャッシュ・ログテスト
      test_cache.py
      test_logging.py
    data/                  # データ層テスト
      test_common_data_loader.py
      test_config.py
      test_csv_parser.py
      test_data_source_registry.py
      test_dataset_summarizer.py
      test_filter_engine.py
      test_parquet_reader.py
      test_parquet_reader_partition.py
      test_type_inferrer.py
    pages/                 # ページ別テスト
      test_apac_dot_due_date.py
      test_dashboard_home.py
      test_page_imports.py
      apac_dot_due_date/
        test_callbacks.py
        test_chart_builders.py
        test_constants.py
        test_data_loader.py
        test_data_sources.py
        test_filters.py
        test_layout.py
      cursor_usage/
        test_callbacks.py
        test_constants.py
        test_data_loader.py
        test_data_sources.py
      hamm_overview/
        test_callbacks.py
        test_chart_builders.py
        test_constants.py
        test_data_loader.py
        test_data_sources.py
        test_layout.py
    utils/                 # ユーティリティテスト
      test_callback_helpers.py
      test_data_helpers.py
      test_filter_helpers.py
    test_exceptions.py
    test_layout.py
  etl/                     # ETLパイプラインテスト
    test_base_etl.py
    test_etl_csv.py
    test_etl_domo.py
    test_etl_skeletons.py
    test_load_csv.py
    test_load_domo.py
    test_masking.py
    test_resolve_csv_path.py
  scripts/                 # スクリプトテスト
    test_upload_csv.py
```

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

## 6. プロジェクト構造

### ソース構造の概要

```
src/
  auth/                    # 認証 (Flask-Login)
    flask_login_setup.py   # Flask-Login初期化、Userモデル
    providers.py           # AuthProviderプロトコル、FormAuthProvider
    login_layout.py        # ログインページUI
    login_callbacks.py     # ログインフォームコールバック
    layout_callbacks.py    # 認証切替レイアウト
  charts/                  # 可視化レイヤー
    chart_builder.py       # DataFrame + ChartSpec -> go.Figure
    table_builder.py       # DataFrame + TableSpec -> DataTable
    empty_states.py        # 空状態/エラー状態プレースホルダー
    specs.py               # ChartSpec, TableSpec (frozen dataclass)
    plotly_theme.py        # テーマ適用
    templates.py           # レガシーテンプレート (render_*_chart)
  components/              # 再利用可能UIコンポーネント (sidebar, filters, cards)
    sidebar.py             # 左ナビゲーションサイドバー
    sidebar_callbacks.py   # サイドバーコールバック (logout等)
    filters.py             # フィルタ選択コンポーネント
    cards.py               # KPIカードコンポーネント
  core/                    # インフラ (cache, logging)
    cache.py               # TTLキャッシュ初期化 (flask-caching)
    logging.py             # 構造化ログ (structlog)
  data/                    # データアクセス層 (S3, Parquet, filter)
    config.py              # Settings & 環境変数 (Pydantic)
    s3_client.py           # S3クライアント (boto3 wrapper)
    parquet_reader.py      # Parquetファイル読み込み & パーティション
    csv_parser.py          # CSV解析 & エンコーディング検出
    data_loader.py         # 共通データローダー
    data_source_registry.py # データソースレジストリ
    type_inferrer.py       # カラム型推論
    dataset_summarizer.py  # データプロファイリング & 統計
    filter_engine.py       # フィルタロジック (カテゴリ, 日付範囲)
    models.py              # Pydanticモデル
  pages/                   # ダッシュボードページ
    dashboard_home.py      # ホームページ (カードグリッド) -- Tier 1
    cursor_usage/          # Cursor Usage ダッシュボード -- Tier 2
      __init__.py          # ページ登録 + layout()
      _constants.py        # DATASET_ID, ID_PREFIX, COLUMN_MAP
      _data_loader.py      # データ読込 & フィルタリング
      _layout.py           # レイアウトビルダー
      _callbacks.py        # Dashコールバック (KPIs, charts, table)
    apac_dot_due_date/     # APAC DOT Due Date ダッシュボード -- Tier 2
      __init__.py          # ページ登録 + layout()
      _constants.py        # DATASET_ID, COLUMN_MAP, CHART_SPECS, TABLE_SPECS
      _data_loader.py      # データ読込 & フィルタリング
      _filters.py          # フィルタUI (slicer + category)
      _layout.py           # レイアウトビルダー
      _callbacks.py        # Dashコールバック
      _chart_builders.py   # カスタム集計・描画ロジック
    hamm_overview/         # HAMM Overview ダッシュボード -- Tier 2
      __init__.py          # ページ登録 + layout()
      _constants.py        # DATASET_ID, ID_PREFIX, COLUMN_MAP
      _data_loader.py      # データ読込, フィルタリング, cadence列生成
      _filters.py          # フィルタUI (slicer + category + cadence chip)
      _layout.py           # レイアウトビルダー (MantineProvider)
      _callbacks.py        # Dashコールバック (volume table/chart, task table)
      _chart_builders.py   # カスタム集計・描画ロジック
  utils/                   # ヘルパー
    callback_helpers.py    # register_clear_callbacks()
    data_helpers.py        # データ変換ヘルパー
    filter_helpers.py      # フィルタ構築ヘルパー
  layout.py                # メインレイアウト
  exceptions.py            # カスタム例外

backend/
  config/                  # ETL設定 (YAML)
    domo_datasets.yaml     # DOMO DataSet定義 (3件)
    csv_datasets.yaml      # CSV DataSet定義 (1件)
  etl/                     # ETLパイプライン
    base_etl.py            # 抽象基底クラス
    etl_csv.py             # CSV -> Parquet
    etl_domo.py            # DOMO API -> Parquet
    masking.py             # HMAC-SHA256 マスキング
    resolve_csv_path.py    # CSVパス解決
    etl_api.py, etl_s3.py, etl_rds.py  # スケルトン
  scripts/                 # CLI entrypoints
    load_domo.py           # DOMO ETLローダー
    load_csv.py            # CSV ETLローダー
    clear_dataset.py       # データセット削除

scripts/
  upload_csv.py            # 単体CSVアップロード
```

### 共通基盤 (全ページで使用)

```python
# チャート/テーブル構築
from src.charts.table_builder import build_table
from src.charts.chart_builder import build_chart
from src.charts.specs import TableSpec, ChartSpec

# 空状態・エラー状態
from src.charts.empty_states import (
    create_empty_figure,
    create_empty_table,
    create_error_figure,
)

# コールバックヘルパー
from src.utils.callback_helpers import register_clear_callbacks

# データソース解決
from src.data.data_source_registry import resolve_dataset_id

# UIコンポーネント
from src.components.filters import (
    create_category_filter,
    create_date_range_filter,
    create_slicer_filter,
)

# データヘルパー（新規ページで利用可能）
from src.utils.data_helpers import (
    safe_load_filter_options,
    strip_timezone,
    resolve_single_dataset_id,
)
```

## 7. 新規ダッシュボードページの追加手順

1. パッケージディレクトリ作成: `src/pages/<page_name>/`
2. 必須ファイル作成:
   - `__init__.py` -- Dash登録 + `build_layout` 参照 + コールバックインポート
   - `_constants.py` -- `DATASET_ID`, `ID_PREFIX`, `COLUMN_MAP`, `TABLE_SPECS`, `CHART_SPECS`, `CLEAR_PAIRS`
   - `_data_loader.py` -- `load_filter_options()`, `load_and_filter_data()`
   - `_layout.py` -- `build_layout()`
   - `_callbacks.py` -- コールバック群 + `register_clear_callbacks(CLEAR_PAIRS)`
   - `SPEC.md` -- ユーザー向け設計書（日本語）
3. `app.py` に明示的インポート追加: `import src.pages.<page_name>  # noqa: F401`
4. テスト作成: `tests/unit/pages/<page_name>/test_constants.py`, `test_data_loader.py`

パッケージ形式が必要な理由: Dashのページスキャナーが `__init__.py` を `_` 始まりとしてスキップするため、`app.py` での明示的インポートが必須。

### 7.1 チャート視認性の再利用パターン（DOMO比較で有効）

`hamm_overview` の Content Metadata で有効だった改善を、他ページへ横展開するための標準手順。

実装チェックリスト:
- [ ] `dbc.CardHeader` を使う場合、Plotlyのタイトルは消す（`title={"text": None}`）
- [ ] `dcc.Graph` に `config={"displayModeBar": False, "responsive": True}` を設定
- [ ] 単一系列バーは `show_legend=False`
- [ ] 積み上げバーは `text_template="%{y}"` と `textposition="inside"` を組み合わせる
- [ ] `ChartSpec.height` を用途別に明示し、描画面積を確保する
- [ ] CSSはセクションclassでスコープし、全ページ共通classに直接影響させない

責務分担:

| ファイル | 役割 | 例 |
|---------|------|----|
| `_layout.py` | `dcc.Graph` config とスコープclass付与 | `className="xx-metadata-graph"` |
| `_constants.py` | `ChartSpec` の高さ・凡例・ラベル方針 | `show_legend=False`, `text_template="%{y}"` |
| `_chart_builders.py` | `build_chart()` 後の最終レイアウト調整 | `title=None`, `margin`, `legend` |
| `assets/*.css` | セクション限定の余白最適化 | `.xx-row .xx-card .card-body { ... }` |

最小雛形:

```python
# _layout.py
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Genre", className="card-header"),
            dbc.CardBody([
                dcc.Graph(
                    id=CHART_ID_GENRE,
                    className="page-metadata-graph",
                    config={"displayModeBar": False, "responsive": True},
                ),
            ]),
        ], className="page-metadata-card"),
    ], md=4),
], className="mb-4 page-metadata-row")
```

```python
# _constants.py
GENRE_SPEC = ChartSpec(
    title="Genre",
    chart_type="bar",
    x_column="genre",
    y_columns=["count"],
    text_template="%{y}",
    show_legend=False,
    height=460,
)
```

```python
# _chart_builders.py
def _apply_chart_readability(fig):
    fig.update_layout(
        title={"text": None},
        margin={"l": 24, "r": 8, "t": 8, "b": 44},
        xaxis_title="",
        yaxis_title="",
    )
    return fig
```

```css
/* assets/05-charts.css */
.page-metadata-row .page-metadata-card .card-body {
  padding: 0.25rem;
}

.page-metadata-row .page-metadata-graph {
  min-height: 460px;
}
```

アンチパターン:
- `CardHeader` と `ChartSpec.title` を同時表示して縦スペースを二重消費する
- 単一系列なのに凡例を表示し、プロット面積を圧迫する
- `.card` など共通classへ直接padding変更を入れて他ページを壊す

実装後確認:
- [ ] タイトル重複がない
- [ ] 凡例が本当に必要なチャートだけ表示される
- [ ] データラベルが重ならず読める
- [ ] CSS変更が対象セクション外へ波及しない

## 8. ETL設定ファイル

### backend/config/domo_datasets.yaml

現在の登録データセット:

| 名前 | DOMO ID | MinIO ID | パーティション | 除外フィルタ | 状態 |
|------|---------|----------|----------------|-------------|------|
| APAC DOT join Due Date change(first time) | c1cddf9d-... | apac-dot-due-date | delivery completed date | exclude_flg = "Not Exclude" | enabled |
| APAC DOT DDD Change + Issue(SQL) | 2aff337e-... | apac-dot-ddd-change-issue-sql | edit month | exclude_flg = "Not Exclude" | enabled |
| Hamm_Dashboard | 0bc70adb-... | hamm-dashboard | null | なし | enabled |

### backend/config/csv_datasets.yaml

現在の登録データセット:

| 名前 | MinIO ID | ソース | パターン | パーティション | 状態 |
|------|----------|--------|---------|----------------|------|
| Cursor Usage Events | cursor-usage | backend/data_sources | team-usage-events-*.csv | Date | enabled |

## 9. Docker Compose サービス構成

| サービス | 役割 | ポート | 備考 |
|----------|------|--------|------|
| `dash` | Dashアプリ | 8050 | MinIO依存、ヘルスチェック付き |
| `minio` | S3互換ストレージ | 9000/9001 | ヘルスチェック付き |
| `minio-init` | MinIO初期設定 | - | `bi-datasets` バケット作成 |
| `test` | テスト実行 | - | `profiles: [test]` (手動起動のみ) |

## 10. CI/CD

### GitHub Actions ワークフロー

定義ファイル: `.github/workflows/ci.yml`

トリガー:
- `main` ブランチへの push
- `main` ブランチへの pull_request

同一ブランチに対する新しいpushが発生すると、実行中のジョブは自動キャンセルされる（`concurrency` 設定）。

### ジョブ構成（3並列）

| ジョブ | 内容 | 依存パッケージ | 実行コマンド |
|--------|------|----------------|-------------|
| `lint` | Lintチェック | ruff のみ | `ruff check src/` |
| `typecheck` | 型チェック | requirements.txt + requirements-dev.txt | `mypy src/` |
| `test` | テスト実行 | requirements.txt + requirements-dev.txt | `pytest -v --tb=short` |

3ジョブは独立して並列実行される。全ジョブが成功しないとPRのマージはできない（ブランチ保護ルール設定時）。

共通設定:
- Python 3.9（`pyproject.toml` の `requires-python` と一致）
- `typecheck` と `test` は pip キャッシュを使用（`cache-dependency-path` で `requirements.txt` と `requirements-dev.txt` を参照）
- `test` ジョブにはS3/MinIO不要の最小環境変数が設定済み（`ENV=test`, `S3_ENDPOINT=""` 等）

### ローカルでのCI相当チェック

PR作成前に以下を実行して、CI通過を事前確認する:

```bash
ruff check src/
mypy src/
pytest -v --tb=short
```
