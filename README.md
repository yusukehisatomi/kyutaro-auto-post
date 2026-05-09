# X（Twitter）自動投稿スクリプト

Googleスプレッドシートで管理した投稿をX API v2で自動投稿するシステムです。  
GitHub Actionsで毎日21:00 JST（12:00 UTC）に実行されます。

## ディレクトリ構成

```
.
├── post_to_x.py                   # メインスクリプト
├── requirements.txt               # 依存ライブラリ
├── sample_data.csv                # スプレッドシート初期データ
└── .github/workflows/post_to_x.yml  # GitHub Actions ワークフロー
```

## Googleスプレッドシートの設定

### 列構成

| 列 | 項目名 | 内容 |
|----|--------|------|
| A | id | 連番 |
| B | text | 投稿本文 |
| C | scheduled_date | 投稿予定日（YYYY-MM-DD） |
| D | posted | 投稿済みフラグ（TRUE / FALSE） |

### 初期データの投入

`sample_data.csv` の内容をスプレッドシートにコピーしてください。  
1行目はヘッダー行（id, text, scheduled_date, posted）として使用します。

## セットアップ手順

### 1. Googleサービスアカウントの作成

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. 「APIとサービス」→「ライブラリ」から **Google Sheets API** を有効化
3. 「APIとサービス」→「認証情報」→「サービスアカウントを作成」
4. サービスアカウントのJSONキーをダウンロード
5. スプレッドシートの共有設定でサービスアカウントのメールアドレスに **編集者** 権限を付与

### 2. JSONキーをBase64エンコード

```bash
base64 -i your-service-account.json | tr -d '\n'
```

出力された文字列を `GOOGLE_CREDENTIALS` シークレットに設定します。

### 3. X（Twitter）API認証情報の取得

[X Developer Portal](https://developer.twitter.com/) で以下を取得：

- API Key → `X_API_KEY`
- API Key Secret → `X_API_KEY_SECRET`
- Access Token → `X_ACCESS_TOKEN`
- Access Token Secret → `X_ACCESS_TOKEN_SECRET`

アクセストークンの権限は **Read and Write** が必要です。

### 4. GitHub Secretsの設定

リポジトリの「Settings」→「Secrets and variables」→「Actions」から以下を設定：

| シークレット名 | 値 |
|---------------|----|
| `X_API_KEY` | X APIキー |
| `X_API_KEY_SECRET` | X APIキーシークレット |
| `X_ACCESS_TOKEN` | Xアクセストークン |
| `X_ACCESS_TOKEN_SECRET` | Xアクセストークンシークレット |
| `GOOGLE_CREDENTIALS` | サービスアカウントJSONのBase64文字列 |
| `SPREADSHEET_ID` | スプレッドシートのID（URLの `/d/` と `/edit` の間の文字列） |

## 動作確認（手動実行）

GitHub Actionsの「Actions」タブ → 「Post to X」→ 「Run workflow」から手動実行できます。

## ローカルでのテスト

```bash
pip install -r requirements.txt

export X_API_KEY=your_key
export X_API_KEY_SECRET=your_secret
export X_ACCESS_TOKEN=your_token
export X_ACCESS_TOKEN_SECRET=your_token_secret
export GOOGLE_CREDENTIALS=$(base64 -i your-service-account.json | tr -d '\n')
export SPREADSHEET_ID=your_spreadsheet_id

python post_to_x.py
```
