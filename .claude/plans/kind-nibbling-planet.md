# dash-bi-workflow スキルにレイアウトパターンを追記

## Context

HAMM OverviewのDOMOレイアウト再現で得た知見（CSS Gridフィルタ行、Mantine Chip切り詰め、非対称カラム幅など）を、今後のダッシュボード開発で再利用できるようにスキルに残したい。

## 方針: `dash-bi-workflow` に `layout-patterns.md` を新規追加

推奨度 ☆☆☆☆☆ -- 既存スキルの構造に合う

| 選択肢 | 推奨度 | 理由 |
|--------|--------|------|
| A: `dash-bi-workflow/layout-patterns.md` 新規追加 | ☆5 | 既存の分割パターン（TROUBLESHOOTING.md, examples.md）に沿う。SKILL.mdが肥大化しない。レイアウトはダッシュボード開発の一部なので同スキル内が自然 |
| B: `dash-bi-workflow/SKILL.md` に直接追記 | ☆2 | 既に423行で長い。レイアウトの話題はPhase 2に該当するが混ぜると可読性が落ちる |
| C: 別スキル `dash-layout` を新規作成 | ☆2 | レイアウトだけで独立スキルにするほどの量・頻度ではない。ダッシュボード作成時に2スキル起動が必要になり面倒 |

---

## 変更対象

| ファイル | 変更内容 |
|---------|---------|
| `.claude/skills/dash-bi-workflow/layout-patterns.md` | 新規作成 -- レイアウトレシピ集 |
| `.claude/skills/dash-bi-workflow/SKILL.md` | Phase 2に `layout-patterns.md` への参照リンクを1行追加 |

---

## `layout-patterns.md` に含める内容

### 1. フィルタ行レイアウトパターン

| パターン | 使い分け | 実装方法 |
|----------|----------|----------|
| Bootstrap Grid (`dbc.Row` + `dbc.Col`) | フィルタ6個以下、非対称幅が必要な場合 | `md=6/2/2/2` のように指定 |
| CSS Grid (`html.Div` + `.filter-row-Ncol`) | フィルタ7個以上、均等幅で1行に並べたい場合 | `grid-template-columns: repeat(N, 1fr)` |

### 2. CSS Gridフィルタ行の実装レシピ

- `.filter-row-7col` のCSS定義（grid, gap, align-items）
- カード内パディング縮小（密集レイアウト向け）
- カードヘッダー・ボディのコンパクト化

### 3. Mantine Chip テキスト切り詰め

- `.filter-row-Ncol` 内の `.mantine-Chip-label` に対する ellipsis 設定
- ChipGroupの `flex-direction: row` + `flex-wrap: wrap` 明示
- フォントサイズ・パディング縮小（密集グリッド向け）

### 4. タイトル + フィルタ行の非対称レイアウト

- タイトル50% + フィルタ3個（各16.7%）のパターン
- `height: 100%` + `display: flex` + `alignItems: center` で高さ揃え

### 5. 実際のCSS（コピペ可能なコードブロック）

- HAMM Overviewで使用した `.filter-row-7col` 関連CSS一式
- Mantine Chip切り詰めCSS一式

---

## 実装ステップ

### Step 1: `layout-patterns.md` 作成

`.claude/skills/dash-bi-workflow/layout-patterns.md` を新規作成。
上記セクション構成でレイアウトパターンを記述。

### Step 2: `SKILL.md` にリンク追記

Phase 2（ダッシュボードページ作成）セクションの末尾に1行追加:
```
レイアウトパターンの詳細は [layout-patterns.md](layout-patterns.md) を参照してください。
```

### Step 3: 検証

- スキルが正しく読み込めることを確認（Skill tool で `dash-bi-workflow` を起動）

---

## 参照元（実コード）

| ファイル | 該当箇所 |
|---------|---------|
| `assets/03-components.css` L135-170 | `.filter-row-7col` + Chip切り詰めCSS |
| `src/pages/hamm_overview/_layout.py` L74-149 | Row 1 (md=6/2/2/2) + Row 2 (CSS Grid 7col) |
