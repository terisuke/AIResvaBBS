export interface ModelInfo {
  name: string;
  model_id: string;
  description?: string;
  size?: string;
}

export interface DebateMetrics {
  tps: number;
  ttft?: number;
  total_tokens?: number;
}

export type AgentType = 'A' | 'B' | 'judge';

export interface TokenStreamMessage {
  type: 'token_stream';
  agent: AgentType;
  token: string;
  metrics?: DebateMetrics;
}

export interface TurnStartMessage {
  type: 'turn_start';
  agent: AgentType;
}

export interface TurnEndMessage {
  type: 'turn_end';
  agent: AgentType;
}

export interface DebateStartedMessage {
  type: 'debate_started';
  topic: string;
  agents: {
    combatant_a: string;
    combatant_b: string;
    judge: string;
  };
}

export interface DebateEndedMessage {
  type: 'debate_ended';
  summary: DebateSummary;
}

export interface ErrorMessage {
  type: 'error';
  message: string;
}

export type WebSocketMessage =
  | TokenStreamMessage
  | TurnStartMessage
  | TurnEndMessage
  | DebateStartedMessage
  | DebateEndedMessage
  | ErrorMessage;

export interface StartDebateMessage {
  action: 'start_debate';
  topic: string;
  roles: {
    combatant_a: string;
    combatant_b: string;
    judge: string;
  };
  personas?: {
    combatant_a?: string;
    combatant_b?: string;
  };
}

export interface DebateTurn {
  agent: string;
  content: string;
  timestamp: string;
  metrics: {
    ttft?: number;
    tps: number;
    total_tokens: number;
  };
}

export interface DebateSummary {
  topic: string;
  combatant_a: {
    name: string;
    model: string;
    elo_score: number;
  };
  combatant_b: {
    name: string;
    model: string;
    elo_score: number;
  };
  turns: number;
  state: string;
  history: DebateTurn[];
}

export interface ArenaState {
  // Connection
  isConnected: boolean;
  connectionError: string | null;
  
  // Models
  availableModels: ModelInfo[];
  selectedModels: {
    combatant_a: string;
    combatant_b: string;
    judge: string;
  };
  
  // Debate
  debateTopic: string;
  isDebateActive: boolean;
  currentSpeaker: AgentType | null;
  
  // Content
  agentOutputs: {
    A: string;
    B: string;
    judge: string;
  };
  
  // Metrics
  agentMetrics: {
    A: DebateMetrics | null;
    B: DebateMetrics | null;
    judge: DebateMetrics | null;
  };
  
  // Summary
  debateSummary: DebateSummary | null;
}