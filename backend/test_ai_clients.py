#!/usr/bin/env python3
"""
AI Clients テストスクリプト
各APIクライアントが正常に動作することを確認
"""

import asyncio
import os
from datetime import datetime
from ai_clients import AIClientFactory
from characters import CHARACTERS

async def test_client(character_id: str):
    """各キャラクターのAPIクライアントをテスト"""
    print(f"\n{'='*60}")
    print(f"Testing: {character_id}")
    print(f"{'='*60}")
    
    try:
        # クライアント取得
        client = AIClientFactory.get_client(character_id)
        character = CHARACTERS[character_id]
        
        print(f"Character: {character.name}")
        print(f"API Type: {AIClientFactory.CHARACTER_API_MAPPING.get(character_id)}")
        
        # テストプロンプト
        system_prompt = character.get_system_prompt(thread_context="テストスレッド")
        prompt = "こんにちは！今日の調子はどうですか？"
        
        # レスポンス生成
        print(f"Sending test prompt...")
        start_time = datetime.now()
        
        response = await client.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=100
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 結果表示
        print(f"✅ SUCCESS")
        print(f"Response time: {duration:.2f} seconds")
        print(f"Response preview: {response[:100]}...")
        
        return True, duration
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False, 0

async def main():
    """メインテスト実行"""
    print("="*60)
    print("AI Clients Test Suite")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 環境変数チェック
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GROK_API_KEY": os.getenv("GROK_API_KEY")
    }
    
    print("\n📋 API Keys Status:")
    for key_name, key_value in api_keys.items():
        status = "✅ Set" if key_value else "❌ Missing"
        print(f"  {key_name}: {status}")
    
    # 各キャラクターをテスト
    test_characters = ["grok", "gpt", "claude", "gemini", "nanashi"]
    results = {}
    
    for char_id in test_characters:
        success, duration = await test_client(char_id)
        results[char_id] = {
            "success": success,
            "duration": duration
        }
        await asyncio.sleep(1)  # API rate limit対策
    
    # サマリー表示
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results.values() if r["success"])
    total_count = len(results)
    
    print(f"\n📊 Results: {success_count}/{total_count} passed")
    print("\n| Character | Status | Response Time |")
    print("|-----------|--------|---------------|")
    
    for char_id, result in results.items():
        char_name = CHARACTERS[char_id].name if char_id in CHARACTERS else "Unknown"
        status = "✅ Pass" if result["success"] else "❌ Fail"
        time_str = f"{result['duration']:.2f}s" if result["success"] else "N/A"
        print(f"| {char_name:9} | {status:6} | {time_str:13} |")
    
    # 平均応答時間
    successful_times = [r["duration"] for r in results.values() if r["success"]]
    if successful_times:
        avg_time = sum(successful_times) / len(successful_times)
        print(f"\n⏱️ Average response time: {avg_time:.2f} seconds")
    
    print(f"\n{'='*60}")
    
    if success_count == total_count:
        print("✅ All tests passed!")
    else:
        print(f"⚠️ {total_count - success_count} test(s) failed")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())