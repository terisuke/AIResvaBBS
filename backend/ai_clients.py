import os
import random
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from xai_sdk import Client as XAIClient
from xai_sdk.chat import user, system
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import logging

# Suppress gRPC and Abseil warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
logging.getLogger('absl').setLevel(logging.ERROR)

load_dotenv()

logger = logging.getLogger(__name__)

# Model fallback configuration
MODEL_FALLBACKS = {
    "grok": ["grok-3-mini", "grok-2-latest"],
    "openai": ["gpt-5-mini-2025-08-07", "gpt-4o-mini", "gpt-4o"],
    "anthropic": ["claude-sonnet-4-20250514", "claude-opus-4-1-20250805", "claude-3-5-sonnet-20240620"],
    "google": ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
}

# Default parameters for each API
DEFAULT_PARAMS = {
    "temperature": 0.8,
    "top_p": 0.9,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.1
}

def get_api_key(env_var: str) -> str:
    """
    Get API key from environment variable
    
    Args:
        env_var: Name of the environment variable
        
    Returns:
        str: The API key
        
    Raises:
        ValueError: If the API key is not set
    """
    api_key = os.getenv(env_var)
    if not api_key:
        raise ValueError(f"{env_var} is not set")
    return api_key

class BaseAIClient(ABC):
    """Base class for all AI clients"""
    
    def __init__(self, api_type: str):
        self.api_type = api_type
        self.models = MODEL_FALLBACKS.get(api_type, [])
        
    @abstractmethod
    async def generate_response(self, prompt: str, system_prompt: str, max_tokens: int = 8192) -> str:
        """
        Generate a response from the AI model
        
        Args:
            prompt: The user's input prompt
            system_prompt: The system instructions for the model
            max_tokens: Maximum number of tokens (ignored - length control via prompt)
            
        Returns:
            str: The generated response text
            
        Raises:
            Exception: If all model fallbacks fail
        """
        pass
    
    # _truncate_responseメソッドは削除（使用されていないため）

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

class GrokClient(BaseAIClient):
    """Grok API専用クライアント"""
    def __init__(self):
        super().__init__("grok")
        api_key = get_api_key("GROK_API_KEY")
        self.client = XAIClient(api_key=api_key, timeout=3600)
    
    async def generate_response(self, prompt: str, system_prompt: str, max_tokens: int = 8192) -> str:
        for model in self.models:
            try:
                chat = self.client.chat.create(model=model)
                chat.append(system(system_prompt))
                chat.append(user(prompt))
                response = chat.sample()
                logger.info(f"Grok: Successfully used model {model}")
                return response.content  # 文字数制御はプロンプトで実施
            except Exception as e:
                logger.warning(f"Grok: Failed with model {model}: {str(e)}")
                if model == self.models[-1]:
                    raise e
                continue

class OpenAIClient(BaseAIClient):
    """OpenAI API専用クライアント"""
    def __init__(self):
        super().__init__("openai")
        api_key = get_api_key("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_response(self, prompt: str, system_prompt: str, max_tokens: int = 8192) -> str:
        for model in self.models:
            try:
                # GPT-5-mini uses max_completion_tokens instead of max_tokens
                if model.startswith("gpt-5"):
                    params = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "max_completion_tokens": 16384,  # GPT-5の上限
                        "temperature": 1.0
                        # include_reasoningはサポートされていないので削除
                    }
                else:
                    params = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 16384,  # OpenAIの上限
                        "temperature": DEFAULT_PARAMS["temperature"],
                        "top_p": DEFAULT_PARAMS["top_p"],
                        "frequency_penalty": DEFAULT_PARAMS["frequency_penalty"],
                        "presence_penalty": DEFAULT_PARAMS["presence_penalty"]
                    }
                
                response = await self.client.chat.completions.create(**params)
                logger.info(f"OpenAI: Successfully used model {model}")
                
                content = response.choices[0].message.content
                if content is None or content == "":
                    # GPT-5のデバッグ情報を追加
                    if model.startswith("gpt-5"):
                        logger.warning(f"OpenAI: Empty response from GPT-5 model {model}")
                        logger.warning(f"  Token usage: {getattr(response, 'usage', 'N/A')}")
                        logger.warning(f"  Finish reason: {response.choices[0].finish_reason}")
                    else:
                        logger.warning(f"OpenAI: Empty response from model {model}, using fallback")
                    
                    if model == self.models[-1]:
                        return "そうですね、確かに興味深い話題ですね。"
                    continue
                    
                return content
            except Exception as e:
                logger.warning(f"OpenAI: Failed with model {model}: {str(e)}")
                if model == self.models[-1]:
                    raise e
                continue

class AnthropicClient(BaseAIClient):
    """Anthropic API専用クライアント"""
    def __init__(self):
        super().__init__("anthropic")
        api_key = get_api_key("ANTHROPIC_API_KEY")
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def generate_response(self, prompt: str, system_prompt: str, max_tokens: int = 8192) -> str:
        for model in self.models:
            try:
                adjusted_max_tokens = 8192  # Anthropicの実用的な上限
                response = await self.client.messages.create(
                    model=model,
                    max_tokens=adjusted_max_tokens,
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

class GeminiClient(BaseAIClient):
    """Google Gemini API専用クライアント"""
    def __init__(self):
        super().__init__("google")
        api_key = get_api_key("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
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
    
    async def generate_response(self, prompt: str, system_prompt: str, max_tokens: int = 8192) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
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
                
                generation_config = genai.GenerationConfig(
                    max_output_tokens=8192,  # Geminiの実用的な上限
                    temperature=0.8,
                    top_p=0.9
                )
                
                response = await self.current_model.generate_content_async(
                    full_prompt,
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                )
                
                if not response.candidates:
                    logger.warning(f"Gemini: No candidates returned for model {model_name}")
                    return "なるほど、それは興味深い話題ですね。"
                
                candidate = response.candidates[0]
                
                if candidate.content and candidate.content.parts and candidate.content.parts[0].text:
                    text = candidate.content.parts[0].text.strip()
                    if text:
                        logger.info(f"Gemini: Successfully used model {model_name}")
                        return text
                
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason == 2:
                    logger.warning(f"Gemini: Response truncated due to token limit")
                    if candidate.content and candidate.content.parts:
                        partial_text = candidate.content.parts[0].text
                        if partial_text and partial_text.strip():
                            return partial_text
                
                logger.warning(f"Gemini: Using fallback response for {model_name}")
                return "そうだね、確かにそういう見方もあるね。"
            except Exception as e:
                logger.warning(f"Gemini: Failed with model {model_name}: {str(e)}")
                if "response.text" in str(e) and "finish_reason" in str(e):
                    logger.warning(f"Gemini: Detected finish_reason error for {model_name}")
                    if model_name == self.models[-1]:
                        return "そうですね、確かに興味深い議論です。"
                    continue
                if model_name == self.models[-1]:
                    raise e
                continue