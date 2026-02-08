# ドキュメント同期 (update-docs)

## Context

最近のETL機能追加（masking, exclude_filter）、ダッシュボードページ更新（hamm_overview追加）、Dash 4.x対応等の変更に対し、ドキュメントが部分的に追従していない。主要ドキュメント（CONTRIB.md, RUNBOOK.md）を現状のコードベースと同期させる。

## 変更サマリー

### 1. `.env.example` に ETL変数を追加

ファイル: `.env.example`

現状の変数（S3 + Auth）に加え、以下を追加:

```
# DOMO API (ETL)
DOMO_CLIENT_ID=
DOMO_CLIENT_SECRET=

# ETL Masking (HMAC-SHA256)
ETL_MASKING_SECRET=
```

理由: CONTRIB.md の環境変数テーブルのソースが `.env.example` であり、ETL利用者が設定漏れしやすい。

### 2. `docs/CONTRIB.md` の更新

ファイル: `docs/CONTRIB.md`

(a) sec.3 環境変数テーブルに3行追加:

| 変数名 | デフォルト値 | 目的 | 形式 |
|---|---|---|---|
| `DOMO_CLIENT_ID` | (空) | DOMO API Client ID（ETL用） | DOMO Developer Portalで発行 |
| `DOMO_CLIENT_SECRET` | (空) | DOMO API Client Secret（ETL用） | DOMO Developer Portalで発行 |
| `ETL_MASKING_SECRET` | (空) | ETLマスキング用秘密鍵（masking有効時のみ必須） | 任意の文字列 |

(b) sec.6 プロジェクト構造に `hamm_overview/` を追加:

```
    pages/
      cursor_usage/
      apac_dot_due_date/
      hamm_overview/           # ← 追加
```

(c) 最終更新日を `2026-02-08 (rev.5)` に更新

### 3. `docs/RUNBOOK.md` の更新

ファイル: `docs/RUNBOOK.md`

(a) sec.3 追加設定テーブルに `ETL_MASKING_SECRET` を追加:

| 変数 | 説明 | 備考 |
|---|---|---|
| `ETL_MASKING_SECRET` | ETLマスキング用HMAC秘密鍵 | masking有効なDataSet使用時に必須 |

(b) sec.5 に Issue 9 を追加: ETLマスキングエラー

```
### Issue 9: ETLマスキングが失敗する

症状: `ETL_MASKING_SECRET environment variable is required` エラー

解決策:
- `.env` に `ETL_MASKING_SECRET` を設定
- `backend/config/{csv,domo}_datasets.yaml` の `masking.enabled` を確認
- `masking.strict: true` の場合、対象カラムがデータに存在するか確認
```

(c) 最終更新日を `2026-02-08 (rev.5)` に更新

### 4. 不要CSSルールの特定（報告のみ）

`assets/03-components.css` の `.mantine-ChipGroup-root` ルールは dmc 2.5.1 では無効。
削除は別タスクとし、本プランでは報告のみ。

## 修正対象ファイル一覧

| ファイル | 変更種別 |
|---|---|
| `.env.example` | 3変数追加 |
| `docs/CONTRIB.md` | 環境変数テーブル + プロジェクト構造更新 |
| `docs/RUNBOOK.md` | 追加設定 + トラブルシューティング追加 |

## 検証

```bash
# ドキュメント内のリンク切れ確認（手動）
# .env.example の変数が CONTRIB.md テーブルと一致しているか目視確認
# RUNBOOK.md の環境変数が .env.example + CONTRIB.md と整合しているか確認
```
