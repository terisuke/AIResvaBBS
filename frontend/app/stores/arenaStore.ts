import { create } from 'zustand';
import { ArenaState, ModelInfo, AgentType, DebateMetrics, DebateSummary } from '../types/arena';

interface ArenaStore extends ArenaState {
  // Actions
  setConnected: (isConnected: boolean) => void;
  setConnectionError: (error: string | null) => void;
  setAvailableModels: (models: ModelInfo[]) => void;
  selectModel: (role: 'combatant_a' | 'combatant_b' | 'judge', modelId: string) => void;
  setSelectedModels: (models: { combatant_a: string; combatant_b: string; judge: string }) => void;
  setDebateTopic: (topic: string) => void;
  startDebate: () => void;
  endDebate: () => void;
  setCurrentSpeaker: (speaker: AgentType | null) => void;
  appendAgentOutput: (agent: AgentType, token: string) => void;
  clearAgentOutput: (agent: AgentType) => void;
  updateAgentMetrics: (agent: AgentType, metrics: DebateMetrics) => void;
  setDebateSummary: (summary: DebateSummary) => void;
  resetDebate: () => void;
}

const initialState: ArenaState = {
  isConnected: false,
  connectionError: null,
  availableModels: [],
  selectedModels: {
    combatant_a: '',
    combatant_b: '',
    judge: ''
  },
  debateTopic: '',
  isDebateActive: false,
  currentSpeaker: null,
  agentOutputs: {
    A: '',
    B: '',
    judge: ''
  },
  agentMetrics: {
    A: null,
    B: null,
    judge: null
  },
  debateSummary: null
};

export const useArenaStore = create<ArenaStore>((set) => ({
  ...initialState,
  
  setConnected: (isConnected) => set({ isConnected }),
  
  setConnectionError: (error) => set({ connectionError: error }),
  
  setAvailableModels: (models) => set({ availableModels: models }),
  
  selectModel: (role, modelId) => set((state) => ({
    selectedModels: {
      ...state.selectedModels,
      [role]: modelId
    }
  })),
  
  setSelectedModels: (models) => set({ selectedModels: models }),
  
  setDebateTopic: (topic) => set({ debateTopic: topic }),
  
  startDebate: () => set({ 
    isDebateActive: true,
    agentOutputs: { A: '', B: '', judge: '' },
    agentMetrics: { A: null, B: null, judge: null },
    debateSummary: null
  }),
  
  endDebate: () => set({ 
    isDebateActive: false,
    currentSpeaker: null 
  }),
  
  setCurrentSpeaker: (speaker) => set({ currentSpeaker: speaker }),
  
  appendAgentOutput: (agent, token) => set((state) => ({
    agentOutputs: {
      ...state.agentOutputs,
      [agent]: state.agentOutputs[agent] + token
    }
  })),
  
  clearAgentOutput: (agent) => set((state) => ({
    agentOutputs: {
      ...state.agentOutputs,
      [agent]: ''
    }
  })),
  
  updateAgentMetrics: (agent, metrics) => set((state) => ({
    agentMetrics: {
      ...state.agentMetrics,
      [agent]: metrics
    }
  })),
  
  setDebateSummary: (summary) => set({ debateSummary: summary }),
  
  resetDebate: () => set({
    debateTopic: '',
    isDebateActive: false,
    currentSpeaker: null,
    agentOutputs: { A: '', B: '', judge: '' },
    agentMetrics: { A: null, B: null, judge: null },
    debateSummary: null
  })
}));