# APAC DOT Due Date Dashboard

## 概要
APAC DOT（Delivery On Time）のDue Date Delivery実績を追跡するダッシュボードです。月別のWork Order数をピボットテーブルで表示し、納期遵守状況を分析できます。

## KPI
ページ上部にフィルタ適用後の主要指標を表示します。

### Total Work Orders
現在のフィルタ条件に該当するWork Order（作業指示書）の総数を表示します。重複を除いたユニークなWork Order IDの件数で集計されます。

## データソース
- apac-dot-due-date データセット（基準データ）
- apac-dot-ddd-change-issue-sql データセット（変更・課題データ）

## 表示切替コントロール

### 件数/割合表示
ピボットテーブルの表示形式を切り替えます。
- 件数: Work Orderの実数を表示
- 割合: 全体に対する割合（%）を表示

### 分類軸
ピボットテーブルの行軸を切り替えます。
- Area: ビジネスエリア別の集計
- Category: メトリックワークストリーム別の集計
- Vendor: ベンダー別の集計

## フィルタの使い方

### 月
対象月を選択します。複数月を選択して期間比較も可能です。

### PRC
PRCコードで絞り込みます（データ固有の分類）。

### Area
ビジネスエリアで絞り込みます。

### Category
メトリックワークストリームで絞り込みます。

### Vendor
ベンダー名で絞り込みます。

### AMP VS AV
AMP/AVスコープで絞り込みます。

### Order Type
オーダータイプ（注文タグ）で絞り込みます。

## チャート・テーブルの見方

### Reference Table（基準ピボットテーブル）
apac-dot-due-date データセットの月別Work Order数を、選択した分類軸（Area/Category/Vendor）で集計したピボットテーブルです。納期遵守の基準データとして使用します。

### DDD Change + Issue Table（変更・課題ピボットテーブル）
apac-dot-ddd-change-issue-sql データセットの月別Work Order数を、選択した分類軸で集計したピボットテーブルです。納期変更や課題が発生したケースを追跡します。

両テーブルを比較することで、変更・課題の発生状況を把握できます。
