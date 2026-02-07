# 各ダッシュボードのユーザー向け設計書（SPEC.md）作成

## Context
各ダッシュボードページの目的や使い方をユーザーが理解しやすくするため、各パッケージ内にユーザー向けの設計書（SPEC.md）を作成する。技術詳細（コールバック、カラムマッピング、コンポーネントID等）は含めず、ダッシュボードの目的・フィルタの使い方・チャートの見方に絞る。

## 対象ファイル（新規作成: 3ファイル）

1. `src/pages/cursor_usage/SPEC.md`
2. `src/pages/apac_dot_due_date/SPEC.md`
3. `src/pages/hamm_overview/SPEC.md`

## 各SPEC.mdの共通構成

```
# <ダッシュボード名>

## 概要
- このダッシュボードの目的・何を見るためのものか

## データソース
- どこからデータが来るか（データセット名のみ、技術詳細なし）

## フィルタの使い方
- 各フィルタの名前と、何を絞り込めるかの説明

## チャート・テーブルの見方
- 各チャート/テーブルの名前と、何が表示されるかの説明

## KPIカード（該当する場合のみ）
- 各KPI指標の意味
```

## 各ダッシュボードの記載内容

### 1. Cursor Usage Dashboard (`src/pages/cursor_usage/SPEC.md`)

- 概要: Cursor AIツールの利用状況（コスト、トークン消費量、リクエスト数）を追跡
- データソース: cursor-usage データセット
- フィルタ: 日付範囲、AIモデル選択
- チャート: 日次コスト推移（折れ線）、モデル別トークン効率（棒）、モデル別コスト割合（円）、詳細データテーブル
- KPI: Total Cost、Total Tokens、Request Count

### 2. APAC DOT Due Date Dashboard (`src/pages/apac_dot_due_date/SPEC.md`)

- 概要: APAC DOT（Delivery On Time）のDue Date Delivery実績を追跡。月別のWork Order数をピボットテーブルで表示
- データソース: apac-dot-due-date、apac-dot-ddd-change-issue-sql の2つ
- フィルタ/コントロール: 表示切替（件数/割合）、分類軸（Area/Category/Vendor）、月、PRC、Area、Category、Vendor、AMP VS AV、Order Type
- チャート: Reference Table（基準ピボットテーブル）、DDD Change + Issue Table（変更・課題ピボットテーブル）

### 3. HAMM Overview Dashboard (`src/pages/hamm_overview/SPEC.md`)

- 概要: HAMMタスクのボリュームと詳細を追跡。Prelim/ERVのコンテンツタイプ別処理量を集計
- データソース: hamm-dashboard データセット
- フィルタ: Region、Year、Month、Task ID、Content Type、Original Language、Was Dialogue Provided、Genre、Error Code、Error Type、Cadence（集計単位）
- チャート: Volume Table（ボリューム集計テーブル）、Volume Chart（積み上げ棒グラフ）、Task Details（タスク詳細テーブル）

## 実装手順

1. 3つのSPEC.mdファイルを並列で作成（subagent 3つに委託）
2. 作成後、内容の整合性をレビュー

## 検証方法

- 各ファイルが正しいパスに存在することを確認
- 内容がユーザー向け（技術詳細なし）であることを確認
- 日本語で記載されていることを確認
