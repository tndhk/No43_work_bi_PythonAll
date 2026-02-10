---
name: 02-page-spec
description: page_spec.yaml の設計・作成ワークフロー。Parquetデータ探索からYAML設計・バリデーションまでをステップバイステップで支援。新規ダッシュボード作成時、page_spec.yaml の設計・編集に使用。
---

# page_spec.yaml 設計・作成ワークフロー

## 1. 概要

- このスキルは `page_spec.yaml` の設計プロセスを体系化する
- 入力: MinIOにParquet形式で格納されたデータ
- 出力: バリデーション済みの `page_spec.yaml`
- 仕様詳細は `docs/page-spec-reference.md` を参照
- パイプライン例は `03-page-gen` スキルの `examples.md` を参照
- 完了後は `03-page-gen` スキル（Phase 2以降）でコード生成に進む

```
01-etl → 02-page-spec → 03-page-gen (Phase 2以降)
(データ準備)    (YAML設計・作成)    (コード生成・手動ファイル・検証)
```

## 2. 前提条件

- データがMinIOにParquet形式でアップロード済み
- データ取得・ETLが必要な場合は `01-etl` スキルを参照
- Python 3.11以上

## 3. クイックスタートチェックリスト

```
- [ ] Step 1: データ探索（Parquetスキーマ把握）
- [ ] Step 2: metadata + column_map 設計
- [ ] Step 3: derived_columns 設計
- [ ] Step 4: filters 設計
- [ ] Step 5: components 設計
- [ ] Step 6: data_transform パイプライン設計
- [ ] Step 7: layout 設計
- [ ] バリデーション: dry-run 実行
```

## 4. Step 1: データ探索（Parquetスキーマ把握）

このステップではデータの特性を理解し、後続のステップでの設計判断の基盤を作る。

### データ読み込みと概要確認

```python
from src.data.parquet_reader import ParquetReader

reader = ParquetReader()
df = reader.read_dataset("dataset-id")

# 概要確認
print(f"行数: {len(df):,}")
print(f"カラム数: {len(df.columns)}")
print(df.dtypes)
print(df.head(5))
print(df.describe())
```

### カラム分類

データのカラムを以下の用途に分類する:

| データ型 | YAML用途 | 例 |
|----------|----------|-----|
| datetime | derived_columns の source、date フィルタ | `created_at`, `completed_at` |
| categorical (文字列、低カーディナリティ) | フィルタ、チャートの分類軸 | `status`, `region`, `content_type` |
| numeric | KPI の value_column、チャートの y_columns | `revenue`, `quantity` |
| ID (文字列/数値、高カーディナリティ) | nunique 集計、テーブル表示 | `id`, `task_id` |

### カーディナリティ分析

```python
for col in df.select_dtypes(include=["object", "category"]).columns:
    n = df[col].nunique()
    print(f"{col}: {n} unique values")
```

カーディナリティはフィルタタイプ選定に直接影響する:
- 2-10: slicer または chip_group が最適
- 10-50: slicer（クリアボタン付き）が最適
- 50-200: category（ドロップダウン）が最適
- 200以上: category（multi=true、検索付き）または非フィルタ化を検討

### 日付カラムの特定とtimezone確認

```python
for col in df.select_dtypes(include=["datetime", "datetime64[ns, UTC]"]).columns:
    print(f"{col}: dtype={df[col].dtype}, range={df[col].min()} ~ {df[col].max()}")
```

timezone-awareの場合、`strip_timezone()` が必要（CLAUDE.md参照）。

### データ品質チェック

```python
null_rates = df.isnull().mean().sort_values(ascending=False)
print(null_rates[null_rates > 0])
```

NULL率が高いカラムは `exclude_null` フィルタまたは column_map から除外を検討。

## 5. Step 2: metadata + column_map 設計

### metadata

各フィールドの決定ガイド:

| フィールド | 決定基準 |
|-----------|---------|
| dashboard_id | URLパス・ディレクトリ名。snake_case、簡潔に |
| id_prefix | 2-4文字 + ハイフン。他ページとの重複を避ける |
| dataset_id | MinIO上のデータセットID（ETL時に設定済み） |
| title | ナビゲーションバーに表示。簡潔かつ説明的に |
| description | SPEC.md生成用。省略可 |

### id_prefix の重複チェック

```bash
grep -r "id_prefix:" src/pages/*/page_spec.yaml
```

### column_map 設計原則

- 使用するカラムのみマッピングする（全カラムは不要）
- 論理名は短く、snake_case で統一
- 物理名が長い/スペース含みの場合、短い論理名を付ける
  - 例: `region: "notification_company_name"`
- 派生カラムをフィルタで使う場合、エイリアスを追加
  - 例: `year: "_year"`, `month: "_month"`

### チェックリスト

```
- [ ] dashboard_id が他ページと重複しないこと
- [ ] id_prefix が他ページと重複しないこと
- [ ] dataset_id が MinIO のデータセットIDと一致すること
- [ ] column_map に必要なカラムが全て含まれていること
- [ ] 論理名が短く snake_case であること
```

## 6. Step 3: derived_columns 設計

### 必要性の判定フロー

- 日付カラムがある → `_year`, `_month` を追加（ほぼ必須）
- 会計年度が必要 → `_fiscal_year`, `_fiscal_quarter` を追加
- 週次集計が必要 → `_iso_week` を追加
- timedelta カラムがある → `timedelta_to_seconds` で数値化
- 上記で対応できない複雑な派生 → `custom` タイプ

### タイプ選択テーブル

| タイプ | 入力 | 出力 | ユースケース |
|--------|------|------|-------------|
| year | datetime | int (2024) | 年フィルタ、年別集計 |
| month | datetime | str ("2024-01") | 月別集計、時系列チャート |
| fiscal_year | datetime | str ("FY2024") | 会計年度集計 |
| fiscal_quarter | datetime | str ("Q1") | 四半期集計 |
| iso_week | datetime | str ("2024-W01") | 週次集計 |
| datetime_year | datetime | int (2024) | year の別名 |
| datetime_month | datetime | str ("2024-01") | month の別名 |
| timedelta_to_seconds | timedelta | float | 所要時間の数値化 |
| date_extract | datetime | varies | format指定で任意抽出 |
| custom | any | any | 上記で対応できない場合 |

### custom タイプの判断基準

以下のいずれかに該当する場合に `custom` を使用:
- 複数カラムに依存する派生値
- ビジネスルール固有の計算（例: 会計年度が4月開始でない場合）
- 条件分岐を含む派生値

custom の場合、`_custom_logic.py` への実装が必要。`depends_on` で依存カラムを明示する。

### 命名規則

- 派生カラム名はアンダースコアプレフィックス: `_year`, `_month`, `_fiscal_year`
- 元カラムとの名前衝突を回避するため

## 7. Step 4: filters 設計

### フィルタタイプ選択判定テーブル

| カーディナリティ | 用途 | 推奨タイプ |
|----------------|------|-----------|
| 2-10 | メイン分類 | slicer（複数選択 + クリア） |
| 2-5 | 固定選択肢 | chip_group |
| 10-50 | サブ分類 | slicer（クリアボタン付き） |
| 50-200 | 補助フィルタ | category（ドロップダウン） |
| 200+ | 検索型 | category（multi=true） |
| datetime | 日付範囲 | date |

### slicer / category / dropdown 詳細比較

| 特性 | slicer | category | dropdown |
|------|--------|----------|----------|
| UI | チェックリスト | ドロップダウン | ドロップダウン |
| 複数選択 | 常にtrue | multi設定 | multi設定 |
| クリアボタン | has_clear_button | なし | なし |
| placeholder | なし | なし | あり |
| 推奨用途 | メインフィルタ | サブフィルタ | 補助（placeholder必要時） |

### chip_group 設計ガイド

- 固定オプション（データから動的生成しない）に使用
- `options` リストで選択肢を明示的に定義
- `default` で初期値を設定可能
- 例: Cadence（weekly/monthly/quarterly/yearly）、表示モード切替

### date フィルタ

- datetime型カラムに使用
- timezone-aware の場合、`strip_timezone()` が `_data_loader.py` で自動適用される
- CLAUDE.md の「Parquet経由のdatetime列はtimezone-awareになる」を参照

### ID命名規約

hamm_overview準拠で、prefix なしスタイルを推奨:

```yaml
# 推奨: id_prefix を id に含めない（page_generator が自動付与）
- id: "filter-region"
- id: "filter-year"

# 非推奨: id_prefix を手動で含める
- id: "hamm-filter-region"
```

注意: `id_prefix` は page_generator がコード生成時に自動でIDに付与する。page_spec.yaml 内ではプレフィックスなしで記述する。ただし、実装済みの hamm_overview のように明示的にプレフィックスを含める方式も動作する（`clear_button_id` は常にプレフィックスなし）。

### フィルタ配置戦略

- 重要度の高いフィルタを先頭に配置
- 関連するフィルタをグループ化（地域→年→月の順など）
- フィルタ数が7以上の場合、セクション分割を検討

## 8. Step 5: components 設計

### KPIカード設計

agg_func 選択ガイド:

| agg_func | ユースケース | 例 |
|----------|-------------|-----|
| count | 全行数 | 「総レコード数」 |
| nunique | ユニーク数 | 「総タスク数」（IDの重複排除） |
| sum | 合計 | 「総売上」 |
| mean | 平均 | 「平均処理時間」 |
| max / min | 最大/最小 | 「最大値」「最新日付」 |

色の推奨パターン:

| 意味 | bg_color | accent_color |
|------|----------|-------------|
| 情報（メイン指標） | #d6e4f0 | #2f5f8f |
| 成功/完了 | #d4edda | #28a745 |
| 警告/注意 | #fff3cd | #ffc107 |
| エラー/重要 | #f8d7da / #f6b3b3 | #c0392b / #e57f7f |
| ニュートラル | #e3f2fd | #1976d2 |

KPIカードでフィルタ付き集計が必要な場合、`data_transform` に `filter` 操作を追加する。

### チャートタイプ選択判定テーブル

| chart_type | データ特性 | 推奨ケース |
|-----------|-----------|-----------|
| bar | カテゴリ別の単一指標 | カテゴリ少数、比較目的 |
| stacked_bar | カテゴリ別の複数系列 | 構成比 + 合計の表現 |
| grouped_bar | カテゴリ別の複数系列 | 系列間の直接比較 |
| line | 時系列データ | トレンド表現 |
| pie | 全体に占める割合 | カテゴリ2-6個の構成比 |
| scatter | 2変数の関係 | 相関分析 |

### テーブル設計

- `column_order` は必須で定義すること（表示順を制御）
- `column_display` で内部カラム名を表示名に変換
- `style_data_conditional` で条件付き書式を設定可能
- スタイル推奨:
  - `sort_action: "native"` はほぼ必須
  - `page_size: 20` が標準
  - `style_header` の `fontWeight: "600"` と `backgroundColor: "#f8f9fa"` は統一パターン

### layout_overrides パターン

チャートの微調整に使用。主要パターン:

```yaml
# 円グラフ用
layout_overrides:
  margin: { l: 8, r: 8, t: 8, b: 34 }
  legend: { orientation: "h", x: 0.0, y: -0.06 }
  textinfo: "label+value+percent"
  textposition: "inside"

# 棒グラフ用（凡例を右側に）
layout_overrides:
  margin: { l: 16, r: 70, t: 8, b: 30 }
  legend: { orientation: "v", x: 1.02, xanchor: "left", y: 0.5, yanchor: "middle" }
  textposition: "inside"

# 棒グラフ用（凡例なし）
layout_overrides:
  margin: { l: 24, r: 8, t: 8, b: 44 }
```

### 色設計

- 同じページ内で色が重複しないようにする
- KPIカードの色はグループごとに統一感を持たせる
- color_map のキーはピボット後のカラム名と一致させる

## 9. Step 6: data_transform パイプライン設計

### 操作順序の原則

```
filter → group_by → pivot → melt → ensure_columns → add_column → drop_column → rename → sort
```

この順序は論理的依存関係に基づく。早い段階でフィルタリングすることでパフォーマンスが向上する。

### パイプラインパターン索引

| パターン | 操作列 | 用途 |
|---------|--------|------|
| 単純集計 | group_by → rename | テーブル表示 |
| 積み上げ棒グラフ | group_by → pivot → ensure_columns → sort | ステータス別の時系列 |
| 円グラフ | group_by (output_name) → sort | 構成比表示 |
| 合計カラム追加 | group_by → pivot → ensure_columns → add_column → rename | テーブル + 合計列 |
| カスタム変換 | custom → filter → sort | 複雑なビジネスロジック |

詳細なパイプライン例は `03-page-gen` スキルの `examples.md` セクション7を参照。

### 積み上げ棒グラフパイプラインのウォークスルー

1. filter: 不要なステータス（例: Cancelled）を除外
2. group_by: 時間軸 + カテゴリでグループ化、id を nunique で集計
3. pivot: カテゴリ値をカラムに展開（例: status の Completed/Invalid がカラムになる）
4. ensure_columns: ピボット後に欠損する可能性のあるカラムを 0 で補完
5. sort: 時間軸でソート

### params とパラメータ補間 `{{param}}`

- `params` はコールバックから受け取るフィルタ値の名前リスト
- `{{param_name}}` でパイプライン内からパラメータ値を参照
- chip_group フィルタの値をパイプラインで使う場合に有用
- 例: cadence フィルタの値に基づいて集計期間を切り替える

```yaml
data_transform:
  params:
    - cadence
  operations:
    - type: "custom"
      function: "add_cadence_columns"
      args:
        cadence: "{{cadence}}"
```

### custom 操作への分離判断

以下の場合は `custom` 操作を使用し `_custom_logic.py` に実装:
- 10行以上の複雑なデータ変換
- 複数コンポーネントで再利用する処理
- 単体テストが必要な処理
- 標準操作（filter, group_by, pivot等）で表現できない処理

## 10. Step 7: layout 設計

### セクション分割の原則

- 論理的なグループでセクションを分ける（KPI / チャート / テーブル / 詳細）
- `title` と `description` でセクションの意図を明示
- フィルタは自動配置されるため、layout に含めない

### Bootstrap 12グリッド配置パターン

| パターン | md値 | 用途 |
|---------|------|------|
| 3列均等 | 4, 4, 4 | KPIカード3つ |
| 4列均等 | 3, 3, 3, 3 | KPIカード4つ |
| 2列均等 | 6, 6 | チャート+テーブル、チャート2つ |
| 2列（左広） | 8, 4 | メインチャート + サマリ |
| 全幅 | 12 | 詳細テーブル |

### className の使い分け

| className | 用途 |
|-----------|------|
| "mb-3" | KPIカード行（小さい余白） |
| "mb-4" | チャート/テーブル行（大きい余白） |
| セクションの className | セクション全体の余白制御 |

### レイアウト検証チェックリスト

```
- [ ] 全コンポーネントが layout に配置されていること
- [ ] layout の component_id が components の id と一致すること
- [ ] md値の合計が各行で12以下であること
- [ ] 適切な className が設定されていること
```

## 11. バリデーションとファイナライズ

### テンプレートコピーコマンド

```bash
mkdir -p src/pages/<page_name>
cp tools/page_generator/templates/new_page_spec.yaml src/pages/<page_name>/page_spec.yaml
```

テンプレートをコピーしてから編集すると、構造の抜け漏れを防げる。

### dry-run 実行

```bash
python3 -m tools.page_generator src/pages/<page_name> --dry-run
```

### よくあるバリデーションエラーと対処法

| エラー | 原因 | 対処法 |
|--------|------|--------|
| Field required | 必須フィールド未設定 | page-spec-reference.md の該当セクションを確認 |
| Duplicate IDs found | ID重複 | コンポーネントID、フィルタIDの重複を解消 |
| references unknown column | column_map 未定義のカラム参照 | column_map にカラムを追加 |
| references unknown component_id | layout で未定義の component_id | components に定義を追加するか layout から削除 |
| Input should be a valid string | 型不一致 | YAML の値を文字列（引用符付き）に修正 |

### 最終チェックリスト

```
- [ ] dry-run がエラーなく通る
- [ ] 全カラムが column_map に定義されている
- [ ] 全コンポーネントIDが layout に配置されている
- [ ] 全フィルタの column が column_map に存在する
- [ ] id_prefix が他ページと重複しない
- [ ] color_map のキーがピボット後のカラム名と一致する
```

## 12. よくある失敗パターン

| 失敗パターン | 合理化メッセージ | 正しい行動 |
|-------------|-----------------|-----------|
| データ探索をスキップ | 「カラム名は分かっている」 | Step 1 でカーディナリティとデータ型を確認 |
| 全カラムを column_map に追加 | 「後で使うかもしれない」 | 使用するカラムのみマッピング |
| フィルタタイプを直感で選択 | 「slicer でいいだろう」 | カーディナリティに基づいて選択 |
| data_transform をなしで開始 | 「シンプルなデータだから不要」 | チャートやテーブルの表示形式から逆算して設計 |
| dry-run をスキップ | 「YAMLは正しいはず」 | 必ず dry-run でバリデーション |
| hamm_overview のYAMLをそのままコピー | 「参考にすれば確実」 | テンプレートからスタートし、Step 1-7 で設計 |
| layout を最後に考える | 「後で並べればいい」 | コンポーネント設計と並行して配置を検討 |

## 13. 参照ドキュメント

| ドキュメント | 用途 |
|------------|------|
| `docs/page-spec-reference.md` | YAML完全リファレンス（フィールド定義、型、デフォルト値） |
| `tools/page_generator/templates/new_page_spec.yaml` | YAMLテンプレート（コピー元） |
| `src/pages/hamm_overview/page_spec.yaml` | 実稼働ページの実装例 |
| `tools/page_generator/schema.py` | Pydanticスキーマ定義（YAML構造の正式定義） |
| `tools/page_generator/README.md` | ツールのCLI使用方法 |

## 14. 関連スキル

- `01-etl`: データ取得・ETL処理（本スキルの前工程）
- `03-page-gen`: コード生成・手動ファイル・検証（本スキルの後工程、Phase 2以降）
- `dash-manual`: 手書きダッシュボード開発（page_generator非対応の場合）
- `spec-updater`: SPEC.md作成・更新（Phase 3で使用）
