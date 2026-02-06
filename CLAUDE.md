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
