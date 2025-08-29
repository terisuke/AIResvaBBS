#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
from ai_clients import AIClientFactory

load_dotenv()

async def test_multiple_apis():
    """複数のAPIが正しく使い分けられているか確認"""
    
    print("=== API Client Test ===\n")
    
    grok_client = AIClientFactory.get_client("grok")
    gpt_client = AIClientFactory.get_client("gpt")
    claude_client = AIClientFactory.get_client("claude")
    gemini_client = AIClientFactory.get_client("gemini")
    
    assert type(grok_client).__name__ == "GrokClient", "Grok client type mismatch"
    assert type(gpt_client).__name__ == "OpenAIClient", "OpenAI client type mismatch"
    assert type(claude_client).__name__ == "AnthropicClient", "Anthropic client type mismatch"
    assert type(gemini_client).__name__ == "GeminiClient", "Gemini client type mismatch"
    
    print("✅ 各キャラクターが正しいAPIを使用しています")
    print(f"  - Grok → {type(grok_client).__name__}")
    print(f"  - GPT君 → {type(gpt_client).__name__}")
    print(f"  - Claude先輩 → {type(claude_client).__name__}")
    print(f"  - Gemini → {type(gemini_client).__name__}")
    print()
    
    print("=== Environment Variables Check ===\n")
    
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GROK_API_KEY": os.getenv("GROK_API_KEY")
    }
    
    all_set = True
    for key, value in env_vars.items():
        if value:
            print(f"✅ {key}: Set (length: {len(value)})")
        else:
            print(f"❌ {key}: Not set")
            all_set = False
    
    if all_set:
        print("\n✅ All API keys are configured!")
    else:
        print("\n❌ Some API keys are missing. Please check your .env file.")
        return False
    
    print("\n=== Basic API Test ===\n")
    
    try:
        print("Testing Grok API...")
        response = await grok_client.generate_response(
            prompt="こんにちは",
            system_prompt="あなたはテストです。短く返答してください。",
            max_tokens=50
        )
        print(f"  Grok response: {response[:50]}...")
        
    except Exception as e:
        print(f"  ❌ Grok API error: {e}")
    
    try:
        print("Testing OpenAI API...")
        response = await gpt_client.generate_response(
            prompt="こんにちは",
            system_prompt="あなたはテストです。短く返答してください。",
            max_tokens=50
        )
        print(f"  GPT response: {response[:50]}...")
        
    except Exception as e:
        print(f"  ❌ OpenAI API error: {e}")
    
    try:
        print("Testing Anthropic API...")
        response = await claude_client.generate_response(
            prompt="こんにちは",
            system_prompt="あなたはテストです。短く返答してください。",
            max_tokens=50
        )
        print(f"  Claude response: {response[:50]}...")
        
    except Exception as e:
        print(f"  ❌ Anthropic API error: {e}")
    
    try:
        print("Testing Google Gemini API...")
        response = await gemini_client.generate_response(
            prompt="自己紹介をしてください。",
            system_prompt="あなたはテストです。短く返答してください。",
            max_tokens=50
        )
        print(f"  Gemini response: {response[:50]}...")
        
    except Exception as e:
        print(f"  ❌ Google API error: {e}")
    
    print("\n=== Test Complete ===")
    return True

if __name__ == "__main__":
    asyncio.run(test_multiple_apis())