# 🚀 開発準備完了通知

## ✅ セットアップ済み項目

**プロダクトマネジメントチームより、以下の初期セットアップを完了しました：**

1. ✅ **OpenArenaコードベースの完全コピー完了**
   - backend/ ディレクトリ：全ファイルコピー済み
   - frontend/ ディレクトリ：全ファイルコピー済み
   - run_dev.sh：起動スクリプトコピー済み

2. ✅ **プロジェクトドキュメント配置完了**
   - PRD.md（プロダクト要求仕様書）
   - TDD.md（技術設計書）
   - IMPLEMENTATION_GUIDE.md（実装ガイドライン）
   - TEST_PLAN.md（テスト計画書）

## 🎯 開発チームの次のアクション

### STEP 1: 不要ファイルの削除（5分）

```bash
cd /Users/teradakousuke/Developer/AIResvaBBS

# バックエンドの不要ファイル削除
rm backend/llm_arena.py
rm backend/arena_config.yaml
rm -rf backend/assets/

# フロントエンドの不要コンポーネント削除
rm frontend/app/components/AgentStream.tsx
rm frontend/app/components/ArenaView.tsx

echo "クリーンアップ完了！"
```

### STEP 2: 環境変数の設定（2分）

```bash
# バックエンド環境変数を作成
cat > backend/.env << 'EOF'
# API Keys（各自のキーに置き換えてください）
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxx

# 動作設定
PRIMARY_API=openai
DELAY_BETWEEN_POSTS=3
MAX_REQUESTS_PER_MINUTE=20
EOF

echo "環境変数ファイル作成完了！"
```

### STEP 3: 依存関係のインストール（10分）

```bash
# Python仮想環境のセットアップ（既存のvenvは削除）
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# requirements.txtの更新
cat > requirements.txt << 'EOF'
fastapi==0.115.4
uvicorn[standard]==0.32.0
websockets==13.1
aiohttp==3.10.10
pydantic==2.9.2
python-multipart==0.0.9
openai==1.54.3
anthropic==0.39.0
google-generativeai==0.8.3
python-dotenv==1.0.1
EOF

pip install -r requirements.txt

# フロントエンドの依存関係
cd ../frontend
npm install

echo "依存関係インストール完了！"
```

### STEP 4: 動作確認（2分）

```bash
# プロジェクトルートに戻る
cd /Users/teradakousuke/Developer/AIResvaBBS

# 開発サーバー起動
./run_dev.sh
```

ブラウザで http://localhost:3000 を開いて、OpenArenaベースのアプリが起動することを確認してください。

## 📝 各チームの作業開始ポイント

### バックエンドチーム
**ファイル: `backend/debate_manager.py`**
- Line 33-45: クラス名を `DebateAgent` → `ResbaCharacter` に変更
- Line 87-120: Ollama呼び出しをクラウドAPI呼び出しに変更
- 新規作成: `backend/characters.py`（AIキャラクター定義）

### フロントエンドチーム
**新規作成が必要なコンポーネント:**
1. `frontend/app/components/ThreadView.tsx` - 2ch風スレッド表示
2. `frontend/app/components/PostItem.tsx` - 個別レス表示
3. `frontend/app/components/ControlBar.tsx` - 操作ボタン

**修正が必要なファイル:**
- `frontend/app/page.tsx` - メインページのレイアウト変更
- `frontend/app/globals.css` - 2ch風スタイリング追加

### 作業の優先順位

1. **最優先（今すぐ）**
   - 上記のSTEP 1-4を実行
   - 動作確認

2. **高優先（Day 1-2）**
   - バックエンド：characters.py作成
   - フロントエンド：ThreadView.tsx作成

3. **中優先（Day 3-5）**
   - API統合テスト
   - WebSocketメッセージ形式変更

## ⚠️ 注意事項

### 触ってはいけないファイル
- ✅ `backend/main.py` のWebSocket基本構造
- ✅ `frontend/app/hooks/useWebSocket.ts` の接続ロジック
- ✅ `run_dev.sh` の起動スクリプト

これらは**OpenArenaで実績のある安定したコード**なので、必要最小限の修正に留めてください。

## 💬 サポート

問題が発生した場合：
1. まず `IMPLEMENTATION_GUIDE.md` のトラブルシューティングを確認
2. Slack #ai-resuba-dev で質問
3. 緊急時はPdMに直接連絡

---

**準備は整いました！さあ、開発を始めましょう！** 🚀

*更新日時: 2024年8月29日*
*準備完了者: プロダクトマネジメントチーム*
