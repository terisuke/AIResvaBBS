import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Post {
  number: number;
  character_id: string;
  character_name: string;
  content: string;
  timestamp: string;
  anchors: number[];
  character_color: string;
}

interface Thread {
  id: string;
  title: string;
  posts: Post[];
  maxPosts: number;
  isRunning: boolean;
  createdAt: string;
}

interface ThreadStore {
  currentThread: Thread | null;
  threads: Thread[];
  wsConnection: WebSocket | null;
  
  createThread: (title: string, maxPosts: number) => Promise<string>;
  startThread: (threadId: string) => void;
  stopThread: () => void;
  addPost: (post: Post) => void;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  loadThread: (threadId: string) => void;
  saveToLocalStorage: () => void;
}

export const useThreadStore = create<ThreadStore>()(
  persist(
    (set, get) => ({
      currentThread: null,
      threads: [],
      wsConnection: null,

      createThread: async (title: string, maxPosts: number) => {
        try {
          const response = await fetch('http://localhost:8000/api/thread/new', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, max_posts: maxPosts }),
          });

          if (!response.ok) throw new Error('Failed to create thread');

          const data = await response.json();
          const newThread: Thread = {
            id: data.thread_id,
            title: title || 'AIが生成中...',
            posts: [],
            maxPosts: maxPosts,
            isRunning: false,
            createdAt: new Date().toISOString(),
          };

          set((state) => ({
            threads: [...state.threads, newThread],
            currentThread: newThread,
          }));

          return data.thread_id;
        } catch (error) {
          console.error('Error creating thread:', error);
          throw error;
        }
      },

      startThread: (threadId: string) => {
        const { wsConnection } = get();
        if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
          wsConnection.send(JSON.stringify({
            action: 'start_thread',
            thread_id: threadId,
          }));
          
          set((state) => ({
            currentThread: state.currentThread ? {
              ...state.currentThread,
              isRunning: true,
            } : null,
          }));
        }
      },

      stopThread: () => {
        const { wsConnection } = get();
        if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
          wsConnection.send(JSON.stringify({
            action: 'stop_thread',
          }));
        }
        
        set((state) => ({
          currentThread: state.currentThread ? {
            ...state.currentThread,
            isRunning: false,
          } : null,
        }));
      },

      addPost: (post: Post) => {
        set((state) => {
          if (!state.currentThread) return state;
          
          const updatedThread = {
            ...state.currentThread,
            posts: [...state.currentThread.posts, post],
          };
          
          const updatedThreads = state.threads.map(thread =>
            thread.id === updatedThread.id ? updatedThread : thread
          );
          
          return {
            currentThread: updatedThread,
            threads: updatedThreads,
          };
        });
      },

      connectWebSocket: () => {
        const ws = new WebSocket('ws://localhost:8000/ws/arena');
        
        ws.onopen = () => {
          console.log('WebSocket connected');
          set({ wsConnection: ws });
        };
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'thread_started':
              set((state) => ({
                currentThread: state.currentThread ? {
                  ...state.currentThread,
                  title: data.title,
                  isRunning: true,
                } : null,
              }));
              break;
              
            case 'post_start':
              // Add new post with streaming flag
              get().addPost({
                ...data.post,
                content: '',
                isStreaming: true,
                streamingContent: '',
              });
              break;
              
            case 'post_stream':
              // Update streaming content
              set((state) => {
                if (!state.currentThread) return state;
                
                const updatedPosts = state.currentThread.posts.map(post => {
                  if (post.number === data.post_number) {
                    return {
                      ...post,
                      streamingContent: (post.streamingContent || '') + data.content_chunk,
                    };
                  }
                  return post;
                });
                
                const updatedThread = {
                  ...state.currentThread,
                  posts: updatedPosts,
                };
                
                const updatedThreads = state.threads.map(thread =>
                  thread.id === updatedThread.id ? updatedThread : thread
                );
                
                return {
                  currentThread: updatedThread,
                  threads: updatedThreads,
                };
              });
              break;
              
            case 'post_complete':
              // Finalize post content and remove streaming flag
              set((state) => {
                if (!state.currentThread) return state;
                
                const updatedPosts = state.currentThread.posts.map(post => {
                  if (post.number === data.post.number) {
                    return {
                      ...data.post,
                      isStreaming: false,
                      streamingContent: undefined,
                    };
                  }
                  return post;
                });
                
                const updatedThread = {
                  ...state.currentThread,
                  posts: updatedPosts,
                };
                
                const updatedThreads = state.threads.map(thread =>
                  thread.id === updatedThread.id ? updatedThread : thread
                );
                
                return {
                  currentThread: updatedThread,
                  threads: updatedThreads,
                };
              });
              break;
              
            case 'new_post':
              get().addPost(data.post);
              break;
              
            case 'thread_completed':
              set((state) => ({
                currentThread: state.currentThread ? {
                  ...state.currentThread,
                  isRunning: false,
                } : null,
              }));
              get().saveToLocalStorage();
              break;
              
            case 'error':
              console.error('WebSocket error:', data.message);
              break;
          }
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
        
        ws.onclose = () => {
          console.log('WebSocket disconnected');
          set({ wsConnection: null });
          
          setTimeout(() => {
            get().connectWebSocket();
          }, 3000);
        };
      },

      disconnectWebSocket: () => {
        const { wsConnection } = get();
        if (wsConnection) {
          wsConnection.close();
          set({ wsConnection: null });
        }
      },

      loadThread: (threadId: string) => {
        const thread = get().threads.find(t => t.id === threadId);
        if (thread) {
          set({ currentThread: thread });
        }
      },

      saveToLocalStorage: () => {
        const { threads } = get();
        const threadsToSave = threads.slice(-10);
        localStorage.setItem('ai_resuba_threads', JSON.stringify(threadsToSave));
      },
    }),
    {
      name: 'ai-resuba-storage',
      partialize: (state) => ({ threads: state.threads }),
    }
  )
);