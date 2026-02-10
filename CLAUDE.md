# Plotly Dash BI Dashboard

## プロジェクト概要
- Plotly Dashベースのダッシュボード
- S3/Parquetからデータ取得
- Flask-Login + セッションベースのフォーム認証（`src/auth/`）

## ドキュメント参照ガイド

作業内容に応じて、以下のドキュメントを参照すること。

| 作業内容 | 参照先 | 備考 |
|----------|--------|------|
| プロジェクト全体把握 | `codemaps/architecture.md` | 依存関係、データフロー、コンポーネント構成 |
| 新規ダッシュボードページ作成 | `docs/CONTRIB.md` sec.7 + `codemaps/frontend.md` | 手順とUIコンポーネント一覧 |
| ETL追加・修正 | `docs/CONTRIB.md` sec.8 + `codemaps/backend.md` | 設定ファイル構成とETLクラス |
| データ層の理解 | `codemaps/data.md` | フィルタ、キャッシュ、データローダー |
| 運用・トラブルシュート | `docs/RUNBOOK.md` | デプロイ、ETL実行、障害対応 |
| 技術仕様確認 | `docs/tech-spec.md` | チャート構築API、データ変換仕様 |
| 環境構築・コマンド一覧 | `docs/CONTRIB.md` sec.2-3 | セットアップ、テスト、ETLコマンド |

### docs/ vs codemaps/ の役割

- `docs/`: 手順書・仕様書（人間が読む運用ドキュメント）
- `codemaps/`: コード構造マップ（AIがコードベースを把握するための参照資料）

codemapsは実装変更時に更新すること（`doc-updater` サブエージェント活用を推奨）。

## ページ設計ポリシー

### 2層ポリシー
`src/pages/` のページは以下の2層に分類される:

| 層 | 条件 | 形式 | 例 |
|---|---|---|---|
| Tier 1 | コールバックなし かつ データ読込なし | 単一ファイル | `dashboard_home.py` |
| Tier 2 | コールバックあり または データ読込あり | パッケージ形式 | `cursor_usage/`, `apac_dot_due_date/` |

### パッケージ構造とファイル役割

パッケージ形式のカノニカル構造、ファイル別の役割、共通基盤の使用については `docs/CONTRIB.md` sec.6 を参照。

### レイアウト構築ルール

#### チャート/テーブルのカード配置（必須）

全てのチャート、テーブル、KPIカードは `dbc.Card` で囲むこと。

```python
# 必須構造
dbc.Card([
    dbc.CardHeader("Chart Title", className="card-header"),
    dbc.CardBody([
        dcc.Graph(id=CHART_ID),
    ]),
])
```

理由:
- ページ全体の灰色背景（`var(--bg-base)`）との対比で視認性向上
- フィルターエリアとのデザイン統一
- `assets/03-components.css` のカードスタイル（白背景、境界線、ホバー効果）が自動適用

参考実装: `src/pages/hamm_overview/_layout.py`

### SPEC.md 必須ルール（MANDATORY）
- 全ダッシュボードページには `SPEC.md` を配置すること
- 目的: ユーザーがダッシュボードの目的・使い方を理解するため
- 更新タイミング: フィルタ、チャート、KPI、テーブルを追加・修正した際は必ずSPEC.mdも更新
- 形式: 日本語、技術詳細なし（コールバック、カラムマッピング、コンポーネントID等は含めない）
- 構成: 概要、データソース、フィルタの使い方、チャート・テーブルの見方、KPIカード（該当時）
- 詳細: `spec-updater` スキルを参照

### ID_PREFIX 必須ルール
- 全コンポーネントID（フィルタ、KPIカード、チャート、テーブル等）には `ID_PREFIX` を付与すること
- 形式: `f"{ID_PREFIX}component-name"` (例: `"cu-filter-date"`, `"cu-kpi-total-cost"`)
- 理由: 複数ページ間でのID衝突を防止

### 新規ページ追加手順

詳細な手順は `docs/CONTRIB.md` sec.7 を参照。

## 開発メモ

### Parquet経由のdatetime列はtimezone-awareになる
- ParquetにUTCタイムスタンプを保存すると、読み込み時に `datetime64[ns, UTC]` になる
- `filter_engine.apply_filters` はtimezone-naiveなTimestampで比較するため、そのまま渡すと `TypeError: Invalid comparison between dtype=datetime64[ns, UTC] and Timestamp` が発生する
- 対処: `strip_timezone(df, column_name)` ヘルパーを使用（`src.utils.data_helpers`）、または `pd.to_datetime(df["col"], utc=True).dt.tz_convert(None)` で手動変換

### Dash 4.x では dangerously_allow_html が廃止されている
- `html.Div(content, dangerously_allow_html=True)` は Dash 4.0.0 で使えない
- `src/charts/templates.py` に残っているレガシーラッパー（`render_bar_chart`, `render_line_chart`, `render_pie_chart`）は非推奨
- 新規実装では `build_chart()` + `ChartSpec` と `build_table()` + `TableSpec` を使用すること

### Dash 4.x のドロップダウン/DatePickerが背面に回る
- 症状: ドロップダウンのポップアップが他のカードやセクションの背面に隠れる
- 原因は2つある（両方対処が必要）:

  1. z-indexの不足: Dash 4.x (Radix UI) のポップアップはデフォルトでz-indexが低い
  2. スタッキングコンテキスト: `.card`クラス（`dbc.Card`が自動付与）に`transform`や`transition: all`が設定されていると、新しいスタッキングコンテキストが作成され、内部の`z-index: 9999`が外部要素に対して無効になる

- 対処:
  - `[data-radix-popper-content-wrapper]`に`z-index: 9999 !important`を設定
  - `.dash-dropdown-content`に`background-color`を明示設定（デフォルトで透明になることがある）
  - `.card`の`transition`を`transform`を含まない形に限定（例: `transition: box-shadow 0.3s ease, border-color 0.3s ease`）
  - `.card:hover`の`transform: translateY(-2px)`を削除（スタッキングコンテキスト作成を防止）
  - 既知の問題: `assets/04-animations.css:112`の`.card`は`transition: transform 0.3s ease, ...`を含んでいる。これ単体では問題を起こさない（`:hover`での`transform`がスタッキングコンテキストを作成）が、将来的な問題防止のため`transition: transform`は削除が望ましい。現状の回避策: フィルタを含むカードには`.hover-lift`クラスを付与しないこと

- やってはいけないこと:
  - `[data-radix-popper-content-wrapper]`に`position`を上書きしてはいけない（Radixの内部位置計算が破壊される）
  - `position: fixed`や`position: relative`を外部から設定すると、ポップアップの位置ずれや背景透明の原因になる

### Dash 4.x dcc.Dropdown の実際のHTML構造
- Dash 4.0.0はRadix UIベースの独自ドロップダウンを使用（React Selectではない）
- ポータルは`body`直下ではなく`.dash-dropdown-wrapper`内にレンダリングされる
- 主なCSSクラス:
  - `.dash-dropdown` - トリガーボタン
  - `.dash-dropdown-wrapper` - 外側ラッパー（ポータルコンテナ）
  - `.dash-dropdown-content` - ポップアップパネル全体
  - `.dash-dropdown-options` - オプションリストコンテナ
  - `.dash-dropdown-option` - 個々のオプション
  - `.dash-dropdown-search` - 検索入力
  - `.dash-dropdown-actions` - Select All / Deselect All ボタン
- 旧Dash (2.x) の`.Select-menu-outer`/`.Select-option`等のセレクタは4.xでは無効

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
- `backend/config/csv_datasets.yaml` でCSVデータセットを管理
- DOMO API ETLも同パターン: `backend/config/domo_datasets.yaml`
- `backend/scripts/load_csv.py` で汎用ローダーを使用（個別スクリプト作成不要）
- スタンドアロンETLスクリプトのモジュールインポートエラー対処:
  - `python3 backend/scripts/load_csv.py` で直接実行するとモジュールが見つからない
  - スクリプト冒頭に以下を追加: `project_root = Path(__file__).parent.parent.parent; sys.path.insert(0, str(project_root))`
  - これにより `backend.etl.etl_csv` などのモジュールを正しくインポート可能

## 実行環境の注意点（macOS）

### コマンドライン
- Docker: `docker compose` を使用（`docker-compose` は非推奨/インストールされていない）
- Python: `python3` を使用（`python` コマンドは存在しない）
