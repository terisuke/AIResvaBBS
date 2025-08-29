#!/usr/bin/env python3
"""
ストリーミングUI機能のテストスクリプト
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_streaming():
    """WebSocketストリーミング機能をテスト"""
    uri = "ws://localhost:8000/ws/arena"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket接続成功")
            
            # スレッド開始
            await websocket.send(json.dumps({
                "action": "start_thread",
                "title": "ストリーミングテスト",
                "max_posts": 5
            }))
            print("📤 スレッド開始リクエスト送信")
            
            # メッセージ受信
            message_count = 0
            streaming_posts = {}
            
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30)
                    data = json.loads(message)
                    message_count += 1
                    
                    if data["type"] == "thread_started":
                        print(f"🚀 スレッド開始: {data.get('title', 'N/A')}")
                    
                    elif data["type"] == "post_start":
                        post = data["post"]
                        post_num = post["number"]
                        streaming_posts[post_num] = ""
                        print(f"\n📝 投稿開始 #{post_num} - {post['character_name']}")
                    
                    elif data["type"] == "post_stream":
                        post_num = data["post_number"]
                        chunk = data["content_chunk"]
                        streaming_posts[post_num] += chunk
                        print(chunk, end="", flush=True)
                    
                    elif data["type"] == "post_complete":
                        post = data["post"]
                        post_num = post["number"]
                        print(f"\n✅ 投稿完了 #{post_num}")
                        
                        # ストリーミング内容と最終内容の一致確認
                        if post_num in streaming_posts:
                            streamed = streaming_posts[post_num]
                            final = post["content"]
                            if streamed == final:
                                print(f"  ✓ ストリーミング内容一致")
                            else:
                                print(f"  ✗ ストリーミング内容不一致!")
                                print(f"    Streamed: {streamed[:50]}...")
                                print(f"    Final: {final[:50]}...")
                    
                    elif data["type"] == "thread_completed":
                        total_posts = data.get("total_posts", 0)
                        print(f"\n🎉 スレッド完了! 総投稿数: {total_posts}")
                        break
                    
                    elif data["type"] == "error":
                        print(f"❌ エラー: {data.get('message', 'Unknown error')}")
                        break
                        
                except asyncio.TimeoutError:
                    print("\n⏱️ タイムアウト (30秒)")
                    break
            
            print(f"\n📊 受信メッセージ総数: {message_count}")
            
            # 停止リクエスト
            await websocket.send(json.dumps({"action": "stop_thread"}))
            print("📤 スレッド停止リクエスト送信")
            
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        return False
    
    return True

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("ストリーミングUI機能テスト")
    print("=" * 60)
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    success = asyncio.run(test_streaming())
    
    print("-" * 60)
    if success:
        print("✅ テスト成功")
    else:
        print("❌ テスト失敗")
    print("=" * 60)

if __name__ == "__main__":
    main()