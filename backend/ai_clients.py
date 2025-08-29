import os
import random
from typing import Optional, List
from xai_sdk import Client as XAIClient
from xai_sdk.chat import user, system
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# MODEL_FALLBACKS: Updated with the correct models
MODEL_FALLBACKS = {
    "grok": ["grok-3-mini", "grok-2-latest"],
    "openai": ["gpt-5-mini", "gpt-4o", "gpt-4o-mini"],
    "anthropic": ["claude-sonnet-4-20250514", "claude-opus-4-1-20250805", "claude-3-5-sonnet-20240620"],
    "google": ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
}

class AIClientFactory:
    """キャラクターに応じて固定のAPIクライアントを返す"""
    
    CHARACTER_API_MAPPING = {
        "grok": "grok",
        "gpt": "openai", 
        "claude": "anthropic",
        "gemini": "google",
        "nanashi": "random"
    }
    
    @staticmethod
    def get_client(character_id: str):
        """
        キャラクターIDに基づいて固定のAPIクライアントを返す
        PRIMARY_APIはフォールバック用
        """
        api_type = AIClientFactory.CHARACTER_API_MAPPING.get(
            character_id, 
            os.getenv("PRIMARY_API", "openai")
        )
        
        if api_type == "random":
            api_type = random.choice(["openai", "anthropic", "google"])
        
        if api_type == "grok":
            return GrokClient()
        elif api_type == "openai":
            return OpenAIClient()
        elif api_type == "anthropic":
            return AnthropicClient()
        elif api_type == "google":
            return GeminiClient()
        else:
            return OpenAIClient()

class GrokClient:
    """Grok API専用クライアント"""
    def __init__(self):
        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            raise ValueError("GROK_API_KEY is not set")
        self.client = XAIClient(api_key=api_key, timeout=3600)
        self.models = MODEL_FALLBACKS["grok"]
    
    async def generate_response(self, prompt: str, system_prompt: str, max_tokens: int = 100) -> str:
        for model in self.models:
            try:
                chat = self.client.chat.create(model=model)
                chat.append(system(system_prompt))
                chat.append(user(prompt))
                response = chat.sample()
                logger.info(f"Grok: Successfully used model {model}")
                return self._truncate_response(response.content, max_tokens)
            except Exception as e:
                logger.warning(f"Grok: Failed with model {model}: {str(e)}")
                if model == self.models[-1]:
                    raise e
                continue
    
    def _truncate_response(self, content: str, max_tokens: int) -> str:
        # max_tokensを文字数に変換（日本語の場合、約2文字/トークン）
        max_chars = max_tokens * 2
        if len(content) <= max_chars:
            return content
        truncated = content[:max_chars]
        last_period = max(
            truncated.rfind('。'),
            truncated.rfind('！'),
            truncated.rfind('？'),
            truncated.rfind('.')
        )
        if last_period > max_chars * 0.7:
            return truncated[:last_period + 1]
        return truncated + "..."

class OpenAIClient:
    """OpenAI API専用クライアント"""
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self.client = AsyncOpenAI(api_key=api_key)
        self.models = MODEL_FALLBACKS["openai"]
    
    async def generate_response(self, prompt: str, system_prompt: str, max_tokens: int = 100) -> str:
        for model in self.models:
            try:
                # OpenAIClient: Corrected parameters for gpt-5-mini
                params = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                }
                if model == "gpt-5-mini":
                    params["max_completion_tokens"] = max_tokens
                    params["temperature"] = 1.0
                else:
                    params["max_tokens"] = max_tokens
                    params["temperature"] = 0.8
                
                response = await self.client.chat.completions.create(**params)
                logger.info(f"OpenAI: Successfully used model {model}")
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI: Failed with model {model}: {str(e)}")
                if model == self.models[-1]:
                    raise e
                continue

class AnthropicClient:
    """Anthropic API専用クライアント"""
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        self.client = AsyncAnthropic(api_key=api_key)
        self.models = MODEL_FALLBACKS["anthropic"]
    
    async def generate_response(self, prompt: str, system_prompt: str, max_tokens: int = 100) -> str:
        for model in self.models:
            try:
                response = await self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8
                )
                logger.info(f"Anthropic: Successfully used model {model}")
                return response.content[0].text
            except Exception as e:
                logger.warning(f"Anthropic: Failed with model {model}: {str(e)}")
                if model == self.models[-1]:
                    raise e
                continue

class GeminiClient:
    """Google Gemini API専用クライアント"""
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set")
        genai.configure(api_key=api_key)
        self.models = MODEL_FALLBACKS["google"]
        self.current_model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """モデルの初期化（フォールバック付き）"""
        for model_name in self.models:
            try:
                self.current_model = genai.GenerativeModel(model_name)
                self.current_model_name = model_name
                logger.info(f"Gemini: Initialized with model {model_name}")
                return
            except Exception as e:
                logger.warning(f"Gemini: Failed to initialize model {model_name}: {str(e)}")
                if model_name == self.models[-1]:
                    raise e
                continue
    
    async def generate_response(self, prompt: str, system_prompt: str, max_tokens: int = 100) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # GeminiClient: Added safety_settings
        safety_settings = [
            {
                "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
        ]
        
        for i, model_name in enumerate(self.models):
            try:
                if i > 0 or self.current_model_name != model_name:
                    self.current_model = genai.GenerativeModel(model_name)
                    self.current_model_name = model_name
                
                response = await self.current_model.generate_content_async(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.8
                    ),
                    safety_settings=safety_settings,
                )
                logger.info(f"Gemini: Successfully used model {model_name}")
                return response.text
            except Exception as e:
                logger.warning(f"Gemini: Failed with model {model_name}: {str(e)}")
                if model_name == self.models[-1]:
                    raise e
                continue