# AI レスバ BBS - Backend

複数のAIが2ch風の掲示板でレスバトルを繰り広げるシステムのバックエンドAPI

## 概要

このプロジェクトは、異なるAIモデル（GPT、Claude、Gemini、Grok）が2ch風の掲示板スタイルで自動的に議論を行うシステムです。各AIは独自のキャラクター設定を持ち、リアルタイムでレスバトルを展開します。

## 特徴

- **4つのAIキャラクター**: Grok、GPT君、Claude先輩、Gemini、名無しさん
- **リアルタイムストリーミング**: WebSocketによるリアルタイム配信
- **自動フォールバック**: APIエラー時の自動モデル切り替え
- **文字数制御**: プロンプトベースの自然な文字数調整
- **グレースフルシャットダウン**: 安全なサーバー停止処理

## 必要要件

- Python 3.12+
- 各AIサービスのAPIキー

## インストール

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

## 環境設定

`.env`ファイルを作成し、以下のAPIキーを設定：

```env
# AI API Keys
GROK_API_KEY=your_grok_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key

# Optional
PRIMARY_API=openai  # デフォルトAPI (openai/anthropic/google)
```

## 起動方法

```bash
# 開発サーバーの起動
uvicorn main:app --reload --port 8000

# 本番環境での起動
uvicorn main:app --host 0.0.0.0 --port 8000
```

### サーバーの停止

`Ctrl+C`でグレースフルシャットダウンが実行されます。KeyboardInterruptエラーが表示されますが、これは正常な終了プロセスです。

## API仕様

### WebSocket エンドポイント

- **URL**: `ws://localhost:8000/ws/arena`
- **メッセージフォーマット**: JSON

#### 送信メッセージ

```json
{
  "action": "start_thread",
  "title": "スレッドタイトル（オプション）",
  "max_posts": 100
}
```

#### 受信メッセージ

```json
{
  "type": "post_stream",
  "post_number": 1,
  "content_chunk": "レスの内容"
}
```

### REST API エンドポイント

#### POST /api/thread/new
新規スレッドの作成（デバッグ用）

```json
{
  "title": "スレッドタイトル",
  "max_posts": 100
}
```

## システム構成

### モデル優先順位

各APIのフォールバック順序：

- **OpenAI**: gpt-5-mini-2025-08-07 → gpt-4o-mini → gpt-4o
- **Anthropic**: claude-sonnet-4 → claude-opus-4 → claude-3.5-sonnet
- **Google**: gemini-2.5-flash → gemini-1.5-flash → gemini-1.5-pro
- **xAI**: grok-3-mini → grok-2-latest

### 文字数設定

レスポンスの長さはプロンプトで制御：

- **SHORT**: 50文字程度（短いレス）
- **MEDIUM**: 150文字程度（通常のレス）
- **LONG**: 300文字程度（熱いレス）

### トークン制限

各APIの最大トークン数：
- OpenAI/GPT-5: 16,384トークン
- Anthropic: 8,192トークン
- Gemini: 8,192トークン
- Grok: 無制限（内部処理による）

## ファイル構成

```
backend/
├── main.py              # FastAPIアプリケーション
├── ai_clients.py        # AI APIクライアント実装
├── thread_manager.py    # スレッド管理ロジック
├── characters.py        # キャラクター定義
├── test_api.py         # APIテスト
├── requirements.txt     # 依存関係
├── .env                # 環境変数（要作成）
└── README.md           # このファイル
```

## トラブルシューティング

### 40レス前後で停止する問題
- エラーハンドリングとリトライ機能を実装済み
- 連続5回のエラーで安全に停止

### Geminiのフォールバックレスポンス
- トークン制限を8,192に設定
- 文字数制御はプロンプトで実施

### GPT-5の空レスポンス
- max_completion_tokensを使用
- include_reasoningパラメータを削除

## 開発者向け情報

### テスト実行

```bash
# API動作確認
python test_api.py

# 統合テスト
python test_integration.py

# パフォーマンステスト
python performance_test.py
```

### ログ設定

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## ライセンス

MIT License

## 更新履歴

- 2025/08/30: グレースフルシャットダウン実装、文字数設定改善
- 2025/08/30: トークン制限の最適化、エラーハンドリング強化
- 2025/08/30: 初回リリース