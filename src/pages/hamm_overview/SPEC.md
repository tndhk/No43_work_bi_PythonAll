# HAMM Overview Dashboard

## 概要
HAMMタスクのボリュームと詳細を追跡するダッシュボードです。Completed/Invalidのステータス別処理量を集計し、タスクの進捗状況を可視化します。

## データソース
- hamm-dashboard データセット

## フィルタの使い方

### SlicerのClear（標準）
Slicer形式のフィルタには個別のClear操作があります。対象のSlicerだけ選択を解除できます。

### Region
通知会社名（地域）で絞り込みます。

### Year
対象年で絞り込みます。

### Month
対象月で絞り込みます。

### Task ID
特定のタスクIDで絞り込みます。

### Content Type
ビデオタイプ（コンテンツタイプ）で絞り込みます。

### Original Language
オリジナル言語で絞り込みます。

### Was Dialogue Provided
ダイアログの提供有無で絞り込みます。

### Genre
ジャンルで絞り込みます。

### Error Code
エラーコードで絞り込みます。

### Error Type
エラータイプ（ユーザー起因/システム起因）で絞り込みます。

### Cadence（集計単位）
データの集計単位を選択します。2x2のグリッド配置で表示されます。
- weekly: ISO週単位
- monthly: 月単位
- quarterly: 四半期単位
- yearly: 年単位

## チャート・テーブルの見方

### Volume セクション
青色のヘッダーエリアにタイトルと説明文を表示し、右側にCadenceフィルタを配置しています。両セクションは高さが揃っています。

#### KPIカード
Volumeセクションには3つのKPIカードが表示され、フィルタに連動して集計値が更新されます。

##### Total Screens Processed
処理された全画面数の合計を表示します。薄青色の背景で強調表示されます。

##### Total ERV Processed
ERV（Error Rate Verification）処理された件数の合計を表示します。薄ピンク色の背景で強調表示されます。

##### Total Prelim Processed
Prelim（Preliminary）処理された件数の合計を表示します。濃いピンク色の背景で強調表示されます。

### Volume Table（ボリューム集計テーブル）
選択した集計単位（Cadence）でタスクのボリュームを集計したテーブルです。ステータス別（Completed/Invalid）の件数と合計を表示します。Cancelledステータスは除外されます。コンパクトなフォントサイズで多くのカラムを表示します。

### Volume Chart（積み上げ棒グラフ）
Volume Tableのデータを積み上げ棒グラフで可視化します。時系列での処理量の推移や、ステータス別（Completed: 緑色、Invalid: グレー）の内訳を視覚的に把握できます。各バーセグメントにはデータラベルが表示されます。

### Task Details（タスク詳細テーブル）
個別タスクの詳細情報を一覧表示します。コンパクトなフォントサイズで、タスクID、タイトル、ステータス、作成日、完了日、ビデオ時間、エラー情報など多くのカラムを一度に確認できます。

### Content Metadata（コンテンツメタデータ）
Original Language、Was dialogue Provided?、Genre の3つの観点で件数分布を表示します。すべて既存フィルタに連動して更新されます。

#### Original Language
オリジナル言語ごとの件数割合を円グラフで表示します。言語構成の偏りを直感的に把握できます。

#### Was dialogue Provided?
Screener Type（Prelim/ERV）ごとに、ダイアログ提供の有無（Yes/No）を積み上げ棒グラフで表示します。コンテンツタイプ別の提供傾向を比較できます。

#### Genre
ジャンルごとの件数を棒グラフで表示します。対象期間・条件における主要ジャンルを把握できます。

### Error Details（エラー詳細）

#### Issues Ratio (HAMM vs Human Intervention)
ユーザー起因エラーとHAMM起因エラーの割合を円グラフで表示します。

#### Intervention per Screener Type
Screener Type（Prelim/ERV）別の介入件数を、User/HAMM別に積み上げ棒グラフで表示します。

#### User Intervention Breakdown
ユーザー起因エラーの内訳を、エラー内容別に棒グラフで表示します。

#### HAMM Intervention Breakdown
HAMM起因エラーの内訳を、エラー内容別に棒グラフで表示します。
