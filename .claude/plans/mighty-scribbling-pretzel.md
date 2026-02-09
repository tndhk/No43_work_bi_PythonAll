# Plan: hamm_overview VolumeセクションにKPIカード3枚追加

## Context

hamm_overviewダッシュボードのVolumeセクション（青ヘッダー + Cadenceフィルタ）の直下に、フィルタ連動するKPIカード3枚を追加する。現在はVolume Table/Chartが直接表示されているが、ユーザーが一目でVolume合計を把握できるKPIカードが欠けている。

スクリーンショットの目標状態:
- "Total Screens Processed" -- 薄青背景 (`#d6e4f0`)、濃青アクセント (`#2f5f8f`)
- "Total ERV Processed" -- 薄ピンク背景 (`#f6b3b3`)、ピンクアクセント (`#e57f7f`)
- "Total Prelim Processed" -- 濃ピンク背景 (`#e57f7f`)、赤アクセント (`#c0392b`)

## 変更ファイル一覧

| # | ファイル | 変更内容 |
|---|---------|---------|
| 1 | `src/components/cards.py` | `create_kpi_card()` に `bg_color`, `accent_color` オプション引数追加 |
| 2 | `src/pages/hamm_overview/_constants.py` | KPI用 Chart ID 3つ + カラー定数追加 |
| 3 | `src/pages/hamm_overview/_layout.py` | Volumeヘッダー行(67行目)直後にKPIカード用 `dbc.Row` 挿入 |
| 4 | `src/pages/hamm_overview/_callbacks.py` | Output 3つ追加 + `volume_summary` から合計値算出 + KPIカード生成 |
| 5 | `src/pages/hamm_overview/SPEC.md` | KPIカードセクション追記 |

## 実装ステップ

### Step 1: テスト作成（TDD）

`tests/pages/hamm_overview/` 配下にKPIカード関連のテストを追加:

- `create_kpi_card()` の拡張テスト: `bg_color`/`accent_color` 指定時にstyleが適用されること、未指定時は既存挙動が変わらないこと
- コールバックテスト: `volume_summary` からKPI値が正しく算出されること（VOLUME TOTAL.sum(), ERV.sum(), Prelim.sum()）

### Step 2: `src/components/cards.py` 拡張

`create_kpi_card()` に2つのオプション引数を追加（後方互換）:

```python
def create_kpi_card(
    title: str,
    value: Union[str, int, float],
    subtitle: Optional[str] = None,
    bg_color: Optional[str] = None,       # カスタム背景色
    accent_color: Optional[str] = None,   # 上部ボーダーアクセント色
) -> dbc.Card:
```

- `bg_color` 指定時: `style={"backgroundColor": bg_color}` をカードに追加
- `accent_color` 指定時: `style={"borderTop": f"4px solid {accent_color}"}` をカードに追加
- 未指定時: 既存の `.kpi-card` CSSスタイルがそのまま適用（破壊的変更なし）

### Step 3: `_constants.py` に定数追加

```python
# KPI Card IDs
CHART_ID_KPI_TOTAL_SCREENS = f"{ID_PREFIX}kpi-total-screens"
CHART_ID_KPI_TOTAL_ERV     = f"{ID_PREFIX}kpi-total-erv"
CHART_ID_KPI_TOTAL_PRELIM  = f"{ID_PREFIX}kpi-total-prelim"

# KPI Card colors
KPI_COLOR_SCREENS = {"bg": "#d6e4f0", "accent": "#2f5f8f"}
KPI_COLOR_ERV     = {"bg": "#f6b3b3", "accent": "#e57f7f"}
KPI_COLOR_PRELIM  = {"bg": "#e57f7f", "accent": "#c0392b"}
```

### Step 4: `_layout.py` にKPIカード行挿入

Volumeヘッダー行(67行目)直後、Volume Table/Chart行(69行目)直前に挿入:

```python
# KPI Cards row
dbc.Row([
    dbc.Col([html.Div(id=CHART_ID_KPI_TOTAL_SCREENS)], md=4),
    dbc.Col([html.Div(id=CHART_ID_KPI_TOTAL_ERV)], md=4),
    dbc.Col([html.Div(id=CHART_ID_KPI_TOTAL_PRELIM)], md=4),
], className="mb-3"),
```

### Step 5: `_callbacks.py` にOutput追加 + KPI生成ロジック

1. Output 3つ追加（既存7つの先頭または末尾に）:
   ```python
   Output(CHART_ID_KPI_TOTAL_SCREENS, "children"),
   Output(CHART_ID_KPI_TOTAL_ERV, "children"),
   Output(CHART_ID_KPI_TOTAL_PRELIM, "children"),
   ```

2. `volume_summary` から合計値算出（既存の128行目付近、volume_summary計算後に追加）:
   ```python
   total_screens = int(volume_summary["VOLUME TOTAL"].sum())
   total_erv = int(volume_summary[ERV_LABEL].sum())
   total_prelim = int(volume_summary[PRELIM_LABEL].sum())
   ```

3. `create_kpi_card()` でKPIカード生成:
   ```python
   kpi_screens = create_kpi_card(
       "Total Screens Processed", f"{total_screens:,}",
       bg_color=KPI_COLOR_SCREENS["bg"], accent_color=KPI_COLOR_SCREENS["accent"],
   )
   kpi_erv = create_kpi_card(
       "Total ERV Processed", f"{total_erv:,}",
       bg_color=KPI_COLOR_ERV["bg"], accent_color=KPI_COLOR_ERV["accent"],
   )
   kpi_prelim = create_kpi_card(
       "Total Prelim Processed", f"{total_prelim:,}",
       bg_color=KPI_COLOR_PRELIM["bg"], accent_color=KPI_COLOR_PRELIM["accent"],
   )
   ```

4. returnタプルに3つの値を追加

### Step 6: `SPEC.md` 更新

VolumeセクションにKPIカードの説明を追記（`dash-spec-updater` スキル参照）。

### Step 7: `data_sources.yml` 更新

KPIカード3つのIDをデータセットIDにマッピング追加。

## 既存コードの再利用

| 既存資産 | パス | 用途 |
|---------|------|------|
| `create_kpi_card()` | `src/components/cards.py` | KPIカード生成（拡張して再利用） |
| `build_volume_summary()` | `src/pages/hamm_overview/_data_loader.py` | 既存のvolume集計結果からsum()で値取得 |
| `PRELIM_LABEL`, `ERV_LABEL` | `src/pages/hamm_overview/_constants.py` | カラム名定数（既存） |
| `VOLUME_CHART_SPEC.color_map` | `src/pages/hamm_overview/_constants.py` | ERV/Prelim色は既存色定義と一致 |

## 検証方法

1. ユニットテスト: `python3 -m pytest tests/pages/hamm_overview/ -v`
2. `create_kpi_card` テスト: `python3 -m pytest tests/components/ -v`
3. アプリ起動確認: `python3 app.py` でhamm-overviewページを開き、Volumeセクション直下に3つのKPIカードが表示されること
4. フィルタ連動確認: Region/Year/Cadence等のフィルタ変更でKPI値が更新されること
5. 空データ確認: フィルタで全データが除外された場合、KPIが0または空状態を表示すること
