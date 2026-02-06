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
