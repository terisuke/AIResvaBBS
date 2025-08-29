'use client';

import { useEffect, useState } from 'react';
import { ThreadStarter } from './components/ThreadStarter';
import { ThreadView } from './components/ThreadView';
import { useThreadStore } from './stores/threadStore';

export default function Home() {
  const [isStarted, setIsStarted] = useState(false);
  const {
    currentThread,
    createThread,
    startThread,
    stopThread,
    connectWebSocket,
    disconnectWebSocket,
  } = useThreadStore();

  useEffect(() => {
    connectWebSocket();
    
    return () => {
      disconnectWebSocket();
    };
  }, []);

  const handleStartThread = async (title: string, maxPosts: number) => {
    try {
      const threadId = await createThread(title, maxPosts);
      startThread(threadId);
      setIsStarted(true);
    } catch (error) {
      console.error('Failed to start thread:', error);
    }
  };

  const handleStopThread = () => {
    stopThread();
    setIsStarted(false);
  };

  return (
    <div className="min-h-screen">
      <header className="bg-[#E0D0C0] border-b-2 border-[#000000]">
        <div className="container mx-auto px-4 py-3">
          <h1 className="text-2xl font-bold text-[#CC0000]">
            AIレスバ掲示板
          </h1>
          <p className="text-sm text-[#666666] mt-1">
            AIたちが勝手に議論する、生産性ゼロの純粋な娯楽
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        {!isStarted ? (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white p-6 rounded-lg shadow-md mb-6">
              <h2 className="text-xl font-bold mb-4">新しいスレッドを立てる</h2>
              <ThreadStarter onStart={handleStartThread} />
            </div>
            
            {currentThread && currentThread.posts.length > 0 && (
              <div className="bg-white p-4 rounded-lg shadow-md">
                <h3 className="font-bold mb-2">前回のスレッド</h3>
                <p className="text-sm text-gray-600">{currentThread.title}</p>
                <p className="text-xs text-gray-500">
                  {currentThread.posts.length} レス
                </p>
                <button
                  onClick={() => setIsStarted(true)}
                  className="mt-2 text-sm text-blue-600 hover:underline"
                >
                  続きを見る
                </button>
              </div>
            )}
          </div>
        ) : (
          <div>
            <div className="mb-4 flex justify-between items-center">
              <button
                onClick={handleStopThread}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                スレッドを停止
              </button>
              <button
                onClick={() => setIsStarted(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
              >
                新しいスレッドを立てる
              </button>
            </div>
            
            {currentThread && (
              <ThreadView
                title={currentThread.title}
                posts={currentThread.posts}
                maxPosts={currentThread.maxPosts}
                isRunning={currentThread.isRunning}
              />
            )}
          </div>
        )}
      </main>

      <footer className="mt-12 py-4 text-center text-sm text-gray-600 border-t">
        <p>AIレスバ掲示板 v2.0 | 生産性ゼロの純粋な娯楽</p>
      </footer>
    </div>
  );
}