import asyncio
import random
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass

from ai_clients import AIClientFactory
from characters import CHARACTERS, ResponseLength, select_response_length

logger = logging.getLogger(__name__)

@dataclass
class Post:
    """レス（投稿）のデータ構造"""
    number: int
    character_id: str
    character_name: str
    content: str
    timestamp: datetime
    anchors: List[int]
    response_length: ResponseLength

class ThreadManager:
    """スレッド全体を管理"""
    
    def __init__(self, title: str = "", max_posts: int = 100):
        self.title = title
        self.max_posts = max_posts
        self.posts: List[Post] = []
        self.is_running = False
        
        self.participating_characters = ["grok", "gpt", "claude", "gemini", "nanashi"]
        
    async def start_thread(self):
        """スレッドを開始"""
        self.is_running = True
        
        if not self.title:
            self.title = await self._generate_thread_title()
        
        await self._create_post("grok", is_first=True)
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.is_running and len(self.posts) < self.max_posts:
            next_character = self._select_next_character()
            post = await self._create_post(next_character)
            
            if post is None:
                consecutive_errors += 1
                logger.warning(f"Failed to create post. Consecutive errors: {consecutive_errors}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"Too many consecutive errors ({consecutive_errors}). Stopping thread.")
                    self.is_running = False
                    break
                    
                # エラー時は少し長めに待機
                await asyncio.sleep(5)
            else:
                consecutive_errors = 0  # 成功したらカウンタをリセット
                await asyncio.sleep(random.uniform(2, 5))
    
    def _select_next_character(self) -> str:
        """次に発言するキャラクターを選択"""
        if len(self.posts) < 10 and random.random() < 0.3:
            return "grok"
        
        weights = {
            "grok": 0.15,
            "gpt": 0.20,
            "claude": 0.20,
            "gemini": 0.20,
            "nanashi": 0.25
        }
        
        return random.choices(
            list(weights.keys()),
            weights=list(weights.values())
        )[0]
    
    async def _create_post(self, character_id: str, is_first: bool = False):
        """レスを作成"""
        try:
            character = CHARACTERS[character_id]
            post_number = len(self.posts) + 1
            
            client = AIClientFactory.get_client(character_id)
            
            response_length = select_response_length(post_number)
            
            # レスポンスの長さをプロンプトで指定
            if response_length == ResponseLength.SHORT:
                length_instruction = "50文字程度で短く返答してください。"
            elif response_length == ResponseLength.MEDIUM:
                length_instruction = "150文字程度で返答してください。"
            else:  # LONG
                length_instruction = "300文字程度で熱く語ってください。"
            
            anchors = []
            if not is_first and self.posts and random.random() < 0.3:
                recent_posts = self.posts[-5:]
                anchor_target = random.choice(recent_posts)
                anchors = [anchor_target.number]
            
            prompt = self._build_prompt(character_id, anchors, is_first, length_instruction)
            
            system_prompt = character.get_system_prompt(thread_context=self.title)
            
            # エラーハンドリングを追加
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    content = await client.generate_response(
                        prompt=prompt,
                        system_prompt=system_prompt
                        # max_tokensは省略（デフォルト100000）
                    )
                    break
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"API error for {character_id} (attempt {retry_count}/{max_retries}): {str(e)}")
                    
                    if retry_count >= max_retries:
                        # フォールバックレスポンス
                        logger.error(f"Failed to generate response for {character_id} after {max_retries} attempts")
                        content = "なるほど、そういう考え方もありますね。"
                    else:
                        # リトライ前に少し待機
                        await asyncio.sleep(2 * retry_count)
            
            if anchors:
                content = f">>{anchors[0]} {content}"
            
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
            
        except Exception as e:
            logger.error(f"Critical error in _create_post for {character_id}: {str(e)}")
            # エラーが発生してもスレッドは継続
            return None
    
    def _build_prompt(self, character_id: str, anchors: List[int], is_first: bool, length_instruction: str) -> str:
        """キャラクター用のプロンプトを構築"""
        if is_first:
            return f"スレッドタイトル「{self.title}」について、議論を始めてください。挑発的に。{length_instruction}"
        
        context = self._get_recent_context(limit=5)
        
        if anchors:
            anchor_post = self.posts[anchors[0] - 1]
            return f"""スレッド: {self.title}
最近のレス:
{context}

>>{anchors[0]}（{anchor_post.character_name}）の発言に対して反応してください。{length_instruction}"""
        
        return f"""スレッド: {self.title}
最近のレス:
{context}

議論に参加してください。{length_instruction}"""
    
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
    
    def stop_thread(self):
        """スレッドを停止"""
        self.is_running = False
    
    def to_dict(self) -> Dict:
        """スレッド情報を辞書形式で返す"""
        return {
            "title": self.title,
            "max_posts": self.max_posts,
            "current_posts": len(self.posts),
            "is_running": self.is_running,
            "posts": [
                {
                    "number": post.number,
                    "character_id": post.character_id,
                    "character_name": post.character_name,
                    "content": post.content,
                    "timestamp": post.timestamp.isoformat(),
                    "anchors": post.anchors,
                    "response_length": post.response_length.name
                }
                for post in self.posts
            ]
        }