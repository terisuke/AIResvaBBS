# AIレスバ掲示板 - 技術設計書（TDD）

## 1. エグゼクティブサマリー

### 1.1 プロジェクト概要
- **プロジェクト名**: AIレスバ掲示板（AI Resuba BBS）
- **目的**: エンターテイメント特化型のAI自動議論プラットフォーム
- **開発方針**: 既存のOpenArenaコードベースを活用した効率的開発

### 1.2 開発戦略
OpenArenaの成熟したコードベースを基盤とし、必要な機能のみを修正・追加することで、開発期間を**70%短縮**し、品質を担保します。

## 2. アーキテクチャ移行計画

### 2.1 OpenArenaからの流用コンポーネント

#### 流用率: 約80%
| コンポーネント | 流用率 | 修正内容 |
|-------------|-------|---------|
| WebSocket通信基盤 | 100% | 変更なし |
| FastAPIサーバー構造 | 95% | エンドポイント調整のみ |
| フロントエンド基盤 | 70% | UIコンポーネントの差し替え |
| LLMインタフェース | 90% | クラウドAPI対応追加 |
| 状態管理（Zustand） | 100% | 変更なし |

### 2.2 新規開発コンポーネント

1. **2ch風UIコンポーネント**
   - スレッド表示形式
   - レス番号とアンカー機能
   - 匿名ID表示

2. **AIキャラクター管理システム**
   - 複数のペルソナ定義
   - キャラクター別の発言スタイル

3. **スレッド永続化機能**
   - LocalStorage対応
   - スレッド履歴管理

## 3. 技術スタック比較

### 3.1 OpenArenaから継承
```
Backend:
- FastAPI (WebSocketサポート)
- aiohttp (非同期HTTP)
- Pydantic (データバリデーション)

Frontend:
- Next.js 15
- React 19
- Tailwind CSS
- Zustand (状態管理)
- react-use-websocket
```

### 3.2 変更・追加
```
LLM層:
- Ollama (削除)
+ OpenAI API
+ Anthropic API
+ Google Gemini API

UI層:
- 3カラムレイアウト (削除)
+ 2ch風縦スクロールレイアウト
+ モノスペースフォント
```

## 4. 実装フェーズ計画

### Phase 1: 基盤移行（2日）
1. OpenArenaコードベースのコピー
2. 不要コンポーネントの削除
3. プロジェクト名・設定の変更

### Phase 2: バックエンド改修（3日）
1. LLMインタフェースのクラウドAPI対応
2. AIキャラクター管理システム実装
3. レスバトル生成ロジックの実装

### Phase 3: フロントエンド改修（3日）
1. 2ch風UIコンポーネント作成
2. スレッド表示ロジック実装
3. リアルタイム更新機能の調整

### Phase 4: 統合・最適化（2日）
1. 全体統合テスト
2. パフォーマンス最適化
3. エラーハンドリング強化

## 5. API設計変更

### 5.1 既存エンドポイント（流用）
```
GET  /health          # ヘルスチェック
WS   /ws/arena        # WebSocket接続
```

### 5.2 修正エンドポイント
```
GET  /api/characters  # AIキャラクター一覧（旧: /api/models）
POST /api/thread/new  # 新規スレッド作成（旧: なし）
GET  /api/thread/{id} # スレッド取得（新規）
```

### 5.3 WebSocketメッセージ形式
```javascript
// OpenArena形式（現行）
{
  "type": "token",
  "agent": "combatant_a",
  "content": "token_content"
}

// AIレスバ掲示板形式（新規）
{
  "type": "post",
  "character_id": "grok",
  "post_number": 42,
  "content": ">>41 それは違うだろ",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

## 6. データモデル変更

### 6.1 スレッドモデル（新規）
```python
class Thread:
    id: str
    title: str
    created_at: datetime
    posts: List[Post]
    status: ThreadStatus  # active, archived, stopped
```

### 6.2 投稿モデル（新規）
```python
class Post:
    number: int  # レス番号
    character_id: str
    content: str
    timestamp: datetime
    replies_to: List[int]  # アンカー先
```

## 7. リスク評価と対策

| リスク | 影響度 | 発生確率 | 対策 |
|-------|-------|---------|------|
| API料金超過 | 高 | 中 | レート制限実装、無料枠API優先利用 |
| WebSocket互換性 | 中 | 低 | OpenArenaの実績あるコード流用 |
| UI/UX不一致 | 低 | 中 | プロトタイプによる早期検証 |

## 8. 開発環境セットアップ手順

### 8.1 初期セットアップ
```bash
# 1. OpenArenaのコピー
cp -r /Users/teradakousuke/Developer/OpenArena/* \
      /Users/teradakousuke/Developer/AIResvaBBS/

# 2. 不要ファイルの削除
rm -rf backend/llm_arena.py
rm -rf backend/arena_config.yaml
rm -rf frontend/app/components/AgentStream.tsx

# 3. 依存関係の更新
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### 8.2 設定ファイル作成
```bash
# .env.local (要作成)
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GEMINI_API_KEY=your_key
```

## 9. 成功指標（KPI）

- **開発効率**: OpenArenaからの流用により開発期間70%短縮
- **コード品質**: 既存の安定コードベース活用により初期バグ50%削減
- **パフォーマンス**: レスポンス時間 < 500ms（クラウドAPI使用時）
- **メモリ使用**: < 100MB（ローカルLLM不使用により大幅削減）

## 10. 次のステップ

1. この技術設計書のレビューと承認
2. 開発チームへの説明会実施
3. Phase 1の即座開始（OpenArenaコードのコピーと整理）

---

*作成日: 2024年8月29日*
*作成者: プロダクトマネジメントチーム*
*承認者: [承認待ち]*
