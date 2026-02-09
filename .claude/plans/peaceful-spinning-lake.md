# Plan: hamm_overview に "Language per Task" テーブルを追加

## Context

hamm_overview ダッシュボードのページ最下部に「Language per Task」テーブルを追加する。
タスクごとの言語構成を一覧表示し、Status列とContent Type列にセル単位の条件付きカラーリングを適用する。

## テーブル仕様

カラム順: Task ID, Task Name, Genre, Language Count, Original Language, Additional Languages, Dialog Location, Content Type, Status

条件付きスタイル（セル単位）:
- Status = "Completed" -> 緑背景 (#28a745) + 白文字
- Content Type = "ERV" -> ピンク背景 (#f8d7da)
- Content Type = "Prelim" -> ピンク背景 (#f8d7da)

## 新規カラムマッピング

| 論理キー | Parquet列名 |
|----------|-------------|
| `language_count` | `number of languages` |
| `additional_languages` | `additional languages` |

## 修正対象ファイル

### ソースファイル (7ファイル)
1. `src/pages/hamm_overview/_constants.py`
2. `src/pages/hamm_overview/_data_loader.py`
3. `src/pages/hamm_overview/_chart_builders.py`
4. `src/pages/hamm_overview/_callbacks.py`
5. `src/pages/hamm_overview/_layout.py`
6. `src/pages/hamm_overview/data_sources.yml`
7. `src/pages/hamm_overview/SPEC.md`

### テストファイル
- `tests/unit/pages/hamm_overview/test_constants.py`
- `tests/unit/pages/hamm_overview/test_chart_builders.py`
- `tests/unit/pages/hamm_overview/test_data_loader.py`
- `tests/unit/pages/hamm_overview/test_callbacks.py`
- `tests/unit/pages/hamm_overview/test_data_sources.py`
- `tests/unit/pages/hamm_overview/test_layout.py`

## 実装ステップ (TDD)

### Step 0: テスト RED フェーズ

各ステップのテストを先に書く（RED）。実装後にGREENにする。

### Step 1: `_constants.py` - 定数追加

1a. COLUMN_MAP に2エントリ追加:
```python
"language_count": "number of languages",
"additional_languages": "additional languages",
```

1b. 新 CHART_ID 追加（line 19の後）:
```python
CHART_ID_LANGUAGE_TABLE: str = f"{ID_PREFIX}language-table"
```

1c. LANGUAGE_TABLE_SPEC 追加（GENRE_SPEC の後）:
```python
LANGUAGE_TABLE_SPEC: TableSpec = TableSpec(
    title="Language per Task",
    style_table={"overflowX": "auto"},
    style_cell=_COMPACT_CELL,
    style_header=_COMPACT_HEADER,
    style_data_conditional=[
        {
            "if": {"filter_query": '{Status} = "Completed"', "column_id": "Status"},
            "backgroundColor": "#28a745",
            "color": "white",
        },
        {
            "if": {"filter_query": '{Content Type} = "ERV"', "column_id": "Content Type"},
            "backgroundColor": "#f8d7da",
        },
        {
            "if": {"filter_query": '{Content Type} = "Prelim"', "column_id": "Content Type"},
            "backgroundColor": "#f8d7da",
        },
    ],
    sort_action="native",
    page_size=20,
    column_order=[
        "Task ID", "Task Name", "Genre", "Language Count",
        "Original Language", "Additional Languages",
        "Dialog Location", "Content Type", "Status",
    ],
)
```

### Step 2: `_data_loader.py` - データ準備関数追加

2a. import に `CHART_ID_LANGUAGE_TABLE`, `LANGUAGE_TABLE_SPEC` 追加

2b. `resolve_dataset_id_for_dashboard()` の `chart_ids` リストに `CHART_ID_LANGUAGE_TABLE` 追加

2c. `prepare_language_display_df()` 関数追加（`prepare_task_display_df` のパターンに従う）:
- COLUMN_MAP から対象カラムを選択・リネーム
- Additional Languages の NaN を "N/A" に置換
- Task ID で数値ソート
- 空DataFrameの場合は column_order のカラムを持つ空DFを返す

### Step 3: `_chart_builders.py` - ビルダー関数追加

3a. import に `LANGUAGE_TABLE_SPEC` 追加

3b. `build_language_table(df)` 関数追加:
```python
def build_language_table(df: pd.DataFrame) -> tuple[str, Any]:
    return build_table(df, LANGUAGE_TABLE_SPEC)
```

### Step 4: `_layout.py` - レイアウト追加

4a. import に `CHART_ID_LANGUAGE_TABLE` 追加

4b. Error Details row 2 (line 199) の後、MantineProvider閉じの前に追加:
```python
# Language per Task table
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Language per Task", className="card-header"),
            dbc.CardBody([
                html.Div(id=CHART_ID_LANGUAGE_TABLE),
            ]),
        ]),
    ], md=12),
], className="mb-4"),
```

### Step 5: `_callbacks.py` - コールバック修正

5a. import に `CHART_ID_LANGUAGE_TABLE` 追加、`_data_loader` から `prepare_language_display_df` 追加、`_chart_builders` から `build_language_table` 追加

5b. `@callback` デコレータに 14番目の Output 追加:
```python
Output(CHART_ID_LANGUAGE_TABLE, "children"),
```

5c. try ブロック内、task_table構築後に追加:
```python
language_display_df = prepare_language_display_df(df)
_, language_table = build_language_table(language_display_df)
```

5d. 成功パスの return tuple に `language_table` 追加（14番目）

5e. エラーパスの return tuple に `error_msg` 追加（14番目）

### Step 6: `data_sources.yml` - マッピング追加

```yaml
  hamm-language-table: hamm-dashboard
```

### Step 7: `SPEC.md` - ドキュメント更新

Language per Task セクション追加（日本語、技術詳細なし）

## 検証

1. `python3 -m pytest tests/unit/pages/hamm_overview/ -v` で全テスト GREEN
2. `python3 -m pytest tests/ -v` で全体テスト GREEN
3. アプリ起動後、ページ最下部に Language per Task テーブルが表示される
4. フィルタ操作でテーブルデータが連動する
5. Status="Completed" セルが緑、Content Type="ERV"/"Prelim" セルがピンク
6. ソート機能が動作する
