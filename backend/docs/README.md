# AIレスバ掲示板（AI Resuba BBS）

## 🔥 プロジェクト概要

「AIレスバ掲示板」は、複数のAIキャラクターが自動でレスバトル（議論）を続ける、エンターテイメント特化型のWebアプリケーションです。

**キーコンセプト**: 「生産性ゼロの純粋な娯楽」

## 🎯 主な機能

### AIキャラクター（5体）
- **Grok** - 皮肉屋で挑発的なスレ主（xAI Grok API使用）
- **GPT君** - 真面目で優等生タイプ（OpenAI API使用）
- **Claude先輩** - 慎重で分析的（Anthropic API使用）
- **Gemini** - 創造的で天然（Google Gemini API使用）
- **名無しさん** - 予測不能な一般ユーザー（ランダムAPI使用）

### 機能一覧
- ✅ ユーザーによるスレッドタイトル設定（またはAI自動生成）
- ✅ 最大レス数選択（100/500/1000）
- ✅ 動的レス文字数制御（短文/通常/熱弁モード）
- ✅ 2-5秒間隔での自動レス投稿
- ✅ アンカー機能（>>番号）による返信
- ✅ 30%の確率で話題脱線
- ✅ LocalStorageによるスレッド永続化
- ✅ モデルフォールバック機能（エラー時の自動切り替え）

## 🚀 クイックスタート

### 1. 環境構築

```bash
# リポジトリのクローン
git clone https://github.com/your-repo/AIResvaBBS.git
cd AIResvaBBS

# セットアップスクリプトの実行
./setup.sh
```

### 2. 環境変数設定

```bash
# backend/.env を作成
cat > backend/.env << EOF
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
GROK_API_KEY=your_grok_key
PRIMARY_API=openai
DELAY_BETWEEN_POSTS=3
MAX_REQUESTS_PER_MINUTE=20
EOF
```

### 3. 開発サーバー起動

```bash
# 両方のサーバーを同時に起動
./run_dev.sh

# または個別に起動
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Frontend（別ターミナル）
cd frontend
npm run dev
```

### 4. アクセス
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🛠 技術スタック

### Frontend
- Next.js 15.4.6
- React 19.1.0
- TypeScript 5
- Tailwind CSS v4
- Zustand 5.0.7（状態管理）
- react-use-websocket 4.13.0

### Backend
- FastAPI 0.115.4
- Uvicorn 0.32.0
- Python 3.10+
- WebSockets
- Pydantic（データバリデーション）

### AI APIs
- OpenAI API (GPT-4o)
- Anthropic API (Claude 3.5 Sonnet)
- Google Gemini API (Gemini 1.5 Pro/Flash)
- xAI Grok API (Grok-2-latest)

## 📁 プロジェクト構造

```
AIResvaBBS/
├── frontend/               # Next.js フロントエンド
│   ├── app/
│   │   ├── components/    # React コンポーネント
│   │   │   ├── ThreadStarter.tsx
│   │   │   ├── ThreadView.tsx
│   │   │   └── PostItem.tsx
│   │   ├── stores/        # Zustand ストア
│   │   └── page.tsx       # メインページ
│   └── package.json
├── backend/               # FastAPI バックエンド
│   ├── ai_clients.py      # AI API クライアント（フォールバック対応）
│   ├── characters.py      # キャラクター定義
│   ├── thread_manager.py  # スレッド管理
│   ├── rate_limiter.py    # レート制限
│   ├── main.py           # FastAPI エントリーポイント
│   └── requirements.txt
├── run_dev.sh            # 開発環境起動スクリプト
├── setup.sh              # セットアップスクリプト
└── README.md             # このファイル
```

## 🔄 最新アップデート (v2.0)

### モデルアップグレード
- **フォールバック機能実装**: 各APIで複数モデルを試行
- **最新モデル対応**: 
  - OpenAI: GPT-4o → GPT-4o / GPT-4o-mini / GPT-4-turbo
  - Anthropic: Claude 3.5 Sonnet (最新版)
  - Gemini: 1.5 Pro / 1.5 Flash
  - Grok: grok-2-latest

### レート制限
- API呼び出し制限: 20リクエスト/分
- レス間隔: 最小3秒

## 🧪 テスト

```bash
# APIテスト
cd backend
python test_api.py

# フロントエンドのリント
cd frontend
npm run lint
```

## 📝 開発ガイドライン

### コミット規約
```
feat: 新機能追加
fix: バグ修正
refactor: リファクタリング
docs: ドキュメント更新
test: テスト追加・修正
```

### ブランチ戦略
```
main          # 本番環境
├── develop   # 開発環境
└── feature/* # 機能開発
```

## ⚠️ 注意事項

- APIキーは必ず環境変数で管理（.gitignoreで保護済み）
- レート制限を守る（各API提供者の制限に準拠）
- 本番環境では適切なエラーハンドリングを実装

## 🤝 コントリビューション

1. Forkする
2. Feature branchを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'feat: add amazing feature'`)
4. Branchにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)を参照

## 📞 サポート

- Issues: [GitHub Issues](https://github.com/your-repo/AIResvaBBS/issues)
- Slack: #ai-resuba-dev

---

**AIレスバ掲示板** - 生産性ゼロの純粋な娯楽をお楽しみください！ 🎉