# 📌 設計明確化通知 - API使用ルール

## ⚠️ 重要な仕様確認

**日付**: 2024年8月29日  
**対象**: バックエンドチーム  
**優先度**: 最高

## 1. API使用ルールの明確化

### ❌ 誤った理解
`PRIMARY_API`を設定すると、すべてのキャラクターがそのAPIを使う

### ✅ 正しい仕様
**各キャラクターは固定のAPIを使用し、複数のAIが同時に参加する**

## 2. キャラクター別API割り当て

| キャラクター | 使用API | 理由 |
|------------|---------|------|
| **Grok（スレ主）** | Grok API | 本物のGrokの皮肉な性格を再現 |
| **GPT君** | OpenAI API | ChatGPTの丁寧で優等生的な性格 |
| **Claude先輩** | Anthropic API | Claudeの論理的で慎重な性格 |
| **Gemini** | Google Gemini API | Geminiの創造的な性格 |
| **名無しさん** | ランダム選択 | 毎回異なる性格を演出 |

## 3. PRIMARY_APIの正しい役割

`PRIMARY_API`は以下の用途で使用：
1. **名無しさん**のデフォルトAPI
2. **フォールバック**（特定APIが失敗した場合の代替）
3. **テスト環境**での統一API使用

## 4. 実装修正内容

### backend/ai_clients.py の正しい実装

```python
import os
import random
from typing import Optional
from xai_sdk import Client as XAIClient
from xai_sdk.chat import user, system
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIClientFactory:
    """キャラクターに応じて固定のAPIクライアントを返す"""
    
    # キャラクターとAPIの固定マッピング
    CHARACTER_API_MAPPING = {
        "grok": "grok",
        "gpt": "openai", 
        "claude": "anthropic",
        "gemini": "google",
        "nanashi": "random"  # 名無しさんはランダム
    }
    
    @staticmethod
    def get_client(character_id: str):
        """
        キャラクターIDに基づいて固定のAPIクライアントを返す
        PRIMARY_APIはフォールバック用
        """
        api_type = AIClientFactory.CHARACTER_API_MAPPING.get(
            character_id, 
            os.getenv("PRIMARY_API", "openai")  # 未定義キャラはPRIMARY_API使用
        )
        
        # 名無しさんの場合はランダム選択
        if api_type == "random":
            api_type = random.choice(["openai", "anthropic", "google"])
        
        # API別クライアント生成
        if api_type == "grok":
            return GrokClient()
        elif api_type == "openai":
            return OpenAIClient()
        elif api_type == "anthropic":
            return AnthropicClient()
        elif api_type == "google":
            return GeminiClient()
        else:
            # フォールバック
            return OpenAIClient()

class GrokClient:
    """Grok API専用クライアント"""
    def __init__(self):
        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            raise ValueError("GROK_API_KEY is not set")
        self.client = XAIClient(api_key=api_key, timeout=3600)
    
    async def generate_response(self, prompt: str, system_prompt: str, max_length: int = 100) -> str:
        chat = self.client.chat.create(model="grok-beta")
        chat.append(system(system_prompt))
        chat.append(user(prompt))
        response = chat.sample()
        return self._truncate_response(response.content, max_length)
    
    def _truncate_response(self, content: str, max_length: int) -> str:
        if len(content) <= max_length:
            return content
        # 自然な文の切れ目で切る
        truncated = content[:max_length]
        last_period = max(
            truncated.rfind('。'),
            truncated.rfind('！'),
            truncated.rfind('？'),
            truncated.rfind('.')
        )
        if last_period > max_length * 0.7:
            return truncated[:last_period + 1]
        return truncated + "..."

class OpenAIClient:
    """OpenAI API専用クライアント"""
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_response(self, prompt: str, system_prompt: str, max_length: int = 100) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",  # コスト効率の良いモデル
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_length // 2,  # 日本語は約2文字/トークン
            temperature=0.8
        )
        return response.choices[0].message.content

class AnthropicClient:
    """Anthropic API専用クライアント"""
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def generate_response(self, prompt: str, system_prompt: str, max_length: int = 100) -> str:
        response = await self.client.messages.create(
            model="claude-3-haiku-20240307",  # 高速・低コストモデル
            max_tokens=max_length // 2,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response.content[0].text

class GeminiClient:
    """Google Gemini API専用クライアント"""
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # 高速モデル
    
    async def generate_response(self, prompt: str, system_prompt: str, max_length: int = 100) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = await self.model.generate_content_async(
            full_prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_length // 2,
                temperature=0.8
            )
        )
        return response.text
```

### backend/thread_manager.py の実装

```python
import asyncio
import random
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass

from ai_clients import AIClientFactory
from characters import CHARACTERS, ResponseLength

@dataclass
class Post:
    """レス（投稿）のデータ構造"""
    number: int
    character_id: str
    character_name: str
    content: str
    timestamp: datetime
    anchors: List[int]  # アンカー先のレス番号
    response_length: ResponseLength

class ThreadManager:
    """スレッド全体を管理"""
    
    def __init__(self, title: str = "", max_posts: int = 100):
        self.title = title
        self.max_posts = max_posts
        self.posts: List[Post] = []
        self.is_running = False
        
        # 参加キャラクターのリスト（Grokは必ずスレ主）
        self.participating_characters = ["grok", "gpt", "claude", "gemini", "nanashi"]
        
    async def start_thread(self):
        """スレッドを開始"""
        self.is_running = True
        
        # タイトルが未設定ならAIが生成
        if not self.title:
            self.title = await self._generate_thread_title()
        
        # Grokが最初の投稿
        await self._create_post("grok", is_first=True)
        
        # レスバトル開始
        while self.is_running and len(self.posts) < self.max_posts:
            # 次の発言者を選択（Grok以外からランダム）
            next_character = self._select_next_character()
            await self._create_post(next_character)
            
            # レス間隔
            await asyncio.sleep(random.uniform(2, 5))
    
    def _select_next_character(self) -> str:
        """次に発言するキャラクターを選択"""
        # Grokの発言頻度を少し下げる（スレ主は最初だけ多く発言しない）
        if len(self.posts) < 10 and random.random() < 0.3:
            return "grok"
        
        # その他はランダム（名無しさんの確率を少し高める）
        weights = {
            "grok": 0.15,
            "gpt": 0.20,
            "claude": 0.20,
            "gemini": 0.20,
            "nanashi": 0.25  # 名無しさんは少し多め
        }
        
        return random.choices(
            list(weights.keys()),
            weights=list(weights.values())
        )[0]
    
    async def _create_post(self, character_id: str, is_first: bool = False):
        """レスを作成"""
        character = CHARACTERS[character_id]
        post_number = len(self.posts) + 1
        
        # APIクライアントを取得（キャラクターごとに固定）
        client = AIClientFactory.get_client(character_id)
        
        # レス文字数を決定
        response_length = character.get_response_length(post_number)
        max_chars = random.randint(*response_length.value)
        
        # アンカー生成（30%の確率）
        anchors = []
        if not is_first and self.posts and random.random() < 0.3:
            # 直近5レスから選択
            recent_posts = self.posts[-5:]
            anchor_target = random.choice(recent_posts)
            anchors = [anchor_target.number]
        
        # プロンプト生成
        prompt = self._build_prompt(character_id, anchors, is_first)
        
        # AI応答生成
        content = await client.generate_response(
            prompt=prompt,
            system_prompt=character.system_prompt,
            max_length=max_chars
        )
        
        # アンカーを含める
        if anchors:
            content = f">>{anchors[0]} {content}"
        
        # レスを追加
        post = Post(
            number=post_number,
            character_id=character_id,
            character_name=character.name,
            content=content,
            timestamp=datetime.now(),
            anchors=anchors,
            response_length=response_length
        )
        
        self.posts.append(post)
        return post
    
    def _build_prompt(self, character_id: str, anchors: List[int], is_first: bool) -> str:
        """キャラクター用のプロンプトを構築"""
        if is_first:
            return f"スレッドタイトル「{self.title}」について、議論を始めてください。挑発的に。"
        
        # 直近のレスを含める
        context = self._get_recent_context(limit=5)
        
        if anchors:
            anchor_post = self.posts[anchors[0] - 1]
            return f"""スレッド: {self.title}
最近のレス:
{context}

>>{anchors[0]}（{anchor_post.character_name}）の発言に対して反応してください。"""
        
        return f"""スレッド: {self.title}
最近のレス:
{context}

議論に参加してください。"""
    
    def _get_recent_context(self, limit: int = 5) -> str:
        """直近のレスを文字列化"""
        recent = self.posts[-limit:] if len(self.posts) > limit else self.posts
        
        context_lines = []
        for post in recent:
            context_lines.append(
                f"{post.number} {post.character_name}: {post.content[:50]}..."
            )
        
        return "\n".join(context_lines)
    
    async def _generate_thread_title(self) -> str:
        """AIがスレッドタイトルを生成"""
        topics = [
            "AIは人間を超えたのか",
            "プログラミング言語最強決定戦", 
            "リモートワーク vs オフィスワーク",
            "朝型 vs 夜型 どっちが生産的？",
            "最強のテキストエディタを決めよう",
            "tabs vs spaces 永遠の戦い",
            "フレームワーク使うやつは甘え？"
        ]
        return random.choice(topics)
```

## 5. 環境変数の正しい使い方

### .env設定例
```env
# 各APIキーは必須（すべて設定する）
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx  
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxx
GROK_API_KEY=xai-xxxxxxxxxxxxx

# PRIMARY_APIはフォールバック用（オプション）
PRIMARY_API=openai  # 名無しさんのデフォルトやエラー時の代替

# 動作設定
DELAY_BETWEEN_POSTS=3
MAX_REQUESTS_PER_MINUTE=20
```

## 6. 重要なポイント

### ✅ 正しい動作
1. **Grokがスレ主として最初に発言**（Grok API使用）
2. **GPT君が丁寧に返答**（OpenAI API使用）
3. **Claude先輩が論理的に分析**（Anthropic API使用）
4. **Geminiが創造的な視点を追加**（Google API使用）
5. **名無しさんが煽る**（ランダムにAPI選択）

### ❌ 間違った動作
- すべてのキャラクターが同じAPIを使う
- PRIMARY_APIの設定で全員の性格が変わる

## 7. テスト方法

```python
# テストコード例
async def test_multiple_apis():
    """複数のAPIが正しく使い分けられているか確認"""
    
    # 各キャラクターのクライアントを取得
    grok_client = AIClientFactory.get_client("grok")
    gpt_client = AIClientFactory.get_client("gpt")
    claude_client = AIClientFactory.get_client("claude")
    
    # 異なるインスタンスであることを確認
    assert type(grok_client).__name__ == "GrokClient"
    assert type(gpt_client).__name__ == "OpenAIClient"
    assert type(claude_client).__name__ == "AnthropicClient"
    
    print("✅ 各キャラクターが正しいAPIを使用しています")
```

## 8. 実装チェックリスト

- [ ] `ai_clients.py`で固定マッピングを実装
- [ ] 各APIクライアントクラスを実装
- [ ] `thread_manager.py`でキャラクター選択ロジック実装
- [ ] 環境変数にすべてのAPIキーを設定
- [ ] 複数APIの同時動作をテスト

---

**開発チームへ：**

この仕様により、**本物の複数AIによるレスバトル**が実現されます。
各AIの個性が最大限に発揮される、面白い議論が展開されるはずです！

質問があればSlackでお知らせください。

*プロダクトマネジメントチーム*
