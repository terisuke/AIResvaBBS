from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Literal
import json
import asyncio
from datetime import datetime
import uuid

from thread_manager import ThreadManager
from characters import CHARACTERS

app = FastAPI(title="AI Resuba BBS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_threads: Dict[str, ThreadManager] = {}
active_connections: List[WebSocket] = []


class ThreadCreateRequest(BaseModel):
    title: Optional[str] = ""
    max_posts: Literal[100, 500, 1000] = 100


class CharacterInfo(BaseModel):
    id: str
    name: str
    color: str
    description: str


@app.get("/")
async def root():
    return {
        "message": "AI Resuba BBS API",
        "version": "1.0.0",
        "endpoints": {
            "characters": "/api/characters",
            "new_thread": "/api/thread/new",
            "websocket": "/ws/arena",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "AI Resuba BBS is running"
    }


@app.get("/api/characters", response_model=List[CharacterInfo])
async def get_characters():
    """利用可能なAIキャラクターの一覧を返す"""
    characters = []
    for char_id, char in CHARACTERS.items():
        characters.append(CharacterInfo(
            id=char.id,
            name=char.name,
            color=char.color,
            description=char.personality[:100] + "..."
        ))
    return characters


@app.post("/api/thread/new")
async def create_thread(request: ThreadCreateRequest):
    """新しいスレッドを作成"""
    thread_id = str(uuid.uuid4())
    thread_manager = ThreadManager(
        title=request.title,
        max_posts=request.max_posts
    )
    
    active_threads[thread_id] = thread_manager
    
    return {
        "thread_id": thread_id,
        "title": request.title if request.title else "AIが生成予定",
        "max_posts": request.max_posts,
        "status": "created"
    }


@app.get("/api/thread/{thread_id}")
async def get_thread(thread_id: str):
    """スレッドの情報を取得"""
    if thread_id not in active_threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    thread = active_threads[thread_id]
    return thread.to_dict()


@app.websocket("/ws/arena")
async def websocket_arena(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    thread_manager = None
    thread_task = None
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["action"] == "start_thread":
                thread_id = message.get("thread_id")
                
                if thread_id and thread_id in active_threads:
                    thread_manager = active_threads[thread_id]
                else:
                    thread_manager = ThreadManager(
                        title=message.get("title", ""),
                        max_posts=message.get("max_posts", 100)
                    )
                    thread_id = str(uuid.uuid4())
                    active_threads[thread_id] = thread_manager
                
                await websocket.send_json({
                    "type": "thread_started",
                    "thread_id": thread_id,
                    "title": thread_manager.title if thread_manager.title else "生成中...",
                    "max_posts": thread_manager.max_posts
                })
                
                async def run_thread():
                    try:
                        # Track sent posts
                        sent_posts = set()
                        
                        # Start the thread generation in background
                        thread_task = asyncio.create_task(thread_manager.start_thread())
                        
                        while thread_manager.is_running or not thread_task.done():
                            await asyncio.sleep(0.5)
                            
                            # Check for new posts
                            for post in thread_manager.posts:
                                if post.number not in sent_posts:
                                    sent_posts.add(post.number)
                                    
                                    # Send post_start event for streaming UI
                                    await websocket.send_json({
                                        "type": "post_start",
                                        "post": {
                                            "number": post.number,
                                            "character_id": post.character_id,
                                            "character_name": post.character_name,
                                            "timestamp": post.timestamp.isoformat(),
                                            "character_color": CHARACTERS[post.character_id].color
                                        }
                                    })
                                    
                                    # Simulate streaming by sending content in chunks
                                    content = post.content
                                    chunk_size = 10  # Send 10 characters at a time
                                    
                                    for i in range(0, len(content), chunk_size):
                                        chunk = content[i:i+chunk_size]
                                        await websocket.send_json({
                                            "type": "post_stream",
                                            "post_number": post.number,
                                            "content_chunk": chunk
                                        })
                                        await asyncio.sleep(0.05)  # Small delay for streaming effect
                                    
                                    # Send post_complete event
                                    await websocket.send_json({
                                        "type": "post_complete",
                                        "post": {
                                            "number": post.number,
                                            "character_id": post.character_id,
                                            "character_name": post.character_name,
                                            "content": post.content,
                                            "timestamp": post.timestamp.isoformat(),
                                            "anchors": post.anchors,
                                            "character_color": CHARACTERS[post.character_id].color
                                        }
                                    })
                        
                        # Wait for thread task to complete
                        await thread_task
                        
                        await websocket.send_json({
                            "type": "thread_completed",
                            "thread_id": thread_id,
                            "total_posts": len(thread_manager.posts)
                        })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "message": str(e)
                        })
                
                thread_task = asyncio.create_task(run_thread())
            
            elif message["action"] == "stop_thread":
                if thread_manager:
                    thread_manager.stop_thread()
                    if thread_task:
                        thread_task.cancel()
                    await websocket.send_json({
                        "type": "thread_stopped"
                    })
            
            elif message["action"] == "get_status":
                if thread_manager:
                    await websocket.send_json({
                        "type": "status",
                        "data": thread_manager.to_dict()
                    })
                else:
                    await websocket.send_json({
                        "type": "status",
                        "data": {"state": "no_active_thread"}
                    })
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        if thread_manager:
            thread_manager.stop_thread()
        if thread_task:
            thread_task.cancel()
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        if thread_manager:
            thread_manager.stop_thread()
        if thread_task:
            thread_task.cancel()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)