import React, { useEffect, useRef } from 'react';
import { PostItem } from './PostItem';

interface Post {
  number: number;
  character_id: string;
  character_name: string;
  content: string;
  timestamp: string;
  anchors: number[];
  character_color: string;
}

interface ThreadViewProps {
  title: string;
  posts: Post[];
  maxPosts: number;
  isRunning: boolean;
}

export const ThreadView: React.FC<ThreadViewProps> = ({ title, posts, maxPosts, isRunning }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [posts]);

  const scrollToPost = (postNumber: number) => {
    const element = document.getElementById(`post-${postNumber}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      element.classList.add('highlight');
      setTimeout(() => element.classList.remove('highlight'), 2000);
    }
  };

  return (
    <div className="thread-view">
      <div className="thread-header">
        <h1 className="thread-title">{title || 'スレッドタイトル生成中...'}</h1>
        <div className="thread-info">
          <span className="post-count">
            {posts.length} / {maxPosts} レス
          </span>
          {isRunning && (
            <span className="status-indicator">
              <span className="status-dot"></span>
              進行中
            </span>
          )}
        </div>
      </div>

      <div className="thread-body">
        {posts.map((post) => (
          <PostItem
            key={post.number}
            post={post}
            onAnchorClick={scrollToPost}
          />
        ))}
        
        {posts.length === 0 && (
          <div className="no-posts">
            まだレスがありません。スレッドを開始してください。
          </div>
        )}
        
        <div ref={bottomRef} />
      </div>

      {posts.length >= maxPosts && (
        <div className="thread-footer">
          <div className="thread-completed">
            このスレッドは最大レス数に達しました。
          </div>
        </div>
      )}
    </div>
  );
};