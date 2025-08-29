#!/usr/bin/env python3
"""
デモシナリオ生成スクリプト
"""

import argparse
import asyncio
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from thread_manager import ThreadManager
from characters import CHARACTERS

# デモシナリオ定義
DEMO_SCENARIOS = {
    1: {
        "title": "AIは人間を超えたのか？",
        "description": "AIの能力が人間を超えたかどうかを議論する哲学的なスレッド",
        "max_posts": 50
    },
    2: {
        "title": "tabs vs spaces 永遠の戦い",
        "description": "プログラマー永遠のテーマ「タブvsスペース」論争",
        "max_posts": 50
    },
    3: {
        "title": "朝型 vs 夜型 どっちが生産的？",
        "description": "一般的で親しみやすい話題での議論",
        "max_posts": 50
    }
}

async def create_demo(scenario_id: int, posts: int = 50):
    """デモシナリオを生成"""
    
    if scenario_id not in DEMO_SCENARIOS:
        print(f"❌ シナリオ {scenario_id} は存在しません")
        return False
    
    scenario = DEMO_SCENARIOS[scenario_id]
    scenario["max_posts"] = posts
    
    print("=" * 60)
    print(f"デモシナリオ #{scenario_id} 生成開始")
    print("=" * 60)
    print(f"タイトル: {scenario['title']}")
    print(f"説明: {scenario['description']}")
    print(f"最大投稿数: {posts}")
    print("-" * 60)
    
    # ThreadManager作成
    thread_manager = ThreadManager(
        title=scenario['title'],
        max_posts=posts
    )
    
    # 生成開始
    print("🚀 スレッド生成開始...")
    start_time = datetime.now()
    
    try:
        await thread_manager.start_thread()
        
        # 生成完了待ち
        while thread_manager.is_running:
            await asyncio.sleep(1)
            current_posts = len(thread_manager.posts)
            print(f"  生成中... {current_posts}/{posts} レス", end="\r")
        
        print(f"\n✅ 生成完了! 総レス数: {len(thread_manager.posts)}")
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        return False
    
    # 結果を保存
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    result = {
        "scenario_id": scenario_id,
        "title": scenario['title'],
        "description": scenario['description'],
        "created_at": start_time.isoformat(),
        "duration_seconds": duration,
        "total_posts": len(thread_manager.posts),
        "posts": []
    }
    
    # 投稿内容を追加
    for post in thread_manager.posts:
        result["posts"].append({
            "number": post.number,
            "character_id": post.character_id,
            "character_name": post.character_name,
            "content": post.content,
            "timestamp": post.timestamp.isoformat(),
            "anchors": post.anchors
        })
    
    # ファイルに保存
    filename = f"demo_scenario_{scenario_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"💾 結果を {filename} に保存しました")
    
    # 統計情報表示
    print("-" * 60)
    print("📊 統計情報:")
    print(f"  生成時間: {duration:.2f}秒")
    print(f"  平均生成時間: {duration/posts:.2f}秒/レス")
    
    # キャラクター別投稿数
    char_counts = {}
    for post in thread_manager.posts:
        char_id = post.character_id
        char_counts[char_id] = char_counts.get(char_id, 0) + 1
    
    print("\n  キャラクター別投稿数:")
    for char_id, count in sorted(char_counts.items()):
        char_name = CHARACTERS[char_id].name if char_id in CHARACTERS else "名無しさん"
        percentage = (count / len(thread_manager.posts)) * 100
        print(f"    {char_name}: {count}レス ({percentage:.1f}%)")
    
    # アンカー統計
    anchor_count = sum(1 for post in thread_manager.posts if post.anchors)
    anchor_percentage = (anchor_count / len(thread_manager.posts)) * 100
    print(f"\n  アンカー付きレス: {anchor_count}レス ({anchor_percentage:.1f}%)")
    
    # コンテンツ長統計
    content_lengths = [len(post.content) for post in thread_manager.posts]
    avg_length = sum(content_lengths) / len(content_lengths)
    max_length = max(content_lengths)
    min_length = min(content_lengths)
    
    print(f"\n  コンテンツ長:")
    print(f"    平均: {avg_length:.1f}文字")
    print(f"    最大: {max_length}文字")
    print(f"    最小: {min_length}文字")
    
    print("=" * 60)
    print("✅ デモシナリオ生成完了!")
    print("=" * 60)
    
    return True

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='デモシナリオ生成スクリプト')
    parser.add_argument(
        '--scenario',
        type=int,
        required=True,
        choices=[1, 2, 3],
        help='シナリオID (1: AI vs 人間, 2: tabs vs spaces, 3: 朝型 vs 夜型)'
    )
    parser.add_argument(
        '--posts',
        type=int,
        default=50,
        help='生成するレス数 (デフォルト: 50)'
    )
    
    args = parser.parse_args()
    
    # 実行
    success = asyncio.run(create_demo(args.scenario, args.posts))
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()