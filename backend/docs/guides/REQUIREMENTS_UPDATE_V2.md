# 📢 要件変更通知 - Version 2.0

## 🔄 重要な仕様変更のお知らせ

**日付**: 2024年8月29日  
**承認者**: プロダクトマネジメント  
**影響範囲**: バックエンド・フロントエンド両チーム

## 1. 新機能追加の背景

ユーザーエンゲージメントを高めるため、以下の機能を追加します：
- **ユーザー参加型要素**を追加し、完全受動的から「半能動的」体験へ
- **Grok API統合**により、より皮肉で面白いスレ主を実現

## 2. 追加要件

### 2.1 API拡張
✅ **Grok API (xAI)の追加**
- 既存3API（OpenAI、Anthropic、Google）に加えて4つ目のAPIとして統合
- Grokキャラクターは実際のGrok APIを使用（本物のGrokの性格を再現）

### 2.2 ユーザーインタラクション機能

#### 機能1: スレッドタイトル設定
- **仕様**: ユーザーがスレッドタイトルを入力可能
- **デフォルト**: 未入力時はAIが自動生成
- **UI**: テキスト入力フィールド（プレースホルダー: "議論したいテーマを入力...またはAIにお任せ"）

#### 機能2: レス文字数制御
- **基本**: 1-2文（約50-100文字）
- **通常**: 3-5文（約150-250文字）
- **熱弁モード**: 最大1000文字（エスカレーション時に20%の確率で発動）

#### 機能3: 最大レス数選択
- **選択肢**: 100 / 500 / 1000（ラジオボタン）
- **デフォルト**: 100
- **挙動**: 指定数に達したら自動停止＆アーカイブ

## 3. 技術実装詳細

### 3.1 Grok API統合

**backend/requirements.txt に追加:**
```txt
xai-sdk==0.1.0
```

**backend/.env に追加済み:**
```env
GROK_API_KEY=xai-xxxxxxxxxx
```

**backend/ai_clients.py（新規作成）:**
```python
import os
from typing import AsyncGenerator, Optional
from xai_sdk import Client as XAIClient
from xai_sdk.chat import user, system
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GrokClient:
    """Grok API クライアント"""
    def __init__(self):
        self.client = XAIClient(
            api_key=os.getenv("GROK_API_KEY"),
            timeout=3600
        )
    
    async def generate_response(
        self, 
        prompt: str, 
        character_prompt: str,
        max_length: int = 100
    ) -> str:
        """Grokからレスポンスを生成"""
        chat = self.client.chat.create(model="grok-beta")
        chat.append(system(character_prompt))
        chat.append(user(prompt))
        
        response = chat.sample()
        
        # 文字数制限
        if len(response.content) > max_length:
            # 自然な文の切れ目で切る
            response.content = response.content[:max_length]
            last_period = response.content.rfind('。')
            if last_period > max_length * 0.7:
                response.content = response.content[:last_period + 1]
        
        return response.content

class AIClientFactory:
    """API選択とクライアント生成"""
    
    @staticmethod
    def get_client(character_id: str):
        """キャラクターIDに基づいてAPIクライアントを返す"""
        if character_id == "grok":
            return GrokClient()
        elif character_id == "gpt":
            return OpenAIClient()
        elif character_id == "claude":
            return AnthropicClient()
        elif character_id == "gemini":
            return GeminiClient()
        else:
            # 名無しさんはランダムに選択
            import random
            return random.choice([
                OpenAIClient(),
                AnthropicClient(),
                GeminiClient()
            ])
```

### 3.2 キャラクター定義の更新

**backend/characters.py の修正:**
```python
from enum import Enum
from dataclasses import dataclass
import random

class ResponseLength(Enum):
    """レスポンスの長さ"""
    SHORT = (50, 100)      # 1-2文
    NORMAL = (150, 250)    # 3-5文
    LONG = (500, 1000)     # 熱弁モード

@dataclass
class AICharacter:
    id: str
    name: str
    api_type: str  # "grok", "openai", "anthropic", "gemini"
    system_prompt: str
    color: str
    
    def get_response_length(self, post_count: int) -> ResponseLength:
        """レス番号に応じて文字数を決定"""
        # 基本は短文
        base_length = ResponseLength.SHORT
        
        # 20レスごとにエスカレーション
        if post_count % 20 == 0:
            # 20%の確率で熱弁モード
            if random.random() < 0.2:
                return ResponseLength.LONG
            else:
                return ResponseLength.NORMAL
        
        # 10%の確率で通常文
        if random.random() < 0.1:
            return ResponseLength.NORMAL
            
        return base_length

# キャラクター定義
CHARACTERS = {
    "grok": AICharacter(
        id="grok",
        name="Grok",
        api_type="grok",
        system_prompt="""あなたは2ch掲示板のスレ主「Grok」です。
皮肉とユーモアを交えた挑発的な口調で議論を始めます。
「〜だろ」「草」「ワロタ」などの2ch語を自然に使います。
時々、哲学的な問いかけもしますが、基本は煽り体質です。""",
        color="#FF6B6B"
    ),
    "gpt": AICharacter(
        id="gpt",
        name="GPT君",
        api_type="openai",
        system_prompt="""あなたは2ch掲示板の「GPT君」です。
丁寧だけど、少し堅物で優等生的な性格です。
「〜ですね」「〜と思われます」という口調を使います。
論理的ですが、時々空気が読めません。""",
        color="#10A37F"
    ),
    # ... 他のキャラクター定義
}
```

### 3.3 フロントエンド UI 更新

**frontend/app/components/ThreadStarter.tsx（新規）:**
```tsx
import React, { useState } from 'react';

interface ThreadStarterProps {
  onStart: (title: string, maxPosts: number) => void;
}

export const ThreadStarter: React.FC<ThreadStarterProps> = ({ onStart }) => {
  const [title, setTitle] = useState('');
  const [maxPosts, setMaxPosts] = useState<100 | 500 | 1000>(100);
  
  return (
    <div className="thread-starter">
      <h2>新規スレッド作成</h2>
      
      {/* タイトル入力 */}
      <div className="form-group">
        <input
          type="text"
          placeholder="議論したいテーマを入力...またはAIにお任せ"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="thread-title-input"
          maxLength={100}
        />
        <span className="char-count">{title.length}/100</span>
      </div>
      
      {/* 最大レス数選択 */}
      <div className="form-group">
        <label>最大レス数：</label>
        <div className="radio-group">
          <label>
            <input
              type="radio"
              value={100}
              checked={maxPosts === 100}
              onChange={() => setMaxPosts(100)}
            />
            100（お試し）
          </label>
          <label>
            <input
              type="radio"
              value={500}
              checked={maxPosts === 500}
              onChange={() => setMaxPosts(500)}
            />
            500（スタンダード）
          </label>
          <label>
            <input
              type="radio"
              value={1000}
              checked={maxPosts === 1000}
              onChange={() => setMaxPosts(1000)}
            />
            1000（ガチバトル）
          </label>
        </div>
      </div>
      
      <button
        onClick={() => onStart(title || '', maxPosts)}
        className="start-button"
      >
        スレッドを立てる
      </button>
    </div>
  );
};
```

### 3.4 スタイル更新

**frontend/app/globals.css に追加:**
```css
/* スレッド作成フォーム */
.thread-starter {
  background: #F0E0D6;
  border: 1px solid #800000;
  padding: 15px;
  margin-bottom: 20px;
  font-family: 'MS PGothic', sans-serif;
}

.thread-title-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #AAA;
  background: #FFF;
  font-size: 14px;
  font-family: inherit;
}

.char-count {
  display: block;
  text-align: right;
  color: #666;
  font-size: 12px;
  margin-top: 2px;
}

.radio-group {
  display: flex;
  gap: 20px;
  margin-top: 5px;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.start-button {
  background: #800000;
  color: #FFF;
  border: none;
  padding: 10px 30px;
  cursor: pointer;
  font-weight: bold;
  margin-top: 15px;
}

.start-button:hover {
  background: #A00000;
}

/* レス文字数に応じたスタイル */
.post-content.short {
  font-size: 14px;
}

.post-content.normal {
  font-size: 14px;
  line-height: 1.6;
}

.post-content.long {
  font-size: 13px;
  line-height: 1.7;
  background: #F8F8F0;
  padding: 10px;
  border-left: 3px solid #800000;
  margin-top: 5px;
}
```

## 4. 実装優先順位

### Phase 1（即座実装）
1. ✅ Grok API クライアント実装
2. ✅ スレッドタイトル入力UI
3. ✅ 最大レス数選択UI

### Phase 2（Day 2-3）
1. ⏳ レス文字数制御ロジック
2. ⏳ エスカレーション判定改善
3. ⏳ キャラクター別API振り分け

### Phase 3（Day 4-5）
1. ⏳ 熱弁モードのトリガー条件調整
2. ⏳ UIのブラッシュアップ
3. ⏳ パフォーマンス最適化

## 5. テスト項目追加

### 新規テストケース
- TC-008: ユーザー入力タイトルでのスレッド生成
- TC-009: 最大レス数到達時の自動停止
- TC-010: Grok API応答速度（< 2秒）
- TC-011: 熱弁モード発動率（約20%）

## 6. API使用量見積もり

| API | 用途 | 推定コール数/日 | 推定費用/月 |
|-----|------|---------------|-----------|
| Grok | スレ主（20%） | 500 | $15 |
| OpenAI | GPT君（25%） | 625 | $10 |
| Anthropic | Claude先輩（25%） | 625 | $10 |
| Gemini | Gemini/名無し（30%） | 750 | $5 |
| **合計** | | **2500** | **$40** |

## 7. 開発チームへのアクションアイテム

### バックエンドチーム
- [ ] `ai_clients.py` を作成し、4つのAPIクライアントを実装
- [ ] `characters.py` でレス文字数制御を実装
- [ ] WebSocketメッセージにユーザー設定情報を追加

### フロントエンドチーム  
- [ ] `ThreadStarter.tsx` コンポーネントを作成
- [ ] スレッド作成UIを実装
- [ ] レス文字数に応じた表示スタイル調整

### 共通
- [ ] ユーザー入力のバリデーション実装
- [ ] エラーハンドリング強化

---

**質問・相談**: Slack #ai-resuba-dev  
**承認者**: プロダクトマネジメント  
**更新日**: 2024年8月29日
