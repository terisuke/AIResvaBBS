import React, { useState, useEffect } from 'react';

interface Post {
  number: number;
  character_id: string;
  character_name: string;
  content: string;
  timestamp: string;
  anchors: number[];
  character_color: string;
  isStreaming?: boolean;
  streamingContent?: string;
}

interface PostItemProps {
  post: Post;
  onAnchorClick: (postNumber: number) => void;
}

export const PostItem: React.FC<PostItemProps> = ({ post, onAnchorClick }) => {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    const milliseconds = String(date.getMilliseconds()).padStart(2, '0');
    
    return `${year}/${month}/${day}(${getDayOfWeek(date.getDay())}) ${hours}:${minutes}:${seconds}.${milliseconds}`;
  };

  const getDayOfWeek = (day: number) => {
    const days = ['日', '月', '火', '水', '木', '金', '土'];
    return days[day];
  };

  const generateId = (characterId: string, postNumber: number) => {
    const hash = characterId.split('').reduce((acc, char) => {
      return acc + char.charCodeAt(0);
    }, 0);
    return `ID:${hash}${postNumber}`;
  };

  const renderContent = (content: string) => {
    const parts = content.split(/(>>\\d+)/g);
    return parts.map((part, index) => {
      const match = part.match(/^>>(\\d+)$/);
      if (match) {
        const postNumber = parseInt(match[1]);
        return (
          <span
            key={index}
            className="anchor-link"
            onClick={() => onAnchorClick(postNumber)}
          >
            {part}
          </span>
        );
      }
      return part;
    });
  };

  const getPostClass = () => {
    let classes = 'post-item';
    
    // Add streaming class if post is streaming
    if (post.isStreaming) {
      classes += ' streaming';
    }
    
    // Add length-based class
    const length = post.content.length;
    if (length > 500) {
      classes += ' post-long';
    } else if (length > 150) {
      classes += ' post-normal';
    } else {
      classes += ' post-short';
    }
    
    return classes;
  };

  const displayContent = post.isStreaming && post.streamingContent !== undefined 
    ? post.streamingContent 
    : post.content;

  return (
    <div id={`post-${post.number}`} className={getPostClass()}>
      <div className="post-header">
        <span className="post-number">{post.number}</span>
        <span className="post-name" style={{ color: post.character_color }}>
          {post.character_name}
        </span>
        <span className="post-time">{formatTimestamp(post.timestamp)}</span>
        <span className="post-id">{generateId(post.character_id, post.number)}</span>
      </div>
      <div className="post-content">
        {renderContent(displayContent)}
        {post.isStreaming && <span className="streaming-cursor">▌</span>}
      </div>
    </div>
  );
};