# Napkin

## Corrections
| Date | Source | What Went Wrong | What To Do Instead |
|------|--------|----------------|-------------------|
| 2026-02-07 | self | Used exec_command to run apply_patch instead of apply_patch tool | Use apply_patch tool directly for patches |
| 2026-02-07 | self | Repeatedly used exec_command to run apply_patch despite warning | Always use apply_patch tool for patches |
| 2026-02-08 | self | Started ETL pytest run before checking test deps, failed on missing `boto3` import from `tests/conftest.py` | Check/install core test deps (at least `boto3`, `moto`) before running suite in this environment |
| 2026-02-08 | self | test_data_loader.py で19件が DATASETS NameError。メソッド内importがある関数とない関数が混在 | テストファイルで定数をメソッド内importする場合、全メソッドで統一するかトップレベルimportにする |
| 2026-02-09 | self | `python3 -m py_compile` に Markdown (`.claude/napkin.md`) を含めて失敗 | `py_compile` は Python ファイルのみに限定する |
| 2026-02-09 | self | 依存確認前に pytest を実行し `boto3`/`dash` 未インストールで停止 | この環境では最初に依存確認し、未導入時は `py_compile` と差分レビューを優先する |
| 2026-02-10 | self | セッション開始直後に napkin を読む前に `ls` を実行した | 毎セッション開始時は最初のコマンド前に `.claude/napkin.md` を確認する |
| 2026-02-10 | self | `tools/page_generator` 健全性確認で `pytest tools/page_generator` の失敗を見落としかけた | 「運用可否」の回答前に対象サブシステムのテスト結果を必ず確認し、失敗件数と内容を明示する |

## User Preferences
- Prefer YAML only for look/labels; keep calculation logic in Python templates.
- Wants human-editable settings separated clearly from non-editable logic.

## Patterns That Don't Work
- 2026-02-07: MinIO access from this environment failed (`http://localhost:9000` PermissionError). Run ParquetReader validation in the user environment where MinIO is reachable.
- 2026-02-09: `git checkout -b codex/...` can fail in sandbox because writing `.git/refs/heads/*` is blocked. Retry with escalated permissions.

## Patterns That Work
- 2026-02-08: DOMO ETL (`python3 backend/scripts/load_domo.py --dataset ...`) works when network is available. Previous DNS failure was transient.
- 2026-02-08: ISO week calculation fix in `_add_cadence_columns` - use Monday start (weekday 0 → offset 0) not Tuesday start.
- 2026-02-08: Vendor component docs (e.g., Dash Dropdown) are better captured as concise "reference notes" unless they include project-specific guardrails or repeated failure patterns.
- 2026-02-08: `_normalize_month_series` ベクトル化 — `.apply(func)` を `pd.to_datetime(..., utc=True).dt.tz_convert(None)` + `.where()` + `.dt.strftime()` に置換で66x高速化。
- 2026-02-08: キャッシュTTL 300→3600変更は日次ETLデータに適切。テスト影響なし。
- 2026-02-09: UI改善の横展開は `docs/CONTRIB.md` + `docs/tech-spec.md` + `codemaps/frontend.md` + `.claude/skills/dash-bi-workflow/SKILL.md` を同時更新すると再利用性と運用整合が高い。

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
- 2026-02-09: Dashページのチャート/テーブルは全て `dbc.Card` で囲むのが必須ルール。灰色背景（`--bg-base`）との対比で視認性向上、フィルターエリアとのデザイン統一。`hamm_overview` で実装し、`dash-bi-workflow` と `CLAUDE.md` にデフォルトルールとして記載。
- 2026-02-09: hamm_overview ページにフィルタ追加する際の修正順序: _constants.py (ID定義) → _data_loader.py (FILTER_COLUMN_MAP + load_filter_options) → _filters.py (UI作成) → _callbacks.py (Input + filter_pairs) → _layout.py (通常は自動配置)。この順序で依存関係が構成される。
- 2026-02-09: 3ダッシュボード共通化レビュー完了。cursor_usageにdbc.Card wrap、CLEAR_PAIRS、_chart_builders.py分離を追加。apac_dot_due_dateのCLEAR_PAIRSを_constants.pyに移動。hamm_overviewパターンが標準構成となった。
- 2026-02-09: チャートデザイン改善の横展開（hamm_overview → cursor_usage）完了。TDDアプローチ（RED: テスト追加 → GREEN: 実装 → REFACTOR: コードレビュー指摘対応）で実施。CSS クラスを汎用化（hamm-metadata-* → chart-density-*）し、重複ヘルパー関数を `tests/helpers/dash_test_utils.py` の `find_components()` と `src/charts/layout_helpers.py` の `apply_compact_chart_layout()` に統合。SPEC.md は技術詳細なしでユーザー視点の記述を維持。
- 2026-02-10: page_generator で再構築時、backup の YAML は旧スキーマ形式。主な変換ルール: layout の `columns` → `rows > items`, コンポーネントに `spec` フィールド追加（KPI: KPICardSpec, Chart: title必須, Table: title必須）, pivot の `columns` → `columns_pivot`。
- 2026-02-10: page_generator の chip_group フィルタ（column=None）は schema.py と data_loader.py.j2 の両方で guard が必要。schema.py の validate_column_references と テンプレートの `.startswith()` 呼び出し箇所。
- 2026-02-10: hamm_overview 再構築で自動生成コードと既存テスト（298件）の整合を取る際、_constants.py にエイリアス定数（ERV_LABEL, PRELIM_LABEL, 短縮ID等）と _callbacks.py に compute_volume_kpis 等のビジネスロジック関数を追加する必要があった。自動生成はスキャフォールドに留め、手動で接合するのが現実的。
- 2026-02-10: `page_generator` は `_constants.py/_layout.py/_filters.py/_data_loader.py/_callbacks.py/_chart_builders.py/_custom_logic.py` を生成するが、`__init__.py`・`SPEC.md`・`data_sources.yml`・`app.py` インポート追記は生成対象外。新規ページ完成には手動工程が残る。
- 2026-02-10: `python3 -m pytest -q tools/page_generator` 実行で 8 件失敗（`tools/page_generator/test_data_loader_gen.py`）。主因は `DataTransformSpec` を dict として扱う旧テスト（`.get` 呼び出し）と import 期待値のずれ。
