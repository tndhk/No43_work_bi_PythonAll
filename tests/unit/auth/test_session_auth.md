# テスト観点表: Flask-Login認証

| Case ID | Input / Precondition | Perspective (Equivalence / Boundary) | Expected Result | Notes |
|---------|---------------------|--------------------------------------|----------------|-------|
| TC-N-01 | 正しいユーザー名/パスワードでログイン | Equivalence - normal | ログイン成功、セッションにユーザー情報保存、リダイレクト | - |
| TC-N-02 | ログイン済みユーザーがダッシュボードにアクセス | Equivalence - normal | ダッシュボード表示 | - |
| TC-N-03 | ログイン済みユーザーがログアウト | Equivalence - normal | セッションクリア、ログイン画面へリダイレクト | - |
| TC-A-01 | 間違ったユーザー名でログイン | Equivalence - abnormal | ログイン失敗、エラーメッセージ表示 | - |
| TC-A-02 | 間違ったパスワードでログイン | Equivalence - abnormal | ログイン失敗、エラーメッセージ表示 | - |
| TC-A-03 | 空のユーザー名でログイン | Boundary - empty | バリデーションエラー | - |
| TC-A-04 | 空のパスワードでログイン | Boundary - empty | バリデーションエラー | - |
| TC-A-05 | 未認証ユーザーがダッシュボードにアクセス | Equivalence - abnormal | ログイン画面へリダイレクト | - |
| TC-A-06 | セッション期限切れ後にダッシュボードアクセス | Equivalence - abnormal | ログイン画面へリダイレクト | - |
| TC-B-01 | ユーザー名: 最小長（1文字） | Boundary - minimum | ログイン成功（有効な場合） | - |
| TC-B-02 | ユーザー名: 最大長（設定による） | Boundary - maximum | ログイン成功またはバリデーションエラー | - |
| TC-B-03 | パスワード: 最小長（1文字） | Boundary - minimum | ログイン成功（有効な場合） | - |
| TC-B-04 | パスワード: 最大長（設定による） | Boundary - maximum | ログイン成功またはバリデーションエラー | - |
| TC-B-05 | ユーザー名: NULL/None | Boundary - NULL | バリデーションエラー | - |
| TC-B-06 | パスワード: NULL/None | Boundary - NULL | バリデーションエラー | - |
| TC-E-01 | 認証プロバイダーが例外を発生 | Equivalence - abnormal | エラーハンドリング、ログイン失敗 | - |
| TC-E-02 | セッション保存時にエラー発生 | Equivalence - abnormal | エラーハンドリング、ログイン失敗 | - |
| TC-U-01 | ログイン後にユーザーのgroupsプロパティが空リスト | Equivalence - normal | groups = [] | 将来拡張用 |
| TC-U-02 | ログイン後にユーザーのidプロパティが設定される | Equivalence - normal | id = ユーザー名 | - |
