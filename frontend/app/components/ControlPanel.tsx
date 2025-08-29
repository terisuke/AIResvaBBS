'use client';

import { useState, useEffect } from 'react';
import { Play, Loader2, RefreshCw } from 'lucide-react';

import { useArenaStore } from '../stores/arenaStore';

interface ControlPanelProps {
  onStartDebate: (topic: string, roles: {
    combatant_a: string;
    combatant_b: string;
    judge: string;
  }) => void;
}

export const ControlPanel = ({ onStartDebate }: ControlPanelProps) => {
  const { isConnected, isDebateActive, setDebateTopic, setSelectedModels } = useArenaStore();
  const [topic, setTopic] = useState('');
  const [combatantA, setCombatantA] = useState('');
  const [combatantB, setCombatantB] = useState('');
  const [judge, setJudge] = useState('');
  const [availableModels, setAvailableModels] = useState<any[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);

  const fetchModels = async () => {
    setIsLoadingModels(true);
    try {
      const response = await fetch('http://localhost:8000/api/models');
      if (response.ok) {
        const data = await response.json();
        // Handle both array and object with models property
        const modelsList = Array.isArray(data) ? data : (data.models || []);
        setAvailableModels(modelsList);
        
        // Set default models if available
        if (modelsList.length > 0) {
          const modelIds = modelsList.map((m: any) => 
            typeof m === 'string' ? m : m.model_id || m.name
          );
          setCombatantA(modelIds[0]);
          setCombatantB(modelIds[Math.min(1, modelIds.length - 1)]);
          setJudge(modelIds[Math.min(2, modelIds.length - 1)]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
      setAvailableModels([]);
    } finally {
      setIsLoadingModels(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleStartDebate = () => {
    if (!topic.trim()) {
      alert('Please enter a debate topic');
      return;
    }
    
    if (!combatantA || !combatantB || !judge) {
      alert('Please select all models');
      return;
    }

    // Store に設定を保存
    setDebateTopic(topic);
    setSelectedModels({
      combatant_a: combatantA,
      combatant_b: combatantB,
      judge: judge,
    });

    onStartDebate(topic, {
      combatant_a: combatantA,
      combatant_b: combatantB,
      judge: judge,
    });
  };

  const isFormValid = topic.trim() && combatantA && combatantB && judge && isConnected && !isDebateActive;

  return (
    <div className="bg-gray-900 rounded-lg p-6 space-y-4">
      <h2 className="text-xl font-bold text-white mb-4">Debate Control Panel</h2>
      
      {/* Connection Status */}
      <div className="flex items-center space-x-2">
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-sm text-gray-300">
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      {/* Topic Input */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Debate Topic
        </label>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a topic for debate..."
          className="w-full px-3 py-2 bg-gray-800 text-white rounded-md border border-gray-700 focus:border-blue-500 focus:outline-none"
          disabled={isDebateActive}
        />
      </div>

      {/* Model Selection */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="block text-sm font-medium text-gray-300">
            Model Selection
          </label>
          <button
            onClick={fetchModels}
            disabled={isLoadingModels}
            className="text-sm text-blue-400 hover:text-blue-300 disabled:opacity-50"
          >
            {isLoadingModels ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Combatant A */}
        <div>
          <label className="block text-xs text-gray-400 mb-1">Combatant A (Pro)</label>
          <select
            value={combatantA}
            onChange={(e) => setCombatantA(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 text-white rounded-md border border-gray-700 focus:border-blue-500 focus:outline-none"
            disabled={isDebateActive || isLoadingModels}
          >
            <option value="">Select Model...</option>
            {availableModels.map((model) => {
              const modelId = typeof model === 'string' ? model : model.model_id || model.name;
              const modelName = typeof model === 'string' ? model : model.name || model.model_id;
              return (
                <option key={modelId} value={modelId}>
                  {modelName}
                </option>
              );
            })}
          </select>
        </div>

        {/* Combatant B */}
        <div>
          <label className="block text-xs text-gray-400 mb-1">Combatant B (Con)</label>
          <select
            value={combatantB}
            onChange={(e) => setCombatantB(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 text-white rounded-md border border-gray-700 focus:border-blue-500 focus:outline-none"
            disabled={isDebateActive || isLoadingModels}
          >
            <option value="">Select Model...</option>
            {availableModels.map((model) => {
              const modelId = typeof model === 'string' ? model : model.model_id || model.name;
              const modelName = typeof model === 'string' ? model : model.name || model.model_id;
              return (
                <option key={modelId} value={modelId}>
                  {modelName}
                </option>
              );
            })}
          </select>
        </div>

        {/* Judge */}
        <div>
          <label className="block text-xs text-gray-400 mb-1">Judge</label>
          <select
            value={judge}
            onChange={(e) => setJudge(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 text-white rounded-md border border-gray-700 focus:border-blue-500 focus:outline-none"
            disabled={isDebateActive || isLoadingModels}
          >
            <option value="">Select Model...</option>
            {availableModels.map((model) => {
              const modelId = typeof model === 'string' ? model : model.model_id || model.name;
              const modelName = typeof model === 'string' ? model : model.name || model.model_id;
              return (
                <option key={modelId} value={modelId}>
                  {modelName}
                </option>
              );
            })}
          </select>
        </div>
      </div>

      {/* Recommended Models Note */}
      {availableModels.length === 0 && !isLoadingModels && (
        <div className="text-xs text-yellow-400 bg-yellow-900/20 p-2 rounded">
          No models found. Please ensure Ollama is running with models installed.
          <br />
          Recommended: qwen3:32b, gpt-oss:20b, gemma-3:27b
        </div>
      )}

      {/* Start Button */}
      <button
        onClick={handleStartDebate}
        disabled={!isFormValid}
        className={`w-full py-3 px-4 rounded-md font-medium flex items-center justify-center space-x-2 transition-colors ${
          isFormValid
            ? 'bg-blue-600 hover:bg-blue-700 text-white'
            : 'bg-gray-700 text-gray-400 cursor-not-allowed'
        }`}
      >
        {isDebateActive ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Debate in Progress...</span>
          </>
        ) : (
          <>
            <Play className="w-5 h-5" />
            <span>Start Debate</span>
          </>
        )}
      </button>
    </div>
  );
};