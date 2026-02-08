# Plotly Dash BI Dashboard

## プロジェクト概要
- Plotly Dashベースのダッシュボード
- S3/Parquetからデータ取得
- Flask-Login + セッションベースのフォーム認証（`src/auth/`）

## ページ設計ポリシー

### 2層ポリシー
`src/pages/` のページは以下の2層に分類される:

| 層 | 条件 | 形式 | 例 |
|---|---|---|---|
| Tier 1 | コールバックなし かつ データ読込なし | 単一ファイル | `dashboard_home.py` |
| Tier 2 | コールバックあり または データ読込あり | パッケージ形式 | `cursor_usage/`, `apac_dot_due_date/` |

### パッケージ形式のカノニカル構造

```
src/pages/<page_name>/
├── __init__.py          # 必須: Dash登録 + build_layout参照 + コールバックインポート
├── _constants.py        # 必須: DASHBOARD_ID, DATASET_ID, ID_PREFIX, COLUMN_MAP, TABLE_SPECS, CHART_SPECS
├── _data_loader.py      # 必須: load_filter_options(), load_and_filter_data()
├── _layout.py           # 必須: build_layout()
├── _callbacks.py        # 必須: コールバック関数群（薄いオーケストレータ）
├── _filters.py          # 条件付き必須: フィルタUI構築（フィルタ5個以上の場合）
├── data_sources.yml     # 必須: チャートID -> データセットIDマッピング
├── SPEC.md              # 必須: ユーザー向け設計書（日本語）
├── _utils.py            # オプション: ヘルパー関数
└── _chart_builders.py   # オプション: カスタム集計・描画ロジック
```

#### ファイル別の役割

**_constants.py**
- 必須定数: `DASHBOARD_ID`, `ID_PREFIX`
- `DATASET_ID`: レガシー/フォールバック用。実行時のデータセット解決は `data_sources.yml` 経由で `resolve_dataset_id()` を使用。後方互換性とテストフィクスチャーのため保持
- `COLUMN_MAP`: 必須（トップレベルのdict、または複数データセットページではDatasetConfig内にネスト）
- チャート/テーブル定義: `TABLE_SPECS` (dict[str, TableSpec]), `CHART_SPECS` (dict[str, ChartSpec])、または個別変数として定義（`COST_TREND_SPEC`, `DETAIL_TABLE_SPEC`等）
- Specは `src.charts.specs` からインポート
- フィルタクリアペア: `CLEAR_PAIRS` (list[tuple[str, str]]) - 推奨: `_constants.py`に定義。インライン定義も可
- 複数データセットの場合: `COLUMN_MAP`等をDatasetConfigなどにネストして定義可（apac_dot_due_date 参照）

**_data_loader.py**
- フィルタオプション取得: `load_filter_options()`
- データ読込・フィルタリング: `load_and_filter_data()`
- データ変換ロジック（集計前の整形など）

**_callbacks.py**
- 薄いオーケストレータ層（ビジネスロジックは最小限）
- フィルタ入力受取 -> data_loader呼出 -> chart_builders呼出 -> 戻り値返却
- クリアコールバック: `register_clear_callbacks(CLEAR_PAIRS)` を末尾で呼ぶ（CLEAR_PAIRSは `_constants.py` で定義推奨）
- 共通empty_statesを使用: `create_empty_figure()`, `create_empty_table()`, `create_error_figure()`

**_chart_builders.py**（オプション）
- カスタム集計ロジック（pivot, groupby, 複雑な計算など）
- 共通ビルダーで対応できないカスタム描画
- 共通ビルダーを活用: `build_table(df, spec)`, `build_chart(df, spec)`
- Spec定義は `_constants.py` に配置（このファイルには置かない）

#### 共通基盤の使用

利用可能な共通基盤:

```python
# チャート/テーブル構築（全ページで使用）
from src.charts.table_builder import build_table
from src.charts.chart_builder import build_chart
from src.charts.specs import TableSpec, ChartSpec

# 空状態・エラー状態（全ページで使用）
from src.charts.empty_states import (
    create_empty_figure,
    create_empty_table,
    create_error_figure,
)

# コールバックヘルパー（全ページで使用）
from src.utils.callback_helpers import register_clear_callbacks

# データソース解決（全ページで使用）
from src.data.data_source_registry import resolve_dataset_id

# UIコンポーネント（全ページで使用）
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

### SPEC.md 必須ルール（MANDATORY）
- 全ダッシュボードページには `SPEC.md` を配置すること
- 目的: ユーザーがダッシュボードの目的・使い方を理解するため
- 更新タイミング: フィルタ、チャート、KPI、テーブルを追加・修正した際は必ずSPEC.mdも更新
- 形式: 日本語、技術詳細なし（コールバック、カラムマッピング、コンポーネントID等は含めない）
- 構成: 概要、データソース、フィルタの使い方、チャート・テーブルの見方、KPIカード（該当時）
- 詳細: `dash-spec-updater` スキルを参照

### ID_PREFIX 必須ルール
- 全コンポーネントID（フィルタ、KPIカード、チャート、テーブル等）には `ID_PREFIX` を付与すること
- 形式: `f"{ID_PREFIX}component-name"` (例: `"cu-filter-date"`, `"cu-kpi-total-cost"`)
- 理由: 複数ページ間でのID衝突を防止

### 新規ページ追加手順
1. パッケージディレクトリ作成: `src/pages/<page_name>/`
2. 必須ファイル作成: `__init__.py`, `_constants.py`, `_data_loader.py`, `_layout.py`, `_callbacks.py`, `data_sources.yml`, `SPEC.md`
3. `app.py` に明示的インポート追加: `import src.pages.<page_name>  # noqa: F401`
   - 理由: Dashのスキャナーが `__init__.py` を `_` 始まりとしてスキップするため
   - パッケージ内の `__init__.py` では `dash.register_page(__name__, ..., layout=layout)` のようにレイアウト関数を明示的に渡すこと
4. テスト作成: 最低限 `test_constants.py`, `test_data_loader.py`, `test_data_sources.py`。推奨: `test_callbacks.py`, `test_layout.py`
   - `tests/conftest.py` のグローバルモックを前提とする

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
