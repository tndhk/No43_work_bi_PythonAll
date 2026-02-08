# トラブルシューティングガイド

このドキュメントでは、Plotly Dash BIダッシュボード開発で遭遇する可能性のある問題と、その解決方法を詳しく説明します。

---

## Bug Pattern 1: Timezone-aware datetime エラー

### 完全なエラーメッセージ

```
TypeError: Invalid comparison between dtype=datetime64[ns, UTC] and Timestamp
```

または

```
TypeError: Cannot compare tz-naive and tz-aware datetime-like objects
```

### 発生箇所

- フィルタリング処理中（`apply_filters` 関数内）
- 日付範囲フィルタを使用している場合
- Parquetから読み込んだデータに対して日付比較を行う場合

### 原因の詳細

1. **Parquetのdatetime保存形式**
   - ParquetにUTCタイムスタンプを保存すると、読み込み時に `datetime64[ns, UTC]` 型になります
   - これはtimezone-aware（タイムゾーン情報付き）なdatetimeオブジェクトです

2. **フィルタエンジンの期待**
   - `filter_engine.apply_filters` はtimezone-naive（タイムゾーン情報なし）なTimestampで比較します
   - そのため、timezone-awareなdatetimeと比較しようとするとエラーが発生します

### 解決方法

データ読み込み後、必ずtimezoneを除去します：

```python
# データ読み込み
df = get_cached_dataset(reader, dataset_id)

# CRITICAL: Strip timezone from datetime columns
df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_convert(None)
df["DateOnly"] = df["Date"].dt.date
```

### デバッグ手順

1. データ読み込み直後に `df["Date"].dtype` を確認
   - `datetime64[ns, UTC]` の場合はtimezone-aware
   - `datetime64[ns]` の場合はtimezone-naive（問題なし）

2. フィルタ適用前に `df["Date"].head()` を確認
   - タイムゾーン情報（`+00:00` など）が表示されていないか確認

3. エラーが発生した場合、スタックトレースから該当箇所を特定
   - `filter_engine.py` の `apply_filters` 関数内で発生しているか確認

### 予防策

- データ読み込み直後に必ずtimezone変換を行う習慣をつける
- コールバック関数の最初でtimezone変換を実行
- レイアウト関数でも同様に処理する（フィルタの初期値設定時）

---

## Bug Pattern 2: Dash 4.x API変更 - dangerously_allow_html

### 完全なエラーメッセージ

```
dash.exceptions.InvalidComponentError: The `html.Div` component (version 4.0.0) received an unexpected keyword argument: `dangerously_allow_html`

Allowed arguments: accessKey, aria-*, children, className, contentEditable, data-*, dir, disable_n_clicks, draggable, hidden, id, key, lang, n_clicks, n_clicks_timestamp, role, spellCheck, style, tabIndex, title
```

### 発生箇所

- テーブル表示を実装する際
- `render_table` 関数を使用している場合
- HTML文字列を直接表示しようとする場合

### 原因の詳細

Dash 4.0でセキュリティ上の理由から `dangerously_allow_html` 属性が削除されました。これにより、HTML文字列を直接表示することができなくなりました。

### 解決方法

テーブル表示には `dash_table.DataTable` を直接使用します：

```python
import dash_table

# ❌ 使えない（Dash 4.xではエラー）
from src.charts.templates import render_table
table_component = render_table(df)

# ✅ 正しい方法
table_component = dash_table.DataTable(
    data=df.to_dict("records"),
    columns=[{"name": c, "id": c} for c in df.columns],
    page_size=20,
    style_table={"overflowX": "auto"},
    style_cell={"textAlign": "left", "padding": "8px"},
    style_header={"fontWeight": "bold"},
)
```

### デバッグ手順

1. エラーメッセージから該当コンポーネントを特定
   - `html.Div` に `dangerously_allow_html` を渡している箇所を探す

2. `src/charts/templates.py` の `render_table` 関数を確認
   - この関数はDash 4.xでは使用できない

3. すべてのテーブル表示を `dash_table.DataTable` に置き換える

### 予防策

- 新しいダッシュボードでは最初から `dash_table.DataTable` を使用
- `render_table` 関数は使用しない
- HTML文字列を直接表示する必要がある場合は、別の方法を検討する

---

## Bug Pattern 3: CSS z-index問題 - ドロップダウン/DatePickerが背面に隠れる

### 症状の詳細

- ドロップダウンのメニューがKPIカードの後ろに隠れる
- DatePickerのカレンダーが他の要素の後ろに表示される
- マウス位置によって表示が不安定（時々表示される、時々隠れる）
- スクロール位置によって表示が変わる

### 発生条件

- Dash 4.xを使用している場合
- KPIカードにhover効果がある場合
- 複数のレイヤーが重なっている場合

### 原因の詳細

1. **Dash 4.xのRadix UI実装**
   - Dash 4.xはRadix UIを使用してドロップダウンやDatePickerを実装
   - これらのポップアップは `dash-dropdown-content` や `dash-options-list` などのクラスを使用
   - デフォルトのz-indexが低いため、他の要素の後ろに隠れる

2. **Stacking Contextの問題**
   - `.kpi-card:hover` で `transform: translateY(-2px)` を使用している場合、新しいstacking contextが作成される
   - これにより、z-indexの比較が正しく機能しなくなる

### 解決方法

#### Step 1: CSSでz-indexを設定

`assets/03-components.css` に以下を追加：

```css
/* Dash 4.x (radix) dropdown/datepicker content */
.dash-dropdown-content,
.dash-options-list,
.dash-dropdown-options,
.dash-datepicker-content,
.dash-datepicker-popover,
.dash-datepicker-overlay,
[data-radix-popper-content-wrapper] {
  position: relative !important;
  z-index: 9999 !important;
}

[data-radix-popper-content-wrapper] > * {
  z-index: 9999 !important;
}
```

#### Step 2: KPIカードのhover効果を調整

`assets/03-components.css` の `.kpi-card:hover` を修正：

```css
.kpi-card:hover {
  /* transform: translateY(-2px); を削除またはコメントアウト */
  box-shadow: var(--shadow-md), var(--shadow-glow);
  border-color: var(--border-accent);
}
```

#### Step 3: Docker環境での確認

`docker-compose.yml` でassetsがマウントされているか確認：

```yaml
services:
  dash:
    volumes:
      - ./assets:/app/assets  # この行があるか確認
```

#### Step 4: ブラウザでハードリロード

CSS変更後は必ずハードリロードを実行：
- Mac: Cmd+Shift+R
- Windows/Linux: Ctrl+Shift+F5

### デバッグ手順

1. **ブラウザのDevToolsで確認**
   - ドロップダウンを開いた状態で、Elementsタブを開く
   - `.dash-dropdown-content` 要素を検索
   - Computedタブでz-indexの値を確認
   - 期待値: `9999`

2. **Stacking Contextの確認**
   - `.kpi-card` 要素を検索
   - Computedタブで `transform` プロパティを確認
   - `none` 以外の値が設定されている場合は削除

3. **CSSファイルの読み込み確認**
   - Networkタブで `03-components.css` が読み込まれているか確認
   - ステータスコードが200であることを確認

4. **Docker環境の場合**
   - コンテナ内で `ls -la /app/assets/` を実行してファイルが存在するか確認
   - `docker-compose.yml` のvolumes設定を確認

### 予防策

- 新しいダッシュボードを作成する際は、最初からz-index設定を含める
- KPIカードのhover効果では `transform` を使わない
- Docker環境では必ずassetsをマウントする
- CSS変更後は必ずハードリロードを実行する

---

## Bug Pattern 4: Docker環境でアセットが反映されない

### 症状の詳細

- CSSの変更がブラウザに反映されない
- JavaScriptファイルの変更が反映されない
- 画像ファイルが表示されない
- `backend/scripts/` のスクリプトが実行できない

### 原因の詳細

Dockerコンテナ内でアプリケーションが実行されている場合、ホストのファイルシステムとコンテナのファイルシステムは分離されています。ボリュームマウントが設定されていないと、変更が反映されません。

### 解決方法

`docker-compose.yml` にボリュームマウントを追加：

```yaml
services:
  dash:
    volumes:
      - ./src:/app/src
      - ./backend:/app/backend
      - ./assets:/app/assets  # 追加
      - ./app.py:/app/app.py
```

### デバッグ手順

1. **docker-compose.ymlの確認**
   - `volumes` セクションに必要なディレクトリがマウントされているか確認

2. **コンテナ内での確認**
   ```bash
   docker-compose exec dash ls -la /app/assets/
   ```
   - ファイルが存在するか確認

3. **ファイル変更の確認**
   - ホストでファイルを変更
   - コンテナ内で同じファイルを確認
   - 変更が反映されているか確認

4. **ブラウザのキャッシュ確認**
   - ハードリロード（Cmd+Shift+R / Ctrl+Shift+F5）を実行
   - Networkタブでファイルが304（Not Modified）ではなく200（OK）で読み込まれているか確認

### 予防策

- 新しいプロジェクトでは最初から必要なディレクトリをマウントする
- `docker-compose.yml` のテンプレートを作成して再利用する
- 開発時は常にボリュームマウントを使用する

---

## Bug Pattern 5: data_sources.ymlのchart_idが見つからない

### 完全なエラーメッセージ

```
KeyError: 'chart_id_name'
```

または

```
ValueError: No dataset mapping found for chart_id: ...
```

### 発生箇所

- `resolve_dataset_id()` 関数を呼び出している場合
- 新しいダッシュボードページを追加した場合
- DASHBOARD_IDやCHART_IDが間違っている場合

### 原因の詳細

`backend/config/data_sources.yml` に該当のchart_idが定義されていない、またはDASHBOARD_IDが間違っているため、データセットIDを解決できません。

### 解決方法

#### Step 1: data_sources.ymlにマッピングを追加

`backend/config/data_sources.yml` を開き、該当のdashboard_id配下にchart_idを追加：

```yaml
<dashboard_id>:
  <chart_id>: "<dataset_id>"
```

例：
```yaml
hamm_overview:
  hamm-kpi-total-machines: "domo_hamm_kpi_data"
  hamm-chart-status-trend: "domo_hamm_status_trend"
```

#### Step 2: DASHBOARD_IDとCHART_IDの確認

`_constants.py` で定義されている値が正しいか確認：

```python
DASHBOARD_ID = "hamm_overview"  # data_sources.ymlのキーと一致しているか
ID_PREFIX = "hamm-"  # 一貫性があるか

# CHART_IDはID_PREFIXを含む完全なID
CHART_ID = f"{ID_PREFIX}kpi-total-machines"
```

### デバッグ手順

1. **resolve_dataset_id()の戻り値を確認**
   ```python
   from backend.etl.resolve_dataset import resolve_dataset_id
   dataset_id = resolve_dataset_id(DASHBOARD_ID, CHART_ID)
   print(f"Resolved dataset_id: {dataset_id}")
   ```

2. **data_sources.ymlの内容を確認**
   - 該当のDASHBOARD_IDが存在するか
   - CHART_IDが正しく定義されているか
   - インデントが正しいか（YAMLの構文エラー）

3. **CHART_IDの形式を確認**
   - ID_PREFIXを含む完全なIDになっているか
   - 例：`"hamm-kpi-total-machines"` （正）vs `"kpi-total-machines"` （誤）

### 予防策

- 新しいダッシュボードページを追加する際は、最初に `data_sources.yml` にマッピングを追加
- `_constants.py` で定義する際は、DASHBOARD_IDとID_PREFIXの一貫性を確認
- テストで `resolve_dataset_id()` の戻り値を検証

---

## Bug Pattern 6: パッケージページがapp.pyでインポートされていない

### 症状の詳細

- ダッシュボードページにアクセスすると404エラー
- Dashのページ一覧（`/`）に表示されない
- コンソールに「Page not found」エラー

### 発生条件

- パッケージ形式のページ（`src/pages/<page_name>/`）を新規追加した場合
- `app.py` に明示的importが追加されていない場合

### 原因の詳細

パッケージ形式のページは、Dashのページ自動検出機能が `__init__.py` を `_` 始まりとしてスキップするため、明示的に `app.py` でインポートする必要があります。単一ファイルページ（例：`cursor_usage.py`）とは異なり、自動検出されません。

### 解決方法

#### Step 1: app.pyに明示的importを追加

`app.py` の適切な位置に以下を追加：

```python
# Pages (package-style pages must be imported explicitly)
import src.pages.cursor_usage  # noqa: F401
import src.pages.apac_dot_due_date  # noqa: F401
import src.pages.hamm_overview  # noqa: F401
import src.pages.<new_page_name>  # noqa: F401  ← 追加
```

#### Step 2: __init__.pyでregister_pageを確認

パッケージの `__init__.py` で `dash.register_page()` が正しく呼ばれているか確認：

```python
import dash

from ._layout import build_layout

dash.register_page(
    __name__,
    path="/<page_name>",
    title="Page Title",
    name="Page Name",
    layout=build_layout,  # 関数オブジェクトを渡す
)

# コールバックをインポート（register_pageの後）
from . import _callbacks  # noqa: F401, E402
```

### デバッグ手順

1. **app.pyでimportが存在するか確認**
   ```bash
   grep "import src.pages.<page_name>" app.py
   ```
   - 存在しない場合は追加

2. **Dashアプリ起動ログを確認**
   ```
   docker-compose logs dash | grep "Registered page"
   ```
   - 該当ページが登録されているか確認

3. **ブラウザで直接URLにアクセス**
   - `http://localhost:8050/<page_name>` にアクセス
   - 404エラーの場合はimport追加が必要

4. **__init__.pyの内容を確認**
   - `dash.register_page(__name__, ...)` が呼ばれているか
   - `layout` パラメータが正しく設定されているか

### 予防策

- 新しいパッケージページを追加する際は、必ず `app.py` にimportを追加
- テンプレートを作成して再利用する
- チェックリストに「app.pyへのimport追加」を含める

---

## Bug Pattern 7: register_clear_callbacks のdefault_value不一致

### 症状の詳細

- クリアボタンを押してもフィルタがクリアされない
- クリアボタンを押すと予期しない値になる
- クリアボタンを押すとエラーが発生する

### 発生条件

- `register_clear_callbacks()` を使用している場合
- フィルタの初期値とdefault_valueが一致していない場合

### 原因の詳細

`register_clear_callbacks()` の `default_value` パラメータは、クリアボタンを押した際にフィルタを何にリセットするかを指定します。このdefault_valueが、フィルタコンポーネントの初期値（`value`プロパティ）と一致していない場合、期待通りに動作しません。

### 解決方法

#### Step 1: フィルタの型に合わせてdefault_valueを設定

通常、`register_clear_callbacks()` はフィルタの型を自動判定してデフォルト値を設定するため、明示的な指定は不要です。カスタムフィルタの場合のみ、以下のように設定：

```python
from src.utils.callback_helpers import register_clear_callbacks

# CLEAR_PAIRS定義（_constants.py）
CLEAR_PAIRS = [
    (f"{ID_PREFIX}btn-clear-date", f"{ID_PREFIX}filter-date"),
    (f"{ID_PREFIX}btn-clear-category", f"{ID_PREFIX}filter-category"),
]

# コールバック登録（_callbacks.py）
register_clear_callbacks(CLEAR_PAIRS)
```

#### Step 2: カスタムdefault_valueが必要な場合

特殊なケースで明示的に指定する場合：

- ドロップダウン（単一選択）: `default_value=None`
- ドロップダウン（複数選択）: `default_value=[]`
- DatePickerRange: `default_value=(None, None)`
- Chips（スライサーフィルタ）: `default_value=None`

### デバッグ手順

1. **_callbacks.pyでregister_clear_callbacks呼出を確認**
   ```python
   # ファイルの末尾に配置
   register_clear_callbacks(CLEAR_PAIRS)
   ```

2. **フィルタの初期値を確認**
   ```python
   # _layout.pyでフィルタの初期値を確認
   dcc.Dropdown(
       id=f"{ID_PREFIX}filter-category",
       value=None,  # または [] など
       ...
   )
   ```

3. **ブラウザのDevToolsで確認**
   - クリアボタンをクリック
   - Consoleタブでエラーが出ていないか確認
   - Networkタブでコールバックが正常に実行されているか確認

### 予防策

- 基本的には `register_clear_callbacks(CLEAR_PAIRS)` のみで対応
- カスタムフィルタの場合は、フィルタの初期値と同じ型・値を使用
- テストでクリアボタンの動作を検証

---

## Bug Pattern 8: build_table で page_size=0 が無視される

### 症状の詳細

- `TableSpec(page_size=0)` を指定しても、テーブルにページネーションが表示される
- デフォルトで20行ごとにページが分割される
- 全行を一度に表示したいが、できない

### 発生条件

- `build_table()` 関数で `TableSpec` を使用している場合
- `page_size=0` を指定して全行表示を期待している場合

### 原因の詳細

Dash DataTableの仕様上、`page_size=0` は無効値として扱われ、デフォルト値（20）に自動的に置換されます。これはDashの内部実装によるもので、`build_table()` の問題ではありません。

### 解決方法

#### 方法1: 大きなpage_sizeを指定（推奨）

実質的に全行を表示する場合は、大きな値を指定：

```python
from src.charts.specs import TableSpec

TABLE_SPECS = {
    "all-data": TableSpec(
        page_size=10000,  # 実質的に全行表示
        sort_column="Date",
        sort_ascending=False,
    ),
}
```

#### 方法2: ページネーションを無効化

ページネーション自体を無効にする場合：

```python
TABLE_SPECS = {
    "all-data": TableSpec(
        page_action='none',  # ページネーション無効
        sort_column="Date",
        sort_ascending=False,
    ),
}
```

### デバッグ手順

1. **TableSpecの定義を確認**
   ```python
   # _constants.py
   print(TABLE_SPECS["all-data"].page_size)
   # 0の場合は大きな値に変更
   ```

2. **build_table()の戻り値を確認**
   ```python
   table = build_table(df, TABLE_SPECS["all-data"])
   print(table.page_size)  # 20になっている場合は対処が必要
   ```

3. **ブラウザでテーブルを確認**
   - ページネーションが表示されているか
   - 全行が表示されているか

### 予防策

- `page_size=0` は使用しない
- 全行表示が必要な場合は `page_size=10000` など大きな値を指定
- ページネーション不要な場合は `page_action='none'` を使用
- データ量が多い場合は、パフォーマンスを考慮してページネーションを維持

---

## その他のよくある問題

### 問題: データが表示されない

**確認事項:**
1. ETLスクリプトが正常に実行されたか
2. MinIOにParquetファイルがアップロードされたか
3. `dataset_id` が正しいか
4. データのカラム名が正しいか

**デバッグ方法:**
```python
# データ読み込みを確認
reader = ParquetReader()
df = get_cached_dataset(reader, dataset_id)
print(f"Data shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(df.head())
```

### 問題: フィルタが機能しない

**確認事項:**
1. フィルタのIDがコールバックのInputと一致しているか
2. フィルタの値が正しく取得できているか
3. `apply_filters` 関数が正しく呼ばれているか

**デバッグ方法:**
```python
# フィルタの値を確認
print(f"Start date: {start_date}")
print(f"End date: {end_date}")
print(f"Category values: {category_values}")

# フィルタ適用後のデータを確認
print(f"Filtered data shape: {filtered_df.shape}")
```

### 問題: チャートが表示されない

**確認事項:**
1. データが空でないか
2. チャートのパラメータが正しいか
3. Plotlyのバージョンが正しいか

**デバッグ方法:**
```python
# チャート用のデータを確認
chart_data = filtered_df.groupby("Date")["Value"].sum().reset_index()
print(f"Chart data shape: {chart_data.shape}")
print(chart_data.head())

# チャートのパラメータを確認
print(f"X column: {params['x_column']}")
print(f"Y column: {params['y_column']}")
```

---

## デバッグのベストプラクティス

1. **エラーメッセージを完全に読む**
   - スタックトレースの最初のエラーに注目
   - エラーメッセージに含まれるファイル名と行番号を確認

2. **段階的にデバッグする**
   - 問題を小さな単位に分割
   - 一つずつ確認していく

3. **ログを活用する**
   - `print()` で中間値を確認
   - データの形状や型を確認

4. **ブラウザのDevToolsを活用する**
   - ConsoleタブでJavaScriptエラーを確認
   - Networkタブでリソースの読み込みを確認
   - ElementsタブでDOM構造を確認

5. **Docker環境の確認**
   - コンテナ内で直接コマンドを実行して確認
   - ログを確認（`docker-compose logs dash`）
