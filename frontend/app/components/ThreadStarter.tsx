import React, { useState } from 'react';

interface ThreadStarterProps {
  onStart: (title: string, maxPosts: number) => void;
}

export const ThreadStarter: React.FC<ThreadStarterProps> = ({ onStart }) => {
  const [title, setTitle] = useState('');
  const [maxPosts, setMaxPosts] = useState<100 | 500 | 1000>(100);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onStart(title, maxPosts);
  };

  return (
    <div className="thread-starter">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-bold mb-2">
            スレッドタイトル
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="議論したいテーマを入力...またはAIにお任せ"
            maxLength={100}
            className="w-full px-3 py-2 border border-gray-400 rounded bg-gray-50 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-bold mb-2">
            最大レス数
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                value={100}
                checked={maxPosts === 100}
                onChange={(e) => setMaxPosts(Number(e.target.value) as 100)}
                className="mr-2"
              />
              <span>100</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value={500}
                checked={maxPosts === 500}
                onChange={(e) => setMaxPosts(Number(e.target.value) as 500)}
                className="mr-2"
              />
              <span>500</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value={1000}
                checked={maxPosts === 1000}
                onChange={(e) => setMaxPosts(Number(e.target.value) as 1000)}
                className="mr-2"
              />
              <span>1000</span>
            </label>
          </div>
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 transition-colors"
        >
          スレッドを立てる
        </button>
      </form>
    </div>
  );
};