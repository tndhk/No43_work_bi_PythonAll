# デザインリニューアル: ダークテーマ → Warm Professional ライトテーマ

## Context

現在のBIダッシュボードは「Minimal Luxury Dark Theme」（ゴールドアクセントの高級感あるダークテーマ）を採用している。会社で使用するシステムとして、より落ち着いた業務ツール風のライトモードデザインに変更する。

変更の方針:
- 方向性: Warm Professional（明るいウォームホワイト/ライトグレー背景、品のある業務ツール風）
- フォント: Noto Sans JP（日本語対応）+ Inter（欧文）+ JetBrains Mono（データ）
- サイドバー: ライトカラーに統一
- アクセント: ゴールド → ブルー系に変更

---

## 新カラーシステム（CSS Variables）

```css
:root {
  /* Backgrounds */
  --bg-base: #f8f9fa;          /* ウォームライトグレー（ページ全体） */
  --bg-surface: #ffffff;        /* 白（サイドバー等の面） */
  --bg-card: #ffffff;           /* 白（カード背景） */
  --bg-elevated: #f1f3f5;      /* 薄いグレー（入力フィールド等） */

  /* Accent - ブルー系 */
  --accent-primary: #2563eb;    /* メインブルー */
  --accent-primary-dim: #1d4ed8; /* ダークブルー */
  --accent-hover: #3b82f6;     /* ホバー時の明るいブルー */

  /* Text - ダーク文字 on ライト背景 */
  --text-primary: #1a1a2e;      /* ほぼ黒（メインテキスト） */
  --text-secondary: #64748b;    /* スレートグレー（補助テキスト） */
  --text-muted: #94a3b8;        /* ライトグレー（控えめテキスト） */

  /* Borders */
  --border-subtle: #e2e8f0;     /* ライトグレーボーダー */
  --border-accent: rgba(37, 99, 235, 0.3); /* ブルーアクセントボーダー */

  /* Status（ライト背景で映える少し落ち着いた色） */
  --status-success: #059669;    /* エメラルドグリーン */
  --status-warning: #d97706;    /* アンバー */
  --status-danger: #dc2626;     /* レッド */

  /* Spacing - 変更なし */

  /* Shadows - ライト用に軽く */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-glow: 0 0 20px rgba(37, 99, 235, 0.1); /* ブルーグロウ */
}
```

## 新フォントシステム

```
見出し + 本文: "Noto Sans JP" (400, 500, 600, 700)
欧文補助: "Inter" (400, 500, 600, 700)
データ/等幅: "JetBrains Mono" (400, 500, 600)  ← 維持
```

Google Fonts URL:
```
https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap
```

---

## 実装ステップ

### Step 1: `assets/00-reset.css` - デザイントークン変更
ファイル: `/Users/takahiko_tsunoda/work/dev/work_BI_PythonAll/assets/00-reset.css`

変更内容:
- コメント「Minimal Luxury Dark Theme」→「Warm Professional Light Theme」
- `:root` 内の全CSS変数を上記の新カラーシステムに置換
- `body` の `font-family` を `"Noto Sans JP", "Inter", sans-serif` に変更
- シャドウ値を軽いライト用に変更

### Step 2: `assets/01-typography.css` - フォント変更
ファイル: `/Users/takahiko_tsunoda/work/dev/work_BI_PythonAll/assets/01-typography.css`

変更内容:
- Google Fonts `@import` URLを新フォント（Noto Sans JP + Inter + JetBrains Mono）に変更
- `h1-h6, .display-font`: `font-family` を `"Noto Sans JP", "Inter", sans-serif` に変更
  - `letter-spacing: -0.02em` → `letter-spacing: 0` に（Noto Sans JPでは不要）
- `body, p, span, ...`: `font-family` を `"Noto Sans JP", "Inter", sans-serif` に変更
- `code, pre, .monospace, table`: JetBrains Mono は維持

### Step 3: `assets/02-layout.css` - サイドバー＆レイアウト
ファイル: `/Users/takahiko_tsunoda/work/dev/work_BI_PythonAll/assets/02-layout.css`

変更内容:
- `.sidebar`:
  - `background-color` → `var(--bg-surface)`
  - `background: linear-gradient(...)` → 削除（フラットな白背景に）
  - `backdrop-filter: blur(10px)` → 削除
  - `border-right: 1px solid var(--border-subtle)` → 維持（変数値が変わるので自動適用）
- `.sidebar-brand`: `font-family` → `"Noto Sans JP", "Inter", sans-serif`
- `.sidebar-logout-button`: `font-family` → `"Noto Sans JP", "Inter", sans-serif`
- `.dashboard-card-title`: `font-family` → `"Noto Sans JP", "Inter", sans-serif`
- `.dashboard-card:hover`: `box-shadow` からグロウ効果を控えめに（`var(--shadow-md)` のみでも可）

### Step 4: `assets/03-components.css` - コンポーネント調整
ファイル: `/Users/takahiko_tsunoda/work/dev/work_BI_PythonAll/assets/03-components.css`

変更内容:
- CSS変数を参照している箇所は自動で反映されるため、主にフォント名の差し替え:
  - `"Syne"` → `"Noto Sans JP", "Inter"` （card-header, kpi-value, summary-number-value, filter-header）
  - `"Plus Jakarta Sans"` → `"Noto Sans JP", "Inter"` （summary-number-container, table headers）
- ハードコードされた色値がないか確認（CSS変数経由なら自動反映）

### Step 5: `assets/04-animations.css` - アニメーション調整
ファイル: `/Users/takahiko_tsunoda/work/dev/work_BI_PythonAll/assets/04-animations.css`

変更内容:
- `.hover-glow` のシャドウ色を確認（CSS変数参照なら自動反映）
- 基本的に変更不要（アニメーション自体はテーマに依存しない）

### Step 6: `assets/05-charts.css` - チャートスタイル
ファイル: `/Users/takahiko_tsunoda/work/dev/work_BI_PythonAll/assets/05-charts.css`

変更内容:
- `.chart-title`: `font-family` → `"Noto Sans JP", "Inter", sans-serif`
- CSS変数参照箇所は自動反映

### Step 7: `assets/06-login.css` - ログインページ
ファイル: `/Users/takahiko_tsunoda/work/dev/work_BI_PythonAll/assets/06-login.css`

変更内容:
- `.login-brand`: `font-family` → `"Noto Sans JP", "Inter", sans-serif`
- `.login-subtitle`, `.login-input`, `.login-button`, `.login-error`: `font-family` → `"Noto Sans JP", "Inter", sans-serif`
- `.login-input:focus`: `box-shadow` 色を `rgba(201, 165, 92, 0.1)` → `rgba(37, 99, 235, 0.15)` に変更（ハードコード値）
- `.login-button:hover` の `color: var(--bg-base)` はライト背景だと文字が見えないため → `color: #ffffff` に変更

### Step 8: `src/charts/plotly_theme.py` - Plotlyテーマ
ファイル: `/Users/takahiko_tsunoda/work/dev/work_BI_PythonAll/src/charts/plotly_theme.py`

変更内容:
- コメント更新: 「Minimal Luxury dark theme」→「Warm Professional light theme」
- `PLOTLY_COLOR_PALETTE`: ブルー系ベースのパレットに変更:
  ```python
  PLOTLY_COLOR_PALETTE = [
      "#2563eb",  # Blue (primary)
      "#059669",  # Emerald
      "#d97706",  # Amber
      "#dc2626",  # Red
      "#7c3aed",  # Violet
      "#0891b2",  # Cyan
  ]
  ```
- `paper_bgcolor` / `plot_bgcolor`: `"rgba(0,0,0,0)"` → 維持（透明のままカード背景が反映）
- `font.color`: `"#8b8d9a"` → `"#64748b"` （text-secondary）
- `font.family`: `"Plus Jakarta Sans"` → `"Noto Sans JP, Inter, sans-serif"`
- `title.font.color`: `"#e8e6e1"` → `"#1a1a2e"` （text-primary）
- `title.font.family`: `"Syne"` → `"Noto Sans JP, Inter, sans-serif"`
- `xaxis/yaxis gridcolor`: `"rgba(255,255,255,0.06)"` → `"#e2e8f0"` （border-subtle）
- `xaxis/yaxis linecolor`: 同上
- `xaxis/yaxis tickfont.color`: `"#8b8d9a"` → `"#64748b"`
- `xaxis/yaxis title.font.color`: `"#e8e6e1"` → `"#1a1a2e"`
- `xaxis/yaxis title.font.family`: → `"Noto Sans JP, Inter"`
- `legend.bordercolor`: → `"#e2e8f0"`
- `legend.font.color`: → `"#64748b"`
- `legend.font.family`: → `"Noto Sans JP, Inter"`
- `hoverlabel.bgcolor`: `"#1c1c27"` → `"#ffffff"`
- `hoverlabel.bordercolor`: → `"rgba(37, 99, 235, 0.3)"`
- `hoverlabel.font.color`: → `"#1a1a2e"`
- `hoverlabel.font.family`: → `"Noto Sans JP, Inter"`

### Step 9: `src/pages/apac_dot_due_date.py` - インラインスタイル修正
ファイル: `/Users/takahiko_tsunoda/work/dev/work_BI_PythonAll/src/pages/apac_dot_due_date.py`

変更内容:
- `style_header`: `backgroundColor: "#4A5568"` → `"#2563eb"`, `color: "white"` → 維持
- `style_data_conditional` GRAND TOTAL行: `backgroundColor: "#EDF2F7"` → `"#eff6ff"`（ブルー系の薄い背景）

---

## 変更対象ファイル一覧

| # | ファイル | 変更内容 |
|---|---------|---------|
| 1 | `assets/00-reset.css` | CSS変数（全カラー・シャドウ）、フォント |
| 2 | `assets/01-typography.css` | Google Fonts URL、全font-family |
| 3 | `assets/02-layout.css` | サイドバーグラデーション削除、フォント |
| 4 | `assets/03-components.css` | フォント名差し替え |
| 5 | `assets/04-animations.css` | 確認のみ（変更なしの可能性大） |
| 6 | `assets/05-charts.css` | フォント名差し替え |
| 7 | `assets/06-login.css` | フォント、ハードコード色値修正 |
| 8 | `src/charts/plotly_theme.py` | 全色・全フォント・パレット変更 |
| 9 | `src/pages/apac_dot_due_date.py` | インラインDataTableスタイル修正 |

---

## 検証手順

1. `docker-compose up` でアプリ起動（またはローカル `python app.py`）
2. ブラウザでハードリロード（Cmd+Shift+R）してCSSキャッシュクリア
3. 確認ポイント:
   - ログインページ: 白背景にブルーのサインインボタン、入力フォーカスがブルーリング
   - サイドバー: 白背景、ブルーのアクティブリンク、グレーの非アクティブリンク
   - ホームページ: ライトグレー背景にホワイトカード、ブルーの「開く」リンク
   - Cursor Usage: KPIカード・チャートがライト背景で視認性良好
   - APAC DOT Due Date: テーブルヘッダーがブルー、GRAND TOTAL行が薄いブルー背景
   - 全体: フォントがNoto Sans JP/Interで統一、日本語表示が自然
4. レスポンシブ確認: 768px以下でサイドバーが非表示になること
