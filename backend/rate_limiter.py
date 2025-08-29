import asyncio
import time
from typing import Dict, Optional
from dataclasses import dataclass
import os

@dataclass
class RateLimitConfig:
    """レート制限設定"""
    max_requests_per_minute: int = 20
    delay_between_posts: float = 3.0

class RateLimiter:
    """APIレート制限管理"""
    
    def __init__(self):
        self.config = RateLimitConfig(
            max_requests_per_minute=int(os.getenv("MAX_REQUESTS_PER_MINUTE", "20")),
            delay_between_posts=float(os.getenv("DELAY_BETWEEN_POSTS", "3"))
        )
        self.request_times: Dict[str, list] = {
            "openai": [],
            "anthropic": [],
            "google": [],
            "grok": []
        }
        self.last_post_time = 0
    
    async def wait_if_needed(self, api_type: str):
        """必要に応じて待機"""
        current_time = time.time()
        
        if api_type not in self.request_times:
            self.request_times[api_type] = []
        
        self.request_times[api_type] = [
            t for t in self.request_times[api_type] 
            if current_time - t < 60
        ]
        
        if len(self.request_times[api_type]) >= self.config.max_requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[api_type][0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        time_since_last_post = current_time - self.last_post_time
        if time_since_last_post < self.config.delay_between_posts:
            await asyncio.sleep(self.config.delay_between_posts - time_since_last_post)
        
        self.request_times[api_type].append(current_time)
        self.last_post_time = current_time

rate_limiter = RateLimiter()