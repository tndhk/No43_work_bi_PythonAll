# update-codemaps.md Python対応 書き換え計画

## Context

前回 `/update-docs` スキルの Python 対応を完了。今回は `/update-codemaps` スキルに残る Node.js/TypeScript 固有記述を修正する。

現状の問題:
- `update-codemaps.md` に "TypeScript/Node.js tooling" / "TypeScript/Node.js for static analysis" という記述が2箇所残存
- 存在しないテンプレートファイル (`codemap-template.md`, `diff-report-template.txt`) への参照がある
- `codemaps-guide.md` の出力ディレクトリが `docs/codemaps/` になっているが、実際は `codemaps/` (ルート直下)

---

## 課題サマリ

| # | 箇所 | 深刻度 | ファイル |
|---|------|--------|---------|
| 1 | L27 "TypeScript/Node.js tooling" | 高 | `update-codemaps.md` |
| 2 | L55 "Use TypeScript/Node.js for static analysis" | 高 | `update-codemaps.md` |
| 3 | L49 存在しない `codemap-template.md` 参照 | 高 | `update-codemaps.md` |
| 4 | L50 存在しない `diff-report-template.txt` 参照 | 高 | `update-codemaps.md` |
| 5 | L283 出力先 `docs/codemaps` → `codemaps` | 中 | `codemaps-guide.md` |
| 6 | L373 デフォルトパス `docs/codemaps` → `codemaps` | 中 | `codemaps-guide.md` |
| 7 | L420 出力先 `docs/codemaps/` → `codemaps/` | 中 | `codemaps-guide.md` |

---

## 実装タスク

### Task A: `update-codemaps.md` の4箇所修正

ファイル: `~/.claude/commands/update-codemaps.md`

#### Edit 1 - L27: TypeScript/Node.js tooling 参照を修正

変更前:
```
The doc-updater agent coordinates with TypeScript/Node.js tooling to perform the analysis and document generation.
```
変更後:
```
The doc-updater agent coordinates with Python tooling (ast/importlib) to perform the analysis and document generation.
```

#### Edit 2 - L49: 存在しないテンプレート参照を修正

変更前:
```
- `~/.claude/templates/doc-updater/codemap-template.md` - Codemap format specification
```
変更後:
```
- `~/.claude/templates/doc-updater/codemaps-guide.md` - Codemap format specification and analysis guide
```

#### Edit 3 - L50: 存在しないテンプレート参照を削除

変更前:
```
- `~/.claude/templates/doc-updater/diff-report-template.txt` - Diff reporting format
```
変更後: (行ごと削除)

#### Edit 4 - L55: TypeScript/Node.js 静的解析の参照を修正

変更前:
```
- Use TypeScript/Node.js for static analysis of imports and exports
```
変更後:
```
- Use Python ast module for static analysis of imports and exports
```

### Task B: `codemaps-guide.md` の出力ディレクトリパス3箇所修正

ファイル: `~/.claude/templates/doc-updater/codemaps-guide.md`

#### Edit 5 - L283: Usage docstring のパス

変更前: `python generate_codemaps.py --src-dir src --output-dir docs/codemaps`
変更後: `python generate_codemaps.py --src-dir src --output-dir codemaps`

#### Edit 6 - L373: argparse デフォルト値

変更前: `parser.add_argument("--output-dir", type=Path, default=Path("docs/codemaps"))`
変更後: `parser.add_argument("--output-dir", type=Path, default=Path("codemaps"))`

#### Edit 7 - L420: 説明文のパス

変更前: `` This will analyze the project and generate/update codemap files in `docs/codemaps/`. ``
変更後: `` This will analyze the project and generate/update codemap files in `codemaps/`. ``

---

## 変更対象ファイル一覧

| ファイル | 操作 | 編集数 |
|---------|------|--------|
| `~/.claude/commands/update-codemaps.md` | 編集 | 4箇所 |
| `~/.claude/templates/doc-updater/codemaps-guide.md` | 編集 | 3箇所 |

---

## 変更不要と確認済み

- `~/.claude/templates/doc-updater/docs-update-guide.md` -- 前回対応済み
- `~/.claude/templates/doc-updater/pr-template.md` -- 言語非依存
- `~/.claude/templates/doc-updater/quality-checklist.md` -- 前回対応済み
- `codemaps/` 配下の4ファイル -- 既にPython/Dash向けに正しく生成済み
- `.reports/codemap-diff.txt` -- 正常動作中

---

## 検証手順

1. `grep "TypeScript\|Node.js" ~/.claude/commands/update-codemaps.md` → 0件であること
2. `grep "docs/codemaps" ~/.claude/templates/doc-updater/codemaps-guide.md` → 0件であること
3. 参照パス `~/.claude/templates/doc-updater/codemaps-guide.md` が実在すること
4. `/update-codemaps` を実行し、エラーなく完了すること
5. 出力が `codemaps/` (ルート直下) に生成されること
