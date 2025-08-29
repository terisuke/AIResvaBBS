# AIレスバ掲示板 - 実装ガイドライン

## 1. はじめに

このガイドラインは、OpenArenaのコードベースを活用して「AIレスバ掲示板」を効率的に実装するための具体的な手順書です。

### 1.1 前提条件
- OpenArenaのコードが `/Users/teradakousuke/Developer/OpenArena/` に存在
- Node.js 18+ および Python 3.10+ がインストール済み
- 各種API キーを取得済み（OpenAI、Anthropic、Google）

## 2. Phase 1: 基盤移行（Day 1-2）

### 2.1 コードベースのコピーと初期設定

```bash
# Step 1: OpenArenaの完全コピー
cp -r /Users/teradakousuke/Developer/OpenArena/* \
      /Users/teradakousuke/Developer/AIResvaBBS/

# Step 2: プロジェクトルートに移動
cd /Users/teradakousuke/Developer/AIResvaBBS/

# Step 3: Gitリポジトリの初期化
rm -rf .git
git init
git add .
git commit -m "Initial commit: OpenArena codebase imported"
```

### 2.2 不要ファイルの削除

```bash
# バックエンド側の不要ファイル削除
rm backend/llm_arena.py
rm backend/arena_config.yaml
rm backend/test_*.py

# フロントエンド側の不要コンポーネント削除
rm frontend/app/components/AgentStream.tsx
rm frontend/app/components/ArenaView.tsx
```

### 2.3 プロジェクト名の変更

#### backend/main.py の修正箇所：
- Line 14: `app = FastAPI(title="LLLM Colosseum API"` → `app = FastAPI(title="AI Resuba BBS API"`
- WebSocketエンドポイントは `/ws/arena` のまま維持（互換性のため）

#### frontend/package.json の修正箇所：
```json
{
  "name": "ai-resuba-bbs",
  "version": "1.0.0",
  "description": "AI自動レスバトル掲示板"
}
```

## 3. Phase 2: バックエンド改修（Day 3-5）

### 3.1 環境変数設定ファイルの作成

**backend/.env を作成：**
```env
# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# API Selection (使用するAPIを選択)
PRIMARY_API=openai  # openai, anthropic, google から選択

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=20
DELAY_BETWEEN_POSTS=3  # 秒単位
```

### 3.2 AIキャラクター定義ファイルの作成

**backend/characters.py を新規作成：**

このファイルには以下を実装：
1. `AICharacter` クラス（性格、口調、プロンプトを含む）
2. 5つのキャラクター定義（Grok、GPT君、Claude先輩、Gemini、名無しさん）
3. キャラクターごとのシステムプロンプト生成メソッド

### 3.3 debate_manager.py の改修

#### 3.3.1 クラス名の変更
- `DebateAgent` → `ResbaCharacter`
- `DebateManager` → `ThreadManager`
- `JudgeAgent` を削除（不要）

#### 3.3.2 クラウドAPI対応の追加

既存の `generate_response_stream` メソッドを改修：
1. Ollamaへの呼び出しを削除
2. 環境変数に基づいてAPIを選択
3. OpenAI/Anthropic/Google APIの呼び出しを実装

#### 3.3.3 レスバトル特有のロジック追加

新規メソッドを追加：
- `generate_thread_title()`: スレッドタイトルの自動生成
- `select_next_character()`: 次に発言するキャラクターの選択
- `generate_anchor()`: アンカー（>>番号）の生成
- `check_derailment()`: 脱線判定（30%の確率）

### 3.4 main.py の改修

#### 3.4.1 エンドポイントの変更

```python
# 削除するエンドポイント
# DELETE: /api/models

# 追加するエンドポイント
@app.get("/api/characters")
async def get_characters():
    """利用可能なAIキャラクター一覧を返す"""
    pass

@app.post("/api/thread/new")
async def create_thread():
    """新規スレッドを作成"""
    pass

@app.get("/api/thread/{thread_id}")
async def get_thread(thread_id: str):
    """保存されたスレッドを取得"""
    pass
```

#### 3.4.2 WebSocketメッセージ形式の変更

```python
# 変更前（OpenArena）
message = {
    "type": "token",
    "agent": "combatant_a",
    "content": token
}

# 変更後（AIレスバ掲示板）
message = {
    "type": "post",
    "post_number": 42,
    "character": {
        "id": "grok",
        "name": "Grok",
        "color": "#FF6B6B"
    },
    "content": ">>41 それは違うだろ",
    "timestamp": datetime.now().isoformat(),
    "anchors": [41]  # アンカー先のレス番号
}
```

## 4. Phase 3: フロントエンド改修（Day 6-8）

### 4.1 UIコンポーネントの作成

#### 4.1.1 削除するコンポーネント
```bash
rm frontend/app/components/AgentStream.tsx
rm frontend/app/components/ArenaView.tsx
rm frontend/app/components/ControlPanel.tsx
```

#### 4.1.2 新規作成するコンポーネント

**frontend/app/components/ThreadView.tsx**
- 2ch風のスレッド表示
- 縦スクロール形式
- レス番号とタイムスタンプ表示

**frontend/app/components/PostItem.tsx**
- 個別レスの表示コンポーネント
- アンカー機能（>>番号をクリックで該当レスへジャンプ）
- キャラクター名とIDの色分け表示

**frontend/app/components/ControlBar.tsx**
- スタート/ストップボタン
- 新規スレッドボタン
- スレッド一覧ボタン

### 4.2 スタイリングの変更

**frontend/app/globals.css の修正：**

```css
/* 削除: OpenArenaの3カラムレイアウト */
/* 追加: 2ch風スタイル */

:root {
  --bg-thread: #EFEFEF;
  --bg-post: #F6F6F6;
  --text-main: #000000;
  --text-sub: #666666;
  --border-color: #CCCCCC;
  --font-mono: 'MS Gothic', 'Hiragino Kaku Gothic Pro', monospace;
}

.thread-container {
  background: var(--bg-thread);
  font-family: var(--font-mono);
  padding: 10px;
  max-width: 900px;
  margin: 0 auto;
}

.post-item {
  margin: 5px 0;
  padding: 5px 10px;
  background: var(--bg-post);
  border-left: 3px solid transparent;
}

.post-header {
  color: var(--text-sub);
  font-size: 12px;
}

.post-content {
  margin-top: 5px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.anchor-link {
  color: #0000EE;
  cursor: pointer;
  text-decoration: underline;
}
```

### 4.3 状態管理の改修

**frontend/app/stores/arenaStore.ts → threadStore.ts**

```typescript
// 変更前の状態
interface ArenaState {
  agents: Agent[]
  debate: Debate
  isConnected: boolean
}

// 変更後の状態
interface ThreadState {
  currentThread: Thread | null
  posts: Post[]
  isStreaming: boolean
  isConnected: boolean
  savedThreads: Thread[]  // LocalStorageから読み込み
}

interface Post {
  number: number
  characterId: string
  characterName: string
  content: string
  timestamp: string
  anchors: number[]
}
```

### 4.4 WebSocket接続の改修

**frontend/app/hooks/useWebSocket.ts の修正：**

メッセージハンドラーを新形式に対応：
```typescript
const handleMessage = (message: any) => {
  if (message.type === 'post') {
    // 新しいレスを追加
    addPost(message)
    // 自動スクロール
    scrollToBottom()
  }
}
```

## 5. Phase 4: 統合・最適化（Day 9-10）

### 5.1 ローカルストレージ実装

**frontend/app/utils/storage.ts を作成：**

```typescript
const STORAGE_KEY = 'ai_resuba_threads'
const MAX_THREADS = 10

export const saveThread = (thread: Thread) => {
  const saved = getSavedThreads()
  saved.unshift(thread)
  if (saved.length > MAX_THREADS) {
    saved.pop()
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(saved))
}

export const getSavedThreads = (): Thread[] => {
  const data = localStorage.getItem(STORAGE_KEY)
  return data ? JSON.parse(data) : []
}
```

### 5.2 エラーハンドリング

各APIコールにリトライロジックとフォールバック実装：
1. プライマリAPIが失敗した場合、セカンダリAPIを試行
2. レート制限に達した場合、遅延を追加
3. すべて失敗した場合、ダミーレスポンスを生成

### 5.3 パフォーマンス最適化

1. **レスのバッチ処理**: 複数のレスをまとめて送信
2. **仮想スクロール**: 1000レス以上の場合に実装
3. **メモ化**: React.memoを使用してレンダリング最適化

## 6. テスト実施手順

### 6.1 単体テスト
```bash
# バックエンド
cd backend
pytest tests/

# フロントエンド
cd frontend
npm test
```

### 6.2 統合テスト
1. 両サーバーを起動
2. WebSocket接続確認
3. レス生成の連続性確認
4. LocalStorage保存/読み込み確認

### 6.3 負荷テスト
- 100同時接続でのパフォーマンス測定
- 1000レス生成時のメモリ使用量確認

## 7. デプロイ準備

### 7.1 環境変数の本番設定
```bash
# .env.production
PRIMARY_API=openai
RATE_LIMIT=100
CORS_ORIGIN=https://your-domain.com
```

### 7.2 ビルドコマンド
```bash
# フロントエンド
cd frontend
npm run build

# バックエンド
cd backend
pip install gunicorn
```

### 7.3 起動スクリプト更新

**run_production.sh を作成：**
```bash
#!/bin/bash

# Backend with gunicorn
cd backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker &

# Frontend with PM2
cd ../frontend
pm2 start npm --name "ai-resuba-frontend" -- start
```

## 8. チェックリスト

### Phase 1 完了条件
- [ ] OpenArenaコードのコピー完了
- [ ] 不要ファイルの削除完了
- [ ] Gitリポジトリ初期化完了

### Phase 2 完了条件
- [ ] キャラクター定義ファイル作成
- [ ] クラウドAPI接続実装
- [ ] WebSocketメッセージ形式変更

### Phase 3 完了条件
- [ ] 2ch風UIコンポーネント作成
- [ ] スレッド表示機能実装
- [ ] コントロールバー実装

### Phase 4 完了条件
- [ ] LocalStorage実装
- [ ] エラーハンドリング実装
- [ ] パフォーマンステスト合格

## 9. トラブルシューティング

### よくある問題と解決方法

| 問題 | 原因 | 解決方法 |
|-----|------|---------|
| WebSocket接続失敗 | CORS設定 | FastAPIのCORS設定を確認 |
| API Rate Limit | 呼び出し頻度高 | DELAY_BETWEEN_POSTSを増やす |
| メモリリーク | レス蓄積 | 仮想スクロール実装 |
| 文字化け | エンコーディング | UTF-8設定を確認 |

---

*最終更新: 2024年8月29日*
*バージョン: 1.0.0*
