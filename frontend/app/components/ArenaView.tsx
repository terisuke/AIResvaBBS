'use client';

import { AgentStream } from './AgentStream';
import { Trophy } from 'lucide-react';
import { useArenaStore } from '../stores/arenaStore';

export const ArenaView = () => {
  const { debateTopic, selectedModels } = useArenaStore();

  return (
    <div className="bg-gray-900 rounded-lg p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Trophy className="w-6 h-6 text-yellow-500" />
        <h2 className="text-xl font-bold">Debate Arena</h2>
      </div>
      
      {debateTopic && (
        <div className="mb-4 p-3 bg-gray-800 rounded">
          <p className="text-sm text-gray-400">Debate Topic:</p>
          <p className="font-medium">{debateTopic}</p>
        </div>
      )}

      <div className="grid grid-cols-3 gap-4">
        <AgentStream 
          agentId="A" 
          title="Agent A (Pro)"
          modelName={selectedModels.combatant_a}
        />
        <AgentStream 
          agentId="judge" 
          title="Judge"
          modelName={selectedModels.judge}
        />
        <AgentStream 
          agentId="B" 
          title="Agent B (Con)"
          modelName={selectedModels.combatant_b}
        />
      </div>
    </div>
  );
};