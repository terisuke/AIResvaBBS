#!/usr/bin/env python3
"""
統合テストスクリプト
完全なスレッド生成をテストし、すべてのキャラクターが参加することを確認
"""

import asyncio
import json
from datetime import datetime
from thread_manager import ThreadManager
from characters import CHARACTERS

async def test_thread_generation():
    """スレッド生成の統合テスト"""
    print("="*60)
    print("Thread Generation Integration Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # テストスレッド作成
    test_title = "AIクライアント統合テスト - GPT君が表示されるか確認"
    max_posts = 10
    
    print(f"\n📝 Test Configuration:")
    print(f"  Title: {test_title}")
    print(f"  Max Posts: {max_posts}")
    print("-"*60)
    
    # ThreadManager作成
    thread_manager = ThreadManager(
        title=test_title,
        max_posts=max_posts
    )
    
    print("\n🚀 Starting thread generation...")
    start_time = datetime.now()
    
    try:
        # スレッド生成開始
        await thread_manager.start_thread()
        
        # 生成完了待ち
        while thread_manager.is_running:
            await asyncio.sleep(0.5)
            current = len(thread_manager.posts)
            print(f"  Progress: {current}/{max_posts} posts", end="\r")
        
        print(f"\n✅ Generation completed!")
        
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        return False
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # 結果分析
    print("\n" + "="*60)
    print("📊 Results Analysis")
    print("="*60)
    
    # キャラクター別投稿数
    char_counts = {}
    for post in thread_manager.posts:
        char_id = post.character_id
        char_counts[char_id] = char_counts.get(char_id, 0) + 1
    
    print("\n📈 Character Participation:")
    print("| Character | Posts | Percentage | Status |")
    print("|-----------|-------|------------|--------|")
    
    all_characters_present = True
    expected_chars = ["grok", "gpt", "claude", "gemini"]
    
    for char_id in expected_chars:
        char_name = CHARACTERS[char_id].name
        count = char_counts.get(char_id, 0)
        percentage = (count / len(thread_manager.posts) * 100) if thread_manager.posts else 0
        status = "✅" if count > 0 else "❌"
        
        if count == 0:
            all_characters_present = False
            
        print(f"| {char_name:9} | {count:5} | {percentage:9.1f}% | {status:6} |")
    
    # 名無しさんも確認
    nanashi_count = char_counts.get("nanashi", 0)
    if nanashi_count > 0:
        percentage = (nanashi_count / len(thread_manager.posts) * 100)
        print(f"| 名無しさん     | {nanashi_count:5} | {percentage:9.1f}% | ✅     |")
    
    # サンプル投稿表示
    print("\n📝 Sample Posts:")
    print("-"*60)
    
    for i, post in enumerate(thread_manager.posts[:5], 1):
        char_name = CHARACTERS[post.character_id].name if post.character_id in CHARACTERS else "名無しさん"
        content_preview = post.content[:80].replace("\n", " ")
        if len(post.content) > 80:
            content_preview += "..."
        print(f"\n#{post.number} [{char_name}]:")
        print(f"  {content_preview}")
    
    # 統計情報
    print("\n" + "="*60)
    print("📊 Statistics")
    print("="*60)
    print(f"  Total Posts: {len(thread_manager.posts)}")
    print(f"  Generation Time: {duration:.2f} seconds")
    print(f"  Average Time per Post: {duration/max_posts:.2f} seconds")
    
    # アンカー統計
    anchor_count = sum(1 for post in thread_manager.posts if post.anchors)
    anchor_percentage = (anchor_count / len(thread_manager.posts) * 100) if thread_manager.posts else 0
    print(f"  Posts with Anchors: {anchor_count} ({anchor_percentage:.1f}%)")
    
    # 最終判定
    print("\n" + "="*60)
    print("🎯 Test Result")
    print("="*60)
    
    success = all_characters_present and len(thread_manager.posts) == max_posts
    
    if success:
        print("✅ SUCCESS: All characters participated!")
        print("✅ GPT君 is now properly displayed!")
    else:
        print("❌ FAILURE: Some issues detected")
        if not all_characters_present:
            print("  - Not all characters participated")
        if len(thread_manager.posts) != max_posts:
            print(f"  - Expected {max_posts} posts, got {len(thread_manager.posts)}")
    
    print("="*60)
    
    # 結果をJSONで保存
    result_data = {
        "test_time": start_time.isoformat(),
        "duration": duration,
        "success": success,
        "total_posts": len(thread_manager.posts),
        "character_counts": char_counts,
        "all_characters_present": all_characters_present
    }
    
    filename = f"integration_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")
    
    return success

async def main():
    """メイン実行"""
    success = await test_thread_generation()
    exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())