# GitHub Actions CI パイプライン構築

## Context

RUNBOOK.md にて「CI/CDパイプライン定義 [TBD]」と記載されており、CI未整備。
PR前の品質チェック (ruff, mypy, pytest) が手動実行に依存しているため、
GitHub Actionsで自動化し、PRマージ前の品質ゲートを確立する。

## 変更対象ファイル

| ファイル | 操作 | 目的 |
|----------|------|------|
| `.github/workflows/ci.yml` | 新規作成 | CIワークフロー定義 |
| `requirements-dev.txt` | 新規作成 | 開発/テスト依存の分離 |
| `requirements.txt` | 修正 | テスト依存 (pytest, pytest-cov, moto) を除去 |
| `pyproject.toml` | 修正 | mypy の ignore_missing_imports 追加 |
| `Dockerfile.dev` | 修正 | requirements-dev.txt も pip install |

## 実装ステップ

### Step 1: requirements-dev.txt 新規作成

```
# Development and test dependencies
# Usage: pip install -r requirements.txt -r requirements-dev.txt

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
moto[s3]>=5.0.0

# Linting
ruff>=0.4.0

# Type checking
mypy>=1.9.0
```

### Step 2: requirements.txt から テスト依存を除去

以下3行を削除:
- `moto[s3]>=5.0.0` (L16)
- `pytest>=7.0.0` (L17)
- `pytest-cov>=4.0.0` (L18)

### Step 3: pyproject.toml に mypy overrides 追加

現状 `pyarrow.*` と `botocore.*` のみ。以下モジュールの型スタブが存在しないため追加:
- `dash.*`
- `dash_bootstrap_components.*`
- `dash_mantine_components.*`
- `flask_caching.*`
- `flask_login.*`
- `plotly.*`

NOTE: 追加前に `mypy src/` をローカル実行して不足分を確認する。

### Step 4: Dockerfile.dev 修正

```dockerfile
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
```

理由: docker-compose.yml の test サービスが同じ Dockerfile.dev を使用しているため、
テスト依存が requirements-dev.txt に移動した後もビルドが通るようにする。

### Step 5: .github/workflows/ci.yml 新規作成

3並列ジョブ構成:

```
lint (ruff)          -- ruff のみインストール、高速完了
typecheck (mypy)     -- 全依存 + mypy インストール
test (pytest)        -- 全依存 + テストツール、カバレッジレポート付き
```

トリガー: PR (main向け) + main への push
concurrency: 同一ref で cancel-in-progress

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.9"
      - run: pip install ruff
      - run: ruff check src/

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.9"
          cache: pip
          cache-dependency-path: |
            requirements.txt
            requirements-dev.txt
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: mypy src/

  test:
    runs-on: ubuntu-latest
    env:
      ENV: test
      S3_ENDPOINT: ""
      S3_REGION: ap-northeast-1
      S3_BUCKET: bi-datasets
      S3_ACCESS_KEY: test
      S3_SECRET_KEY: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.9"
          cache: pip
          cache-dependency-path: |
            requirements.txt
            requirements-dev.txt
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest -v --tb=short
```

設計ポイント:
- lint ジョブは ruff のみインストール (本番依存不要で高速)
- typecheck は全依存が必要 (import解決のため)
- test の環境変数は docker-compose.yml の test サービスと同一
- pytest の `--cov=src --cov=backend --cov-report=term-missing` は pyproject.toml の addopts で自動適用
- カバレッジ閾値は設定しない (レポートのみ)

## 検証手順

1. ローカルで各チェックが通ることを確認:
   ```bash
   ruff check src/
   mypy src/
   pytest -v --tb=short
   ```
2. Docker テストサービスが動作することを確認:
   ```bash
   docker compose run --rm test
   ```
3. GitHub に push 後、Actions タブで3ジョブが全て green になることを確認
