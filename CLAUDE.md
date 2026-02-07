# Plotly Dash BI Dashboard

## プロジェクト概要
- Plotly Dashベースのダッシュボード
- S3/Parquetからデータ取得
- Basic認証

## 開発メモ

### Parquet経由のdatetime列はtimezone-awareになる
- ParquetにUTCタイムスタンプを保存すると、読み込み時に `datetime64[ns, UTC]` になる
- `filter_engine.apply_filters` はtimezone-naiveなTimestampで比較するため、そのまま渡すと `TypeError: Invalid comparison between dtype=datetime64[ns, UTC] and Timestamp` が発生する
- 対処: `pd.to_datetime(df["col"], utc=True).dt.tz_convert(None)` でtimezoneを除去してからフィルタに渡す

### Dash 4.x では dangerously_allow_html が廃止されている
- `html.Div(content, dangerously_allow_html=True)` は Dash 4.0.0 で使えない
- `render_table` (src/charts/templates.py) がこれを使っているため、テーブル表示には `dash.dash_table.DataTable` を直接使うこと

### Dash 4.x のドロップダウン/DatePickerが背面に回る
- 症状: DateRangeやModelのプルダウンがKPIカードの背面に隠れる、マウス位置で不安定
- 原因: Dash 4.x (Radix) のポップアップが `dash-dropdown-content` / `dash-options-list` を使い、z-indexが低いまま
- 対処:
  - `assets/03-components.css` に以下を追加して前面固定:
    - `.dash-dropdown-content`, `.dash-options-list`, `.dash-dropdown-options`, `.dash-datepicker-content` へ `z-index: 9999 !important`
  - Docker利用時は `docker-compose.yml` に `./assets:/app/assets` を追加してCSSを確実に反映
  - 反映確認はブラウザのハードリロードで行う

### Package-style Pages（パッケージ形式のページ）
- 単一ファイルページ（例: `cursor_usage.py`）はDashが自動検出する
- パッケージ形式（例: `apac_dot_due_date/`）は `app.py` に明示的importが必要
- 理由: Dashのスキャナーが `__init__.py` を `_` 始まりとしてスキップする
- 新規パッケージページ追加時: `app.py` に `import src.pages.<name>  # noqa: F401` を追加
- パッケージ内の `__init__.py` では `dash.register_page(__name__, ..., layout=layout)` のようにレイアウト関数を明示的に渡す必要がある（単一ファイルページでは自動検出されるが、パッケージ形式では必須）

## ETL開発の注意点

### DOMO API ETL
- `.env`の値にダブルクォート不要: `DOMO_CLIENT_ID=abc123`（`"abc123"`は誤り）
- `src/data/config.py`にPydantic設定追加必須: `domo_client_id: Optional[str] = None`
- スクリプトで明示的に`.env`ロード: `load_dotenv(project_root / ".env")`
- MinIO認証情報（ローカル）: `S3_ENDPOINT=http://localhost:9000`, `S3_ACCESS_KEY/SECRET_KEY=minioadmin`

### データ検証
- スタンドアロンスクリプトではキャッシュなし: `reader.read_dataset("id")`
- `get_cached_dataset()`はFlaskアプリコンテキストが必要

### パーティション分割
- 1-10万行: 日付カラムあれば推奨
- 10万行以上: 必須
- 注意: NULL値レコードはパーティションから除外される（元データより行数が減る）

### CSV ETL（設定駆動化）
- `backend/config/csv_datasets.yaml` でCSVデータセットを管理（DOMO APIと同じパターン）
- `backend/scripts/load_csv.py` で汎用ローダーを使用（個別スクリプト作成不要）
- スタンドアロンETLスクリプトのモジュールインポートエラー対処:
  - `python3 backend/scripts/load_csv.py` で直接実行するとモジュールが見つからない
  - スクリプト冒頭に以下を追加: `project_root = Path(__file__).parent.parent.parent; sys.path.insert(0, str(project_root))`
  - これにより `backend.etl.etl_csv` などのモジュールを正しくインポート可能

## 実行環境の注意点（macOS）

### コマンドライン
- Docker: `docker compose` を使用（`docker-compose` は非推奨/インストールされていない）
- Python: `python3` を使用（`python` コマンドは存在しない）

### ETLスクリプト実行
```bash
# 正しい実行方法
python3 backend/scripts/load_*.py

# 誤り（エラーになる）
python backend/scripts/load_*.py
```

### Docker操作
```bash
# 正しい実行方法
docker compose ps
docker compose up -d
docker compose logs -f

# 誤り（エラーになる）
docker-compose ps
```
