#!/bin/bash

# AIレスバ掲示板 - ワンクリック初期化スクリプト
# このスクリプトを実行するだけで開発環境が整います

echo "🚀 AIレスバ掲示板 開発環境セットアップを開始します..."

# プロジェクトディレクトリに移動
cd /Users/teradakousuke/Developer/AIResvaBBS

# Git初期化（OpenArenaの履歴を削除）
echo "📝 Gitリポジトリを初期化中..."
rm -rf .git
git init
git add .
git commit -m "Initial commit: OpenArena codebase imported for AI Resuba BBS"

# 不要ファイルの削除
echo "🧹 不要ファイルをクリーンアップ中..."
rm -f backend/llm_arena.py
rm -f backend/arena_config.yaml
rm -rf backend/assets/
rm -f frontend/app/components/AgentStream.tsx
rm -f frontend/app/components/ArenaView.tsx

# 環境変数ファイルのテンプレート作成
echo "⚙️ 環境変数テンプレートを作成中..."
cat > backend/.env.example << 'EOF'
# API Keys（各自のキーに置き換えてください）
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxx

# 動作設定
PRIMARY_API=openai
DELAY_BETWEEN_POSTS=3
MAX_REQUESTS_PER_MINUTE=20
EOF

# .gitignore更新
echo "📂 .gitignoreを設定中..."
cat > .gitignore << 'EOF'
# Python
backend/venv/
backend/__pycache__/
backend/*.pyc
backend/.env
backend/*.log

# Node
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Project specific
*.db
*.sqlite
logs/
EOF

# 開発ブランチの作成
echo "🌳 開発ブランチを作成中..."
git add .
git commit -m "chore: cleanup unnecessary files and add configurations"
git branch develop
git checkout develop
git branch feature/phase2-backend
git branch feature/phase3-frontend
git branch feature/phase4-integration

echo "
✅ セットアップ完了！

次のステップ:
1. backend/.env.example を backend/.env にコピーしてAPIキーを設定
   cp backend/.env.example backend/.env
   
2. 依存関係をインストール
   cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
   cd ../frontend && npm install
   
3. 開発サーバーを起動
   ./run_dev.sh

現在のブランチ: develop
作業開始時は適切なfeatureブランチにチェックアウトしてください:
- バックエンド開発: git checkout feature/phase2-backend
- フロントエンド開発: git checkout feature/phase3-frontend

Happy Coding! 🎉
"
