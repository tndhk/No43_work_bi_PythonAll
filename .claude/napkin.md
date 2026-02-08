# Napkin

## Corrections
| Date | Source | What Went Wrong | What To Do Instead |
|------|--------|----------------|-------------------|
| 2026-02-07 | self | Used exec_command to run apply_patch instead of apply_patch tool | Use apply_patch tool directly for patches |
| 2026-02-07 | self | Repeatedly used exec_command to run apply_patch despite warning | Always use apply_patch tool for patches |
| 2026-02-08 | self | Started ETL pytest run before checking test deps, failed on missing `boto3` import from `tests/conftest.py` | Check/install core test deps (at least `boto3`, `moto`) before running suite in this environment |
| 2026-02-08 | self | test_data_loader.py で19件が DATASETS NameError。メソッド内importがある関数とない関数が混在 | テストファイルで定数をメソッド内importする場合、全メソッドで統一するかトップレベルimportにする |

## User Preferences
- Prefer YAML only for look/labels; keep calculation logic in Python templates.
- Wants human-editable settings separated clearly from non-editable logic.

## Patterns That Don't Work
- 2026-02-07: MinIO access from this environment failed (`http://localhost:9000` PermissionError). Run ParquetReader validation in the user environment where MinIO is reachable.

## Patterns That Work
- 2026-02-08: DOMO ETL (`python3 backend/scripts/load_domo.py --dataset ...`) works when network is available. Previous DNS failure was transient.
- 2026-02-08: ISO week calculation fix in `_add_cadence_columns` - use Monday start (weekday 0 → offset 0) not Tuesday start.
- 2026-02-08: Vendor component docs (e.g., Dash Dropdown) are better captured as concise "reference notes" unless they include project-specific guardrails or repeated failure patterns.
- 2026-02-08: `_normalize_month_series` ベクトル化 — `.apply(func)` を `pd.to_datetime(..., utc=True).dt.tz_convert(None)` + `.where()` + `.dt.strftime()` に置換で66x高速化。
- 2026-02-08: キャッシュTTL 300→3600変更は日次ETLデータに適切。テスト影響なし。

## Domain Notes
- (project/domain context that matters)
- 2026-02-08: docs同期タスクで `package.json` 指定があっても、このリポジトリは非Node構成で `package.json` が存在しない。scripts表は「未定義」を明示し、補助的に `pyproject.toml` と `backend/scripts/*.py` を参照して運用コマンドを文書化する。
- 2026-02-08: `.claude/skills/dash-bi-workflow/SKILL.md` と `.codex/skills/dash-bi-workflow/SKILL.md` はシンボリックリンクではなく同一inode（ハードリンク）。
- 2026-02-08: `apac_dot_due_date` フィルタは2段構成（上段3-4ブロック、下段5ブロック）へ再編しても、既存IDを維持すればコールバック互換を保てる。
- 2026-02-08: `src.pages.apac_dot_due_date._data_loader` を直接 import すると `__init__.py` の `dash.register_page` が走って PageError になる場合がある。ページ配下モジュールの単体確認は `py_compile` 優先。

- 2026-02-08: `apac_dot_due_date` の callback テスト3件は `build_pivot_table` の位置引数前提で失敗。実装はキーワード引数呼び出しのため、テスト修正が必要（UI Slicer変更とは独立）。
- 2026-02-08: dmc.ChipGroupを使うページでは対象コンポーネントがMantineProvider配下である必要。全体を包むとlayoutテスト前提を崩す場合があるため、必要な行のみMantineProviderでラップする。
- 2026-02-08: Slicer単位のClear要求では、全体ボタンより `create_slicer_filter` に clear button オプションを追加してヘッダー内で統一実装するとレイアウト差分を最小化できる。
- 2026-02-08: Slicerの標準化は `create_slicer_filter` に clear UI を集約し、各ページで clear callback だけ追加する構成が最小変更で横展開しやすい。- 2026-02-08: AGENTS.md で Markdown太字と絵文字が禁止。ドキュメント更新時も `**` と emoji を使わない。
- 2026-02-08: ドキュメント更新はリポジトリで確認できる運用だけを記載し、未確認インフラ前提はTBD明記が必要。
- 2026-02-08: ドキュメント刷新時、既存RUNBOOKに未確認クラウド前提が混在していたため、Compose運用ベースに置換しTBDを明記すると整合が保てる。
