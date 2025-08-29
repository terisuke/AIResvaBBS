'use client';

import { useEffect, useRef } from 'react';
import { User, Gavel, MessageSquare } from 'lucide-react';
import { useArenaStore } from '../stores/arenaStore';

interface AgentStreamProps {
  agentId: 'A' | 'B' | 'judge';
  title: string;
  modelName?: string;
}

export const AgentStream = ({ agentId, title, modelName }: AgentStreamProps) => {
  const contentRef = useRef<HTMLDivElement>(null);
  const { agentOutputs, agentMetrics, currentSpeaker } = useArenaStore();
  
  const content = agentOutputs[agentId];
  const metrics = agentMetrics[agentId];
  const isActive = currentSpeaker === agentId;

  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [content]);

  const getAgentIcon = () => {
    if (agentId === 'judge') return <Gavel className="w-5 h-5" />;
    if (agentId === 'A') return <User className="w-5 h-5" />;
    return <MessageSquare className="w-5 h-5" />;
  };

  const getBorderColor = () => {
    if (agentId === 'judge') return 'border-blue-500';
    if (agentId === 'A') return 'border-green-500';
    return 'border-red-500';
  };

  return (
    <div className={`bg-gray-800 rounded-lg overflow-hidden border-2 ${getBorderColor()} ${isActive ? 'ring-2 ring-yellow-500' : ''}`}>
      <div className="p-4 bg-gray-900 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {getAgentIcon()}
          <span className="font-medium">{title}</span>
        </div>
        {modelName && (
          <span className="text-xs bg-gray-700 px-2 py-1 rounded">{modelName}</span>
        )}
      </div>
      
      <div ref={contentRef} className="p-4 h-96 overflow-y-auto">
        {content || <span className="text-gray-500 italic">Waiting for response...</span>}
      </div>
      
      {metrics && (
        <div className="p-2 bg-gray-900 border-t border-gray-700 text-xs text-gray-400">
          <span>Speed: {metrics.tps?.toFixed(1)} t/s</span>
          {metrics.ttft && <span className="ml-3">TTFT: {metrics.ttft.toFixed(2)}s</span>}
        </div>
      )}
    </div>
  );
};