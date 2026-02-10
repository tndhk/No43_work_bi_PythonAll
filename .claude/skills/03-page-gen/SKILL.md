---
name: 03-page-gen
description: Use when creating new Dash dashboard pages or regenerating existing pages using tools/page_generator. Triggered by new page requests, page_spec.yaml editing, or YAML-driven page generation.
---

# YAML駆動ダッシュボードページ生成ワークフロー

## 1. 前提条件

- データがMinIOにParquet形式でアップロード済みであること
- データ取得・ETLが必要な場合は `01-etl` スキルを参照
- Python 3.11以上

## 2. クイックスタートチェックリスト

Phase 1〜5のチェックリスト:

- [ ] Phase 1: page_spec.yaml 作成（→ `02-page-spec` スキル）
- [ ] Phase 2: コード生成（dry-run → 本実行）
- [ ] Phase 3: 手動ファイル作成（__init__.py, data_sources.yml, SPEC.md）
- [ ] Phase 4: カスタムロジック実装（必要時）
- [ ] Phase 5: 動作確認（app.pyインポート + 検証チェックリスト）

---

## 3. Phase 1: page_spec.yaml 作成

`02-page-spec` スキルを使用してください。
データ探索からYAMLバリデーションまでの完全なワークフローを提供します。

完了条件: `python3 -m tools.page_generator src/pages/<page_name> --dry-run` がエラーなく通ること。

> 既存の page_spec.yaml を軽微に修正する場合は、
> `docs/page-spec-reference.md` を参照して直接編集し、dry-run で検証してください。

---

## 4. Phase 2: コード生成

```bash
# バリデーション（必須。先にdry-runで確認）
python3 -m tools.page_generator src/pages/<page_name> --dry-run

# 全ファイル生成
python3 -m tools.page_generator src/pages/<page_name>

# 部分再生成（既存ファイルの一部のみ更新したい場合）
python3 -m tools.page_generator src/pages/<page_name> --files constants layout
```

生成されるファイル:

- `_constants.py`
- `_layout.py`
- `_filters.py`
- `_data_loader.py`
- `_callbacks.py`
- `_chart_builders.py`
- `_custom_logic.py`（オプション）

---

## 5. Phase 3: 手動ファイル作成

以下の3ファイルはpage_generatorが生成しないため、手動作成が必須。

### __init__.py

```python
"""<Page Name> page."""
import dash

from ._layout import build_layout
from . import _callbacks  # noqa: F401


dash.register_page(
    __name__,
    path="/<page-url-path>",
    name="<Page Display Name>",
    order=<number>,
    layout=build_layout,
)
```

### data_sources.yml

```yaml
charts:
  <id_prefix>kpi-xxx: <dataset_id>
  <id_prefix>chart-xxx: <dataset_id>
  <id_prefix>table-xxx: <dataset_id>
```

全コンポーネントIDとデータセットIDのマッピングを記述。

### SPEC.md

`spec-updater` スキルに従って作成。日本語、技術詳細なし。

---

## 6. Phase 4: カスタムロジック実装（必要時）

`_custom_logic.py` にスケルトンが生成されるので、関数本体を実装する。

分離基準:

- 10行以上の複雑なデータ変換
- 複数コンポーネントで再利用する処理
- 単体テストが必要な処理

---

## 7. Phase 5: 動作確認

### app.py へのインポート追加

```python
import src.pages.<page_name>  # noqa: F401
```

### 検証チェックリスト

- [ ] `python3 -m tools.page_generator <dir> --dry-run` がエラーなく通る
- [ ] 全ファイルが生成されている（_constants.py, _layout.py, _filters.py, _data_loader.py, _callbacks.py, _chart_builders.py）
- [ ] __init__.py が作成されている（dash.register_page含む）
- [ ] data_sources.yml が作成されている（全コンポーネントIDを含む）
- [ ] SPEC.md が作成されている
- [ ] app.py にインポートが追加されている
- [ ] カスタムロジックがある場合、_custom_logic.py の関数が実装されている
- [ ] ダッシュボードがエラーなく表示される
- [ ] 全てのフィルタが正しく動作する
- [ ] 全てのKPIカード、チャート、テーブルが正しく表示される

---

## 8. dash-manual との使い分け

| 条件 | 使うスキル | 理由 |
|------|-----------|------|
| 新規ダッシュボード作成 | 03-page-gen | YAMLから自動生成が圧倒的に効率的 |
| 既存page_spec.yaml変更後の再生成 | 03-page-gen | --filesで部分再生成可能 |
| page_generatorで対応できないカスタムUI | dash-manual | 手書きが必要な場合 |
| フィルタ追加・コールバック修正のみ | dash-manual | 既存コード修正は手動の方が適切 |
| 既存手書きページの保守 | dash-manual | page_spec.yaml がないページ |

---

## 9. よくある失敗パターン

| 失敗パターン | 合理化メッセージ | 正しい行動 |
|-------------|-----------------|-----------|
| テンプレートを使わず手書き開始 | 「hamm_overviewのPythonを参考に書く方が早い」 | テンプレートをコピーしてYAMLを編集する |
| hamm_overviewの生成済みPythonをコピー | 「既存コードを流用すれば確実」 | page_spec.yamlをコピーして修正する |
| --dry-runをスキップ | 「YAMLは正しいはず」 | 必ずdry-runでバリデーション |
| __init__.py / data_sources.yml を忘れる | 「page_generatorが全部生成してくれたはず」 | Phase 3の手動ファイルを確認 |
| SPEC.md を作成しない | 「後で書く」 | Phase 3で必ず作成 |
| ID_PREFIXの不統一 | 「気にしなくても動く」 | metadata.id_prefix を全IDに一貫して使用 |
| data_transformの操作順序ミス | 「どの順でも同じ結果になるはず」 | filter → group_by → pivot → rename → sort |
| column_map未定義のカラム参照 | 「物理名で直接書けば動く」 | 全カラムをcolumn_mapに定義 |
| app.pyへのインポート追加を忘れる | 「自動検出されるはず」 | 明示的にインポートを追加 |

---

## 10. 参照ドキュメント

| ドキュメント | 用途 |
|------------|------|
| `tools/page_generator/templates/new_page_spec.yaml` | YAMLテンプレート（コピー元） |
| `docs/page-spec-reference.md` | YAML完全リファレンス |
| `tools/page_generator/README.md` | ツールのCLI使用方法 |
| `src/pages/hamm_overview/page_spec.yaml` | 実稼働ページの実装例 |
| `docs/CONTRIB.md` sec.9 | SPEC-Driven Dashboard Page Creation |
| `tools/page_generator/schema.py` | Pydanticスキーマ定義（YAML構造の正式定義） |

---

## 11. 関連スキル

- `02-page-spec`: page_spec.yaml の設計・作成ワークフロー（Phase 1 で使用）
- `01-etl`: データ取得・ETL処理（page_spec.yaml作成前にデータが必要）
- `dash-manual`: 手書きダッシュボード開発（page_generator非対応の場合）
- `spec-updater`: SPEC.md作成・更新
