#!/usr/bin/env python3
"""
デモスレッド作成スクリプト
3つのテーマでサンプルスレッドを生成
"""
import asyncio
import json
from datetime import datetime
from thread_manager import ThreadManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEMO_TOPICS = [
    {
        "title": "AIは人間を超えたのか",
        "description": "哲学的議論",
        "max_posts": 50
    },
    {
        "title": "tabs vs spaces 永遠の戦い",
        "description": "技術論争",
        "max_posts": 50
    },
    {
        "title": "朝型 vs 夜型 どっちが生産的？",
        "description": "日常的な話題",
        "max_posts": 50
    }
]

async def create_demo_thread(topic_info):
    """デモスレッドを作成"""
    logger.info(f"Creating demo thread: {topic_info['title']}")
    
    thread_manager = ThreadManager(
        title=topic_info['title'],
        max_posts=topic_info['max_posts']
    )
    
    # スレッドを開始（非同期で実行）
    thread_task = asyncio.create_task(thread_manager.start_thread())
    
    # 進捗を表示
    while thread_manager.is_running:
        await asyncio.sleep(5)
        current_posts = len(thread_manager.posts)
        logger.info(f"[{topic_info['title']}] Progress: {current_posts}/{topic_info['max_posts']} posts")
        
        # サンプルレスを表示
        if thread_manager.posts and current_posts % 10 == 0:
            latest_post = thread_manager.posts[-1]
            logger.info(f"  Latest: {latest_post.character_name}: {latest_post.content[:50]}...")
    
    await thread_task
    
    # 結果を保存
    filename = f"demo_thread_{topic_info['title'].replace(' ', '_')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(thread_manager.to_dict(), f, ensure_ascii=False, indent=2)
    
    logger.info(f"Thread saved to {filename}")
    
    # 統計情報
    total_posts = len(thread_manager.posts)
    characters_used = {}
    anchor_count = 0
    total_length = 0
    
    for post in thread_manager.posts:
        characters_used[post.character_name] = characters_used.get(post.character_name, 0) + 1
        if post.anchors:
            anchor_count += 1
        total_length += len(post.content)
    
    avg_length = total_length / total_posts if total_posts > 0 else 0
    
    return {
        "title": topic_info['title'],
        "description": topic_info['description'],
        "total_posts": total_posts,
        "characters": characters_used,
        "anchor_rate": f"{(anchor_count/total_posts)*100:.1f}%",
        "avg_post_length": f"{avg_length:.0f} chars",
        "filename": filename
    }

async def main():
    """メイン処理"""
    logger.info("=== Demo Thread Generator ===")
    logger.info("Creating 3 sample threads for demonstration")
    
    results = []
    
    for topic in DEMO_TOPICS:
        logger.info(f"\n--- {topic['description']} ---")
        result = await create_demo_thread(topic)
        results.append(result)
        
        # API負荷を避けるため、スレッド間で待機
        logger.info("Waiting 30 seconds before next thread...")
        await asyncio.sleep(30)
    
    # サマリーレポート
    logger.info("\n=== Demo Thread Summary ===")
    for result in results:
        logger.info(f"\n{result['title']} ({result['description']})")
        logger.info(f"  - Total posts: {result['total_posts']}")
        logger.info(f"  - Anchor rate: {result['anchor_rate']}")
        logger.info(f"  - Avg length: {result['avg_post_length']}")
        logger.info(f"  - Characters:")
        for char, count in result['characters'].items():
            logger.info(f"    - {char}: {count} posts")
        logger.info(f"  - Saved to: {result['filename']}")
    
    logger.info("\n✅ All demo threads created successfully!")

if __name__ == "__main__":
    asyncio.run(main())