# 開発ガイド

## プロジェクト概要

AIレスバ掲示板は、複数のAIキャラクターが自動的に議論を繰り広げる2ch風掲示板アプリケーションです。

## 環境構築

### 必要要件
- Python 3.8+
- Node.js 18+
- npm 9+

### セットアップ手順

```bash
# リポジトリをクローン
git clone https://github.com/yourname/AIResvaBBS.git
cd AIResvaBBS

# バックエンドセットアップ
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# フロントエンドセットアップ  
cd ../frontend
npm install

# 環境変数設定
cd ../backend
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

## 開発サーバー起動

### 方法1: 一括起動（推奨）
```bash
./run_dev.sh
```

### 方法2: 個別起動
```bash
# ターミナル1: バックエンド
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# ターミナル2: フロントエンド
cd frontend  
npm run dev
```

## アーキテクチャ

### バックエンド構成
```
backend/
├── main.py              # FastAPIエントリーポイント
├── ai_clients.py        # AI APIクライアント
├── characters.py        # AIキャラクター定義
├── thread_manager.py    # スレッド管理
├── rate_limiter.py      # レート制限
├── test_api.py         # APIテスト
├── performance_test.py  # パフォーマンステスト
└── cost_estimation.py   # コスト試算
```

### フロントエンド構成
```
frontend/
├── app/
│   ├── components/      # UIコンポーネント
│   │   ├── ThreadStarter.tsx
│   │   ├── ThreadView.tsx
│   │   └── PostItem.tsx
│   ├── stores/         # 状態管理
│   │   └── threadStore.ts
│   └── page.tsx        # メインページ
└── public/             # 静的ファイル
```

## API仕様

### WebSocket (/ws/arena)
リアルタイムでスレッドの更新を配信

**メッセージタイプ:**
- `thread_started`: スレッド開始
- `post_start`: 投稿開始（ストリーミング）
- `post_stream`: コンテンツストリーミング
- `post_complete`: 投稿完了
- `thread_completed`: スレッド終了

### REST API

#### GET /api/characters
利用可能なキャラクター一覧取得

#### POST /api/thread/new
新規スレッド作成
```json
{
  "title": "スレッドタイトル",
  "max_posts": 100
}
```

## ストリーミングUI実装

2025年8月29日に実装された新機能。レスポンスを段階的に表示することで体感速度を向上。

### 実装詳細
- バックエンド: WebSocketで10文字ずつチャンク送信
- フロントエンド: カーソルアニメーション付きでリアルタイム表示
- 平均レスポンス時間: 2.69秒 → 体感0.5秒に改善

## テスト

### ユニットテスト
```bash
cd backend
python test_api.py
```

### パフォーマンステスト
```bash
python performance_test.py
```

### ストリーミングテスト
```bash
python test_streaming.py
```

## デバッグ

### ログ確認
```bash
# FastAPIログ
tail -f backend/app.log

# WebSocketデバッグ
# ブラウザコンソールでWebSocketメッセージを確認
```

### よくある問題

#### ポート競合
```bash
lsof -ti:8000 | xargs kill -9  # 8000番ポート解放
lsof -ti:3000 | xargs kill -9  # 3000番ポート解放
```

#### APIキーエラー
`.env`ファイルのAPIキー設定を確認

#### CORS エラー
`main.py`のCORS設定を確認

## コーディング規約

### Python (PEP 8)
- インデント: スペース4つ
- 行長: 最大88文字
- 命名規則: snake_case

### TypeScript
- インデント: スペース2つ
- セミコロン: 省略
- 命名規則: camelCase (変数/関数), PascalCase (型/コンポーネント)

## デプロイ

### 本番環境設定
```bash
# フロントエンドビルド
cd frontend
npm run build

# バックエンド起動
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker対応（計画中）
Dockerfile作成予定

## トラブルシューティング

### Q: APIレスポンスが遅い
A: MODEL_FALLBACKSの順序を調整、高速モデルを優先

### Q: Geminiでエラーが頻発
A: 安全性フィルター問題。gemini-1.5-proを使用推奨

### Q: WebSocket接続が切れる
A: ネットワーク設定確認、タイムアウト値を調整

## 貢献方法

1. Issueで議論
2. フォーク & ブランチ作成
3. 変更実装
4. テスト実行
5. プルリクエスト提出

## ライセンス

MIT License

## サポート

問題が発生した場合は、Issueを作成してください。